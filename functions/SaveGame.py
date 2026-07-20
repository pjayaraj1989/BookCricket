"""
Persist an in-progress match to disk so it can be resumed after the server
(or console) is closed mid-game.

The whole Match -> Team -> Player object graph is pickled at every over
boundary (and at each innings boundary), which captures essentially all of
the match state - scores, the batting pair, the current bowler and bowlers'
spells, fall of wickets, targets, rain/DLS state, milestone trackers, and
the save cursor the resume logic needs. A small JSON sidecar holds
human-readable metadata (teams, score, over, timestamp) so the "resume"
picker can list saves without unpickling every file.

Security: loading a pickle runs whatever the pickle says to construct, so
uploaded/foreign save files are a code-execution risk. Loads therefore go
through _SafeUnpickler, which only permits this game's own classes (modules
under functions./data.) plus a small set of harmless builtins - enough to
rebuild a match, not enough to import os and run a command.
"""
import io
import json
import os
import pickle
import time
import uuid

# saves live in <project_root>/saves. functions/ is one level down from root.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVES_DIR = os.path.join(_ROOT, "saves")

# bump when the pickled shape changes incompatibly; resume refuses mismatches
SAVE_FORMAT_VERSION = 1

# Exactly what a saved match's object graph is allowed to reconstruct:
#  - the game's own data classes (plain attribute holders),
#  - the builtins/reconstructors the pickle machinery needs for containers,
#  - numpy's data-only scalar/array reconstructors (the engine leaves the odd
#    numpy int/float on objects, e.g. from numpy.random.choice).
# Nothing here executes arbitrary code. This is an explicit allow-list rather
# than a module-prefix match on purpose: allowing all of functions.* would let
# a crafted save reference callables like functions.utilities.Error_Exit
# (a process-exit DoS) via a pickle reduce.
_ALLOWED = {
    "functions.Base.Match": {"Match"},
    "functions.Base.Team": {"Team"},
    "functions.Base.Player": {"Player"},
    "functions.Base.PlayerAttr": {"PlayerAttr"},
    "functions.helper": {
        "Venue", "Result", "InningsSummary", "Fow", "Partnership",
        "Delivery", "Shot", "Innings", "Tournament",
    },
    "builtins": {
        "list", "dict", "set", "frozenset", "tuple", "object", "bytearray",
        "complex", "bool", "int", "float", "str", "bytes",
    },
    "copyreg": {"_reconstructor", "__newobj__"},
    "collections": {"OrderedDict", "defaultdict"},
    "numpy": {"dtype", "ndarray"},
    "numpy.core.multiarray": {"scalar", "_reconstruct"},
    "numpy._core.multiarray": {"scalar", "_reconstruct"},
}


class SaveLoadError(Exception):
    """A save file could not be read/validated/reconstructed safely."""


class _SafeUnpickler(pickle.Unpickler):
    """Unpickler that only resolves this game's own classes and a short
    allow-list of harmless builtins, so a hand-crafted/uploaded save file
    cannot be used to execute arbitrary code on load."""

    def find_class(self, module, name):
        if name in _ALLOWED.get(module, ()):
            return super().find_class(module, name)
        raise SaveLoadError(
            "Refusing to load disallowed type %s.%s from save file" % (module, name)
        )


def _ensure_dir():
    if not os.path.isdir(SAVES_DIR):
        os.makedirs(SAVES_DIR, exist_ok=True)


def new_save_id():
    """A short, unique id used for this match's save file names."""
    return uuid.uuid4().hex[:12]


def _paths(save_id):
    return (
        os.path.join(SAVES_DIR, "%s.pkl" % save_id),
        os.path.join(SAVES_DIR, "%s.json" % save_id),
    )


def save_match(match):
    """
    Write (or overwrite) the save files for this match. The pickle is written
    to a temp file and atomically renamed, so a crash mid-write can never
    leave a half-written save that resume would choke on.

    Args:
        match: the live Match. Must carry a `save_id` (set when the match
            started); a metadata dict is taken from match.SaveMeta().

    Returns:
        str: the save id.
    """
    _ensure_dir()
    save_id = match.save_id
    pkl_path, json_path = _paths(save_id)

    blob = pickle.dumps(match, protocol=pickle.HIGHEST_PROTOCOL)

    tmp = pkl_path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(blob)
    os.replace(tmp, pkl_path)

    meta = match.SaveMeta()
    meta["version"] = SAVE_FORMAT_VERSION
    meta["id"] = save_id
    meta["updated"] = time.time()
    tmp = json_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(meta, f)
    os.replace(tmp, json_path)
    return save_id


def _reconstruct(blob):
    match = _SafeUnpickler(io.BytesIO(blob)).load()
    if getattr(match, "match_type", None) is None and not hasattr(match, "team1"):
        raise SaveLoadError("Save file does not contain a match")
    return match


def load_match(save_id):
    """Load and safely reconstruct a saved Match by id."""
    pkl_path, _ = _paths(save_id)
    if not os.path.isfile(pkl_path):
        raise SaveLoadError("No save found with id %s" % save_id)
    with open(pkl_path, "rb") as f:
        blob = f.read()
    return _reconstruct(blob)


def load_match_bytes(blob):
    """Load a Match from raw pickle bytes (an uploaded save file)."""
    if not blob:
        raise SaveLoadError("Empty save file")
    try:
        return _reconstruct(blob)
    except SaveLoadError:
        raise
    except Exception as exc:  # malformed pickle, truncated upload, etc.
        raise SaveLoadError("Could not read save file: %s" % exc)


def list_saves(client_id=None):
    """
    Metadata for saves on disk, newest first, read from the JSON sidecars (no
    unpickling). A sidecar whose .pkl has gone missing, or that is unreadable,
    is skipped.

    Args:
        client_id: when given, only saves owned by that browser/client are
            returned (web isolation). None returns every save (console/CLI).

    Returns:
        list[dict]
    """
    _ensure_dir()
    saves = []
    for name in os.listdir(SAVES_DIR):
        if not name.endswith(".json"):
            continue
        save_id = name[: -len(".json")]
        pkl_path, json_path = _paths(save_id)
        if not os.path.isfile(pkl_path):
            continue
        try:
            with open(json_path) as f:
                meta = json.load(f)
        except (ValueError, OSError):
            continue
        meta.setdefault("id", save_id)
        if client_id is not None and meta.get("clientId") != client_id:
            continue
        saves.append(meta)
    saves.sort(key=lambda m: m.get("updated", 0), reverse=True)
    return saves


def delete_save(save_id):
    """Remove a save's files. Silent if they're already gone."""
    for path in _paths(save_id):
        try:
            os.remove(path)
        except OSError:
            pass


def describe(meta):
    """A one-line human label for a save, for the console/CLI picker."""
    score = "%s/%s" % (meta.get("score", 0), meta.get("wickets", 0))
    who = meta.get("batting_team", "?")
    situation = meta.get("situation", "")
    fmt = meta.get("match_type", meta.get("format", ""))
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(meta.get("updated", 0)))
    return "%s v %s (%s) - %s %s, %s [%s]" % (
        meta.get("team1", "?"),
        meta.get("team2", "?"),
        fmt,
        who,
        score,
        situation,
        when,
    )
