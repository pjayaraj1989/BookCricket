# main routines
import logging
from BookCricket import ScriptPath, venue_data, data_path
from data.resources import *
from data.commentary import *
from functions.DisplayScores import ShowHighlights, DisplayScore, DisplayBowlingStats, MatchSummary, GetCurrentRate, \
    GetRequiredRate
from functions.Initiate import ValidateMatchTeams, Toss, GetVenue, ReadTeams
from functions.helper import *
from functions.results import CalculateResult, FindPlayerOfTheMatch
from functions.utilities import *
from numpy.random import choice
import random
import time


# read data from data files
def ReadData():
    # input teams to play    # now get the json files available
    json_files = [f for f in os.listdir(data_path) if (f.startswith('teams_') and f.endswith('.json'))]
    leagues = [json_file.lstrip('teams_').strip('.json') for json_file in json_files]
    # welcome text
    PrintInColor(commentary.intro_game, Style.BRIGHT)
    league = ChooseFromOptions(leagues, "Choose league", 5)
    data_file = [json_file for json_file in json_files if league in json_file][0]
    team_data = os.path.join(data_path, data_file)
    teams = ReadTeams(team_data)
    # now read venue data
    venue = GetVenue(venue_data)
    return teams, venue


# play match :  start
def PlayMatch(match):
    # logging
    log_file = 'log_%s_v_%s_%s_%s_overs.log' % (match.team1.name,
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
    match.team1, match.team2 = match.batting_first, match.batting_second

    # match start
    match.status = True
    match.batting_team, match.bowling_team = match.team1, match.team2

    # play
    Play(match)

    # display batting and bowling scorecard
    DisplayScore(match, match.team1)
    DisplayBowlingStats(match)

    # play second inns with target
    match.team2.target = match.team1.total_score + 1

    # swap teams now
    match.batting_team, match.bowling_team = match.team2, match.team1

    # play
    Play(match)

    # show batting and bowling scores
    DisplayScore(match, match.team2)
    DisplayBowlingStats(match)

    # match ended
    match.status = False

    # show results
    CalculateResult(match)
    MatchSummary(match)
    FindPlayerOfTheMatch(match)

    # close log handler
    handler.close()

    return


# match abandon due to rain
def MatchAbandon(match):
    batting_team, bowling_team = match.batting_team, match.bowling_team

    # abandon due to rain
    PrintInColor(Randomize(commentary.commentary_rain_interrupt), Style.BRIGHT)
    input("Press any key to continue")

    # check nrr and crr
    nrr = GetRequiredRate(batting_team)
    crr = GetCurrentRate(batting_team)
    result = Result(team1=match.team1, team2=match.team2)

    remaining_overs = match.overs - BallsToOvers(batting_team.total_balls)
    simulated_score = int(round(remaining_overs * crr)) + batting_team.total_score

    result_str = "%s wins by %s run(s) using D/L method!"

    if crr >= nrr:
        # calculate win margin
        result_str = result_str % (batting_team.name, str(abs(simulated_score - batting_team.target)))
    else:
        result_str = result_str % (bowling_team.name, str(abs(batting_team.target - simulated_score)))
    input("Press any key to continue")

    match.status = False
    result.result_str = result_str
    DisplayScore(match, batting_team)
    DisplayBowlingStats(match)

    # change result string
    match.result = result
    MatchSummary(match)
    return


def CheckDRS(match):
    result = False
    team = match.batting_team
    pair = team.current_pair

    if team.drs_chances <= 0:
        PrintInColor(Randomize(commentary.commentary_lbw_nomore_drs), Fore.LIGHTRED_EX)
        return result
    # check if all 4 decisions are taken
    elif team.drs_chances > 0:
        opt = ChooseFromOptions(['y', 'n'],
                                "DRS? %s chance(s) left" % (str(team.drs_chances)),
                                200000)
        if opt == 'n':
            PrintInColor(Randomize(commentary.commentary_lbw_drs_not_taken), Fore.LIGHTRED_EX)
            return result
        else:
            PrintInColor(Randomize(commentary.commentary_lbw_drs_taken) %
                         (GetSurname(pair[0].name), GetSurname(pair[1].name)), Fore.LIGHTGREEN_EX)
            print("Decision pending...")
            time.sleep(5)
            result = random.choice([True, False])
            impact_outside_bat_involved = random.choice([True, False])
            # if not out
            if result:
                # if edged or pitching outside
                if impact_outside_bat_involved:
                    PrintInColor(Randomize(commentary.commentary_lbw_edged_outside), Fore.LIGHTGREEN_EX)
                else:
                    team.drs_chances -= 1
                PrintInColor(Randomize(commentary.commentary_lbw_overturned), Fore.LIGHTGREEN_EX)

            # if out!
            else:
                PrintInColor(Randomize(commentary.commentary_lbw_decision_stays) % match.umpire, Fore.LIGHTRED_EX)
                team.drs_chances -= 1
    return result


# a pair face a delivery
def PairFaceBall(pair, run):
    # find out who is on strike
    if pair[0].onstrike is True and pair[1].onstrike:
        Error_Exit("Error! both cant be on strike!")
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)

    alt_ind = 0
    if ind == 0:
        alt_ind = 1

    pair[ind].runs += run
    pair[ind].balls += 1
    # now if runs is 1 / 3
    if run % 2 != 0:
        pair[ind].onstrike, pair[alt_ind].onstrike = False, True

    return pair


