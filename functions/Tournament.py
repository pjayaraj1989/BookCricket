"""
Tournament / series play built on top of the single-match engine.

A Tournament owns only plain data (team/venue specs, fixtures, standings and
per-player aggregates) - never live Match/Team/Player objects - so it pickles
small and safe and can be resumed between matches. For each fixture it builds
fresh teams from the roster files, plays (or silently simulates) one match via
the normal engine, then folds that match's result and scorecards into the
standings and aggregates.

Points: win 2, tie/draw/no-result 1, loss 0. For limited-overs series, teams
level on points are separated by net run rate (all-out innings count the full
over quota, as in real cricket). Two teams play a fixed number of matches;
three or more play a single round robin, then the top two contest a final.
"""
import contextlib
import os
import sys

import functions.utilities as utilities
from functions.utilities import (
    PrintInColor,
    ChooseFromOptions,
    BallsToOvers,
    GetShortName,
    Randomize,
)
from functions.helper import FillAttributes
from functions.Initiate import (
    LoadTeam, LoadVenueByName, AssignWeather, BuildMatch,
    ListLeagues, LeagueTeamNames, VenueChoices,
)
from web.io_bridge import get_channel, set_channel
from colorama import Style, Fore

WIN_POINTS = 2
DRAW_POINTS = 1


def _overs_to_balls(overs):
    """Convert an a.b overs figure (3.4 = 3 overs 4 balls) back to balls."""
    whole = int(overs)
    return whole * 6 + int(round((overs - whole) * 10))


