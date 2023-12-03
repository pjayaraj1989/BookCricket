# main routines
import logging
from BookCricket import ScriptPath, venue_data, data_path
from data.resources import *
from functions.Initiate import GetVenue, ReadTeams
from functions.Pair import BatsmanOut, PairFaceBall, RotateStrike
from functions.SimulateDelivery import GenerateRunNew
from functions.helper import *
from functions.utilities import *
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
    match.ValidateMatchTeams()

    # toss, select who is batting first
    match.Toss()
    match.team1, match.team2 = match.batting_first, match.batting_second

    # match start
    match.status = True
    match.batting_team, match.bowling_team = match.team1, match.team2

    # play 1st innings
    Play(match)

    # display batting and bowling scorecard
    match.team1.DisplayScore(match)
    match.DisplayBowlingStats()

    # say something about the first innings
    match.batting_team.SummarizeBatting()
    # summarize about bowling performance
    match.bowling_team.SummarizeBowling()

    # play second inns with target
    match.team2.target = match.team1.total_score + 1

    # swap teams now
    match.batting_team, match.bowling_team = match.team2, match.team1

    # play second innings
    Play(match)

    # show batting and bowling scores
    match.team2.DisplayScore(match)
    match.DisplayBowlingStats()

    # match ended
    match.status = False

    # show results
    match.CalculateResult()

    # say something about the first innings
    match.batting_team.SummarizeBatting()
    # summarize about bowling performance
    match.bowling_team.SummarizeBowling()

    match.MatchSummary()
    match.FindPlayerOfTheMatch()

    # close log handler
    handler.close()

    return

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

    # add player dismissed to the list of wickets for the bowler
    bowler.wickets_taken.append(player_dismissed)

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
    # isOnAHattrick = CheckForConsecutiveElements(arr, 'Wkt', 2)
    isHattrick = CheckForConsecutiveElements(arr, 'Wkt', 3)

    # if isOnAHattrick:
    #    PrintInColor(Randomize(commentary.commentary_on_a_hattrick), bowling_team.color)

    if isHattrick:
        bowler.hattricks += 1
        PrintInColor(Randomize(commentary.commentary_hattrick), bowling_team.color)
        input('press enter to continue..')
    if bowler.wkts == 3:
        PrintInColor('Third wkt for %s !' % bowler.name, bowling_team.color)
        input('press enter to continue..')
    # check if bowler got 5 wkts
    if bowler.wkts == 5:
        PrintInColor('That\'s 5 Wickets for %s !' % bowler.name, bowling_team.color)
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

    match.PrintCommentaryDismissal(dismissal)
    # show score
    match.CurrentMatchStatus()
    # get next batsman
    match.GetNextBatsman()
    input('press enter to continue')
    match.batting_team.DisplayScore(match)
    match.DisplayProjectedScore()
    return

# play a ball
def Ball(match, run):
    batting_team, bowling_team = match.batting_team, match.bowling_team
    bowler = bowling_team.current_bowler
    logger = match.logger
    pair = batting_team.current_pair

    # get who is on strike
    on_strike = next((x for x in pair if x.onstrike), None)

    # first runs
    if batting_team.total_score == 0 and (run not in [-1, 0]) and not batting_team.off_the_mark:
        PrintInColor(Randomize(commentary.commentary_first_runs) % (batting_team.name, on_strike.name),
                     batting_team.color)
        batting_team.off_the_mark = True

    # if out
    used_drs = False
    while run == -1:
        dismissal = match.GenerateDismissal()
        if 'lbw' in dismissal:
            PrintInColor(Randomize(commentary.commentary_lbw_umpire) % match.umpire, Fore.LIGHTRED_EX)

            # if match has no DRS, do not go into this
            if match.drs is False:
                UpdateDismissal(match, dismissal)
                return

            # if DRS opted, check
            result = match.CheckDRS()

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

    # appropriate commentary for 4s and 6s
    if run == 4:
        # check if this is after a wicket?
        if batting_team.ball_history != []:
            if 'Wkt' in str(batting_team.ball_history[-1]) or 'RO' in str(batting_team.ball_history[-1]):
                PrintInColor(Randomize(commentary.commentary_boundary_after_wkt), Fore.LIGHTGREEN_EX)
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

    # six
    elif run == 6:
        # check if this is after a wicket?
        if batting_team.ball_history != []:
            if 'Wkt' in str(batting_team.ball_history[-1]) or 'RO' in str(batting_team.ball_history[-1]):
                PrintInColor(Randomize(commentary.commentary_boundary_after_wkt), Fore.LIGHTGREEN_EX)
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
        on_strike.dots += 1
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

    # ones and twos and threes
    else:
        bowler.ball_history.append(run)
        batting_team.ball_history.append(run)
        field = Randomize(resources.fields["ground_shot"])
        comment = Randomize(commentary.commentary_ground_shot)
        if run == 1:
            on_strike.singles += 1
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
            if run == 2:
                on_strike.doubles += 1
            elif run == 3:
                on_strike.threes += 1
            print('%s,%s %s runs' % (comment, field, str(run)))

    # update balls runs
    bowler.balls_bowled += 1
    bowler.runs_given += run
    # update bowler economy
    if bowler.balls_bowled > 0:
        eco = float(bowler.runs_given / BallsToOvers(bowler.balls_bowled))
        eco = round(eco, 2)
        bowler.eco = eco
    PairFaceBall(pair, run)
    batting_team.total_balls += 1
    batting_team.total_score += run

    # check for milestones
    match.CheckMilestone()
    return



