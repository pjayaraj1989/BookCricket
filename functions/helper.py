from functions.Pair import BatsmanOut
from functions.utilities import FillAttributes, BallsToOvers, PrintInColor, GetShortName, PrintListFormatted, Randomize, \
    Error_Exit, ChooseFromOptions, GetFirstName, GetSurname, CheckForConsecutiveElements
from colorama import Style, Fore
from data.commentary import *
from numpy.random import choice
import random
from operator import attrgetter
import time


# mainly used classes
# add the default attributes and values here
# the FillAttributes function will populate it accordingly

class Tournament:
    def __init__(self, **kwargs):
        attrs = {'name': ' ',
                 'teams': []}
        self = FillAttributes(self, attrs, kwargs)


class Venue:
    def __init__(self, **kwargs):
        attrs = {'name': ' ',
                 'run_prob': [],
                 'run_prob_t20': [],
                 'weather': None}
        self = FillAttributes(self, attrs, kwargs)


class PlayerAttr:
    def __init__(self, **kwargs):
        attrs = {'batting': 0,
                 'bowling': 0,
                 'iskeeper': False, 'iscaptain': False, 'isopeningbowler': False, 'isspinner': False, 'ispacer': False}
        self = FillAttributes(self, attrs, kwargs)


class Player:
    def __init__(self, **kwargs):
        attrs = {'attr': PlayerAttr(),
                 'name': ' ', 'dismissal': ' ',
                 'no': None, 'runs': 0, 'balls': 0, 'wkts': 0, 'fifty': 0, 'hundred': 0, 'hattricks': 0, 'doubles': 0,
                 'threes': 0, 'balls_bowled': 0, 'runs_given': 0, 'maidens': 0, 'max_overs': 0, 'fours': 0, 'sixes': 0,
                 'singles': 0, 'dots': 0, 'eco': 0.0, 'strikerate': 0.0, 'catches': 0, 'stumpings': 0, 'runouts': 0,
                 'ball_history': [],
                 'status': True, 'spell_over': False, 'onfield': False, 'onstrike': False, 'iscaptain': False,
                 'isopeningbowler': False,
                 'nickname': '',
                 'wickets_taken': [],
                 'isspinner': False, 'ispacer': False}
        self = FillAttributes(self, attrs, kwargs)

    def GetMomStat(self):
        res = ''
        char_notout = ''
        if self.runs > 0:
            # if not out, give a *
            if self.status:
                char_notout = '*'
            res += "scored %s%s off %s balls" % (str(self.runs),
                                                 char_notout,
                                                 str(self.balls))

        char_runs_given = ''
        char_overs = ''
        char_wkts = ''
        if self.balls_bowled > 0:
            overs = BallsToOvers(self.balls_bowled)
            if self.runs_given > 1:
                char_runs_given = 's'
            if overs > 1:
                char_overs = 's'
            if self.wkts > 1:
                char_wkts = 's'
            res += " Took %s wkt%s,conceding %s run%s in %s over%s" % (str(self.wkts),
                                                                       char_wkts,
                                                                       str(self.runs_given),
                                                                       char_runs_given,
                                                                       str(overs),
                                                                       char_overs,
                                                                       )
        return res

    def SummarizeBowlerSpell(self):
        # FIXME randomize these commentary
        # FIXME also based on match (in T20, this might be good
        if self.eco <= 5.0:   print("Very economical spell from %s" % self.name)
        if self.eco < 6.0 and self.wkts >= 3:   print("A terrific spell from him!")
        if self.eco > 6.0 and self.wkts >= 3:   print("Got %s wkts but slightly expensive today" % str(self.wkts))
        if self.eco > 7.0 and self.wkts == 0:   print("Very disappointing performance from him!")

        # check if he has got any key wickets!
        key_wkts = []
        msg = ''
        if self.wkts > 0:
            for wicket in self.wickets_taken:
                if wicket.runs > 50:    key_wkts.append(wicket)
            if len(key_wkts) == 1:
                msg = "he has got the key wicket of %s" % (key_wkts[0].name)
            elif len(key_wkts) > 1:
                msg = "he has got the key wicket of %s" % (','.join([x.name for x in key_wkts]))
            print(msg)
        return


