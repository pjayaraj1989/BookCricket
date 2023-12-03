from functions.utilities import FillAttributes, BallsToOvers, PrintInColor, GetShortName, PrintListFormatted, Randomize
from colorama import Style, Fore
from data.commentary import *

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
