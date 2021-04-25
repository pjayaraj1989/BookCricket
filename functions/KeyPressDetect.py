import time


def GetKeyPressTime():
    input("Press enter after 5 seconds:")
    begin = time.time()
    input("")  # this is when you start typing
    end = time.time()
    elapsed = end - begin

    return elapsed
