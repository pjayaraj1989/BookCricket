from colorama import Style
from functions.Base.PlayerAttr import PlayerAttr
from functions.utilities import FillAttributes, BallsToOvers, PrintInColor


class Player:
    def __init__(self, **kwargs):
        """
        Initialize a Player object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Player object.
        """
        attrs = {
            "attr": PlayerAttr(),
            "name": " ",
            "dismissal": " ",
            "no": None,
            "runs": 0,
            "balls": 0,
            "wkts": 0,
            "fifty": 0,
            "hundred": 0,
            "hattricks": 0,
            "doubles": 0,
            "threes": 0,
            "balls_bowled": 0,
            "runs_given": 0,
            "maidens": 0,
            "max_overs": 0,
            "fours": 0,
            "sixes": 0,
            "singles": 0,
            "dots": 0,
            "eco": 0.0,
            "strikerate": 0.0,
            "catches": 0,
            "stumpings": 0,
            "runouts": 0,
            "ball_history": [],
            "status": True,
            "spell_over": False,
            "onfield": False,
            "onstrike": False,
            "iscaptain": False,
            "isopeningbowler": False,
            "nickname": "",
            "wickets_taken": [],
            "isspinner": False,
            "ispacer": False,
        }
        self = FillAttributes(self, attrs, kwargs)

    def GetMomStat(self):
        """
        Get the Man of the Match statistics for the player.

        Returns:
            str: The Man of the Match statistics.
        """
        res = ""
        char_notout = ""
        if self.runs > 0:
            # if not out, give a *
            if self.status:
                char_notout = "*"
            res += "scored %s%s off %s balls" % (
                str(self.runs),
                char_notout,
                str(self.balls),
            )

        char_runs_given = ""
        char_overs = ""
        char_wkts = ""
        if self.balls_bowled > 0:
            overs = BallsToOvers(self.balls_bowled)
            if self.runs_given > 1:
                char_runs_given = "s"
            if overs > 1:
                char_overs = "s"
            if self.wkts > 1:
                char_wkts = "s"
            res += " Took %s wicket%s, conceding %s run%s in %s over%s" % (
                str(self.wkts),
                char_wkts,
                str(self.runs_given),
                char_runs_given,
                str(overs),
                char_overs,
            )
        return res

    def SummarizeBowlerSpell(self):
        """
        Summarize the bowler's spell.

        Returns:
            None
        """
        # FIXME randomize these commentary
        # FIXME also based on match (in T20, this might be good
        if self.eco <= 5.0:
            PrintInColor("Very economical spell from %s" % self.name, Style.BRIGHT)
        if self.eco < 6.0 and self.wkts >= 3:
            PrintInColor("A terrific spell from him!", Style.BRIGHT)
        if self.eco > 6.0 and self.wkts >= 3:
            PrintInColor(
                "Got %s wkts but slightly expensive today" % str(self.wkts),
                Style.BRIGHT,
            )
        if self.eco > 7.0 and self.wkts == 0:
            PrintInColor("Very disappointing performance from him!", Style.BRIGHT)

        # check if he has got any key wickets!
        key_wkts = []
        msg = ""
        if self.wkts > 0:
            for wicket in self.wickets_taken:
                if wicket.runs > 50:
                    key_wkts.append(wicket)
            if len(key_wkts) == 1:
                msg = "he has got the key wicket of %s" % (key_wkts[0].name)
            elif len(key_wkts) > 1:
                msg = "he has got the key wicket of %s" % (
                    ",".join([x.name for x in key_wkts])
                )
            print(msg)
        return