# rotate strike
def RotateStrike(pair):
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)
    alt_ind = 0
    if ind == 0:
        alt_ind = 1

    pair[ind].onstrike = False
    pair[alt_ind].onstrike = True


# batsman out
def BatsmanOut(pair, dismissal):
    # find out who is on strike
    if pair[0].onstrike is True and pair[1].onstrike is True:
        Error_Exit("Error! both cant be on strike!")
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)
    # batsman dismissed
    pair[ind].status = False
    pair[ind].onfield = False
    pair[ind].balls += 1
    pair[ind].strikerate = float((pair[ind].runs / pair[ind].balls) * 100)
    pair[ind].strikerate = round(pair[ind].strikerate, 2)
    # update dismissal mode
    pair[ind].dismissal = dismissal
    return pair


# randomly select a mode of dismissals
def GenerateDismissal(match):
    bowling_team = match.bowling_team
    bowler = bowling_team.current_bowler

    dismissal_str = None
    keeper = next((x for x in bowling_team.team_array if x.attr.iskeeper), None)
    # now get a list of fielders
    fielder = Randomize(bowling_team.team_array)
    # list of mode of dismissals
    if bowler.attr.isspinner:
        dismissal_types = ['c', 'st', 'runout', 'lbw', 'b']
        dismissal_prob = [0.38, 0.2, 0.02, 0.2, 0.2]
    else:
        dismissal_types = ['c', 'runout', 'lbw', 'b']
        dismissal_prob = [0.45, 0.05, 0.25, 0.25]

    # generate dismissal
    dismissal = choice(dismissal_types, 1, p=dismissal_prob, replace=False)[0]
    # generate dismissal string
    if dismissal == 'lbw' or dismissal == 'b':
        dismissal_str = '%s %s' % (dismissal, GetShortName(bowler.name))
    elif dismissal == 'st':
        # stumped
        dismissal_str = 'st %s b %s' % (GetShortName(keeper.name), GetShortName(bowler.name))
    elif dismissal == 'c':
        # check if catcher is the bowler
        if fielder == bowler:
            dismissal_str = 'c&b %s' % (GetShortName(bowler.name))
        else:
            dismissal_str = '%s %s b %s' % (dismissal, GetShortName(fielder.name), GetShortName(bowler.name))
    elif dismissal == 'runout':
        dismissal_str = 'runout %s' % (GetShortName(fielder.name))

    return dismissal_str


