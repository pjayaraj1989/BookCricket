# routines to calculate results
from functions.helper import Result
from operator import attrgetter
from colorama import Style
from functions.utilities import PrintInColor, BallsToOvers, Randomize


# calculate match result
def CalculateResult(match):
    team1 = match.team1
    team2 = match.team2

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
                                      str(match.overs * 6 - result.winner.total_balls))
        elif not result.winner.batting_second:
            win_margin = abs(result.winner.total_score - loser.total_score)
            if win_margin != 0:
                result.result_str += " by %s run(s)" % (str(win_margin))

    match.result = result


# find best player
def FindBestPlayers(match):
    result = match.result
    total_players = result.team1.team_array + result.team2.team_array
    bowlers_list = match.team1.bowlers + match.team2.bowlers

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
def FindPlayerOfTheMatch(match):
    # find which team won
    # if tied
    if match.team1.total_score == match.team2.total_score:
        match.winner = Randomize([match.team1, match.team2])
        match.loser = match.winner
    # if any team won
    else:
        match.winner, match.loser = max([match.team1, match.team2], key=attrgetter('total_score')), \
                                    min([match.team1, match.team2], key=attrgetter('total_score'))

    # find best batsman, bowler from winning team
    # always two batsmen will play
    best_batsmen = sorted(match.winner.team_array, key=attrgetter('runs'), reverse=True)
    best_bowlers = sorted(match.winner.bowlers, key=attrgetter('wkts'), reverse=True)

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
            best_batsmen = [plr for plr in best_batsmen if plr.status][0]
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
    margin = float(match.winner.total_score / match.loser.total_score)
    if margin >= 1.2:
        mom_is_bowler += 1

    # if losing team is bowled out
    if match.loser.wickets_fell >= 8:
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

    match.result.mom = best_player
    msg = "Player of the match: %s (%s)" % (best_player.name,
                                            GetMomStat(best_player))
    PrintInColor(msg, Style.BRIGHT)
    match.logger.info(msg)


def GetMomStat(player):
    res = ''
    char_notout = ''
    if player.runs > 0:
        # if not out, give a *
        if player.status:
            char_notout = '*'
        res += "scored %s%s off %s balls" % (str(player.runs),
                                             char_notout,
                                             str(player.balls))

    char_runs_given = ''
    char_overs = ''
    char_wkts = ''
    if player.balls_bowled > 0:
        overs = BallsToOvers(player.balls_bowled)
        if player.runs_given > 1:
            char_runs_given = 's'
        if overs > 1:
            char_overs = 's'
        if player.wkts > 1:
            char_wkts = 's'
        res += " Took %s wkt%s,conceding %s run%s in %s over%s" % (str(player.wkts),
                                                                   char_wkts,
                                                                   str(player.runs_given),
                                                                   char_runs_given,
                                                                   str(overs),
                                                                   char_overs,
                                                                   )
    return res
