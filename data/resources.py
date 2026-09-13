# resources needed


class resources:
    # color maps
    from colorama import Fore

    color_map = {
        "lcyan": Fore.LIGHTCYAN_EX,
        "lblue": Fore.LIGHTBLUE_EX,
        "lgreen": Fore.LIGHTGREEN_EX,
        "lyellow": Fore.LIGHTYELLOW_EX,
        "lmagenta": Fore.LIGHTMAGENTA_EX,
        "lred": Fore.LIGHTRED_EX,
        "grey": Fore.LIGHTBLACK_EX,
        "green": Fore.GREEN,
        "blue": Fore.BLUE,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA,
        "yellow": Fore.YELLOW,
        "red": Fore.RED,
        "black": Fore.BLACK,
    }

    # populate weather
    weathers = {
        "sunny": "Weather looks so pleasant and sunny, ideal for cricket",
        "overcast": "Overcast weather, might help the swing bowlers",
        "rainy": "There is a slight rain scare",
        "cloudy": "cloudy weather, hope we won't have a rain interruption",
        "humid": "A very humid day!",
    }

    weather_prob = [0.3, 0.2, 0.1, 0.2, 0.2]

    commentators = [
        "Harsha Bhogle",
        "Ramiz Raja",
        "Tony Greig",
        "Ian Smith",
        "Sunil Gavaskar",
        "Sanjay Manjrekar",
        "Ravi Shastri",
        "Richie Benaud",
        "Mike Haysman",
        "Phil Tufnell",
        "David Lloyd",
        "Dean Jones",
        "Ian Botham",
        "Geoff Boycott",
        "Ian Chappell",
        "Greg Chappell",
        "Martin Crowe",
        "Ian Bishop",
        "Isa Guha",
        "Bill Lawry",
        "Danny Morrison",
        "Mark Nicholas",
        "Michael Holding",
    ]

    umpires = [
        "Kumar Dharmasena",
        "Ian Gould",
        "Asad Rauf",
        "Aleem Dar",
        "Nitin Menon",
        "Marais Erasmus",
        "Richard Kettleborough",
        "Nigel Llong",
        "Paul Reiffel",
        "Rudi Koertzen",
        "Richard Illingworth",
        "Simon Tauffel",
        "S. Ravi",
        "Steve Davis",
        "Joel Wilson",
        "Mark Benson",
        "Bruce Oxenford",
        "Billy Doctrove",
        "Billy Bowden",
    ]

    # fielders - shot descriptions any bowler type can concede. Type-specific
    # ones (a cut needs pace and bounce to work with; a sweep or a charge
    # down the track is a spin-countering shot) live in fields_pace/
    # fields_spin below instead, and Match.py's four/six/ground-shot
    # commentary only mixes those in when the bowler actually matches -
    # see the "invalid commentary" fix: a cut/yorker off a spinner, or a
    # sweep/short-leg shot off a pacer, doesn't happen in real cricket
    fields = {
        4: [
            "that's gone over first slip!",
            "through the covers",
            "hit nice and straight!",
            "chipped in the air over the fielder at midwicket",
            "over backward point",
            "steered between the covers",
            "punched off the backfoot",
            "driven off the front foot",
            "driven through extra cover",
            "over extra cover",
            "worked that through short midwicket",
            "smashed like a bullet!",
            "in the air... just over the fielder at point!",
            "hit through midoff",
            "delicately pushed it to fine leg",
            "wristy flick, well steered into the legside",
            "punched it through the gap! unbelievable timing!",
            "moved across the line and steered it through fine leg",
            "lofted in the air",
            "driven like a tracer bullet!",
            "driven like a rocket!",
            "hit hard and nearly killed the umpire!",
            "smashed it over midwicket",
            "wristy flick between midwicket and square leg",
            "driven between extra cover and mid-off",
            "flicks it towards the leg side",
            "hit hard and just missed his partners head!",
            "solidly played through extra cover",
        ],
        6: [
            "straight down the ground",
            "over deep point!",
            "smashes it over long-on",
            "over long on",
            "over long off!",
            "moves across and hits it over deep midwicket",
            "over deep cover!",
            "over deep extra cover!",
            "moves across the stumps and smashes it through leg side",
            "blasted that through the covers",
            "smashed it over long off",
        ],
        "ground_shot": [
            "driven through the covers",
            "drive through extra cover",
            "worked that into the gap",
            "sweetly timed into the gap",
            "driven nicely through midwicket",
            "hit that hard through point",
            "steered it towards fine leg",
            "between point and cover",
            "through square leg",
            "between point and backward point",
            "well timed it into the leg side!",
            "steered expertly into the gap!",
            "advances and drives it straight!",
            "punched through extra cover",
            "runs it down the third man",
        ],
    }

    # shots that only make sense against pace - need real pace and bounce to
    # work with (a cut, an upper cut, a steer off the seam past the slips),
    # or a genuinely fast, short delivery to begin with
    fields_pace = {
        4: [
            "that is a fierce square cut!",
            "delicately steered it through slips...",
            "upper cut over the keepers hands!",
            "soft hands... steered it through second slip!",
            "steered it towards the gap between deep third man and deep backward point",
            "cut hard through point",
            "square cut over the point fielder",
            "short ball punished through leg side",
            "between the first slip and short third man!",
        ],
        6: [
            "cuts it hard over point",
            "pulls it away in front of square, that's gone all the way!",
            "picks the bouncer and hooks it for six!",
            "upper-cut over the keeper's head, and that's out of the ground!",
        ],
        "ground_shot": [
            "runs past the slips",
            "between first slip and short third man",
            "between leg slip and the gully",
        ],
    }

    # shots that only make sense against spin - a batsman gets down the
    # track or sweeps because the ball is slower and gives them time; a
    # fielder stands at short leg/silly mid-on because it's safe to
    fields_spin = {
        4: [
            "advances down the ground",
            "reverse sweep",
            "driven through silly mid on",
            "swept through fine leg!",
        ],
        6: [
            "advances down the ground and launches it out of the park!",
            "down the track and smashed over long on!",
            "slog-sweeps it into the stands!",
            "switch-hit! what audacity, and it's gone all the way for six!",
        ],
        "ground_shot": [
            "between short leg and silly mid on",
            "danced down the track and worked it away",
            "swept fine for a single",
        ],
    }

    # the last over of a limited-overs innings, where nobody is playing
    # proper cricket any more: sweeps, switch hits, scoops, ramps, charges
    # down the track. Replaces the ordinary pools wholesale for that over
    # (see Match._FieldShotPool). Fragments, read as "<shot> FOUR!" / "SIX!"
    fields_last_over = {
        4: [
            "reverse sweep, and it races away!",
            "switch hit! that's outrageous",
            "scooped over the keeper's head!",
            "down the track and lofted over mid-off!",
            "paddle sweep, fine and fast!",
            "reverse paddle, the keeper had no chance",
            "charged down and drilled through the covers!",
            "slog sweep, bisecting the fielders!",
            "a cheeky dab past the keeper!",
            "walked across and flicked it fine!",
            "the reverse scoop! what audacity",
            "backed away and carved it over point!",
            "shuffled across and swept it round the corner!",
            "helicopter shot! wristed away through midwicket!",
            "dilscoop! straight over the keeper!",
            "reverse hit over backward point!",
            "down on one knee, slogged through midwicket!",
            "gave himself room and smashed it through cover!",
            "the lap shot, past short fine leg!",
            "switched hands and carved it away!",
            "stepped away to leg and drove it over extra cover!",
            "premeditated sweep, and it beats the man!",
            "a scoop off the full toss, over the keeper!",
            "ran down the pitch and clipped it wide of mid-on!",
            "the reverse lap, and it's away!",
            "shimmied down and steered it past point!",
            "audacious! a paddle over the keeper's shoulder!",
            "inside-out over cover, made room for it!",
            "walked at the bowler and whipped it through square leg!",
            "a slog across the line, and it's found the gap!",
        ],
        6: [
            "scooped straight over the keeper's head!",
            "slog sweep into the stands!",
            "down the track and launched over long-on!",
            "switch hit! unbelievable!",
            "scooped over fine leg, all the way!",
            "reverse sweep, that's audacious!",
            "the helicopter shot, and it's cleared midwicket!",
            "charged and hoisted it over long-off!",
            "backed away and carved it over point!",
            "the dilscoop, straight back over the umpire's head!",
            "on one knee, slog-swept over deep square!",
            "reverse lap! the crowd can't believe it!",
            "made room and hammered it over extra cover!",
            "down the track, inside-out, over cover!",
            "flat-batted straight back over the bowler!",
            "the paddle scoop, clean over fine leg!",
            "switched hands and lofted it into the stands!",
            "stepped outside leg and hit it over long-on!",
            "reverse pull! that's gone the distance!",
            "shimmied down and deposited it over long-off!",
            "the reverse scoop over point, and it's gone!",
            "premeditated slog, clean over the rope!",
            "a wild swing, but he's connected - over midwicket!",
            "the reverse scoop! extraordinary!",
            "lap-swept over short fine leg and away!",
            "walked at the bowler and crunched it over long-on!",
            "a brazen scoop, sailing over fine leg!",
            "gave himself room and launched it over cover!",
            "the slog sweep, and it's a monster!",
            "danced down and swung it over the sightscreen!",
        ],
    }

    # ramps and upper cuts need real pace to work with - these join the
    # last-over pool only off a quick, so a spinner is never "upper cut"
    fields_last_over_pace = {
        4: [
            "ramped over the slips!",
            "upper cut over point!",
            "a ramp off the quick, past the keeper!",
            "upper-cut over the keeper's gloves!",
        ],
        6: [
            "upper cut, and it's sailed over third man!",
            "a ramp off the quick, over the keeper's head and gone!",
            "upper cut over the slip cordon and into the crowd!",
            "used the pace, ramped it over the rope!",
            "ramp shot over the keeper!",
            "the ramp over point, and it's gone!",
            "audacious ramp, sailing over the keeper!",
        ],
    }
