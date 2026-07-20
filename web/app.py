#! /usr/bin/env python3
# Flask-SocketIO server that lets a browser play BookCricket. Each connected
# browser tab gets its own background thread running the *unmodified* game
# engine (functions/Base/Match.py etc, via BookCricket.run_game); its
# input()/print()/PrintInColor()/ChooseFromOptions() calls are transparently
# redirected to that thread's WebChannel by web/io_bridge.py.
import os
import re
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.io_bridge import WebChannel, GameAborted, set_channel, clear_channel, install_web_io

# must happen before BookCricket (and everything it pulls in) is imported,
# so the game engine's input()/print() calls are already redirectable.
install_web_io()

import BookCricket  # noqa: E402
import functions.SaveGame as SaveGame  # noqa: E402

from flask import Flask, abort, jsonify, request, send_from_directory  # noqa: E402
from flask_socketio import SocketIO  # noqa: E402

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
RESOURCES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"
)
PLAYER_PICS_DIR = os.path.join(RESOURCES_DIR, "players", "pics")
TEAM_FLAGS_DIR = os.path.join(RESOURCES_DIR, "teams", "flags")
MISC_PICS_DIR = os.path.join(RESOURCES_DIR, "misc")
VENUE_PICS_DIR = os.path.join(RESOURCES_DIR, "venues")
UMPIRE_PICS_DIR = os.path.join(RESOURCES_DIR, "umpires")
COMMENTATOR_PICS_DIR = os.path.join(RESOURCES_DIR, "commentators")
PIC_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
app.config["SECRET_KEY"] = os.urandom(24)
socketio = SocketIO(app, async_mode="threading")

# public mode: set PUBLIC=1 (done in render.yaml; RENDER is set automatically
# on render.com) to disable the shutdown endpoint/button - on a shared server
# a visitor must not be able to kill the game for everyone else.
IS_PUBLIC = (
    os.environ.get("PUBLIC", "").lower() in ("1", "true", "yes")
    or os.environ.get("RENDER") is not None
)
# each browser tab runs its own game thread; cap them so a public instance
# can't be trivially exhausted by opening tabs
MAX_SESSIONS = int(os.environ.get("MAX_SESSIONS", 20))

_channels = {}
_channels_lock = threading.Lock()


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


def _serve_pic(directory, name):
    # The browser asks for a raw name ("Virat Kohli", "NewZealand", "lunch");
    # resolve it to a file by slug (virat_kohli.png/.jpg/...), so the filename
    # convention lives in exactly one place. 404 means "no pic saved" - the
    # frontend falls back to an initials avatar or an emoji.
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not slug:
        abort(404)
    for ext in PIC_EXTENSIONS:
        if os.path.isfile(os.path.join(directory, slug + ext)):
            return send_from_directory(directory, slug + ext)
    abort(404)


@app.route("/players/pics/<path:player_name>")
def player_pic(player_name):
    return _serve_pic(PLAYER_PICS_DIR, player_name)


@app.route("/teams/flags/<path:team_name>")
def team_flag(team_name):
    return _serve_pic(TEAM_FLAGS_DIR, team_name)


@app.route("/misc/<path:kind>")
def misc_pic(kind):
    return _serve_pic(MISC_PICS_DIR, kind)


@app.route("/venues/<path:venue_name>")
def venue_pic(venue_name):
    return _serve_pic(VENUE_PICS_DIR, venue_name)


@app.route("/umpires/<path:umpire_name>")
def umpire_pic(umpire_name):
    return _serve_pic(UMPIRE_PICS_DIR, umpire_name)


@app.route("/commentators/<path:commentator_name>")
def commentator_pic(commentator_name):
    return _serve_pic(COMMENTATOR_PICS_DIR, commentator_name)


# cap on how large an uploaded save may be (a pickled match is tens of KB)
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@app.route("/saves")
def list_saves_route():
    """List a client's resumable saves (client id via ?clientId=...)."""
    client_id = request.args.get("clientId") or None
    try:
        return jsonify({"saves": SaveGame.list_saves(client_id=client_id)})
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.route("/upload_save", methods=["POST"])
def upload_save_route():
    """
    Accept an uploaded save file, validate it by safely reconstructing the
    match, then store it as a normal server-side save owned by the uploading
    client and return its new id so the client can resume it.
    """
    upload = request.files.get("file")
    if upload is None:
        return {"error": "No file uploaded"}, 400
    blob = upload.read(MAX_UPLOAD_BYTES + 1)
    if len(blob) > MAX_UPLOAD_BYTES:
        return {"error": "Save file too large"}, 400
    try:
        match = SaveGame.load_match_bytes(blob)
    except SaveGame.SaveLoadError as exc:
        return {"error": "Not a valid BookCricket save: %s" % exc}, 400

    client_id = request.form.get("clientId") or None
    # give the uploaded copy a fresh id owned by this client, so it can't
    # collide with an existing save and shows up in this browser's list
    match.save_id = SaveGame.new_save_id()
    match.save_client_id = client_id
    match.save_enabled = True
    try:
        SaveGame.save_match(match)
    except Exception as exc:
        return {"error": "Could not store uploaded save: %s" % exc}, 500
    return {"id": match.save_id, "meta": match.SaveMeta()}


