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


def _offer_console_resume():
    """
    Console-only startup menu: if any saved games exist, ask whether to start
    a new match or resume one, and let the player pick from the list. Returns
    a reconstructed Match to resume, or None to start a fresh match.
    """
    saves = SaveGame.list_saves()
    if not saves:
        return None
    choice = ChooseFromOptions(
        ["New game", "Resume a saved game"], "Start a new game or resume a saved one?", 5
    )
    if choice != "Resume a saved game":
        return None
    labels = [SaveGame.describe(m) for m in saves] + ["Back (start a new game)"]
    picked = ChooseFromOptions(labels, "Pick a saved game to resume", 5)
    if picked is None or picked.startswith("Back"):
        return None
    save_id = saves[labels.index(picked)]["id"]
    return _resume_saved_match(save_id=save_id)


def run_game(autoplay=False, overs=None, format_override=None, fast=False,
             resume_id=None, resume_blob=None, save_owner=None):
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
            once, on the first match; later "play again" rounds start fresh.
        resume_blob: raw pickle bytes of an uploaded save to resume, taking
            precedence over resume_id.
    """
    # a resume requested by the caller (web) applies only to the first match
    pending_resume_id = resume_id
    pending_resume_blob = resume_blob

    while True:
        # commentary (text-to-speech) prompt removed for now - always off
        commentary_enabled = False

        # clear the web UI's side pane so a replayed match doesn't show the
        # previous one's scorecard/innings/run-rate (no-op in console mode)
        PushMatchReset()

        # resume path: caller-supplied save (web), or the console resume menu.
        # Autoplay never resumes (CI plays fresh matches deterministically).
        resume_match = None
        if not autoplay:
            if pending_resume_id or pending_resume_blob is not None:
                resume_match = _resume_saved_match(pending_resume_id, pending_resume_blob)
            elif not IsWebMode():
                resume_match = _offer_console_resume()
        pending_resume_id = None
        pending_resume_blob = None

        if resume_match is not None:
            resume_match.autoplay = False
            resume_match.fast = fast
            resume_match.save_enabled = True
            # (re)tag ownership to the current browser so its future saves stay
            # in that browser's resume list
            resume_match.save_client_id = save_owner
            resume_match.commentary_enabled = commentary_enabled
            resume_match.ResumeMatch(ScriptPath)
        else:
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