# routines to display scores, etc
# display temporary stats
from data.commentary import *
from functions.utilities import PrintInColor, BallsToOvers, GetShortName, PrintListFormatted, Randomize, \
    ChooseFromOptions
from colorama import Style, Fore


# get current rate
def GetCurrentRate(team):
    crr = 0.0
    if team.total_balls > 0:
        crr = team.total_score / BallsToOvers(team.total_balls)
    crr = round(crr, 2)
    return crr


def GetRequiredRate(team):
    nrr = 0.0
    # if chasing, calc net nrr
    balls_remaining = team.total_overs * 6 - team.total_balls
    if balls_remaining > 0:
        overs_remaining = BallsToOvers(balls_remaining)
        towin = team.target - team.total_score
        nrr = float(towin / overs_remaining)
        nrr = round(nrr, 2)
    return nrr


# batting summary - scoreboard
def DisplayScore(match, team):
    logger = match.logger
    ch = '-'
    print(ch * 45)
    logger.info(ch * 45)

    msg = ch * 15 + 'Batting Summary' + ch * 15
    PrintInColor(msg, team.color)
    logger.info(msg)
    print(ch * 45)
    logger.info(ch * 45)

    # this should be a nested list of 3 elements
    data_to_print = []
    for p in team.team_array:
        name = p.name
        name = name.upper()
        if p.attr.iscaptain:
            name += '(c)'
        if p.attr.iskeeper:
            name += '(wk)'
        if p.status is True:  # * if not out
            if not p.onfield:
                data_to_print.append([name, 'DNB', ''])
            else:
                data_to_print.append([name, "not out", "%s* (%s)" % (str(p.runs), str(p.balls))])
        else:
            data_to_print.append([name, p.dismissal, "%s (%s)" % (str(p.runs), str(p.balls))])

    PrintListFormatted(data_to_print, 0.01, logger)

    msg = "Extras: %s" % str(team.extras)
    print(msg)
    logger.info(msg)
    print(' ')
    logger.info(' ')

    msg = '%s %s/%s from (%s overs)' % (team.name.upper(),
                                        str(team.total_score),
                                        str(team.wickets_fell),
                                        str(BallsToOvers(team.total_balls)))
    PrintInColor(msg, team.color)
    logger.info(msg)

    # show RR
    crr = GetCurrentRate(team)
    msg = "RunRate: %s" % (str(crr))
    print(msg)
    logger.info(msg)
    print(' ')
    logger.info(' ')

    # show FOW
    if team.wickets_fell != 0:
        PrintInColor('FOW:', Style.BRIGHT)
        logger.info('FOW:')
        # get fow_array
        fow_array = []
        for f in team.fow:
            fow_array.append('%s/%s %s(%s)' % (str(f.runs),
                                               str(f.wkt),
                                               GetShortName(f.player_dismissed.name),
                                               str(BallsToOvers(f.total_balls))))
        fow_str = ', '.join(fow_array)
        PrintInColor(fow_str, team.color)
        logger.info(fow_str)

    # partnerships
    msg = "Partnerships:"
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)
    for p in team.partnerships:
        msg = '%s - %s :\t%s' % (p.batsman_onstrike.name,
                                 p.batsman_dismissed.name,
                                 str(p.runs))
        if p.batsman_dismissed.status and p.batsman_onstrike.status:
            msg += '*'
        print(msg)
        logger.info(msg)

    print(ch * 45)
    logger.info(ch * 45)


# Showhighights
def ShowHighlights(match):
    logger = match.logger
    batting_team, bowling_team = match.batting_team, match.bowling_team
    crr = GetCurrentRate(batting_team)
    rr = GetRequiredRate(batting_team)

    # if match ended, do nothing, just return
    if not match.status:
        return

    # default msg
    msg = '\n%s %s / %s (%s Overs)' % (batting_team.name,
                                       str(batting_team.total_score),
                                       str(batting_team.wickets_fell),
                                       str(BallsToOvers(batting_team.total_balls)))
    msg += ' Current RR: %s' % str(crr)
    if batting_team.batting_second and match.status:
        msg += ' Required RR: %s\n' % str(rr)
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)
    return


