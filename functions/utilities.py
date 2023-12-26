import colorama
from colorama import AnsiToWin32, init, Style
import time
import sys
from functions.Initiate import *
import random
import os

# function used to fill class attributes based on input arguments
def FillAttributes(obj, attrs, kwargs):
    for k, v in attrs.items():
        setattr(obj, k, attrs[k])
    if kwargs is not None:
        for k, v in kwargs.items():
            for attr in attrs:
                if k == attr:
                    setattr(obj, attr, v)
    return obj


# choose from options a list
def ChooseFromOptions(options, msg, tries):
    print(msg)
    option_selected = None
    options_dict = {}
    for x in range(len(options)):
        options_dict[str(x)] = options[x]
    msg = ''
    for k, v in options_dict.items():
        msg += '%s.%s ' % (k, v)
    keys = list(options_dict.keys())
    n = tries
    while n > 0:
        opt = input("Select from : %s" % msg)
        if opt not in keys:
            n -= 1
            if n == 0:
                Error_Exit("exiting!")
            else:
                print('Invalid choice! Try again')
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
def Randomize(mylist):
    op = random.choice(mylist)
    return op


# check for N consecutive elements in a list
def CheckForConsecutiveElements(arr, element, N):
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
def GetShortName(name):
    # get first part and make it initial
    pieces = name.split(' ')
    firstname, lastname = pieces[0], pieces[-1]
    if '.' in firstname:
        initials = firstname
    else:
        initials = firstname[0] + '.'
    shortname = initials + ' ' + lastname
    return shortname


# get second name
def GetSurname(name):
    return name.split(' ')[-1]


# get first name
def GetFirstName(name):
    return name.split(' ')[0]


# print nested array in formatted way
def PrintListFormatted(data_to_print, seconds, logger):
    # now print it
    col_width = max(len(word) for row in data_to_print for word in row) + 1
    for row in data_to_print:
        msg = "".join(word.ljust(col_width) for word in row)
        PrintInColor(msg, Style.BRIGHT)
        if logger is not None:
            logger.info(msg)
        time.sleep(seconds)


# print in color
def PrintInColor(msg, color):
    init(wrap=False)
    stream = AnsiToWin32(sys.stderr).stream
    print(color + msg + Style.RESET_ALL, file=stream)


# just error and exit
def Error_Exit(msg):
    if 'nt' in os.name:
        print(msg)
    else:
        colorama.init()
        PrintInColor("Error: %s" % msg, Fore.RED)
    input('Press enter to continue..')
    sys.exit(0)


# balls to overs
def BallsToOvers(balls):
    overs = 0.0
    if balls >= 0:
        overs = float(str(int(balls / 6)) + '.' + str(balls % 6))
    return overs