@app.route("/shutdown", methods=["POST"])
def shutdown():
    # os._exit rather than sys.exit: this is a dev tool running as a single
    # local process, and Werkzeug's dev server offers no clean programmatic
    # stop in recent versions. Delay briefly so this response actually
    # reaches the browser before the process disappears.
    if IS_PUBLIC:
        return {"status": "disabled"}, 403

    def _stop():
        time.sleep(0.3)
        os._exit(0)

    threading.Thread(target=_stop, daemon=True).start()
    return {"status": "stopping"}


def _play(sid, channel, resume_id=None, client_id=None, series=False,
          resume_kind="match"):
    set_channel(channel)
    try:
        BookCricket.run_game(
            autoplay=False, overs=None, resume_id=resume_id, save_owner=client_id,
            series=series, resume_kind=resume_kind,
        )
        channel.output("All done. Refresh the page to start again.", "style-bright")
    except GameAborted:
        pass
    except Exception as exc:
        # one player's crash shouldn't take down the server for everyone else
        channel.output("Something went wrong: %s" % exc, "fore-lightred_ex")
    finally:
        channel.flush()
        clear_channel()
        with _channels_lock:
            _channels.pop(sid, None)


def _start_game(sid, resume_id=None, series=False, resume_kind="match"):
    """Start the game thread for a session once, from the start menu choice."""
    with _channels_lock:
        channel = _channels.get(sid)
    if channel is None or getattr(channel, "game_started", False):
        return
    channel.game_started = True
    thread = threading.Thread(
        target=_play,
        args=(sid, channel, resume_id, getattr(channel, "client_id", None),
              series, resume_kind),
        daemon=True,
    )
    thread.start()


@socketio.on("connect")
def handle_connect():
    sid = request.sid
    channel = WebChannel(lambda event, data: socketio.emit(event, data, to=sid))
    channel.client_id = None
    channel.game_started = False
    with _channels_lock:
        if len(_channels) >= MAX_SESSIONS:
            channel.output(
                "Server is full (%d matches in progress). Try again later."
                % MAX_SESSIONS,
                "fore-lightred_ex",
            )
            return False  # reject the connection
        _channels[sid] = channel
    socketio.emit("server_config", {"allowShutdown": not IS_PUBLIC}, to=sid)
    # the game no longer auto-starts: the client sends "hello" with its id,
    # we reply with the start menu (new game / resume a saved one), and the
    # game thread begins only once the client emits "start_game".


@socketio.on("hello")
def handle_hello(data):
    """Client handshake carrying its persistent id; reply with the start
    menu (this client's resumable saves)."""
    sid = request.sid
    client_id = (data or {}).get("clientId") if isinstance(data, dict) else None
    with _channels_lock:
        channel = _channels.get(sid)
    if channel is None:
        return
    channel.client_id = client_id or None
    try:
        saves = SaveGame.list_saves(client_id=channel.client_id, kind="match")
        tournaments = SaveGame.list_saves(client_id=channel.client_id, kind="tournament")
    except Exception:
        saves, tournaments = [], []
    socketio.emit(
        "start_menu",
        {"saves": saves, "tournaments": tournaments, "canUpload": True,
         "canSeries": True},
        to=sid,
    )


@socketio.on("start_game")
def handle_start_game(data):
    """Begin play: a fresh match, a new series, or resume a saved match/series."""
    sid = request.sid
    data = data or {}
    mode = data.get("mode")
    if mode == "series":
        _start_game(sid, series=True)
    elif mode == "resume":
        _start_game(sid, resume_id=data.get("id"), resume_kind="match")
    elif mode == "resume_series":
        _start_game(sid, resume_id=data.get("id"), resume_kind="tournament")
    else:  # "new"
        _start_game(sid)


@socketio.on("client_input")
def handle_client_input(value):
    sid = request.sid
    with _channels_lock:
        channel = _channels.get(sid)
    if channel is not None:
        channel.submit(value)


@socketio.on("event_ack")
def handle_event_ack(eid):
    # the browser reporting that an event pop-up has left the screen; wakes
    # the game thread blocked in WebChannel.event() so play stays in sync
    # with the pop-ups the player actually sees
    sid = request.sid
    with _channels_lock:
        channel = _channels.get(sid)
    if channel is not None:
        channel.ack_event(eid)


@socketio.on("declare_request")
def handle_declare_request():
    # the GUI's Declare button: flags the session's game thread, which shows
    # the confirmation prompt at the next over boundary (Test innings only)
    sid = request.sid
    with _channels_lock:
        channel = _channels.get(sid)
    if channel is not None:
        channel.request_declare()


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    with _channels_lock:
        channel = _channels.pop(sid, None)
    if channel is not None:
        channel.close()


if __name__ == "__main__":
    # 127.0.0.1 by default so the game isn't exposed to the LAN unless asked.
    # Set HOST=0.0.0.0 to allow other devices on the network to connect.
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5050))
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)