# update dismissal
def UpdateDismissal(match, dismissal):
    batting_team, bowling_team = match.batting_team, match.bowling_team
    pair = batting_team.current_pair
    bowler = bowling_team.current_bowler

    if 'runout' in dismissal:
        bowler.ball_history.append('RO')
        batting_team.ball_history.append('RO')
    else:
        # add this to bowlers history
        bowler.ball_history.append('Wkt')
        batting_team.ball_history.append('Wkt')
        bowler.wkts += 1
        # check if he had batted well in the first innings
        if bowler.runs > 50:
            PrintInColor(Randomize(commentary.commentary_all_round_bowler) % bowler.name, bowling_team.color)

    # update wkts, balls, etc
    bowler.balls_bowled += 1
    batting_team.wickets_fell += 1
    batting_team.total_balls += 1
    pair = BatsmanOut(pair, dismissal)
    player_dismissed = next((x for x in pair if not x.status), None)
    player_onstrike = next((x for x in pair if x.status), None)

    # check if player dismissed is captain
    if player_dismissed.attr.iscaptain:
        PrintInColor(Randomize(commentary.commentary_captain_out), bowling_team.color)

    PrintInColor("OUT ! %s %s %s (%s) SR: %s" % (GetShortName(player_dismissed.name),
                                                 player_dismissed.dismissal,
                                                 str(player_dismissed.runs),
                                                 str(player_dismissed.balls),
                                                 str(player_dismissed.strikerate)),
                 Fore.LIGHTRED_EX)

    # show 4s, 6s
    PrintInColor("4s:%s, 6s:%s, 1s:%s, 2s:%s 3s:%s" % (str(player_dismissed.fours),
                                                       str(player_dismissed.sixes),
                                                       str(player_dismissed.singles),
                                                       str(player_dismissed.doubles),
                                                       str(player_dismissed.threes)),
                 Style.BRIGHT)

    # detect a hat-trick!
    arr = [x for x in bowler.ball_history if x != 'WD' or x != 'NB']
    isOnAHattrick = CheckForConsecutiveElements(arr, 'Wkt', 2)
    isHattrick = CheckForConsecutiveElements(arr, 'Wkt', 3)

    if isOnAHattrick:
        PrintInColor(Randomize(commentary.commentary_on_a_hattrick), bowling_team.color)

    if isHattrick:
        bowler.hattricks += 1
        PrintInColor(Randomize(commentary.commentary_hattrick), bowling_team.color)
        input('press enter to continue..')
    if bowler.wkts == 3:
        PrintInColor('Third wkt for %s !' % bowler.name, bowling_team.color)
        input('press enter to continue..')
    # check if bowler got 5 wkts
    if bowler.wkts == 5:
        PrintInColor('Thats 5 Wickets for %s !' % bowler.name, bowling_team.color)
        PrintInColor(Randomize(commentary.commentary_fifer), bowling_team.color)
        input('press enter to continue..')
    # update fall of wicket
    fow_info = Fow(wkt=batting_team.wickets_fell,
                   runs=batting_team.total_score,
                   total_balls=batting_team.total_balls,
                   player_onstrike=player_onstrike,
                   player_dismissed=player_dismissed, )
    # update fall of wkts
    batting_team.fow.append(fow_info)
    # check if 5 wkts gone
    if batting_team.wickets_fell == 5:
        PrintInColor(Randomize(commentary.commentary_five_down), bowling_team.color)

    # get partnership details
    # 1st wkt partnership
    if batting_team.wickets_fell == 1:
        PrintInColor(Randomize(commentary.commentary_one_down), bowling_team.color)
        partnership_runs = batting_team.fow[0].runs
    else:
        partnership_runs = batting_team.fow[batting_team.wickets_fell - 1].runs - batting_team.fow[
            batting_team.wickets_fell - 2].runs
    partnership = Partnership(batsman_dismissed=fow_info.player_dismissed,
                              batsman_onstrike=fow_info.player_onstrike,
                              runs=partnership_runs)
    # update batting team partnership details
    batting_team.partnerships.append(partnership)
    # if partnership is great
    if partnership.runs > 50:
        PrintInColor(Randomize(commentary.commentary_partnership_milestone) % (GetSurname(pair[0].name),
                                                                               GetSurname(pair[1].name)),
                     Style.BRIGHT)

    PrintCommentaryDismissal(match, dismissal)
    # show score
    ShowHighlights(match)
    # get next batsman
    GetNextBatsman(match)
    input('press enter to continue')

    return


# print commentary for dismissal
def PrintCommentaryDismissal(match, dismissal):
    # commentary
    comment = ' '
    pair = match.batting_team.current_pair
    bowler = match.bowling_team.current_bowler

    batting_team, bowling_team = match.batting_team, match.bowling_team
    player_dismissed = next((x for x in pair if not x.status), None)
    player_onstrike = next((x for x in pair if x.status), None)
    keeper = bowling_team.keeper

    if 'runout' in dismissal:
        comment = Randomize(commentary.commentary_runout) % (GetSurname(player_dismissed.name),
                                                             GetSurname(player_onstrike.name))
    elif 'st ' in dismissal:
        comment = Randomize(commentary.commentary_stumped) % GetShortName(keeper.name)
    # if bowler is the catcher
    elif 'c&b' in dismissal:
        comment = Randomize(commentary.commentary_return_catch) % GetSurname(bowler.name)
    elif 'c ' in dismissal and ' b ' in dismissal:
        # see if the catcher is the keeper
        if GetShortName(keeper.name) in dismissal:
            comment = Randomize(commentary.commentary_keeper_catch) % GetSurname(keeper.name)
        else:
            fielder = dismissal.split(' b ')[0].strip('c ')
            comment = Randomize(commentary.commentary_caught) % fielder
    elif 'b ' or 'lbw' in dismissal:
        # reverse swing if > 30 overs
        if 150 <= batting_team.total_balls <= 240 and bowler.attr.ispacer:
            PrintInColor(Randomize(commentary.commentary_reverse), Style.BRIGHT)
        # initial swing
        if batting_team.total_balls < 24 and bowler.attr.ispacer:
            PrintInColor(Randomize(commentary.commentary_swing), Style.BRIGHT)
        # turn
        if bowler.attr.isspinner:
            PrintInColor(Randomize(commentary.commentary_turn), Style.BRIGHT)
        # if lbw
        if 'lbw' in dismissal:
            comment = Randomize(commentary.commentary_lbw) % GetSurname(player_dismissed.name)
        else:
            comment = Randomize(commentary.commentary_bowled)

    # comment dismissal
    PrintInColor(comment, Style.BRIGHT)
    # if he missed a fifty or century
    if 90 <= player_dismissed.runs < 100:
        PrintInColor(Randomize(commentary.commentary_nineties) % GetSurname(player_dismissed.name), Style.BRIGHT)
    # if lost fifty
    if 40 <= player_dismissed.runs < 50:
        PrintInColor(Randomize(commentary.commentary_forties) % GetSurname(player_dismissed.name), Style.BRIGHT)
    # if its a great knock, say this
    if player_dismissed.runs > 50:
        PrintInColor(Randomize(commentary.commentary_out_fifty) % GetSurname(player_dismissed.name), Style.BRIGHT)
    # if duck
    if player_dismissed.runs == 0:
        PrintInColor(Randomize(commentary.commentary_out_duck), Style.BRIGHT)
    # out first ball
    if player_dismissed.balls == 1:
        PrintInColor(Randomize(commentary.commentary_out_first_ball) % GetSurname(player_dismissed.name), Style.BRIGHT)

    # calculate the situation
    if batting_team.batting_second and (7 <= batting_team.wickets_fell < 10):
        PrintInColor(Randomize(commentary.commentary_goingtolose) % batting_team.name, Style.BRIGHT)

    # last man
    if batting_team.wickets_fell == 9:
        PrintInColor(Randomize(commentary.commentary_lastman), batting_team.color)
    return


