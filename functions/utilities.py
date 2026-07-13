import colorama
from colorama import AnsiToWin32, init, Style
import time
import sys
from functions.Initiate import *
import random
import os
import pyttsx3
from math import ceil
from web.io_bridge import get_channel, GameAborted


# function used to fill class attributes based on input arguments
def FillAttributes(obj, attrs, kwargs):
    """
    Fill the attributes of an object based on input arguments.

    Args:
        obj: The object whose attributes need to be filled.
        attrs: A dictionary of default attributes.
        kwargs: A dictionary of input arguments.

    Returns:
        The object with filled attributes.
    """
    for key, value in attrs.items():
        setattr(obj, key, kwargs.get(key, value))
    return obj


# choose from options a list
def ChooseFromOptions(options: list, msg: str, tries: int):
    """
    Choose an option from a list of options.

    Args:
        options: A list of options to choose from.
        msg: A message to display to the user.
        tries: The number of attempts allowed for the user to make a valid choice.

    Returns:
        The selected option.
    """
    channel = get_channel()
    if channel is not None:
        return channel.choose(options, msg)

    print(msg)
    option_selected = None
    options_dict = {}
    for x in range(len(options)):
        options_dict[str(x)] = options[x]
    msg = ""
    for k, v in options_dict.items():
        msg += "%s.%s " % (k, v)
    keys = list(options_dict.keys())
    n = tries
    while n > 0:
        opt = input("Select from : %s" % msg)
        if opt not in keys:
            n -= 1
            if n == 0:
                Error_Exit("exiting!")
            else:
                print("Invalid choice! Try again")
                continue
        else:
            for k, v in options_dict.items():
                if opt == k:
                    option_selected = v
                    print("Selected : %s" % v)
                    break
        break
    return option_selected


# randomize
def Randomize(mylist: list):
    """
    Randomly select an element from a list.

    Args:
        mylist: The list to select from.

    Returns:
        A randomly selected element from the list.
    """
    op = random.choice(mylist)
    return op


# check for N consecutive elements in a list
def CheckForConsecutiveElements(arr: list, element, N: int):
    """
    Check for N consecutive elements in a list.

    Args:
        arr: The list to check.
        element: The element to check for.
        N: The number of consecutive elements to check for.

    Returns:
        True if N consecutive elements are found, False otherwise.
    """
    result = False
    l = len(arr)
    if len(arr) >= N:
        for i in range(l):
            temp = []
            for x in range(N):
                temp.append(arr[i - x])
            # check for equal elements
            if len(temp) > 0 and all(elem == element for elem in temp):
                result = True
                break
    return result


# get short name
def GetShortName(name: str):
    """
    Get the short name from a full name.

    Args:
        name: The full name.

    Returns:
        The short name.
    """
    # get first part and make it initial
    pieces = name.split(" ")
    firstname, lastname = pieces[0], pieces[-1]
    if "." in firstname:
        initials = firstname
    else:
        initials = firstname[0] + "."
    shortname = initials + " " + lastname
    return shortname


# get second name
def GetSurname(name: str):
    """
    Get the surname from a full name.

    Args:
        name: The full name.

    Returns:
        The surname.
    """
    return name.split(" ")[-1]


# get first name
def GetFirstName(name: str):
    """
    Get the first name from a full name.

    Args:
        name: The full name.

    Returns:
        The first name.
    """
    return name.split(" ")[0]


# print nested array in formatted way
def PrintListFormatted(data_to_print: list, seconds: int, logger):
    """
    Print a nested array in a formatted way.

    Args:
        data_to_print: The nested array to print.
        seconds: The delay in seconds between printing each row.
        logger: The logger to log the printed messages.

    Returns:
        None
    """
    # now print it
    col_width = max(len(word) for row in data_to_print for word in row) + 1
    for row in data_to_print:
        msg = "".join(word.ljust(col_width) for word in row)
        print(msg)
        if logger is not None:
            logger.info(msg)
        time.sleep(seconds)


