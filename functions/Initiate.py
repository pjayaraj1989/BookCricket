# functions to initiate the game

# read venue data
import json
from data.resources import *
from data.commentary import *
from functions.DisplayScores import DisplayPlayingXI
from functions.helper import Venue, Team, Player, Match
from functions.utilities import ChooseFromOptions, PrintInColor, Randomize, Error_Exit
import random
from numpy.random import choice
from colorama import Fore, Style


def GetVenue(venue_data):
    f = open(venue_data)
    data = json.load(f)
    if data is None:
        Error_Exit("No data read from file %s" % f)
    countries = data['Venues']

    # now get venues for each countries
    country = ChooseFromOptions(list(countries.keys()), "Select Venue", 5)

    # now get venues in this
    venue = random.choice(countries[country]['places'])
    print("Selected Stadium: %s" % venue['name'])
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
    Teams_List = []
    f = open(json_file)
    data = json.load(f)
    if data is not None:
        # read values for the key 'teams'
        teams = data['Teams']
        for k, v in teams.items():
            # create teams
            t = Team(name=k)
            # now create team array from the array of values
            for plr in v['players']:
                p = Player(name=plr['name'])
                if 'batting' in plr:
                    p.attr.batting = plr['batting']
                if 'bowling' in plr:
                    p.attr.bowling = plr['bowling']
                if 'spinner' in plr and plr['spinner'] == 1:
                    p.attr.isspinner = True
                if 'pacer' in plr and plr['pacer'] == 1:
                    p.attr.ispacer = True

                # assign keeper and captain
                if 'keeper' in plr and plr['keeper'] == 1:
                    p.attr.iskeeper = True
                    t.keeper = p
                if 'captain' in plr and plr['captain'] == 1:
                    p.attr.iscaptain = True
                    t.captain = p
                if 'openingbowler' in plr and plr['openingbowler'] == 1:
                    p.attr.isopeningbowler = True

                # read nicknames if any
                if 'nickname' in plr and plr['nickname'] != '' or None:
                    p.nickname = plr['nickname']

                t.team_array.append(p)

            t.key = v["key"]
            t.opening_pair = [t.team_array[0], t.team_array[1]]
            # assign color
            t.color = resources.color_map[v["color"]]
            Teams_List.append(t)

    return Teams_List


# get match info
def GetMatchInfo(list_of_teams, venue):
    intro = Randomize(commentary.intro_dialogues)
    commentator = random.sample(set(resources.commentators), 3)
    umpire = random.sample(set(resources.umpires), 2)

    # get list of teams
    teams = [team.key for team in list_of_teams]

    # select overs
    overs = input('Select overs (multiple of 5)\n')

    # if not multiple of 5 or invalid entry, it selects default (5 overs)
    if (not overs.isdigit()) or \
            (int(overs) % 5 != 0) or \
            (int(overs) > 50) or \
            (int(overs) <= 0):
        overs = 5
        print("Invalid entry, default %s overs selected" % overs)

    overs = int(overs)
    # max overs allotted for each bowler
    bowler_max_overs = overs / 5

    # input teams
    t1 = ChooseFromOptions(teams, "Select your team", 5)
    teams.remove(t1)
    t2 = ChooseFromOptions(teams, 'Select opponent', 5)
    print('Selected %s and %s' % (t1, t2))

    # find teams from user input
    for t in list_of_teams:
        if t.key == t1:
            team1 = t
        if t.key == t2:
            team2 = t

    match_type = str(overs) + ' overs'

    if overs == 50:
        match_type = 'ODI'
    elif overs == 20:
        match_type = 'T20'
    elif overs == 5:
        match_type = 'Exhibition'

    # initialize match with teams, overs
    match = Match(team1=team1,
                  team2=team2,
                  overs=overs,
                  match_type=match_type,
                  venue=venue,
                  bowler_max_overs=bowler_max_overs,
                  umpire=umpire[0],
                  result=None)

    match_descriptions = ['exciting', 'most awaited', 'much awaited', ]
    msg = '%s, %s, for the %s %s match between %s and %s' % (intro,
                                                             venue.name,
                                                             Randomize(match_descriptions),
                                                             match.match_type,
                                                             team1.name,
                                                             team2.name,)
    PrintInColor(msg, Fore.LIGHTCYAN_EX)

    print('In the commentary box, myself %s with %s, and %s' % (commentator[0],
                                                                commentator[1],
                                                                commentator[2],
                                                                ))
    print('Umpires: %s and %s' % (umpire[0], umpire[1]))
    input('press enter to continue..')

    # set overs to team also
    for t in [match.team1, match.team2]:
        t.total_overs = match.overs

    # display squad
    DisplayPlayingXI(match)

    return match