class Tournament:
    def __init__(self, **kwargs):
        attrs = {
            "name": "Series",
            "is_test": False,
            "overs": None,            # limited-overs count (None for Test)
            "fast": False,
            "autoplay": False,        # simulate the whole thing (CLI/CI/tests)
            # team specs identify a roster without pickling it:
            #   {"league": str, "name": str, "is_test": bool}
            "team_specs": [],
            "venue_country": None,
            "venue_name": None,
            "series_matches": 3,      # 2-team series length (ignored for 3+)
            # fixtures: {"round", "home", "away", "kind": league|final,
            #            "played", "result": <summary dict>}
            "fixtures": [],
            "fixture_index": 0,
            "standings": {},          # team name -> stats dict
            "batting_agg": {},        # player name -> batting tallies
            "bowling_agg": {},        # player name -> bowling tallies
            "player_team": {},        # player name -> team name (for display)
            "finished": False,
            "champion": None,
            # save/resume
            "save_id": None,
            "save_enabled": False,
            "save_client_id": None,
            "resuming": False,
        }
        self = FillAttributes(self, attrs, kwargs)

    # ---- team names -------------------------------------------------------
    @property
    def team_names(self):
        return [s["name"] for s in self.team_specs]

    def _load_team(self, name):
        spec = next(s for s in self.team_specs if s["name"] == name)
        return LoadTeam(spec["league"], spec["name"], spec.get("is_test", False))

    # ---- fixtures ---------------------------------------------------------
    def generate_fixtures(self):
        """Build the league fixture list (the final, for 3+ teams, is added
        once the league table is known)."""
        names = self.team_names
        self.fixtures = []
        if len(names) == 2:
            a, b = names
            for i in range(self.series_matches):
                home, away = (a, b) if i % 2 == 0 else (b, a)
                self.fixtures.append(self._fixture(i + 1, home, away, "league"))
        else:
            rnd = 0
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    rnd += 1
                    self.fixtures.append(
                        self._fixture(rnd, names[i], names[j], "league")
                    )
        self._init_standings()

    def _fixture(self, rnd, home, away, kind):
        return {
            "round": rnd, "home": home, "away": away, "kind": kind,
            "played": False, "result": None,
        }

    def _init_standings(self):
        for name in self.team_names:
            self.standings[name] = {
                "team": name, "played": 0, "won": 0, "lost": 0, "tie": 0,
                "points": 0, "for_runs": 0, "for_balls": 0,
                "against_runs": 0, "against_balls": 0,
            }

    @property
    def is_round_robin(self):
        return len(self.team_names) > 2

    # ---- the main loop ----------------------------------------------------
    def play(self, ScriptPath):
        """Run the tournament to completion, resumably. Between fixtures the
        player can view standings/stats or quit (autoplay just plays on)."""
        self.ScriptPath = ScriptPath
        if not self.resuming and not self.fixtures:
            self.generate_fixtures()

        while True:
            # once the league phase is complete, seed the final before doing
            # anything else - done here (idempotently) rather than only after
            # a match so a crash in that gap still resumes into the final
            if self.is_round_robin and self._league_complete() and not self._final_exists():
                self._maybe_seed_final()

            if self.fixture_index >= len(self.fixtures):
                break

            if not self.autoplay:
                while True:
                    action = self._between_matches_menu()
                    if action == "standings":
                        self.show_standings()
                        continue
                    if action == "stats":
                        self.show_stats(final=False)
                        continue
                    if action == "quit":
                        PrintInColor(
                            "Series paused. It will be waiting to resume.",
                            Style.BRIGHT,
                        )
                        return
                    # "play" or "simulate": remember the choice and go
                    self._next_sim = (action == "simulate")
                    break

            self._play_fixture(self.fixtures[self.fixture_index])
            self.fixture_index += 1
            self._save()

        self._finalize()

    def _league_complete(self):
        return all(f["played"] for f in self.fixtures if f["kind"] == "league")

    def _final_exists(self):
        return any(f["kind"] == "final" for f in self.fixtures)

    def _maybe_seed_final(self):
        if self._final_exists():
            return
        table = self.standings_table()
        if len(table) < 2:
            return
        first, second = table[0]["team"], table[1]["team"]
        self.fixtures.append(
            self._fixture(len(self.fixtures) + 1, first, second, "final")
        )
        PrintInColor(
            "League stage done! The final is %s vs %s." % (first, second),
            Style.BRIGHT,
        )
        utilities.PushEvent(
            "series", {"stage": "final_set", "teamA": first, "teamB": second}
        )
        self._save()

    # ---- one fixture ------------------------------------------------------
    def _between_matches_menu(self):
        fx = self.fixtures[self.fixture_index]
        label = "FINAL" if fx["kind"] == "final" else "Match %s" % str(fx["round"])
        PrintInColor(
            "%s next: %s vs %s" % (label, fx["home"], fx["away"]), Style.BRIGHT
        )
        options = ["Play this match", "Simulate this match", "Show standings",
                   "Show tournament stats", "Quit (resume later)"]
        choice = ChooseFromOptions(options, "What next?", 5)
        return {
            "Play this match": "play",
            "Simulate this match": "simulate",
            "Show standings": "standings",
            "Show tournament stats": "stats",
            "Quit (resume later)": "quit",
        }.get(choice, "play")

    def _play_fixture(self, fx):
        simulate = True
        if not self.autoplay:
            # the between-matches menu already picked play vs simulate, but on
            # a resume (or autoplay) default to simulate
            simulate = getattr(self, "_next_sim", True)
        self._next_sim = True

        home = self._load_team(fx["home"])
        away = self._load_team(fx["away"])
        venue = LoadVenueByName(self.venue_country, self.venue_name)
        AssignWeather(venue, announce=not simulate)

        label = "FINAL" if fx["kind"] == "final" else "Match %s" % str(fx["round"])
        PrintInColor(
            "%s: %s vs %s at %s" % (label, fx["home"], fx["away"], self.venue_name),
            Fore.LIGHTCYAN_EX,
        )
        utilities.PushEvent(
            "series",
            {"stage": "match_start", "label": label, "home": fx["home"],
             "away": fx["away"]},
        )

        match = BuildMatch(
            home, away, venue, self.overs, self.is_test,
            fast=self.fast or simulate, autoplay=simulate or self.autoplay,
            announce=not simulate,
        )
        # tournament fixtures never write single-match resume saves - the
        # tournament owns resume
        match.save_enabled = False

        # a match the user chose to simulate (not a whole-tournament autoplay)
        # should still hand a tie to the player: defer the super over so it's
        # played interactively/visibly after the silent simulation.
        interactive_super = simulate and not self.autoplay and not self.is_test
        match.defer_super_over = interactive_super

        if simulate or self.autoplay:
            # a full-screen "simulating" overlay stays up for the whole (silent)
            # simulation; the match_result event clears it. Pushed before the
            # channel is detached, and acked immediately by the browser so it
            # never blocks. Console just gets a line.
            PrintInColor("Simulating %s..." % label, Style.BRIGHT)
            utilities.PushEvent(
                "series",
                {"stage": "simulating", "label": label, "home": fx["home"],
                 "away": fx["away"]},
            )
            with _silent_play():
                match.PlayMatch(self.ScriptPath)
        else:
            match.PlayMatch(self.ScriptPath)

        # a simulated match that finished level: play the decider now, in the
        # open (channel attached, not silenced), so the player gets the super over
        if (
            interactive_super
            and match.result is not None
            and match.result.winner is None
            and match.result.result_str.startswith("Match Tied")
        ):
            self._play_deferred_super_over(match, fx)

        self._record_result(fx, match)

    def _play_deferred_super_over(self, match, fx):
        """Play the super over for a simulated match that ended level, out loud
        (the sim itself was silent). Updates match.result with the winner."""
        # clear the "simulating" overlay and announce the tie
        utilities.PushEvent(
            "series",
            {"stage": "tie", "home": fx["home"], "away": fx["away"]},
        )
        PrintInColor(
            "%s vs %s ended level - it's a SUPER OVER!" % (fx["home"], fx["away"]),
            Style.BRIGHT,
        )
        match.autoplay = False        # play it interactively
        match.defer_super_over = False
        winner = match._PlaySuperOver()
        if winner is not None:
            match.result.winner = winner
            match.result.result_str = "Match Tied - %s won the Super Over" % winner.name

    def _record_result(self, fx, match):
        result = match.result
        winner = result.winner.name if result and result.winner else None
        home, away = fx["home"], fx["away"]
        loser = None
        if winner:
            loser = away if winner == home else home
        result_str = result.result_str if result else "No result"

        # standings
        for name in (home, away):
            self.standings[name]["played"] += 1
        if winner:
            self.standings[winner]["won"] += 1
            self.standings[winner]["points"] += WIN_POINTS
            self.standings[loser]["lost"] += 1
        else:
            for name in (home, away):
                self.standings[name]["tie"] += 1
                self.standings[name]["points"] += DRAW_POINTS

        # net run rate inputs (limited overs only) + player aggregates
        if not self.is_test:
            self._accumulate_nrr(match)
        self._accumulate_players(match)

        fx["played"] = True
        fx["result"] = {
            "label": "FINAL" if fx["kind"] == "final" else "Match %s" % str(fx["round"]),
            "home": home, "away": away, "winner": winner,
            "result_str": result_str,
        }
        PrintInColor("Result: %s" % result_str, Style.BRIGHT)
        utilities.PushEvent(
            "series",
            {"stage": "match_result", "home": home, "away": away,
             "winner": winner, "resultStr": result_str},
        )

    def _accumulate_nrr(self, match):
        quota_balls = int(match.overs) * 6 if match.overs else 0
        for inn in match.innings_log:
            bat = inn.batting_team
            bowl = inn.bowling_team
            if bat not in self.standings or bowl not in self.standings:
                continue
            balls = quota_balls if inn.wickets >= 10 and quota_balls else inn.balls
            self.standings[bat]["for_runs"] += inn.score
            self.standings[bat]["for_balls"] += balls
            self.standings[bowl]["against_runs"] += inn.score
            self.standings[bowl]["against_balls"] += balls

    def _accumulate_players(self, match):
        for inn in match.innings_log:
            for b in inn.batting_card:
                name = b["name"]
                self.player_team.setdefault(name, inn.batting_team)
                agg = self.batting_agg.setdefault(
                    name, {"runs": 0, "balls": 0, "innings": 0, "outs": 0,
                           "hs": 0, "fifties": 0, "hundreds": 0}
                )
                if b["balls"] > 0 or b["dismissal"] not in ("DNB", "not out"):
                    agg["innings"] += 1
                agg["runs"] += b["runs"]
                agg["balls"] += b["balls"]
                agg["hs"] = max(agg["hs"], b["runs"])
                if b["runs"] >= 100:
                    agg["hundreds"] += 1
                elif b["runs"] >= 50:
                    agg["fifties"] += 1
                if b["dismissal"] not in ("not out", "DNB"):
                    agg["outs"] += 1
            for bw in inn.bowling_card:
                name = bw["name"]
                self.player_team.setdefault(name, inn.bowling_team)
                agg = self.bowling_agg.setdefault(
                    name, {"wickets": 0, "runs": 0, "balls": 0}
                )
                agg["wickets"] += bw["wickets"]
                agg["runs"] += bw["runs"]
                agg["balls"] += _overs_to_balls(bw["overs"])

    # ---- standings & stats ------------------------------------------------
    def _nrr(self, row):
        nrr = 0.0
        if row["for_balls"]:
            nrr += row["for_runs"] * 6.0 / row["for_balls"]
        if row["against_balls"]:
            nrr -= row["against_runs"] * 6.0 / row["against_balls"]
        return round(nrr, 3)

    def standings_table(self):
        rows = []
        for row in self.standings.values():
            r = dict(row)
            r["nrr"] = self._nrr(row)
            rows.append(r)
        rows.sort(key=lambda r: (-r["points"], -r["nrr"], -r["won"], r["team"]))
        return rows

    def show_standings(self):
        rows = self.standings_table()
        lines = ["", "%-22s %3s %3s %3s %3s %4s %7s" %
                 ("Team", "P", "W", "L", "T", "Pts", "NRR")]
        lines.append("-" * 52)
        for r in rows:
            lines.append("%-22s %3d %3d %3d %3d %4d %+7.3f" % (
                r["team"][:22], r["played"], r["won"], r["lost"], r["tie"],
                r["points"], r["nrr"]))
        for ln in lines:
            PrintInColor(ln, Style.BRIGHT)
        utilities.PushEvent("series", {"stage": "standings", "table": rows})

    def top_batters(self, n=5):
        rows = [dict(v, name=k, team=self.player_team.get(k, ""),
                     avg=(v["runs"] / v["outs"] if v["outs"] else v["runs"]))
                for k, v in self.batting_agg.items()]
        rows.sort(key=lambda r: (-r["runs"], -r["hs"]))
        return rows[:n]

    def top_bowlers(self, n=5):
        rows = []
        for k, v in self.bowling_agg.items():
            overs = BallsToOvers(v["balls"])
            eco = (v["runs"] * 6.0 / v["balls"]) if v["balls"] else 0.0
            rows.append(dict(v, name=k, team=self.player_team.get(k, ""),
                             overs=overs, eco=round(eco, 2)))
        rows.sort(key=lambda r: (-r["wickets"], r["eco"]))
        return rows[:n]

    def player_of_the_tournament(self):
        # simple all-round metric: runs plus a premium per wicket
        best, best_score = None, -1
        names = set(self.batting_agg) | set(self.bowling_agg)
        for name in names:
            runs = self.batting_agg.get(name, {}).get("runs", 0)
            wkts = self.bowling_agg.get(name, {}).get("wickets", 0)
            score = runs + 25 * wkts
            if score > best_score:
                best, best_score = name, score
        return best

    def show_stats(self, final=True):
        title = "Tournament statistics" if final else "Tournament so far"
        PrintInColor("\n=== %s ===" % title, Style.BRIGHT)
        bats = self.top_batters()
        bowls = self.top_bowlers()
        if bats:
            PrintInColor("Most runs:", Style.BRIGHT)
            for r in bats:
                PrintInColor("  %-20s %4d runs (HS %d, %d inns)" %
                             (GetShortName(r["name"]), r["runs"], r["hs"],
                              r["innings"]), Fore.LIGHTGREEN_EX)
        if bowls:
            PrintInColor("Most wickets:", Style.BRIGHT)
            for r in bowls:
                PrintInColor("  %-20s %3d wkts (%.2f eco)" %
                             (GetShortName(r["name"]), r["wickets"], r["eco"]),
                             Fore.LIGHTGREEN_EX)
        potm = self.player_of_the_tournament()
        if final and potm:
            PrintInColor("Player of the tournament: %s" % potm, Fore.LIGHTCYAN_EX)
        utilities.PushEvent("series", {
            "stage": "stats", "final": final,
            "topBatters": bats, "topBowlers": bowls,
            "playerOfTournament": potm if final else None,
        })

    # ---- finish -----------------------------------------------------------
    def _finalize(self):
        if len(self.team_names) == 2:
            a, b = self.team_names
            wa, wb = self.standings[a]["won"], self.standings[b]["won"]
            if wa > wb:
                self.champion = a
            elif wb > wa:
                self.champion = b
            else:
                self.champion = None
            summary = ("%s win the series %d-%d" % (self.champion,
                        max(wa, wb), min(wa, wb))) if self.champion \
                else "Series drawn %d-%d" % (wa, wb)
        else:
            final_fx = next((f for f in self.fixtures if f["kind"] == "final"), None)
            if final_fx and final_fx["result"]:
                winner = final_fx["result"]["winner"]
                if not winner:
                    # a drawn/tied final goes to the higher league finisher
                    table = self.standings_table()
                    order = [r["team"] for r in table]
                    winner = min([final_fx["home"], final_fx["away"]],
                                 key=lambda t: order.index(t))
                self.champion = winner
                summary = "%s are the champions!" % winner
            else:
                self.champion = None
                summary = "Tournament complete."

        self.finished = True
        PrintInColor("\n" + "=" * 40, Style.BRIGHT)
        PrintInColor(summary, Fore.LIGHTCYAN_EX)
        PrintInColor("=" * 40, Style.BRIGHT)
        self.show_standings()
        self.show_stats(final=True)
        utilities.PushEvent("series", {
            "stage": "champion", "champion": self.champion, "summary": summary,
        })
        self._delete_save()

    # ---- save/resume ------------------------------------------------------
    def _save(self):
        if not self.save_enabled or self.autoplay or not self.save_id:
            return
        try:
            import functions.SaveGame as SaveGame
            SaveGame.save_tournament(self)
        except Exception:
            pass

    def _delete_save(self):
        if self.save_id:
            import functions.SaveGame as SaveGame
            SaveGame.delete_save(self.save_id)

    def SaveMeta(self):
        played = sum(1 for f in self.fixtures if f["played"])
        total = len(self.fixtures) if self.fixtures else self.series_matches
        return {
            "kind": "tournament",
            "name": self.name,
            "format": "Test" if self.is_test else "Limited overs",
            "match_type": "Test" if self.is_test else (
                "%s ov" % self.overs if self.overs else ""),
            "overs": self.overs,
            "teams": self.team_names,
            "venue": self.venue_name,
            "played": played,
            "total": total,
            "situation": "%d of %d matches played" % (played, total),
            "clientId": self.save_client_id,
        }