# print in color
def PrintInColor(msg: str, color):
    """
    Print a message in color and optionally speak it.

    Args:
        msg: The message to print.
        color: The color to print the message in.

    Returns:
        None
    """
    channel = get_channel()
    if channel is not None:
        channel.output(msg, color)
        return

    commentary_enabled = False
    # read commentary_enabled from file if available #FIXME, a bad idea, this should be a global variable!
    if os.path.exists("commentary_enabled.txt"):
        f = open("commentary_enabled.txt", "r")
        # if the file contains string 'True', set commentary_enabled to True, else False
        if "true" in f.read().strip().lower():
            commentary_enabled = True
        f.close()

    init(wrap=False)
    stream = AnsiToWin32(sys.stderr).stream
    print(color + msg + Style.RESET_ALL, file=stream)
    # speak text
    if commentary_enabled == True:
        engine = pyttsx3.init()
        engine.say(msg)
        engine.runAndWait()


# just error and exit
def Error_Exit(msg):
    """
    Print an error message and exit the program.

    Args:
        msg: The error message to print.

    Returns:
        None
    """
    channel = get_channel()
    if channel is not None:
        channel.output("Error: %s" % msg)
        raise GameAborted(msg)

    if "nt" in os.name:
        print(msg)
    else:
        colorama.init()
        #PrintInColor("Error: %s" % msg, Fore.RED)
        print ("Error: %s" % msg)
    input("Press enter to continue..")
    sys.exit(0)


def PushEvent(kind, data=None):
    """
    Fire a short-lived highlight to the web UI's top-left event pane (toss,
    wicket, four, six, DRS). No-op in console mode (no channel set).

    Args:
        kind: A short string identifying the event ("toss", "wicket", "four",
            "six", "drs_pending", "drs_result").
        data: Optional dict of extra fields for the frontend to render.

    Returns:
        None
    """
    channel = get_channel()
    if channel is None:
        return
    channel.event(kind, data)


def PushScorecard(match):
    """
    Send a compact, structured snapshot of the live match state to the
    browser's side-pane scorecard. No-op in console mode (no channel set).

    Args:
        match: The Match object, called once an over has just finished.

    Returns:
        None
    """
    channel = get_channel()
    if channel is None:
        return

    batting = match.batting_team
    bowling = match.bowling_team

    batsmen = [
        {"name": p.name, "runs": _int(p.runs), "balls": _int(p.balls), "onStrike": bool(p.onstrike)}
        for p in (batting.current_pair or [])
    ]

    bowler = bowling.current_bowler
    bowler_state = None
    if bowler is not None:
        bowler_state = {
            "name": bowler.name,
            "overs": _float(BallsToOvers(bowler.balls_bowled)),
            "maidens": _int(bowler.maidens),
            "runs": _int(bowler.runs_given),
            "wickets": _int(bowler.wkts),
        }

    is_test = bool(getattr(match, "is_test", False))

    # Lead/trail, Test only, and only outside of a run-chase (a chase already
    # shows its own target/runs-needed line below, so a separate lead/trail
    # line would be redundant there).
    lead_trail = None
    if is_test and not batting.batting_second:
        batting_total = sum(inn.score for inn in batting.innings_history) + batting.total_score
        bowling_total = sum(inn.score for inn in bowling.innings_history)
        if batting.innings_history or bowling.innings_history:
            diff = batting_total - bowling_total
            if diff > 0:
                lead_trail = {"team": batting.name, "diff": _int(diff)}
            elif diff < 0:
                lead_trail = {"team": bowling.name, "diff": _int(-diff)}
            else:
                lead_trail = {"team": None, "diff": 0}

    # Runs and wickets still needed to win, Test 4th-innings chase only.
    runs_needed = None
    wickets_in_hand = None
    if is_test and batting.batting_second:
        runs_needed = _int(max(batting.target - batting.total_score, 0))
        wickets_in_hand = _int(10 - batting.wickets_fell)

    # Once a chase is actually decided (target reached, or the chasing side
    # is all out), "Need 0 more · RRR: 0.00" reads as broken rather than
    # informative - replace the target line with the plain result instead.
    # A finer-grained "won by an innings"/draw/no-result message still comes
    # later from CalculateResult()/_FinalizeChase() once the innings fully
    # unwinds; this is just the immediate, ball-by-ball chase outcome.
    result_message = None
    if batting.batting_second and batting.target:
        if batting.total_score >= batting.target:
            wkts_left = _int(10 - batting.wickets_fell)
            result_message = "%s won by %s wicket%s" % (
                batting.name, str(wkts_left), "" if wkts_left == 1 else "s"
            )
        elif batting.wickets_fell == 10:
            margin = batting.target - 1 - batting.total_score
            if margin == 0:
                result_message = "Match Tied"
            else:
                result_message = "%s won by %s run%s" % (
                    bowling.name, str(margin), "" if margin == 1 else "s"
                )

    channel.state({
        "battingTeam": batting.name,
        "bowlingTeam": bowling.name,
        "score": _int(batting.total_score),
        "wickets": _int(batting.wickets_fell),
        "overs": _float(BallsToOvers(batting.total_balls)),
        # match.overs is None for a Test match (no fixed innings length)
        "totalOvers": _int(match.overs) if match.overs else None,
        "isTest": is_test,
        "day": _int(match.day) if is_test else None,
        "maxDays": _int(match.max_days) if is_test else None,
        "crr": _float(batting.GetCurrentRate()),
        "target": _int(batting.target) if batting.batting_second else None,
        # GetRequiredRate() is intentionally a no-op (returns 0.0) for Test -
        # send None rather than a misleading "0.00" rate
        "requiredRunRate": (
            _float(batting.GetRequiredRate()) if batting.batting_second and not is_test else None
        ),
        "leadTrail": lead_trail,
        "resultMessage": result_message,
        "runsNeeded": runs_needed,
        "wicketsInHand": wickets_in_hand,
        "batsmen": batsmen,
        "bowler": bowler_state,
    })