# assign batsman
def AssignBatsman(match, pair):
    batting_team = match.batting_team
    remaining_batsmen = [plr for plr in batting_team.team_array if (plr.status and plr not in pair)]

    next_batsman = input('Choose next batsman: {0} [Press Enter to auto-select]'.format(
        ' / '.join([str(x.no) + '.' + GetShortName(x.name) for x in remaining_batsmen])))
    batsman = next((x for x in remaining_batsmen if (str(next_batsman) == str(x.no)
                                                     or next_batsman.lower() in GetShortName(x.name).lower())),
                   None)

    if batsman is None:
        Error_Exit("No batsman assigned!")

    return batsman


# get next batsman
def GetNextBatsman(match):
    batting_team = match.batting_team
    pair = batting_team.current_pair
    player_dismissed = next((x for x in pair if not x.status), None)
    if batting_team.wickets_fell < 10:
        ind = pair.index(player_dismissed)

        # choose next one from the team
        pair[ind] = AssignBatsman(match, pair)

        pair[ind].onstrike = True
        PrintInColor("New Batsman: %s" % pair[ind].name, batting_team.color)
        # check if he is captain
        if pair[ind].attr.iscaptain:
            PrintInColor(Randomize(commentary.commentary_captain_to_bat_next), batting_team.color)
        # now new batter on field
        pair[ind].onfield = True

    batting_team.current_pair = pair
    return pair


