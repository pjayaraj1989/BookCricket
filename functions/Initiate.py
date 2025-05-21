# functions to initiate the game

# read venue data
import json

from BookCricket import data_path, venue_data
from data.resources import *
from data.commentary import *
from functions.helper import Venue
from functions.Base.Player import Player
from functions.Base.Match import Match
from functions.Base.Team import Team
from functions.utilities import ChooseFromOptions, PrintInColor, Randomize, Error_Exit
import random
from numpy.random import choice
from colorama import Fore, Style
import os


def GetVenue(venue_data):
    """
    Get the venue for the match by letting user choose.

    Args:
        venue_data: The path to the venue data file.

    Returns:
        A Venue object with the selected venue details.
    """
    f = open(venue_data)
    data = json.load(f)
    if data is None:
        Error_Exit("No data read from file %s" % f)
    countries = data['Venues']

    # now get venues for each countries
    country = ChooseFromOptions(list(countries.keys()), "Select Country", 5)

    # Let user choose from available venues in the country
    venues = countries[country]['places']
    venue_names = [venue['name'] for venue in venues]
    msg = "Select Stadium"
    selected_venue_name = ChooseFromOptions(venue_names, msg, 5)
    
    # Get the selected venue details
    venue = next((v for v in venues if v['name'] == selected_venue_name), None)
    
    PrintInColor("Selected Stadium: %s" % venue['name'], Style.BRIGHT)
    venue_obj = Venue(name=venue['name'], run_prob=venue['run_prob'])

    # populate run_prob_t20
    run_prob_t20 = data['run_prob_t20']
    venue_obj.run_prob_t20 = run_prob_t20

    # choose weather
    weather = choice(list(resources.weathers.keys()), 1, p=resources.weather_prob, replace=False)[0]
    venue_obj.weather = weather
    PrintInColor(resources.weathers[weather], Style.BRIGHT)

    return venue_obj


# read teams and
def ReadTeams(json_file):
    """
    Read the teams from a JSON file.

    Args:
        json_file: The path to the JSON file containing team data.

    Returns:
        A list of Team objects.
    """
    Teams_List = []
    f = open(json_file)
    data = json.load(f)
    if data is not None:
        # read values for the key 'teams'
        teams = data["Teams"]
        for k, v in teams.items():
            # create teams
            t = Team(name=k)
            # now create team array from the array of values
            for plr in v["players"]:
                p = Player(name=plr["name"])
                if "batting" in plr:
                    p.attr.batting = plr["batting"]
                if "bowling" in plr:
                    p.attr.bowling = plr["bowling"]
                if "spinner" in plr and plr["spinner"] == 1:
                    p.attr.isspinner = True
                if "pacer" in plr and plr["pacer"] == 1:
                    p.attr.ispacer = True

                # assign keeper and captain
                if "keeper" in plr and plr["keeper"] == 1:
                    p.attr.iskeeper = True
                    t.keeper = p
                if "captain" in plr and plr["captain"] == 1:
                    p.attr.iscaptain = True
                    t.captain = p
                if "openingbowler" in plr and plr["openingbowler"] == 1:
                    p.attr.isopeningbowler = True

                # read nicknames if any
                if "nickname" in plr and plr["nickname"] != "" or None:
                    p.nickname = plr["nickname"]

                t.team_array.append(p)

            t.key = v["key"]
            t.opening_pair = [t.team_array[0], t.team_array[1]]
            # assign color
            t.color = resources.color_map[v["color"]]
            Teams_List.append(t)

    return Teams_List


# read data from data files
def ReadData():
    """
    Read the data for the match, including teams and venue.

    Returns:
        A tuple containing a list of Team objects and a Venue object.
    """
    # input teams to play    # now get the json files available
    json_files = [
        f
        for f in os.listdir(data_path)
        if (f.startswith("teams_") and f.endswith(".json"))
    ]
    leagues = [json_file.lstrip("teams_").strip(".json") for json_file in json_files]
    # welcome text
    PrintInColor(commentary.intro_game, Style.BRIGHT)
    league = ChooseFromOptions(leagues, "Choose league", 5)
    data_file = [json_file for json_file in json_files if league in json_file][0]
    team_data = os.path.join(data_path, data_file)
    teams = ReadTeams(team_data)
    # now read venue data
    venue = GetVenue(venue_data)
    return teams, venue


# get match info
def GetMatchInfo(list_of_teams, venue):
    """
    Get the match information, including teams, venue, and match type.

    Args:
        list_of_teams: A list of Team objects.
        venue: A Venue object.

    Returns:
        A Match object with the match details.
    """
    intro = Randomize(commentary.intro_dialogues)
    commentator = random.choices(list(resources.commentators), k=3)
    umpire = random.choices(list(resources.umpires), k=2)

    # get list of teams
    teams = [team.key for team in list_of_teams]

    # select overs
    msg = "Select overs (multiple of 5)"
    PrintInColor(msg, Style.BRIGHT)
    overs = input()

    # if not multiple of 5 or invalid entry, it selects default (5 overs)
    if (
        (not overs.isdigit())
        or (int(overs) % 5 != 0)
        or (int(overs) > 50)
        or (int(overs) <= 0)
    ):
        overs = 5
        print("Invalid entry, default %s overs selected" % overs)

    overs = int(overs)
    # max overs allotted for each bowler
    bowler_max_overs = overs / 5

    # input teams
    msg = "Select your team"
    PrintInColor(msg, Style.BRIGHT)
    t1 = ChooseFromOptions(teams, "", 5)
    teams.remove(t1)
    msg = "Select opponent"
    t2 = ChooseFromOptions(teams, "", 5)
    print("Selected %s and %s" % (t1, t2))

    # find teams from user input
    for t in list_of_teams:
        if t.key == t1:
            team1 = t
        if t.key == t2:
            team2 = t

    match_type = str(overs) + " overs"

    if overs == 50:
        match_type = "ODI"
    elif overs == 20:
        match_type = "T20"
    elif overs == 5:
        match_type = "Exhibition"

    # initialize match with teams, overs
    match = Match(
        team1=team1,
        team2=team2,
        overs=overs,
        match_type=match_type,
        venue=venue,
        bowler_max_overs=bowler_max_overs,
        umpire=umpire[0],
        result=None,
    )

    match_descriptions = [
        "exciting",
        "most awaited",
        "much anticipated",
    ]
    msg = "%s, %s, for the %s %s match between %s and %s" % (
        intro,
        venue.name,
        Randomize(match_descriptions),
        match.match_type,
        team1.name,
        team2.name,
    )
    PrintInColor(msg, Fore.LIGHTCYAN_EX)

    PrintInColor(
        "In the commentary box, myself %s with %s, and %s"
        % (
            commentator[0],
            commentator[1],
            commentator[2],
        ),
        Style.BRIGHT,
    )
    PrintInColor(
        "Umpires for todays match are %s and %s" % (umpire[0], umpire[1]), Style.BRIGHT
    )
    input("press enter to continue..")

    # set overs to team also
    for t in [match.team1, match.team2]:
        t.total_overs = match.overs

    # display squad
    match.DisplayPlayingXI()

    return match
