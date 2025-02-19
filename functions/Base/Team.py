from colorama import Style
from functions.utilities import FillAttributes, BallsToOvers, PrintInColor, PrintListFormatted


class Team:
    def __init__(self, **kwargs):
        """
        Initialize a Team object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Team object.
        """
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
        """
        Summarize the batting performance of the team.

        Returns:
            None
        """
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

        PrintInColor(msg, Style.BRIGHT)
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
                PrintInColor("In the top order, there were some stable performers %s played really well" % msg, Style.BRIGHT)
            if len(top_order_great) != 0:
                msg = ','.join(x.name for x in top_order_great)
                PrintInColor("terrific from %s high quality batting" % msg, Style.BRIGHT)
            if len(top_order_poor) != 0:
                msg = ','.join(x.name for x in top_order_poor)
                PrintInColor("Disappointment for %s" % msg, Style.BRIGHT)

        # same for middle order and tail
        if len(middle_order) != 0:
            if len(middle_order_good) != 0:
                msg = ','.join(x.name for x in middle_order_good)
                PrintInColor("some stable performance in the middle order %s" % msg, Style.BRIGHT)
            if len(middle_order_great) != 0:
                msg = ','.join(x.name for x in middle_order_great)
                PrintInColor("terrific batting from %s" % msg, Style.BRIGHT)
            if len(middle_order_poor) != 0:
                msg = ','.join(x.name for x in middle_order_poor)
                PrintInColor("Disappointment for %s" % msg, Style.BRIGHT)

        # see if tail did great
        if len(tail) != 0 and len(tail_good) != 0:
            msg = ','.join(x.name for x in tail_great)
            PrintInColor("terrific effort from the lower order! %s" % msg, Style.BRIGHT)

        # randomize this commentary
        if top_order_collapse and not middle_order_collapse:
            PrintInColor("We have seen some top order collapse!.. but good come back in the middle order", Style.BRIGHT)
        if not top_order_collapse and middle_order_collapse:
            PrintInColor("The top order gave a good start.. but middle order collapsed!", Style.BRIGHT)
        if tail_good_performance:
            PrintInColor("Some terrific fightback from the tail!", Style.BRIGHT)
        # FIXME say about chasing, facing bowlers, etc
        input()
        return

    def SummarizeBowling(self):
        """
        Summarize the bowling performance of the team.

        Returns:
            None
        """
        # get best bowlers
        # FIXME say if good performance
        best_economical_bowlers = [x for x in self.team_array if x.eco < 6.0 and x.balls_bowled > 0]
        best_wickets_bowlers = [x for x in self.team_array if x.wkts >= 3 and x.balls_bowled > 0]
        if len(best_economical_bowlers) > 0:
            msg = ','.join(x.name for x in best_economical_bowlers)
            # FIXME randomize this commentary
            PrintInColor("Very economical stuff from %s" % msg, Style.BRIGHT)
        if len(best_wickets_bowlers) > 0:
            msg = ','.join(x.name for x in best_wickets_bowlers)
            PrintInColor("Most wickets taken by %s" % msg, Style.BRIGHT)
        input()
        return

    def GetCurrentRate(self):
        """
        Calculate the current run rate of the team.

        Returns:
            float: The current run rate.
        """
        crr = 0.0
        if self.total_balls > 0:
            crr = self.total_score / BallsToOvers(self.total_balls)
        crr = round(crr, 2)
        return crr

    def GetRequiredRate(self):
        """
        Calculate the required run rate for the team.

        Returns:
            float: The required run rate.
        """
        nrr = 0.0
        # if chasing, calc net nrr
        balls_remaining = self.total_overs * 6 - self.total_balls
        if balls_remaining > 0:
            overs_remaining = BallsToOvers(balls_remaining)
            towin = self.target - self.total_score
            nrr = float(towin / overs_remaining)
            nrr = round(nrr, 2)
        return nrr