# comment about the current match status
def CurrentMatchStatus(match):
    logger = match.logger
    batting_team, bowling_team = match.batting_team, match.bowling_team
    crr = GetCurrentRate(batting_team)
    rr = GetRequiredRate(batting_team)

    # if match ended, nothing, just return
    if not match.status:
        return

    # how much is the score
    if batting_team.total_score >= 50 and not batting_team.fifty_up:
        PrintInColor(Randomize(commentary.commentary_score_fifty) % batting_team.name, Style.BRIGHT)
        batting_team.fifty_up = True

    if batting_team.total_score >= 100 and not batting_team.hundred_up:
        PrintInColor(Randomize(commentary.commentary_score_hundred) % batting_team.name, Style.BRIGHT)
        batting_team.hundred_up = True

    if batting_team.total_score >= 200 and not batting_team.two_hundred_up:
        PrintInColor(Randomize(commentary.commentary_score_two_hundred) % batting_team.name, Style.BRIGHT)
        batting_team.two_hundred_up = True

    if batting_team.total_score >= 300 and not batting_team.three_hundred_up:
        PrintInColor(Randomize(commentary.commentary_score_three_hundred) % batting_team.name, Style.BRIGHT)
        batting_team.three_hundred_up = True

    # default msg
    msg = '\n%s %s / %s (%s Overs)' % (batting_team.name,
                                       str(batting_team.total_score),
                                       str(batting_team.wickets_fell),
                                       str(BallsToOvers(batting_team.total_balls)))
    msg += ' Current Rate: %s' % str(crr)
    if batting_team.batting_second:
        msg += ' Required Rate: %s\n' % str(rr)
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)

    # wickets fell
    wkts_fell = batting_team.wickets_fell

    # who are not out and going good
    top_batsmen = sorted([batsman for batsman in batting_team.team_array],
                         key=lambda t: t.runs, reverse=True)
    top_batsmen_notout = sorted([batsman for batsman in batting_team.team_array if batsman.status],
                                key=lambda t: t.runs, reverse=True)
    # who can win the match for them
    savior = top_batsmen_notout[0]

    # who all bowled so far
    bowlers = [bowler for bowler in bowling_team.bowlers if bowler.balls_bowled > 0]
    # top wkt takers
    bowlers_most_wkts = sorted(bowlers, key=lambda t: t.wkts, reverse=True)[0]

    # check if first batting
    if not batting_team.batting_second:
        if crr <= 4.0:
            PrintInColor(Randomize(commentary.commentary_situation_low_rr) % batting_team.name, Fore.GREEN)

        elif crr >= 8.0:
            PrintInColor(Randomize(commentary.commentary_situation_good_rr) % batting_team.name, Fore.GREEN)
            PrintInColor(Randomize(commentary.commentary_situation_major_contr_batting) % top_batsmen[0].name,
                         Style.BRIGHT)

        if wkts_fell == 0:
            PrintInColor(Randomize(commentary.commentary_situation_no_wkts_fell) % batting_team.name, Fore.GREEN)

        elif 1 < wkts_fell <= 6:
            PrintInColor(Randomize(commentary.commentary_situation_unstable) % batting_team.name, Style.BRIGHT)
            print("Lost %s wkts so far!" % wkts_fell)
            PrintInColor(Randomize(commentary.commentary_situation_major_contr_bowling) % bowlers_most_wkts.name,
                         Style.BRIGHT)

        elif 6 < wkts_fell < 10:
            PrintInColor(Randomize(commentary.commentary_situation_trouble) % batting_team.name, Style.BRIGHT)
            PrintInColor(Randomize(commentary.commentary_situation_major_contr_bowling) % bowlers_most_wkts.name,
                         Style.BRIGHT)

    # if chasing
    else:
        # gettable
        if crr >= rr:
            PrintInColor(Randomize(commentary.commentary_situation_reqd_rate_low) % batting_team.name, Fore.GREEN)
            if 0 <= batting_team.wickets_fell <= 2:
                PrintInColor(Randomize(commentary.commentary_situation_reqd_rate_low) % batting_team.name, Fore.GREEN)
            if batting_team.wickets_fell <= 5:
                PrintInColor(Randomize(commentary.commentary_situation_shouldnt_lose_wks) % batting_team.name,
                             Style.BRIGHT)
            elif 5 <= batting_team.wickets_fell < 7:
                PrintInColor(Randomize(commentary.commentary_situation_unstable) % batting_team.name, Style.BRIGHT)
            elif 7 < batting_team.wickets_fell < 10:
                # say who can save the match
                PrintInColor(Randomize(commentary.commentary_situation_savior) % savior.name, Fore.RED)

        # gone case!
        if rr - crr >= 1.0:
            PrintInColor(Randomize(commentary.commentary_situation_reqd_rate_high) % batting_team.name, Style.BRIGHT)
            if 0 <= batting_team.wickets_fell <= 2:
                PrintInColor(Randomize(commentary.commentary_situation_got_wkts_in_hand) % batting_team.name,
                             Style.BRIGHT)
            if 7 <= batting_team.wickets_fell < 10:
                PrintInColor(Randomize(commentary.commentary_situation_gone_case) % batting_team.name, Fore.RED)
                # say who can save the match
                PrintInColor(Randomize(commentary.commentary_situation_savior) % savior.name, Fore.RED)

    show_proj_score = ChooseFromOptions(['y', 'n'], "Do you need to view the projected score?", 500)
    if show_proj_score == 'y':
        DisplayProjectedScore(match)

    return


