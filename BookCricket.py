#! /usr/bin/env python3
from functions.Initiate import *
import os

ScriptPath = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(ScriptPath, "data")
venue_data = os.path.join(data_path, "venue_data.json")

if __name__ == "__main__":
    while True:
        # opt for commentary
        commentary_enabled = input("Enable commentary? yY/nN")
        # make this a global variable
        if commentary_enabled.lower() == "y":
            commentary_enabled = True
        elif commentary_enabled.lower() == "n":
            commentary_enabled = False
        else:
            exit("Invalid input, choose y or n")

        # write this commentary_enabled to a config file
        f = open("commentary_enabled.txt", "w")
        f.write(str(commentary_enabled))
        f.close()

        teams, venue = ReadData()
        match = GetMatchInfo(teams, venue)
        match.PlayMatch(ScriptPath)
        while True:
            opt = input("Play again? y/n")
            if opt.lower() in ["y", "n"]:
                break
            print("Invalid input")
        if opt.lower() == "y":
            continue
        else:
            break
    msg = "Thanks for playing, goodbye!"
    PrintInColor(msg, Style.BRIGHT)
