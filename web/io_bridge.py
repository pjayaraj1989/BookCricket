# Thread-local I/O bridge so the console game engine (functions/Base/Match.py,
# functions/Initiate.py, etc.) can be driven from a browser over a websocket
# without changing any of its input()/print()/PrintInColor()/ChooseFromOptions()
# call sites. Each browser session runs the game on its own thread; input()/print()
# are patched process-wide, but the patched versions look up a per-thread channel,
# so console usage (no channel set) is unaffected.
import builtins
import queue
import re
import threading
import time

import colorama

_local = threading.local()
_DISCONNECTED = object()
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class GameAborted(Exception):
    """Raised inside a session's game thread to unwind play cleanly on
    disconnect or fatal error, instead of sys.exit()-ing the whole server."""


class WebChannel:
    def __init__(self, emit):
        # emit(event_name, data) sends a message to this session's browser tab.
        self._emit = emit
        self._queue = queue.Queue()
        # acks for event pop-ups: the browser reports when each pop-up has
        # left the screen, so the game thread can stay in sync with what the
        # player is actually watching (see event() below)
        self._ack_queue = queue.Queue()
        self._event_seq = 0
        self._line_buffer = ""
        # set from the socket thread when the GUI's Declare button is pressed;
        # the game thread consumes it at the next over boundary (single bool
        # flip, so no lock needed under the GIL)
        self._declare_requested = False

    def request_declare(self):
        self._declare_requested = True

    def consume_declare_request(self):
        requested = self._declare_requested
        self._declare_requested = False
        return requested

    def output(self, text, color=None):
        self._emit("server_event", {"type": "output", "text": strip_ansi(text), "color": resolve_color(color)})

    def reset(self):
        # tell the browser to clear the side pane (scorecard, innings
        # summaries, run-rate graph) before a fresh match begins.
        self._emit("server_event", {"type": "reset"})

    def state(self, data):
        # structured snapshot for the side-pane scorecard, distinct from the
        # scrolling commentary log; not a request/response, fire-and-forget.
        self._emit("server_event", {"type": "state", "data": data})

    def innings(self, data):
        # full batting/bowling card + fall of wickets, sent once an innings
        # has just finished.
        self._emit("server_event", {"type": "innings", "data": data})

    # how long event() will wait for the browser's pop-up ack before giving
    # up and letting the game continue (a missed ack - old cached app.js,
    # a wedged tab - must never stall the match)
    EVENT_ACK_TIMEOUT = 20.0

    def event(self, kind, data=None):
        # a short-lived highlight for the event pane (toss/wicket/four/six/
        # DRS/rain...), distinct from the scrolling log and the structured
        # scorecard state. Blocks until the browser acks it, so play cannot
        # run ahead of what the player is watching: the browser acks a
        # full-screen "takeover" pop-up only once it leaves the screen, and
        # everything else immediately on receipt.
        self._event_seq += 1
        eid = self._event_seq
        self._emit(
            "server_event",
            {"type": "event", "kind": kind, "data": data or {}, "eid": eid},
        )
        deadline = time.monotonic() + self.EVENT_ACK_TIMEOUT
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return
            try:
                value = self._ack_queue.get(timeout=remaining)
            except queue.Empty:
                return
            if value is _DISCONNECTED:
                raise GameAborted("client disconnected")
            try:
                # monotonic ids: a stale ack for an earlier (timed-out) event
                # is drained and ignored rather than satisfying this wait
                if int(value) >= eid:
                    return
            except (TypeError, ValueError):
                continue

    def ack_event(self, eid):
        # called from the socket thread when the browser reports a pop-up done
        self._ack_queue.put(eid)

    def playing_xi(self, data):
        # persistent two-column playing-XI card (with player pics) for the
        # scrolling log, sent alongside the plain-text elevens table.
        self._emit("server_event", {"type": "xi", "data": data})

    def highlights(self, data):
        # a persistent post-match summary card (result, top scorers/
        # wicket-takers, player of the match), sent once the match is over.
        self._emit("server_event", {"type": "highlights", "data": data})

    def write(self, text, color, end):
        """Console print() calls a line at a time (default end="\\n"), but some
        (e.g. PlotOversBarGraph's ASCII bar chart in functions/utilities.py)
        build a single row across several print(..., end='') calls that only
        make sense concatenated horizontally, as a real terminal would. Buffer
        fragments until a full line (up to a "\\n") is assembled, so each
        browser line matches one console line instead of one print() call."""
        if not self._line_buffer and end == "\n" and "\n" not in text:
            # common case: this call is already a complete, standalone line
            self.output(text, color)
            return
        self._line_buffer += text + end
        while "\n" in self._line_buffer:
            line, self._line_buffer = self._line_buffer.split("\n", 1)
            self.output(line)

    def flush(self):
        if self._line_buffer:
            self.output(self._line_buffer)
            self._line_buffer = ""

    def choose(self, options, msg):
        self._emit("server_event", {"type": "choose", "msg": strip_ansi(msg), "options": list(options)})
        return self._wait()

    def input(self, prompt):
        self._emit("server_event", {"type": "input", "prompt": strip_ansi(str(prompt))})
        return self._wait()

    def submit(self, value):
        self._queue.put(value)

    def close(self):
        self._queue.put(_DISCONNECTED)
        # release the game thread if it is blocked waiting on a pop-up ack
        self._ack_queue.put(_DISCONNECTED)

    def _wait(self):
        value = self._queue.get()
        if value is _DISCONNECTED:
            raise GameAborted("client disconnected")
        return value