def PushInningsScorecard(match, summary):
    """
    Send the full batting card, bowling card, and fall-of-wickets for the
    innings that just finished, for the side-pane's end-of-innings summary.
    No-op in console mode (no channel set). A pure serializer of the
    InningsSummary Match.BuildInningsSummary() already built (and, for Test
    matches, also stored in Team.innings_history) - all fields on it are
    already native int/float/str/bool/list/dict, so no further casting
    is needed here.

    Args:
        match: The Match object, called once an innings has just finished.
        summary: The InningsSummary snapshot for that innings.

    Returns:
        None
    """
    channel = get_channel()
    if channel is None:
        return

    channel.innings({
        "battingTeam": summary.batting_team,
        "bowlingTeam": summary.bowling_team,
        "score": summary.score,
        "wickets": summary.wickets,
        "overs": summary.overs,
        "extras": summary.extras,
        "declared": summary.declared,
        "battingCard": summary.batting_card,
        "bowlingCard": summary.bowling_card,
        "fow": summary.fow,
        "inProgress": False,
    })


def PushLiveInningsScorecard(match):
    """
    Push a full (batting/bowling card + fall-of-wickets) scorecard snapshot
    of the innings CURRENTLY IN PROGRESS - called after every ball, as
    opposed to PushInningsScorecard's once-per-completed-innings push.
    No-op in console mode (the console already shows the full scorecard
    every over via DisplayScore/DisplayBowlingStats).

    Args:
        match: The Match object, called mid-innings.

    Returns:
        None
    """
    channel = get_channel()
    if channel is None:
        return

    summary = match.BuildInningsSummary()
    channel.innings({
        "battingTeam": summary.batting_team,
        "bowlingTeam": summary.bowling_team,
        "score": summary.score,
        "wickets": summary.wickets,
        "overs": summary.overs,
        "extras": summary.extras,
        "declared": summary.declared,
        "battingCard": summary.batting_card,
        "bowlingCard": summary.bowling_card,
        "fow": summary.fow,
        "inProgress": True,
    })


def _int(value):
    # values sourced from run generation (numpy.random.choice) can end up as
    # numpy.int64, which the SocketIO/Flask JSON encoder can't serialize.
    return int(value)


def _float(value):
    return float(value)


# balls to overs
def BallsToOvers(balls: int):
    """
    Convert balls to overs.

    Args:
        balls: The number of balls.

    Returns:
        The number of overs.
    """
    overs = 0.0
    if balls >= 0:
        overs = float(str(int(balls / 6)) + "." + str(balls % 6))
    return overs