# play a ball
def Ball(match, run):
    batting_team, bowling_team = match.batting_team, match.bowling_team
    bowler = bowling_team.current_bowler
    logger = match.logger
    pair = batting_team.current_pair

    # get who is on strike
    on_strike = next((x for x in pair if x.onstrike), None)

    # if out
    used_drs = False
    while run == -1:
        dismissal = GenerateDismissal(match)
        if 'lbw' in dismissal:
            PrintInColor(Randomize(commentary.commentary_lbw_umpire) % match.umpire, Fore.LIGHTRED_EX)

            # if match has no DRS, do not go into this
            if match.drs is False:
                UpdateDismissal(match, dismissal)
                return

            # if DRS opted, check
            result = CheckDRS(match)

            # overturn
            if result:
                run = 0
                used_drs = True
                break
            # decision stays
            else:
                UpdateDismissal(match, dismissal)
                return
        else:
            UpdateDismissal(match, dismissal)
            return

    # other than dismissal
    if run != -1:
        # appropriate commentary for 4s and 6s
        if run == 4:
            bowler.ball_history.append(4)
            batting_team.ball_history.append(4)

            # check if first 4 of the innings
            if batting_team.fours == 0:
                PrintInColor(Randomize(commentary.commentary_first_four_team), Fore.LIGHTGREEN_EX)
            batting_team.fours += 1

            field = Randomize(resources.fields[4])
            comment = Randomize(commentary.commentary_four)
            PrintInColor(field + " FOUR! " + comment, Fore.LIGHTGREEN_EX)
            logger.info("FOUR")
            # check if first ball hit for a boundary
            if on_strike.balls == 0:
                PrintInColor(Randomize(commentary.commentary_firstball_four), Fore.LIGHTGREEN_EX)
            # hattrick 4s
            arr = [x for x in bowler.ball_history if x != 'WD']
            if CheckForConsecutiveElements(arr, 4, 3):
                PrintInColor(Randomize(commentary.commentary_in_a_row), Fore.LIGHTGREEN_EX)
            # inc numbers of 4s
            on_strike.fours += 1
        elif run == 6:
            bowler.ball_history.append(6)
            batting_team.ball_history.append(6)

            # check if first six
            if batting_team.sixes == 0:
                PrintInColor(Randomize(commentary.commentary_first_six_team), Fore.LIGHTGREEN_EX)
            batting_team.sixes += 1

            # check uf first ball is hit
            if on_strike.balls == 0:
                PrintInColor(Randomize(commentary.commentary_firstball_six), Fore.LIGHTGREEN_EX)
            # hattrick sixes
            arr = [x for x in bowler.ball_history if x != 'WD']
            if CheckForConsecutiveElements(arr, 6, 3):
                PrintInColor(Randomize(commentary.commentary_in_a_row), Fore.LIGHTGREEN_EX)
            field = Randomize(resources.fields[6])
            comment = Randomize(commentary.commentary_six)
            PrintInColor(field + " SIX! " + comment, Fore.LIGHTGREEN_EX)
            logger.info("SIX")
            # inc number of 6s
            on_strike.sixes += 1
        # dot ball
        elif run == 0:
            bowler.ball_history.append(0)
            batting_team.ball_history.append(0)
            if not used_drs:
                if bowler.attr.ispacer:
                    comment = Randomize(commentary.commentary_dot_ball_pacer) % (GetSurname(bowler.name),
                                                                                 on_strike.name)
                else:
                    comment = Randomize(commentary.commentary_dot_ball) % (GetSurname(bowler.name),
                                                                           GetSurname(on_strike.name))
            else:
                comment = "Decision overturned!"
            print('%s, No Run' % comment)
            logger.info("DOT BALL")
        # ones and twos and threes
        else:
            logger.info(str(run))
            bowler.ball_history.append(run)
            batting_team.ball_history.append(run)
            field = Randomize(resources.fields["ground_shot"])
            comment = Randomize(commentary.commentary_ground_shot)
            if run == 1:
                # detect if its a dropped catch
                catch_drop = Randomize([True, False])
                # get fielders list
                fielder = Randomize([player for player in bowling_team.team_array if player is not bowler])

                # if dropped catch
                if catch_drop is True:
                    dropped_by_keeper_prob = [0.1, 0.9]
                    dropped_by_keeper = choice([True, False], 1, p=dropped_by_keeper_prob, replace=False)[0]
                    if dropped_by_keeper is True:
                        comment = Randomize(commentary.commentary_dropped_keeper) % bowling_team.keeper.name
                    else:
                        comment = Randomize(commentary.commentary_dropped) % fielder.name

                print('%s,%s run' % (comment, str(run)))
            else:
                print('%s,%s %s runs' % (comment, field, str(run)))
            # update 1s and 2s
            if run == 1:
                on_strike.singles += 1
            elif run == 2:
                on_strike.doubles += 1
            elif run == 3:
                on_strike.threes += 1

        # update balls runs
        bowler.balls_bowled += 1
        bowler.runs_given += run
        PairFaceBall(pair, run)
        batting_team.total_balls += 1
        batting_team.total_score += run

        # check for milestones
        CheckMilestone(match)

        # check for ball history

    return


# check ball history so far
def GetBallHistory(match):
    batting_team = match.batting_team
    # check extras
    noballs = batting_team.ball_history.count('NB')
    wides = batting_team.ball_history.count('WD')
    runouts = batting_team.ball_history.count('RO')
    sixes = batting_team.ball_history.count(6)
    fours = batting_team.ball_history.count(4)

    return


# update last partnership
def UpdateLastPartnership(match):
    batting_team = match.batting_team
    pair = batting_team.current_pair

    # update last partnership
    if batting_team.wickets_fell > 0:
        last_fow = batting_team.fow[-1].runs
        last_partnership_runs = batting_team.total_score - last_fow
        last_partnership = Partnership(batsman_dismissed=pair[0],
                                       batsman_onstrike=pair[1],
                                       runs=last_partnership_runs)
        # not all out
        if batting_team.wickets_fell < 10:
            last_partnership.both_notout = True

        batting_team.partnerships.append(last_partnership)
    # if no wkt fell
    elif batting_team.wickets_fell == 0:
        last_partnership_runs = batting_team.total_score
        last_partnership = Partnership(batsman_dismissed=pair[0],
                                       batsman_onstrike=pair[1],
                                       both_notout=True,
                                       runs=last_partnership_runs)
        batting_team.partnerships.append(last_partnership)