class Match:
    def __init__(self, **kwargs):
        attrs = {'status': False, 'overs': 0, 'match_type': None, 'bowler_max_overs': 0,
                 'logger': None, 'result': None, 'team1': None, 'team2': None, 'winner': None, 'loser': None,
                 'venue': None, 'umpire': None, 'commentators': None,
                 'drs': False,
                 'firstinnings': None, 'secondinnings': None,
                 'batting_first': None, 'batting_second': None, 'won': False, 'autoplay': False, 'batting_team': None,
                 'bowling_team': None}
        self = FillAttributes(self, attrs, kwargs)

    # update dismissal
    def UpdateDismissal(self, dismissal):
        batting_team, bowling_team = self.batting_team, self.bowling_team
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

        self.PrintCommentaryDismissal(dismissal)
        # show score
        self.CurrentMatchStatus()
        # get next batsman
        self.GetNextBatsman()
        input('press enter to continue')
        self.DisplayScore()
        self.DisplayProjectedScore()
        return

    # batting summary - scoreboard
    def DisplayScore(self):
        batting_team = self.batting_team
        logger = self.logger
        ch = '-'
        print(ch * 45)
        logger.info(ch * 45)

        msg = ch * 15 + 'Batting Summary' + ch * 15
        PrintInColor(msg, batting_team.color)
        logger.info(msg)
        print(ch * 45)
        logger.info(ch * 45)

        # this should be a nested list of 3 elements
        data_to_print = []
        for p in batting_team.team_array:
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

        msg = "Extras: %s" % str(batting_team.extras)
        print(msg)
        logger.info(msg)
        print(' ')
        logger.info(' ')

        msg = '%s %s/%s from (%s overs)' % (batting_team.name.upper(),
                                            str(batting_team.total_score),
                                            str(batting_team.wickets_fell),
                                            str(BallsToOvers(batting_team.total_balls)))
        PrintInColor(msg, batting_team.color)
        logger.info(msg)

        # show RR
        crr = batting_team.GetCurrentRate()
        msg = "RunRate: %s" % (str(crr))
        print(msg)
        logger.info(msg)
        print(' ')
        logger.info(' ')

        # show FOW
        if batting_team.wickets_fell != 0:
            PrintInColor('FOW:', Style.BRIGHT)
            logger.info('FOW:')
            # get fow_array
            fow_array = []
            for f in batting_team.fow:
                fow_array.append('%s/%s %s(%s)' % (str(f.runs),
                                                   str(f.wkt),
                                                   GetShortName(f.player_dismissed.name),
                                                   str(BallsToOvers(f.total_balls))))
            fow_str = ', '.join(fow_array)
            PrintInColor(fow_str, batting_team.color)
            logger.info(fow_str)

        # partnerships
        msg = "Partnerships:"
        PrintInColor(msg, Style.BRIGHT)
        logger.info(msg)
        for p in batting_team.partnerships:
            msg = '%s - %s :\t%s' % (p.batsman_onstrike.name,
                                     p.batsman_dismissed.name,
                                     str(p.runs))
            if p.batsman_dismissed.status and p.batsman_onstrike.status:
                msg += '*'
            print(msg)
            logger.info(msg)

        print(ch * 45)
        logger.info(ch * 45)
        return

    # generate run
    # FIXME: check current over, current player on strike, avoid this args
    def GenerateRun(self, over, player_on_strike):
        batting_team = self.batting_team
        bowler = self.bowling_team.current_bowler
        overs = self.overs
        venue = self.venue
        prob = venue.run_prob_t20

        # if ODI, override the prob
        if overs == 50:
            prob = venue.run_prob

        # run array
        run_array = [-1, 0, 1, 2, 3, 4, 5, 6]

        # death over situation
        prob_death = [0.2, 0.2, 0, 0, 0, 0.2, 0.2, 0.2]

        # in the death overs, increase prob of boundaries and wickets
        if over == overs - 1:
            prob = prob_death

        if batting_team.batting_second:
            # if required rate is too much, try to go big!
            if (batting_team.total_balls > 0 and
                    batting_team.GetRequiredRate() - batting_team.GetCurrentRate() >= 2.0 and
                    over <= overs - 2):
                prob = prob_death

            # if need 1 to win, don't take 2 or 3,
            if batting_team.target - batting_team.total_score == 1:
                prob = [1 / 7, 1 / 7, 1 / 7, 0, 0, 2 / 7, 1 / 7, 1 / 7, ]
            # if 2 to win, don't take 3
            if (batting_team.target - batting_team.total_score) == 2:
                prob = [1 / 7, 1 / 7, 1 / 7, 1 / 7, 0, 1 / 7, 1 / 7, 1 / 7, ]

        # FIXME:
        # if initial overs, play carefully based on RR
        # if death overs, try to go big
        # but, if batsman is poor and bowler is skilled, more chances of getting out
        if bowler.attr.bowling - player_on_strike.attr.batting >= 4:
            prob = [0.25, 0.20, 0.20, 0.15, 0.05, 0.05, 0.05, 0.05]

        # select from final run_array with the given probability distribution
        run = choice(run_array, 1, p=prob, replace=False)[0]
        return run

    # death over
    def DetectDeathOvers(self, over):
        batting_team = self.batting_team
        overs = self.overs
        # towards the death overs, show a highlights
        towin = abs(batting_team.target - batting_team.total_score)
        # calculate if score is close
        if batting_team.batting_second:
            if towin <= 0:
                # show batting team highlights
                self.ShowHighlights()
                PrintInColor("Match won!!", Fore.LIGHTGREEN_EX)
                self.status = False
            elif towin <= 20 or over == overs - 1:
                self.ShowHighlights()
                if towin == 1:
                    PrintInColor("Match tied!", Fore.LIGHTGREEN_EX)
                else:
                    PrintInColor('To win: %s from %s' % (str(towin),
                                                         str(overs * 6 - batting_team.total_balls)),
                                 Style.BRIGHT)
        return

    # match abandon due to rain
    def MatchAbandon(self):
        batting_team, bowling_team = self.batting_team, self.bowling_team

        # abandon due to rain
        PrintInColor(Randomize(commentary.commentary_rain_interrupt), Style.BRIGHT)
        input("Press any key to continue")

        # check nrr and crr
        nrr = batting_team.GetRequiredRate()
        crr = batting_team.GetCurrentRate()
        result = Result(team1=self.team1, team2=self.team2)

        remaining_overs = self.overs - BallsToOvers(batting_team.total_balls)
        simulated_score = int(round(remaining_overs * crr)) + batting_team.total_score

        result_str = "%s wins by %s run(s) using D/L method!"

        if crr >= nrr:
            # calculate win margin
            result_str = result_str % (batting_team.name, str(abs(simulated_score - batting_team.target)))
        else:
            result_str = result_str % (bowling_team.name, str(abs(batting_team.target - simulated_score)))
        input("Press any key to continue")

        self.status = False
        result.result_str = result_str
        self.DisplayScore()
        self.DisplayBowlingStats()

        # change result string
        self.result = result
        self.MatchSummary()
        self.FindPlayerOfTheMatch()
        return

    def CheckDRS(self):
        result = False
        team = self.batting_team
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
                    PrintInColor(Randomize(commentary.commentary_lbw_decision_stays) % self.umpire, Fore.LIGHTRED_EX)
                    team.drs_chances -= 1
        return result

    # print commentary for dismissal
    def PrintCommentaryDismissal(self, dismissal):
        # commentary
        comment = ' '
        pair = self.batting_team.current_pair
        bowler = self.bowling_team.current_bowler

        batting_team, bowling_team = self.batting_team, self.bowling_team
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
            PrintInColor(Randomize(commentary.commentary_out_first_ball) % GetSurname(player_dismissed.name),
                         Style.BRIGHT)

        # calculate the situation
        if batting_team.batting_second and (7 <= batting_team.wickets_fell < 10):
            PrintInColor(Randomize(commentary.commentary_goingtolose) % batting_team.name, Style.BRIGHT)

        # last man
        if batting_team.wickets_fell == 9:
            PrintInColor(Randomize(commentary.commentary_lastman), batting_team.color)
        return

    # assign bowler
    def AssignBowler(self):
        bowler = None
        bowling_team = self.bowling_team
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
                if self.autoplay:
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

    # get next batsman
    def GetNextBatsman(self):
        batting_team = self.batting_team
        pair = batting_team.current_pair
        player_dismissed = next((x for x in pair if not x.status), None)
        if batting_team.wickets_fell < 10:
            ind = pair.index(player_dismissed)

            # choose next one from the team
            pair[ind] = self.AssignBatsman(pair)

            pair[ind].onstrike = True
            PrintInColor("New Batsman: %s" % pair[ind].name, batting_team.color)
            # check if he is captain
            if pair[ind].attr.iscaptain:
                PrintInColor(Randomize(commentary.commentary_captain_to_bat_next), batting_team.color)

            # check if he had a good day with the ball earlier
            if pair[ind].balls_bowled > 0:
                if pair[ind].wkts >= 2:
                    PrintInColor(Randomize(commentary.commentary_good_bowler_to_bat), batting_team.color)
                if pair[ind].wkts == 0 and pair[ind].eco >= 7.0:
                    PrintInColor(Randomize(commentary.commentary_bad_bowler_to_bat), batting_team.color)

            # now new batter on field
            pair[ind].onfield = True

        batting_team.current_pair = pair
        return pair

    # assign batsman
    def AssignBatsman(self, pair):
        batting_team = self.batting_team
        remaining_batsmen = [plr for plr in batting_team.team_array if (plr.status and plr not in pair)]

        next_batsman = input('Choose next batsman: {0} [Press Enter to auto-select]'.format(
            ' / '.join([str(x.no) + '.' + GetShortName(x.name) for x in remaining_batsmen])))
        batsman = next((x for x in remaining_batsmen if (str(next_batsman) == str(x.no)
                                                         or next_batsman.lower() in GetShortName(x.name).lower())),
                       None)

        if batsman is None: Error_Exit("No batsman assigned!")
        return batsman

    # calculate match result
    def CalculateResult(self):
        team1 = self.team1
        team2 = self.team2

        result = Result(team1=team1,
                        team2=team2)
        # see who won
        loser = None
        if team1.total_score == team2.total_score:
            result.winner = None
            result.result_str = "Match Tied"
        elif team1.total_score > team2.total_score:
            result.winner, loser = team1, team2
            result.result_str = "%s won" % team1.name
        elif team2.total_score > team1.total_score:
            result.winner, loser = team2, team1
            result.result_str = "%s won" % team2.name
        else:
            result.result_str = "No result"

        if result.winner is not None:
            # if batting first, simply get diff between total runs
            # else get how many wkts remaining
            if result.winner.batting_second:
                win_margin = 10 - result.winner.wickets_fell
                if win_margin != 0:
                    result.result_str += " by %s wicket(s) with %s ball(s) left" % \
                                         (str(win_margin),
                                          str(self.overs * 6 - result.winner.total_balls))
            elif not result.winner.batting_second:
                win_margin = abs(result.winner.total_score - loser.total_score)
                if win_margin != 0:
                    result.result_str += " by %s run(s)" % (str(win_margin))

        self.result = result

    # find best player
    def FindBestPlayers(self):
        result = self.result
        total_players = result.team1.team_array + result.team2.team_array
        bowlers_list = self.team1.bowlers + self.team2.bowlers

        # find best batsman
        most_runs = sorted(total_players, key=lambda x: x.runs, reverse=True)
        if len(most_runs) >= 3:
            most_runs = most_runs[:3]  # we need only top 3 scorers
        result.most_runs = most_runs

        # find most wkts
        most_wkts = sorted(bowlers_list, key=lambda x: x.wkts, reverse=True)
        if len(most_wkts) >= 3:
            most_wkts = most_wkts[:3]  # we need only top 3 scorers
        result.most_wkts = most_wkts

        # find best eco bowler
        best_eco = sorted(bowlers_list, key=lambda x: x.eco, reverse=False)
        if len(best_eco) >= 3:
            best_eco = best_eco[:3]  # we need only top 3 scorers
        result.besteco = best_eco

        return result

    # Man of the match
    def FindPlayerOfTheMatch(self):
        # find which team won
        # if tied
        if self.team1.total_score == self.team2.total_score:
            self.winner = Randomize([self.team1, self.team2])
            self.loser = self.winner
        # if any team won
        else:
            self.winner, self.loser = max([self.team1, self.team2], key=attrgetter('total_score')), \
                min([self.team1, self.team2], key=attrgetter('total_score'))

        # find best batsman, bowler from winning team
        # always two batsmen will play
        best_batsmen = sorted(self.winner.team_array, key=attrgetter('runs'), reverse=True)
        best_bowlers = sorted(self.winner.bowlers, key=attrgetter('wkts'), reverse=True)

        # we need only two best batters
        if len(best_batsmen) > 2:
            best_batsmen = best_batsmen[:2]
        if len(best_bowlers) > 2:
            best_bowlers = best_bowlers[:2]

        # if both of them have same runs,
        if best_batsmen[0].runs == best_batsmen[1].runs:
            # find who is not out among these
            # if neither one is not out, get best SR
            if not [plr for plr in best_batsmen if plr.status]:
                best_batsman = sorted(best_batsmen, key=attrgetter('strikerate'), reverse=True)[0]
            # if there is one not out among them
            else:
                best_batsmen = [plr for plr in best_batsmen if plr.status]
                # if both are not out, select randomly
                if len(best_batsmen) == 2:
                    best_batsman = sorted(best_batsmen, key=attrgetter('strikerate'), reverse=True)[0]
                elif len(best_batsmen) == 1:
                    best_batsman = best_batsmen[0]

        else:
            best_batsman = best_batsmen[0]

        # if same wkts, get best economy bowler
        if best_bowlers[0].wkts == best_bowlers[1].wkts:
            best_bowler = sorted(best_bowlers, key=attrgetter('eco'), reverse=False)[0]
        else:
            best_bowler = best_bowlers[0]

        # check if mom is best batsman or bowler
        mom_is_batsman = 1
        mom_is_bowler = 1

        # check if win margin is >50% or if bowler took 5 wkts, if so, give credit to bowlers, else batsmen
        margin = float(self.winner.total_score / self.loser.total_score)
        if margin >= 1.2:
            mom_is_bowler += 1

        # if losing team is bowled out
        if self.loser.wickets_fell >= 8:
            # if there is a 5 or 3 wkt haul;
            if best_bowler.wkts >= 3:
                mom_is_bowler += 1

        best_player = best_batsman
        # check points
        if mom_is_bowler > mom_is_batsman:
            best_player = best_bowler

        # override
        # if a player is found in both top batsmen and bowler list he is my MOM
        common_players = list(set(best_bowlers).intersection(best_batsmen))
        if len(common_players) != 0:
            best_player = common_players[0]

        self.result.mom = best_player
        msg = "Player of the match: %s (%s)" % (best_player.name, best_player.GetMomStat())
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)

    # toss
    def Toss(self):
        logger = self.logger
        print('Toss..')
        print('We have the captains %s(%s) and %s(%s) in the middle' % (self.team1.captain.name,
                                                                        self.team1.name,
                                                                        self.team2.captain.name,
                                                                        self.team2.name))

        print('%s is gonna flip the coin' % self.team2.captain.name)
        # FIXME: use the ChooseFromOptions function here
        opts = [1, 2]
        call = input('%s, your call, Heads or tails? 1.Heads 2.Tails\n' % self.team1.captain.name)
        # if invalid, auto-select
        if call == '' or None:
            call = int(Randomize(opts))
            print("Invalid choice, auto-selected")
        coin = int(Randomize(opts))

        # check if call == coin selected
        if coin == call:
            call = input('%s, you have won the toss, do you wanna 1.Bat 2.Bowl first?\n' % self.team1.captain.name)
            # if invalid, auto-select
            if call == '' or None:
                call = int(Randomize(opts))
                print("Invalid choice, auto-selected")
            if int(call) == 1:
                msg = '%s has elected to bat first' % self.team1.captain.name
                PrintInColor(msg, self.team1.color)
                self.team1.batting_second = False
                self.team2.batting_second = True
                logger.info(msg)
            else:
                msg = '%s has elected to bowl first' % self.team1.captain.name
                PrintInColor(msg, self.team1.color)
                self.team2.batting_second = False
                self.team1.batting_second = True
                logger.info(msg)
        else:
            call = input('%s, you have won the toss, do you wanna 1.Bat 2.Bowl first?\n' % self.team2.captain.name)
            # if invalid, auto-select
            if call == '' or None:
                call = int(Randomize(opts))
                print("Invalid choice, auto-selected")
            if int(call) == 1:
                msg = '%s has elected to bat first' % self.team2.captain.name
                PrintInColor(msg, self.team2.color)
                self.team2.batting_second = False
                self.team1.batting_second = True
                logger.info(msg)
            else:
                msg = '%s has elected to bowl first' % self.team2.captain.name
                PrintInColor(msg, self.team2.color)
                self.team1.batting_second = False
                self.team2.batting_second = True
                logger.info(msg)

        # now find out who is batting first
        batting_first = next((x for x in [self.team1, self.team2] if not x.batting_second), None)
        batting_second = next((x for x in [self.team1, self.team2] if x.batting_second), None)
        self.batting_first = batting_first
        self.batting_second = batting_second

        # do you need DRS?
        drs_opted = ChooseFromOptions(['y', 'n'], "Do you need DRS for this match? ", 5)
        if drs_opted == 'y':
            print("DRS opted")
            self.drs = True
            input("press enter to continue")

        self.status = True
        return

    # validate teams
    def ValidateMatchTeams(self):
        if self.team1 is None or self.team2 is None:
            Error_Exit('No teams found!')

        for t in [self.team1, self.team2]:
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
                    bowler.max_overs = self.bowler_max_overs

        # ensure no common members in the teams
        common_players = list(set(self.team1.team_array).intersection(self.team2.team_array))
        if common_players:
            Error_Exit("Common players in teams found! : %s" % (','.join([p.name for p in common_players])))

        # make first batsman on strike
        for t in [self.team1, self.team2]:
            t.opening_pair[0].onstrike, t.opening_pair[1].onstrike = True, False
            t.opening_pair[0].onfield, t.opening_pair[1].onfield = True, True

        # check if players have numbers, else assign randomly
        # using np instead of random.choice so that there are no duplicates
        import numpy as np
        for t in [self.team1, self.team2]:
            for player in t.team_array:
                if player.no is None:
                    player.no = np.random.choice(list(range(100)), size=1, replace=False)[0]
        PrintInColor('Validated teams', Style.BRIGHT)
        return

    # check ball history so far
    def GetBallHistory(self):
        batting_team = self.batting_team
        # check extras
        # FIXME: this isnt used?
        noballs = batting_team.ball_history.count('NB')
        wides = batting_team.ball_history.count('WD')
        runouts = batting_team.ball_history.count('RO')
        sixes = batting_team.ball_history.count(6)
        fours = batting_team.ball_history.count(4)
        return

    # update extras
    def UpdateExtras(self):
        batting_team, bowling_team = self.batting_team, self.bowling_team
        bowler = bowling_team.current_bowler

        logger = self.logger
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
            PrintInColor(Randomize(commentary.commentary_wide) % self.umpire, Style.BRIGHT)
            logger.info("WIDE")
        elif extra == 'nb':
            # no balls
            bowler.ball_history.append('NB')
            batting_team.ball_history.append('NB')
            PrintInColor("NO BALL...!", Fore.LIGHTCYAN_EX)
            PrintInColor(Randomize(commentary.commentary_no_ball), Style.BRIGHT)
            logger.info("NO BALL")

        return

    # get bowler comments
    def GetBowlerComments(self):
        bowler = self.bowling_team.current_bowler
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
        if (BallsToOvers(bowler.balls_bowled) == self.bowler_max_overs - 1) and (bowler.balls_bowled != 0):
            PrintInColor(Randomize(commentary.commentary_bowler_last_over), Style.BRIGHT)
            if bowler.wkts >= 3 or bowler.eco <= 5.0:
                PrintInColor(Randomize(commentary.commentary_bowler_good_spell), Style.BRIGHT)
            elif bowler.eco >= 7.0:
                PrintInColor(Randomize(commentary.commentary_bowler_bad_spell), Style.BRIGHT)
        return

    # check for milestones
    def CheckMilestone(self):
        logger = self.logger
        batting_team = self.batting_team
        pair = batting_team.current_pair

        # call_by_first_name = Randomize([True, False])

        for p in pair:
            name = GetFirstName(p.name)
            if not Randomize([True, False]):
                name = GetSurname(p.name)
            # if nickname defined, call by it
            if p.nickname != '' or None:
                name = p.nickname

            # first fifty
            if p.runs >= 50 and p.fifty == 0:
                p.fifty += 1
                msg = "50 for %s!" % name
                PrintInColor(msg, batting_team.color)
                logger.info(msg)
                PrintInColor("%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT)
                # check if captain
                if p.attr.iscaptain:
                    PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)

                # call by first name or last name
                PrintInColor(Randomize(commentary.commentary_milestone) % name, batting_team.color)

                #  check if he had a good day with the ball as well
                if p.wkts >= 2:
                    PrintInColor(Randomize(commentary.commentary_all_round_batsman), batting_team.color)

            elif p.runs >= 100 and (p.fifty == 1 and p.hundred == 0):
                # after first fifty is done
                p.hundred += 1
                p.fifty += 1
                msg = "100 for %s!" % name
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
                msg = "200 for %s! What a superman!" % name
                PrintInColor(msg, batting_team.color)
                logger.info(msg)
                PrintInColor("%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT)
                # check if captain
                if p.attr.iscaptain:
                    PrintInColor(Randomize(commentary.commentary_captain_leading), batting_team.color)
                PrintInColor(Randomize(commentary.commentary_milestone) % name, batting_team.color)

        input('press enter to continue..')
        return

    # update last partnership
    def UpdateLastPartnership(self):
        batting_team = self.batting_team
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

    # randomly select a mode of dismissals
    def GenerateDismissal(self):
        bowling_team = self.bowling_team
        bowler = bowling_team.current_bowler
        keeper = bowling_team.keeper

        dismissal_str = None
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
            keeper.stumpings += 1

        elif dismissal == 'c':
            fielder.catches += 1
            # check if catcher is the bowler
            if fielder == bowler:
                dismissal_str = 'c&b %s' % (GetShortName(bowler.name))
            else:
                dismissal_str = '%s %s b %s' % (dismissal, GetShortName(fielder.name), GetShortName(bowler.name))
        elif dismissal == 'runout':
            fielder.runouts += 1
            dismissal_str = 'runout %s' % (GetShortName(fielder.name))

        # check if fielder is on fire!
        if fielder.runouts >= 2 or fielder.catches >= 2:
            PrintInColor(Randomize(commentary.commentary_fielder_on_fire) % fielder.name, bowling_team.color)
        if keeper.stumpings >= 2:
            PrintInColor(Randomize(commentary.commentary_fielder_on_fire) % keeper.name, bowling_team.color)

        return dismissal_str

    # Showhighights
    def ShowHighlights(self):
        logger = self.logger
        batting_team, bowling_team = self.batting_team, self.bowling_team
        crr = batting_team.GetCurrentRate()
        rr = batting_team.GetRequiredRate()

        # if match ended, do nothing, just return
        if not self.status:
            return

        # default msg
        msg = '\n%s %s / %s (%s Overs)' % (batting_team.name,
                                           str(batting_team.total_score),
                                           str(batting_team.wickets_fell),
                                           str(BallsToOvers(batting_team.total_balls)))
        msg += ' Current RR: %s' % str(crr)
        if batting_team.batting_second and self.status:
            msg += ' Required RR: %s\n' % str(rr)
        PrintInColor(msg, Style.BRIGHT)
        logger.info(msg)
        return

    # comment about the current match status
    def CurrentMatchStatus(self):
        logger = self.logger
        batting_team, bowling_team = self.batting_team, self.bowling_team
        crr = batting_team.GetCurrentRate()
        rr = batting_team.GetRequiredRate()

        # if match ended, nothing, just return
        if not self.status:
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
                    PrintInColor(Randomize(commentary.commentary_situation_reqd_rate_low) % batting_team.name,
                                 Fore.GREEN)
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
                PrintInColor(Randomize(commentary.commentary_situation_reqd_rate_high) % batting_team.name,
                             Style.BRIGHT)
                if 0 <= batting_team.wickets_fell <= 2:
                    PrintInColor(Randomize(commentary.commentary_situation_got_wkts_in_hand) % batting_team.name,
                                 Style.BRIGHT)
                if 7 <= batting_team.wickets_fell < 10:
                    PrintInColor(Randomize(commentary.commentary_situation_gone_case) % batting_team.name, Fore.RED)
                    # say who can save the match
                    PrintInColor(Randomize(commentary.commentary_situation_savior) % savior.name, Fore.RED)

        return

    # display projected score
    def DisplayProjectedScore(self):
        if not self.status:   return
        if BallsToOvers(self.batting_team.total_balls) == self.overs: return
        import numpy as np
        overs_left = BallsToOvers(self.overs * 6 - self.batting_team.total_balls)
        current_score = self.batting_team.total_score
        crr = self.batting_team.GetCurrentRate()
        proj_score = lambda x: np.ceil(current_score + (x * overs_left))
        print("Projected Score")
        # FIXME this has some wierd notation at times. round them off to 1/2
        print('Current Rate(%s): %s' % (str(crr), proj_score(crr)), end=' ')
        lim = crr + 3.0
        crr += 0.5
        while crr <= lim:
            print('%s: %s' % (str(crr), proj_score(crr)), end=' ')
            crr += 1.0
        print('\n')

    # print bowlers stats
    def DisplayBowlingStats(self):
        logger = self.logger
        team = self.bowling_team
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
        return

    # print playing XI
    def DisplayPlayingXI(self):
        t1, t2 = self.team1, self.team2
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

    # match summary
    def MatchSummary(self):
        logger = self.logger
        ch = '-'
        result = self.result

        msg = '%s Match Summary %s' % (ch * 10, ch * 10)
        PrintInColor(msg, Style.BRIGHT)
        logger.info(msg)

        msg = '%s vs %s, at %s' % (result.team1.name, result.team2.name, self.venue.name)
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


class Innings:
    def __init__(self, **kwargs):
        attrs = {'status': False, 'overs': 0, 'result': None, 'batting_team': None, 'bowling_team': None}
        self = FillAttributes(self, attrs, kwargs)


class Fow:
    def __init__(self, **kwargs):
        attrs = {'total_balls': 0, 'wkt': 0, 'runs': 0, 'player_dismissed': None, 'player_onstrike': None}
        self = FillAttributes(self, attrs, kwargs)


class Partnership:
    def __init__(self, **kwargs):
        attrs = {'balls': 0, 'runs': 0, 'batsman_dismissed': None, 'batsman_onstrike': None, 'both_notout': False}
        self = FillAttributes(self, attrs, kwargs)


class Result:
    def __init__(self, **kwargs):
        attrs = {'team1': None, 'team2': None, 'winner': None, 'most_runs': None, 'most_wkts': None, 'best_eco': None,
                 'mom': None, 'result_str': ' '}
        self = FillAttributes(self, attrs, kwargs)


class Team:
    def __init__(self, **kwargs):
        attrs = {'total_overs': 0, 'drs_chances': 2, 'total_score': 0, 'target': 0, 'wickets_fell': 0, 'total_balls': 0,
                 'extras': 0, 'top_scorer': None, 'most_wkts': None, 'off_the_mark': False,
                 'fours': 0, 'sixes': 0,
                 'fifty_up': False, 'hundred_up': False, 'two_hundred_up': False, 'three_hundred_up': False,
                 'innings_over': False, 'batting_second': False, 'name': ' ', 'key': ' ',
                 'last_bowler': None, 'captain': None, 'keeper': None, 'color': None,
                 'team_array': [], 'opening_pair': [], 'bowlers': [], 'fow': [], 'partnerships': [],
                 'current_pair': [],
                 'current_bowler': None,
                 'ball_history': [], }
        self = FillAttributes(self, attrs, kwargs)

    def SummarizeBatting(self):
        # find what happened in the top order
        # check if it was a good score
        total_runs = self.total_score
        total_overs = self.total_overs
        wkts = self.wickets_fell
        # say if this was a good total
        msg = 'Thats the end of the innings, and %s has scored %s off %s overs..' % (
            self.name, str(total_runs), str(total_overs))
        nrr = self.GetCurrentRate()
        if nrr > 7.0 and wkts < 10:
            msg += 'They have scored at a terrific rate of %s ' % (str(nrr))
        if wkts == 10:
            msg += 'They have been bowled out!'

        print(msg)
        # now say about the top order
        top_order_collapse = middle_order_collapse = False
        tail_good_performance = False

        top_order = [x for x in self.team_array[:4] if x.balls > 0]
        top_order_good = [x for x in top_order if x.runs >= 30]
        top_order_great = [x for x in top_order if x.runs >= 50]
        top_order_poor = [x for x in top_order if x.runs <= 10]
        if len(top_order_poor) >= 3:
            top_order_collapse = True

        middle_order = [x for x in self.team_array[4:7] if x.balls > 0]
        middle_order_good = [x for x in middle_order if x.runs >= 30]
        middle_order_great = [x for x in middle_order if x.runs >= 50]
        middle_order_poor = [x for x in middle_order if x.runs <= 10]
        if len(middle_order_poor) >= 3:
            middle_order_collapse = True

        tail = self.team_array[8:10]
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

    def SummarizeBowling(self):
        # get best bowlers
        # FIXME say if good performance
        best_economical_bowlers = [x for x in self.team_array if x.eco < 6.0 and x.balls_bowled > 0]
        best_wickets_bowlers = [x for x in self.team_array if x.wkts >= 3 and x.balls_bowled > 0]
        if len(best_economical_bowlers) > 0:
            msg = ','.join(x.name for x in best_economical_bowlers)
            # FIXME randomize this commentary
            print("Very economical stuff from %s" % msg)
        if len(best_wickets_bowlers) > 0:
            msg = ','.join(x.name for x in best_wickets_bowlers)
            print("Most wickets taken by %s" % msg)
        input()
        return

    def GetCurrentRate(self):
        crr = 0.0
        if self.total_balls > 0:
            crr = self.total_score / BallsToOvers(self.total_balls)
        crr = round(crr, 2)
        return crr

    def GetRequiredRate(self):
        nrr = 0.0
        # if chasing, calc net nrr
        balls_remaining = self.total_overs * 6 - self.total_balls
        if balls_remaining > 0:
            overs_remaining = BallsToOvers(balls_remaining)
            towin = self.target - self.total_score
            nrr = float(towin / overs_remaining)
            nrr = round(nrr, 2)
        return nrr


class Delivery:
    def __init__(self, **kwargs):
        attrs = {'type': None, 'speed': None, 'line': None, 'length': None, }
        self = FillAttributes(self, attrs, kwargs)


class Shot:
    def __init__(self, **kwargs):
        attrs = {'type': None, 'direction': None, 'foot': None, }
        self = FillAttributes(self, attrs, kwargs)
