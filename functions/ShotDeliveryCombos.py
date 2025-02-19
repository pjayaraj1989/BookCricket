def GetCombinations(delivery, shot):
    result = False
    if delivery.length in ["full"]:
        # assign valid shots
        if shot.type == ["drive", "sweep"]:
            result = True
    elif delivery.length == "short":
        if shot.type in ["cut", "pull"]:
            result = True
    elif delivery.length == "goodlength":
        if shot.type in ["leave", "defence"]:
            result = True

    return result
