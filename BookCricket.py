#! /usr/bin/env python3
from functions.Initiate import *
import os
import sys

ScriptPath = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(ScriptPath, 'data')
venue_data = os.path.join(data_path, 'venue_data.json')

# Define commentary_enabled as a global variable
commentary_enabled = False

if __name__ == "__main__":
    # check if an argument is passed for autoplay
    if len(sys.argv) == 2 and sys.argv[1] == 'autoplay':
        autoplay = True
    else:
        autoplay = False
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
        match = GetMatchInfo(teams, venue, autoplay)
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
    else:
        sys.exit()