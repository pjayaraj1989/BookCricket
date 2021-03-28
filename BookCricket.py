#! /usr/bin/env python3
from functions.Initiate import ReadTeams, ValidateMatchTeams, Toss, GetMatchInfo, GetVenue
from functions.functions import *
import logging
import os
from functions.results import CalculateResult, FindPlayerOfTheMatch

ScriptPath = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(ScriptPath, 'data')
venue_data = os.path.join(data_path, 'venue_data.json')


def ReadData():
    # input teams to play    # now get the json files available
    json_files = [f for f in os.listdir(data_path) if (f.startswith('teams_') and f.endswith('.json'))]
    leagues = [l.lstrip('teams_').strip('.json') for l in json_files]
    # welcome text
    PrintInColor(commentary.intro_game, Style.BRIGHT)
    league = ChooseFromOptions(leagues, "Choose league", 5)
    data_file = [l for l in json_files if league in l][0]
    team_data = os.path.join(data_path, data_file)
    teams = ReadTeams(team_data)
    # now read venue data
    venue = GetVenue(venue_data)
    return teams, venue


def PlayMatch(match):
    # logging
    log_file = 'log_{0}_v_{1}_{2}_{3}_ovrs.log'.format(match.team1.name,
                                                       match.team2.name,
                                                       match.venue.name.replace(' ', '_'),
                                                       str(match.overs))
    log_folder = os.path.join(ScriptPath, 'logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    log = os.path.join(log_folder, log_file)
    if os.path.isfile(log):
        os.remove(log)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log)
    logger.addHandler(handler)
    # add logger to match
    match.logger = logger
    # see if teams are valid
    ValidateMatchTeams(match)
    # toss, select who is batting first
    match = Toss(match)
    match.team1 = match.batting_first
    match.team2 = match.batting_second
    # play one inns
    # match start
    match.status = True

    match.batting_team = match.team1
    match.bowling_team = match.team2
    Play(match)
    DisplayScore(match, match.team1)
    DisplayBowlingStats(match)
    # play second inns with target
    match.team2.target = match.team1.total_score + 1

    match.batting_team = match.team2
    match.bowling_team = match.team1
    Play(match)
    DisplayScore(match, match.team2)
    DisplayBowlingStats(match)
    match.status = False
    # show results
    CalculateResult(match)
    MatchSummary(match)
    FindPlayerOfTheMatch(match)
    handler.close()


if __name__ == "__main__":
    t = Tournament(name="Friendly")
    while True:
        teams, venue = ReadData()
        match = GetMatchInfo(teams, venue)
        t.teams.append(match.team1)
        t.teams.append(match.team2)
        PlayMatch(match)
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