# play an over
def PlayOver(match, over):
    pair = match.batting_team.current_pair
    overs = match.overs
    batting_team, bowling_team = match.batting_team, match.bowling_team
    logger = match.logger

    # get bowler
    bowler = match.AssignBowler()
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

    match.GetBowlerComments()

    ismaiden = True
    total_runs_in_over = 0
    ball = 1
    over_arr = []

    # loop for an over
    while ball <= 6:
        # if match ended
        if not match.status:
            break

        # check if dramatic over!
        if over_arr.count(6) > 2 or over_arr.count(4) > 2 \
                and -1 in over_arr:
            PrintInColor(Randomize(commentary.commentary_dramatic_over), Style.BRIGHT)

        if over == overs - 1 and ball == 6:
            if batting_team.batting_second:
                PrintInColor(Randomize(commentary.commentary_last_ball_match), Style.BRIGHT)
            else:
                PrintInColor(Randomize(commentary.commentary_last_ball_innings), Style.BRIGHT)

        match.DetectDeathOvers(over)

        print("Over: %s.%s" % (str(over), str(ball)))
        player_on_strike = next((x for x in pair if x.onstrike), None)
        print("%s to %s" % (GetShortName(bowler.name), GetShortName(player_on_strike.name)))
        if match.autoplay:
            time.sleep(1)
        else:
            input('press enter to continue..')

        # generate run, updates runs and maiden status
        # FIXME dont pass over and player on strike, instead detect it!
        run = match.GenerateRun(over, player_on_strike)
        # run = GenerateRunNew(match, over, player_on_strike)

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
            match.UpdateExtras()
            # comment on too many extras
            if over_arr.count(5) > 2:
                print("%s extras in this over!" % str(over_arr.count(5)))
            total_runs_in_over += 1
            if match.status is False:
                break

        # if not wide
        else:
            Ball(match, run)
            ball += 1
            if run != -1:
                total_runs_in_over += run
            if match.status is False:
                break

        if batting_team.total_balls == (match.overs * 6):
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

        # check if 1st innings over
        # if all out first innings
        if not batting_team.batting_second:
            if batting_team.wickets_fell == 10:
                PrintInColor(Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX)
                if (match.overs * 6) / batting_team.total_score <= 1.2:
                    PrintInColor(Randomize(commentary.commentary_all_out_good_score), Fore.GREEN)
                elif 0.0 <= batting_team.GetCurrentRate() >= 1.42:
                    PrintInColor(Randomize(commentary.commentary_all_out_bad_score), Fore.GREEN)
                input('press enter to continue...')
                break

        # batting second
        elif batting_team.batting_second:
            if batting_team.total_balls >= (match.overs * 6):
                # update last partnership
                match.UpdateLastPartnership()
                match.status = False
                # if won in the last ball
                if batting_team.total_score >= batting_team.target:
                    PrintInColor(
                        Randomize(commentary.commentary_won_last_ball) % (batting_team.name, bowling_team.name),
                        Style.BRIGHT)
                else:
                    PrintInColor(Randomize(commentary.commentary_lost_chasing) % (batting_team.name, bowling_team.name),
                                 Style.BRIGHT)
                input('press enter to continue...')
                break
            # check if target achieved chasing
            if batting_team.total_score >= batting_team.target:
                PrintInColor(Randomize(commentary.commentary_match_won), Fore.LIGHTGREEN_EX)
                PrintInColor(Randomize(commentary.commentary_match_won_chasing), Fore.LIGHTGREEN_EX)
                match.status = False
                match.UpdateLastPartnership()
                input('press enter to continue...')
                break
            # if all out first innings
            if batting_team.wickets_fell == 10:
                PrintInColor(Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX)
                input('press enter to continue...')
                break

    # check total runs taken in over
    # if expensive over
    if total_runs_in_over > 14:
        PrintInColor(Randomize(commentary.commentary_expensive_over) % bowler.name + '\n' +
                     '%s runs in this over!' % (str(total_runs_in_over)),
                     Style.BRIGHT)
    # check if maiden over
    elif total_runs_in_over == 0:
        PrintInColor(Randomize(commentary.commentary_maiden_over) % bowler.name,
                     Style.BRIGHT)
        bowler.maidens += 1
    # check for an economical over
    elif total_runs_in_over < 6:
        PrintInColor(Randomize(commentary.commentary_economical_over) % bowler.name + '\n' +
                     'only %s run(s) off this over!' % (str(total_runs_in_over)),
                     Style.BRIGHT)

    # if bowler finished his spell, update it
    if BallsToOvers(bowler.balls_bowled) == bowler.max_overs:
        bowler.spell_over = True
        PrintInColor(Randomize(commentary.commentary_bowler_finished_spell) % bowler.name, Style.BRIGHT)
        # now say about his performance
        bowler.SummarizeBowlerSpell()
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
        reqd_rr = batting_team.GetRequiredRate()
        msg = "Reqd. run rate: %s" % (str(reqd_rr))
        print(msg)
        logger.info(msg)

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
                match.MatchAbandon()
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

        # check hows it going in regular intervals
        if over > 1 and over % 5 == 0:
            match.CurrentMatchStatus()

        # play an over
        match.batting_team.current_pair = pair

        # if all out
        if match.batting_team.wickets_fell == 10:
            break
        PlayOver(match, over)
        if match.status is False:
            break

        # show batting stats
        for p in pair:
            msg = '%s %s (%s)' % (GetShortName(p.name), str(p.runs), str(p.balls))
            PrintInColor(msg, Style.BRIGHT)
            logger.info(msg)

        match.ShowHighlights()
        match.DisplayBowlingStats()
        match.batting_team.DisplayScore(match)
        match.DisplayProjectedScore()
        # rotate strike after an over
        RotateStrike(pair)

    return
