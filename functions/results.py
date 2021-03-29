# routines to calculate results
from functions.helper import Result
from operator import attrgetter
import random
from colorama import Style
from functions.utilities import PrintInColor, BallsToOvers


# calculate match result
def CalculateResult(match):
    team1 = match.team1
    team2 = match.team2
    bowlers_t1 = match.team1.bowlers
    bowlers_t2 = match.team2.bowlers

    # from the bowlers list, get rid of those who did not bowl at all
    bowlers_t1 = [plr for plr in bowlers_t1 if plr.balls_bowled > 0]
    bowlers_t2 = [plr for plr in bowlers_t2 if plr.balls_bowled > 0]

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
                result.result_str += " by %s wicket(s) with %s ball(s) left" % (str(win_margin),
                                                                                str(
                                                                                    match.overs * 6 - result.winner.total_balls))
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
    if match.team1.total_score == match.team2.total_score:
        team_won, team_lost = (match.team1, match.team2)
    else:
        team_won = max([match.team1, match.team2], key=attrgetter('total_score'))
        team_lost = min([match.team1, match.team2], key=attrgetter('total_score'))

    best_batsman = None
    best_bowler = None

    # find best batsman, bowler from winning team
    # always two batsmen will play
    best_batsmen = sorted(team_won.team_array, key=attrgetter('runs'), reverse=True)
    best_bowlers = sorted(team_won.bowlers, key=attrgetter('wkts'), reverse=True)

    # now process these lists
    # if both have same runs, pick who is not out
    if len(best_batsmen) > 2:
        best_batsmen = best_batsmen[:2]
        if best_batsmen[0].runs == best_batsmen[1].runs:
            # workaround, if both are 0 and both are out
            if best_batsmen[0].runs == best_batsmen[1].runs == 0:
                best_batsman = best_batsmen[0]
            else:
                # get who are not out
                best_batsmen = [plr for plr in best_batsmen if plr.status]
                # if both are notout
                if best_batsmen[0].status == best_batsmen[1].status:
                    # get random
                    best_batsman = random.choice([best_batsmen[0], best_batsmen[1]])
                else:
                    best_batsman = best_batsmen[0]
        else:
            best_batsman = best_batsmen[0]

    # if same no of wkts, check eco
    if len(best_bowlers) > 2:
        best_bowlers = best_bowlers[:2]
        if best_bowlers[0].wkts == best_bowlers[1].wkts:
            best_bowler = sorted(best_bowlers, key=attrgetter('eco'), reverse=False)[0]
        else:
            best_bowler = best_bowlers[0]

    # if scores tied, select randomly
    if team_won.total_score == team_lost.total_score:
        best_player = max(team_won.team_array, key=attrgetter('runs'))
    # check if win margin is >50% , if so, give credit to bowlers, else batsmen
    elif float(team_won.total_score / team_lost.total_score) >= 1.2:
        best_player = best_bowler
    else:
        best_player = best_batsman

    # if a player is found in both top batsmen and bowler list he is my MOM
    common_players = list(set(best_bowlers).intersection(best_batsmen))
    if len(common_players) != 0:    best_player = common_players[0]

    match.result.mom = best_player
    msg = "Player of the match: %s (%s)" % (best_player.name,
                                            GetMomStat(best_player))
    PrintInColor(msg, Style.BRIGHT)
    match.logger.info(msg)


def GetMomStat(player):
    res = ''
    if player.runs > 0:
        res += "scored %s runs off %s balls" % (str(player.runs),
                                                str(player.balls))
    if player.balls_bowled > 0:
        overs = BallsToOvers(player.balls_bowled)
        res += ",took %s wkt(s),conceding %s run(s) in %s over(s)" % (str(player.wkts),
                                                                        str(player.runs_given),
                                                                        str(overs))
    return res
