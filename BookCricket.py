#! /usr/bin/env python3
from functions.Initiate import *
import os

ScriptPath = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(ScriptPath, 'data')
venue_data = os.path.join(data_path, 'venue_data.json')

if __name__ == "__main__":
    while True:
        teams, venue = ReadData()
        match = GetMatchInfo(teams, venue)
        match.PlayMatch(ScriptPath)
        while True:
            opt = input("Play again? y/n")
            if opt.lower() in ['y', 'n']:
                break
            print("Invalid input")
        if opt.lower() == 'y':
            continue
        else:
            break
    input("Thanks for playing, goodbye!")
