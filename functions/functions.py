# main routines

from data.resources import *
from data.commentary import *
from functions.DisplayScores import ShowHighlights, DisplayScore, DisplayBowlingStats, MatchSummary, GetCurrentRate, \
    GetRequiredRate
from functions.helper import *
from functions.utilities import *
from numpy.random import choice
import random
import time


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
    result_str = ''
    remaining_overs = match.overs - BallsToOvers(batting_team.total_balls)
    simulated_score = int(round(remaining_overs * crr)) + batting_team.total_score
    if crr >= nrr:
        # calculate win margin
        result_str = "{0} wins by {1} run(s) using D/L method!".format(batting_team.name,
                                                                       str(abs(simulated_score - batting_team.target)))
    else:
        result_str = "{0} wins by {1} run(s) D/L method!".format(bowling_team.name,
                                                                 str(abs(batting_team.target - simulated_score)))
    input("Press any key to continue")
    match.status = False
    result.result_str = result_str
    DisplayScore(match, batting_team)
    DisplayBowlingStats(match)
    # change result string
    match.result = result
    MatchSummary(match)


def CheckDRS(match, pair):
    result = False
    team = match.batting_team

    impact_outside_bat_involved = False
    if team.drs_chances <= 0:
        PrintInColor(Randomize(commentary.commentary_lbw_nomore_drs), Fore.LIGHTRED_EX)
        return result
    # check if all 4 decisions are taken
    elif team.drs_chances > 0:
        opt = ChooseFromOptions(['y', 'n'],
                                "DRS? {0} chance(s) left".format(str(team.drs_chances)),
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
    elif ind == 1:
        alt_ind = 0
    pair[ind].runs += run
    pair[ind].balls += 1
    # now if runs is 1 / 3
    if run % 2 != 0:
        pair[ind].onstrike = False
        pair[alt_ind].onstrike = True
    return pair


# rotate strike
def RotateStrike(pair):
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)
    alt_ind = 0
    if ind == 0:
        alt_ind = 1
    elif ind == 1:
        alt_ind = 0
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
def GenerateDismissal(bowler, bowling_team):
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
        dismissal_str = '{0} {1}'.format(dismissal, GetShortName(bowler.name))
    elif dismissal == 'st':
        # stumped
        dismissal_str = 'st {0} b {1}'.format(GetShortName(keeper.name), GetShortName(bowler.name))
    elif dismissal == 'c':
        # check if catcher is the bowler
        if fielder == bowler:
            dismissal_str = 'c&b {0}'.format(GetShortName(bowler.name))
        else:
            dismissal_str = '{0} {1} b {2}'.format(dismissal, GetShortName(fielder.name), GetShortName(bowler.name))
    elif dismissal == 'runout':
        dismissal_str = 'runout {0}'.format(GetShortName(fielder.name))

    return dismissal_str