def DisplayProjectedScore(match):
    import numpy as np
    overs_left = BallsToOvers(match.overs * 6 - match.batting_team.total_balls)
    current_score = match.batting_team.total_score
    crr = GetCurrentRate(match.batting_team)
    proj_score = lambda x: np.ceil(current_score + (x * overs_left))
    print("Projected Score")
    print('Current Rate(%s): %s' % (str(crr), proj_score(crr)), end=' ')
    lim = crr + 3.0
    crr += 0.5
    while crr <= lim:
        print('%s: %s' % (str(crr), proj_score(crr)), end=' ')
        crr += 1.0
    print('\n')


# match summary
def MatchSummary(match):
    logger = match.logger
    ch = '-'
    result = match.result

    msg = '%s Match Summary %s' % (ch * 10, ch * 10)
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)

    msg = '%s vs %s, at %s' % (result.team1.name, result.team2.name, match.venue.name)
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)

    msg = ch * 45
    print(ch * 45)
    logger.info(msg)

    msg = result.result_str
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)

    print(ch * 45)
    logger.info(ch * 45)

    msg = '%s %s/%s (%s)' % (result.team1.key,
                             str(result.team1.total_score),
                             str(result.team1.wickets_fell),
                             str(BallsToOvers(result.team1.total_balls)))
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)

    # see who all bowled
    bowlers1 = [plr for plr in result.team1.team_array if plr.balls_bowled > 0]
    bowlers2 = [plr for plr in result.team2.team_array if plr.balls_bowled > 0]

    # print first N top scorers
    n = 3

    most_runs = sorted(result.team1.team_array, key=lambda t: t.runs, reverse=True)

    # there will be always two batsmen and two bowlers
    if len(most_runs) > 2:
        most_runs = most_runs[:n]

    best_bowlers = sorted(bowlers2, key=lambda b: b.wkts, reverse=True)

    if len(best_bowlers) > 2:
        best_bowlers = best_bowlers[:n]
    # must be a nested list of fixed size elements
    data_to_print = []
    for x in range(n):
        runs = str(most_runs[x].runs)
        # if not out, put a * in the end
        if most_runs[x].status:
            runs += '*'

        # print
        data_to_print.append([GetShortName(most_runs[x].name),
                              '%s(%s)' % (runs, most_runs[x].balls),
                              GetShortName(best_bowlers[x].name),
                              '%s/%s' % (best_bowlers[x].runs_given, best_bowlers[x].wkts)])

    # print
    PrintListFormatted(data_to_print, 0.01, logger)

    data_to_print = []
    print(ch * 45)
    logger.info(ch * 45)

    msg = '%s %s/%s (%s)' % (result.team2.key,
                             str(result.team2.total_score),
                             str(result.team2.wickets_fell),
                             str(BallsToOvers(result.team2.total_balls)))
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)

    most_runs = sorted(result.team2.team_array, key=lambda t: t.runs, reverse=True)
    most_runs = most_runs[:n]
    best_bowlers = sorted(bowlers1, key=lambda b: b.wkts, reverse=True)
    best_bowlers = best_bowlers[:n]
    for x in range(n):
        runs = str(most_runs[x].runs)
        # if not out, put a *
        if most_runs[x].status:
            runs += '*'

        # print
        data_to_print.append([GetShortName(most_runs[x].name),
                              '%s(%s)' % (runs, most_runs[x].balls),
                              GetShortName(best_bowlers[x].name),
                              '%s/%s' % (best_bowlers[x].runs_given, best_bowlers[x].wkts)])

    PrintListFormatted(data_to_print, 0.01, logger)
    print('-' * 43)
    logger.info('-' * 43)
    input('Press Enter to continue..')


