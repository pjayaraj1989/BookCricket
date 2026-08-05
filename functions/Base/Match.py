import logging
import os
import random
import threading
import time
from operator import attrgetter
from colorama import Style, Fore
from numpy.random import choice
from data.commentary import commentary
from data.resources import resources
from functions.Pair import RotateStrike, PairFaceBall, BatsmanOut
from functions.helper import Partnership, Fow, Result, InningsSummary
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
    is_name_valid,
)
import functions.utilities as utilities
from functions.DuckworthLewis import ResourcesRemaining, RevisedTarget, ParScore, G50
import functions.SaveGame as SaveGame
import functions.Trivia as Trivia


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
            "umpires": [],  # both umpires' names (self.umpire is just the on-field one used in commentary); for trivia
            "commentators": None,
            "drs": False,
            "review_upheld": False,  # last DRS review was taken and OUT stood
            "free_hit": False,  # next legal delivery is a free hit (after a no-ball)
            "firstinnings": None,
            "secondinnings": None,
            "batting_first": None,
            "batting_second": None,
            "won": False,
            "autoplay": False,
            "fast": False,  # skip PlayOver's per-ball sleep even outside autoplay; dev/test use only
            "skip_name_check": False,  # bypass the autoplay Wikipedia roster check (tournament sims)
            "defer_super_over": False,  # leave a tie unresolved for the caller (tournament) to play the super over interactively
            "batting_team": None,
            "bowling_team": None,
            # every completed innings of this match, in the order they were
            # played (both formats - Team.innings_history is Test-only and
            # per-team, so it can't give a chronological match-wide view)
            "innings_log": [],
            # Test-match fields (all unused/no-op for limited-overs formats)
            "is_test": False,
            "day": 1,
            "max_days": 5,
            "session": 1,  # 1-3, within the current day
            "sessions_per_day": 3,
            "overs_per_session": 30,
            "overs_bowled_this_session": 0,
            "match_drawn": False,
            "declare_eligible": False,
            "follow_on_margin": 200,
            # rainy-Test rain sequence (all no-op on dry venues / limited-overs)
            "rain_enabled": False,
            "rain_done": False,
            "rain_stage": 0,  # 0 waiting, 1 cloudy, 2 drizzle, 3 heavy/stopped
            "rain_buildup_over": 0,  # match-over count when the build-up begins
            "rain_next_over": 0,  # match-over count for the next build-up stage
            "match_overs_bowled": 0,
            # limited-overs rain / Duckworth-Lewis state (all no-op unless
            # the venue is rainy and the format is limited-overs)
            "original_overs": 0,  # overs per side as scheduled at the toss
            "lo_rain_innings": 0,  # innings (1 or 2) the rain arrives in
            "lo_rain_over": 0,  # completed-over count when it arrives
            "lo_rain_done": False,  # the one rain event has happened
            "dls_lost_inn1": 0.0,  # resources (%) washed out of innings 1
            "dls_target": 0,  # D/L-revised chase target (0 = no revision)
            "rain_ended_match": False,  # washout decided the match on D/L par
            # last-over-of-a-chase tension pop-ups (set up in PlayOver)
            "last_over_phrases": [],  # the lines picked for this over's balls
            "tension_ball_shown": 0,  # last ball a tension line was popped for
            # live milestone pop-ups (reset each innings in Play)
            "team_score_milestone_shown": 0,  # highest team-total 100 popped
            "partnership_milestone_shown": 0,  # highest 50 popped, current stand
            "partnership_tracked_wkt": 0,  # wickets_fell the stand is tracked at
            # drinks break pop-ups (see _DrinksBreakOvers/_PostOverDisplay).
            # Limited-overs: reset fresh each innings in Play. Test: reset
            # whenever the session actually advances in _AdvanceSessionIfNeeded
            # (not per-innings - a session spans both teams' play within it).
            "drinks_breaks_fired": set(),  # over-numbers already fired this innings
            "drinks_break_fired_this_session": False,
            # save/resume state (see functions/SaveGame.py). save_slot is the
            # index of the innings currently in progress (limited-overs: 0/1;
            # Test: 0-3); save_started/save_done bracket that innings; the
            # over to resume at is derived from the batting side's total_balls.
            "save_enabled": False,  # only real (non-autoplay) games auto-save
            "save_id": None,  # file id, set once the match starts
            "save_client_id": None,  # owning browser (web), for save isolation
            "save_slot": 0,
            "save_started": False,
            "save_done": False,
            "resuming": False,  # this run was reconstructed from a save file
            "test_follow_on": None,  # Test: None until the follow-on is decided
            # background trivia thread (web UI only - see _StartTriviaThread);
            # neither is picklable, so both are stripped in __getstate__
            "_trivia_stop": None,
            "_trivia_thread": None,
        }
        self = FillAttributes(self, attrs, kwargs)

    def __getstate__(self):
        # the logger (a logging.Logger with an open FileHandler) and the
        # trivia thread/stop-event (threading primitives) can't be pickled
        # and are rebuilt/restarted on resume, so drop them from saved state
        state = dict(self.__dict__)
        state.pop("logger", None)
        state.pop("_trivia_stop", None)
        state.pop("_trivia_thread", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.logger = None
        self._trivia_stop = None
        self._trivia_thread = None

    def _SetupLogger(self, ScriptPath):
        """
        Build the per-match file logger and attach it as self.logger. Shared
        by PlayMatch and ResumeMatch (the logger is not part of the saved
        state - see Match.__getstate__ - so a resumed match rebuilds it).

        Returns:
            logging.FileHandler: the handler, so the caller can close it.
        """
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
        # a resumed match appends to its existing log rather than wiping it
        if os.path.isfile(log) and not self.resuming:
            os.remove(log)

        logger = logging.getLogger("%s.%s" % (__name__, self.save_id or "console"))
        logger.setLevel(logging.INFO)
        logger.handlers = []  # avoid duplicate handlers on a resumed logger
        handler = logging.FileHandler(log)
        logger.addHandler(handler)
        self.logger = logger
        return handler

    # trivia refresh cadence, in seconds - loose jitter so it doesn't feel
    # mechanical; two independent free sources (DuckDuckGo + Wikipedia)
    # comfortably tolerate this pace without rate-limiting
    TRIVIA_FIRST_DELAY = 6
    TRIVIA_INTERVAL_RANGE = (15, 25)

    def _StartTriviaThread(self):
        """
        Start a background thread that periodically fetches a short
        Wikipedia snippet - about either team, a player currently out in the
        middle, the venue, or an umpire (see functions/Trivia.py) - and pushes
        it to the web UI's corner panel. Runs on its own thread so a slow or
        failed network call never stalls actual gameplay; a no-op outside
        web mode (console has no such panel).

        Returns:
            None
        """
        channel = utilities.get_channel()
        if channel is None:
            return
        self._trivia_stop = threading.Event()
        thread = threading.Thread(
            target=self._TriviaLoop, args=(channel,), daemon=True
        )
        self._trivia_thread = thread
        thread.start()

    def _TriviaLoop(self, channel):
        """
        Background body of _StartTriviaThread. Takes the channel as an
        explicit argument rather than looking it up via get_channel(): that
        lookup is thread-local, keyed to whichever thread called
        set_channel() (the main game thread), and would resolve to nothing
        on this separate thread.

        Returns:
            None
        """
        stop = self._trivia_stop
        if stop.wait(self.TRIVIA_FIRST_DELAY):
            return
        while not stop.is_set():
            # this is pure decoration - nothing here may ever be allowed to
            # kill the thread or (far worse) escape into the game thread
            try:
                item = Trivia.GetTrivia(self)
                if item:
                    channel.trivia(item)
            except Exception:
                pass
            try:
                wait_s = random.randint(*self.TRIVIA_INTERVAL_RANGE)
            except Exception:
                wait_s = self.TRIVIA_INTERVAL_RANGE[0]
            if stop.wait(wait_s):
                break

    def _StopTriviaThread(self):
        """Signal the trivia thread to stop. It's a daemon thread (so it can
        never keep the process alive on its own), but this lets it exit
        promptly rather than lingering until its next sleep expires.

        Returns:
            None
        """
        if self._trivia_stop is not None:
            self._trivia_stop.set()

    def _PostPlay(self):
        """Victory card + persistent highlights, once the result is final.
        Shared tail of PlayMatch/ResumeMatch."""
        result = getattr(self, "result", None)
        if result is not None and getattr(result, "winner", None) is not None:
            utilities.PushEvent(
                "victory",
                {"team": result.winner.name, "result": result.result_str},
            )
        # persistent post-match highlights card; no-op in console mode
        utilities.PushMatchHighlights(self)

    def PlayMatch(self, ScriptPath):
        """
        Play the match.

        Args:
            ScriptPath: The path to the script directory.

        Returns:
            None
        """
        handler = self._SetupLogger(ScriptPath)

        # see if teams are valid
        self.ValidateMatchTeams()

        # toss, select who is batting first
        self.Toss()
        self.team1, self.team2 = self.batting_first, self.batting_second

        # teams are finalized: give this match a save-file id so every over
        # boundary can persist it for resume (real games only, not autoplay)
        if self.save_enabled and self.save_id is None:
            self.save_id = SaveGame.new_save_id()

        # match start
        self.status = True
        self.batting_team, self.bowling_team = self.team1, self.team2

        self._StartTriviaThread()
        try:
            if self.match_type == "Test":
                self.is_test = True
                self._PlayTestMatch()
            else:
                self._PlayLimitedOversMatch()

            self._PostPlay()
        finally:
            self._StopTriviaThread()

        # close log handler
        handler.close()
        return

    def ResumeMatch(self, ScriptPath):
        """
        Continue a match reconstructed from a save file. Teams, scores,
        batting pair, bowler spells, targets and the save cursor were all
        restored by unpickling; only the logger has to be rebuilt. The
        format-specific orchestrators (_PlayLimitedOversMatch / _PlayTestMatch)
        see self.resuming = True and skip fresh setup, picking up from the
        saved cursor instead.

        Returns:
            None
        """
        handler = self._SetupLogger(ScriptPath)
        self.resuming = True
        self.status = True

        PrintInColor(
            "Resuming saved match - %s vs %s at %s"
            % (self.team1.name, self.team2.name, self.venue.name),
            Style.BRIGHT,
        )
        utilities.PushEvent(
            "resume",
            {
                "team1": self.team1.name,
                "team2": self.team2.name,
                "battingTeam": self.batting_team.name,
                "score": int(self.batting_team.total_score),
                "wickets": int(self.batting_team.wickets_fell),
                "overs": float(BallsToOvers(self.batting_team.total_balls)),
            },
        )

        self._StartTriviaThread()
        try:
            if self.is_test:
                self._PlayTestMatch()
            else:
                self._PlayLimitedOversMatch()

            self._PostPlay()
        finally:
            self._StopTriviaThread()
        handler.close()
        return

    def _SaveGame(self):
        """Persist the match at the current over/innings boundary (no-op for
        autoplay or if saving is disabled)."""
        if not self.save_enabled or self.autoplay or not self.save_id:
            return
        try:
            SaveGame.save_match(self)
        except Exception as exc:  # never let a save error interrupt play
            if self.logger:
                self.logger.info("save failed: %s" % exc)

    def _DeleteSave(self):
        """Remove this match's save files (called when the match finishes)."""
        if self.save_id:
            SaveGame.delete_save(self.save_id)

    def _MarkInningsStart(self, slot):
        """Enter a fresh innings `slot`: reset the save cursor and persist so
        a crash before the first over still resumes into this innings."""
        self.save_slot = slot
        self.save_started = False
        self.save_done = False

    def SaveMeta(self):
        """Human-readable metadata for the resume picker (see SaveGame)."""
        bt = self.batting_team
        fmt = "Test" if self.is_test else "Limited overs"
        if self.is_test:
            situation = "Day %s, innings %s" % (
                str(self.day),
                str(self.save_slot + 1),
            )
        else:
            situation = "Innings %s, %s ov" % (
                str(self.save_slot + 1),
                str(BallsToOvers(bt.total_balls) if bt else 0),
            )
        target = int(bt.target) if bt and bt.batting_second and bt.target else None
        return {
            "kind": "match",
            "format": fmt,
            "match_type": self.match_type,
            "overs": self.overs,
            "venue": self.venue.name if self.venue else "",
            "team1": self.team1.name if self.team1 else "?",
            "team2": self.team2.name if self.team2 else "?",
            "battingTeam": bt.name if bt else "?",
            "batting_team": bt.name if bt else "?",
            "score": int(bt.total_score) if bt else 0,
            "wickets": int(bt.wickets_fell) if bt else 0,
            "situation": situation,
            "target": target,
            "clientId": self.save_client_id,
            "created": getattr(self, "_save_created", None) or time.time(),
        }

    def _PlayLimitedOversMatch(self):
        """
        The original fixed-length, 2-innings-total sequence (Exhibition/
        T20/ODI/custom overs) - unchanged behavior, just extracted out of
        PlayMatch so Test can use a different orchestration.

        Returns:
            None
        """
        if not self.resuming:
            self.original_overs = self.overs

            # a rainy venue gets one rain event, in either innings, at a random
            # over - it may shorten the innings (D/L revised target) or wash out
            # the rest of the match (D/L par decides the result)
            if self.venue.weather == "rainy" and self.overs:
                self.lo_rain_innings = random.choice([1, 2])
                self.lo_rain_over = random.randint(
                    max(3, self.overs // 4), self.overs - 1
                )
            self._MarkInningsStart(0)

        # INNINGS 1 (save slot 0). Skipped entirely on a resume that was saved
        # during the second innings (save_slot == 1).
        if self.save_slot == 0:
            if not self.save_done:
                self.Play(resume=self.save_started)

            # display batting and bowling scorecard
            self.DisplayScore()
            self.DisplayBowlingStats()

            # say something about the first innings
            self.batting_team.SummarizeBatting(self.autoplay)
            self.bowling_team.SummarizeBowling(self.autoplay)

            # set the second-innings target (straight, or D/L revised) and swap
            self._SetSecondInningsTarget()
            self.batting_team, self.bowling_team = self.team2, self.team1
            self._MarkInningsStart(1)
            self._SaveGame()

        # INNINGS 2 (save slot 1)
        if not self.save_done:
            self.Play(resume=self.save_started)

        # show batting and bowling scores
        self.DisplayScore()
        self.DisplayBowlingStats()

        # match ended
        self.status = False

        # show results (a mid-innings washout has already decided them on
        # D/L par and built self.result)
        if not self.rain_ended_match:
            self.CalculateResult()

        # level scores are settled with a super over. Its own stats are
        # deliberately thrown away (see _PlaySuperOver) - only the result
        # carries over, on top of the match's real scorecard. A D/L-tied
        # washout skips this: there's no play possible in the rain.
        if (
            not self.rain_ended_match
            and self.result.winner is None
            and self.result.result_str.startswith("Match Tied")
            and not self.defer_super_over
        ):
            super_winner = self._PlaySuperOver()
            if super_winner is not None:
                self.result.winner = super_winner
                self.result.result_str = "Match Tied - %s won the Super Over" % (
                    super_winner.name
                )

        # say something about the first innings
        self.batting_team.SummarizeBatting(self.autoplay)
        # summarize about bowling performance
        self.bowling_team.SummarizeBowling(self.autoplay)

        self.MatchSummary()
        self.FindPlayerOfTheMatch()
        # match is over: drop the save file so it no longer shows up to resume
        self._DeleteSave()
        return

    def _SetSecondInningsTarget(self):
        """Set team2's chase target between innings: the first innings score
        plus one, or the Duckworth-Lewis revised target if rain shortened the
        first innings."""
        if self.dls_lost_inn1 > 0:
            self.team2.target = RevisedTarget(
                self.team1.total_score,
                self._DLSResourcesTeam1(),
                ResourcesRemaining(self.overs, 0),
                self._DLSAvgScore(),
            )
            self.dls_target = self.team2.target
            msg = "D/L revised target for %s: %s from %s overs" % (
                self.team2.name,
                str(self.team2.target),
                str(self.overs),
            )
            PrintInColor(msg, Style.BRIGHT)
            if self.logger:
                self.logger.info(msg)
        else:
            self.team2.target = self.team1.total_score + 1

    # A super-over ball: high risk, high reward. Indexes SUPER_OVER_RUNS
    # (-1 is a wicket); no fives, they don't happen off the bat.
    SUPER_OVER_RUNS = [-1, 0, 1, 2, 3, 4, 6]
    SUPER_OVER_PROB = [0.10, 0.15, 0.25, 0.15, 0.03, 0.17, 0.15]

    def _PlaySuperOver(self):
        """
        Decide a tied limited-overs match with a super over: one over a side,
        three batsmen, and a maximum of two wickets, higher score wins.

        Everything is tallied locally - no Player or Team figure is ever
        written to - so the super over stays completely out of the match's own
        scorecard and stats, just as it does in the real game. A tied super
        over is replayed (capped, so a freak run of ties can't hang the game).

        Returns:
            Team: the winning team, or None if it stayed tied.
        """
        # whoever chased in the match bats first in the super over
        first = self.team2 if self.team2.batting_second else self.team1
        second = self.team1 if first is self.team2 else self.team2

        PrintInColor("The scores are level! We go to a SUPER OVER!", Style.BRIGHT)
        utilities.PushEvent("super_over", {"stage": "start"})
        if not self.autoplay:
            input("press enter to continue..")

        for attempt in range(1, 4):
            if attempt > 1:
                PrintInColor(
                    "The super over is tied as well! Another one it is!", Style.BRIGHT
                )
                utilities.PushEvent("super_over", {"stage": "start"})

            first_runs, first_wkts = self._PlaySuperOverInnings(first, second)
            second_runs, second_wkts = self._PlaySuperOverInnings(
                second, first, target=first_runs + 1
            )

            if first_runs != second_runs:
                winner = first if first_runs > second_runs else second
                msg = "%s win the super over, %s/%s to %s/%s!" % (
                    winner.name,
                    str(max(first_runs, second_runs)),
                    str(first_wkts if winner is first else second_wkts),
                    str(min(first_runs, second_runs)),
                    str(second_wkts if winner is first else first_wkts),
                )
                PrintInColor(msg, winner.color)
                utilities.PushEvent(
                    "super_over", {"stage": "result", "team": winner.name}
                )
                if not self.autoplay:
                    input("press enter to continue..")
                return winner

        PrintInColor("Still nothing between them - honours shared!", Style.BRIGHT)
        utilities.PushEvent("super_over", {"stage": "result", "team": None})
        return None

    def _PickSuperOverBatsmen(self, batting_team):
        """
        Pick the three batsmen for a super over: the player chooses them
        (numbers or short names, Enter or anything unrecognized falls back
        to auto-selection) unless autoplay. Auto-selection sends in the
        side's three best batsmen of the day.

        Returns:
            list: three Player objects.
        """
        default = sorted(batting_team.team_array, key=lambda p: -p.runs)[:3]
        if self.autoplay:
            return default
        # picked one at a time (rather than a typed list) so the web UI can
        # render each round as buttons; auto-select stops asking and fills
        # the rest from the defaults
        picked = []
        for slot in range(3):
            available = [p for p in batting_team.team_array if p not in picked]
            chosen = self._PickFromPlayers(
                available,
                "Choose batsman %s of 3 for %s's super over"
                % (str(slot + 1), batting_team.name),
            )
            if chosen is None:
                break
            picked.append(chosen)
        # top up an empty/partial selection from the defaults
        for p in default:
            if len(picked) == 3:
                break
            if p not in picked:
                picked.append(p)
        return picked

    def _PickSuperOverBowler(self, bowling_team):
        """
        Pick the bowler for a super over: the player chooses (number or
        short name, Enter or anything unrecognized auto-selects the most
        skilled bowler) unless autoplay.

        Returns:
            Player
        """
        candidates = sorted(
            bowling_team.bowlers or bowling_team.team_array,
            key=lambda p: p.attr.bowling,
            reverse=True,
        )
        if self.autoplay:
            return candidates[0]
        bowler = self._PickFromPlayers(
            candidates, "Pick %s's super-over bowler" % bowling_team.name
        )
        # auto-select (or nothing to pick from): the most skilled bowler
        return bowler if bowler is not None else candidates[0]

    def _PlaySuperOverInnings(self, batting_team, bowling_team, target=None):
        """
        One super-over innings: up to six balls, three batsmen, two wickets
        (with only three batsmen there is nobody left after the second).
        Played ball-by-ball at the same pace as a normal over, with both
        line-ups chosen by the player (unless autoplay). Read-only against
        the real squads - the tallies here are local.

        Args:
            batting_team: The team batting this super over.
            bowling_team: The team bowling it.
            target: Runs needed to win, if batting second.

        Returns:
            tuple: (runs, wickets)
        """
        batsmen = self._PickSuperOverBatsmen(batting_team)
        bowler = self._PickSuperOverBowler(bowling_team)
        PrintInColor(
            "%s to bat: %s - and %s has the ball."
            % (
                batting_team.name,
                ", ".join(GetShortName(b.name) for b in batsmen),
                GetShortName(bowler.name),
            ),
            batting_team.color,
        )

        runs = 0
        wickets = 0
        striker, next_in = 0, 2
        for ball in range(1, 7):
            # same ball-by-ball cadence as a normal over (PlayOver): announce
            # the matchup, then wait for the player before the delivery
            if target is not None:
                need = target - runs
                print(
                    "%s need %s off %s ball%s"
                    % (
                        batting_team.name,
                        str(need),
                        str(7 - ball),
                        "" if 7 - ball == 1 else "s",
                    )
                )
            print(
                "%s to %s"
                % (
                    GetShortName(bowler.name),
                    GetShortName(batsmen[striker].name),
                )
            )
            if self.autoplay:
                if not self.fast:
                    time.sleep(1)
            else:
                input("press enter to continue..")

            hit = int(choice(self.SUPER_OVER_RUNS, 1, p=self.SUPER_OVER_PROB)[0])
            if hit == -1:
                wickets += 1
                PrintInColor(
                    "%s.%s  OUT! %s goes, %s bowled by %s"
                    % (
                        str(ball // 6),
                        str(ball % 6),
                        GetShortName(batsmen[striker].name),
                        "%s/%s" % (str(runs), str(wickets)),
                        GetShortName(bowler.name),
                    ),
                    Fore.LIGHTRED_EX,
                )
                # two down and only three batsmen: that's the innings
                if wickets >= 2:
                    break
                striker = next_in
                next_in += 1
            else:
                runs += hit
                PrintInColor(
                    "%s.%s  %s scores %s - %s"
                    % (
                        str(ball // 6),
                        str(ball % 6),
                        GetShortName(batsmen[striker].name),
                        str(hit),
                        "%s/%s" % (str(runs), str(wickets)),
                    ),
                    batting_team.color,
                )
            if target is not None and runs >= target:
                break

        PrintInColor(
            "%s finish their super over on %s/%s"
            % (batting_team.name, str(runs), str(wickets)),
            Style.BRIGHT,
        )
        utilities.PushEvent(
            "super_over",
            {
                "stage": "innings",
                "team": batting_team.name,
                "runs": runs,
                "wickets": wickets,
            },
        )
        return runs, wickets

    def _SetupTestInnings(self, batting_team, bowling_team, chase, target=0):
        """
        Point Match at the next Test innings and set its chase/target
        framing. Per-innings stat resets happen inside Play() itself
        (Team.StartBattingInnings/StartBowlingInnings), not here.

        Returns:
            None
        """
        self.batting_team, self.bowling_team = batting_team, bowling_team
        batting_team.batting_second = chase
        batting_team.target = target
        self.declare_eligible = not chase

    def _ShowLeadOrTrail(self, batting_team, bowling_team):
        """
        After a completed non-chase Test innings, announce how much the
        team that just batted leads or trails by, based on runs scored so
        far by each side across all their completed innings. No-op if the
        opponent hasn't batted yet (nothing to compare against) - not
        called at all after the final chase innings, where the target
        already conveys the same thing.

        Returns:
            None
        """
        if not bowling_team.innings_history:
            return
        batting_total = sum(inn.score for inn in batting_team.innings_history)
        bowling_total = sum(inn.score for inn in bowling_team.innings_history)
        diff = batting_total - bowling_total
        if diff > 0:
            msg = "%s lead by %s run%s." % (batting_team.name, str(diff), "" if diff == 1 else "s")
        elif diff < 0:
            msg = "%s trail by %s run%s." % (batting_team.name, str(-diff), "" if diff == -1 else "s")
        else:
            msg = "Scores are level between %s and %s." % (batting_team.name, bowling_team.name)
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)

    def _FinalizeIfDrawn(self):
        """
        If the match was drawn (ran out of match days mid-innings),
        finalize the draw result/summary.

        Returns:
            bool: True if the match was drawn (caller should stop), else False.
        """
        if not self.match_drawn:
            return False
        self.status = False
        self.result = Result(
            team1=self.team1, team2=self.team2, winner=None, result_str="Match Drawn"
        )
        self.MatchSummaryTest()
        self.FindPlayerOfTheMatchTest()
        self._DeleteSave()
        return True

    def _DecideFollowOn(self, team_a, team_b, a_inn1, b_inn1):
        """
        Ask (or, in autoplay, decide) whether team_a's captain enforces the
        follow-on against team_b, who trailed by at least follow_on_margin
        after the first innings each.

        Returns:
            bool
        """
        lead = a_inn1.score - b_inn1.score
        msg = (
            "%s lead by %s runs after the first innings. Enforce the follow-on on %s?"
            % (team_a.name, str(lead), team_b.name)
        )
        PrintInColor(msg, Style.BRIGHT)
        if self.autoplay:
            # simple default: enforce whenever there are enough days left to
            # realistically bowl the opposition out twice
            enforce = (self.max_days - self.day) >= 2
            print(
                "Auto-selected choice: %s"
                % ("Enforce follow-on" if enforce else "Bat again")
            )
            return enforce
        return ChooseFromOptions(["y", "n"], "Enforce follow-on?", 5) == "y"

    def _FinalizeTestResult(self, winner, loser, kind, margin):
        """
        Build self.result for a decisive (non-draw) Test outcome and run
        the Test-specific summary/player-of-the-match.

        Args:
            kind: "innings" | "runs" | "wickets"

        Returns:
            None
        """
        self.status = False
        result = Result(team1=self.team1, team2=self.team2, winner=winner)
        if kind == "innings":
            result.result_str = "%s won by an innings and %s runs" % (
                winner.name,
                str(margin),
            )
        elif kind == "runs":
            char = "run" if margin == 1 else "runs"
            result.result_str = "%s won by %s %s" % (winner.name, str(margin), char)
        else:  # "wickets"
            char = "wicket" if margin == 1 else "wickets"
            result.result_str = "%s won by %s %s" % (winner.name, str(margin), char)
        self.result = result
        self.MatchSummaryTest()
        self.FindPlayerOfTheMatchTest()
        self._DeleteSave()

    def _FinalizeChase(self, chasing, defending, target):
        """
        Resolve the result of a Test's final (target-chasing) innings.

        Returns:
            None
        """
        if self.match_drawn:
            self._FinalizeIfDrawn()
            return
        if chasing.total_score >= target:
            margin = 10 - chasing.wickets_fell
            self._FinalizeTestResult(
                winner=chasing, loser=defending, kind="wickets", margin=margin
            )
        elif chasing.wickets_fell == 10:
            margin = target - 1 - chasing.total_score
            self._FinalizeTestResult(
                winner=defending, loser=chasing, kind="runs", margin=margin
            )
        else:
            # days ran out mid-chase without the batting side being bowled
            # out - survived to a draw, not a bowling-side win
            self.match_drawn = True
            self._FinalizeIfDrawn()

    def _PlayTestMatch(self):
        """
        Orchestrate a full Test match: up to 4 innings (2 per team), with a
        follow-on option and draw handling. Toss()/ValidateMatchTeams()
        already ran; self.team1 bats first, self.team2 bats second (per
        the existing Toss()/PlayMatch reassignment convention).

        Returns:
            None
        """
        team_a, team_b = self.team1, self.team2

        if not self.resuming:
            # a rainy venue gets a live rain sequence later in the day (once per
            # match): flag it and greet the players with brooding rain clouds
            if self.venue.weather == "rainy":
                self.rain_enabled = True
                # build-up begins after ~30+ overs of play
                self.rain_buildup_over = 30 + random.randint(0, 25)
                utilities.PushEvent("rain", {"stage": "clouds"})
                PrintInColor(
                    "Dark rain clouds hang over the ground as the players take the field.",
                    Style.BRIGHT,
                )
            self._MarkInningsStart(0)

        # The 4 Test innings are numbered save slots 0-3 so a resume can jump
        # back to the exact one in progress. Each slot: set it up (deterministic,
        # safe to repeat on resume), play it (fresh, or continuing from the
        # saved over), then handle the between-innings logic and advance.

        # SLOT 0: A's first innings
        if self.save_slot == 0:
            if not self.save_done:
                self._SetupTestInnings(team_a, team_b, chase=False)
                self.Play(resume=self.save_started)
            if self._FinalizeIfDrawn():
                return
            self._TestAdvanceSlot(1)

        # SLOT 1: B's first innings
        if self.save_slot == 1:
            if not self.save_done:
                self._SetupTestInnings(team_b, team_a, chase=False)
                self.Play(resume=self.save_started)
            if self._FinalizeIfDrawn():
                return
            self._ShowLeadOrTrail(team_b, team_a)
            self._TestAdvanceSlot(2)

        # both first innings are complete: work out who leads (deterministic
        # from innings_history, so it recomputes identically on resume)
        a_inn1 = team_a.innings_history[0]
        b_inn1 = team_b.innings_history[0]
        if a_inn1.score >= b_inn1.score:
            lead_team, trail_team = team_a, team_b
            lead_inn1, trail_inn1 = a_inn1, b_inn1
        else:
            lead_team, trail_team = team_b, team_a
            lead_inn1, trail_inn1 = b_inn1, a_inn1

        # decide the follow-on exactly once, then persist it so a resume never
        # re-prompts the captain (None = not yet decided)
        if self.test_follow_on is None:
            available = (lead_inn1.score - trail_inn1.score) >= self.follow_on_margin
            self.test_follow_on = bool(
                available
                and self._DecideFollowOn(lead_team, trail_team, lead_inn1, trail_inn1)
            )
            self._SaveGame()

        if self.test_follow_on:
            # SLOT 2 (follow-on): the trailing team bats again immediately
            if self.save_slot == 2:
                if not self.save_started:
                    utilities.PushEvent(
                        "follow_on",
                        {"team": lead_team.name, "opponent": trail_team.name},
                    )
                if not self.save_done:
                    self._SetupTestInnings(trail_team, lead_team, chase=False)
                    self.Play(resume=self.save_started)
                if self._FinalizeIfDrawn():
                    return
                self._ShowLeadOrTrail(trail_team, lead_team)
                trail_combined = trail_inn1.score + trail_team.innings_history[1].score
                if trail_combined <= lead_inn1.score:
                    # leading team wins by an innings, never bats again
                    margin = lead_inn1.score - trail_combined
                    self._FinalizeTestResult(
                        winner=lead_team, loser=trail_team, kind="innings", margin=margin
                    )
                    return
                self._TestAdvanceSlot(3)

            # SLOT 3 (follow-on): leading team chases
            target = (
                trail_inn1.score + trail_team.innings_history[1].score
            ) - lead_inn1.score + 1
            if not self.save_done:
                self._SetupTestInnings(lead_team, trail_team, chase=True, target=target)
                self.Play(resume=self.save_started)
            self._FinalizeChase(chasing=lead_team, defending=trail_team, target=target)
            return

        # normal order (no follow-on): team_a always bats innings 2 next
        # regardless of who's ahead - follow-on is the only thing that
        # changes the natural batting order
        # SLOT 2 (normal): A's second innings
        if self.save_slot == 2:
            if not self.save_done:
                self._SetupTestInnings(team_a, team_b, chase=False)
                self.Play(resume=self.save_started)
            if self._FinalizeIfDrawn():
                return
            self._ShowLeadOrTrail(team_a, team_b)
            self._TestAdvanceSlot(3)

        # SLOT 3 (normal): B bats innings 2, chasing
        a_inn2 = team_a.innings_history[1]
        target = (a_inn1.score + a_inn2.score) - b_inn1.score + 1
        if not self.save_done:
            self._SetupTestInnings(team_b, team_a, chase=True, target=target)
            self.Play(resume=self.save_started)
        self._FinalizeChase(chasing=team_b, defending=team_a, target=target)
        return

    def _TestAdvanceSlot(self, slot):
        """Move the Test save cursor to the next innings slot and persist, so
        a crash in the gap between innings resumes cleanly into the new one."""
        self._MarkInningsStart(slot)
        self._SaveGame()

    def Play(self, resume=False):
        """
        Play the innings.

        Args:
            resume: True when continuing an innings that was interrupted and
                reloaded from a save - the openers intro, milestone-tracker
                reset and per-innings figure reset are all skipped, and the
                over loop picks up from the saved position (derived from the
                batting side's ball count) with the saved batting pair.

        Returns:
            None
        """
        batting_team = self.batting_team
        bowling_team = self.bowling_team
        logger = self.logger

        if resume:
            # continue an in-progress innings: the batting pair, strike flags,
            # scores and bowler spells are all as they were at the last over
            # boundary; don't reset anything.
            pair = list(batting_team.current_pair)
            start_over = int(batting_team.total_balls // 6)
            PrintInColor(
                "Resuming %s's innings at %s/%s (%s overs)."
                % (
                    batting_team.name,
                    str(batting_team.total_score),
                    str(batting_team.wickets_fell),
                    str(BallsToOvers(batting_team.total_balls)),
                ),
                batting_team.color,
            )
        else:
            # a new list, not a reference to opening_pair itself: GetNextBatsman
            # mutates this pair in place (pair[ind] = ...) as wickets fall, and
            # that mutation must never bleed back into Team.opening_pair - a
            # pre-existing aliasing bug that was harmless when a team only ever
            # batted once, but corrupted the record of who the real openers are
            # once a team can bat a second time in a Test match
            pair = list(batting_team.opening_pair)
            start_over = 0

            utilities.PushEvent(
                "openers",
                {
                    "names": [p.name for p in pair],
                    "caption": Randomize(commentary.commentary_openers_intro)
                    % (pair[0].name, pair[1].name),
                },
            )

            # fresh milestone tracking for this innings (team-total and stand pop-ups)
            self.team_score_milestone_shown = 0
            self.partnership_milestone_shown = 0
            self.partnership_tracked_wkt = 0
            self.drinks_breaks_fired = set()

            # reset accumulators for this innings. For limited-overs matches this
            # is a no-op in effect (each team only ever calls it once, and fields
            # already start at their __init__ defaults) - it's what lets a team
            # bat a *second* time in a Test match without old figures bleeding in.
            batting_team.StartBattingInnings()
            bowling_team.StartBowlingInnings()
            # make the pair reachable immediately, so a crash during the very
            # first over resumes with a valid current_pair
            batting_team.current_pair = pair
            # the innings has now begun; mark the cursor and persist
            self.save_started = True
            self._SaveGame()

        if batting_team.batting_second is True:
            msg = "Target for %s: %s" % (batting_team.name, str(batting_team.target))
            if self.overs:
                msg += " from %s overs" % str(self.overs)
            PrintInColor(msg, batting_team.color)
            logger.info(msg)
            # required run rate isn't a meaningful concept for a Test chase
            # (see Team.GetRequiredRate) - skip the line entirely there
            if not self.is_test:
                reqd_rr = batting_team.GetRequiredRate()
                msg = "Reqd. run rate: %s" % (str(reqd_rr))
                print(msg)
                logger.info(msg)

        # pop-up as the innings begins: the target when chasing, or (in a Test)
        # how far this side leads/trails entering the innings
        self._PushInningsSituation()

        if self.is_test:
            self._PlayTestInningsOvers(pair, start_over)
        else:
            self._PlayLimitedOversInnings(pair, start_over)

        # the innings' over loop has ended (all out / overs up / chase won /
        # declared / days out): mark it complete and persist, so resume never
        # replays this final, possibly decisive over with fresh dice
        self.save_done = True
        self._SaveGame()

        # innings just finished: snapshot it first so the "innings over" card
        # can carry a quick summary (top scorer / best bowler)
        summary = self.BuildInningsSummary()

        # pop the "innings over" card if the match is still alive (not a
        # completed chase or a day-5 draw - the victory card says it better).
        if self.status:
            faced = [b for b in summary.batting_card if b["balls"] > 0]
            top_bat = max(faced, key=lambda b: b["runs"], default=None)
            top_bowl = None
            if summary.bowling_card:
                top_bowl = sorted(
                    summary.bowling_card, key=lambda b: (-b["wickets"], b["runs"])
                )[0]
            utilities.PushEvent(
                "innings_over",
                {
                    "team": batting_team.name,
                    "score": int(batting_team.total_score),
                    "wickets": int(batting_team.wickets_fell),
                    "overs": float(summary.overs),
                    "topBatter": (
                        {"name": top_bat["name"], "runs": top_bat["runs"], "balls": top_bat["balls"]}
                        if top_bat
                        else None
                    ),
                    "topBowler": (
                        {"name": top_bowl["name"], "wickets": top_bowl["wickets"], "runs": top_bowl["runs"]}
                        if top_bowl
                        else None
                    ),
                },
            )

        # the deeper read on how the innings actually went. Unlike the card
        # above this fires for EVERY innings including the last, so a completed
        # chase still gets its analysis (after the victory card, not instead)
        analysis = self._BuildInningsAnalysis(summary)
        if analysis:
            utilities.PushEvent("innings_analysis", analysis)

        # store the snapshot (Test's multi-innings history) and send the web
        # UI's full innings summary; the push is a no-op outside web mode
        if self.is_test:
            batting_team.innings_history.append(summary)
        # chronological, match-wide record used by the final highlights card
        self.innings_log.append(summary)
        utilities.PushInningsScorecard(self, summary)
        return

    def _PlayLimitedOversInnings(self, pair, start_over=0):
        """
        Play a fixed-length (Exhibition/T20/ODI/custom) innings, over by
        over, for exactly self.overs overs.

        Args:
            start_over: over to begin at (non-zero when resuming a saved
                innings that was interrupted partway through).

        Returns:
            None
        """
        batting_team = self.batting_team

        # loop over-by-over; a while (not a for) because a rain interruption
        # can revise self.overs downwards mid-innings
        over = start_over
        while over < self.overs:
            # rain build-up/stoppage; True means the innings (maybe the
            # match) ends right here
            if self._MaybeLimitedOversRain(over):
                break

            # check match stats and comment
            if self.status is False:
                break

            # check if last over
            if over == self.overs - 1:
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

            # if match ended
            if self.status is False:
                break

            self._PostOverDisplay(pair)
            over += 1
            # over boundary: persist so a crash loses at most this partial over
            self.save_started = True
            self.save_done = False
            self._SaveGame()
        return

    def _MaybeLimitedOversRain(self, over):
        """
        Drive the limited-overs rain sequence on a rainy venue: build-up
        commentary in the overs before the scheduled stoppage, then the
        stoppage itself, which washes a random number of overs out of the
        match. One rain event per match, in either innings.

        If some overs survive, the innings continues with a reduced overs
        count (self.overs is revised; a chase also gets a Duckworth-Lewis
        revised target). If the rain eats everything that was left, the
        innings ends here - and if that innings is the chase, the match is
        decided immediately on the D/L par score.

        Args:
            over: Completed overs bowled in this innings so far.

        Returns:
            bool: True if the innings should end right now.
        """
        if not self.overs or self.lo_rain_done or not self.lo_rain_innings:
            return False
        innings_now = 2 if self.batting_team.batting_second else 1
        if innings_now != self.lo_rain_innings:
            return False

        if over == self.lo_rain_over - 5:
            PrintInColor(Randomize(commentary.commentary_rain_cloudy), Style.BRIGHT)
            utilities.PushEvent("rain", {"stage": "cloudy"})
        elif over == self.lo_rain_over - 3:
            PrintInColor(Randomize(commentary.commentary_rain_drizzling), Style.BRIGHT)
            utilities.PushEvent("rain", {"stage": "drizzle"})
        elif over == self.lo_rain_over - 1:
            PrintInColor(Randomize(commentary.commentary_rain_heavy), Style.BRIGHT)
            utilities.PushEvent("rain", {"stage": "heavy"})
        elif over == self.lo_rain_over:
            self.lo_rain_done = True
            PrintInColor(
                Randomize(commentary.commentary_rain_interrupt), Style.BRIGHT
            )
            remaining = self.overs - over
            lost = random.randint(max(2, self.overs // 5), self.overs)
            if lost >= remaining:
                return self._RainEndsInnings(over)
            return self._RainShortensInnings(over, lost)
        return False

    def _RainShortensInnings(self, over, lost):
        """
        Rain washed out `lost` overs but play resumes: revise self.overs
        down, record the resources lost, and - if this is the chase - set
        the Duckworth-Lewis revised target immediately.

        Returns:
            bool: True if the (rare) revised target is already passed and
            the innings is over.
        """
        batting_team = self.batting_team
        remaining_before = self.overs - over
        wkts = batting_team.wickets_fell
        washed_resources = ResourcesRemaining(
            remaining_before, wkts
        ) - ResourcesRemaining(remaining_before - lost, wkts)

        self._ReviseOvers(self.overs - lost)
        msg = "Rain has stopped play! %s overs are lost - the %s is reduced to %s overs." % (
            str(lost),
            "chase" if batting_team.batting_second else "innings",
            str(self.overs),
        )
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)
        utilities.PushEvent(
            "rain", {"stage": "stopped", "resume": msg}
        )

        if not batting_team.batting_second:
            # innings 1: bank the lost resources; the chase target is
            # computed from them at the innings break, and the chase is
            # played to the same reduced overs
            self.dls_lost_inn1 += washed_resources
            if not self.autoplay:
                input("press enter to continue..")
            return False

        # innings 2: revise the target right away
        r2 = ResourcesRemaining(self.original_overs, 0) - washed_resources
        batting_team.target = RevisedTarget(
            self.bowling_team.total_score,
            self._DLSResourcesTeam1(),
            r2,
            self._DLSAvgScore(),
        )
        self.dls_target = batting_team.target
        msg = "D/L revised target for %s: %s from %s overs" % (
            batting_team.name,
            str(batting_team.target),
            str(self.overs),
        )
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)
        utilities.PushEvent(
            "target",
            {
                "team": batting_team.name,
                "runsToWin": int(batting_team.target - batting_team.total_score),
                "overs": int(self.overs),
                "dls": True,
            },
        )
        if not self.autoplay:
            input("press enter to continue..")

        # the revision can (rarely) leave the chasers already past the new
        # target - the match is won on the spot
        if batting_team.total_score >= batting_team.target:
            self.status = False
            self.rain_ended_match = True
            result = Result(team1=self.team1, team2=self.team2, winner=batting_team)
            margin = 10 - batting_team.wickets_fell
            result.result_str = "%s won by %s wicket%s (D/L method)" % (
                batting_team.name,
                str(margin),
                "" if margin == 1 else "s",
            )
            self.result = result
            PrintInColor(result.result_str, batting_team.color)
            # the revised target is already beaten - this IS the winning
            # moment, same as an ordinary chase decision
            self._PushChaseDecided(chasing_won=True)
            return True
        return False

    def _RainEndsInnings(self, over):
        """
        Rain washed out everything that was left of this innings.

        Innings 1: the innings closes at `over` overs and the chase is
        reduced to the same length (target follows at the innings break).
        Innings 2: no further play is possible - the match is decided
        right here on the Duckworth-Lewis par score.

        Returns:
            bool: True always (the innings is over).
        """
        batting_team = self.batting_team
        remaining = self.overs - over
        wkts = batting_team.wickets_fell

        if not batting_team.batting_second:
            self.dls_lost_inn1 += ResourcesRemaining(remaining, wkts)
            self._ReviseOvers(over)
            msg = (
                "The rain refuses to relent! %s's innings is cut short at %s overs - "
                "the match is reduced to %s overs a side." % (
                    batting_team.name,
                    str(over),
                    str(over),
                )
            )
            PrintInColor(msg, Style.BRIGHT)
            self.logger.info(msg)
            utilities.PushEvent("rain", {"stage": "stopped", "resume": msg})
            if not self.autoplay:
                input("press enter to continue..")
            return True

        # chase washed out: decide the match on D/L par
        r2_start = ResourcesRemaining(self.overs, 0)
        r2_used = r2_start - ResourcesRemaining(remaining, wkts)
        par = ParScore(
            self.bowling_team.total_score,
            self._DLSResourcesTeam1(),
            r2_used,
            self._DLSAvgScore(),
        )
        score = int(batting_team.total_score)

        self.status = False
        self.rain_ended_match = True
        result = Result(team1=self.team1, team2=self.team2)
        if score > par:
            result.winner = batting_team
            margin = score - par
            result.result_str = "%s won by %s run%s (D/L method)" % (
                batting_team.name,
                str(margin),
                "" if margin == 1 else "s",
            )
        elif score == par:
            result.winner = None
            result.result_str = "Match Tied (D/L method)"
        else:
            result.winner = self.bowling_team
            margin = par - score
            result.result_str = "%s won by %s run%s (D/L method)" % (
                self.bowling_team.name,
                str(margin),
                "" if margin == 1 else "s",
            )
        self.result = result
        # no further play is possible, so this par-score comparison IS the
        # winning moment - unless it's a tie (no winner to celebrate, and no
        # super over follows a rain-decided match either)
        if result.winner is not None:
            self._PushChaseDecided(chasing_won=(result.winner is batting_team))

        msg = (
            "No further play is possible! At %s/%s after %s overs, "
            "the D/L par score was %s. %s" % (
                str(score),
                str(wkts),
                str(over),
                str(par),
                result.result_str,
            )
        )
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)
        utilities.PushEvent("rain", {"stage": "stopped", "resume": msg})
        if not self.autoplay:
            input("press enter to continue..")
        return True

    def _ReviseOvers(self, new_overs):
        """
        Cut the match's overs-per-side to new_overs after a rain delay,
        keeping the teams' own overs fields (used for required-rate maths
        and the web scorecard) in sync. Bowlers' per-spell caps are left
        alone - with fewer total overs they simply never bind.

        Returns:
            None
        """
        self.overs = int(new_overs)
        self.team1.total_overs = self.overs
        self.team2.total_overs = self.overs

    def _DLSResourcesTeam1(self):
        """
        Resources (%) the side batting first actually had: a full innings'
        worth for the scheduled overs, minus whatever the rain washed out
        of their innings.

        Returns:
            float
        """
        return ResourcesRemaining(self.original_overs, 0) - self.dls_lost_inn1

    def _DLSAvgScore(self):
        """
        The G50 constant (average full-innings score) scaled to this
        match's scheduled length, for D/L target maths in short formats.

        Returns:
            float
        """
        return G50 * self.original_overs / 50.0

    def _PlayTestInningsOvers(self, pair, start_over=0):
        """
        Play an open-ended Test innings: continues until all-out, declared,
        or the match runs out of days - never a fixed overs count.

        Args:
            start_over: over to begin at (non-zero when resuming a saved
                innings). The session/day counters that actually govern a
                Test innings live on the Match and are restored from the save,
                so this only re-seeds the local over counter.

        Returns:
            None
        """
        batting_team = self.batting_team
        over = start_over
        # discard a Declare press (and a stale "simulate rest of innings"
        # press) left over from a previous innings so neither can trigger a
        # surprise at the first over of this innings
        utilities.ConsumeDeclareRequest()
        utilities.ConsumeSimulateInningsRequest()
        # entered once the GUI's "Simulate rest of innings" button fires (see
        # below); torn down in the finally so a crash/early return can never
        # leave the browser channel detached. original_autoplay/fast are
        # restored verbatim rather than to False - a tournament match can
        # already be running with fast=True (or the whole thing on autoplay)
        # before this innings even starts, and that must survive untouched.
        original_autoplay, original_fast = self.autoplay, self.fast
        silent_cm = None
        try:
            while True:
                if self._AdvanceSessionIfNeeded():
                    break
                if self.status is False:
                    break
                if batting_team.wickets_fell == 10:
                    break

                if (
                    silent_cm is None
                    and not self.autoplay
                    and utilities.ConsumeSimulateInningsRequest()
                ):
                    # push the notice, THEN detach - once silenced nothing
                    # reaches the browser until this innings ends
                    utilities.PushEvent(
                        "simulating_innings", {"team": batting_team.name}
                    )
                    PrintInColor(
                        "Simulating the rest of %s's innings..." % batting_team.name,
                        Style.BRIGHT,
                    )
                    self.autoplay, self.fast = True, True
                    silent_cm = utilities.SilentPlay()
                    silent_cm.__enter__()

                if self._ShouldDeclare(over):
                    batting_team.declared = True
                    utilities.PushEvent(
                        "declare",
                        {
                            "team": batting_team.name,
                            "score": int(batting_team.total_score),
                            "wickets": int(batting_team.wickets_fell),
                        },
                    )
                    PrintInColor(
                        "%s have declared their innings at %s/%s (%s overs)!"
                        % (
                            batting_team.name,
                            str(batting_team.total_score),
                            str(batting_team.wickets_fell),
                            str(BallsToOvers(batting_team.total_balls)),
                        ),
                        Style.BRIGHT,
                    )
                    break

                if over > 1 and over % 20 == 0:
                    self.CurrentMatchStatus()

                self.batting_team.current_pair = pair
                self.PlayOver(over)
                self.overs_bowled_this_session += 1
                self.match_overs_bowled += 1

                if self.status is False:
                    break

                # rain may build up and eventually stop play, burning overs
                # off the day/match clock (and drawing the match if days run out)
                if self._MaybeRain():
                    break

                self._PostOverDisplay(pair)
                over += 1
                # over boundary: persist so a crash loses at most this partial over
                self.save_started = True
                self.save_done = False
                self._SaveGame()
        finally:
            if silent_cm is not None:
                silent_cm.__exit__(None, None, None)
                # this innings only - hand back whatever mode was in effect
                # before the button was pressed for whatever comes next
                # (follow-on choice, next innings, etc.)
                self.autoplay, self.fast = original_autoplay, original_fast
        return

    def _MaybeRain(self):
        """
        Drive the Test-match rain sequence on a rainy venue: a gradual
        build-up (cloudy -> drizzle -> heavy) spread over a handful of overs,
        then a stoppage that burns overs off the day/match clock. Runs once
        per match; a no-op on dry venues or after it has already happened.
        Called once per over from the Test over-loop.

        Returns:
            bool: True if the rain stoppage ended the match (drew it).
        """
        if not self.rain_enabled or self.rain_done:
            return False
        n = self.match_overs_bowled

        if self.rain_stage == 0:
            if n < self.rain_buildup_over:
                return False
            PrintInColor(Randomize(commentary.commentary_rain_cloudy), Style.BRIGHT)
            utilities.PushEvent("rain", {"stage": "cloudy"})
            self.rain_stage = 1
            self.rain_next_over = n + random.randint(5, 10)
        elif self.rain_stage == 1 and n >= self.rain_next_over:
            PrintInColor(Randomize(commentary.commentary_rain_drizzling), Style.BRIGHT)
            utilities.PushEvent("rain", {"stage": "drizzle"})
            self.rain_stage = 2
            self.rain_next_over = n + random.randint(2, 5)
        elif self.rain_stage == 2 and n >= self.rain_next_over:
            PrintInColor(Randomize(commentary.commentary_rain_heavy), Style.BRIGHT)
            utilities.PushEvent("rain", {"stage": "heavy"})
            self.rain_stage = 3
            self.rain_done = True
            return self._RainStopsPlay()
        return False

    def _RainStopsPlay(self):
        """
        Rain has stopped play: announce it, wash out a chunk of overs from the
        day/match clock (rolling into the next day if the rest of today is
        lost), and draw the match if the delay uses up the scheduled days.

        Returns:
            bool: True if the match is now drawn (over), else False.
        """
        lost = random.randint(25, 60)  # overs washed out by the rain
        day_before = self.day
        drawn = self._BurnOversToRain(lost)
        if drawn:
            PrintInColor(
                "The rain has the final say - no further play is possible and "
                "the match is drawn!",
                Style.BRIGHT,
            )
            utilities.PushEvent(
                "rain", {"stage": "stopped", "resume": "No further play - match drawn"}
            )
            return True
        resume = (
            "Play resumes on Day %s" % str(self.day)
            if self.day > day_before
            else "Play will resume shortly"
        )
        PrintInColor("Rain has stopped play. %s." % resume, Style.BRIGHT)
        utilities.PushEvent("rain", {"stage": "stopped", "resume": resume})
        if not self.autoplay:
            input("press enter to continue..")
        return False

    def _BurnOversToRain(self, n):
        """
        Advance the session/day clock by n washed-out overs, rolling into
        later sessions and the next day as needed. Marks the match drawn if
        the days run out.

        Returns:
            bool: True if the match ran out of days (drawn), else False.
        """
        while n > 0:
            remaining = self.overs_per_session - self.overs_bowled_this_session
            if n < remaining:
                self.overs_bowled_this_session += n
                return False
            n -= remaining
            self.overs_bowled_this_session = 0
            self.drinks_break_fired_this_session = False
            if self.session < self.sessions_per_day:
                self.session += 1
            else:
                self.session = 1
                self.day += 1
                if self.day > self.max_days:
                    self.match_drawn = True
                    self.status = False
                    return True
        return False

    def _PostOverDisplay(self, pair):
        """
        Shared per-over display/bookkeeping used by both the limited-overs
        and Test over-loops: current batsmen figures, highlights, bowling/
        batting scorecards, projected score (limited-overs only), strike
        rotation.

        Returns:
            None
        """
        logger = self.logger
        for p in pair:
            msg = "%s %s (%s)" % (GetShortName(p.name), str(p.runs), str(p.balls))
            print(msg)
            logger.info(msg)

        self.ShowHighlights()
        self.DisplayBowlingStats()
        self.DisplayScore()
        # extrapolating a "projected final score" from self.overs is a
        # limited-overs-only concept - meaningless (and would crash on
        # self.overs being None) for a Test innings
        if not self.is_test:
            self.DisplayProjectedScore()

        # the full (batting/bowling/fall-of-wickets) scorecard snapshot is
        # already pushed to the web UI's side pane after every ball (see the
        # per-ball loop in PlayOver), so no additional push is needed here

        # milestone pop-ups (team total 100/200/..., current stand 50/100/...)
        self._CheckScoreMilestones()

        # how's the chase going? every 10th completed over while chasing (the
        # wicket-triggered check lives in UpdateDismissal) - a no-op outside
        # a limited-overs run chase, so this is safe to call unconditionally
        # from the Test over-loop too
        if self.overs and self.batting_team.batting_second:
            completed_overs = self.batting_team.total_balls // 6
            if completed_overs > 0 and completed_overs % 10 == 0:
                self._PushChaseAssessment()

        self._CheckDrinksBreak()

        # rotate strike after an over
        RotateStrike(pair)

    def _DrinksBreakOvers(self):
        """
        Completed-over counts at which a drinks break falls in this
        limited-overs innings: 2 for an ODI-length innings, 1 for a
        T20-length one, none for a short exhibition game. Recomputed live
        from self.overs (not cached) so a rain-revised over count reschedules
        automatically rather than firing at a now-stale over number.

        Returns:
            list[int]
        """
        if not self.overs:
            return []
        if self.overs >= 40:
            return [round(self.overs / 3), round(2 * self.overs / 3)]
        if self.overs >= 10:
            return [round(self.overs / 2)]
        return []

    def _CheckDrinksBreak(self):
        """
        Pop a "drinks break" card at the scheduled point(s) for this innings:
        twice for an ODI-length limited-overs innings, once for a T20-length
        one (see _DrinksBreakOvers), or once per Test session - never within
        the last 5 overs of a limited-overs innings, so it can't fire right
        as the game is about to finish. Called once per over from
        _PostOverDisplay, so it applies to both formats.

        Returns:
            None
        """
        bt = self.batting_team
        if self.overs:
            completed_overs = bt.total_balls // 6
            overs_left = self.overs - completed_overs
            if (
                overs_left >= 5
                and completed_overs in self._DrinksBreakOvers()
                and completed_overs not in self.drinks_breaks_fired
            ):
                self.drinks_breaks_fired.add(completed_overs)
                utilities.PushEvent("drinks_break", {"team": bt.name})
        elif self.is_test:
            # Test has no fixed over limit, so the "not near the end" guard
            # doesn't apply - once per session, at its rough halfway point
            if (
                not self.drinks_break_fired_this_session
                and self.overs_bowled_this_session >= self.overs_per_session // 2
            ):
                self.drinks_break_fired_this_session = True
                utilities.PushEvent("drinks_break", {"team": bt.name})

    def _UpdateBoundaryStreak(self, batsman, run):
        """
        Track a batsman's back-to-back boundaries and pop a big card once they
        reach three in a row (and again for each one after that). A boundary
        never changes the strike, so the streak is genuinely one batsman's.
        Any non-boundary ball they face clears it.

        Args:
            batsman: The batsman on strike (None is tolerated).
            run: Runs off the ball (4 or 6 extends the streak, anything else
                ends it).

        Returns:
            None
        """
        if batsman is None:
            return
        if run not in (4, 6):
            batsman.boundary_streak = []
            return

        batsman.boundary_streak.append(run)
        streak = batsman.boundary_streak
        if len(streak) < 3:
            return

        # name the shot when the streak is all one kind, otherwise call them
        # boundaries
        if all(r == 6 for r in streak):
            what = "SIXES"
        elif all(r == 4 for r in streak):
            what = "FOURS"
        else:
            what = "BOUNDARIES"
        text = "%s %s IN A ROW!" % (str(len(streak)), what)
        PrintInColor(
            "%s - %s!" % (text, GetShortName(batsman.name)), Fore.LIGHTGREEN_EX
        )
        utilities.PushEvent(
            "boundary_streak",
            {"name": batsman.name, "count": len(streak), "text": text},
        )

    def _BowlerWicketStreak(self, bowler):
        """
        This bowler's currently-live streak of consecutive wicket-taking
        deliveries, for hat-trick / N-in-a-row detection: walk backward
        through their ball history, skipping wides (not a delivery faced,
        so they can neither extend nor break the streak), and stop at the
        first entry that isn't a bowler-credited wicket - a run scored, a
        no-ball, or a run-out (never credited to the bowler, and itself a
        real delivery that breaks the sequence).

        Returns:
            int: the streak length (0 if the last delivery wasn't a wicket).
        """
        streak = 0
        for entry in reversed(bowler.ball_history):
            if entry == "WD":
                continue
            if entry == "Wkt":
                streak += 1
                continue
            break
        return streak

    def _PushChaseDecided(self, chasing_won):
        """
        Fire a big, immediate full-screen "victory moment" popup right after
        the ball that decides a limited-overs run-chase (won or lost) - a
        punchy flavor line, shown well before the later, factual result/
        trophy card that only appears at the very end of PlayMatch (after
        the scorecards, summaries, and player-of-the-match).

        Args:
            chasing_won: True if the chasing side reached the target, False
                if it fell short (the defending side held on).

        Returns:
            None
        """
        batting_team, bowling_team = self.batting_team, self.bowling_team
        winner = batting_team if chasing_won else bowling_team
        pool = (
            commentary.commentary_chase_success
            if chasing_won
            else commentary.commentary_chase_failed
        )
        line = Randomize(pool)
        PrintInColor(line, winner.color)
        utilities.PushEvent("match_decided", {"team": winner.name, "text": line})

    def _PushLastOverTension(self, ball):
        """
        Pop a tension line for one ball of the final over of a chase: balls 1-5
        use the lines picked for this over, and the last ball gets a stronger
        one of its own.

        Args:
            ball: The ball number within the over (1-6).

        Returns:
            None
        """
        if ball >= 6:
            phrase = Randomize(commentary.commentary_last_ball_tension)
        elif self.last_over_phrases:
            phrase = self.last_over_phrases[(ball - 1) % len(self.last_over_phrases)]
        else:
            return
        bt = self.batting_team
        # equation as this ball is about to be bowled: runs still needed and
        # legal balls left in the over (this ball included)
        runs_to_win = int(bt.target - bt.total_score)
        balls_left = 7 - ball
        PrintInColor(phrase, Style.BRIGHT)
        utilities.PushEvent(
            "tension",
            {
                "text": phrase,
                "final": ball >= 6,
                "runsToWin": runs_to_win,
                "ballsLeft": balls_left,
            },
        )

    def _PushInningsSituation(self):
        """
        Pop up the state of play as an innings begins: the run target when a
        side is chasing (limited-overs 2nd innings, or a Test 4th innings),
        or - in a Test non-chase innings - how far the batting side leads or
        trails on aggregate. No-op for a first innings with nothing to compare
        against. The push is a no-op in console mode.

        Returns:
            None
        """
        bt = self.batting_team

        if bt.batting_second:
            data = {"team": bt.name, "runsToWin": int(bt.target)}
            if self.overs:
                data["overs"] = int(self.overs)
            if self.dls_target:
                data["dls"] = True
            utilities.PushEvent("target", data)
            return

        if not self.is_test:
            return

        # Test, batting again but not chasing: lead/trail on aggregate so far
        opp = self.bowling_team
        if not (bt.innings_history or opp.innings_history):
            return
        diff = sum(i.score for i in bt.innings_history) - sum(
            i.score for i in opp.innings_history
        )
        if diff < 0:
            utilities.PushEvent("target", {"team": bt.name, "status": "trail", "diff": -diff})
        elif diff > 0:
            utilities.PushEvent("target", {"team": bt.name, "status": "lead", "diff": diff})

    def _CheckScoreMilestones(self):
        """
        Fire web pop-ups when the team total crosses a fresh multiple of 100
        (100/200/300/...) or the current unbroken partnership crosses a fresh
        multiple of 50 (50/100/150/...). Checked once per over; no-op in
        console mode (the pushes are no-ops when no channel is set).

        Returns:
            None
        """
        bt = self.batting_team

        # team total milestone: every 100 runs crossed, but show the exact
        # live score (not the rounded 100/200/300 threshold that triggered it)
        hundred = (int(bt.total_score) // 100) * 100
        if hundred >= 100 and hundred > self.team_score_milestone_shown:
            self.team_score_milestone_shown = hundred
            utilities.PushEvent(
                "team_score",
                {
                    "team": bt.name,
                    "score": int(bt.total_score),
                    "wickets": int(bt.wickets_fell),
                },
            )
            self._PushNextBatsmenPreview()

        # partnership milestone: every 50 runs for the current stand. A new
        # stand (a wicket has fallen) resets the tracked milestone.
        if bt.wickets_fell != self.partnership_tracked_wkt:
            self.partnership_tracked_wkt = bt.wickets_fell
            self.partnership_milestone_shown = 0
        if bt.wickets_fell < 10:
            runs_at_last_wkt = bt.fow[-1].runs if bt.fow else 0
            stand = int(bt.total_score) - int(runs_at_last_wkt)
            fifty = (stand // 50) * 50
            if fifty >= 50 and fifty > self.partnership_milestone_shown:
                self.partnership_milestone_shown = fifty
                pair = [p for p in (bt.current_pair or []) if p is not None]
                names = [p.name for p in pair]
                batsmen = [
                    {
                        "name": p.name,
                        "runs": int(p.runs),
                        "balls": int(p.balls),
                        "notOut": bool(p.status),
                    }
                    for p in pair
                ]
                utilities.PushEvent(
                    "partnership_milestone",
                    {"runs": fifty, "names": names, "batsmen": batsmen},
                )
                self._PushNextBatsmenPreview()

    def _PushNextBatsmenPreview(self):
        """
        Pop up a quick preview of the next few batsmen due in, with their
        photos - fired only at milestone/summary moments (a team-score or
        partnership milestone, or the periodic match-status check), never on
        every ball. Same not-out/not-already-in-the-middle filter
        AssignBatsman uses to pick the next man in, just read here as a
        preview rather than a selection.

        A no-op once the innings has actually ended (all out, overs
        exhausted, or the match already decided) - one of its callers is the
        wicket-fall handler, and the very wicket that ends the innings/match
        still leaves genuine not-yet-out reserves on the roster, who would
        otherwise get previewed as "next in" despite never actually batting.

        Returns:
            None
        """
        bt = self.batting_team
        if not self.status or bt.wickets_fell >= 10:
            return
        if self.overs and bt.total_balls >= self.overs * 6:
            return
        current_pair = bt.current_pair or []
        upcoming = [
            p.name for p in bt.team_array if p.status and p not in current_pair
        ][:3]
        if upcoming:
            utilities.PushEvent("next_batsmen", {"names": upcoming})

    # tier names in ascending order of difficulty - indices double as a
    # comparable "how bad is it" scale for _ClassifyChase's rate/resource mix
    _CHASE_TIERS = ["cruising", "on_track", "in_balance", "tough", "improbable"]

    def _ClassifyChase(self, rrr, crr, wickets_in_hand, batting_strength):
        """
        Rough difficulty tier for a run chase: how the required rate
        compares to the current rate (the "ask"), floored by the resources
        still available to answer it (wickets in hand and the average
        batting quality of everyone still to come, attr.batting is 1-10).

        The rate alone can look deceptively comfortable with wickets
        tumbling and only the tail left - a low ask means little with no
        one left to bat it out - so a thin/weak lower order puts a floor
        under how good the verdict can be, regardless of how easy the rate
        math looks.

        Returns:
            str: one of "cruising", "on_track", "in_balance", "tough",
            "improbable".
        """
        if rrr <= 0:
            rate_index = 0
        else:
            rate_ratio = rrr / max(crr, 0.5)
            if rate_ratio <= 0.85:
                rate_index = 0
            elif rate_ratio <= 1.05:
                rate_index = 1
            elif rate_ratio <= 1.4:
                rate_index = 2
            elif rate_ratio <= 2.0:
                rate_index = 3
            else:
                rate_index = 4

        if wickets_in_hand <= 1:
            floor_index = 3  # last-pair territory is never "cruising"
        elif wickets_in_hand <= 3 and batting_strength < 5:
            floor_index = 2
        elif wickets_in_hand <= 5 and batting_strength < 4:
            floor_index = 2
        else:
            floor_index = 0

        return self._CHASE_TIERS[max(rate_index, floor_index)]

    def _PushChaseAssessment(self):
        """
        Pop up a "how's the chase going" verdict while batting second in a
        limited-overs run chase - on every wicket (see UpdateDismissal) and
        every 10th completed over (see _PostOverDisplay). A no-op outside a
        live limited-overs chase (Test matches, first innings, or once the
        chase is already won/lost).

        Returns:
            None
        """
        bt = self.batting_team
        if not (self.overs and bt.batting_second and bt.target):
            return
        balls_left = self.overs * 6 - bt.total_balls
        if balls_left <= 0 or bt.wickets_fell >= 10:
            return
        runs_needed = bt.target - bt.total_score
        if runs_needed <= 0:
            return  # already won - the victory pop-up covers this moment

        crr = bt.GetCurrentRate()
        rrr = bt.GetRequiredRate()
        wickets_in_hand = 10 - bt.wickets_fell
        remaining = [p for p in bt.team_array if p.status]
        batting_strength = (
            sum(p.attr.batting for p in remaining) / len(remaining)
            if remaining
            else 0
        )

        tier = self._ClassifyChase(rrr, crr, wickets_in_hand, batting_strength)
        lines = {
            "cruising": commentary.commentary_chase_cruising,
            "on_track": commentary.commentary_chase_on_track,
            "in_balance": commentary.commentary_chase_in_balance,
            "tough": commentary.commentary_chase_tough,
            "improbable": commentary.commentary_chase_improbable,
        }[tier]
        utilities.PushEvent(
            "chase_update",
            {
                "team": bt.name,
                "tier": tier,
                "comment": Randomize(lines) % bt.name,
                "runsNeeded": int(runs_needed),
                "ballsLeft": int(balls_left),
                "crr": crr,
                "rrr": rrr,
                "wicketsInHand": int(wickets_in_hand),
            },
        )

    def _AdvanceSessionIfNeeded(self):
        """
        Advance to the next session (morning/lunch/afternoon/tea/evening,
        3 sessions of overs_per_session overs each) if the current session's
        over budget is used up; rolls over to the next day after the 3rd
        session, and ends the match in a draw if all match days are
        exhausted. Checked at the top of every over in a Test innings,
        never mid-over. Pushes a full scorecard snapshot to the web UI at
        every session break.

        Returns:
            bool: True if the current innings (and match) should stop now.
        """
        if self.overs_bowled_this_session < self.overs_per_session:
            return False

        self.overs_bowled_this_session = 0
        self.drinks_break_fired_this_session = False
        utilities.PushLiveInningsScorecard(self)

        if self.session < self.sessions_per_day:
            # session break (lunch/tea), same day continues
            interval = "Lunch" if self.session == 1 else "Tea"
            utilities.PushEvent("session_break", {"interval": interval})
            self.session += 1
            PrintInColor(
                "%s break! End of session %s, Day %s."
                % (interval, str(self.session - 1), str(self.day)),
                Style.BRIGHT,
            )
            if not self.autoplay:
                input("press enter to continue..")
            return False

        # 3rd session of the day just finished - stumps, roll over to the
        # next day
        finished_day = self.day
        self.session = 1
        self.day += 1
        match_ends_at_stumps = self.day > self.max_days

        # only pop up "Stumps!" when there's a next day to look forward to -
        # if this is the final day, the draw result covers it instead
        if not match_ends_at_stumps:
            PrintInColor("Stumps! End of Day %s." % str(finished_day), Style.BRIGHT)
            utilities.PushEvent(
                "stumps",
                {
                    "day": int(finished_day),
                    "team": self.batting_team.name,
                    "comment": Randomize(commentary.commentary_stumps),
                },
            )

        if match_ends_at_stumps:
            PrintInColor(
                "That's the end of the 5th day - the match ends in a draw.",
                Style.BRIGHT,
            )
            self.match_drawn = True
            self.status = False
            return True
        if not self.autoplay:
            input("press enter to continue..")
        return False

    def _ShouldDeclare(self, over):
        """
        Decide whether the batting captain declares this Test innings
        closed. Only offered for non-chase innings (self.declare_eligible).
        In the web GUI a persistent Declare button raises the confirmation
        prompt at the next over boundary (no score threshold); the console
        keeps the classic behavior of offering it every over once the
        innings passes 300.

        Returns:
            bool
        """
        if not self.declare_eligible or self.batting_team.wickets_fell >= 10:
            return False
        bt = self.batting_team
        if self.autoplay:
            if bt.total_score < 300:
                return False
            return self._AutoplayDeclareHeuristic(over)
        if utilities.IsWebMode():
            # only confirm when the GUI's Declare button was pressed
            if not utilities.ConsumeDeclareRequest():
                return False
        elif bt.total_score < 300:
            return False
        return (
            ChooseFromOptions(
                ["y", "n"],
                "Declare %s's innings at %s/%s (%s overs)?"
                % (
                    bt.name,
                    str(bt.total_score),
                    str(bt.wickets_fell),
                    str(BallsToOvers(bt.total_balls)),
                ),
                5,
            )
            == "y"
        )

    def _AutoplayDeclareHeuristic(self, over):
        """
        NOTE: a simple simulation heuristic for autoplay, not real
        Test-match tactics - just plausible enough to occasionally trigger.

        Returns:
            bool
        """
        bt = self.batting_team
        if bt.wickets_fell >= 7 and over >= 80:
            return True
        if bt.total_score >= 350 and bt.wickets_fell >= 5:
            return True
        if (self.max_days - self.day) <= 1 and bt.wickets_fell >= 6 and bt.total_score >= 200:
            return True
        return False

    def _ParRunRate(self):
        """
        The run rate a side would be expected to score at in this format -
        the yardstick the innings analysis judges a total against.

        Returns:
            float
        """
        if self.is_test:
            return 3.2
        if not self.overs:
            return 5.0
        if self.overs <= 10:
            return 8.5
        if self.overs <= 20:
            return 7.5
        if self.overs <= 30:
            return 6.0
        return 5.4

    def _InningsPhaseNotes(self, summary):
        """
        Read the shape of the innings - how it started, how the middle went
        and how it finished - from the per-over score/wicket history, which
        Team.StartBattingInnings resets so it only ever covers this innings.

        Returns:
            list[str]: narrative lines, in the order they happened.
        """
        bt = self.batting_team
        overs_done = sorted(bt.over_history.keys())
        # under 6 completed overs there aren't really three phases to talk about
        if len(overs_done) < 6:
            return []

        third = len(overs_done) // 3
        phases = [overs_done[:third], overs_done[third: 2 * third], overs_done[2 * third:]]

        notes = []
        prev_score = 0
        stats = []
        for chunk in phases:
            if not chunk:
                stats.append(None)
                continue
            end_score = int(bt.over_history[chunk[-1]])
            runs = end_score - prev_score
            prev_score = end_score
            wkts = sum(int(bt.over_wkt_history.get(o, 0)) for o in chunk)
            stats.append({"runs": runs, "wkts": wkts, "overs": len(chunk)})

        overall_rr = summary.score / (summary.balls / 6.0) if summary.balls else 0.0

        start, middle, end = stats
        if start:
            rr = start["runs"] / start["overs"]
            if start["wkts"] >= 3:
                notes.append(
                    Randomize(commentary.commentary_phase_early_wickets)
                    % str(start["wkts"])
                )
            elif start["wkts"] == 0 and rr >= overall_rr:
                notes.append(Randomize(commentary.commentary_phase_good_start))
            elif start["wkts"] == 0 or rr < overall_rr * 0.8:
                notes.append(Randomize(commentary.commentary_phase_slow_start))

        if middle:
            rr = middle["runs"] / middle["overs"]
            if middle["wkts"] >= 3:
                notes.append(
                    Randomize(commentary.commentary_phase_middle_wobble)
                    % str(middle["wkts"])
                )
            elif rr >= overall_rr * 1.1:
                notes.append(Randomize(commentary.commentary_phase_middle_rebuild))
            elif rr < overall_rr * 0.8:
                notes.append(Randomize(commentary.commentary_phase_middle_quiet))

        if end:
            rr = end["runs"] / end["overs"]
            if rr >= overall_rr * 1.35:
                notes.append(
                    Randomize(commentary.commentary_phase_death_surge)
                    % (str(end["runs"]), str(end["overs"]))
                )
            elif end["wkts"] >= 3:
                notes.append(
                    Randomize(commentary.commentary_phase_death_collapse)
                    % str(end["wkts"])
                )
            elif rr < overall_rr * 0.75:
                notes.append(Randomize(commentary.commentary_phase_death_quiet))
        return notes

    def _MatchMarginVerdict(self, summary, chase_won):
        """
        How the match was won or lost: a nail-biter, a routine result, or a
        thrashing. Judged on what was actually left at the end - wickets and
        balls to spare for a successful chase, the run margin for a failed
        one. Only meaningful once the chase has finished, so it returns None
        while the innings is still live.

        Returns:
            str or None
        """
        bt = self.batting_team
        if not (self.overs and bt.batting_second and bt.target):
            return None
        balls_left = self.overs * 6 - int(summary.balls)
        # still in progress (rain/interruption aside) - nothing to judge yet
        if not chase_won and summary.wickets < 10 and balls_left > 0:
            return None

        if chase_won:
            wickets_left = 10 - int(summary.wickets)
            if wickets_left <= 2 or balls_left <= 6:
                pool = commentary.commentary_margin_thriller
            elif wickets_left >= 7 or balls_left >= self.overs * 6 * 0.35:
                pool = commentary.commentary_margin_crushing
            else:
                pool = commentary.commentary_margin_comfortable
        else:
            margin = int(bt.target - 1 - summary.score)
            if margin <= 10:
                pool = commentary.commentary_margin_thriller
            # "big" scales with the format - 100 in a T20 is not 100 in an ODI
            elif margin >= max(40, int(bt.target * 0.35)):
                pool = commentary.commentary_margin_crushing
            else:
                pool = commentary.commentary_margin_comfortable
        return Randomize(pool)

    def _BuildInningsAnalysis(self, summary):
        """
        A read on the innings just finished: how the total rates for this
        format, the shape of the innings, who batted well, who disappointed,
        and how the bowling side fared. Structured data (not prose) where the
        UI can render it better as chips - see the "innings_analysis" event.

        Returns:
            dict or None: None if nothing meaningful was bowled.
        """
        if not summary or not summary.balls:
            return None

        bt = self.batting_team
        overs = summary.balls / 6.0
        run_rate = round(summary.score / overs, 2) if overs else 0.0
        par = self._ParRunRate()

        # headline: how does this total rate for the format?
        if run_rate >= par * 1.2:
            pool = commentary.commentary_innings_commanding
        elif run_rate >= par:
            pool = commentary.commentary_innings_solid
        elif run_rate >= par * 0.8:
            pool = commentary.commentary_innings_modest
        else:
            pool = commentary.commentary_innings_poor
        # the "bowled out"/"declared" rider is added by _BuildAnalysisSpeech,
        # which has the score to hand - adding it here too would say it twice
        headline = Randomize(pool) % str(run_rate)

        # a T20/ODI-style "runs per wicket" read on how well they batted deep
        notes = self._InningsPhaseNotes(summary)

        # --- batting: who stood up, who fell away ---
        faced = [b for b in summary.batting_card if b["balls"] > 0]
        by_runs = sorted(faced, key=lambda b: -b["runs"])
        # a meaningful score depends on the format's length
        good_mark = 25 if (self.overs and self.overs <= 20) else 35
        good = [b for b in by_runs if b["runs"] >= good_mark][:4]
        if not good:
            # nobody passed the bar (a low-scoring innings) - still name the
            # top contributors rather than showing an empty "did well" list
            good = [b for b in by_runs if b["runs"] >= 10][:2]
        # only the recognised batters (top 7) count as a disappointment - a
        # tailender out cheaply is not news
        top_order = [b for b in summary.batting_card[:7] if b["balls"] > 0]
        poor = sorted(
            [b for b in top_order if b["runs"] < 10 and b["dismissal"] != "not out"],
            key=lambda b: b["runs"],
        )[:4]

        def bat_entry(b):
            sr = round((b["runs"] / b["balls"]) * 100, 1) if b["balls"] else 0.0
            return {
                "name": b["name"],
                "runs": int(b["runs"]),
                "balls": int(b["balls"]),
                "strikeRate": float(sr),
                "notOut": b["dismissal"] == "not out",
            }

        # --- bowling: the standouts on the other side ---
        card = [b for b in summary.bowling_card if b["overs"] > 0]
        best = econ = expensive = None
        if card:
            wicket_takers = [b for b in card if b["wickets"] > 0]
            if wicket_takers:
                best = sorted(wicket_takers, key=lambda b: (-b["wickets"], b["runs"]))[0]
            # economy only means something over a real spell
            spells = [b for b in card if b["overs"] >= 2] or card
            econ = sorted(spells, key=lambda b: b["economy"])[0]
            expensive = sorted(spells, key=lambda b: -b["economy"])[0]
            # the same figures shouldn't be listed twice - the wicket-taker
            # already carries the praise, and in a one-bowler innings the
            # cheapest and dearest spell are the same spell
            if econ is best:
                econ = None
            if expensive is econ or expensive is best:
                expensive = None

        def bowl_entry(b):
            if b is None:
                return None
            return {
                "name": b["name"],
                "overs": float(b["overs"]),
                "runs": int(b["runs"]),
                "wickets": int(b["wickets"]),
                "economy": float(b["economy"]),
            }

        analysis = {
            "team": bt.name,
            "bowlingTeam": self.bowling_team.name,
            "score": int(summary.score),
            "wickets": int(summary.wickets),
            "overs": float(summary.overs),
            "runRate": run_rate,
            "headline": headline,
            "notes": notes,
            "batting": {
                "good": [bat_entry(b) for b in good],
                "poor": [bat_entry(b) for b in poor],
            },
            "bowling": {
                "best": bowl_entry(best),
                "economical": bowl_entry(econ),
                "expensive": bowl_entry(expensive),
            },
        }

        # chasing: say whether the target was reached, and by how far
        if bt.batting_second and bt.target:
            got_there = summary.score >= bt.target
            analysis["chase"] = {
                "target": int(bt.target),
                "successful": bool(got_there),
                "margin": int(abs(bt.target - 1 - summary.score)),
            }
            verdict = self._MatchMarginVerdict(summary, got_there)
            if verdict:
                analysis["verdict"] = verdict

        # turn all of the above into something a commentator would actually
        # say, and put a name and face to it
        analysis["speech"] = self._BuildAnalysisSpeech(analysis, summary)
        if self.commentators:
            analysis["commentator"] = Randomize(list(self.commentators))
        return analysis

    def _BuildAnalysisSpeech(self, analysis, summary):
        """
        Read the innings analysis out as a commentator would - flowing
        sentences naming the players, rather than a list of labelled figures.

        Args:
            analysis: the structured analysis built above.
            summary: the InningsSummary it was derived from.

        Returns:
            list[str]: paragraphs, in the order they should be spoken.
        """
        paras = []

        # 1. the opener, the headline read on the total, and the shape of it
        opening = Randomize(commentary.commentary_analysis_opener) % analysis["team"]
        opening += " " + analysis["headline"]
        if summary.declared:
            opening += " They declared on %s/%s." % (
                str(analysis["score"]), str(analysis["wickets"])
            )
        elif analysis["wickets"] >= 10:
            opening += " Bowled out for %s." % str(analysis["score"])
        paras.append(opening)

        if analysis["notes"]:
            paras.append(" ".join(analysis["notes"]))

        # 2. the batting - who stood up, who fell away
        def figures(b):
            return "%s%s off %s" % (
                str(b["runs"]), "*" if b["notOut"] else "", str(b["balls"])
            )

        bat_lines = []
        for b in analysis["batting"]["good"][:2]:
            bat_lines.append(
                Randomize(commentary.commentary_analysis_bat_praise)
                % (b["name"], figures(b))
            )
        for b in analysis["batting"]["poor"][:2]:
            bat_lines.append(
                Randomize(commentary.commentary_analysis_bat_fail)
                % (b["name"], figures(b))
            )
        if bat_lines:
            paras.append(" ".join(bat_lines))

        # 3. the bowling from the other side
        bowl = analysis["bowling"]
        bowl_lines = []
        if bowl["best"]:
            bowl_lines.append(
                Randomize(commentary.commentary_analysis_bowl_star)
                % (
                    bowl["best"]["name"],
                    "%s/%s" % (str(bowl["best"]["wickets"]), str(bowl["best"]["runs"])),
                )
            )
        if bowl["economical"]:
            bowl_lines.append(
                Randomize(commentary.commentary_analysis_bowl_econ)
                % (
                    bowl["economical"]["name"],
                    ("%.2f" % bowl["economical"]["economy"]),
                )
            )
        if bowl["expensive"]:
            bowl_lines.append(
                Randomize(commentary.commentary_analysis_bowl_expensive)
                % (
                    bowl["expensive"]["name"],
                    ("%.2f" % bowl["expensive"]["economy"]),
                )
            )
        if bowl_lines:
            paras.append(" ".join(bowl_lines))

        # 4. the chase result, then sign off
        chase = analysis.get("chase")
        if chase:
            if chase["successful"]:
                closing = "They got there, chasing down %s." % str(chase["target"])
            else:
                closing = "They fell %s run%s short of %s." % (
                    str(chase["margin"]),
                    "" if chase["margin"] == 1 else "s",
                    str(chase["target"]),
                )
            if analysis.get("verdict"):
                closing += " " + analysis["verdict"]
            paras.append(closing)
        else:
            paras.append(Randomize(commentary.commentary_analysis_signoff))
        return paras

    def BuildInningsSummary(self):
        """
        Snapshot the still-live batting/bowling figures into an
        InningsSummary, before Team.StartBattingInnings/StartBowlingInnings
        reset anything for the next innings. Used for Test-match multi-
        innings history and the web UI's innings-scorecard push.

        Returns:
            InningsSummary
        """
        batting = self.batting_team
        bowling = self.bowling_team

        batting_card = []
        for p in batting.team_array:
            if p.status is True:
                dismissal = "not out" if p.onfield else "DNB"
            else:
                dismissal = p.dismissal
            batting_card.append(
                {
                    "name": p.name,
                    "captain": bool(p.attr.iscaptain),
                    "keeper": bool(p.attr.iskeeper),
                    "dismissal": dismissal,
                    "runs": int(p.runs),
                    "balls": int(p.balls),
                }
            )

        bowling_card = []
        for bowler in bowling.bowlers:
            if bowler.balls_bowled == 0:
                continue
            overs = float(BallsToOvers(bowler.balls_bowled))
            economy = round(int(bowler.runs_given) / overs, 2) if overs > 0 else 0.0
            # per-wicket quality (batting rating + runs of everyone this
            # bowler dismissed) - snapshotted now, before StartBowlingInnings
            # resets wickets_taken for the next innings. Used by the Test
            # player-of-the-match impact score (see FindPlayerOfTheMatchTest);
            # harmless extra field for every other consumer of this dict.
            wicket_quality = sum(
                d.attr.batting * 1.5 + d.runs * 0.5 for d in bowler.wickets_taken
            )
            bowling_card.append(
                {
                    "name": bowler.name,
                    "overs": overs,
                    "maidens": int(bowler.maidens),
                    "runs": int(bowler.runs_given),
                    "wickets": int(bowler.wkts),
                    "economy": float(economy),
                    "ballsBowled": int(bowler.balls_bowled),
                    "wicketQuality": float(round(wicket_quality, 2)),
                }
            )

        fow = [
            {
                "wicket": int(f.wkt),
                "runs": int(f.runs),
                "player": f.player_dismissed.name,
                "overs": float(BallsToOvers(f.total_balls)),
            }
            for f in batting.fow
        ]

        return InningsSummary(
            innings_no=len(batting.innings_history) + 1,
            batting_team=batting.name,
            bowling_team=bowling.name,
            score=int(batting.total_score),
            wickets=int(batting.wickets_fell),
            balls=int(batting.total_balls),
            overs=float(BallsToOvers(batting.total_balls)),
            extras=int(batting.extras),
            declared=bool(batting.declared),
            batting_card=batting_card,
            bowling_card=bowling_card,
            fow=fow,
        )

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

        utilities.PushEvent(
            "new_bowler",
            {
                "name": bowler.name,
                "opening": over == 0,
                "caption": (
                    Randomize(commentary.commentary_opening_bowler_intro)
                    % bowler.name
                )
                if over == 0
                else None,
            },
        )
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
        total_wickets_in_over = 0
        ball = 1
        over_arr = []
        wides_this_over = 0
        noballs_this_over = 0

        # last over of a chase: pick this over's tension lines up front so no
        # two balls repeat one, and reset the per-ball tracker
        is_last_over_chase = bool(
            overs and over == overs - 1 and batting_team.batting_second
        )
        if is_last_over_chase:
            pool = commentary.commentary_last_over_tension
            self.last_over_phrases = random.sample(pool, min(5, len(pool)))
            self.tension_ball_shown = 0

        # loop for an over
        while ball <= 6:
            # if match ended
            if not self.status:
                break

            # crank up the tension, once per ball (a wide/no-ball re-enters the
            # loop on the same ball number, so don't pop the same line twice)
            if is_last_over_chase and ball != self.tension_ball_shown:
                self.tension_ball_shown = ball
                self._PushLastOverTension(ball)

            # check if dramatic over!
            if over_arr.count(6) > 2 or over_arr.count(4) > 2 and -1 in over_arr:
                PrintInColor(
                    Randomize(commentary.commentary_dramatic_over), Style.BRIGHT
                )

            if overs and over == overs - 1 and ball == 6:
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
                if not self.fast:
                    time.sleep(1)
            else:
                input("press enter to continue..")

            # generate run, updates runs and maiden status
            # FIXME dont pass over and player on strike, instead detect it!
            run = self.GenerateRun(over, player_on_strike)
            # run = GenerateRunNew(match, over, player_on_strike)

            # count wkts fell in the over
            if run == -1:
                total_wickets_in_over += 1

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
                extra_kind = self.UpdateExtras()
                if extra_kind == "wd":
                    wides_this_over += 1
                else:
                    noballs_this_over += 1
                # comment on too many extras
                extras_this_over = wides_this_over + noballs_this_over
                if extras_this_over > 2:
                    PrintInColor(
                        "%s extras in this over!" % str(extras_this_over), Style.BRIGHT
                    )
                # a big-screen warning the moment this over's extras first
                # reach 2 - fired once, not again for every extra ball after
                if extras_this_over == 2:
                    utilities.PushEvent(
                        "too_many_extras",
                        {
                            "bowler": bowler.name,
                            "team": bowling_team.name,
                            "count": extras_this_over,
                            "wides": wides_this_over,
                            "noballs": noballs_this_over,
                            "comment": Randomize(commentary.commentary_too_many_extras)
                            % bowler.name,
                        },
                    )
                total_runs_in_over += 1
                utilities.PushScorecard(self)
                utilities.PushLiveInningsScorecard(self)
                if self.status is False:
                    break

            # if not wide
            else:
                self.Ball(run)
                ball += 1
                if run != -1:
                    total_runs_in_over += run
                utilities.PushScorecard(self)
                utilities.PushLiveInningsScorecard(self)
                if self.status is False:
                    break

            if self.overs and batting_team.total_balls == (self.overs * 6):
                PrintInColor("End of innings", Fore.LIGHTCYAN_EX)
                # The chasing side must NOT break out here: the batting-second
                # branch below is what settles the result (status, commentary
                # and the "match decided" pop-up). Breaking early skipped all
                # of that whenever a chase simply ran out of balls with wickets
                # still standing, so a failed chase never announced itself.
                if batting_team.wickets_fell > 0 and not batting_team.batting_second:
                    # update last partnership
                    last_fow = batting_team.fow[-1].runs
                    last_partnership_runs = batting_team.total_score - last_fow
                    last_partnership = Partnership(
                        batsman_dismissed=pair[0],
                        batsman_onstrike=pair[1],
                        runs=last_partnership_runs,
                    )
                    batting_team.partnerships.append(last_partnership)
                    if not self.autoplay:
                        input("press enter to continue")
                    break

            # check if 1st innings over
            # if all out first innings
            if not batting_team.batting_second:
                if batting_team.wickets_fell == 10:
                    PrintInColor(
                        Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX
                    )
                    # "bowled out in under 1.2x the innings overs" framing
                    # only makes sense for a fixed-length innings with runs on
                    # the board (an all-out-for-a-duck would divide by zero)
                    if self.overs and batting_team.total_score > 0:
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
                    if not self.autoplay:
                        input("press enter to continue...")
                    break

            # batting second
            elif batting_team.batting_second:
                if self.overs and batting_team.total_balls >= (self.overs * 6):
                    # update last partnership
                    self.UpdateLastPartnership()
                    self.status = False
                    # tied scores go to a super over, not a win/loss - the
                    # decisive-moment popup only fires on an actual result
                    is_tie = batting_team.total_score == batting_team.target - 1
                    # if won in the last ball
                    if batting_team.total_score >= batting_team.target:
                        PrintInColor(
                            Randomize(commentary.commentary_won_last_ball)
                            % batting_team.name,
                            Style.BRIGHT,
                        )
                        self._PushChaseDecided(chasing_won=True)
                    else:
                        PrintInColor(
                            Randomize(commentary.commentary_lost_chasing)
                            % (batting_team.name, bowling_team.name),
                            Style.BRIGHT,
                        )
                        if not is_tie:
                            self._PushChaseDecided(chasing_won=False)
                    if not self.autoplay:
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
                    self._PushChaseDecided(chasing_won=True)
                    self.status = False
                    self.UpdateLastPartnership()
                    if not self.autoplay: input("press enter to continue...")
                    break
                # if all out first innings
                if batting_team.wickets_fell == 10:
                    PrintInColor(
                        Randomize(commentary.commentary_all_out), Fore.LIGHTRED_EX
                    )
                    # tied scores go to a super over, not a loss
                    if batting_team.total_score != batting_team.target - 1:
                        self._PushChaseDecided(chasing_won=False)
                    if not self.autoplay: input("press enter to continue...")
                    break

        # the loop only reaches ball == 7 by exhausting "while ball <= 6"
        # naturally (all 6 legal deliveries bowled); anything less means it
        # was cut short by a break - the innings/match ending mid-over (e.g.
        # the last wicket falling on ball 3) - so the over was never finished
        over_completed = ball > 6

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
        elif total_runs_in_over == 0 and over_completed:
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
            
        # update batting team over history
        #nrr = batting_team.GetCurrentRate()
        batting_team.over_history[over] = batting_team.total_score
        batting_team.over_wkt_history[over] = total_wickets_in_over

        # refresh the web UI's side-pane scorecard; no-op outside web mode
        utilities.PushScorecard(self)
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

        # this legal delivery consumes any pending free hit (a no-ball earlier
        # in the over set it; wides/no-balls don't reach Ball(), so it survives
        # them until a legal ball is bowled)
        is_free_hit = self.free_hit
        self.free_hit = False

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
            dismissal = self.GenerateDismissal(free_hit=is_free_hit)
            # free hit: anything but a run out is not out
            if dismissal is None:
                PrintInColor(
                    Randomize(commentary.commentary_free_hit_survived),
                    Fore.LIGHTGREEN_EX,
                )
                run = 0  # treat as a dot; the batsman lives on
                break
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
            elif dismissal.startswith("c&b") or dismissal.startswith("c "):
                # caught: the umpire gives it out on the appeal, and the
                # batsman can review it for a missing edge
                PrintInColor(
                    Randomize(commentary.commentary_caught_appeal), Fore.LIGHTRED_EX
                )

                # if match has no DRS, do not go into this
                if self.drs is False:
                    self.UpdateDismissal(dismissal)
                    return

                if self.CheckDRS(kind="caught"):
                    run = 0  # no edge - the batsman survives
                    used_drs = True
                    break
                # an edge confirmed on review is a catch behind the wicket, so
                # the keeper always takes it
                if self.review_upheld:
                    dismissal = self._RewriteCatchToKeeper(dismissal)
                self.UpdateDismissal(dismissal)
                return
            elif "runout" in dismissal or "st " in dismissal:
                # run-outs and stumpings: the umpire either gives it out on
                # the spot or refers it upstairs, and the third umpire's
                # verdict can overturn it
                kind = "runout" if "runout" in dismissal else "stumped"
                if not self._CheckThirdUmpire(dismissal, kind):
                    run = 0  # third umpire reprieve - the batsman survives
                    used_drs = True
                    break
                self.UpdateDismissal(dismissal)
                return
            else:
                self.UpdateDismissal(dismissal)
                return

        # no wicket was rolled, but on a dot ball the fielding side
        # occasionally has a shout of their own - a plausible LBW/catch
        # appeal the umpire turned down, reviewable on the bowling team's
        # own DRS quota (separate from the batting side's)
        if run == 0:
            reprieve_dismissal = self._MaybeBowlingReview()
            if reprieve_dismissal is not None:
                self.UpdateDismissal(reprieve_dismissal)
                return

        # appropriate commentary for 4s and 6s
        if run == 4:
            utilities.PushEvent("four")
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
            utilities.PushEvent("six")
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

        # back-to-back boundaries for the batsman on strike (after the FOUR!/
        # SIX! commentary above, so the streak card lands on top of it)
        self._UpdateBoundaryStreak(on_strike, run)

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
        # a wicket while no legal ball has been faced yet = first ball of the
        # innings (checked before the ball count below is bumped)
        is_first_ball = batting_team.total_balls == 0

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

        # LBW is the umpire's call, so pop up the umpire giving the decision;
        # run-outs and stumpings already showed their third-umpire pop-up
        # before UpdateDismissal was reached; everything else (bowled/caught)
        # gets the generic stumps animation
        if "lbw" in dismissal:
            utilities.PushEvent("lbw", {"umpire": self.umpire})
        elif "runout" in dismissal or "st " in dismissal:
            pass  # third-umpire flow already showed the decision
        else:
            utilities.PushEvent("wicket")

        # a bowler's wicket off the very first ball of the innings - a big
        # double bill of the bowler and the departing batsman (a run-out
        # isn't the bowler's wicket, so it's left out)
        if is_first_ball and "runout" not in dismissal:
            utilities.PushEvent(
                "first_ball_wicket",
                {
                    "batter": player_dismissed.name,
                    "bowler": bowler.name,
                    "text": Randomize(commentary.commentary_first_ball_wicket),
                },
            )

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

        # hat-trick / N-wickets-in-N-balls detection. A run-out never reaches
        # here with a live streak (it isn't a bowler-credited wicket, so
        # _BowlerWicketStreak stops at it), so this only ever fires for the
        # bowler's own dismissals.
        streak = self._BowlerWicketStreak(bowler)
        # a "he's on a hat-trick" tension line promises a next delivery from
        # this bowler - not valid if this wicket was the innings' 10th and
        # last: there's no next ball left for him to bowl here.
        innings_over = batting_team.wickets_fell == 10
        if streak == 2 and not innings_over:
            # one more and it's a hat-trick - flag the tension before the
            # very next ball is bowled
            PrintInColor(Randomize(commentary.commentary_on_a_hattrick), bowling_team.color)
            utilities.PushEvent(
                "achievement",
                {
                    "name": bowler.name,
                    "type": "hattrick_building",
                    "text": "ON A HAT-TRICK!",
                },
            )
        elif streak >= 3:
            if streak == 3:
                bowler.hattricks += 1
                text = "HAT-TRICK!"
                line = Randomize(commentary.commentary_hattrick)
                achievement_type = "hattrick"
            else:
                text = "%s IN %s BALLS!" % (str(streak), str(streak))
                line = Randomize(commentary.commentary_multi_wicket_streak) % streak
                achievement_type = "hattrick_streak"
            utilities.PushEvent(
                "achievement",
                {"name": bowler.name, "type": achievement_type, "text": text,
                 "streak": streak},
            )
            PrintInColor(line, bowling_team.color)
            if not self.autoplay:   input("press enter to continue..")
        if bowler.wkts == 3:
            PrintInColor("Third wkt for %s !" % bowler.name, bowling_team.color)
            if not self.autoplay:   input("press enter to continue..")
        # check if bowler got 5 wkts
        if bowler.wkts == 5:
            achievement_data = {
                "name": bowler.name, "type": "bowling", "text": "5 wickets!"
            }
            if bowler.attr.iscaptain:
                achievement_data["captainComment"] = Randomize(
                    commentary.commentary_captain_leading
                )
            utilities.PushEvent("achievement", achievement_data)
            PrintInColor("That's 5 Wickets for %s !" % bowler.name, bowling_team.color)
            PrintInColor(Randomize(commentary.commentary_fifer), bowling_team.color)
            if not self.autoplay:   input("press enter to continue..")
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
            breakthrough_data = {
                "runs": int(partnership.runs),
                "comment": Randomize(commentary.commentary_breakthrough)
                % bowling_team.name,
            }
            if "runout" in dismissal:
                fielder_name = dismissal.replace("runout", "").strip()
                fielder = next(
                    (
                        p
                        for p in bowling_team.team_array
                        if GetShortName(p.name) == fielder_name
                    ),
                    None,
                )
                breakthrough_data["kind"] = "runout"
                breakthrough_data["fielder"] = fielder.name if fielder else fielder_name
            else:
                breakthrough_data["kind"] = "bowler"
                breakthrough_data["bowler"] = bowler.name

            # is this breakthrough actually worth much? Reuses the same
            # chase-difficulty read as the "how's the chase going" pop-up
            # (_ClassifyChase) - if the chasing side is still cruising/on
            # track even after losing this stand, the wicket is too little,
            # too late to matter. Only meaningful for a live limited-overs
            # chase; a first-innings or Test stand has no such signal.
            if (
                self.overs
                and batting_team.batting_second
                and batting_team.target
                and batting_team.wickets_fell < 10
            ):
                crr = batting_team.GetCurrentRate()
                rrr = batting_team.GetRequiredRate()
                wickets_in_hand = 10 - batting_team.wickets_fell
                remaining = [p for p in batting_team.team_array if p.status]
                batting_strength = (
                    sum(p.attr.batting for p in remaining) / len(remaining)
                    if remaining
                    else 0
                )
                tier = self._ClassifyChase(rrr, crr, wickets_in_hand, batting_strength)
                if tier in ("cruising", "on_track"):
                    breakthrough_data["tooLateComment"] = (
                        Randomize(commentary.commentary_breakthrough_too_late)
                        % batting_team.name
                    )

            utilities.PushEvent("partnership_broken", breakthrough_data)

        self.PrintCommentaryDismissal(dismissal)
        # show score
        self.CurrentMatchStatus()
        # how's the chase going? (wicket-triggered; the every-10-overs
        # trigger lives in _PostOverDisplay). Skipped if this very wicket
        # already decided the match (all out) - _PushChaseDecided covers that
        if self.status and batting_team.wickets_fell < 10:
            self._PushChaseAssessment()
        # a new batsman only walks out if there is still an innings to bat:
        # not when the wicket fell on the last ball of the innings, and not
        # when it ended the match (GetNextBatsman itself handles all-out)
        overs_done = bool(
            self.overs and batting_team.total_balls >= self.overs * 6
        )
        if self.status and not overs_done:
            self.GetNextBatsman()
        if not self.autoplay:   input("press enter to continue")
        self.DisplayScore()
        if not self.is_test:
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

        PrintListFormatted(data_to_print, 0 if self.fast else 0.01, logger)

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
        
        # plot the graph (not meaningful for a Test innings that can run
        # to 100+ overs across multiple days)
        # temporarily disabled
        # if not self.is_test:
        #     utilities.PlotOversBarGraph(batting_team.over_history, batting_team.over_wkt_history, "RR Graph")
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

        # run array: [-1(wkt), 0, 1, 2, 3, 4, 5, 6]
        run_array = [-1, 0, 1, 2, 3, 4, 5, 6]

        # Test batting: watchful and risk-averse - mostly dots, singles and
        # twos (occupying the crease, rotating strike), and even rarer to
        # get out than to find a boundary. This is the neutral baseline for
        # an average batter against an average bowler - the batter/bowler
        # skill matchup below adjusts it further either way.
        prob_test = [0.025, 0.40, 0.40, 0.15, 0.01, 0.0, 0.015, 0.0]

        prob = venue.run_prob_t20
        if self.is_test:
            prob = prob_test
        elif overs == 50:
            # if ODI, override the prob
            prob = venue.run_prob

        # death over situation
        prob_death = [0.2, 0.2, 0, 0, 0, 0.2, 0.2, 0.2]

        # in the death overs, increase prob of boundaries and wickets
        # (no fixed "last over" concept in a Test innings)
        if overs and over == overs - 1:
            prob = prob_death

        if batting_team.batting_second:
            # if required rate is too much, try to go big! (meaningless
            # without a fixed overs count, so Test's chase skips this)
            if (
                overs
                and batting_team.total_balls > 0
                and batting_team.GetRequiredRate() - batting_team.GetCurrentRate()
                >= 2.0
                and over <= overs - 2
            ):
                prob = prob_death

        # FIXME:
        # if initial overs, play carefully based on RR
        # if death overs, try to go big
        # but, if batsman is poor and bowler is skilled, more chances of getting out
        if bowler.attr.bowling - player_on_strike.attr.batting >= 4:
            prob = [0.25, 0.20, 0.20, 0.15, 0.05, 0.05, 0.05, 0.05]

        # endgame: batsmen only run what's needed to win - with 1 to win
        # never a 2 or 3, with 2 to win never a 3 (boundaries still count in
        # full). Applied last so no distribution override above (death overs,
        # skill matchup) can sneak the impossible outcomes back in; the
        # remaining probabilities are renormalized rather than replaced, so
        # the batting character of the situation is otherwise preserved.
        if batting_team.batting_second and batting_team.target:
            needed = batting_team.target - batting_team.total_score
            if needed in (1, 2):
                prob = [
                    0.0 if (r in (2, 3) and r > needed) else p
                    for r, p in zip(run_array, prob)
                ]
                total = sum(prob)
                prob = [p / total for p in prob]

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
            elif towin <= 20 or (overs and over == overs - 1):
                self.ShowHighlights()
                if towin == 1:
                    PrintInColor("Match tied!", Fore.LIGHTGREEN_EX)
                elif overs:
                    PrintInColor(
                        "To win: %s from %s"
                        % (str(towin), str(overs * 6 - batting_team.total_balls)),
                        Style.BRIGHT,
                    )
                else:
                    PrintInColor("To win: %s" % str(towin), Style.BRIGHT)
        return

    def CheckDRS(self, kind="lbw"):
        """
        Offer the batting side a review of an on-field OUT decision (an LBW or
        a catch). Each team gets Team.drs_chances reviews per innings. A
        successful review (the on-field call is overturned) costs nothing; an
        unsuccessful one (the on-field call was right) burns a chance.

        Args:
            kind: "lbw" or "caught" - picks the review commentary.

        Returns:
            bool: True if the decision is overturned (batsman NOT out).
        """
        team = self.batting_team
        pair = team.current_pair
        # set true only when a review was actually taken and the on-field OUT
        # stood (i.e. an edge/impact was confirmed) - read by the catch flow
        self.review_upheld = False

        if team.drs_chances <= 0:
            PrintInColor(
                Randomize(commentary.commentary_lbw_nomore_drs), Fore.LIGHTRED_EX
            )
            return False

        opt = ChooseFromOptions(
            ["y", "n"], "DRS? %s chance(s) left" % (str(team.drs_chances)), 200000
        )
        if opt == "n":
            PrintInColor(
                Randomize(commentary.commentary_lbw_drs_not_taken), Fore.LIGHTRED_EX
            )
            return False

        PrintInColor(
            Randomize(commentary.commentary_lbw_drs_taken)
            % (GetSurname(pair[0].name), GetSurname(pair[1].name)),
            Fore.LIGHTGREEN_EX,
        )
        PrintInColor("Decision pending...", Style.BRIGHT)
        utilities.PushEvent("drs_pending", {"kind": kind})
        if not self.fast:
            time.sleep(5)

        overturned = random.choice([True, False])
        utilities.PushEvent("drs_result", {"out": not overturned, "kind": kind})

        if overturned:
            # on-field call was wrong: the batsman survives and, because the
            # review succeeded, the team keeps the chance
            if kind == "caught":
                PrintInColor(
                    Randomize(commentary.commentary_caught_overturned),
                    Fore.LIGHTGREEN_EX,
                )
            else:
                # both lists describe a successful LBW review (missing the
                # stumps, or bat/impact outside the line)
                PrintInColor(
                    Randomize(
                        commentary.commentary_lbw_overturned
                        + commentary.commentary_lbw_edged_outside
                    ),
                    Fore.LIGHTGREEN_EX,
                )
            PrintInColor(
                "Review successful - %s keep their %s review(s)."
                % (team.name, str(team.drs_chances)),
                Style.BRIGHT,
            )
        else:
            # on-field call was right: a chance is burnt (and, for a catch,
            # an edge was confirmed - so it's a catch behind the wicket)
            self.review_upheld = True
            if kind == "caught":
                PrintInColor(
                    Randomize(commentary.commentary_caught_decision_stays)
                    % self.umpire,
                    Fore.LIGHTRED_EX,
                )
            else:
                PrintInColor(
                    Randomize(commentary.commentary_lbw_decision_stays) % self.umpire,
                    Fore.LIGHTRED_EX,
                )
            team.drs_chances -= 1
            PrintInColor(
                "Review lost - %s have %s review(s) left."
                % (team.name, str(team.drs_chances)),
                Style.BRIGHT,
            )
        return overturned

    def _MaybeBowlingReview(self):
        """
        On a dot ball, occasionally the fielding side has a shout of their
        own - an LBW or catch appeal the on-field umpire turned down - which
        they can review using their own Team.drs_chances, separate from the
        batting side's quota. A no-op when DRS isn't enabled for this match
        or the bowling team has no chances left to spend.

        Returns:
            str or None: the dismissal string if the review overturns the
            not-out call (the batter is out after all); None if no appeal
            happened, or the not-out call stood.
        """
        if not self.drs or self.bowling_team.drs_chances <= 0:
            return None
        if random.random() > 0.04:  # a close shout on roughly 1 in 25 dot balls
            return None

        kind = random.choice(["lbw", "caught"])
        bowler = self.bowling_team.current_bowler
        # the appeal itself, turned down on the field - before the bowling
        # side's own review of that not-out call
        self._PushAppealDrama(bowler, "catch" if kind == "caught" else kind, out=False)
        PrintInColor(
            Randomize(commentary.commentary_bowling_appeal) % self.umpire,
            Fore.LIGHTRED_EX,
        )
        if not self._CheckBowlingReview(kind):
            return None
        return self._GenerateBowlingReviewDismissal(kind)

    def _CheckBowlingReview(self, kind):
        """
        Mirror of CheckDRS, but the FIELDING side reviewing a NOT OUT call
        (an LBW or catch appeal the umpire turned down), spending the
        bowling team's own drs_chances. Unlike CheckDRS - where an overturn
        means the batter SURVIVES - here an overturn means the not-out call
        was wrong and the batter IS out after all.

        Args:
            kind: "lbw" or "caught".

        Returns:
            bool: True if the review overturns the not-out call (batter out).
        """
        team = self.bowling_team

        opt = ChooseFromOptions(
            ["y", "n"],
            "%s review the not-out call? %s chance(s) left"
            % (team.name, str(team.drs_chances)),
            200000,
        )
        if opt == "n":
            return False

        PrintInColor("Decision pending...", Style.BRIGHT)
        utilities.PushEvent("drs_pending", {"kind": kind})
        if not self.fast:
            time.sleep(5)

        overturned = random.choice([True, False])
        utilities.PushEvent("drs_result", {"out": overturned, "kind": kind})

        if overturned:
            PrintInColor(
                Randomize(commentary.commentary_bowling_review_success) % team.name,
                Fore.LIGHTRED_EX,
            )
            PrintInColor(
                "Review successful - %s keep their %s review(s)."
                % (team.name, str(team.drs_chances)),
                Style.BRIGHT,
            )
        else:
            team.drs_chances -= 1
            PrintInColor(
                Randomize(commentary.commentary_bowling_review_fail) % team.name,
                Fore.LIGHTGREEN_EX,
            )
            PrintInColor(
                "Review lost - %s have %s review(s) left."
                % (team.name, str(team.drs_chances)),
                Style.BRIGHT,
            )
        return overturned

    def _GenerateBowlingReviewDismissal(self, kind):
        """
        Build the dismissal string for a bowling-side review that overturns
        a not-out call, crediting the same fielding stats GenerateDismissal
        would for an equivalent LBW/catch dismissal.

        Args:
            kind: "lbw" or "caught".

        Returns:
            str: the dismissal string.
        """
        bowling_team = self.bowling_team
        bowler = bowling_team.current_bowler
        if kind == "lbw":
            return "lbw %s" % GetShortName(bowler.name)

        fielder = Randomize(bowling_team.team_array)
        fielder.catches += 1
        if fielder.catches == 5:
            utilities.PushEvent(
                "achievement",
                {"name": fielder.name, "type": "fielding", "text": "5 catches!"},
            )
        if fielder == bowler:
            return "c&b %s" % GetShortName(bowler.name)
        if fielder.attr.iskeeper:
            return "c +%s b %s" % (GetShortName(fielder.name), GetShortName(bowler.name))
        return "c %s b %s" % (GetShortName(fielder.name), GetShortName(bowler.name))

    def _CheckThirdUmpire(self, dismissal, kind):
        """
        Resolve a run-out or stumping. The on-field umpire either gives it out
        on the spot or refers it upstairs; a referral shows the big-screen
        replay and green/red lights, and the third umpire's verdict can
        overturn the dismissal. `kind` is "runout" or "stumped".

        Returns:
            bool: True if the batsman is OUT, False if reprieved (not out).
        """
        referred = random.choice([True, False])
        if not referred:
            # given out on the spot
            PrintInColor(Randomize(commentary.commentary_given_out), Fore.LIGHTRED_EX)
            utilities.PushEvent(
                "third_umpire", {"stage": "out", "kind": kind, "umpire": self.umpire}
            )
            return True

        # referred to the third umpire
        referral = (
            commentary.commentary_referred_stumped
            if kind == "stumped"
            else commentary.commentary_referred_runout
        )
        PrintInColor(Randomize(referral), Style.BRIGHT)
        utilities.PushEvent("third_umpire", {"stage": "referred", "kind": kind})
        # green/red lights, just like DRS
        utilities.PushEvent("drs_pending", {"kind": kind})
        if not self.fast:
            time.sleep(4)
        out = random.choice([True, False])
        utilities.PushEvent("drs_result", {"out": out, "kind": kind})
        if out:
            PrintInColor(
                Randomize(commentary.commentary_third_umpire_out), Fore.LIGHTRED_EX
            )
        else:
            PrintInColor(
                Randomize(commentary.commentary_third_umpire_not_out),
                Fore.LIGHTGREEN_EX,
            )
            # a reprieve must un-credit the stat GenerateDismissal already
            # awarded, so an overturned dismissal leaves no phantom on record
            self._UndoDismissalStat(dismissal, kind)
        return out

    def _UndoDismissalStat(self, dismissal, kind):
        """
        Reverse the fielding stat GenerateDismissal credited when a run-out or
        stumping is overturned upstairs.

        Returns:
            None
        """
        if kind == "stumped":
            keeper = self.bowling_team.keeper
            keeper.stumpings = max(0, keeper.stumpings - 1)
        else:  # runout: fielder named in "runout <shortname>"
            name = dismissal.replace("runout", "").strip()
            fielder = next(
                (
                    p
                    for p in self.bowling_team.team_array
                    if GetShortName(p.name) == name
                ),
                None,
            )
            if fielder is not None:
                fielder.runouts = max(0, fielder.runouts - 1)

    def _RewriteCatchToKeeper(self, dismissal):
        """
        A caught dismissal whose edge was confirmed on review is a catch behind
        the wicket, so credit it to the keeper. Rewrites the dismissal string
        to "c +<keeper> b <bowler>" and moves the catch off whoever
        GenerateDismissal first credited (a fielder, or the bowler on a c&b).
        Already-keeper catches are left untouched.

        Args:
            dismissal: The generated catch dismissal string.

        Returns:
            str: The (possibly rewritten) dismissal string.
        """
        keeper = self.bowling_team.keeper
        bowler = self.bowling_team.current_bowler
        # already a keeper catch: nothing to change
        if dismissal.startswith("c +"):
            return dismissal

        if dismissal.startswith("c&b"):
            original = bowler
        else:  # "c <fielder> b <bowler>"
            name = dismissal.split(" b ")[0][2:].strip()
            original = next(
                (
                    p
                    for p in self.bowling_team.team_array
                    if GetShortName(p.name) == name
                ),
                None,
            )
        if original is keeper:
            return dismissal

        # move the catch from the original catcher to the keeper
        if original is not None:
            original.catches = max(0, original.catches - 1)
        keeper.catches += 1
        return "c +%s b %s" % (GetShortName(keeper.name), GetShortName(bowler.name))

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

    # offered alongside the real players whenever a pick can fall back to the
    # engine's own choice - see _PickFromPlayers
    AUTO_SELECT = "Auto-select"

    def _PickFromPlayers(self, players, msg, allow_auto=True):
        """
        Ask the player to pick one of `players`, one option per player so the
        web UI renders them as buttons instead of a number to type in. Names
        are unique within a squad (ValidateMatchTeams enforces it), so the
        chosen label maps back to exactly one player.

        Args:
            players: candidate Player objects.
            msg: the prompt to show.
            allow_auto: include an "Auto-select" option that returns None,
                letting the caller apply its own default.

        Returns:
            Player, or None if there were no candidates or auto-select was
            chosen.
        """
        if not players:
            return None
        by_label = {p.name: p for p in players}
        options = list(by_label.keys())
        if allow_auto:
            options.append(self.AUTO_SELECT)
        chosen = ChooseFromOptions(options, msg, 200000)
        return by_label.get(chosen)

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
                # else pick bowler (one option per bowler, so the web UI
                # renders them as buttons rather than a number to type)
                else:
                    bowler = self._PickFromPlayers(temp, "Pick next bowler")
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
            utilities.PushEvent("new_batsman", {"name": pair[ind].name})
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

        if self.autoplay:
            # when autoplay is enabled, Randomize returns a player object
            # so assign it directly instead of treating it as a string
            batsman = Randomize(remaining_batsmen)
        else:
            # one option per batsman, so the web UI renders them as buttons
            batsman = self._PickFromPlayers(remaining_batsmen, "Choose next batsman")
            if batsman is None and remaining_batsmen:
                # auto-select: next man in the batting order
                batsman = remaining_batsmen[0]

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

        # rain revised the chase target: the result compares team2 with the
        # D/L target, not with team1's total
        if self.dls_target:
            self._CalculateResultDLS()
            return

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

    def _CalculateResultDLS(self):
        """
        Result of a rain-shortened match that was still played to a finish:
        the chase is judged against the Duckworth-Lewis revised target
        (self.dls_target) rather than team1's raw total.

        Returns:
            None
        """
        team1, team2 = self.team1, self.team2
        target = self.dls_target
        score2 = int(team2.total_score)
        result = Result(team1=team1, team2=team2)

        if score2 >= target:
            result.winner = team2
            margin = 10 - team2.wickets_fell
            balls_left = self.overs * 6 - team2.total_balls
            result.result_str = "%s won by %s wicket%s" % (
                team2.name,
                str(margin),
                "" if margin == 1 else "s",
            )
            if balls_left > 0:
                result.result_str += " with %s ball%s left" % (
                    str(balls_left),
                    "" if balls_left == 1 else "s",
                )
            result.result_str += " (D/L method)"
        elif score2 == target - 1:
            result.winner = None
            result.result_str = "Match Tied (D/L method)"
        else:
            result.winner = team1
            margin = target - 1 - score2
            result.result_str = "%s won by %s run%s (D/L method)" % (
                team1.name,
                str(margin),
                "" if margin == 1 else "s",
            )

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

    def _PlayerImpactScore(self, p):
        """
        How much this player actually contributed to the winning team's win
        - not just raw runs or wickets. Batting rewards runs scored at a
        good strike rate, with a bonus for finishing the innings not out
        (closed the game out rather than just padding a total). Bowling
        rewards each wicket in proportion to the quality of the batter
        dismissed - their batting rating and how many runs they'd already
        made - so 5 wickets against tailenders who never got going is worth
        less than 4 wickets that broke through a well-set top order, plus a
        bonus for bowling economically (enough overs bowled to mean
        something). Summing both halves for the same player is what lets a
        genuine all-rounder's contribution outweigh a one-dimensional spell.

        Returns:
            float: impact score for this player (higher = bigger contribution).
        """
        batting_score = 0.0
        if p.balls > 0:
            # a quick contribution counts for more than a slow one of the
            # same size; a stodgy strike rate below 100 gets no bonus, just
            # the raw runs
            sr_bonus = max(0.0, (p.strikerate - 100) / 100.0) * p.runs * 0.5
            batting_score = p.runs + sr_bonus
            if p.status and p.runs >= 20:
                batting_score += 10  # unbeaten and made it count

        bowling_score = 0.0
        if p.balls_bowled > 0:
            for dismissed in p.wickets_taken:
                # a wicket is worth more the better the batter (their rating)
                # and the more damage they'd already done (their runs) -
                # removing a set, dangerous batsman matters far more than a
                # tailender who nicks off cheaply
                bowling_score += 8 + dismissed.attr.batting * 1.5 + dismissed.runs * 0.5
            if p.balls_bowled >= 12:  # at least 2 overs - a real sample
                bowling_score += max(0.0, 7.0 - p.eco) * 3

        return batting_score + bowling_score

    def FindPlayerOfTheMatch(self):
        """
        Find the player of the match: the winning team's biggest contributor
        to the win, by impact score (see _PlayerImpactScore) rather than
        raw runs/wickets.

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

        best_player = max(
            self.winner.team_array, key=lambda p: self._PlayerImpactScore(p)
        )

        self.result.mom = best_player
        msg = "Player of the match: %s (%s)" % (
            best_player.name,
            best_player.GetMomStat(),
        )
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)

    def FindPlayerOfTheMatchTest(self):
        """
        Test player-of-the-match: aggregates each player's batting/bowling
        figures across their (up to 2) innings_history entries, then picks
        the winning team's biggest contributor by the same impact-score idea
        as the limited-overs version (_PlayerImpactScore) - runs weighted by
        strike rate and a not-out bonus for batting; wickets weighted by the
        quality of the batter dismissed (via each innings' bowling_card
        "wicketQuality", snapshotted in BuildInningsSummary) plus an economy
        bonus for bowling. Silently skips (no MOM) for a draw or if the
        winning team never got to bat - both real possibilities in a Test.

        Returns:
            None
        """
        if self.result is None or self.result.winner is None:
            return
        winner = self.result.winner
        loser = self.team2 if winner is self.team1 else self.team1

        if not winner.innings_history:
            return

        bat_totals = {}
        for inn in winner.innings_history:
            for b in inn.batting_card:
                entry = bat_totals.setdefault(
                    b["name"], {"runs": 0, "balls": 0, "notOut": False}
                )
                entry["runs"] += b["runs"]
                entry["balls"] += b["balls"]
                if b["dismissal"] == "not out":
                    entry["notOut"] = True

        # a team's own bowling figures for an innings get attached to the
        # OPPONENT's innings_history entry (BuildInningsSummary snapshots
        # bowling_card from self.bowling_team, and Play() appends the whole
        # summary to self.batting_team.innings_history) - so the winner's
        # own bowlers are on the loser's innings_history, not the winner's.
        bowl_totals = {}
        for inn in loser.innings_history:
            for bw in inn.bowling_card:
                entry = bowl_totals.setdefault(
                    bw["name"],
                    {"wickets": 0, "runs": 0, "ballsBowled": 0, "wicketQuality": 0.0},
                )
                entry["wickets"] += bw["wickets"]
                entry["runs"] += bw["runs"]
                entry["ballsBowled"] += bw.get("ballsBowled", 0)
                entry["wicketQuality"] += bw.get("wicketQuality", 0.0)

        if not bat_totals and not bowl_totals:
            return

        def impact(name):
            score = 0.0
            bat = bat_totals.get(name)
            if bat and bat["balls"] > 0:
                sr = (bat["runs"] / bat["balls"]) * 100
                sr_bonus = max(0.0, (sr - 100) / 100.0) * bat["runs"] * 0.5
                score += bat["runs"] + sr_bonus
                if bat["notOut"] and bat["runs"] >= 20:
                    score += 10
            bowl = bowl_totals.get(name)
            if bowl and bowl["ballsBowled"] > 0:
                score += 8 * bowl["wickets"] + bowl["wicketQuality"]
                overs = bowl["ballsBowled"] / 6.0
                eco = bowl["runs"] / overs if overs > 0 else 0.0
                if bowl["ballsBowled"] >= 12:
                    score += max(0.0, 7.0 - eco) * 3
            return score

        name = max(set(bat_totals) | set(bowl_totals), key=impact)

        stat_parts = []
        bat = bat_totals.get(name)
        if bat and bat["runs"] > 0:
            stat_parts.append(
                "scored %s%s runs in the match"
                % (str(bat["runs"]), "*" if bat["notOut"] else "")
            )
        bowl = bowl_totals.get(name)
        if bowl and bowl["wickets"] > 0:
            stat_parts.append(
                "took %s wickets for %s runs in the match"
                % (str(bowl["wickets"]), str(bowl["runs"]))
            )
        stat = " and ".join(stat_parts) if stat_parts else "was the standout performer"

        self.result.mom_name = name
        self.result.mom_stat = stat
        msg = "Player of the match: %s (%s)" % (name, stat)
        PrintInColor(msg, Style.BRIGHT)
        self.logger.info(msg)

    def Toss(self):
        """
        Perform the toss. Team1's captain calls it; whoever calls correctly
        wins the toss and chooses to bat or bowl first, and the other side
        gets what's left.

        Returns:
            None
        """
        logger = self.logger
        t1, t2 = self.team1, self.team2

        PrintInColor("Toss..", Style.BRIGHT)
        PrintInColor(
            "We have the captains %s from %s and %s from %s in the middle"
            % (t1.captain.name, t1.name, t2.captain.name, t2.name),
            Style.BRIGHT,
        )
        PrintInColor("%s is going to flip the coin" % t2.captain.name, Style.BRIGHT)

        # the two captains out in the middle, about to toss
        utilities.PushEvent(
            "toss",
            {
                "stage": "intro",
                "captains": [
                    {"name": t1.captain.name, "team": t1.name},
                    {"name": t2.captain.name, "team": t2.name},
                ],
                "flipper": t2.captain.name,
                "caller": t1.captain.name,
            },
        )

        # team1's captain calls the coin
        if self.autoplay:
            call = Randomize(["Heads", "Tails"])
        else:
            call = ChooseFromOptions(
                ["Heads", "Tails"], "%s, Heads or Tails?" % t1.captain.name, 5
            )
        coin = Randomize(["Heads", "Tails"])
        # the coin in the air
        utilities.PushEvent(
            "toss", {"stage": "flip", "team1": t1.name, "team2": t2.name}
        )
        PrintInColor(
            "%s called %s.. and it's %s!" % (t1.captain.name, call, coin),
            Style.BRIGHT,
        )

        # a correct call wins team1 the toss, otherwise team2 wins
        toss_winner = t1 if call == coin else t2
        toss_loser = t2 if toss_winner is t1 else t1
        PrintInColor(
            "%s have won the toss!" % toss_winner.name, toss_winner.color
        )
        utilities.PushEvent(
            "toss",
            {
                "stage": "result",
                "team": toss_winner.name,
                "captain": toss_winner.captain.name,
                "call": call,
                "coin": coin,
            },
        )

        # the toss winner elects to bat or bowl first - but only the user's
        # own side (team1 - see GetMatchInfo's "Select your team") actually
        # gets asked; if the opposition wins it, their call is just randomized
        # and announced, with no "what will it be, skipper?" prompt shown
        user_decides = not self.autoplay and toss_winner is self.team1
        if user_decides:
            utilities.PushEvent(
                "toss",
                {
                    "stage": "decision",
                    "team": toss_winner.name,
                    "captain": toss_winner.captain.name,
                },
            )
            decision = ChooseFromOptions(
                ["Bat", "Bowl"],
                "%s, do you want to bat or bowl first?" % toss_winner.captain.name,
                5,
            )
        else:
            decision = Randomize(["Bat", "Bowl"])

        if decision == "Bat":
            toss_winner.batting_second = False
            toss_loser.batting_second = True
        else:
            toss_winner.batting_second = True
            toss_loser.batting_second = False

        msg = "%s have elected to %s first" % (toss_winner.name, decision.lower())
        PrintInColor(msg, toss_winner.color)
        logger.info(msg)
        utilities.PushEvent(
            "toss",
            {
                "stage": "elected",
                "team": toss_winner.name,
                "captain": toss_winner.captain.name,
                "decision": decision,
            },
        )

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
        if self.autoplay:
            drs_opted = "n"
        else:
            drs_opted = ChooseFromOptions(["y", "n"], "Do you need DRS for this match? ", 5)
        if drs_opted == "y":
            PrintInColor("D.R.S opted", Style.BRIGHT)
            self.drs = True
            if not self.autoplay:
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

        # let the player know why there's a pause between the playing XI and
        # the toss (the autoplay name checks below can take a while)
        PrintInColor("Validating teams, please wait...", Style.BRIGHT)
        utilities.PushEvent("validating_teams", {})

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

        # note: opener onstrike/onfield assignment now happens in
        # Team.StartBattingInnings(), called at the top of every innings
        # (needed so a team's *second* Test innings also starts clean)

        # check if players have numbers, else assign randomly - drawn from
        # a shrinking per-team pool (excluding numbers already set in the
        # data) so two players on the same team can never end up with the
        # same number. size=1 draws on their own (as this used to do, one
        # per player) can't prevent duplicates across separate calls, no
        # matter the replace setting.
        import numpy as np

        for t in [self.team1, self.team2]:
            used_numbers = {p.no for p in t.team_array if p.no is not None}
            available_numbers = [n for n in range(100) if n not in used_numbers]
            for player in t.team_array:
                if player.no is None:
                    # plain int, not a numpy scalar, so it pickles cleanly
                    # into save files (see functions/SaveGame.py)
                    player.no = int(np.random.choice(available_numbers))
                    available_numbers.remove(player.no)
        print("Validated teams")
        
        # additional validation of player names if autoplay (a roster-QA
        # check that hits the network). Skipped for tournament-simulated
        # matches, which run autoplay purely for auto-decisions and must not
        # make dozens of blocking web requests per fixture.
        ValidPlayers = True
        if self.autoplay and not self.skip_name_check:
            print ("Autoplay enabled, validating player names...")
            for t in [self.team1, self.team2]:
                for player in t.team_array:
                    if not is_name_valid(player.name):
                        print("Invalid player name: %s" % player.name)
                        ValidPlayers = False
        if not ValidPlayers:
            Error_Exit("One or more player names are invalid!")
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
            str: "wd" or "nb" - which kind of extra this was, so the caller
            can track a per-over wide/no-ball breakdown.
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
            # the next legal delivery is a free hit - a limited-overs rule only,
            # Test cricket has no free hit
            if not self.is_test:
                self.free_hit = True
                PrintInColor(
                    Randomize(commentary.commentary_free_hit), Fore.LIGHTGREEN_EX
                )
                utilities.PushEvent("free_hit", {"umpire": self.umpire})

        return extra

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

            # approaching a milestone: one run short (49 / 99 / 199)
            nervous = {49: "fifty", 99: "hundred", 199: "double hundred"}
            if p.runs in nervous and p.nervous_at != p.runs:
                p.nervous_at = p.runs
                utilities.PushEvent(
                    "approaching",
                    {
                        "name": p.name,
                        "text": Randomize(commentary.commentary_approaching_milestone),
                        "milestone": nervous[p.runs],
                    },
                )

            # first fifty
            if p.runs >= 50 and p.fifty == 0:
                p.fifty += 1
                achievement_data = {"name": p.name, "type": "batting", "text": "50!"}
                if p.attr.iscaptain:
                    achievement_data["captainComment"] = Randomize(
                        commentary.commentary_captain_leading
                    )
                utilities.PushEvent("achievement", achievement_data)
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
                achievement_data = {"name": p.name, "type": "batting", "text": "100!"}
                if p.attr.iscaptain:
                    achievement_data["captainComment"] = Randomize(
                        commentary.commentary_captain_leading
                    )
                utilities.PushEvent("achievement", achievement_data)
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
                achievement_data = {"name": p.name, "type": "batting", "text": "200!"}
                if p.attr.iscaptain:
                    achievement_data["captainComment"] = Randomize(
                        commentary.commentary_captain_leading
                    )
                utilities.PushEvent("achievement", achievement_data)
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

            # the crowd rises at each 50-run milestone (50/100/150/200/...),
            # with a line that names the ground
            applause = (p.runs // 50) * 50
            if applause >= 50 and applause > p.applause_at:
                p.applause_at = applause
                PrintInColor(
                    Randomize(commentary.commentary_milestone_applause)
                    % self.venue.name,
                    batting_team.color,
                )
        if not self.autoplay:
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

    def _ShouldRiskSecondRun(self):
        """
        A realistic read on whether the batsmen would actually turn back for
        a second right now, for the run-out drama build-up. A single that
        already wins the match is never risked for two - there is nothing to
        gain. Otherwise, while chasing, the odds track the required rate
        against the current one: push harder for twos when quick runs are
        needed, hold back when the chase is already comfortable. Outside a
        chase (batting first, or a Test) there is no such pressure to read,
        so it falls back to a flat, everyday chance.

        Returns:
            bool
        """
        bt = self.batting_team
        chance = 0.45

        if self.overs and bt.batting_second and bt.target:
            runs_needed = bt.target - bt.total_score
            if runs_needed <= 1:
                return False
            rrr = bt.GetRequiredRate()
            crr = bt.GetCurrentRate()
            if rrr > 0:
                # ahead of the rate: nothing to gamble for; behind it: push harder
                ratio = rrr / max(crr, 0.5)
                chance = min(0.75, max(0.15, 0.45 * ratio))

        return random.random() < chance

    def _PushRunOutDrama(self, fielder):
        """
        Play out the attempted run itself before the third umpire's verdict:
        the single being taken, then - if it's actually worth the risk (see
        _ShouldRiskSecondRun) - the batsmen turning back for a second, and
        finally the fielder's throw at the stumps. Purely a big-screen
        narrative build-up; the actual out/not-out decision still goes
        through _CheckThirdUmpire exactly as before.

        Args:
            fielder: the Player who fields the ball and throws.

        Returns:
            None
        """
        batting_team = self.batting_team
        pair = batting_team.current_pair
        # BatsmanOut always dismisses whoever is on strike (see Pair.py) - the
        # non-striker is their running partner for this call
        striker = next((x for x in pair if x.onstrike), None)
        partner = next((x for x in pair if not x.onstrike), None)
        if striker is None or partner is None:
            return

        pace = 0 if self.fast else 1.2

        def push(stage, comment, **extra):
            utilities.PushEvent(
                "run_out_drama",
                dict(
                    {
                        "stage": stage,
                        "batsmen": [striker.name, partner.name],
                        "team": batting_team.name,
                        "comment": comment,
                    },
                    **extra
                ),
            )
            PrintInColor(comment, batting_team.color)
            if pace:
                time.sleep(pace)

        # 1. the single itself
        push(
            "single",
            Randomize(commentary.commentary_runout_call_single)
            % (GetSurname(striker.name), GetSurname(partner.name)),
        )

        # 2. do they turn back for a second? Realistic to the match
        # situation (see _ShouldRiskSecondRun) - this is where a routine run
        # becomes a genuine race against the fielder
        going_for_two = self._ShouldRiskSecondRun()
        if going_for_two:
            push(
                "second",
                Randomize(commentary.commentary_runout_call_second)
                % (GetSurname(striker.name), GetSurname(partner.name)),
            )

        # 3. the throw - fielder rather than batsmen from here on
        comment = Randomize(commentary.commentary_runout_throw) % GetSurname(fielder.name)
        utilities.PushEvent(
            "run_out_drama",
            {
                "stage": "throw",
                "fielder": fielder.name,
                "team": self.bowling_team.name,
                "comment": comment,
            },
        )
        PrintInColor(comment, self.bowling_team.color)
        if pace:
            time.sleep(pace)

    def _PushStumpingDrama(self, keeper, bowler):
        """
        Play out the stumping itself before the third umpire's verdict: the
        batsman drawn out of his ground by flight or turn, then the
        keeper's lightning-quick removal of the bails. Purely a big-screen
        narrative build-up; the actual out/not-out decision still goes
        through _CheckThirdUmpire exactly as before.

        Args:
            keeper: the wicketkeeper.
            bowler: the bowler who drew the batsman forward.

        Returns:
            None
        """
        batting_team = self.batting_team
        pair = batting_team.current_pair
        striker = next((x for x in pair if x.onstrike), None)
        if striker is None:
            return

        pace = 0 if self.fast else 1.2

        comment = Randomize(commentary.commentary_stumped_advance) % (
            GetSurname(striker.name), GetSurname(bowler.name)
        )
        utilities.PushEvent(
            "stumping_drama",
            {
                "stage": "advance",
                "batsman": striker.name,
                "bowler": bowler.name,
                "team": batting_team.name,
                "comment": comment,
            },
        )
        PrintInColor(comment, batting_team.color)
        if pace:
            time.sleep(pace)

        comment = Randomize(commentary.commentary_stumped_whip) % GetSurname(keeper.name)
        utilities.PushEvent(
            "stumping_drama",
            {
                "stage": "whip",
                "keeper": keeper.name,
                "team": self.bowling_team.name,
                "comment": comment,
            },
        )
        PrintInColor(comment, self.bowling_team.color)
        if pace:
            time.sleep(pace)

    def _PushAppealDrama(self, bowler, kind, out):
        """
        Show a big-screen appeal pop-up - the bowler's face, the umpire's
        face, and a flavoured line - the moment the fielding side appeals
        for an LBW or catch. Purely a narrative build-up; the on-field call
        it reports is whatever the caller has already decided (GenerateDismissal
        always gives it out on the initial appeal, _MaybeBowlingReview always
        turns it down), any subsequent DRS review still runs unchanged.

        Args:
            bowler: the Player who bowled the delivery.
            kind: "lbw" or "catch".
            out: True if the on-field umpire is giving it out on the appeal.

        Returns:
            None
        """
        if kind == "lbw":
            pool = (
                commentary.commentary_appeal_lbw_out
                if out
                else commentary.commentary_appeal_lbw_not_out
            )
        else:
            pool = (
                commentary.commentary_appeal_catch_out
                if out
                else commentary.commentary_appeal_catch_not_out
            )
        comment = Randomize(pool) % self.umpire

        utilities.PushEvent(
            "appeal_drama",
            {
                "kind": kind,
                "out": out,
                "bowler": bowler.name,
                "umpire": self.umpire,
                "comment": comment,
            },
        )
        PrintInColor(comment, Fore.LIGHTRED_EX if out else Fore.LIGHTGREEN_EX)
        if not self.fast:
            time.sleep(1.2)

    def GenerateDismissal(self, free_hit=False):
        """
        Generate a random mode of dismissal.

        Args:
            free_hit: When True (a free-hit delivery), only a run out can
                dismiss - any other mode returns None (batsman not out), and
                the check happens before any fielding stat is credited.

        Returns:
            str: The dismissal string, or None if the batsman survives a free
                hit.
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

        # on a free hit only a run out counts - bail before any stat is
        # credited so a survived free hit leaves the fielding figures untouched
        if free_hit and dismissal != "runout":
            return None

        # generate dismissal string
        if dismissal == "lbw" or dismissal == "b":
            dismissal_str = "%s %s" % (dismissal, GetShortName(bowler.name))
            if dismissal == "lbw":
                # the appeal itself, played out before the DRS check that
                # may still follow (see Ball(), unchanged)
                self._PushAppealDrama(bowler, "lbw", out=True)
        elif dismissal == "st":
            # stumped
            dismissal_str = "st +%s b %s" % (
                GetShortName(keeper.name),
                GetShortName(bowler.name),
            )
            keeper.stumpings += 1
            if keeper.stumpings == 5:
                utilities.PushEvent(
                    "achievement",
                    {"name": keeper.name, "type": "fielding", "text": "5 stumpings!"},
                )
            # the batsman drawn out of his ground, then the bails whipped
            # off, played out before the third umpire's verdict (which
            # _CheckThirdUmpire still handles, unchanged)
            self._PushStumpingDrama(keeper, bowler)

        elif dismissal == "c":
            fielder.catches += 1
            if fielder.catches == 5:
                utilities.PushEvent(
                    "achievement",
                    {"name": fielder.name, "type": "fielding", "text": "5 catches!"},
                )
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
            # the appeal itself, played out before the DRS review that may
            # still follow (see Ball(), unchanged)
            self._PushAppealDrama(bowler, "catch", out=True)
        elif dismissal == "runout":
            fielder.runouts += 1
            dismissal_str = "runout %s" % (GetShortName(fielder.name))
            # the attempted run itself, played out before the third umpire's
            # verdict (which _CheckThirdUmpire still handles, unchanged)
            self._PushRunOutDrama(fielder)

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
        # required rate isn't a meaningful concept in a Test chase (see
        # Team.GetRequiredRate) - don't even bother computing it
        rr = None if self.is_test else batting_team.GetRequiredRate()

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
        if batting_team.batting_second and self.status and not self.is_test:
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
        # required rate isn't a meaningful concept in a Test chase (see
        # Team.GetRequiredRate) - don't even bother computing it
        rr = None if self.is_test else batting_team.GetRequiredRate()

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
        if batting_team.batting_second and not self.is_test:
            msg += " Required Rate: %s\n" % str(rr)

        print(msg)
        logger.info(msg)
        # a periodic status summary is exactly the "some summary happens"
        # moment for a Next In preview - not every ball, just here
        self._PushNextBatsmenPreview()
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

        # if chasing (required-run-rate framing doesn't fit a Test chase,
        # where GetRequiredRate() is intentionally a no-op - skip rather
        # than show misleading "gettable"/"gone case" commentary there)
        elif not self.is_test:
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

        PrintListFormatted(data_to_print, 0 if self.fast else 0.01, logger)
        print(char * 45)
        logger.info(char * 45)
        if not self.autoplay:
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
        PrintListFormatted(data_to_print, 0 if self.fast else 0.1, None)
        utilities.PushPlayingXI(self)

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
        PrintListFormatted(data_to_print, 0 if self.fast else 0.01, logger)

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

        PrintListFormatted(data_to_print, 0 if self.fast else 0.01, logger)
        print("-" * 43)
        logger.info("-" * 43)
        if not self.autoplay:
            input("Press Enter to continue..")

    def MatchSummaryTest(self):
        """
        Print the Test match summary: one score line per team, joined with
        " & " when a team batted twice, sourced from innings_history since
        live Team fields only reflect whichever innings was played last.
        Tolerates a team having 0 or 1 completed innings (a draw can mean
        the second team never batted at all).

        Returns:
            None
        """
        logger = self.logger
        ch = "-"
        result = self.result

        msg = "%s Test Match Summary %s" % (ch * 10, ch * 10)
        print(msg)
        logger.info(msg)

        msg = "%s vs %s, at %s" % (result.team1.name, result.team2.name, self.venue.name)
        print(msg)
        logger.info(msg)

        print(ch * 45)
        logger.info(ch * 45)

        msg = result.result_str
        PrintInColor(msg, Style.BRIGHT)
        logger.info(msg)

        print(ch * 45)
        logger.info(ch * 45)

        for team in [self.team1, self.team2]:
            if not team.innings_history:
                msg = "%s: did not bat" % team.name
            else:
                lines = [
                    "%s/%s%s (%s)"
                    % (
                        str(inn.score),
                        str(inn.wickets),
                        "d" if inn.declared else "",
                        str(inn.overs),
                    )
                    for inn in team.innings_history
                ]
                msg = "%s: %s" % (team.name, " & ".join(lines))
            print(msg)
            logger.info(msg)

        print(ch * 45)
        logger.info(ch * 45)
        if not self.autoplay:
            input("Press Enter to continue..")