# assign bowler
def AssignBowler(match):
    bowler = None
    bowling_team = match.bowling_team
    bowlers = bowling_team.bowlers
    # if first over, opening bowler does it
    if bowling_team.last_bowler is None:
        bowler = next((x for x in bowlers if x.attr.isopeningbowler), None)
    else:
        if bowling_team.last_bowler in bowlers:
            # bowling list except the bowler who did last over and bowlers who finished their allotted overs
            temp = [x for x in bowlers if (x != bowling_team.last_bowler and x.balls_bowled < x.max_overs * 6)]
            # sort this based on skill
            temp = sorted(temp, key=lambda x: x.attr.bowling, reverse=True)
            # if autoplay, let bowlers be chosen randomly
            if match.autoplay:
                bowler = Randomize(temp)
            # else pick bowler
            else:
                next_bowler = input('Pick next bowler: {0} [Press Enter to auto-select]'.format(
                    ' / '.join([str(x.no) + '.' + GetShortName(x.name) for x in temp])))
                bowler = next((x for x in temp if (str(next_bowler) == str(x.no)
                                                   or next_bowler.lower() in GetShortName(x.name).lower())),
                              None)
                if bowler is None:
                    bowler = Randomize(temp)

    if bowler is None:
        Error_Exit("No bowler assigned!")

    return bowler


# get bowler comments
def GetBowlerComments(match):
    bowler = match.bowling_team.current_bowler

    # check if bowler is captain
    if bowler.attr.iscaptain:
        PrintInColor(Randomize(commentary.commentary_captain_to_bowl), Style.BRIGHT)
    # check if spinner or seamer
    if bowler.attr.isspinner:
        PrintInColor(Randomize(commentary.commentary_spinner_into_attack), Style.BRIGHT)
    elif bowler.attr.ispacer:
        PrintInColor(Randomize(commentary.commentary_pacer_into_attack), Style.BRIGHT)
    else:
        PrintInColor(Randomize(commentary.commentary_medium_into_attack), Style.BRIGHT)
    # check if it is his last over!
    if (BallsToOvers(bowler.balls_bowled) == match.bowler_max_overs - 1) and (bowler.balls_bowled != 0):
        PrintInColor(Randomize(commentary.commentary_bowler_last_over), Style.BRIGHT)
        if bowler.wkts >= 3 or bowler.eco <= 5.0:
            PrintInColor(Randomize(commentary.commentary_bowler_good_spell), Style.BRIGHT)
        elif bowler.eco >= 7.0:
            PrintInColor(Randomize(commentary.commentary_bowler_bad_spell), Style.BRIGHT)
    return


# update extras
def UpdateExtras(match):
    batting_team, bowling_team = match.batting_team, match.bowling_team
    bowler = bowling_team.current_bowler

    logger = match.logger
    bowler.runs_given += 1
    batting_team.extras += 1
    batting_team.total_score += 1
    # generate wide or no ball
    extra = random.choice(['wd', 'nb'])
    if extra == 'wd':
        # add this to bowlers history
        bowler.ball_history.append('WD')
        batting_team.ball_history.append('WD')
        PrintInColor("WIDE...!", Fore.LIGHTCYAN_EX)
        PrintInColor(Randomize(commentary.commentary_wide) % match.umpire, Style.BRIGHT)
        logger.info("WIDE")
    elif extra == 'nb':
        # no balls
        bowler.ball_history.append('NB')
        batting_team.ball_history.append('NB')
        PrintInColor("NO BALL...!", Fore.LIGHTCYAN_EX)
        PrintInColor(Randomize(commentary.commentary_no_ball), Style.BRIGHT)
        logger.info("NO BALL")

    return


# generate run
def GenerateRun(match, over, player_on_strike):
    batting_team = match.batting_team
    bowler = match.bowling_team.current_bowler
    overs = match.overs
    venue = match.venue
    prob = venue.run_prob_t20

    # if ODI, override the prob
    if overs == 50:
        prob = venue.run_prob

    # run array
    run_array = [-1, 0, 1, 2, 3, 4, 5, 6]

    # in the death overs, increase prob of boundaries and wickets
    if batting_team.batting_second:
        if over == overs - 1:
            prob = [0.2, 0.2, 0, 0, 0, 0.2, 0.2, 0.2]

        # if need 1 to win, don't take 2 or if 2 to win, don't take 3
        if batting_team.target - batting_team.total_score == 1:
            prob = [1 / 7, 1 / 7, 1 / 7, 0, 1 / 7, 1 / 7, 1 / 7, 1 / 7, ]
        if batting_team.target - batting_team.total_score == 2:
            prob = [1 / 7, 1 / 7, 1 / 7, 1 / 7, 0, 1 / 7, 1 / 7, 1 / 7, ]

    # but, if batsman is poor and bowler is skilled, more chances of getting out
    # override all above probs
    if bowler.attr.bowling > 7 and player_on_strike.attr.batting < 6:
        #       -1     0     1      2   3   4   5    6
        prob = [0.25, 0.20, 0.20, 0.15, 0.05, 0.05, 0.05, 0.05]

    # select from final run_array with the given probability distribution
    run = choice(run_array, 1, p=prob, replace=False)[0]

    return run


