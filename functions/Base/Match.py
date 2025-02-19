import logging
import os
import random
import time
from operator import attrgetter
from colorama import Style, Fore
from numpy.random import choice
from data.commentary import commentary
from data.resources import resources
from functions.Pair import RotateStrike, PairFaceBall, BatsmanOut
from functions.helper import Partnership, Fow, Result
from functions.utilities import (
    FillAttributes,
    PrintInColor,
    Randomize,
    Error_Exit,
    GetShortName,
    BallsToOvers,
    PrintListFormatted,
    GetFirstName,
    GetSurname,
    CheckForConsecutiveElements,
    ChooseFromOptions,
)


class Match:
    def __init__(self, **kwargs):
        """
        Initialize a Match object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Match object.
        """
        attrs = {
            "status": False,
            "overs": 0,
            "match_type": None,
            "bowler_max_overs": 0,
            "logger": None,
            "result": None,
            "team1": None,
            "team2": None,
            "winner": None,
            "loser": None,
            "venue": None,
            "umpire": None,
            "commentators": None,
            "drs": False,
            "firstinnings": None,
            "secondinnings": None,
            "batting_first": None,
            "batting_second": None,
            "won": False,
            "autoplay": False,
            "batting_team": None,
            "bowling_team": None,
        }
        self = FillAttributes(self, attrs, kwargs)

    def PlayMatch(self, ScriptPath):
        """
        Play the match.

        Args:
            ScriptPath: The path to the script directory.

        Returns:
            None
        """
        # logging
        log_file = "log_%s_v_%s_%s_%s_overs.log" % (
            self.team1.name,
            self.team2.name,
            self.venue.name.replace(" ", "_"),
            str(self.overs),
        )
        log_folder = os.path.join(ScriptPath, "logs")
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
        self.logger = logger

        # see if teams are valid
        self.ValidateMatchTeams()

        # toss, select who is batting first
        self.Toss()
        self.team1, self.team2 = self.batting_first, self.batting_second

        # match start
        self.status = True
        self.batting_team, self.bowling_team = self.team1, self.team2

        # play 1st innings
        self.Play()

        # display batting and bowling scorecard
        self.DisplayScore()
        self.DisplayBowlingStats()

        # say something about the first innings
        self.batting_team.SummarizeBatting()
        # summarize about bowling performance
        self.bowling_team.SummarizeBowling()

        # play second inns with target
        self.team2.target = self.team1.total_score + 1

        # swap teams now
        self.batting_team, self.bowling_team = self.team2, self.team1

        # play second innings
        self.Play()

        # show batting and bowling scores
        self.DisplayScore()
        self.DisplayBowlingStats()

        # match ended
        self.status = False

        # show results
        self.CalculateResult()

        # say something about the first innings
        self.batting_team.SummarizeBatting()
        # summarize about bowling performance
        self.bowling_team.SummarizeBowling()

        self.MatchSummary()
        self.FindPlayerOfTheMatch()

        # close log handler
        handler.close()
        return

    def Play(self):
        """
        Play the innings.

        Returns:
            None
        """
        batting_team = self.batting_team
        overs = self.overs
        logger = self.logger
        pair = batting_team.opening_pair

        comment = ""
        over_interrupt = 0
        if batting_team.batting_second is True:
            # in case of rainy, interrupt match intermittently
            if self.venue.weather == "rainy":
                over_interrupt = random.choice(list(range(15, 50)))

            msg = "Target for %s: %s from %s overs" % (
                batting_team.name,
                str(batting_team.target),
                str(overs),
            )
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
            if batting_team.batting_second and self.venue.weather == "rainy":
                if over == over_interrupt - 5:
                    PrintInColor(
                        Randomize(commentary.commentary_rain_cloudy), Style.BRIGHT
                    )
                elif over == over_interrupt - 3:
                    PrintInColor(
                        Randomize(commentary.commentary_rain_drizzling), Style.BRIGHT
                    )
                elif over == over_interrupt - 1:
                    PrintInColor(
                        Randomize(commentary.commentary_rain_heavy), Style.BRIGHT
                    )
                elif over == over_interrupt:
                    self.MatchAbandon()
                    self.result.result_str = "No result"
                    Error_Exit("Match abandoned due to rain!!")
                input("Press enter to continue")

            # check match stats and comment
            if self.status is False:
                break

            # check if last over
            if over == overs - 1:
                if batting_team.batting_second:
                    PrintInColor(
                        Randomize(commentary.commentary_last_over_match), Style.BRIGHT
                    )
                else:
                    PrintInColor(
                        Randomize(commentary.commentary_last_over_innings), Style.BRIGHT
                    )

            # check hows it going in regular intervals
            if over > 1 and over % 5 == 0:
                self.CurrentMatchStatus()

            # play an over
            self.batting_team.current_pair = pair

            # if all out
            if self.batting_team.wickets_fell == 10:
                break
            self.PlayOver(over)
            if self.status is False:
                break

            # show batting stats
            for p in pair:
                msg = "%s %s (%s)" % (GetShortName(p.name), str(p.runs), str(p.balls))
                print(msg)
                logger.info(msg)

            self.ShowHighlights()
            self.DisplayBowlingStats()
            self.DisplayScore()
            self.DisplayProjectedScore()
            # rotate strike after an over
            RotateStrike(pair)
        return

    def PlayOver(self, over):
        """
        Play an over.

        Args:
            over: The current over number.

        Returns:
            None
        """
        pair = self.batting_team.current_pair
        overs = self.overs
        batting_team, bowling_team = self.batting_team, self.bowling_team
        logger = self.logger

        # get bowler
        bowler = self.AssignBowler()

        msg = "New bowler is %s" % (bowler.name)
        PrintInColor(msg, bowling_team.color)
        msg = "New bowler: %s %s/%s (%s)" % (
            bowler.name,
            str(bowler.runs_given),
            str(bowler.wkts),
            str(BallsToOvers(bowler.balls_bowled)),
        )
        print(msg)
        logger.info(msg)

        # assign current bowler
        self.bowling_team.current_bowler = bowler
        bowling_team.last_bowler = bowler

        # update bowler economy
        if bowler.balls_bowled > 0:
            eco = float(bowler.runs_given / BallsToOvers(bowler.balls_bowled))
            eco = round(eco, 2)
            bowler.eco = eco

        self.GetBowlerComments()

        ismaiden = True
        total_runs_in_over = 0
        ball = 1
        over_arr = []

        # loop for an over
        while ball <= 6:
            # if match ended
            if not self.status:
                break

            # check if dramatic over!
            if over_arr.count(6) > 2 or over_arr.count(4) > 2 and -1 in over_arr:
                PrintInColor(
                    Randomize(commentary.commentary_dramatic_over), Style.BRIGHT
                )

            if over == overs - 1 and ball == 6:
                if batting_team.batting_second:
                    PrintInColor(
                        Randomize(commentary.commentary_last_ball_match), Style.BRIGHT
                    )
                else:
                    PrintInColor(
                        Randomize(commentary.commentary_last_ball_innings), Style.BRIGHT
                    )

            self.DetectDeathOvers(over)

            print("Over: %s.%s" % (str(over), str(ball)))
            player_on_strike = next((x for x in pair if x.onstrike), None)
            print(
                "%s to %s"
                % (GetShortName(bowler.name), GetShortName(player_on_strike.name)),
                Style.BRIGHT,
            )
            if self.autoplay:
                time.sleep(1)
            else:
                input("press enter to continue..")

            # generate run, updates runs and maiden status
            # FIXME dont pass over and player on strike, instead detect it!
            run = self.GenerateRun(over, player_on_strike)
            # run = GenerateRunNew(match, over, player_on_strike)

            over_arr.append(run)

            # detect too many wkts or boundaries
            if over_arr.count(-1) > 2:
                PrintInColor(
                    "%s wickets already in this over!" % str(over_arr.count(-1)),
                    Style.BRIGHT,
                )
            if (over_arr.count(4) + over_arr.count(6)) > 2:
                print(
                    "%s boundaries already in this over!"
                    % str(over_arr.count(4) + over_arr.count(6)),
                    Style.BRIGHT,
                )

            # check if maiden or not
            if run not in [-1, 0]:
                ismaiden = False

            # check if extra
            if run == 5:
                self.UpdateExtras()
                # comment on too many extras
                if over_arr.count(5) > 2:
                    PrintInColor(
                        "%s extras in this over!" % str(over_arr.count(5)), Style.BRIGHT
                    )
                total_runs_in_over += 1
                if self.status is False:
                    break

            # if not wide
            else:
                self.Ball(run)
                ball += 1
                if run != -1:
                    total_runs_in_over += run
                if self.status is False:
                    break

            if batting_team.total_balls == (self.overs * 6):
                PrintInColor("End of innings", Fore.LIGHTCYAN_EX)
                # update last partnership
                if batting_team.wickets_fell > 0:
                    last_fow = batting_team.fow[-1].runs
                    last_partnership_runs = batting_team.total_score - last_fow
                    last_partnership = Partnership(
                        batsman_dismissed=pair[0],
                        batsman_onstrike=pair[1],
                        runs=last_partnership_runs,
                    )
                    batting_team.partnerships.append(last_partnership)
                    input("press enter to continue")
                    break

            # check if 1st innings over
            # if all out first innings
            if not batting_team.batting_second:
                if batting_team.wickets_fell == 10:
                    PrintInColor(
                        Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX
                    )
                    if (self.overs * 6) / batting_team.total_score <= 1.2:
                        PrintInColor(
                            Randomize(commentary.commentary_all_out_good_score),
                            Fore.GREEN,
                        )
                    elif 0.0 <= batting_team.GetCurrentRate() >= 1.42:
                        PrintInColor(
                            Randomize(commentary.commentary_all_out_bad_score),
                            Fore.GREEN,
                        )
                    input("press enter to continue...")
                    break

            # batting second
            elif batting_team.batting_second:
                if batting_team.total_balls >= (self.overs * 6):
                    # update last partnership
                    self.UpdateLastPartnership()
                    self.status = False
                    # if won in the last ball
                    if batting_team.total_score >= batting_team.target:
                        PrintInColor(
                            Randomize(commentary.commentary_won_last_ball)
                            % (batting_team.name, bowling_team.name),
                            Style.BRIGHT,
                        )
                    else:
                        PrintInColor(
                            Randomize(commentary.commentary_lost_chasing)
                            % (batting_team.name, bowling_team.name),
                            Style.BRIGHT,
                        )
                    input("press enter to continue...")
                    break
                # check if target achieved chasing
                if batting_team.total_score >= batting_team.target:
                    PrintInColor(
                        Randomize(commentary.commentary_match_won), Fore.LIGHTGREEN_EX
                    )
                    PrintInColor(
                        Randomize(commentary.commentary_match_won_chasing),
                        Fore.LIGHTGREEN_EX,
                    )
                    self.status = False
                    self.UpdateLastPartnership()
                    input("press enter to continue...")
                    break
                # if all out first innings
                if batting_team.wickets_fell == 10:
                    PrintInColor(
                        Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX
                    )
                    input("press enter to continue...")
                    break

        # check total runs taken in over
        # if expensive over
        if total_runs_in_over > 14:
            PrintInColor(
                Randomize(commentary.commentary_expensive_over) % bowler.name
                + "\n"
                + "%s runs in this over!" % (str(total_runs_in_over)),
                Style.BRIGHT,
            )
        # check if maiden over only if over is finished
        elif total_runs_in_over == 0:
            PrintInColor(
                Randomize(commentary.commentary_maiden_over) % bowler.name, Style.BRIGHT
            )
            bowler.maidens += 1
        # check for an economical over
        elif total_runs_in_over < 6:
            PrintInColor(
                Randomize(commentary.commentary_economical_over) % bowler.name
                + "\n"
                + "only %s runs off this over!" % (str(total_runs_in_over)),
                Style.BRIGHT,
            )

        # if bowler finished his spell, update it
        if BallsToOvers(bowler.balls_bowled) == bowler.max_overs:
            bowler.spell_over = True
            PrintInColor(
                Randomize(commentary.commentary_bowler_finished_spell) % bowler.name,
                Style.BRIGHT,
            )
            # now say about his performance
            bowler.SummarizeBowlerSpell()
        return

    def Ball(self, run):
        """
        Play a ball.

        Args:
            run: The number of runs scored on the ball.

        Returns:
            None
        """
        batting_team, bowling_team = self.batting_team, self.bowling_team
        bowler = bowling_team.current_bowler
        logger = self.logger
        pair = batting_team.current_pair

        # get who is on strike
        on_strike = next((x for x in pair if x.onstrike), None)

        # first runs
        if (
            batting_team.total_score == 0
            and (run not in [-1, 0])
            and not batting_team.off_the_mark
        ):
            PrintInColor(
                Randomize(commentary.commentary_first_runs)
                % (batting_team.name, on_strike.name),
                batting_team.color,
            )
            batting_team.off_the_mark = True

        # if out
        used_drs = False
        while run == -1:
            dismissal = self.GenerateDismissal()
            if "lbw" in dismissal:
                PrintInColor(
                    Randomize(commentary.commentary_lbw_umpire) % self.umpire,
                    Fore.LIGHTRED_EX,
                )

                # if match has no DRS, do not go into this
                if self.drs is False:
                    self.UpdateDismissal(dismissal)
                    return

                # if DRS opted, check
                result = self.CheckDRS()

                # overturn
                if result:
                    run = 0
                    used_drs = True
                    break
                # decision stays
                else:
                    self.UpdateDismissal(dismissal)
                    return
            else:
                self.UpdateDismissal(dismissal)
                return

        # appropriate commentary for 4s and 6s
        if run == 4:
            # check if this is after a wicket?
            if batting_team.ball_history != []:
                if "Wkt" in str(batting_team.ball_history[-1]) or "RO" in str(
                    batting_team.ball_history[-1]
                ):
                    PrintInColor(
                        Randomize(commentary.commentary_boundary_after_wkt),
                        Fore.LIGHTGREEN_EX,
                    )
            bowler.ball_history.append(4)
            batting_team.ball_history.append(4)

            # check if first 4 of the innings
            if batting_team.fours == 0:
                PrintInColor(
                    Randomize(commentary.commentary_first_four_team), Fore.LIGHTGREEN_EX
                )
            batting_team.fours += 1

            field = Randomize(resources.fields[4])
            comment = Randomize(commentary.commentary_four)
            PrintInColor(field + " FOUR! " + comment, Fore.LIGHTGREEN_EX)
            logger.info("FOUR")
            # check if first ball hit for a boundary
            if on_strike.balls == 0:
                PrintInColor(
                    Randomize(commentary.commentary_firstball_four), Fore.LIGHTGREEN_EX
                )
            # hattrick 4s
            arr = [x for x in bowler.ball_history if x != "WD"]
            if CheckForConsecutiveElements(arr, 4, 3):
                PrintInColor(
                    Randomize(commentary.commentary_in_a_row), Fore.LIGHTGREEN_EX
                )
            # inc numbers of 4s
            on_strike.fours += 1

        # six
        elif run == 6:
            # check if this is after a wicket?
            if batting_team.ball_history != []:
                if "Wkt" in str(batting_team.ball_history[-1]) or "RO" in str(
                    batting_team.ball_history[-1]
                ):
                    PrintInColor(
                        Randomize(commentary.commentary_boundary_after_wkt),
                        Fore.LIGHTGREEN_EX,
                    )
            bowler.ball_history.append(6)
            batting_team.ball_history.append(6)

            # check if first six
            if batting_team.sixes == 0:
                PrintInColor(
                    Randomize(commentary.commentary_first_six_team), Fore.LIGHTGREEN_EX
                )
            batting_team.sixes += 1

            # check uf first ball is hit
            if on_strike.balls == 0:
                PrintInColor(
                    Randomize(commentary.commentary_firstball_six), Fore.LIGHTGREEN_EX
                )
            # hattrick sixes
            arr = [x for x in bowler.ball_history if x != "WD"]
            if CheckForConsecutiveElements(arr, 6, 3):
                PrintInColor(
                    Randomize(commentary.commentary_in_a_row), Fore.LIGHTGREEN_EX
                )
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
                    comment = Randomize(commentary.commentary_dot_ball_pacer) % (
                        GetSurname(bowler.name),
                        on_strike.name,
                    )
                else:
                    comment = Randomize(commentary.commentary_dot_ball) % (
                        GetSurname(bowler.name),
                        GetSurname(on_strike.name),
                    )
            else:
                comment = "Decision overturned!"
            PrintInColor("%s, No Run" % comment, Style.BRIGHT)

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
                fielder = Randomize(
                    [
                        player
                        for player in bowling_team.team_array
                        if player is not bowler
                    ]
                )

                # if dropped catch
                if catch_drop is True:
                    dropped_by_keeper_prob = [0.1, 0.9]
                    dropped_by_keeper = choice(
                        [True, False], 1, p=dropped_by_keeper_prob, replace=False
                    )[0]
                    if dropped_by_keeper is True:
                        comment = (
                            Randomize(commentary.commentary_dropped_keeper)
                            % bowling_team.keeper.name
                        )
                    else:
                        comment = (
                            Randomize(commentary.commentary_dropped) % fielder.name
                        )

                PrintInColor("%s,%s run" % (comment, str(run)), Style.BRIGHT)
            else:
                if run == 2:
                    on_strike.doubles += 1
                elif run == 3:
                    on_strike.threes += 1
                PrintInColor("%s,%s %s runs" % (comment, field, str(run)), Style.BRIGHT)

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
        self.CheckMilestone()
        return

    def UpdateDismissal(self, dismissal):
        """
        Update the dismissal of a batsman.

        Args:
            dismissal: The dismissal string.

        Returns:
            None
        """
        batting_team, bowling_team = self.batting_team, self.bowling_team
        pair = batting_team.current_pair
        bowler = bowling_team.current_bowler

        if "runout" in dismissal:
            bowler.ball_history.append("RO")
            batting_team.ball_history.append("RO")
        else:
            # add this to bowlers history
            bowler.ball_history.append("Wkt")
            batting_team.ball_history.append("Wkt")
            bowler.wkts += 1
            # check if he had batted well in the first innings
            if bowler.runs > 50:
                PrintInColor(
                    Randomize(commentary.commentary_all_round_bowler) % bowler.name,
                    bowling_team.color,
                )

        # update wkts, balls, etc
        bowler.balls_bowled += 1
        batting_team.wickets_fell += 1
        batting_team.total_balls += 1
        pair = BatsmanOut(pair, dismissal)
        player_dismissed = next((x for x in pair if not x.status), None)
        player_onstrike = next((x for x in pair if x.status), None)

        # add player dismissed to the list of wickets for the bowler
        bowler.wickets_taken.append(player_dismissed)

        PrintInColor("Thats OUT !", Fore.RED)
        print(
            "%s %s %s (%s) SR: %s"
            % (
                GetShortName(player_dismissed.name),
                player_dismissed.dismissal,
                str(player_dismissed.runs),
                str(player_dismissed.balls),
                str(player_dismissed.strikerate),
            ),
        )

        # show 4s, 6s
        print(
            "4s:%s, 6s:%s, 1s:%s, 2s:%s 3s:%s"
            % (
                str(player_dismissed.fours),
                str(player_dismissed.sixes),
                str(player_dismissed.singles),
                str(player_dismissed.doubles),
                str(player_dismissed.threes),
            ),
        )

        # check if player dismissed is captain
        if player_dismissed.attr.iscaptain:
            PrintInColor(
                Randomize(commentary.commentary_captain_out), bowling_team.color
            )

        # detect a hat-trick!
        arr = [x for x in bowler.ball_history if x != "WD" or x != "NB"]
        # isOnAHattrick = CheckForConsecutiveElements(arr, 'Wkt', 2)
        isHattrick = CheckForConsecutiveElements(arr, "Wkt", 3)

        # if isOnAHattrick:
        #    PrintInColor(Randomize(commentary.commentary_on_a_hattrick), bowling_team.color)

        if isHattrick:
            bowler.hattricks += 1
            PrintInColor(Randomize(commentary.commentary_hattrick), bowling_team.color)
            input("press enter to continue..")
        if bowler.wkts == 3:
            PrintInColor("Third wkt for %s !" % bowler.name, bowling_team.color)
            input("press enter to continue..")
        # check if bowler got 5 wkts
        if bowler.wkts == 5:
            PrintInColor("That's 5 Wickets for %s !" % bowler.name, bowling_team.color)
            PrintInColor(Randomize(commentary.commentary_fifer), bowling_team.color)
            input("press enter to continue..")
        # update fall of wicket
        fow_info = Fow(
            wkt=batting_team.wickets_fell,
            runs=batting_team.total_score,
            total_balls=batting_team.total_balls,
            player_onstrike=player_onstrike,
            player_dismissed=player_dismissed,
        )
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
            partnership_runs = (
                batting_team.fow[batting_team.wickets_fell - 1].runs
                - batting_team.fow[batting_team.wickets_fell - 2].runs
            )
        partnership = Partnership(
            batsman_dismissed=fow_info.player_dismissed,
            batsman_onstrike=fow_info.player_onstrike,
            runs=partnership_runs,
        )
        # update batting team partnership details
        batting_team.partnerships.append(partnership)
        # if partnership is great
        if partnership.runs > 50:
            PrintInColor(
                Randomize(commentary.commentary_partnership_milestone)
                % (GetSurname(pair[0].name), GetSurname(pair[1].name)),
                Style.BRIGHT,
            )

        self.PrintCommentaryDismissal(dismissal)
        # show score
        self.CurrentMatchStatus()
        # get next batsman
        self.GetNextBatsman()
        input("press enter to continue")
        self.DisplayScore()
        self.DisplayProjectedScore()
        return

    def DisplayScore(self):
        """
        Display the batting summary scoreboard.

        Returns:
            None
        """
        batting_team = self.batting_team
        logger = self.logger
        ch = "-"
        print(ch * 45)
        logger.info(ch * 45)

        msg = ch * 15 + "Batting Summary" + ch * 15
        print(msg)
        logger.info(msg)
        print(ch * 45)
        logger.info(ch * 45)

        # this should be a nested list of 3 elements
        data_to_print = []
        for p in batting_team.team_array:
            name = p.name
            name = name.upper()
            if p.attr.iscaptain:
                name += "(c)"
            if p.attr.iskeeper:
                name += "(wk)"
            if p.status is True:  # * if not out
                if not p.onfield:
                    data_to_print.append([name, "DNB", ""])
                else:
                    data_to_print.append(
                        [name, "not out", "%s* (%s)" % (str(p.runs), str(p.balls))]
                    )
            else:
                data_to_print.append(
                    [name, p.dismissal, "%s (%s)" % (str(p.runs), str(p.balls))]
                )

        PrintListFormatted(data_to_print, 0.01, logger)

        msg = "Extras: %s" % str(batting_team.extras)
        print(msg)
        logger.info(msg)
        print(" ")
        logger.info(" ")

        msg = "%s %s/%s from (%s overs)" % (
            batting_team.name.upper(),
            str(batting_team.total_score),
            str(batting_team.wickets_fell),
            str(BallsToOvers(batting_team.total_balls)),
        )
        print(msg)
        logger.info(msg)

        # show RR
        crr = batting_team.GetCurrentRate()
        msg = "RunRate: %s" % (str(crr))
        print(msg)
        logger.info(msg)
        print(" ")
        logger.info(" ")

        # show FOW
        if batting_team.wickets_fell != 0:
            print("FOW:")
            logger.info("FOW:")
            # get fow_array
            fow_array = []
            for f in batting_team.fow:
                fow_array.append(
                    "%s/%s %s(%s)"
                    % (
                        str(f.runs),
                        str(f.wkt),
                        GetShortName(f.player_dismissed.name),
                        str(BallsToOvers(f.total_balls)),
                    )
                )
            fow_str = ", ".join(fow_array)
            print(fow_str)
            logger.info(fow_str)

        # partnerships
        msg = "Partnerships:"
        print(msg)
        logger.info(msg)
        for p in batting_team.partnerships:
            msg = "%s - %s :\t%s" % (
                p.batsman_onstrike.name,
                p.batsman_dismissed.name,
                str(p.runs),
            )
            if p.batsman_dismissed.status and p.batsman_onstrike.status:
                msg += "*"
            print(msg)
            logger.info(msg)

        print(ch * 45)
        logger.info(ch * 45)
        return

    def GenerateRun(self, over, player_on_strike):
        """
        Generate the number of runs scored on a ball.

        Args:
            over: The current over number.
            player_on_strike: The player on strike.

        Returns:
            int: The number of runs scored.
        """
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
            if (
                batting_team.total_balls > 0
                and batting_team.GetRequiredRate() - batting_team.GetCurrentRate()
                >= 2.0
                and over <= overs - 2
            ):
                prob = prob_death

            # if need 1 to win, don't take 2 or 3,
            if batting_team.target - batting_team.total_score == 1:
                prob = [
                    1 / 7,
                    1 / 7,
                    1 / 7,
                    0,
                    0,
                    2 / 7,
                    1 / 7,
                    1 / 7,
                ]
            # if 2 to win, don't take 3
            if (batting_team.target - batting_team.total_score) == 2:
                prob = [
                    1 / 7,
                    1 / 7,
                    1 / 7,
                    1 / 7,
                    0,
                    1 / 7,
                    1 / 7,
                    1 / 7,
                ]

        # FIXME:
        # if initial overs, play carefully based on RR
        # if death overs, try to go big
        # but, if batsman is poor and bowler is skilled, more chances of getting out
        if bowler.attr.bowling - player_on_strike.attr.batting >= 4:
            prob = [0.25, 0.20, 0.20, 0.15, 0.05, 0.05, 0.05, 0.05]

        # select from final run_array with the given probability distribution
        run = choice(run_array, 1, p=prob, replace=False)[0]
        return run

    def DetectDeathOvers(self, over):
        """
        Detect if the current over is a death over.

        Args:
            over: The current over number.

        Returns:
            None
        """
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
                    PrintInColor(
                        "To win: %s from %s"
                        % (str(towin), str(overs * 6 - batting_team.total_balls)),
                        Style.BRIGHT,
                    )
        return

    def MatchAbandon(self):
        """
        Abandon the match due to rain.

        Returns:
            None
        """
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
            result_str = result_str % (
                batting_team.name,
                str(abs(simulated_score - batting_team.target)),
            )
        else:
            result_str = result_str % (
                bowling_team.name,
                str(abs(batting_team.target - simulated_score)),
            )
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
        """
        Check the Decision Review System (DRS) for a dismissal.

        Returns:
            bool: True if the decision is overturned, False otherwise.
        """
        result = False
        team = self.batting_team
        pair = team.current_pair

        if team.drs_chances <= 0:
            PrintInColor(
                Randomize(commentary.commentary_lbw_nomore_drs), Fore.LIGHTRED_EX
            )
            return result
        # check if all 4 decisions are taken
        elif team.drs_chances > 0:
            opt = ChooseFromOptions(
                ["y", "n"], "DRS? %s chance(s) left" % (str(team.drs_chances)), 200000
            )
            if opt == "n":
                PrintInColor(
                    Randomize(commentary.commentary_lbw_drs_not_taken), Fore.LIGHTRED_EX
                )
                return result
            else:
                PrintInColor(
                    Randomize(commentary.commentary_lbw_drs_taken)
                    % (GetSurname(pair[0].name), GetSurname(pair[1].name)),
                    Fore.LIGHTGREEN_EX,
                )
                PrintInColor("Decision pending...", Style.BRIGHT)
                time.sleep(5)
                result = random.choice([True, False])
                impact_outside_bat_involved = random.choice([True, False])
                # if not out
                if result:
                    # if edged or pitching outside
                    if impact_outside_bat_involved:
                        PrintInColor(
                            Randomize(commentary.commentary_lbw_edged_outside),
                            Fore.LIGHTGREEN_EX,
                        )
                    else:
                        team.drs_chances -= 1
                    PrintInColor(
                        Randomize(commentary.commentary_lbw_overturned),
                        Fore.LIGHTGREEN_EX,
                    )

                # if out!
                else:
                    PrintInColor(
                        Randomize(commentary.commentary_lbw_decision_stays)
                        % self.umpire,
                        Fore.LIGHTRED_EX,
                    )
                    team.drs_chances -= 1
        return result

    def PrintCommentaryDismissal(self, dismissal):
        """
        Print the commentary for a dismissal.

        Args:
            dismissal: The dismissal string.

        Returns:
            None
        """
        # commentary
        comment = " "
        pair = self.batting_team.current_pair
        bowler = self.bowling_team.current_bowler

        batting_team, bowling_team = self.batting_team, self.bowling_team
        player_dismissed = next((x for x in pair if not x.status), None)
        player_onstrike = next((x for x in pair if x.status), None)
        keeper = bowling_team.keeper

        if "runout" in dismissal:
            comment = Randomize(commentary.commentary_runout) % (
                GetSurname(player_dismissed.name),
                GetSurname(player_onstrike.name),
            )
        elif "st " in dismissal:
            comment = Randomize(commentary.commentary_stumped) % GetSurname(keeper.name)
        # if bowler is the catcher
        elif "c&b" in dismissal:
            comment = Randomize(commentary.commentary_return_catch) % GetSurname(
                bowler.name
            )
        elif "c " in dismissal and " b " in dismissal:
            # see if the catcher is the keeper
            if GetShortName(keeper.name) in dismissal:
                comment = Randomize(commentary.commentary_keeper_catch) % GetSurname(
                    keeper.name
                )
            else:
                fielder = dismissal.split(" b ")[0].strip("c ")
                comment = Randomize(commentary.commentary_caught) % fielder
        elif "b " or "lbw" in dismissal:
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
            if "lbw" in dismissal:
                comment = Randomize(commentary.commentary_lbw) % GetSurname(
                    player_dismissed.name
                )
            else:
                comment = Randomize(commentary.commentary_bowled)

        # comment dismissal
        PrintInColor(comment, Style.BRIGHT)
        # if he missed a fifty or century
        if 90 <= player_dismissed.runs < 100:
            PrintInColor(
                Randomize(commentary.commentary_nineties)
                % GetSurname(player_dismissed.name),
                Style.BRIGHT,
            )
        # if lost fifty
        if 40 <= player_dismissed.runs < 50:
            PrintInColor(
                Randomize(commentary.commentary_forties)
                % GetSurname(player_dismissed.name),
                Style.BRIGHT,
            )
        # if its a great knock, say this
        if player_dismissed.runs > 50:
            PrintInColor(
                Randomize(commentary.commentary_out_fifty)
                % GetSurname(player_dismissed.name),
                Style.BRIGHT,
            )
        # if duck
        if player_dismissed.runs == 0:
            PrintInColor(Randomize(commentary.commentary_out_duck), Style.BRIGHT)
        # out first ball
        if player_dismissed.balls == 1:
            PrintInColor(
                Randomize(commentary.commentary_out_first_ball)
                % GetSurname(player_dismissed.name),
                Style.BRIGHT,
            )

        # calculate the situation
        if batting_team.batting_second and (7 <= batting_team.wickets_fell < 10):
            PrintInColor(
                Randomize(commentary.commentary_goingtolose) % batting_team.name,
                Style.BRIGHT,
            )

        # last man
        if batting_team.wickets_fell == 9:
            PrintInColor(Randomize(commentary.commentary_lastman), batting_team.color)
        return

    def AssignBowler(self):
        """
        Assign a bowler for the current over.

        Returns:
            Bowler: The assigned bowler.
        """
        bowler = None
        bowling_team = self.bowling_team
        bowlers = bowling_team.bowlers
        # if first over, opening bowler does it
        if bowling_team.last_bowler is None:
            bowler = next((x for x in bowlers if x.attr.isopeningbowler), None)
        else:
            if bowling_team.last_bowler in bowlers:
                # bowling list except the bowler who did last over and bowlers who finished their allotted overs
                temp = [
                    x
                    for x in bowlers
                    if (
                        x != bowling_team.last_bowler
                        and x.balls_bowled < x.max_overs * 6
                    )
                ]
                # sort this based on skill
                temp = sorted(temp, key=lambda x: x.attr.bowling, reverse=True)
                # if autoplay, let bowlers be chosen randomly
                if self.autoplay:
                    bowler = Randomize(temp)
                # else pick bowler
                else:
                    next_bowler = input(
                        "Pick next bowler: {0} [Press Enter to auto-select]".format(
                            " / ".join(
                                [str(x.no) + "." + GetShortName(x.name) for x in temp]
                            )
                        )
                    )
                    bowler = next(
                        (
                            x
                            for x in temp
                            if (
                                str(next_bowler) == str(x.no)
                                or next_bowler.lower() in GetShortName(x.name).lower()
                            )
                        ),
                        None,
                    )
                    if bowler is None:
                        bowler = Randomize(temp)

        if bowler is None:
            Error_Exit("No bowler assigned!")

        return bowler

    def GetNextBatsman(self):
        """
        Get the next batsman to come to the crease.

        Returns:
            list: The updated pair of batsmen.
        """
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
                PrintInColor(
                    Randomize(commentary.commentary_captain_to_bat_next),
                    batting_team.color,
                )

            # check if he had a good day with the ball earlier
            if pair[ind].balls_bowled > 0:
                if pair[ind].wkts >= 2:
                    PrintInColor(
                        Randomize(commentary.commentary_good_bowler_to_bat),
                        batting_team.color,
                    )
                if pair[ind].wkts == 0 and pair[ind].eco >= 7.0:
                    PrintInColor(
                        Randomize(commentary.commentary_bad_bowler_to_bat),
                        batting_team.color,
                    )

            # now new batter on field
            pair[ind].onfield = True

        batting_team.current_pair = pair
        return pair

    def AssignBatsman(self, pair):
        """
        Assign the next batsman to come to the crease.

        Args:
            pair: The current pair of batsmen.

        Returns:
            Batsman: The assigned batsman.
        """
        batting_team = self.batting_team
        remaining_batsmen = [
            plr for plr in batting_team.team_array if (plr.status and plr not in pair)
        ]

        next_batsman = input(
            "Choose next batsman: {0} [Press Enter to auto-select]".format(
                " / ".join(
                    [str(x.no) + "." + GetShortName(x.name) for x in remaining_batsmen]
                )
            )
        )
        batsman = next(
            (
                x
                for x in remaining_batsmen
                if (
                    str(next_batsman) == str(x.no)
                    or next_batsman.lower() in GetShortName(x.name).lower()
                )
            ),
            None,
        )

        if batsman is None:
            Error_Exit("No batsman assigned!")
        return batsman

    def CalculateResult(self):
        """
        Calculate the result of the match.

        Returns:
            None
        """
        team1 = self.team1
        team2 = self.team2

        result = Result(team1=team1, team2=team2)
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
            char_wkts = "wicket"
            char_balls = "ball"
            char_runs = "run"
            win_balls_left = 0
            # if batting first, simply get diff between total runs
            # else get how many wkts remaining
            if result.winner.batting_second:
                win_margin = 10 - result.winner.wickets_fell
                if win_margin != 0:
                    if win_margin > 1:
                        char_wkts += "s"
                    win_balls_left = self.overs * 6 - result.winner.total_balls
                    if win_balls_left > 1:
                        char_balls += "s"
                    result.result_str += " by %s %s with %s %s left" % (
                        str(win_margin),
                        char_wkts,
                        str(win_balls_left),
                        char_balls,
                    )
            elif not result.winner.batting_second:
                win_margin = abs(result.winner.total_score - loser.total_score)
                if win_margin != 0:
                    if win_margin > 1:
                        char_runs += "s"
                    result.result_str += " by %s %s" % (str(win_margin), char_runs)

        self.result = result

    def FindBestPlayers(self):
        """
        Find the best players in the match.

        Returns:
            Result: The result object with the best players.
        """
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

    def FindPlayerOfTheMatch(self):
        """
        Find the player of the match.

        Returns:
            None
        """
        # find which team won
        # if tied
        if self.team1.total_score == self.team2.total_score:
            self.winner = Randomize([self.team1, self.team2])
            self.loser = self.winner
        # if any team won
        else:
            self.winner, self.loser = max(
                [self.team1, self.team2], key=attrgetter("total_score")
            ), min([self.team1, self.team2], key=attrgetter("total_score"))

        # find best batsman, bowler from winning team
        # always two batsmen will play
        best_batsmen = sorted(
            self.winner.team_array, key=attrgetter("runs"), reverse=True
        )
        best_bowlers = sorted(self.winner.bowlers, key=attrgetter("wkts"), reverse=True)

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
                best_batsman = sorted(
                    best_batsmen, key=attrgetter("strikerate"), reverse=True
                )[0]
            # if there is one not out among them
            else:
                best_batsmen = [plr for plr in best_batsmen if plr.status]
                # if both are not out, select randomly
                if len(best_batsmen) == 2:
                    best_batsman = sorted(
                        best_batsmen, key=attrgetter("strikerate"), reverse=True
                    )[0]
                elif len(best_batsmen) == 1:
                    best_batsman = best_batsmen[0]

        else:
            best_batsman = best_batsmen[0]

        # if same wkts, get best economy bowler
        if best_bowlers[0].wkts == best_bowlers[1].wkts:
            best_bowler = sorted(best_bowlers, key=attrgetter("eco"), reverse=False)[0]
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
        msg = "Player of the match: %s (%s)" % (
            best_player.name,
            best_player.GetMomStat(),
        )
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)

    def Toss(self):
        """
        Perform the toss to decide which team bats first.

        Returns:
            None
        """
        logger = self.logger
        PrintInColor("Toss..", Style.BRIGHT)
        PrintInColor(
            "We have the captains %s from %s and %s from %s in the middle"
            % (
                self.team1.captain.name,
                self.team1.name,
                self.team2.captain.name,
                self.team2.name,
            ),
            Style.BRIGHT,
        )

        PrintInColor(
            "%s is gonna flip the coin" % self.team2.captain.name, Style.BRIGHT
        )
        # FIXME: use the ChooseFromOptions function here
        opts = [1, 2]
        msg = "%s your call, Heads or tails?" % (self.team1.captain.name)
        PrintInColor(msg, self.team1.color)
        call = input("1.Heads 2.Tails\n")
        # if invalid, auto-select
        if call == "" or None:
            call = int(Randomize(opts))
            print("Invalid choice, auto-selected")
        coin = int(Randomize(opts))

        # check if call == coin selected
        if coin == call:
            msg = (
                "%s, you have won the toss, do you wanna bat or bowl first?"
                % self.team1.captain.name
            )
            PrintInColor(msg, Style.BRIGHT)
            call = input("1.Bat 2.Bowl")
            # if invalid, auto-select
            if call == "" or None:
                call = int(Randomize(opts))
                print("Invalid choice, auto-selected")
            if int(call) == 1:
                msg = "%s has elected to bat first" % self.team1.captain.name
                PrintInColor(msg, self.team1.color)
                self.team1.batting_second = False
                self.team2.batting_second = True
                logger.info(msg)
            else:
                msg = "%s has elected to bowl first" % self.team1.captain.name
                PrintInColor(msg, self.team1.color)
                self.team2.batting_second = False
                self.team1.batting_second = True
                logger.info(msg)
        else:
            msg = (
                "%s, you have won the toss, do you wanna bat or bowl first?"
                % self.team2.captain.name
            )
            call = input("1.Bat 2.Bowl first")
            # if invalid, auto-select
            if call == "" or None:
                call = int(Randomize(opts))
                print("Invalid choice, auto-selected")
            if int(call) == 1:
                msg = "%s has elected to bat first" % self.team2.captain.name
                PrintInColor(msg, self.team2.color)
                self.team2.batting_second = False
                self.team1.batting_second = True
                logger.info(msg)
            else:
                msg = "%s has elected to bowl first" % self.team2.captain.name
                PrintInColor(msg, self.team2.color)
                self.team1.batting_second = False
                self.team2.batting_second = True
                logger.info(msg)

        # now find out who is batting first
        batting_first = next(
            (x for x in [self.team1, self.team2] if not x.batting_second), None
        )
        batting_second = next(
            (x for x in [self.team1, self.team2] if x.batting_second), None
        )
        self.batting_first = batting_first
        self.batting_second = batting_second

        # do you need DRS?
        drs_opted = ChooseFromOptions(["y", "n"], "Do you need DRS for this match? ", 5)
        if drs_opted == "y":
            PrintInColor("D.R.S opted", Style.BRIGHT)
            self.drs = True
            input("press enter to continue")

        self.status = True
        return

    def ValidateMatchTeams(self):
        """
        Validate the teams for the match.

        Returns:
            None
        """
        if self.team1 is None or self.team2 is None:
            Error_Exit("No teams found!")

        for t in [self.team1, self.team2]:
            # check if 11 players
            if len(t.team_array) != 11:
                Error_Exit("Only %s members in team %s" % (len(t.team_array), t.name))

            # check if keeper exists
            if t.keeper is None:
                Error_Exit("No keeper found in team %s" % t.name)

            # check if more than one keeper or captain
            if len([plr for plr in t.team_array if plr.attr.iskeeper]) > 1:
                Error_Exit("More than one keeper found")
            if len([plr for plr in t.team_array if plr.attr.iscaptain]) > 1:
                Error_Exit("More than one captain found")

            # check for captain
            if t.captain is None:
                Error_Exit("No captain found in team %s" % t.name)

            # get bowlers who has bowling attribute
            bowlers = [plr for plr in t.team_array if plr.attr.bowling > 0]
            if len(bowlers) < 6:
                Error_Exit("Team %s should have 6 bowlers in the playing XI" % t.name)
            else:
                t.bowlers = bowlers
                # assign max overs for bowlers
                for bowler in t.bowlers:
                    bowler.max_overs = self.bowler_max_overs

        # ensure no common members in the teams
        common_players = list(
            set(self.team1.team_array).intersection(self.team2.team_array)
        )
        if common_players:
            Error_Exit(
                "Common players in teams found! : %s"
                % (",".join([p.name for p in common_players]))
            )

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
                    player.no = np.random.choice(
                        list(range(100)), size=1, replace=False
                    )[0]
        print("Validated teams")
        return

    def GetBallHistory(self):
        """
        Get the ball history so far.

        Returns:
            None
        """
        batting_team = self.batting_team
        # check extras
        # FIXME: this isnt used?
        noballs = batting_team.ball_history.count("NB")
        wides = batting_team.ball_history.count("WD")
        runouts = batting_team.ball_history.count("RO")
        sixes = batting_team.ball_history.count(6)
        fours = batting_team.ball_history.count(4)
        return

    def UpdateExtras(self):
        """
        Update the extras for the current over.

        Returns:
            None
        """
        batting_team, bowling_team = self.batting_team, self.bowling_team
        bowler = bowling_team.current_bowler

        logger = self.logger
        bowler.runs_given += 1
        batting_team.extras += 1
        batting_team.total_score += 1
        # generate wide or no ball
        extra = random.choice(["wd", "nb"])
        if extra == "wd":
            # add this to bowlers history
            bowler.ball_history.append("WD")
            batting_team.ball_history.append("WD")
            PrintInColor("WIDE...!", Fore.LIGHTCYAN_EX)
            PrintInColor(
                Randomize(commentary.commentary_wide) % self.umpire, Style.BRIGHT
            )
            logger.info("WIDE")
        elif extra == "nb":
            # no balls
            bowler.ball_history.append("NB")
            batting_team.ball_history.append("NB")
            PrintInColor("NO BALL...!", Fore.LIGHTCYAN_EX)
            PrintInColor(Randomize(commentary.commentary_no_ball), Style.BRIGHT)
            logger.info("NO BALL")

        return

    def GetBowlerComments(self):
        """
        Get comments about the current bowler.

        Returns:
            None
        """
        bowler = self.bowling_team.current_bowler
        # check if bowler is captain
        if bowler.attr.iscaptain:
            PrintInColor(Randomize(commentary.commentary_captain_to_bowl), Style.BRIGHT)
        # check if spinner or seamer
        if bowler.attr.isspinner:
            PrintInColor(
                Randomize(commentary.commentary_spinner_into_attack), Style.BRIGHT
            )
        elif bowler.attr.ispacer:
            PrintInColor(
                Randomize(commentary.commentary_pacer_into_attack), Style.BRIGHT
            )
        else:
            PrintInColor(
                Randomize(commentary.commentary_medium_into_attack), Style.BRIGHT
            )
        # check if it is his last over!
        if (BallsToOvers(bowler.balls_bowled) == self.bowler_max_overs - 1) and (
            bowler.balls_bowled != 0
        ):
            PrintInColor(
                Randomize(commentary.commentary_bowler_last_over), Style.BRIGHT
            )
            if bowler.wkts >= 3 or bowler.eco <= 5.0:
                PrintInColor(
                    Randomize(commentary.commentary_bowler_good_spell), Style.BRIGHT
                )
            elif bowler.eco >= 7.0:
                PrintInColor(
                    Randomize(commentary.commentary_bowler_bad_spell), Style.BRIGHT
                )
        return

    def CheckMilestone(self):
        """
        Check for milestones achieved by the batsmen.

        Returns:
            None
        """
        logger = self.logger
        batting_team = self.batting_team
        pair = batting_team.current_pair

        # call_by_first_name = Randomize([True, False])

        for p in pair:
            name = GetFirstName(p.name)
            if not Randomize([True, False]):
                name = GetSurname(p.name)
            # if nickname defined, call by it
            if p.nickname != "" or None:
                name = p.nickname

            # first fifty
            if p.runs >= 50 and p.fifty == 0:
                p.fifty += 1
                msg = "50 for %s!" % name
                PrintInColor(msg, batting_team.color)
                logger.info(msg)
                PrintInColor(
                    "%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT
                )
                # check if captain
                if p.attr.iscaptain:
                    PrintInColor(
                        Randomize(commentary.commentary_captain_leading),
                        batting_team.color,
                    )

                # call by first name or last name
                PrintInColor(
                    Randomize(commentary.commentary_milestone) % name,
                    batting_team.color,
                )

                #  check if he had a good day with the ball as well
                if p.wkts >= 2:
                    PrintInColor(
                        Randomize(commentary.commentary_all_round_batsman),
                        batting_team.color,
                    )

            elif p.runs >= 100 and (p.fifty == 1 and p.hundred == 0):
                # after first fifty is done
                p.hundred += 1
                p.fifty += 1
                msg = "100 for %s!" % name
                PrintInColor(msg, batting_team.color)
                logger.info(msg)
                PrintInColor(
                    "%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT
                )
                # check if captain
                if p.attr.iscaptain:
                    PrintInColor(
                        Randomize(commentary.commentary_captain_leading),
                        batting_team.color,
                    )
                PrintInColor(
                    Randomize(commentary.commentary_milestone) % p.name,
                    batting_team.color,
                )

            elif p.runs >= 200 and (p.hundred == 1):
                # after first fifty is done
                p.hundred += 1
                msg = "200 for %s! What a superman!" % name
                PrintInColor(msg, batting_team.color)
                logger.info(msg)
                PrintInColor(
                    "%s fours and %s sixes" % (str(p.fours), str(p.sixes)), Style.BRIGHT
                )
                # check if captain
                if p.attr.iscaptain:
                    PrintInColor(
                        Randomize(commentary.commentary_captain_leading),
                        batting_team.color,
                    )
                PrintInColor(
                    Randomize(commentary.commentary_milestone) % name,
                    batting_team.color,
                )

        input("press enter to continue..")
        return

    def UpdateLastPartnership(self):
        """
        Update the last partnership details.

        Returns:
            None
        """
        batting_team = self.batting_team
        pair = batting_team.current_pair

        # update last partnership
        if batting_team.wickets_fell > 0:
            last_fow = batting_team.fow[-1].runs
            last_partnership_runs = batting_team.total_score - last_fow
            last_partnership = Partnership(
                batsman_dismissed=pair[0],
                batsman_onstrike=pair[1],
                runs=last_partnership_runs,
            )
            # not all out
            if batting_team.wickets_fell < 10:
                last_partnership.both_notout = True

            batting_team.partnerships.append(last_partnership)
        # if no wkt fell
        elif batting_team.wickets_fell == 0:
            last_partnership_runs = batting_team.total_score
            last_partnership = Partnership(
                batsman_dismissed=pair[0],
                batsman_onstrike=pair[1],
                both_notout=True,
                runs=last_partnership_runs,
            )
            batting_team.partnerships.append(last_partnership)

    def GenerateDismissal(self):
        """
        Generate a random mode of dismissal.

        Returns:
            str: The dismissal string.
        """
        bowling_team = self.bowling_team
        bowler = bowling_team.current_bowler
        keeper = bowling_team.keeper

        dismissal_str = None
        # now get a list of fielders
        fielder = Randomize(bowling_team.team_array)
        # list of mode of dismissals
        if bowler.attr.isspinner:
            dismissal_types = ["c", "st", "runout", "lbw", "b"]
            dismissal_prob = [0.38, 0.2, 0.02, 0.2, 0.2]
        else:
            dismissal_types = ["c", "runout", "lbw", "b"]
            dismissal_prob = [0.45, 0.05, 0.25, 0.25]

        # generate dismissal
        dismissal = choice(dismissal_types, 1, p=dismissal_prob, replace=False)[0]

        # generate dismissal string
        if dismissal == "lbw" or dismissal == "b":
            dismissal_str = "%s %s" % (dismissal, GetShortName(bowler.name))
        elif dismissal == "st":
            # stumped
            dismissal_str = "st +%s b %s" % (
                GetShortName(keeper.name),
                GetShortName(bowler.name),
            )
            keeper.stumpings += 1

        elif dismissal == "c":
            fielder.catches += 1
            # check if catcher is the bowler
            if fielder == bowler:
                dismissal_str = "c&b %s" % (GetShortName(bowler.name))
            else:
                if fielder.attr.iskeeper:
                    dismissal_str = "%s +%s b %s" % (
                        dismissal,
                        GetShortName(fielder.name),
                        GetShortName(bowler.name),
                    )
                else:
                    dismissal_str = "%s %s b %s" % (
                        dismissal,
                        GetShortName(fielder.name),
                        GetShortName(bowler.name),
                    )
        elif dismissal == "runout":
            fielder.runouts += 1
            dismissal_str = "runout %s" % (GetShortName(fielder.name))

        # check if fielder is on fire!
        if fielder.runouts >= 2 or fielder.catches >= 2:
            PrintInColor(
                Randomize(commentary.commentary_fielder_on_fire) % fielder.name,
                bowling_team.color,
            )
        if keeper.stumpings >= 2:
            PrintInColor(
                Randomize(commentary.commentary_fielder_on_fire) % keeper.name,
                bowling_team.color,
            )

        return dismissal_str

    def ShowHighlights(self):
        """
        Show the highlights of the match.

        Returns:
            None
        """
        logger = self.logger
        batting_team, bowling_team = self.batting_team, self.bowling_team
        crr = batting_team.GetCurrentRate()
        rr = batting_team.GetRequiredRate()

        # if match ended, do nothing, just return
        if not self.status:
            return

        # default msg
        msg = "\n%s %s / %s (%s Overs)" % (
            batting_team.name,
            str(batting_team.total_score),
            str(batting_team.wickets_fell),
            str(BallsToOvers(batting_team.total_balls)),
        )
        msg += " Current RR: %s" % str(crr)
        if batting_team.batting_second and self.status:
            msg += " Required RR: %s\n" % str(rr)
        print(msg)
        logger.info(msg)
        return

    def CurrentMatchStatus(self):
        """
        Print the current match status.

        Returns:
            None
        """
        logger = self.logger
        batting_team, bowling_team = self.batting_team, self.bowling_team
        crr = batting_team.GetCurrentRate()
        rr = batting_team.GetRequiredRate()

        # if match ended, nothing, just return
        if not self.status:
            return

        # how much is the score
        if batting_team.total_score >= 50 and not batting_team.fifty_up:
            PrintInColor(
                Randomize(commentary.commentary_score_fifty) % batting_team.name,
                Style.BRIGHT,
            )
            batting_team.fifty_up = True

        if batting_team.total_score >= 100 and not batting_team.hundred_up:
            PrintInColor(
                Randomize(commentary.commentary_score_hundred) % batting_team.name,
                Style.BRIGHT,
            )
            batting_team.hundred_up = True

        if batting_team.total_score >= 200 and not batting_team.two_hundred_up:
            PrintInColor(
                Randomize(commentary.commentary_score_two_hundred) % batting_team.name,
                Style.BRIGHT,
            )
            batting_team.two_hundred_up = True

        if batting_team.total_score >= 300 and not batting_team.three_hundred_up:
            PrintInColor(
                Randomize(commentary.commentary_score_three_hundred)
                % batting_team.name,
                Style.BRIGHT,
            )
            batting_team.three_hundred_up = True

        # default msg
        msg = "\n%s %s / %s (%s Overs)" % (
            batting_team.name,
            str(batting_team.total_score),
            str(batting_team.wickets_fell),
            str(BallsToOvers(batting_team.total_balls)),
        )
        msg += " Current Rate: %s" % str(crr)
        if batting_team.batting_second:
            msg += " Required Rate: %s\n" % str(rr)

        print(msg)
        logger.info(msg)
        msg = "%s %s from %s overs now " % (
            batting_team.name,
            str(batting_team.total_score),
            str(BallsToOvers(batting_team.total_balls)),
        )
        if batting_team.wickets_fell == 0:
            msg += " with no wickets gone"
        elif batting_team.wickets_fell == 1:
            msg += "with first wicket gone"
        else:
            msg += " with the loss of %s wickets!" % (str(batting_team.wickets_fell))
        msg += " and at a run rate of %s" % (str(crr))
        PrintInColor(msg, batting_team.color)

        # wickets fell
        wkts_fell = batting_team.wickets_fell

        # who are not out and going good
        top_batsmen = sorted(
            [batsman for batsman in batting_team.team_array],
            key=lambda t: t.runs,
            reverse=True,
        )
        top_batsmen_notout = sorted(
            [batsman for batsman in batting_team.team_array if batsman.status],
            key=lambda t: t.runs,
            reverse=True,
        )
        # who can win the match for them
        savior = top_batsmen_notout[0]

        # who all bowled so far
        bowlers = [bowler for bowler in bowling_team.bowlers if bowler.balls_bowled > 0]
        # top wkt takers
        bowlers_most_wkts = sorted(bowlers, key=lambda t: t.wkts, reverse=True)[0]

        # check if first batting
        if not batting_team.batting_second:
            if crr <= 4.0:
                PrintInColor(
                    Randomize(commentary.commentary_situation_low_rr)
                    % batting_team.name,
                    Fore.GREEN,
                )

            elif crr >= 8.0:
                PrintInColor(
                    Randomize(commentary.commentary_situation_good_rr)
                    % batting_team.name,
                    Fore.GREEN,
                )
                PrintInColor(
                    Randomize(commentary.commentary_situation_major_contr_batting)
                    % top_batsmen[0].name,
                    Style.BRIGHT,
                )

            if wkts_fell == 0:
                PrintInColor(
                    Randomize(commentary.commentary_situation_no_wkts_fell)
                    % batting_team.name,
                    Fore.GREEN,
                )

            elif 1 < wkts_fell <= 6:
                PrintInColor(
                    Randomize(commentary.commentary_situation_unstable)
                    % batting_team.name,
                    Style.BRIGHT,
                )
                PrintInColor("Lost %s wickets so far!" % wkts_fell, Style.BRIGHT)
                PrintInColor(
                    Randomize(commentary.commentary_situation_major_contr_bowling)
                    % bowlers_most_wkts.name,
                    Style.BRIGHT,
                )

            elif 6 < wkts_fell < 10:
                PrintInColor(
                    Randomize(commentary.commentary_situation_trouble)
                    % batting_team.name,
                    Style.BRIGHT,
                )
                PrintInColor(
                    Randomize(commentary.commentary_situation_major_contr_bowling)
                    % bowlers_most_wkts.name,
                    Style.BRIGHT,
                )

        # if chasing
        else:
            # gettable
            if crr >= rr:
                PrintInColor(
                    Randomize(commentary.commentary_situation_reqd_rate_low)
                    % batting_team.name,
                    Fore.GREEN,
                )
                if 0 <= batting_team.wickets_fell <= 2:
                    PrintInColor(
                        Randomize(commentary.commentary_situation_reqd_rate_low)
                        % batting_team.name,
                        Fore.GREEN,
                    )
                if batting_team.wickets_fell <= 5:
                    PrintInColor(
                        Randomize(commentary.commentary_situation_shouldnt_lose_wks)
                        % batting_team.name,
                        Style.BRIGHT,
                    )
                elif 5 <= batting_team.wickets_fell < 7:
                    PrintInColor(
                        Randomize(commentary.commentary_situation_unstable)
                        % batting_team.name,
                        Style.BRIGHT,
                    )
                elif 7 < batting_team.wickets_fell < 10:
                    # say who can save the match
                    PrintInColor(
                        Randomize(commentary.commentary_situation_savior) % savior.name,
                        Fore.RED,
                    )

            # gone case!
            if rr - crr >= 1.0:
                PrintInColor(
                    Randomize(commentary.commentary_situation_reqd_rate_high)
                    % batting_team.name,
                    Style.BRIGHT,
                )
                if 0 <= batting_team.wickets_fell <= 2:
                    PrintInColor(
                        Randomize(commentary.commentary_situation_got_wkts_in_hand)
                        % batting_team.name,
                        Style.BRIGHT,
                    )
                if 7 <= batting_team.wickets_fell < 10:
                    PrintInColor(
                        Randomize(commentary.commentary_situation_gone_case)
                        % batting_team.name,
                        Fore.RED,
                    )
                    # say who can save the match
                    PrintInColor(
                        Randomize(commentary.commentary_situation_savior) % savior.name,
                        Fore.RED,
                    )

        return

    def DisplayProjectedScore(self):
        """
        Display the projected score based on the current run rate.

        Returns:
            None
        """
        if not self.status:
            return
        if BallsToOvers(self.batting_team.total_balls) == self.overs:
            return
        import numpy as np

        overs_left = BallsToOvers(self.overs * 6 - self.batting_team.total_balls)
        current_score = self.batting_team.total_score
        crr = self.batting_team.GetCurrentRate()
        proj_score = lambda x: np.ceil(current_score + (x * overs_left))
        print("Projected Score")
        # FIXME this has some wierd notation at times. round them off to 1/2
        print("Current Rate(%s): %s" % (str(crr), proj_score(crr)), end=" ")
        lim = crr + 3.0
        crr += 0.5
        while crr <= lim:
            print("%s: %s" % (str(crr), proj_score(crr)), end=" ")
            crr += 1.0
        print("\n")

    def DisplayBowlingStats(self):
        """
        Display the bowling statistics.

        Returns:
            None
        """
        logger = self.logger
        team = self.bowling_team
        bowlers = team.bowlers
        # here, remove the bowlers who did not bowl
        bowlers_updated = []
        char = "-"
        print(char * 45)
        logger.info(char * 45)

        msg = "%s-Bowling Stats-%s" % (char * 15, char * 15)
        print(msg)
        logger.info(msg)
        print(char * 45)
        logger.info(char * 45)
        # nested list of fixed size elements
        data_to_print = [["Bowler", "Ovrs", "Mdns", "Runs", "Wkts", "Eco"]]
        for bowler in bowlers:
            # do not print if he has not bowled
            if bowler.balls_bowled != 0:
                bowlers_updated.append(bowler)
                balls = bowler.balls_bowled
                overs = BallsToOvers(balls)
                eco = float(bowler.runs_given / overs)
                eco = round(eco, 2)
                bowler.eco = eco
                data_to_print.append(
                    [
                        bowler.name.upper(),
                        str(overs),
                        str(bowler.maidens),
                        str(bowler.runs_given),
                        str(bowler.wkts),
                        str(bowler.eco),
                    ]
                )

        PrintListFormatted(data_to_print, 0.01, logger)
        print(char * 45)
        logger.info(char * 45)
        input("press enter to continue..")
        return

    def DisplayPlayingXI(self):
        """
        Display the playing XI for both teams.

        Returns:
            None
        """
        t1, t2 = self.team1, self.team2
        # print the playing XI
        PrintInColor("Here are the playing elevens", Style.BRIGHT)
        data_to_print = [[t1.name, t2.name], [" ", " "]]
        for x in range(11):
            name1 = t1.team_array[x].name
            name2 = t2.team_array[x].name

            name1 = name1.upper()
            name2 = name2.upper()

            if t1.team_array[x] == t1.captain:
                name1 += "(c)"
            if t1.team_array[x] == t1.keeper:
                name1 += "(wk)"
            if t2.team_array[x] == t2.captain:
                name2 += "(c)"
            if t2.team_array[x] == t2.keeper:
                name2 += "(wk)"

            data_to_print.append([name1, name2])
        # now print it
        PrintListFormatted(data_to_print, 0.1, None)

    def MatchSummary(self):
        """
        Print the match summary.

        Returns:
            None
        """
        logger = self.logger
        ch = "-"
        result = self.result

        msg = "%s Match Summary %s" % (ch * 10, ch * 10)
        print(msg)
        logger.info(msg)

        msg = "%s vs %s, at %s" % (
            result.team1.name,
            result.team2.name,
            self.venue.name,
        )
        print(msg)
        logger.info(msg)

        msg = ch * 45
        print(ch * 45)
        logger.info(msg)

        msg = result.result_str
        PrintInColor(msg, Style.BRIGHT)
        logger.info(msg)

        print(ch * 45)
        logger.info(ch * 45)

        msg = "%s %s/%s (%s)" % (
            result.team1.key,
            str(result.team1.total_score),
            str(result.team1.wickets_fell),
            str(BallsToOvers(result.team1.total_balls)),
        )
        print(msg)
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
                runs += "*"

            # print
            data_to_print.append(
                [
                    GetShortName(most_runs[x].name),
                    "%s(%s)" % (runs, most_runs[x].balls),
                    GetShortName(best_bowlers[x].name),
                    "%s/%s" % (best_bowlers[x].runs_given, best_bowlers[x].wkts),
                ]
            )

        # print
        PrintListFormatted(data_to_print, 0.01, logger)

        data_to_print = []
        print(ch * 45)
        logger.info(ch * 45)

        msg = "%s %s/%s (%s)" % (
            result.team2.key,
            str(result.team2.total_score),
            str(result.team2.wickets_fell),
            str(BallsToOvers(result.team2.total_balls)),
        )
        print(msg)
        logger.info(msg)

        most_runs = sorted(result.team2.team_array, key=lambda t: t.runs, reverse=True)
        most_runs = most_runs[:n]
        best_bowlers = sorted(bowlers1, key=lambda b: b.wkts, reverse=True)
        best_bowlers = best_bowlers[:n]
        for x in range(n):
            runs = str(most_runs[x].runs)
            # if not out, put a *
            if most_runs[x].status:
                runs += "*"

            # print
            data_to_print.append(
                [
                    GetShortName(most_runs[x].name),
                    "%s(%s)" % (runs, most_runs[x].balls),
                    GetShortName(best_bowlers[x].name),
                    "%s/%s" % (best_bowlers[x].runs_given, best_bowlers[x].wkts),
                ]
            )

        PrintListFormatted(data_to_print, 0.01, logger)
        print("-" * 43)
        logger.info("-" * 43)
        input("Press Enter to continue..")