# print bowlers stats
def DisplayBowlingStats(match):
    logger = match.logger
    team = match.bowling_team
    bowlers = team.bowlers
    # here, remove the bowlers who did not bowl
    bowlers_updated = []
    char = '-'
    print(char * 45)
    logger.info(char * 45)

    msg = '%s-Bowling Stats-%s' % (char * 15, char * 15)
    PrintInColor(msg, Style.BRIGHT)
    logger.info(msg)
    print(char * 45)
    logger.info(char * 45)
    # nested list of fixed size elements
    data_to_print = [['Bowler', 'Ovrs', 'Mdns', 'Runs', 'Wkts', 'Eco']]
    for bowler in bowlers:
        # do not print if he has not bowled
        if bowler.balls_bowled != 0:
            bowlers_updated.append(bowler)
            balls = bowler.balls_bowled
            overs = BallsToOvers(balls)
            eco = float(bowler.runs_given / overs)
            eco = round(eco, 2)
            bowler.eco = eco
            data_to_print.append([bowler.name.upper(),
                                  str(overs),
                                  str(bowler.maidens),
                                  str(bowler.runs_given),
                                  str(bowler.wkts),
                                  str(bowler.eco)])

    PrintListFormatted(data_to_print, 0.01, logger)
    print(char * 45)
    logger.info(char * 45)
    input('press enter to continue..')


# print playing XI
def DisplayPlayingXI(match):
    t1, t2 = match.team1, match.team2
    # print the playing XI
    print('Playing XI:')
    data_to_print = [[t1.name, t2.name], [' ', ' ']]
    for x in range(11):
        name1 = t1.team_array[x].name
        name2 = t2.team_array[x].name

        name1 = name1.upper()
        name2 = name2.upper()

        if t1.team_array[x] == t1.captain:
            name1 += '(c)'
        if t1.team_array[x] == t1.keeper:
            name1 += '(wk)'
        if t2.team_array[x] == t2.captain:
            name2 += '(c)'
        if t2.team_array[x] == t2.keeper:
            name2 += '(wk)'

        data_to_print.append([name1, name2])
    # now print it
    PrintListFormatted(data_to_print, 0.1, None)


