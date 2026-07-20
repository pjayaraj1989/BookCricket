#! /usr/bin/env python3
import os
import sys

# defined before the functions.Initiate import below: functions/Initiate.py does
# `from BookCricket import data_path, venue_data`, which needs these to already
# exist on this module by the time that import runs.
ScriptPath = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(ScriptPath, 'data')
venue_data = os.path.join(data_path, 'venue_data.json')

from functions.Initiate import *
import functions.SaveGame as SaveGame
import functions.Tournament as Tournament
from functions.utilities import ChooseFromOptions, IsWebMode

# Define commentary_enabled as a global variable
commentary_enabled = False


def _resume_saved_match(save_id=None, save_blob=None):
    """
    Load a saved match for resume. `save_blob` (raw pickle bytes of an
    uploaded save) takes precedence over `save_id` (a save on this server).
    Returns a reconstructed Match, or None if it couldn't be loaded.
    """
    try:
        if save_blob is not None:
            return SaveGame.load_match_bytes(save_blob)
        if save_id:
            return SaveGame.load_match(save_id)
    except SaveGame.SaveLoadError as exc:
        PrintInColor("Could not load that saved game: %s" % exc, Style.BRIGHT)
    return None


def _resume_saved_tournament(save_id):
    """Load a saved tournament for resume, or None if it can't be loaded."""
    try:
        return SaveGame.load_tournament(save_id)
    except SaveGame.SaveLoadError as exc:
        PrintInColor("Could not load that series: %s" % exc, Style.BRIGHT)
    return None


def _play_match(match, save_owner, commentary_enabled, resume=False):
    match.fast = match.fast or False
    match.save_enabled = True
    match.save_client_id = save_owner
    match.commentary_enabled = commentary_enabled
    if resume:
        match.autoplay = False
        match.ResumeMatch(ScriptPath)
    else:
        match.PlayMatch(ScriptPath)


def _play_series(t, fast, save_owner, resume=False):
    t.autoplay = False
    t.fast = fast
    t.save_enabled = True
    t.save_client_id = save_owner
    t.resuming = resume
    if not t.save_id:
        t.save_id = SaveGame.new_save_id()
    t.play(ScriptPath)


def _console_start_menu():
    """
    Console startup menu: New game / New series, plus one entry per resumable
    saved match and saved series. Returns (action, save_id) where action is
    one of new_match, new_series, resume_match, resume_series.
    """
    matches = SaveGame.list_saves(kind="match")
    tours = SaveGame.list_saves(kind="tournament")
    options = ["New game", "New series/tournament"]
    targets = [("new_match", None), ("new_series", None)]
    for m in matches:
        options.append("Resume match - " + SaveGame.describe(m))
        targets.append(("resume_match", m["id"]))
    for t in tours:
        options.append("Resume series - " + SaveGame.describe(t))
        targets.append(("resume_series", t["id"]))
    if len(options) == 2:
        # nothing to resume: still offer new game vs new series
        pick = ChooseFromOptions(options, "What would you like to do?", 5)
        return targets[options.index(pick)]
    pick = ChooseFromOptions(options, "What would you like to do?", 5)
    return targets[options.index(pick)]


def run_game(autoplay=False, overs=None, format_override=None, fast=False,
             resume_id=None, resume_blob=None, save_owner=None,
             series=False, resume_kind="match"):
    """
    Play interactive rounds of BookCricket until the player chooses to stop.

    Reusable by both the CLI entrypoint below and the web app (web/app.py),
    which drives the same input()/print() calls over a websocket instead of
    a terminal.

    Args:
        format_override: "test" forces a Test match under autoplay, which
            can't otherwise reach the interactive format menu.
        fast: skip PlayOver's per-ball sleep even under autoplay (dev/test
            use only - a real Test match's day budget makes that sleep add
            up to many minutes otherwise).
        resume_id: id of a server-side save to resume (web resume). Consumed
            once, on the first round; later "play again" rounds start fresh.
        resume_blob: raw pickle bytes of an uploaded save to resume, taking
            precedence over resume_id.
        series: start a new series/tournament (web "Series" choice).
        resume_kind: "match" or "tournament" - which kind resume_id refers to.
    """
    # a resume/series requested by the caller (web) applies only to the first
    # round; later "play again" rounds fall back to a fresh single match
    pending_resume_id = resume_id
    pending_resume_blob = resume_blob
    pending_resume_kind = resume_kind
    pending_series = series

    while True:
        # commentary (text-to-speech) prompt removed for now - always off
        commentary_enabled = False

        # clear the web UI's side pane so a replayed match doesn't show the
        # previous one's scorecard/innings/run-rate (no-op in console mode)
        PushMatchReset()

        handled = False
        if not autoplay:
            if pending_series:
                t = Tournament.SetupSeries()
                if t is not None:
                    _play_series(t, fast, save_owner)
                    handled = True
            elif pending_resume_id or pending_resume_blob is not None:
                if pending_resume_kind == "tournament":
                    t = _resume_saved_tournament(pending_resume_id)
                    if t is not None:
                        _play_series(t, fast, save_owner, resume=True)
                        handled = True
                else:
                    rm = _resume_saved_match(pending_resume_id, pending_resume_blob)
                    if rm is not None:
                        _play_match(rm, save_owner, commentary_enabled, resume=True)
                        handled = True
            elif not IsWebMode():
                action, sid = _console_start_menu()
                if action == "new_series":
                    t = Tournament.SetupSeries()
                    if t is not None:
                        _play_series(t, fast, save_owner)
                        handled = True
                elif action == "resume_series":
                    t = _resume_saved_tournament(sid)
                    if t is not None:
                        _play_series(t, fast, save_owner, resume=True)
                        handled = True
                elif action == "resume_match":
                    rm = _resume_saved_match(save_id=sid)
                    if rm is not None:
                        _play_match(rm, save_owner, commentary_enabled, resume=True)
                        handled = True
        pending_series = False
        pending_resume_id = None
        pending_resume_blob = None

        if not handled:
            teams, venue, match_format = ReadData(autoplay, format_override)
            match = GetMatchInfo(teams, venue, autoplay, overs, format_override, fast, match_format)
            match.commentary_enabled = commentary_enabled
            # real (non-autoplay) games auto-save every over for resume
            match.save_enabled = not autoplay
            match.save_client_id = save_owner
            match.PlayMatch(ScriptPath)
        while True:
            if autoplay:
                opt = 'n'
                break
            opt = input("Play again? y/n")
            if opt.lower() in ['y', 'n']:
                break
            print("Invalid input")
        if opt.lower() == 'y':
            continue
        else:
            break
    msg = "Thanks for playing, goodbye!"
    PrintInColor(msg, Style.BRIGHT)
    if not autoplay:
        input("Press enter to exit...")


if __name__ == "__main__":
    overs = None
    format_override = None
    fast = False
    # check if an argument is passed for autoplay
    # usage: BookCricket.py autoplay <overs> [test] [fast]
    if len(sys.argv) > 2 and sys.argv[1] == 'autoplay':
        autoplay = True
        overs = sys.argv[2]
        extra_args = [a.lower() for a in sys.argv[3:]]
        if 'test' in extra_args:
            format_override = 'test'
        if 'fast' in extra_args:
            fast = True
    else:
        autoplay = False
    run_game(autoplay, overs, format_override, fast)
    if autoplay:
        sys.exit()