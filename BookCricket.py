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

# Define commentary_enabled as a global variable
commentary_enabled = False

def run_game(autoplay=False, overs=None):
    """
    Play interactive rounds of BookCricket until the player chooses to stop.

    Reusable by both the CLI entrypoint below and the web app (web/app.py),
    which drives the same input()/print() calls over a websocket instead of
    a terminal.
    """
    while True:
        # opt for commentary
        if autoplay:
            commentary_enabled = 'n'
        else:
            commentary_enabled = input("Enable commentary? y/n")
        # make this a global variable
        if commentary_enabled.lower() == 'y':   commentary_enabled = True
        else:   commentary_enabled = False

        teams, venue = ReadData(autoplay)
        match = GetMatchInfo(teams, venue, autoplay, overs)
        match.commentary_enabled = commentary_enabled
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
    # check if an argument is passed for autoplay
    if len(sys.argv) > 2 and sys.argv[1] == 'autoplay':
        autoplay = True
        overs = sys.argv[2]
    else:
        autoplay = False
    run_game(autoplay, overs)
    if autoplay:
        sys.exit()