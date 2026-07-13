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
        self._line_buffer = ""

    def output(self, text, color=None):
        self._emit("server_event", {"type": "output", "text": strip_ansi(text), "color": resolve_color(color)})

    def state(self, data):
        # structured snapshot for the side-pane scorecard, distinct from the
        # scrolling commentary log; not a request/response, fire-and-forget.
        self._emit("server_event", {"type": "state", "data": data})

    def innings(self, data):
        # full batting/bowling card + fall of wickets, sent once an innings
        # has just finished.
        self._emit("server_event", {"type": "innings", "data": data})

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