# update dismissal
def UpdateDismissal(match, bowler, pair, dismissal):
    logger = match.logger
    batting_team, bowling_team = match.batting_team, match.bowling_team

    keeper = next((x for x in bowling_team.team_array if x.attr.iskeeper), None)
    if 'runout' in dismissal:
        bowler.ball_history.append('RO')
    else:
        # add this to bowlers history
        bowler.ball_history.append('Wkt')
        bowler.wkts += 1

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

    msg = "OUT ! {0} {1} {2} ({3}) SR: {4}".format(GetShortName(player_dismissed.name),
                                                   player_dismissed.dismissal,
                                                   str(player_dismissed.runs),
                                                   str(player_dismissed.balls),
                                                   str(player_dismissed.strikerate))
    PrintInColor(msg, Fore.LIGHTRED_EX)
    logger.info(msg)
    # show 4s, 6s
    PrintInColor("4s:{0}, 6s:{1}, 1s:{2}, 2s:{3} 3s:{4}".format(str(player_dismissed.fours),
                                                                str(player_dismissed.sixes),
                                                                str(player_dismissed.singles),
                                                                str(player_dismissed.doubles),
                                                                str(player_dismissed.threes)),
                 Style.BRIGHT)

    # detect a hat-trick!
    arr = [x for x in bowler.ball_history if x != 'WD' or x != 'NB']
    isHattrick = CheckForConsecutiveElements(arr, 'Wkt', 3)
    if isHattrick:
        bowler.hattricks += 1
        PrintInColor(Randomize(commentary.commentary_hattrick), bowling_team.color)
        input('press enter to continue..')
    if bowler.wkts == 3:
        PrintInColor('Third wkt for {0} !'.format(bowler.name), bowling_team.color)
        input('press enter to continue..')
    # check if bowler got 5 wkts
    if bowler.wkts == 5:
        PrintInColor('Thats 5 Wickets for {0} !'.format(bowler.name), bowling_team.color)
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
    # commentary
    comment = ' '

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
    # if its a great knock, say this
    if player_dismissed.runs > 50:
        PrintInColor(Randomize(commentary.commentary_out_fifty) % GetSurname(player_dismissed.name), Style.BRIGHT)
    # if duck
    if player_dismissed.runs == 0:
        PrintInColor(Randomize(commentary.commentary_out_duck), Style.BRIGHT)
    # out first ball
    if player_dismissed.balls == 1:
        PrintInColor(Randomize(commentary.commentary_out_first_ball) % GetSurname(player_dismissed.name), Style.BRIGHT)
    # if partnership is great
    if partnership.runs > 50:
        PrintInColor(Randomize(commentary.commentary_partnership_milestone) % (GetSurname(pair[0].name),
                                                                               GetSurname(pair[1].name)),
                     Style.BRIGHT)

    # calculate the situation
    if batting_team.batting_second and (7 <= batting_team.wickets_fell < 10):
        PrintInColor(Randomize(commentary.commentary_goingtolose) % batting_team.name, Style.BRIGHT)

    # last man
    if batting_team.wickets_fell == 9:
        PrintInColor(Randomize(commentary.commentary_lastman), batting_team.color)

    # show score
    ShowHighlights(match)

    if batting_team.wickets_fell < 10:
        ind = pair.index(player_dismissed)
        pair[ind] = batting_team.team_array[batting_team.wickets_fell + 1]
        pair[ind].onstrike = True
        PrintInColor("New Batsman: " + pair[ind].name, batting_team.color)
        # check if he is captain
        if pair[ind].attr.iscaptain:
            PrintInColor(Randomize(commentary.commentary_captain_to_bat_next), batting_team.color)
        # now new batter on field
        pair[ind].onfield = True
    input('press enter to continue..')
    return


# play a ball
def Ball(match, run, pair, bowler):
    batting_team, bowling_team = match.batting_team, match.bowling_team
    logger = match.logger
    # get who is on strike
    on_strike = next((x for x in pair if x.onstrike), None)
    off_strike = next((x for x in pair if not x.onstrike), None)

    # if out
    used_drs = False
    while run == -1:
        dismissal = GenerateDismissal(bowler, bowling_team)
        if 'lbw' in dismissal:
            PrintInColor(Randomize(commentary.commentary_lbw_umpire) % match.umpire, Fore.LIGHTRED_EX)
            result = CheckDRS(match, [on_strike, off_strike])
            # overturn
            if result:
                run = 0
                used_drs = True
                break
            # decision stays
            else:
                run = -1
                UpdateDismissal(match, bowler, pair, dismissal)
                return
        else:
            UpdateDismissal(match, bowler, pair, dismissal)
            return

    # other than dismissal
    if run != -1:
        # appropriate commentary for 4s and 6s
        if run == 4:
            bowler.ball_history.append(4)
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
            # check uf furst ball is hit
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
            # inc nuber of 6s
            on_strike.sixes += 1
        # dot ball
        elif run == 0:
            bowler.ball_history.append(0)
            if not used_drs:
                if bowler.attr.ispacer:
                    comment = Randomize(commentary.commentary_dot_ball_pacer) + '\n' + \
                              Randomize(commentary.commentary_dot_ball) % (GetSurname(bowler.name),
                                                                           on_strike.name)
                else:
                    comment = Randomize(commentary.commentary_dot_ball) % (GetSurname(bowler.name),
                                                                           GetSurname(on_strike.name))
            else:
                comment = "Decision overturned!"
            print('{0}, No Run'.format(comment))
            logger.info("DOT BALL")
        # ones and twos and threes
        else:
            logger.info(str(run))
            bowler.ball_history.append(run)
            field = Randomize(resources.fields["ground_shot"])
            comment = Randomize(commentary.commentary_ground_shot)
            if run == 1:
                print('{0},{1} {2} run'.format(comment, field, str(run)))
            else:
                print('{0},{1} {2} runs'.format(comment, field, str(run)))
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
        CheckMilestone(match, pair)


