# routines to display scores, etc
# display temporary stats
from functions.utilities import PrintInColor, BallsToOvers, GetShortName, PrintListFormatted, Randomize
from colorama import Style


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
    crr = team.GetCurrentRate()
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


def SummarizeBowlerSpell(match, bowler):
    # FIXME randomize these commentary
    # FIXME also based on match (in T20, this might be good
    if bowler.eco <= 5.0:   print("Very economical spell from %s" % bowler.name)
    if bowler.eco < 6.0 and bowler.wkts >= 3:   print("A terrific spell from him!")
    if bowler.eco > 6.0 and bowler.wkts >= 3:   print("Got %s wkts but slightly expensive today" % str(bowler.wkts))
    if bowler.eco > 7.0 and bowler.wkts == 0:   print("Very disappointing performance from him!")

    # check if he has got any key wickets!
    key_wkts = []
    msg = ''
    if bowler.wkts > 0:
        for wicket in bowler.wickets_taken:
            if wicket.runs > 50:    key_wkts.append(wicket)
        if len(key_wkts) == 1:
            msg = "he has got the key wicket of %s" % (key_wkts[0].name)
        elif len(key_wkts) > 1:
            msg = "he has got the key wicket of %s" % (','.join([x.name for x in key_wkts]))
        print(msg)
    return


def SummarizeBowling(match, team):
    # get best bowlers
    # FIXME say if good performance
    best_economical_bowlers = [x for x in team.team_array if x.eco < 6.0 and x.balls_bowled > 0]
    best_wickets_bowlers = [x for x in team.team_array if x.wkts >= 3 and x.balls_bowled > 0]
    if len(best_economical_bowlers) > 0:
        msg = ','.join(x.name for x in best_economical_bowlers)
        # FIXME randomize this commentary
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
    nrr = team.GetCurrentRate()
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