# toss
def Toss(match):
    logger = match.logger
    print('Toss..')
    print('We have the captains %s(%s) and %s(%s) in the middle' % (match.team1.captain.name,
                                                                    match.team1.name,
                                                                    match.team2.captain.name,
                                                                    match.team2.name))

    print('%s is gonna flip the coin' % match.team2.captain.name)
    opts = ['1', '2']
    call = input('%s, your call, Heads or tails? 1.Heads 2.Tails\n' % match.team1.captain.name)
    if call == '' or call not in opts:
        call = Randomize(opts)
        print("Invalid choice!..auto-selected")
    call = int(call)
    coin = Randomize([1, 2])
    coin = int(coin)
    if coin == call:
        msg = '%s won the toss, elected to bat first' % match.team1.captain.name
        PrintInColor(msg, match.team1.color)
        logger.info(msg)
        match.team1.batting_second = False
        match.team2.batting_second = True
    else:
        msg = '%s won the toss, elected to bat first' % match.team2.captain.name
        PrintInColor(msg, match.team2.color)
        logger.info(msg)
        match.team2.batting_second = False
        match.team1.batting_second = True
    # now find out who is batting first
    batting_first = next((x for x in [match.team1, match.team2] if not x.batting_second), None)
    batting_second = next((x for x in [match.team1, match.team2] if x.batting_second), None)
    match.batting_first = batting_first
    match.batting_second = batting_second

    # do you need DRS?
    drs_opted = ChooseFromOptions(['y','n'], "Do you need DRS for this match? ", 5)
    if drs_opted == 'y':
        print("DRS opted")
        match.drs = True
        input("press enter to continue")

    match.status = True

    return match


# validate teams
def ValidateMatchTeams(match):
    if match.team1 is None or match.team2 is None:
        Error_Exit('No teams found!')

    for t in [match.team1, match.team2]:
        # check if 11 players
        if len(t.team_array) != 11:
            Error_Exit('Only %s members in team %s' % (len(t.team_array), t.name))

        # check if keeper exists
        if t.keeper is None:
            Error_Exit('No keeper found in team %s' % t.name)

        # check if more than one keeper or captain
        if len([plr for plr in t.team_array if plr.attr.iskeeper]) > 1:
            Error_Exit("More than one keeper found")
        if len([plr for plr in t.team_array if plr.attr.iscaptain]) > 1:
            Error_Exit("More than one captain found")

        # check for captain
        if t.captain is None:
            Error_Exit('No captain found in team %s' % t.name)

        # get bowlers who has bowling attribute
        bowlers = [plr for plr in t.team_array if plr.attr.bowling > 0]
        if len(bowlers) < 6:
            Error_Exit('Team %s should have 6 bowlers in the playing XI' % t.name)
        else:
            t.bowlers = bowlers
            # assign max overs for bowlers
            for bowler in t.bowlers:
                bowler.max_overs = match.bowler_max_overs

    # ensure no common members in the teams
    common_players = list(set(match.team1.team_array).intersection(match.team2.team_array))
    if common_players:
        Error_Exit("Common players in teams found! : %s" % (','.join([p.name for p in common_players])))

    # make first batsman on strike
    for t in [match.team1, match.team2]:
        t.opening_pair[0].onstrike, t.opening_pair[1].onstrike = True, False
        t.opening_pair[0].onfield, t.opening_pair[1].onfield = True, True

    # check if players have numbers, else assign randomly
    for t in [match.team1, match.team2]:
        for player in t.team_array:
            if player.no is None:
                player.no = random.choice(list(range(100)))

    PrintInColor('Validated teams', Style.BRIGHT)