# Map colorama's ANSI escape strings back to symbolic names (e.g. "fore-lightcyan_ex",
# "style-bright") so the browser can render them as CSS classes instead of raw escapes.
_COLOR_NAMES = {}
for _mod, _prefix in ((colorama.Fore, "fore"), (colorama.Style, "style")):
    for _name, _value in vars(_mod).items():
        if isinstance(_value, str) and _value.startswith("\x1b"):
            _COLOR_NAMES[_value] = "%s-%s" % (_prefix, _name.lower())


def resolve_color(color):
    if not color:
        return None
    return _COLOR_NAMES.get(color)


def strip_ansi(text):
    """Drop any raw ANSI escape codes that ended up embedded in a message
    (e.g. console code that does print(text, Style.BRIGHT) relies on the
    terminal to interpret the trailing escape; a browser would otherwise
    render its visible remainder, like a stray "[1m", as literal text)."""
    return _ANSI_RE.sub("", str(text))


def get_channel():
    return getattr(_local, "channel", None)


def set_channel(channel):
    _local.channel = channel


def clear_channel():
    _local.channel = None


_original_input = builtins.input
_original_print = builtins.print


def _web_input(prompt=""):
    channel = get_channel()
    if channel is None:
        return _original_input(prompt)
    return channel.input(prompt)


def _web_print(*args, **kwargs):
    channel = get_channel()
    if channel is None or kwargs.get("file") is not None:
        return _original_print(*args, **kwargs)

    # some call sites do print(text, Style.BRIGHT) as a console-only trick to
    # leave the terminal in bold mode, relying on the terminal to interpret
    # the trailing escape rather than passing it through PrintInColor. Treat
    # any bare colorama constant among the args as a color, not literal text.
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    text_parts = []
    color = None
    for a in args:
        s = str(a)
        if color is None and s in _COLOR_NAMES:
            color = s
            continue
        text_parts.append(s)
    channel.write(sep.join(text_parts), color, end)


def install_web_io():
    """Install process-wide input()/print() replacements that redirect to a
    per-thread WebChannel when one is set, and fall back to the real console
    otherwise. Call once, at web app startup."""
    builtins.input = _web_input
    builtins.print = _web_print