MAX_TEAMS = 8


def SetupSeries():
    """
    Interactive series/tournament setup (works in both console and web via the
    shared ChooseFromOptions/input). Returns a ready-to-play Tournament, or
    None if the player didn't add at least two teams.
    """
    PrintInColor("Set up a new series/tournament", Style.BRIGHT)
    fmt = ChooseFromOptions(["Limited overs", "Test match"], "Series format", 5)
    is_test = (fmt == "Test match")

    overs = None
    if not is_test:
        PrintInColor("Overs per innings (multiple of 5, e.g. 20 or 50)", Style.BRIGHT)
        raw = input()
        overs = int(raw) if str(raw).isdigit() and int(raw) % 5 == 0 and 0 < int(raw) <= 50 else 5
        if overs == 5 and not (str(raw).isdigit() and int(raw) == 5):
            PrintInColor("Using %s overs." % overs, Style.BRIGHT)

    leagues = ListLeagues()
    specs = []
    chosen = set()
    while len(specs) < MAX_TEAMS:
        league = ChooseFromOptions(leagues, "Pick a league/season to add a team from", 5)
        names = [n for n in LeagueTeamNames(league, is_test) if n not in chosen]
        if not names:
            PrintInColor("No more teams available in that league.", Style.BRIGHT)
        else:
            name = ChooseFromOptions(names, "Add which team?", 5)
            specs.append({"league": league, "name": name, "is_test": is_test})
            chosen.add(name)
            PrintInColor("Added %s (%d team%s so far)." %
                         (name, len(specs), "" if len(specs) == 1 else "s"), Fore.LIGHTGREEN_EX)
        if len(specs) >= 2:
            more = ChooseFromOptions(
                ["Add another team", "Done - start the series"],
                "Add more teams or start?", 5)
            if more != "Add another team":
                break

    if len(specs) < 2:
        PrintInColor("A series needs at least two teams.", Style.BRIGHT)
        return None

    venues = VenueChoices()
    country = ChooseFromOptions(sorted(venues.keys()), "Series venue - country", 5)
    stadium = ChooseFromOptions(venues[country], "Series venue - stadium", 5)

    series_matches = 3
    if len(specs) == 2:
        PrintInColor("How many matches in this series? (1-9)", Style.BRIGHT)
        raw = input()
        series_matches = int(raw) if str(raw).isdigit() and 1 <= int(raw) <= 9 else 3
        PrintInColor("A %d-match series it is." % series_matches, Style.BRIGHT)

    t = Tournament(
        name="Series",
        is_test=is_test,
        overs=overs,
        team_specs=specs,
        venue_country=country,
        venue_name=stadium,
        series_matches=series_matches,
    )
    t.generate_fixtures()
    kind = "%d-team round robin + final" % len(specs) if len(specs) > 2 \
        else "%d-match series" % series_matches
    PrintInColor(
        "Series ready: %s (%s), %s." % (
            " vs ".join(t.team_names) if len(specs) == 2 else "%d teams" % len(specs),
            "Test" if is_test else "%s overs" % overs,
            kind),
        Fore.LIGHTCYAN_EX,
    )
    return t


@contextlib.contextmanager
def _silent_play():
    """
    Run a simulated match without any of its ball-by-ball noise reaching the
    player. In web mode this detaches the browser channel for the duration
    (thread-local, so other sessions are unaffected, and event pop-ups neither
    emit nor block on acks); in console mode it redirects stdout/stderr to
    /dev/null (safe: console play is single-process, single-user).
    """
    was_web = utilities.IsWebMode()
    saved = get_channel()
    redirect = None
    old_out = old_err = None
    if was_web:
        set_channel(None)
    else:
        redirect = open(os.devnull, "w")
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = redirect
    try:
        yield
    finally:
        if was_web:
            set_channel(saved)
        if redirect is not None:
            sys.stdout, sys.stderr = old_out, old_err
            redirect.close()
