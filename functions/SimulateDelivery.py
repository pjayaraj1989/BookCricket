# bowl
from functions.KeyPressDetect import GetKeyPressTime
from functions.helper import Delivery, Shot
from functions.utilities import Randomize

deliveries_pacer = ['inswing', 'outswing', 'straight', 'reverse', 'offcutter', 'legcutter', 'knuckle', 'dipper', ]
deliveries_spinner = ['offspin', 'legspin', 'googly', 'wrongun', 'arm', 'carrom', 'topspin', ]

# speed
ball_speed = ['slow', 'med', 'fast', ]

# length
ball_length = ['short', 'goodlength', 'full']

# line
ball_line = ['offwide', 'outsideoff', 'off', 'middle', 'leg', 'outsideleg', 'legwide', ]

# shots
attrs = {'type': None, 'direction': None, 'foot': None, }
shot_type = ['defend', 'leave', 'drive', 'sweep', 'loft', 'hook', 'reverse', 'cut', 'pull']
shot_direction = ['firstslip', 'gully', 'point', 'cover', 'extracover', 'midoff', 'straight', 'midon', 'midwicket',
                  'squareleg', 'backwardsquareleg', 'fineleg', 'legslip', 'scoop',]
shot_foot = ['backfoot', 'frontfoot', 'advance', ]


def Bowl(bowler):
    delivery = Delivery()
    if bowler.isspinner:
        delivery.type = Randomize(deliveries_spinner)
    elif bowler.ispacer:
        delivery.type = Randomize(deliveries_spinner)

    delivery.speed = Randomize(ball_speed)
    delivery.line = Randomize(ball_line)
    delivery.length = Randomize(ball_length)

    return delivery


def SelectShot(batsman):
    shot = Shot()
    shot.type = Randomize(shot_type)
    shot.direction = Randomize(shot_direction)
    shot.foot = Randomize(shot_foot)

    return shot


# generate run
def GenerateRunNew(match, over, player_on_strike):
    batting_team = match.batting_team
    bowler = match.bowling_team.current_bowler
    overs = match.overs
    venue = match.venue

    delivery = Bowl(bowler)
    shot = SelectShot(player_on_strike)

    # this shot should go accurate as per the batsmans attributes
    # define right set of shots for the deliveries, if it goes fine,
    # early shot
    shot_timing = 0.0
    response_time = GetKeyPressTime()

    if 0.0 <= response_time <= 4.0:
        # this is an early shot
        shot_timing = 'early'
    elif 4.0 <= response_time <= 5.9:
        shot_timing = 'best'
    elif response_time > 5.9:
        shot_timing = 'late'

    if shot_timing == 'early':
        run = Randomize([0, -1])
    elif shot_timing == 'late':
        run = Randomize([1, 2, 3])
    else:
        run = Randomize([4, 6, 5])

    # dummy
    # run_array = [-1, 0, 1, 2, 3, 4, 5, 6]
    # run = Randomize(run_array)
    return run
