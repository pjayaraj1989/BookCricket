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

from flask import Flask, abort, request, send_from_directory  # noqa: E402
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
PIC_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
app.config["SECRET_KEY"] = os.urandom(24)
socketio = SocketIO(app, async_mode="threading")

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


@app.route("/shutdown", methods=["POST"])
def shutdown():
    # os._exit rather than sys.exit: this is a dev tool running as a single
    # local process, and Werkzeug's dev server offers no clean programmatic
    # stop in recent versions. Delay briefly so this response actually
    # reaches the browser before the process disappears.
    def _stop():
        time.sleep(0.3)
        os._exit(0)

    threading.Thread(target=_stop, daemon=True).start()
    return {"status": "stopping"}


def _play(sid, channel):
    set_channel(channel)
    try:
        BookCricket.run_game(autoplay=False, overs=None)
        channel.output("Match finished. Refresh the page to play again.", "style-bright")
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


@socketio.on("connect")
def handle_connect():
    sid = request.sid
    channel = WebChannel(lambda event, data: socketio.emit(event, data, to=sid))
    with _channels_lock:
        _channels[sid] = channel
    thread = threading.Thread(target=_play, args=(sid, channel), daemon=True)
    thread.start()


@socketio.on("client_input")
def handle_client_input(value):
    sid = request.sid
    with _channels_lock:
        channel = _channels.get(sid)
    if channel is not None:
        channel.submit(value)


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