# death over
def DetectDeathOvers(match, over):
    batting_team = match.batting_team
    overs = match.overs
    # towards the death overs, show a highlights
    towin = abs(batting_team.target - batting_team.total_score)
    # calculate if score is close
    if batting_team.batting_second:
        if towin <= 0:
            # show batting team highlights
            ShowHighlights(match)
            PrintInColor("Match won!!", Fore.LIGHTGREEN_EX)
            match.status = False
        elif towin <= 20 or over == overs - 1:
            ShowHighlights(match)
            if towin == 1:
                PrintInColor("Match tied!", Fore.LIGHTGREEN_EX)
            else:
                PrintInColor('To win: %s from %s' % (str(towin),
                                                     str(overs * 6 - batting_team.total_balls)),
                             Style.BRIGHT)
        # input('press enter to continue..')
    return


# play an over
def PlayOver(match, over):
    pair = match.batting_team.current_pair
    overs = match.overs
    batting_team, bowling_team = match.batting_team, match.bowling_team
    match_status = True
    logger = match.logger

    # get bowler
    bowler = AssignBowler(match)
    msg = "New bowler: %s %s/%s (%s)" % (bowler.name,
                                         str(bowler.runs_given),
                                         str(bowler.wkts),
                                         str(BallsToOvers(bowler.balls_bowled)))
    PrintInColor(msg, bowling_team.color)
    logger.info(msg)

    # assign current bowler
    match.bowling_team.current_bowler = bowler
    bowling_team.last_bowler = bowler

    # update bowler economy
    if bowler.balls_bowled > 0:
        eco = float(bowler.runs_given / BallsToOvers(bowler.balls_bowled))
        eco = round(eco, 2)
        bowler.eco = eco

    GetBowlerComments(match)

    ismaiden = True
    total_runs_in_over = 0
    ball = 1
    over_arr = []

    # loop for an over
    while ball <= 6:
        # check if dramatic over!
        if over_arr.count(6) > 2 or over_arr.count(4) > 2 \
                and -1 in over_arr:
            PrintInColor(Randomize(commentary.commentary_dramatic_over), Style.BRIGHT)

        if over == overs - 1 and ball == 6:
            if batting_team.batting_second:
                PrintInColor(Randomize(commentary.commentary_last_ball_match), Style.BRIGHT)
            else:
                PrintInColor(Randomize(commentary.commentary_last_ball_innings), Style.BRIGHT)

        DetectDeathOvers(match, over)

        # if match ended
        if not match.status:
            break

        print("Over: %s.%s" % (str(over), str(ball)))
        player_on_strike = next((x for x in pair if x.onstrike), None)
        print("%s to %s" % (GetShortName(bowler.name), GetShortName(player_on_strike.name)))
        if match.autoplay:
            time.sleep(1)
        else:
            input('press enter to continue..')

        # generate run, updates runs and maiden status
        run = GenerateRun(match, over, player_on_strike)
        over_arr.append(run)

        # detect too many wkts or boundaries
        if over_arr.count(-1) > 2:
            print("%s wickets already in this over!" % str(over_arr.count(-1)))
        if (over_arr.count(4) + over_arr.count(6)) > 2:
            print("%s boundaries already in this over!" % str(over_arr.count(4) + over_arr.count(6)))

        # check if maiden or not
        if run not in [-1, 0]:
            ismaiden = False

        # check if extra
        if run == 5:
            UpdateExtras(match)
            # comment on too many extras
            if over_arr.count(5) > 2:
                print("%s extras in this over!" % str(over_arr.count(5)))
            total_runs_in_over += 1

        # if not wide
        else:
            Ball(match, run)
            ball += 1
            if run != -1:
                total_runs_in_over += run
            if match.status is False:
                break
            # check if 1st innings over
            if batting_team.batting_second is False and batting_team.total_balls == (match.overs * 6):
                PrintInColor("End of innings", Fore.LIGHTCYAN_EX)
                # update last partnership
                if batting_team.wickets_fell > 0:
                    last_fow = batting_team.fow[-1].runs
                    last_partnership_runs = batting_team.total_score - last_fow
                    last_partnership = Partnership(batsman_dismissed=pair[0],
                                                   batsman_onstrike=pair[1],
                                                   runs=last_partnership_runs)
                    batting_team.partnerships.append(last_partnership)
                input('press enter to continue')
                break

            # batting second
            # if chasing and lost
            if batting_team.batting_second is True and batting_team.total_balls >= (match.overs * 6):
                # update last partnership
                UpdateLastPartnership(match)
                match.status = False
                PrintInColor(Randomize(commentary.commentary_lost_chasing) % (batting_team.name, bowling_team.name),
                             Style.BRIGHT)
                input('press enter to continue...')
                break
            # check if target achieved chasing
            if batting_team.batting_second is True and (batting_team.total_score >= batting_team.target):
                PrintInColor(Randomize(commentary.commentary_match_won), Fore.LIGHTGREEN_EX)
                match.status = False
                UpdateLastPartnership(match)
                input('press enter to continue...')
                break
            # if all out
            if batting_team.wickets_fell == 10:
                PrintInColor(Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX)
                match.status = False
                input('press enter to continue...')
                break

    # check if over is a maiden
    if ismaiden:
        bowler.maidens += 1
    # check total runs taken in over
    if total_runs_in_over > 14:
        PrintInColor(Randomize(commentary.commentary_expensive_over) % bowler.name + '\n' +
                     '%s runs in this over!' % (str(total_runs_in_over)),
                     Style.BRIGHT)
    elif total_runs_in_over == 0:
        PrintInColor(Randomize(commentary.commentary_maiden_over) % bowler.name,
                     Style.BRIGHT)
    elif total_runs_in_over < 6:
        PrintInColor(Randomize(commentary.commentary_economical_over) % bowler.name + '\n' +
                     'only %s run(s) off this over!' % (str(total_runs_in_over)),
                     Style.BRIGHT)
    return


