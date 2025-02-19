# a pair face a delivery
from functions.utilities import Error_Exit


def PairFaceBall(pair, run):
    """
    Update the pair of batsmen after facing a ball.

    Args:
        pair: The current pair of batsmen.
        run: The number of runs scored on the ball.

    Returns:
        None
    """
    # find out who is on strike
    if pair[0].onstrike is True and pair[1].onstrike:
        Error_Exit("Error! both cant be on strike!")
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)

    alt_ind = 0
    if ind == 0:
        alt_ind = 1

    pair[ind].runs += run
    pair[ind].balls += 1
    # now if runs is 1 / 3
    if run % 2 != 0:
        pair[ind].onstrike, pair[alt_ind].onstrike = False, True

    return pair


# rotate strike
def RotateStrike(pair):
    """
    Rotate the strike between the two batsmen.

    Args:
        pair: The current pair of batsmen.

    Returns:
        None
    """
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)
    alt_ind = 0
    if ind == 0:
        alt_ind = 1

    pair[ind].onstrike = False
    pair[alt_ind].onstrike = True


# batsman out
def BatsmanOut(pair, dismissal):
    """
    Update the pair of batsmen after a batsman is out.

    Args:
        pair: The current pair of batsmen.
        dismissal: The dismissal string.

    Returns:
        list: The updated pair of batsmen.
    """
    # find out who is on strike
    if pair[0].onstrike is True and pair[1].onstrike is True:
        Error_Exit("Error! both cant be on strike!")
    player_on_strike = next((x for x in pair if x.onstrike), None)
    ind = pair.index(player_on_strike)
    # batsman dismissed
    pair[ind].status = False
    pair[ind].onfield = False
    pair[ind].balls += 1
    pair[ind].strikerate = float((pair[ind].runs / pair[ind].balls) * 100)
    pair[ind].strikerate = round(pair[ind].strikerate, 2)
    # update dismissal mode
    pair[ind].dismissal = dismissal
    return pair