def PlotOversBarGraph(over_runs_dict: dict, over_wkt_history: dict, title: str = "Runs per Over"):
    """
    Plot a scaled ASCII bar graph showing runs and wickets per over.
    """
    if not over_runs_dict or not over_wkt_history:
        return

    # Calculate dimensions with better scaling
    max_runs = max(over_runs_dict.values())
    min_runs = min(over_runs_dict.values())
    
    # Reduce height for more compact display
    height = min(12, max(6, int((max_runs - min_runs) / 2) + 3))  # Reduced height range
    width = len(over_runs_dict)
    
    # Calculate scale intervals for better distribution
    scale_interval = ceil((max_runs - min_runs) / (height - 1))
    if scale_interval == 0:
        scale_interval = 1  # Set minimum scale interval to 1
    max_scale = ceil(max_runs / scale_interval) * scale_interval
    
    # Create fewer scale points for y-axis
    scale_points = [round(i * scale_interval, 1) for i in range(int(max_scale / scale_interval) + 1)]
    display_points = [scale_points[0]]  # Always show minimum
    if len(scale_points) > 2:
        display_points.extend(scale_points[len(scale_points)//2::len(scale_points)//2])  # Show middle and max
    
    # Calculate bar width based on max wickets
    max_wickets = max(over_wkt_history.values())
    bar_width = max(2, max_wickets)  # Minimum width of 2, or wider if needed for wickets
    
    # Print title and header with adjusted width
    PrintInColor(f"\n{title}:", Style.BRIGHT)
    print(f"{'Runs':>6} {'╔' + '═' * (width * bar_width) + '╗'}")

    # Print bars with reduced height and wickets
    for value in reversed(scale_points):
        if value in display_points:
            print(f"{value:>6.0f} ║", end='')
        else:
            print(f"{'':>6} ║", end='')
        
        # Print bars and wickets with adjusted width
        for over in sorted(over_runs_dict.keys()):
            runs = over_runs_dict[over]
            wickets = over_wkt_history.get(over, 0)
            
            if runs >= value:
                # If this is the top of the bar, show wickets with *
                if value == max(v for v in scale_points if v <= runs):
                    print(f"{'*' * wickets:{bar_width}}", end='')
                else:
                    print(f"{'█' * bar_width}", end='')
            else:
                print(" " * bar_width, end='')
        print("║")

    # Print x-axis with adjusted width
    print(f"       ╚{'═' * (width * bar_width)}╝")
    print("       ", end='')
    for over in sorted(over_runs_dict.keys()):
        if over % 3 == 0:
            print(f"{over:>{bar_width}}", end='')
        else:
            print(" " * bar_width, end='')
    print("\n       " + "Overs".center(width * bar_width))
    
    # Print statistics
    total_runs = sum(over_runs_dict.values())
    avg_runs = total_runs / len(over_runs_dict)
    #PrintInColor(f"\nTotal: {total_runs} runs ({avg_runs:.1f} per over)", Style.BRIGHT)
    
    # Add wickets legend if any wickets fell
    #if any(over_wkt_history.values()):
    #    PrintInColor("\nWickets fell in over *", Style.BRIGHT)

    #input("\nPress enter to continue...")


import requests
def normalize_name(name):
    """
    Normalize name by removing dots and extra spaces.
    E.g., 'K.L Rahul' -> 'KL Rahul'
    """
    # some names have (cricketer) suffix, remove it
    # handle cases like Jack Russell (cricketer, born 1963)
    if "(cricketer)" in name:
        name = name.replace("(cricketer)", "").strip()
    
    # some names like de Kock, de Villiers etc, make it deKock, deVilliers for normalization
    name = name.replace("de ", "de")
    name = name.replace("van ", "van")
    
    
    # Remove dots after letters (abbreviations)
    normalized = name.replace('.', '')
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    return normalized

def is_name_valid(name):
    #print (f"Checking validity of name: {name}")
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": name,
        "format": "json"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    normalized_input = normalize_name(name).lower()

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error occurred while checking name: {e}")
        return False
    
    search_results = data.get("query", {}).get("search", [])
    for result in search_results:
        result_title = result.get("title", "")
        normalized_result = normalize_name(result_title).lower()
        
        # Check for exact match after normalization
        if normalized_input == normalized_result:
            return True
    return False