def SummarizeBowling(match, team):
    # get best bowlers
    # FIXME say if good performance
    best_economical_bowlers = [x for x in team.team_array if x.eco < 6.0 and x.balls_bowled > 0]
    best_wickets_bowlers = [x for x in team.team_array if x.wkts >= 3 and x.balls_bowled > 0]
    if len(best_economical_bowlers) > 0:
        msg = ','.join(x.name for x in best_economical_bowlers)
        print("Very economical stuff from %s" % msg)
    if len(best_wickets_bowlers) > 0:
        msg = ','.join(x.name for x in best_wickets_bowlers)
        print("Most wickets taken by %s" % msg)
    input()
    return


def SummarizeBatting(match, team):
    # find what happened in the top order
    # check if it was a good score
    total_runs = team.total_score
    total_overs = team.total_overs
    wkts = team.wickets_fell
    # say if this was a good total
    msg = 'Thats the end of the innings, and %s has scored %s off %s overs..' % (
        team.name, str(total_runs), str(total_overs))
    nrr = GetCurrentRate(team)
    if nrr > 7.0 and wkts < 10:
        msg += 'They have scored at a terrific rate of %s ' % (str(nrr))
    if wkts == 10:
        msg += 'They have been bowled out!'

    print(msg)
    # now say about the top order
    top_order_collapse = middle_order_collapse = False
    tail_good_performance = False

    top_order = [x for x in team.team_array[:4] if x.balls > 0]
    top_order_good = [x for x in top_order if x.runs >= 30]
    top_order_great = [x for x in top_order if x.runs >= 50]
    top_order_poor = [x for x in top_order if x.runs <= 10]
    if len(top_order_poor) >= 3:
        top_order_collapse = True

    middle_order = [x for x in team.team_array[4:7] if x.balls > 0]
    middle_order_good = [x for x in middle_order if x.runs >= 30]
    middle_order_great = [x for x in middle_order if x.runs >= 50]
    middle_order_poor = [x for x in middle_order if x.runs <= 10]
    if len(middle_order_poor) >= 3:
        middle_order_collapse = True

    tail = team.team_array[8:10]
    tail_good = [x for x in tail if x.runs >= 30]
    tail_great = [x for x in tail if x.runs >= 50]
    if len(tail_great) > 1:
        tail_good_performance = True

    if len(top_order) != 0:
        if len(top_order_good) != 0:
            msg = ','.join(x.name for x in top_order_good)
            print("In the top order, there were some stable performers %s played really well" % msg)
        if len(top_order_great) != 0:
            msg = ','.join(x.name for x in top_order_great)
            print("terrific from %s high quality batting" % msg)
        if len(top_order_poor) != 0:
            msg = ','.join(x.name for x in top_order_poor)
            print("Disappointment for %s" % msg)

    # same for middle order and tail
    if len(middle_order) != 0:
        if len(middle_order_good) != 0:
            msg = ','.join(x.name for x in middle_order_good)
            print("some stable performance in the middle order %s" % msg)
        if len(middle_order_great) != 0:
            msg = ','.join(x.name for x in middle_order_great)
            print("terrific batting from %s" % msg)
        if len(middle_order_poor) != 0:
            msg = ','.join(x.name for x in middle_order_poor)
            print("Disappointment for %s" % msg)

    # see if tail did great
    if len(tail) != 0 and len(tail_good) != 0:
        msg = ','.join(x.name for x in tail_great)
        print("terrific effort from the lower order! %s" % msg)

    # randomize this commentary
    if top_order_collapse and not middle_order_collapse:
        print("We have seen some top order collapse!.. but good come back in the middle order")
    if not top_order_collapse and middle_order_collapse:
        print("The top order gave a good start.. but middle order collapsed!")
    if tail_good_performance:
        print("Some terrific fightback from the tail!")
    # FIXME say about chasing, facing bowlers, etc

    input()
    return
