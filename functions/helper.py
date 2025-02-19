from functions.utilities import FillAttributes

# mainly used classes
# add the default attributes and values here
# the FillAttributes function will populate it accordingly

class Tournament:
    def __init__(self, **kwargs):
        """
        Initialize a Tournament object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Tournament object.
        """
        attrs = {'name': ' ',
                 'teams': []}
        self = FillAttributes(self, attrs, kwargs)


class Venue:
    def __init__(self, **kwargs):
        """
        Initialize a Venue object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Venue object.
        """
        attrs = {'name': ' ',
                 'run_prob': [],
                 'run_prob_t20': [],
                 'weather': None}
        self = FillAttributes(self, attrs, kwargs)


class Innings:
    def __init__(self, **kwargs):
        """
        Initialize an Innings object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Innings object.
        """
        attrs = {'status': False, 'overs': 0, 'result': None, 'batting_team': None, 'bowling_team': None}
        self = FillAttributes(self, attrs, kwargs)


class Fow:
    def __init__(self, **kwargs):
        """
        Initialize a Fow (Fall of Wicket) object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Fow object.
        """
        attrs = {'total_balls': 0, 'wkt': 0, 'runs': 0, 'player_dismissed': None, 'player_onstrike': None}
        self = FillAttributes(self, attrs, kwargs)


class Partnership:
    def __init__(self, **kwargs):
        """
        Initialize a Partnership object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Partnership object.
        """
        attrs = {'balls': 0, 'runs': 0, 'batsman_dismissed': None, 'batsman_onstrike': None, 'both_notout': False}
        self = FillAttributes(self, attrs, kwargs)


class Result:
    def __init__(self, **kwargs):
        """
        Initialize a Result object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Result object.
        """
        attrs = {'team1': None, 'team2': None, 'winner': None, 'most_runs': None, 'most_wkts': None, 'best_eco': None,
                 'mom': None, 'result_str': ' '}
        self = FillAttributes(self, attrs, kwargs)


class Delivery:
    def __init__(self, **kwargs):
        """
        Initialize a Delivery object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Delivery object.
        """
        attrs = {'type': None, 'speed': None, 'line': None, 'length': None, }
        self = FillAttributes(self, attrs, kwargs)


class Shot:
    def __init__(self, **kwargs):
        """
        Initialize a Shot object with the given attributes.

        Args:
            **kwargs: Keyword arguments to set the attributes of the Shot object.
        """
        attrs = {'type': None, 'direction': None, 'foot': None, }
        self = FillAttributes(self, attrs, kwargs)
