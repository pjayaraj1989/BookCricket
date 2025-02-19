import colorama
from colorama import AnsiToWin32, init, Style
import time
import sys
from functions.Initiate import *
import random
import os
import pyttsx3


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
    if "nt" in os.name:
        print(msg)
    else:
        colorama.init()
        PrintInColor("Error: %s" % msg, Fore.RED)
    input("Press enter to continue..")
    sys.exit(0)


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