# check for milestones
def CheckMilestone(match):
    logger = match.logger
    batting_team = match.batting_team
    pair = batting_team.current_pair

    for p in pair:
        # first fifty
        if p.runs >= 50 and p.fifty == 0:
            p.fifty += 1
            msg = "50 for %s!" % p.name
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            PrintInColor("%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT)
            # check if captain
            if p.attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
            PrintInColor(Randomize(commentary.commentary_milestone) % GetSurname(p.name), batting_team.color)

            #  check if he had a good day with the ball as well
            if p.wkts >= 2:
                PrintInColor(Randomize(commentary.commentary_all_round_batsman), batting_team.color)

        elif p.runs >= 100 and (p.fifty == 1 and p.hundred == 0):
            # after first fifty is done
            p.hundred += 1
            p.fifty += 1
            msg = "100 for %s!" % p.name
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            PrintInColor("%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT)
            # check if captain
            if p.attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
            PrintInColor(Randomize(commentary.commentary_milestone) % p.name, batting_team.color)

        elif p.runs >= 200 and (p.hundred == 1):
            # after first fifty is done
            p.hundred += 1
            msg = "200 for %s! What a superman!" % p.name
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            PrintInColor("%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT)
            # check if captain
            if p.attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
            PrintInColor(Randomize(commentary.commentary_milestone) % p.name, batting_team.color)

    input('press enter to continue..')
    return


# play!
def Play(match):
    batting_team = match.batting_team
    overs = match.overs
    logger = match.logger
    pair = batting_team.opening_pair

    comment = ''
    over_interrupt = 0
    if batting_team.batting_second is True:
        # in case of rainy, interrupt match intermittently
        if match.venue.weather == 'rainy':
            over_interrupt = random.choice(list(range(15, 50)))

        msg = 'Target for %s: %s from %s overs' % (batting_team.name,
                                                   str(batting_team.target),
                                                   str(overs))
        PrintInColor(msg, batting_team.color)
        logger.info(msg)
        # check if required rate
        reqd_rr = GetRequiredRate(batting_team)
        msg = "Reqd. run rate: %s" % (str(reqd_rr))
        print(msg)
        logger.info(msg)
        if reqd_rr > 8.0:
            comment = Randomize(commentary.commentary_high_req_rate) % batting_team.name
        elif reqd_rr < 5.0:
            comment = Randomize(commentary.commentary_less_req_rate) % batting_team.name
        PrintInColor(comment, Style.BRIGHT)

    # now run for each over
    for over in range(0, overs):
        # check if match interrupted
        if batting_team.batting_second and match.venue.weather == "rainy":
            if over == over_interrupt - 5:
                PrintInColor(Randomize(commentary.commentary_rain_cloudy), Style.BRIGHT)
            elif over == over_interrupt - 3:
                PrintInColor(Randomize(commentary.commentary_rain_drizzling), Style.BRIGHT)
            elif over == over_interrupt - 1:
                PrintInColor(Randomize(commentary.commentary_rain_heavy), Style.BRIGHT)
            elif over == over_interrupt:
                MatchAbandon(match)
                match.result.result_str = "No result"
                Error_Exit("Match abandoned due to rain!!")
            input("Press enter to continue")

        # check match stats and comment
        if match.status is False:
            break

        # check if last over
        if over == overs - 1:
            if batting_team.batting_second:
                PrintInColor(Randomize(commentary.commentary_last_over_match), Style.BRIGHT)
            else:
                PrintInColor(Randomize(commentary.commentary_last_over_innings), Style.BRIGHT)

        # play an over
        match.batting_team.current_pair = pair
        PlayOver(match, over)
        if match.status is False:
            break

        # show batting stats
        for p in pair:
            msg = '%s %s (%s)' % (GetShortName(p.name), str(p.runs), str(p.balls))
            PrintInColor(msg, Style.BRIGHT)
            logger.info(msg)
        ShowHighlights(match)
        DisplayBowlingStats(match)
        # rotate strike after an over
        RotateStrike(pair)