# update last partnership
def UpdateLastPartnership(match, pair):
    batting_team = match.batting_team
    # update last partnership
    if batting_team.wickets_fell > 0:
        last_fow = batting_team.fow[-1].runs
        last_partnership_runs = batting_team.total_score - last_fow
        last_partnership = Partnership(batsman_dismissed=pair[0],
                                       batsman_onstrike=pair[1],
                                       runs=last_partnership_runs)
        batting_team.partnerships.append(last_partnership)
    # if no wkt fell
    elif batting_team.wickets_fell == 0:
        last_partnership_runs = batting_team.total_score
        last_partnership = Partnership(batsman_dismissed=pair[0],
                                       batsman_onstrike=pair[1],
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
            # esle pick bowler
            else:
                choice = input('Pick next bowler: {0} [Press Enter to auto-select]'.format(
                    ' / '.join([str(x.no) + '.' + GetShortName(x.name) for x in temp])))
                bowler = next((x for x in temp if (str(choice) == str(x.no)
                                                   or choice.lower() in GetShortName(x.name).lower())),
                              None)
                if bowler is None:
                    bowler = Randomize(temp)

    if bowler is None:  Error_Exit("No bowler assigned!")

    return bowler


# play an over
def PlayOver(match, over, pair):
    overs = match.overs
    batting_team, bowling_team = match.batting_team, match.bowling_team
    match_status = True
    logger = match.logger
    # get bowler
    bowler = AssignBowler(match)
    msg = "New bowler: {0} {1}/{2} ({3})".format(bowler.name,
                                                 str(bowler.runs_given),
                                                 str(bowler.wkts),
                                                 str(BallsToOvers(bowler.balls_bowled)))
    PrintInColor(msg, bowling_team.color)
    logger.info(msg)
    # update bowler economy
    if bowler.balls_bowled > 0:
        eco = float(bowler.runs_given / BallsToOvers(bowler.balls_bowled))
        eco = round(eco, 2)
        bowler.eco = eco

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

    ball = 1
    bowling_team.last_bowler = bowler
    ismaiden = True
    total_runs_in_over = 0
    while ball <= 6:
        if over == overs - 1 and ball == 6:
            if batting_team.batting_second:
                PrintInColor(Randomize(commentary.commentary_last_ball_match), Style.BRIGHT)
            else:
                PrintInColor(Randomize(commentary.commentary_last_ball_innings), Style.BRIGHT)
        # towards the death overs, show a highlights
        towin = abs(batting_team.target - batting_team.total_score)
        # calculate if score is close
        if batting_team.batting_second:
            if towin <= 0:
                # show batting team highlights
                ShowHighlights(match)
                PrintInColor("Match won!!", Fore.LIGHTGREEN_EX)
                input('press enter to continue...')
                break
            elif towin <= 20 or over == overs - 1:
                ShowHighlights(match)
                if towin == 1:
                    PrintInColor("Match tied!", Fore.LIGHTGREEN_EX)
                else:
                    PrintInColor('To win: {0} from {1}'.format(str(towin),
                                                               str(overs * 6 - batting_team.total_balls)),
                                 Style.BRIGHT)
                input('press enter to continue...')

        msg = "Over: {0}.{1}".format(str(over), str(ball))
        print(msg)
        player_on_strike = next((x for x in pair if x.onstrike), None)
        msg = '{0} to {1}'.format(GetShortName(bowler.name), GetShortName(player_on_strike.name))
        print(msg)
        if match.autoplay:
            time.sleep(1)
        else:
            input('press enter to continue..')

        # generate run
        prob = []
        if match.overs == 50:
            prob = match.venue.run_prob
        else:
            prob = match.venue.run_prob_t20

        #in the death, increase prob of boundaries and wickets
        if batting_team.batting_second:
            #if towin <=20 or (over == overs-1):
            if (over == overs-1):
                prob = [0.2, 0.2, 0, 0, 0, 0.2, 0.2, 0.2]

        run = choice([-1, 0, 1, 2, 3, 4, 5, 6], 1, p=prob, replace=False)[0]

        # check if maiden or not
        # if run > 0, change this flag
        if run not in [-1, 0]:
            ismaiden = False
            if run == 5:
                total_runs_in_over += 1
            else:
                total_runs_in_over += run

        # check if extra
        if run == 5:
            # generate wide or no ball
            extra = random.choice(['wd', 'nb'])
            if extra == 'wd':
                # add this to bowlers history
                bowler.ball_history.append('WD')
                PrintInColor("WIDE...!", Fore.LIGHTCYAN_EX)
                PrintInColor(Randomize(commentary.commentary_wide) % match.umpire, Style.BRIGHT)
                logger.info("WIDE")
                bowler.runs_given += 1
                batting_team.extras += 1
                batting_team.total_score += 1
            elif extra == 'nb':
                # no balls
                bowler.ball_history.append('NB')
                PrintInColor("NO BALL...!", Fore.LIGHTCYAN_EX)
                PrintInColor(Randomize(commentary.commentary_no_ball), Style.BRIGHT)
                logger.info("NO BALL")
                bowler.runs_given += 1
                batting_team.extras += 1
                batting_team.total_score += 1
        # if not wide
        else:
            Ball(match, run, pair, bowler)
            ball += 1
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
                UpdateLastPartnership(match, pair)
                match_status = False
                PrintInColor(Randomize(commentary.commentary_lost_chasing) % (batting_team.name, bowling_team.name),
                             Style.BRIGHT)
                input('press enter to continue...')
                break
            # check if target achieved chasing
            if batting_team.batting_second is True and (batting_team.total_score >= batting_team.target):
                PrintInColor(Randomize(commentary.commentary_match_won), Fore.LIGHTGREEN_EX)
                match_status = False
                UpdateLastPartnership(match, pair)
                input('press enter to continue...')
                break
            # if all out
            if batting_team.wickets_fell == 10:
                PrintInColor(Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX)
                match_status = False
                input('press enter to continue...')
                break
    # check if over is a maiden
    if ismaiden:
        bowler.maidens += 1
    # check total runs taken in over
    if total_runs_in_over > 14:
        PrintInColor(Randomize(commentary.commentary_expensive_over) % bowler.name + '\n' +
                     '{0} runs in this over!'.format(str(total_runs_in_over)),
                     Style.BRIGHT)
    elif total_runs_in_over == 0:
        PrintInColor(Randomize(commentary.commentary_maiden_over) % bowler.name,
                     Style.BRIGHT)
    elif total_runs_in_over < 6:
        PrintInColor(Randomize(commentary.commentary_economical_over) % bowler.name + '\n' +
                     'only {0} run(s) off this over!'.format(str(total_runs_in_over)),
                     Style.BRIGHT)
    return match_status


# check for milestones
def CheckMilestone(match, pair):
    logger = match.logger
    batting_team = match.batting_team
    for p in pair:
        # first fifty
        if p.runs >= 50 and p.fifty == 0:
            p.fifty += 1
            msg = "50 for {0}!".format(p.name)
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            PrintInColor("{0} fours and {1} sixes".format(str(p.fours), str(p.sixes)), Style.BRIGHT)
            # check if captain
            if p.attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
            PrintInColor(Randomize(commentary.commentary_milestone) % GetSurname(p.name), batting_team.color)
            input('press enter to continue..')
        elif p.runs >= 100 and (p.fifty == 1 and p.hundred == 0):
            # after first fifty is done
            p.hundred += 1
            p.fifty += 1
            msg = "100 for {0}!".format(p.name)
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            PrintInColor("{0} fours and {1} sixes".format(str(p.fours), str(p.sixes)), Style.BRIGHT)
            # check if captain
            if p.attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
            PrintInColor(Randomize(commentary.commentary_milestone) % p.name, batting_team.color)
            input('press enter to continue..')
        elif p.runs >= 200 and (p.hundred == 1):
            # after first fifty is done
            p.hundred += 1
            msg = "200 for {0}! What a superman!".format(p.name)
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            PrintInColor("{0} fours and {1} sixes".format(str(p.fours), str(p.sixes)), Style.BRIGHT)
            # check if captain
            if p.attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
            PrintInColor(Randomize(commentary.commentary_milestone) % p.name, batting_team.color)
            input('press enter to continue..')


# play!
def Play(match):
    batting_team = match.batting_team
    overs = match.overs
    logger = match.logger
    pair = batting_team.opening_pair

    comment = ''
    if batting_team.batting_second is True:
        msg = 'Target for {0}: {1} from {2} overs'.format(batting_team.name,
                                                          str(batting_team.target),
                                                          str(overs))
        PrintInColor(msg, batting_team.color)
        logger.info(msg)
        # check if required rate
        nrr = GetRequiredRate(batting_team)
        msg = "Reqd. run rate: {0}".format(str(nrr))
        print(msg)
        logger.info(msg)
        if nrr > 8.0:
            comment = Randomize(commentary.commentary_high_req_rate) % batting_team.name
        elif nrr < 5.0:
            comment = Randomize(commentary.commentary_less_req_rate) % batting_team.name
        PrintInColor(comment, Style.BRIGHT)

    # depending on weather, if rainy, decide after which over
    over_interrupt = 0
    if batting_team.batting_second is True:
        if match.venue.weather == 'rainy':
            over_interrupt = random.choice(list(range(10, 50)))

    # now run for each over
    for over in range(0, overs):
        # check if match interrupted
        if batting_team.batting_second and match.venue.weather == "rainy":
            if over == over_interrupt - 5:
                PrintInColor(Randomize(commentary.commentary_rain_cloudy), Style.BRIGHT)
                input("Press enter to continue")
            elif over == over_interrupt - 3:
                PrintInColor(Randomize(commentary.commentary_rain_drizzling), Style.BRIGHT)
                input("Press enter to continue")
            elif over == over_interrupt - 1:
                PrintInColor(Randomize(commentary.commentary_rain_heavy), Style.BRIGHT)
                input("Press enter to continue")
            elif over == over_interrupt:
                MatchAbandon(match)
                Error_Exit("Match abandoned due to rain!!")

        # check if last over
        if over == overs - 1:
            if batting_team.batting_second:
                PrintInColor(Randomize(commentary.commentary_last_over_match), Style.BRIGHT)
            else:
                PrintInColor(Randomize(commentary.commentary_last_over_innings), Style.BRIGHT)

        # play an over
        status = PlayOver(match, over, pair)
        if status is False:
            break

        # show batting stats
        for p in pair:
            msg = '{0} {1} ({2})'.format(GetShortName(p.name), str(p.runs), str(p.balls))
            PrintInColor(msg, Style.BRIGHT)
            logger.info(msg)
        ShowHighlights(match)
        DisplayBowlingStats(match)
        # rotate strike after an over
        RotateStrike(pair)
