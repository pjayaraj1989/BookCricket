# all the commentary phrases are defined here


# commentary phrases
class commentary:
    """
    A class to hold all the commentary phrases used in the game.
    """

    intro_game = (
        "*" * 50
        + "\n"
        + "*" * 14
        + "Book Cricket Simulator"
        + "*" * 14
        + "\n"
        + "*" * 50
    )

    intro_dialogues = [
        "Welcome everybody! Here we are, at ",
        "Hello everyone, here we are, at ",
        "Hello and welcome everyone, to, ",
        "Electrifying atmosphere here at, ",
        "Warm welcome to everybody, to ",
    ]

    # comment shown on the "Team A vs Team B" pop-up right after teams are picked
    commentary_contest_preview = [
        "it's going to be a high-class contest!",
        "this promises to be a cracker of a game!",
        "two evenly matched sides - buckle up!",
        "this has all the makings of a classic!",
        "expect fireworks out there today!",
        "a mouth-watering contest on the cards!",
        "this one could go right down to the wire!",
        "a real heavyweight clash coming up!",
        "the stage is set for a thriller!",
        "this is the contest everyone's been waiting for!",
        "both sides will fancy their chances here!",
        "get ready for a cracking contest!",
        "this rivalry always produces a good game!",
        "a blockbuster contest awaits!",
        "this could be one for the ages!",
        "two quality sides going head to head!",
        "the crowd is in for a treat today!",
        "this fixture never disappoints!",
        "all set for an enthralling battle!",
        "this looks like a proper contest!",
    ]

    # Run rates
    commentary_less_req_rate = [
        "looks easily gettable for %s",
        "not a big task for %s at all!",
        "target looks easy for %s , but they are going to face some quality bowling attack!",
        "looks like an easy target for %s!",
    ]
    commentary_high_req_rate = [
        "required rate is really high for %s!",
        "this is gonna be a tough chase for %s!",
        "a big target for %s and they will be facing a tough bowling attack too!",
        "a himalayan task ahead for %s! need to bat really well!",
        "that's a big task ahead for %s, and will be facing some quality pace attack too!",
    ]
    # comment situation based on Reqd RR
    commentary_situation_reqd_rate_low = [
        "%s well on course here!",
        "the required rate looks easily gettable for %s!",
        "this chase looks easy for %s!",
        "this chase is on.. good display %s!",
        "%s are cruising here!",
        "%s look relaxed as the asking rate is looking easy!",
        "%s really know their target.. well on course!",
        "%s are punishing the bowlers here! required rate is less than required",
        "%s can get home without any hurdles with this scoring rate!",
        "%s are chasing well here!",
    ]

    commentary_situation_good_rr = [
        "%s going at a terrific run rate so far!",
        "terrific run rate so far for %s",
        "great run rate so far for %s",
        "%s cruising at a terrific pace!",
    ]

    commentary_situation_low_rr = [
        "run rate looking just fine for %s",
    ]

    commentary_situation_no_wkts_fell = [
        "no wickets fell so far for %s",
        "no damages as of now for %s",
        "no wickets fell so far, going fine %s",
    ]

    commentary_situation_reqd_rate_high = [
        "required rate is high for %s!",
        "%s need to push themselves hard to stay on course!",
        "%s need some big hits to boost the run rate!",
        "singles and doubles won't take %s home!",
        "%s need to boost the run rate!",
        "required rate is going higher for %s... pressure building!",
        "bowlers are not giving %s room to keep up with the required rate!",
        "%s will have to struggle to get home with this scoring rate!",
        "chase looks pretty sluggish for %s!",
        "%s need some hard hitters to stay alive in this chase!",
        "%s really need to boost up the run rate here!",
    ]

    commentary_situation_unstable = [
        "%s are looking unstable here!",
    ]

    commentary_situation_trouble = [
        "%s in real trouble here",
    ]

    commentary_situation_got_wkts_in_hand = [
        "%s have got enough wickets in hand though!",
    ]

    commentary_situation_shouldnt_lose_wks = [
        "%s should not lose more wickets..",
        "%s can get home if they don't lose more wickets..",
    ]

    commentary_situation_gone_case = [
        "this looks literally impossible for %s now!",
        "%s need some miracle now to win this from here!",
    ]

    commentary_situation_savior = [
        "its all over i feel, but if anyone could save them from here, it will be %s",
        "tough game for them, but if they make it, it has to be %s",
        "a lot rests on the shoulders of %s",
    ]

    commentary_situation_major_contr_batting = [
        "it was that man %s who majorly contributed so far!",
        "it was %s show today here!",
        "major batting contributor was %s today!",
    ]

    commentary_situation_major_contr_bowling = [
        "it was %s who did most of the damage today!",
        "it was %s who was the star with ball today!",
        "major damage done by %s in the bowling dept.",
    ]

    # comments for diff shots
    commentary_six = [
        "that's in the stands! ",
        "that's launched into orbit!",
        "he's picked the length early and deposited it over the ropes!",
        "clean as a whistle, straight down the ground for six!",
        "the crowd is on its feet, that's a monster hit!",
        "no fielder was going to stop that one!",
        "right off the middle and it has sailed over the rope!",
        "he goes bang ! that's a big one!",
        "smashed it out of the park!",
        "where do you set fielders for this man!",
        "oh what a shot! That has been smashed out of the ground!",
        "stand and deliver!",
        "picked up the slow ball well and hit really hard!",
        "he has blazed that one! go fetch that!",
        "that's gone miles in the air!",
        "he is dealing in sixes here!",
        "loose delivery and punished hard!",
        "what a biggie! it has gone into the trees!",
        "the batsman has decided that tonight's gonna be his night!",
        "fielder in the deep will just watch it sail over the fence!",
        "will this be taken in the deep.. no its 6!",
        "that's a powerful shot.. will be a one bounce.. not its gone all the way for 6!",
        "that's one of the biggest sixes ever!",
        "that is gone, and forgotten! what a hit!",
        "that's a flat six! beautifully hit!",
        "that's big and the crowd will catch it! ",
        "boy what a hit!",
        "that's huge, its out of here!",
    ]
    commentary_four = [
        "what a shot!.. that will find the fence!",
        "threaded the gap beautifully and it races away to the fence!",
        "silky timing, no power needed for that one!",
        "leans into the drive and its four all the way!",
        "cut hard and it flies to the boundary!",
        "clipped off the pads, four more!",
        "the gap was there and he found it, four runs!",
        "short and wide and punished hard!",
        "that's the shot of the day for me!",
        "oh will this be taken in the deep, oh he has dropped it.. and its 4!",
        "the crowd is loving this!",
        "fielder in pursuit... wont get there..",
        "beautiful drive and the fielder has given up the chase!",
        "into the gap for four!",
        "pierced the gap for four!",
        "smashed through the gap!",
        "poor delivery and deserved to be hit!",
        "long chase for the fielder... and the ball wins the race!",
        "how do you set fields for this batsman!",
        "bad ball and punished!..",
        "bad delivery.. it had 4 written all over it!",
        "well connected!.. that will go to the boundary",
        "Great shot! Absolutely magnificent!. And the batsman has not moved an inch!",
        "that will find the fence!",
        "magnificent shot!.. ",
        "oh unbelievable timing!",
        "Beautiful shot.. oh sloppy fielding in the deep!",
        "When He Hits It, It Stays Hit !",
        "he is getting warmed up here!",
        "boy what a shot!",
        "right out of the middle of the bat!",
        "what a smash!",
        "He's a better player than his statistics suggest",
        "that's a great lesson for any youngster watching !",
        "Terrific batting this.. what would be the reply from the bowler?",
        "Another one of those, and there will be a chat between the bowler and his captain!",
        "he goes bang!",
    ]
    commentary_ground_shot = [
        "not timed well but will get some runs",
        "found the gap well",
        "good ball ! but well played into the gap",
        "into the gap",
        "good delivery and somehow the batsman manages to get some runs out of it",
        "very quick running",
        "he has to hurry!",
        "well played into the gap",
        "edged and dropped!!! oh what a miss",
        "in the air, dropped! batsman will get some runs too!",
        "poor fielding, that's gifting singles and doubles to the batsman!",
        "sloppy fielding, useful singles and doubles for the batsman",
        "Oooh! direct hit and he would've gone!",
        "that's quick running!",
        "not timed well but lazy fielding, bowler is not happy!",
        "singles and doubles will surely irritate the fielding captain",
    ]

    # if taken a wicket as well as scored runs in the first innings
    commentary_all_round_bowler = [
        "it was %s with the bat, now with the ball!",
        "oh %s is a brilliant all rounder!",
        "a brilliant bowler %s is, who had a great innings earlier today as well!",
        "%s had a good day with the bat, now he strikes with the ball too!",
    ]
    commentary_all_round_batsman = [
        "he had a good day with the bat and with the ball !",
        "he is a master all rounder!",
        "he is all over the ground today, earlier with the ball, now with the bat!",
    ]
    # check if fielder is good on field
    commentary_fielder_on_fire = [
        "oh this man %s is having a good day on the field!",
        "its that man %s again!",
        "oh %s, he is a live wire on the ground!",
        "%s! he is super fast on the field!",
    ]

    # first runs of  the day for the team
    commentary_first_runs = [
        "first runs of the day for %s and %s",
        "he's away! first runs on the board for %s and %s",
        "%s are off the mark, and it's %s with the first runs",
        "%s are off the mark and it's %s to open the account",
        "%s off the mark with %s getting the first runs",
        "%s, and also %s are up and running",
        "%s and %s are away with that!",
    ]

    # first boundary of the innings
    commentary_first_four_team = [
        "first boundary of this innings!",
        "there is the first one to cross the fence!",
        "first 4 of the innings",
        "first boundary, and it came in style!",
        "that's the first boundary, no wonder it came from him!",
    ]

    commentary_first_six_team = [
        "first sixer of this innings!",
        "there is the first one to sail over the fence!",
        "first 6 of the innings!",
        "first six!, and it came in style!",
        "there is the first biggie.. it came in style!",
        "that's the first maximum, no wonder it came from his bat!",
    ]

    # four first  ball
    commentary_firstball_four = [
        "what a way to start the innings!",
        "glorious start to the innings!",
        "he starts with a bang! no pressure at all!",
        "explosive start! bowler is stunned!",
        "bowler feels the pressure now! first ball has been smoked!",
        "well what a start! the first ball has been hit for a boundary",
        "that's how you start an innings! pressure straightway on the bowler now!",
    ]
    commentary_firstball_six = [
        "six of the first ball!",
        "would you believe it! six of the first ball!",
        "explosive start! bowler is stunned!",
        "bowler looks shell shocked! first ball has been smashed!",
        "first ball and its dispatched! Beware bowlers!",
        "bang! he has smashed the first ball out of here!",
        "that's how you start an innings! pressure straightway on the bowler now!",
        "that's hit off the first ball!.. ",
    ]

    # captain next:
    commentary_captain_to_bat_next = [
        "the captain walking out to the middle!",
        "the skipper to bat next!",
        "and now we have the captain at the crease",
        "the captain now has a job to do!",
        "crowd cheering as the captain walks out to bat",
        "the skipper, to walk into the ground now",
        "huge applause as the captain is going into the middle",
    ]
    # captain out
    commentary_captain_out = [
        "got rid of the skipper!",
        "the captain goes!",
        "got the skipper!",
        "that's the end of the captain!",
        "yes! the skippers is gone!",
    ]
    # captain leading
    commentary_captain_leading = [
        "captain leading from the front",
        "captain courageous!",
        "that's how you lead your team! bravo skipper!",
        "he is a perfect example of a brave leader!",
        "the skipper leading from the front here",
        "this is what leadership looks like!",
        "the captain shows the way!",
        "true leaders lead by example, and there it is!",
        "the skipper putting the team on his shoulders!",
        "a captain's knock if there ever was one!",
        "leading from the front, exactly when the team needs it!",
        "that's a captain's innings right there!",
        "the armband means more today - what an effort from the skipper!",
        "the leader delivers when it matters most!",
        "textbook captaincy - inspire the team by doing it yourself!",
        "the skipper answers the call in style!",
        "that's why he wears the armband!",
        "the captain sets the tone for the whole side!",
        "leading with the bat/ball, exactly as a captain should!",
        "a champion leader, delivering a champion moment!",
    ]

    # comments for wkts
    commentary_one_down = [
        "they draw first blood!",
        "the opening stand is broken!",
        "first one down!",
        "the bowling team draw first blood!",
        "one down!",
    ]
    # half the side is down
    commentary_five_down = [
        "half the side is back in the pavilion!",
        "job half done!.. 5 wickets down!",
        "5 down and i am afraid the flood gates have opened!",
        "half down and the tail is exposed!",
    ]
    # commentary last man
    commentary_lastman = [
        "last man coming out to bat!",
        "9 down, last wicket coming out to bat",
        "now they will be trying to mop up the tail!",
        "tail ender coming out into the middle!",
    ]

    # diff types of dismissals
    commentary_hit_wkt = ["gone! he has hit the stumps!"]
    commentary_bowled = [
        "timber! the stumps are shattered!",
        "through the gate! completely beaten!",
        "castled him! that's a beauty!",
        "the off stump is cartwheeling!",
        "played all around it, bowled!",
        "full and straight what a ball",
        "what a yorker! he is on fire!",
        "bowled him!",
        "poor footwork!.. bowled him",
        "got him! and the bowler lets out a roar!",
        "perfect length, that has hit the top of off-stump!",
        "Middle stump out of here",
        "inside edge and bowled!",
        "dragged on to the stumps",
        "done him and shattered the stumps!",
        "he has made an awful mess of the stumps!",
        "knocked him over with a ripper!",
        "oh hes played it on!.. Batsman would be so disappointed",
        "oh what a delivery!.. Perfect line and length!",
        "Bowled him!! comprehensively bowled!",
        "knocked his stumps over!",
        "off stump out of the ground!",
        "off stump is rattled!",
        "bowled him! You beauty!",
        "done him! peach of a delivery!",
        "Knocked his middle stump out!... And there is a stare at the batsman!",
        "Bowled him! And he is showing the batsman the way to the dressing room!",
        "done him with a toe crushing yorker!",
        "oh bowledimm!, an unplayable delivery!",
    ]
    commentary_in_a_row = [
        "that's 3 in a row!",
        "three in a row now!, bowler is clueless here",
        "three in a row!",
    ]
    commentary_boundary_after_wkt = [
        "what a response after a wicket!",
        "well.. thats the response after a wicket!",
        "thats how you should reply after a wicket!.. no pressure at all!",
        "hows that reponse after a wicket!",
    ]
    commentary_reverse = [
        "Oh that's reversed!",
        "the ball has reversed!",
        "he gets it to reverse!",
        "oh yes he gets it to reverse!",
        "reverse swinging delivery !",
        "magnificent reverse swinging delivery!",
        "brilliant reverse swinger this!",
    ]
    commentary_swing = [
        "Terrific in-swinger!",
        "superb in-swinger!",
        "out-swinging delivery!",
        "wild swinging delivery!",
        "what a peach! that swung inside! ",
        "beautiful seam position.. swinging in!",
        "he has this ability to swing the ball both ways!",
        "that's quick and it swung a long way!!",
        "oh that swung a long way!",
        "brilliant out swinger!",
        "unbelievable swing!",
    ]
    commentary_turn = [
        "that ball turned a long way!",
        "oh that spun a long way!",
        "terrific spin bowling this!",
        "terrific spin! the batsman cant believe it!",
        "oh it turned a long way! surprised even the bowler!",
        "what a turn! the batsman is stunned!",
        "that spun like never before!",
        "deceived by the googly!",
        "that was the one which didn't turn!,, batsman is fooled!",
        "that ball turned so sharp!!",
        "that was the wrong-un!",
        "a ripsnorter!",
        "beautiful top spinner!",
        "what a delivery!.. terrific spin!",
        "oh what a turn! and the batsman is fooled completely!",
        "what a turn! it has stunned the batsman!",
    ]
    commentary_runout = [
        "what a terrible mix up between %s and %s!",
        "this is bizarre!.. terrible miscommunication between %s and %s",
        "dead accurate throw from the fielder!.. poor call from %s and %s pays the price!",
        "this is poor running from %s! that was a wrong call from %s!",
        "magnificent fielding.. brilliant throw!.. and both %s and %s messed it up",
        "%s, no! %s is calling for the second.. direct hit and gone!",
        "that was a horrible call by %s and %s!",
        "there was absolutely no run there! poor running between the wickets between %s and %s!",
        "that is horrific! where was the run there %s?.. it was a call from %s",
        "lazy running between the wickets at this stage of the match by %s and %s!",
        "horrible running between the wickets by %s and %s!",
        "magnificent throw and %s knows it! good fielding!.. poor call from %s",
        "brilliant throw and good collection! umpire need not review this!.. terrible from %s and %s",
        "there was no run there! this is bizarre!. was it %s s call? i think it was %s",
        "rocket arm from the fielder! what a throw!.. and ends a partnership between %s and %s",
        "direct hit and gone!.. both %s and %s will be kicking themselves",
        "that's gone.. run out!! never run off a mis-field, %s and %s!",
        "what was the batsmen thinking!?.. poor start by %s it was initiated by %s i guess!",
    ]
    commentary_stumped = [
        "swift work by the keeper %s!",
        "that's out! stumped.. bravo %s!",
        "%s takes the bails off in a flash!",
        "that spun hard, batsman misses and quick work behind the stumps by %s!",
        "tries for a wild shot and missed it.. quick stumping by %s!",
        "batsman misses it and swift work %s!",
        "stumped, %s looks confident, no need to refer it!",
        "%s's fast hands behind the stumps!",
        "very quick piece of stumping by %s!",
        "terrific stumping by %s!!",
        "quick stumping! %s appeals, umpire says out!",
        "the keeper is lightning quick %s!",
    ]
    commentary_caught = [
        "in the air.. and taken by %s!",
        "that's straight up in the air.. %s calls for it, taken!",
        "bad shot.. leading edge and gone.. good take by %s!",
        "outside edge and a magnificent catch! you beauty %s",
        "that's not timed well and oh what a catch by %s!",
        "in the air that's taken by %s! what a blinder!",
        "brilliant catch! %s is a supreme athlete!",
        "oh man! what a catch by %s! one of the best catches ever!",
        "that's in the air, %s is underneath it, has he dropped it, no he hasn't! what a catch!",
        "that's hit straight down %s's throat!",
        "hit in the air and what a catch!...unbelievable catch by %s!",
        "straight up in the air.. %s says mine.. takes it in the end!",
        "hit very hard but straight to %s.. batsman cant believe what he has done!",
        "magnificent catch by %s..! ..diving in the air!",
        "in the air and taken by %s! batsman looks shell shocked! what a catch!",
        "hit in the air...brilliant dive by %s! what a take! batsman looks stunned!",
        "up in the air and oh what a catch! one handed by %s!",
        "hit hard to the fielder and %s takes it!",
        "hit straight down %s's throat!",
        "in the air and oh! has he taken that? He has! %s! what a catch!",
    ]
    commentary_keeper_catch = [
        "edged.. and taken by the keeper %s!",
        "got him, yes.. caught behind!.. good take by %s",
        "there is an edge and what a catch by the keeper %s!",
        "thin edge, big appeal by %s! given!",
        "is there an edge? %s looks confident! Yes it is!",
        "edged and brilliant dive by %s!",
        "big deflection and yes! safely taken by %s",
        "ooh there is an edge? %s appeals, bowler appeals...given!",
        "outside edge and brilliantly taken by %s!",
        "oh is there a nick!? %s thinks so, Batsman is walking...!",
        "straight up in the air, %s says mine and takes it!",
    ]
    commentary_return_catch = [
        "beautiful return catch by %s!",
        "oh what a return catch by %s!",
        "oh he has dropped.. no he hasn't! what a catch by %s!",
        "that's out, caught n bowled by %s!",
        "caught and bowled by %s! what a reflex!",
        "what kind of reflexes by %s! That's taken!",
        "full toss, and hit it straight back at the bowler! what a take %s",
        "hit it hard but taken by the bowler himself!.. you beauty %s",
    ]

    # dramatic over
    commentary_dramatic_over = [
        "it has been a dramatic over so far!",
        "really exciting over this for the crowd",
        "the crowd loved this over so far! an entertainer",
        "a dramatic over so far!",
    ]

    # modify this as per DRS
    commentary_lbw_umpire = [
        "big appeal.. and %s's finger goes up!",
        "that looks in line and %s says out!",
        "looks plumb, and %s's finger raises!",
        "hit on the pads! and given out by %s!",
        "looks dead straight to me... and %s says out!",
        "that's a big appeal.. and finally given lbw by %s!!",
        "the bowler pleads with %s, and finally given!",
        "big appeal.. and the umpire %s says out! oh that looks like a harsh decision!",
    ]
    commentary_lbw_drs_taken = [
        "%s looks confused.. long chat with his partner %s.. and finally takes it upstairs!",
        "%s is desperate here, long discussion with %s.. and finally decides to go for the D.R.S",
        "Oh they had a quick chat, %s and %s, and they are going with the D.R.S.. looks like a review wasted?",
        "%s is quickly having a chat with %s.. and decides to opt for the D.R.S",
        "This is a tough call.. Will they waste a D.R.S chance here? %s looks confident, "
        "but %s doesn't!",
        "well, %s hasn't even discussed with %s, has gone upstairs instantly!",
        "well %s has gone for the review instantly.. didn't even look at %s!",
    ]
    commentary_lbw_drs_not_taken = [
        "he is having a long chat with the non striker.. and finally he is walking off..",
        "it looked close to me, he discusses with the non striker, will not be wasting a "
        "D.R.S chance here",
        "Will he go upstairs ? don't think so.. a nod at his partner, and he is walking off the field",
        "are they going for the D.R.S here? I don't think so they are interested..",
    ]
    commentary_lbw_decision_stays = [
        "Well it shows that the ball will be hitting the top of off!. Decision stays.. good on field call %s!",
        "Pitching in line, impact in line.. hitting middle.. %s gets it dead right!!",
        "missing leg? No! that's out.. %s gets it right again!",
        "Its pitching in-line! Hitting middle and leg.. %s"
        "s decision stays! He has to go!",
    ]
    commentary_lbw_overturned = [
        "It shows the ball missing the stumps by an inch! not out!",
        "Impact in line, but wickets missing!",
        "pitching in line, impact in line, wickets.. missing! good review!",
        "Oh that's missing the top of off by inches!.. decision will be overturned!",
    ]
    commentary_lbw_edged_outside = [
        "DRS says there is bat involved! Overturned!.. well that saves them a review",
        "impact outside leg!.. this will be overturned",
        "impact outside off!...",
        "pitching outside off.. impact outside off!",
        "DRS says that's pitching outside leg! Not out!",
        "there is a slight nick!.. ",
        "Oh there is an inside edge...? This will be given not out!",
    ]
    commentary_lbw = [
        "trapped %s in front! ",
        "given out, %s is not happy at all",
        "%s doesnt look happy! he is shaking his head!",
        "%s shakes his head",
        "he knew it.. %s walks away..",
        "%s looks unhappy, he thinks it was outside the line",
    ]
    commentary_lbw_nomore_drs = [
        "they do not have any more DRS reviews left!",
        "they have used all their review chances!",
        "No more reviews left!",
    ]

    # last over of a chase - a tension line for each ball (5 are picked at
    # random from this pool at the start of the over)
    commentary_last_over_tension = [
        "the stadium is on its feet!",
        "tension time here at the ground!",
        "you could cut the atmosphere with a knife!",
        "nobody in this crowd is sitting down now!",
        "the nerves are jangling out in the middle!",
        "this is exactly what we came to see!",
        "the crowd is roaring on every single ball!",
        "hearts in mouths in both dressing rooms!",
        "the pressure out there is immense right now!",
        "the captain can barely watch from the dugout!",
        "what a finish this is turning out to be!",
        "the noise here is absolutely deafening!",
        "every single run counts now!",
        "the fielders crowd in.. the tension is unbearable!",
        "the bowler takes a deep breath.. here we go!",
        "the whole ground is holding its breath!",
        "you can feel the tension right up in the stands!",
        "the batsmen have a long chat.. the nerves are showing!",
        "this is high drama at its very best!",
        "goosebumps all around the ground!",
    ]

    # the final ball of a chase - a stronger line than the rest of the over
    commentary_last_ball_tension = [
        "IT ALL COMES DOWN TO THIS! ONE BALL LEFT!",
        "THIS IS IT! THE FINAL BALL OF THE MATCH!",
        "EVERYTHING RIDES ON THIS ONE DELIVERY!",
        "THE WHOLE MATCH IN ONE BALL! UNBEARABLE!",
        "LAST BALL! THE GROUND IS ABSOLUTELY ELECTRIC!",
        "ONE BALL TO DECIDE IT ALL! HOLD YOUR BREATH!",
    ]

    # the appeal for a catch, before the batsman decides whether to review
    commentary_caught_appeal = [
        "looks like there is an edge, and they are appealing!",
        "huge appeal for the catch! the umpire raises his finger",
        "the keeper and the slips go up in unison.. and that's given out!",
        "there was a noise there! the fielders are convinced and the umpire agrees",
        "did that carry? the fielders think so, and the umpire has given it!",
        "an outside edge maybe? big appeal, and up goes the finger!",
    ]

    # review shows no edge - the catch decision is overturned
    commentary_caught_overturned = [
        "no spike on ultra-edge! that's not out, brilliant review!",
        "the bat was nowhere near it! the decision is overturned",
        "flat line on the snicko.. no edge! the batsman survives",
        "it came off the pad, not the bat! not out, great review",
    ]

    # review shows a clear edge - the catch decision stays
    commentary_caught_decision_stays = [
        "there's the spike! a clear edge, and %s got it spot on",
        "ultra-edge confirms it, he has nicked it! %s was right all along",
        "a big deflection off the bat! decision stays, well done %s",
        "that's a clear edge, the on field call from %s stands.. he has to go",
    ]

    # the bowling side appeals for a wicket (lbw/catch) and the on-field
    # umpire gives it not out - a shout they can review on their own DRS quota
    commentary_bowling_appeal = [
        "huge appeal from the bowling side!.. but %s says not out!",
        "they go up as one!.. turned down by %s!",
        "that looked close, but %s is unmoved!",
        "a big shout there, and %s shakes the head!",
        "the fielding side can't believe it!.. not out says %s!",
        "that's given not out by %s, much to the bowlers' disappointment!",
        "a confident appeal, but %s isn't interested!",
        "they were so sure of that one!.. %s says not out!",
        "the whole team goes up!.. %s waves it away!",
        "not given by %s - the bowling side look stunned!",
    ]

    # bowling-side review overturns the not-out call - the batsman is out after all
    commentary_bowling_review_success = [
        "the review shows they were right all along! %s get their wicket!",
        "overturned! %s have their man after all!",
        "the replay proves it - out! great review from %s!",
        "%s were right to review that - the batsman has to go!",
        "the technology backs the bowlers! %s celebrate!",
        "that's out on review! superb call from %s!",
        "the third umpire agrees with %s - he's got to go!",
    ]

    # bowling-side review fails - the not-out call stands, a chance is burnt
    commentary_bowling_review_fail = [
        "the review confirms it - not out! %s lose a review!",
        "no joy for %s - the on-field call stands!",
        "the replay backs the umpire! %s have burned a review!",
        "not out, and %s pay the price for that review!",
        "the technology sides with the batsman - %s lose a chance!",
        "that's stayed not out - costly review from %s!",
        "the umpire's call is upheld - %s down a review now!",
    ]

    commentary_dropped = [
        "that's hit straight up in the air, %s says mine.. oh and put down!",
        "edged and dropped at first slip by %s! disappointment for the bowler.. oh dear!.. batsman is lucky !",
        "in the air and oh.. ! put down by %s.. sigh of relief for the batsman!",
        "good delivery, thats in the air but drops safe.. just bounces in front of %s",
        "well bowled. he hits in the air and chance goes down! goodness me! catches win matches.. costly miss from %s",
        "well bowled, that's in the air and this should be out. oh dropped by %s! goodness me, how lucky are you!!",
        "very good ball. he has hit it straight up in the air, oh %s has dropped it!",
        "in the air ..taken..? i think the fielder %s says the ball has touched the ground",
    ]

    commentary_dropped_keeper = [
        "that's hit straight up in the air, keeper %s says mine.. oh and put down!",
        "that's in the air but put down by the keeper! oh what a miss from %s!!",
        "edged and taken.. no he has dropped it! oh %s... this could prove costly",
        "there is an edge, bowler appeals.. but looks like %s knows he has dropped it",
    ]

    # dot ball
    commentary_dot_ball_pacer = [
        "wild swing from %s and a miss from %s.. no run!",
        "its a short one from %s and hit %s on the shoulder!",
        "oh that is a nasty bouncer from %s! hit %s on the head!",
        "ooh what a ball %s!,.. it bounced and hit the batsman %s!",
        "oh terrific from %s .. that has hit the batsman on the helmet.. hope %s is fine!",
        "oh that's a quick delivery from %s.. %s looks unsettled!",
        "fast and swinging from %s, %s mistimes it.. no run!",
        "that looks close, but not out says the umpire! %s is unlucky and %s, you're a lucky man!",
        "beautiful slow ball from %s.. fooled %s!",
        "right in the block hole by %s! well negotiated by %s",
        "swings and misses.. a stare from %s! %s living dangerously!",
        "good ball from %s, %s hits well but straight to the man at short extra cover!..well fielded!",
        "well bowled %s, outside off and %s misses that!",
        "its fast and swinging dangerously from %s.. missed %s's off stump by inches!",
        "dangerous delivery from %s! batsman %s had no clue about it",
        "oh that was a quick one from %s, too good for %s!",
        "oh %s! that was perilously close to the off stump!, %s looking nervous here!",
        "that bounced too much from %s.. %s had no clue.. and well taken by the keeper too!",
        "dangerous short ball from %s.. %s didn't have a clue !",
    ]

    commentary_dot_ball = [
        "beautiful delivery from %s, missed %s 's stumps by inches!",
        "good from %s, that's very well defended by %s!",
        "well bowled %s and that's a solid defence from %s",
        "accurate from %s and that's a textbook defence from %s!",
        "big big appeal from %s... but umpire shakes his head!.. %s looks relaxed",
        "oh %s, He's Bowling a Good Line and Length.. %s looks unsettled",
        "swings and misses.. a stare from %s %s living dangerously!",
        "deceived the batsman.. and %s gives %s a stare!",
        "big appeal from %s.. but umpire says not out! %s looks nervous",
        "that looks close, but not out says the umpire! %s is unlucky and %s, you're a lucky man!",
        "missed it, there is a stare from %s at %s",
        "oh swing and a miss!.. well bowled %s! %s is looking nervous!",
        "good ball from %s, %s hits well but straight to the man at short extra cover!.. well fielded!",
        "magnificent delivery from %s.. just above %s 's bails to the keeper!",
        "oh what a ball from %s ! tantalizingly close to the stumps... a near miss for %s!",
        "%s thinks there is an edge..? keeper is appealing.. %s looks unhappy! but the umpire shakes his head!",
        "magnificent from %s, deceived %s and nearly missed the off stump",
        "beautiful slow ball from %s.. fooled %s!",
        "bad ball from %s but that's hit in the air by %s, but falls in no man's land",
        "full from %s, driven nicely by %s but the fielder was lightning quick! saved a certain boundary!",
        "a little short from %s, played well by %s but straight to the fielder!",
        "slower ball from %s and %s misses it!",
    ]

    # score reach 50/100/200/300
    commentary_score_fifty = [
        "50 up for %s..",
    ]
    commentary_score_hundred = [
        "hundred up for %s !",
    ]
    commentary_score_two_hundred = [
        "200 up for %s..",
    ]
    commentary_score_three_hundred = [
        "300 up for %s..",
    ]

    # MILESTONES
    commentary_partnership_milestone = [
        "this has been a terrific partnership between %s and %s!",
        "what a partnership this has been between %s and %s!",
        "what a useful partnership this by %s and %s!",
        "this was a magnificent partnership by %s and %s",
        "take a bow %s, %s, one of the best partnerships ever!",
        "ends a terrific partnership between these two.. good work %s, %s!",
    ]

    # a big (50+) partnership finally broken - shown with the bowler's pic,
    # or the fielder's pic if it was a run-out
    commentary_breakthrough = [
        "a breakthrough which %s badly wanted!",
        "that's the breakthrough %s were desperate for!",
        "finally, the breakthrough %s craved!",
        "the partnership is broken - exactly what %s needed!",
        "a huge breakthrough for %s!",
        "%s finally get the breakthrough they were chasing!",
        "that's a massive wicket for %s!",
        "the stand is finally broken - big moment for %s!",
        "%s will be delighted to have finally broken through!",
        "a much-needed breakthrough for %s!",
        "that partnership had to be broken, and %s have done it!",
        "%s have finally found a way through!",
        "the pressure finally tells - a big breakthrough for %s!",
        "%s break the stand at just the right time!",
        "a vital breakthrough for %s!",
        "%s have been waiting for this one!",
        "that's the moment %s needed!",
        "the deadlock is broken - great news for %s!",
        "%s finally prise them apart!",
        "a game-changing breakthrough for %s!",
    ]

    # a big partnership broken, but too late to really matter - the chasing
    # side (%s) is still comfortably on top of the required rate regardless
    commentary_breakthrough_too_late = [
        "too little, too late - %s are already cruising!",
        "the damage is already done - %s are well clear!",
        "this won't change much - %s are firmly in control!",
        "a wicket, but %s are already home and hosed!",
        "too late to stop %s now!",
        "the game's already gone - %s won't be troubled by this!",
        "%s have done enough damage already!",
        "this breakthrough comes far too late for %s to worry!",
        "%s are cruising regardless of that wicket!",
        "the horse has already bolted - %s are coasting!",
        "a nice wicket, but the equation barely changes for %s!",
        "%s can afford to lose a couple more like that!",
        "this won't trouble %s much at this point!",
        "the contest is all but over for %s despite that wicket!",
        "too little to turn this one around against %s now!",
        "%s are cruising to victory regardless!",
        "the writing's already on the wall - %s are cruising!",
        "a consolation wicket at best - %s are well ahead!",
        "the damage was done long before this wicket - %s are in charge!",
        "%s remain firmly in the driver's seat!",
    ]

    # "how's the chase going" verdict pop-up (see Match._ClassifyChase /
    # _PushChaseAssessment) - one tier per difficulty read on the chase
    commentary_chase_cruising = [
        "%s are cruising towards this target!",
        "this chase looks like a formality for %s!",
        "%s in complete control of this chase!",
        "%s coasting home from here!",
    ]
    commentary_chase_on_track = [
        "%s right on top of the chase!",
        "%s ticking along nicely - right where they want to be!",
        "the chase is very much alive and well for %s!",
        "%s in good shape to get this done!",
    ]
    commentary_chase_in_balance = [
        "this chase is delicately poised for %s!",
        "could go either way from here for %s!",
        "%s need something special from here!",
        "the pressure is building on %s!",
    ]
    commentary_chase_tough = [
        "a real uphill battle for %s now!",
        "%s facing a stiff task from here!",
        "the required rate is climbing fast for %s!",
        "%s need a minor miracle from here!",
    ]
    commentary_chase_improbable = [
        "this is looking almost impossible for %s now!",
        "%s staring down the barrel here!",
        "the equation has gotten away from %s!",
        "%s need something extraordinary to pull this off!",
    ]

    # a bowler leaking too many extras (wides/no-balls) in one over
    commentary_too_many_extras = [
        "%s is really struggling with the line today!",
        "too many freebies from %s this over!",
        "%s needs to find his radar, and fast!",
        "the extras are piling up for %s!",
        "%s is gifting runs away here!",
        "that's a costly lapse in discipline from %s!",
        "%s just can't seem to find his rhythm!",
        "the captain won't be happy with %s right now!",
        "%s is handing out free runs like candy!",
        "a really sloppy over developing from %s!",
        "%s needs to tighten up in a hurry!",
        "that's far too generous from %s!",
        "%s is letting the batting side off the hook!",
        "the control just isn't there for %s today!",
        "%s is making this far too easy for the batters!",
        "some wayward bowling from %s here!",
        "%s will want to forget this over in a hurry!",
        "that's a concerning lack of discipline from %s!",
        "%s is spraying it all over the place!",
        "the extras column is getting embarrassing for %s!",
    ]

    commentary_out_first_ball = [
        "Out first ball.. %s has to go!!",
        "gone! %s is out without tickling the scoreboard!",
        "gone... first ball wicket, and nightmare for %s!",
        "Disappointment for %s! gone for a duck!",
        "That's a slow walk back when you're out first ball, %s!",
        "%s is out without disturbing the scoreboard!",
    ]
    commentary_nineties = [
        "Oh %s will be so disappointed! Gone in the nervous nineties!",
        "oh %s! what a shame! missed a deserving century!",
        "gone in the nervous nineties! %s will be so disappointed here!",
        "needless shot! lost a brilliant century from %s!",
        "oh gone in the nineties.. %s will be kicking himself!",
        "unlucky! gone in the nineties.. %s!",
        "oh missed a well deserving ton.. well played %s!",
    ]

    commentary_forties = [
        "Oh %s.. has lost a fifty!",
        "oh %s! what a shame! missed a deserving half century!",
        "gone in the forties! %s will be so disappointed here!",
        "needless shot! lost a brilliant half century from %s!",
        "unlucky! lost a fifty.. %s!",
        "oh missed a well deserving half century.. well played %s!",
    ]

    commentary_out_duck = [
        "The batsman will be so disappointed.. he is gone for nothing!",
        "gone for a duck! His nightmare continues!",
        "that's his second duck in a row in this season!",
        "slow walk back when you're gone for a duck!",
        "out for nothing!",
        "gone for none! The scoreboard is undisturbed by him!",
        "gone for zero.. disappointment for the batsman!",
        "he hasn't troubled the scoreboard!",
    ]
    commentary_out_fifty = [
        "what a valuable innings from %s!",
        "useful innings from %s comes to a close!",
        "terrific from %s! he is out but the damage is done!",
        "big applause from the crowd for %s!",
        "standing ovation for %s here!",
        "the crowd acknowledge this innings from %s! brilliant!",
        "the party is over, the crowd loved the innings.. take a bow %s!",
        "take a bow, what an innings it was from %s!",
        "terrific knock comes to an end from %s!",
        "end of an unbelievable innings from %s",
    ]
    commentary_wide = [
        "he has lost his line completely.. wide called by %s!",
        "oh that's a harsh call from %s!",
        "not good bowling from him!.. %s calls wide",
        "this will irritate the captain!.. another wide called by umpire %s",
        "he is leaking runs here!.. wide called again by %s",
        "leg side.. umpire %s says wide!",
        "poor bowling, wide delivery called by %s!",
        "oh big appeal from the keeper but Wide says %s!",
        "bowler under pressure here!.. %s signals wide again!",
    ]
    commentary_no_ball = [
        "good delivery , batsman misses it.. but No ball called!",
        "well bowled.. but no ball!",
        "he has lost his run up !",
        "oh that's a dangerous beamer! no ball called!",
        "bowler tries a full toss but that's way above the waist height!",
        "bowler loses his rhythm! no ball called",
        "bowled him! but oh that's a no ball!",
        "in the air and taken!. but no ball called!!",
        "oh that's a high full toss! no ball called!",
    ]

    # announced after a no-ball: the next delivery is a free hit
    commentary_free_hit = [
        "and that means the next ball is a FREE HIT!",
        "free hit coming up! the batsman can swing away without fear!",
        "it's a free hit! only a run out can get him now!",
        "here comes the free hit.. license to go big!",
    ]

    # the batsman is bowled/caught/lbw off a free hit - not out!
    commentary_free_hit_survived = [
        "he's cleaned him up.. but it's a FREE HIT! not out!",
        "that would have been the wicket.. but it's a free hit, he survives!",
        "up goes the finger.. no wait, free hit! the batsman lives on!",
        "beaten all ends up, but it doesn't matter - free hit, not out!",
    ]

    # a bowler strikes with the very first ball of an innings - no
    # placeholder, the pop-up shows both players' names
    commentary_first_ball_wicket = [
        "gone first ball! what a start!",
        "a wicket off the very first ball of the innings!",
        "the perfect start with the ball!",
        "first ball, and he's struck!",
        "dream start! a wicket with the very first delivery!",
        "no time to settle - out first ball!",
        "what a way to begin the innings!",
        "the bowler strikes with his very first ball!",
        "an early, early breakthrough!",
        "gone before the innings has even settled!",
        "the innings could not have started any worse!",
        "off the very first ball! sensational!",
        "a golden start for the bowling side!",
        "wicket first ball - dreamland for the bowler!",
        "the crowd has barely settled and there's a wicket!",
        "what a bolt from the blue, first ball!",
        "the opening delivery does the trick!",
        "first ball of the innings, and it's a wicket!",
        "an unplayable first ball!",
        "the breakthrough arrives immediately!",
    ]

    # crowd applause at a personal 50-run milestone - one placeholder, the
    # venue name, e.g. "the Adelaide Oval stands up for him!"
    commentary_milestone_applause = [
        "%s rises to its feet for him!",
        "what an ovation here at %s!",
        "the crowd at %s stands as one!",
        "%s salutes a superb knock!",
        "the roar around %s is deafening!",
        "%s is on its feet for this milestone!",
        "a standing ovation echoes around %s!",
        "the fans at %s roar their approval!",
        "%s rises to acclaim him!",
        "the applause rings out around %s!",
        "%s gives him a hero's reception!",
        "goosebumps around %s for this one!",
        "the whole of %s stands up for him!",
        "%s erupts in celebration!",
        "what a reception from the %s crowd!",
        "%s rises to salute the milestone!",
        "the noise at %s lifts another notch!",
        "%s shows its appreciation in full voice!",
        "a wonderful ovation here at %s!",
        "%s stands up to applaud a fine innings!",
    ]

    # a batsman one run short of a milestone (49/99/199) - no placeholder,
    # the pop-up already shows the batter's name
    commentary_approaching_milestone = [
        "one run away from a landmark!",
        "so close to a big milestone now!",
        "the nerves must be kicking in!",
        "just a single needed to get there!",
        "on the brink of something special!",
        "you can feel the tension building!",
        "one good shot away from glory!",
        "almost there.. just one more run!",
        "the milestone is well and truly in sight!",
        "heart-in-mouth stuff out in the middle!",
        "one run to tick off the landmark!",
        "steady now.. he's oh so close!",
        "the crowd senses a milestone coming!",
        "a single away from the mark!",
        "poised right on the edge of a milestone!",
        "just the one needed for the big one!",
        "nerveless he'll need to be right here!",
        "the landmark beckons!",
        "one run stands between him and the milestone!",
        "the whole ground is willing him to the mark!",
    ]

    # the opening pair walking out - two placeholders, both opener names
    commentary_openers_intro = [
        "%s and %s to get the innings underway!",
        "%s and %s stride out to open the batting",
        "it's %s and %s to face up to the new ball",
        "the opening pair %s and %s make their way to the middle",
        "%s and %s will look to give their side a flying start",
        "here come the openers, %s and %s",
        "%s and %s have the task of seeing off the new ball",
        "%s and %s out there to lay the platform",
        "the new-ball examination awaits %s and %s",
        "%s and %s walk out to a warm reception",
        "plenty riding on the openers, %s and %s",
        "first use of a fresh pitch for %s and %s",
        "%s and %s take guard to begin the innings",
        "all eyes on the top order as %s and %s get us going",
        "%s and %s to set the tone at the top",
        "a big role for the openers %s and %s",
        "%s and %s ready to take on the new ball",
        "the openers are out - %s and %s to start things off",
        "%s and %s stride to the crease to open up",
        "%s and %s to knock the shine off the new ball",
    ]

    # the opening bowler taking the new ball - one placeholder, bowler name
    commentary_opening_bowler_intro = [
        "%s will take the new ball",
        "%s to open the attack",
        "the batsmen will be facing %s first up",
        "%s gets the ball in hand to start the innings",
        "%s to steam in with the new ball",
        "first over of the innings, and it's %s",
        "%s has the shine to work with",
        "%s to lead the attack from one end",
        "the new ball goes to %s",
        "%s marks out his run-up to get us started",
        "%s will be hunting an early breakthrough",
        "up first with the ball is %s",
        "%s to test the openers with the new ball",
        "%s gets the nod to open the bowling",
        "the shiny new ball in the hands of %s",
        "%s to bowl the first over of the innings",
        "%s charges in to get the innings started",
        "%s has been handed the new ball",
        "%s to open up the bowling",
        "a probing first spell expected from %s",
    ]

    commentary_milestone = [
        "Its been a terrific knock by %s today..!",
        "what a fine innings this has been from %s!",
        "%s has led from the front today!",
        "take a bow %s, a knock to remember!",
        "%s has made batting look so easy out there!",
        "what a performance by %s...!",
        "Take a bow %s! What a knock!",
        "Absolutely magnificent innings %s!",
        "%s! he is playing a gem of an innings!",
        "this man %s is on fire today!",
        "%s decides tonight is going to be his night!",
        "that's it! A brilliant knock under pressure by %s!",
        "%s! he is on absolute fire here !",
    ]
    commentary_goingtolose = [
        "surely its all over now for %s!",
        "its literally impossible to win for %s now!",
        "that, I am sure, is the final nail on the coffin for %s!",
        "that's the end of all hopes for %s now!",
        "its surely all over for %s..!",
        "oh %s, they need some miracle to win this match!",
        "spare a thought for %s, one by one they are going down the drain!",
    ]
    commentary_fifer = [
        "what a bowler he is!",
        "five wickets in the bag, what a spell!",
        "he has ripped the heart out of this batting line-up!",
        "a well-deserved five-for, superb bowling!",
        "the batting side simply had no answer to him today!",
        "he has totally rattled this batting team!",
        "he is on absolute fire!",
        "he has been on fire with the ball today!",
        "that's a fantastic five-fer!",
        "he has intimidated every batsmen today!",
        "he has made an awful mess of this innings!",
    ]
    commentary_hattrick = [
        "that's it! that's a hat-trick !!",
        "three wickets in three balls, sensational!",
        "he was on a hat-trick and he has got it!",
        "unbelievable scenes, that's a hat-trick!",
        "he will remember this one forever, a hat-trick!",
        "Hat-trick for the bowler!",
        "3 in 3! This man is on absolute fire!",
        "hat-trick for the bowler! what a performance from him!",
        "the crowd is on its feet, what a hat-trick!",
        "he has etched his name in the record books, a hat-trick!",
        "pandemonium in the stands, that's a hat-trick!",
        "the stuff dreams are made of, a hat-trick!",
        "he has done it! a magical hat-trick!",
        "three in a row, the batting side has no answers!",
        "history made right here, a hat-trick!",
        "he will dine out on this one for years, a hat-trick!",
        "sheer magic! that's a hat-trick!",
        "the perfect over just got a lot better, hat-trick!",
        "a captain's dream, he's bagged his hat-trick!",
        "what a spell, capped off with a hat-trick!",
    ]
    commentary_on_a_hattrick = [
        "he is on a hat-trick now!",
        "two in two and he is on a hat-trick here!",
        "hat-trick ball coming up.. crowd on their feet!",
        "the tension is unbearable, he's on a hat-trick!",
        "one more and he's into the history books!",
        "the fielders are crowding round, hat-trick ball!",
        "you could hear a pin drop, hat-trick ball coming up!",
        "two down in two, can he make it three?",
        "the crowd rises in anticipation, hat-trick ball!",
        "everyone in the ground knows what's at stake, hat-trick ball!",
        "he smells blood, one more for the hat-trick!",
        "the captain has packed the slips, hat-trick ball incoming!",
    ]
    # each line takes exactly one %s: the wicket-streak count (N wickets off
    # N consecutive balls - the ball count is always the same number, so it
    # never needs its own placeholder)
    commentary_multi_wicket_streak = [
        "SENSATIONAL! %s WICKETS IN AS MANY BALLS!",
        "THIS IS CARNAGE - %s IN A ROW!",
        "UNPLAYABLE! %s STRAIGHT WICKETS!",
        "IS THIS EVEN LEGAL?! %s ON THE TROT!",
        "THE STUFF OF LEGEND - %s WICKETS IN AS MANY BALLS!",
        "HE HAS TORN THIS INNINGS APART - %s IN A ROW!",
        "SCENES! %s CONSECUTIVE WICKETS!",
        "A SPELL FOR THE AGES - %s STRAIGHT WICKETS!",
        "THE BATTING SIDE IS IN FREEFALL - %s IN A ROW!",
        "HISTORY IS BEING REWRITTEN - %s WICKETS IN AS MANY BALLS!",
        "ABSOLUTE DEMOLITION - %s ON THE BOUNCE!",
        "NOBODY HAS SEEN ANYTHING LIKE THIS - %s IN A ROW!",
        "HE IS UNSTOPPABLE - %s WICKETS IN AS MANY BALLS!",
        "THE CROWD CANNOT BELIEVE WHAT THEY JUST SAW - %s IN A ROW!",
        "A ONE-MAN WRECKING CREW - %s STRAIGHT WICKETS!",
        "SURELY THIS HAS NEVER HAPPENED BEFORE - %s IN A ROW!",
        "HE HAS LOST ALL SENSE OF MERCY - %s WICKETS IN AS MANY BALLS!",
        "THE OPPOSITION DRESSING ROOM IS STUNNED - %s ON THE TROT!",
        "PURE DEVASTATION - %s WICKETS AND COUNTING!",
        "THIS BOWLER IS WRITING HIS OWN CHAPTER TONIGHT - %s IN A ROW!",
    ]

    # big-screen "victory moment" flavor lines, shown immediately after the
    # ball that decides a run-chase - before the later, factual result/trophy
    # card. commentary_chase_success: the chasing side got there.
    # commentary_chase_failed: the chasing side came up short (the defending
    # side held on) - covers both "failed to chase" and "failed to defend"
    # framings, since they're the same outcome from opposite sides.
    commentary_chase_success = [
        "THEY'VE CHASED IT DOWN!",
        "TARGET OVERHAULED - WHAT A CHASE!",
        "THEY'VE GOT THERE!",
        "CHASE COMPLETE - JOB DONE!",
        "THEY'VE RUN DOWN THE TARGET!",
        "A CHASE FOR THE AGES - COMPLETED!",
        "THEY'VE PULLED IT OFF!",
        "MISSION ACCOMPLISHED - THE CHASE IS DONE!",
        "THEY'VE HUNTED DOWN THE TARGET!",
        "OVER THE LINE - WHAT A RUN CHASE!",
        "THEY'VE GOTTEN THE JOB DONE!",
        "TARGET CHASED, GAME OVER!",
        "THEY'VE SURGED PAST THE TARGET!",
        "A NERVELESS CHASE, COMPLETED!",
        "THEY'VE REELED IN THE TARGET!",
        "CHASE MASTERED - THEY'VE DONE IT!",
        "CLINICAL CHASE - TARGET DOWN!",
        "THEY'VE MADE LIGHT WORK OF THE CHASE!",
        "THE TARGET FALLS - CHASE COMPLETE!",
        "THEY'VE GOT OVER THE LINE!",
    ]
    commentary_chase_failed = [
        "THEY'VE FAILED TO CHASE IT DOWN!",
        "THE CHASE FALLS AGONISINGLY SHORT!",
        "DEFENDED TO PERFECTION!",
        "THEY'VE FAILED TO GET THERE!",
        "A TARGET SUCCESSFULLY DEFENDED!",
        "THE CHASE COMES UP SHORT!",
        "THEY COULDN'T GET OVER THE LINE!",
        "HELD ON - THE DEFENSE HOLDS!",
        "THE RUN CHASE UNRAVELS!",
        "THEY'VE FALLEN SHORT OF THE TARGET!",
        "A TOTAL SUCCESSFULLY DEFENDED!",
        "THE CHASE IS DERAILED!",
        "THEY COULDN'T FINISH THE JOB!",
        "DEFENDED - THE TARGET WAS JUST TOO MUCH!",
        "THE CHASING SIDE COMES UP EMPTY!",
        "A GALLANT CHASE FALLS SHORT!",
        "THE TARGET PROVES JUST OUT OF REACH!",
        "THE DEFENSE STANDS TALL!",
        "SO CLOSE, YET SO FAR - THE CHASE FAILS!",
        "THEY JUST COULDN'T FIND THE RUNS NEEDED!",
    ]

    commentary_match_won = [
        "that's it, that's the end of the match!",
        "the winning runs are struck, it's all over!",
        "job done, they have closed out the match!",
        "the contest is settled, what a game!",
        "and that seals it, the match is won!",
        "that's it, they have won the match!",
        "that's the end of the match!",
    ]

    commentary_match_won_chasing = [
        "they've chased down the target!",
    ]

    commentary_won_last_ball = [
        "a last ball victory for %s!",
        "%s win an absolute thriller!",
        "they've kept their nerves! what a finish %s!",
        "victory off the last ball for %s!",
        "nail biting finish, and in the end its %s who are the winners!",
        "last ball thrilling victory for %s!",
    ]

    commentary_all_out = [
        "that's it! they have been bowled out!",
        "the innings folds, they are all out!",
        "the tail has been mopped up, all out!",
        "no more batsmen to come, that's all out!",
        "the bowlers have done the job, all out!",
        "terrific bowling performance, they have been bowled out!",
        "its all over for them!.. they have been bowled out!",
        "that's all over!! all out!",
    ]

    # end of a Test day's play (there's still a next day to come - see the
    # "unless match ends" guard in _AdvanceSessionIfNeeded)
    commentary_stumps = [
        "that's stumps for the day!",
        "bails off - play is done for the day!",
        "the players will be relieved to see the back of that day!",
        "an eventful day's play draws to a close!",
        "time to reflect on a fascinating day's cricket!",
        "the umpires call time on a captivating day!",
        "stumps drawn on another absorbing day!",
        "that wraps up play for today!",
        "a day to remember, and more still to come!",
        "the teams will regroup overnight!",
        "plenty to talk about after that day's play!",
        "the sun sets on another twist-filled day!",
        "both sides will have plenty to think about tonight!",
        "a hard-fought day comes to an end!",
        "the scoreboard tells only half the story from today!",
        "stumps - and what a day it's been!",
        "the players trudge off as the light fades!",
        "day's play complete - back again tomorrow!",
        "a day of fluctuating fortunes draws to a close!",
        "that's a wrap for today - see you tomorrow!",
    ]

    # ---------------------------------------------------------------
    # End-of-innings analysis (see Match._BuildInningsAnalysis).
    # Every list below is picked from at random. Headline lists take the
    # run rate (one %s); phase lists take the args noted above each.
    # ---------------------------------------------------------------

    # total well above par for the format - takes the run rate
    commentary_innings_commanding = [
        "A commanding total, scoring at %s an over.",
        "A brilliant batting display at %s an over.",
        "They piled on the runs at a superb %s an over.",
        "A dominant innings - %s runs an over throughout.",
        "That is a formidable total, made at %s an over.",
        "The batters were in complete control at %s an over.",
        "A punishing innings, racing along at %s an over.",
        "They put the bowlers to the sword at %s an over.",
        "An outstanding effort with the bat - %s an over.",
        "That's a total to be proud of, at %s an over.",
        "Ruthless batting, %s runs an over from start to finish.",
        "A statement innings at %s an over.",
        "They made batting look easy at %s an over.",
        "A magnificent total, built at %s an over.",
        "The scoreboard raced along at %s an over.",
        "A commanding display - %s an over says it all.",
        "They were relentless, scoring at %s an over.",
        "A superb batting performance at %s an over.",
        "That's a mountain of runs, at %s an over.",
        "Emphatic batting, %s runs an over.",
    ]

    # a decent, par-ish total - takes the run rate
    commentary_innings_solid = [
        "A solid effort, scoring at %s an over.",
        "A competitive total at %s an over.",
        "They batted sensibly, at %s an over.",
        "A respectable innings - %s runs an over.",
        "Steady batting at %s an over.",
        "A workmanlike total, made at %s an over.",
        "They did a decent job at %s an over.",
        "Nothing flashy, but %s an over is competitive.",
        "A serviceable total at %s an over.",
        "They kept it ticking along at %s an over.",
        "A reasonable effort - %s runs an over.",
        "That's about par, at %s an over.",
        "A composed innings at %s an over.",
        "They've given themselves something to defend, at %s an over.",
        "A fair total, scoring at %s an over.",
        "Sound batting throughout at %s an over.",
        "A useful total, built at %s an over.",
        "They knuckled down and made %s an over.",
        "A dependable innings at %s an over.",
        "Job done, more or less - %s an over.",
    ]

    # below par - takes the run rate
    commentary_innings_modest = [
        "A modest innings - %s an over was below par.",
        "They never quite got going, at %s an over.",
        "A slightly underwhelming %s an over.",
        "That's under par, only %s runs an over.",
        "The runs came too slowly, at %s an over.",
        "A laboured innings at %s an over.",
        "They'll feel short of a few, at %s an over.",
        "Not enough urgency - just %s an over.",
        "A sluggish %s runs an over.",
        "They struggled for fluency at %s an over.",
        "A below-par total, scoring at %s an over.",
        "The scoring rate never lifted beyond %s an over.",
        "That's a total light on runs, at %s an over.",
        "They were kept in check at %s an over.",
        "A frustrating innings at %s an over.",
        "The bowlers had the better of that - %s an over.",
        "Too many dot balls, and only %s an over.",
        "A stodgy innings at %s an over.",
        "They'll rue the slow going, at %s an over.",
        "Hard work with the bat, %s an over.",
    ]

    # well below par - takes the run rate
    commentary_innings_poor = [
        "A real struggle with the bat, just %s an over.",
        "A dismal innings at only %s an over.",
        "They were completely bogged down, %s an over.",
        "A miserable effort - a mere %s an over.",
        "That was painful to watch, %s an over.",
        "The batting fell apart at just %s an over.",
        "A woeful total, scoring at %s an over.",
        "They never threatened, at %s an over.",
        "A dreadful batting display - %s an over.",
        "Comprehensively outplayed, just %s an over.",
        "The bowlers ran riot - only %s an over.",
        "A horror show with the bat at %s an over.",
        "Nowhere near good enough, %s an over.",
        "They were strangled throughout, %s an over.",
        "A capitulation - just %s runs an over.",
        "That's an innings to forget, at %s an over.",
        "They had no answers, scoring %s an over.",
        "An abject batting effort - %s an over.",
        "Well short of what was needed, %s an over.",
        "A chastening innings at just %s an over.",
    ]

    # start of the innings - early wickets lost (takes wicket count)
    commentary_phase_early_wickets = [
        "They lost %s early wickets and were in trouble at the top.",
        "A nightmare start - %s wickets down inside the opening overs.",
        "The top order caved in, %s gone early.",
        "%s early wickets left them reeling.",
        "They were rocked early, losing %s up front.",
        "A dreadful opening spell to face - %s wickets fell.",
        "The new ball did the damage, %s wickets early on.",
        "They were %s down before they had settled.",
        "Disaster at the top of the innings - %s wickets gone.",
        "The openers found no answers, %s wickets lost early.",
        "%s early strikes had them on the back foot.",
        "A brutal start, with %s wickets tumbling.",
        "They were in deep trouble early, %s wickets down.",
        "The top order was blown away - %s gone.",
        "%s quick wickets set them back badly.",
        "A horrid start, losing %s in a hurry.",
        "They never recovered from losing %s early.",
        "The innings began in chaos, %s wickets down.",
        "%s early dismissals put them under real pressure.",
        "A shaky beginning - %s wickets lost cheaply.",
    ]

    # start of the innings - wicket-free and flowing
    commentary_phase_good_start = [
        "A superb start - no wickets lost and the runs flowing.",
        "The openers gave them a flying start.",
        "A dream beginning, wickets intact and runs coming.",
        "They came out of the blocks beautifully.",
        "The opening pair laid a perfect platform.",
        "An assured, wicket-free start to the innings.",
        "They got away brilliantly at the top.",
        "The openers made hay early on.",
        "A commanding start with the bat.",
        "The platform was laid superbly up front.",
        "They took the attack to the bowlers early.",
        "A blistering opening to the innings.",
        "The top order was untroubled and fluent.",
        "They started exactly as they would have hoped.",
        "A textbook opening stand.",
        "The bowlers found nothing early on.",
        "They raced away without losing anyone.",
        "A superb foundation from the openers.",
        "Wickets in hand and runs on the board - ideal.",
        "The innings could not have started better.",
    ]

    # start of the innings - cagey / slow
    commentary_phase_slow_start = [
        "A slow, cagey start to the innings.",
        "They took their time settling in.",
        "A watchful opening, with runs hard to come by.",
        "The batters felt their way in cautiously.",
        "A circumspect start to proceedings.",
        "The scoring was sluggish early on.",
        "They were pinned down in the opening overs.",
        "A tentative beginning with the bat.",
        "The bowlers kept it tight up front.",
        "Runs were at a premium early on.",
        "A subdued start to the innings.",
        "They played themselves in slowly.",
        "The openers struggled for timing.",
        "A quiet, attritional opening.",
        "The early overs brought very little.",
        "They were content to survive early on.",
        "A grinding start with few scoring shots.",
        "The bowlers had the upper hand early.",
        "A cautious, low-risk opening.",
        "The innings took a while to warm up.",
    ]

    # middle overs - wickets falling (takes wicket count)
    commentary_phase_middle_wobble = [
        "The middle overs brought a wobble - %s more wickets went down.",
        "A middle-order slump cost them %s wickets.",
        "They lost their way in the middle, %s wickets falling.",
        "%s wickets in the middle overs halted the momentum.",
        "The middle order faltered, losing %s.",
        "A cluster of %s wickets derailed the middle overs.",
        "They stumbled through the middle, %s wickets down.",
        "%s more wickets fell as the innings lost its way.",
        "The bowlers struck back with %s middle-order wickets.",
        "A mid-innings collapse of %s wickets.",
        "They could not stem the flow - %s wickets in the middle.",
        "The middle overs belonged to the bowlers, %s wickets falling.",
        "%s wickets in the middle put the brakes on.",
        "A wobble through the middle cost them %s.",
        "The innings hit turbulence, %s wickets going down.",
        "They lost %s in a damaging middle passage.",
        "A middle-overs slide of %s wickets.",
        "%s wickets fell as the pressure told.",
        "The middle order simply could not hold on - %s gone.",
        "A costly middle spell, %s wickets lost.",
    ]

    # middle overs - rebuilt and kept scoring
    commentary_phase_middle_rebuild = [
        "They rebuilt well and kept the scoreboard ticking.",
        "A fine recovery through the middle overs.",
        "The middle order steadied the ship nicely.",
        "They consolidated superbly in the middle.",
        "A composed rebuild through the middle overs.",
        "The innings was repaired with real maturity.",
        "They knuckled down and rebuilt the innings.",
        "A crucial middle-overs partnership took hold.",
        "The scoring never dried up through the middle.",
        "They kept the momentum going nicely.",
        "A smart, controlled middle passage.",
        "The middle order batted with real intelligence.",
        "They turned things around through the middle overs.",
        "A well-judged rebuild in the middle.",
        "The innings was steadied and then accelerated.",
        "They rotated the strike expertly through the middle.",
        "A calm, assured middle-overs display.",
        "The middle order did its job admirably.",
        "They wrestled back control in the middle.",
        "A productive middle passage with the bat.",
    ]

    # middle overs - quiet, rate dropped
    commentary_phase_middle_quiet = [
        "The middle overs went quiet and the rate dropped.",
        "The innings stagnated through the middle.",
        "They lost momentum badly in the middle overs.",
        "A becalmed middle passage.",
        "The scoring dried up through the middle overs.",
        "The bowlers squeezed hard in the middle.",
        "They could not find the boundary in the middle overs.",
        "A stodgy middle passage with the bat.",
        "The run rate slid through the middle overs.",
        "They were pegged back in the middle.",
        "The middle overs brought very little.",
        "A quiet, uneventful middle passage.",
        "The innings drifted through the middle overs.",
        "They struggled to rotate the strike in the middle.",
        "The pressure built through a scoreless middle spell.",
        "The middle overs were a grind.",
        "They went into their shell through the middle.",
        "A frustrating middle passage for the batters.",
        "The bowlers strangled the middle overs.",
        "Momentum was lost badly through the middle.",
    ]

    # death overs - strong finish (takes runs, then overs)
    commentary_phase_death_surge = [
        "But they picked up superbly at the death - %s runs in the last %s overs!",
        "A blistering finish, %s runs from the final %s overs!",
        "They exploded at the death - %s off the last %s overs!",
        "What a finish! %s runs in the closing %s overs.",
        "The death overs were plundered - %s from %s overs.",
        "They saved the best for last, %s runs in %s overs.",
        "A stunning late surge of %s runs in %s overs.",
        "The finish was brutal - %s runs off the last %s overs.",
        "They cut loose at the end, %s from %s overs.",
        "A devastating final flourish, %s runs in %s overs.",
        "The closing overs brought a deluge - %s from %s.",
        "They finished like a train, %s runs in %s overs.",
        "An explosive end to the innings - %s off %s overs.",
        "The death overs were a blur, %s runs in %s.",
        "They tore into the bowling late, %s from %s overs.",
        "A superb acceleration - %s runs in the last %s overs.",
        "The finish was emphatic, %s runs off %s overs.",
        "They piled on %s in the final %s overs.",
        "A ferocious closing burst, %s runs in %s overs.",
        "A remarkable %s runs came in the last %s overs.",
    ]

    # death overs - collapse (takes wicket count)
    commentary_phase_death_collapse = [
        "The innings fell away at the end, losing %s wickets in the closing overs.",
        "A late collapse cost them %s wickets.",
        "They lost %s wickets in a chaotic finish.",
        "The tail was blown away - %s wickets at the death.",
        "%s wickets fell as the innings unravelled late.",
        "A messy finish, losing %s wickets.",
        "The death overs brought %s wickets and little else.",
        "They threw it away late, %s wickets going down.",
        "The innings ended in a heap - %s wickets lost.",
        "A dramatic late slide of %s wickets.",
        "%s wickets tumbled in the closing overs.",
        "The finish fell flat, %s wickets falling.",
        "They lost their way completely, %s wickets at the end.",
        "A calamitous close - %s wickets gone.",
        "The bowlers cleaned up, taking %s late wickets.",
        "%s wickets in the death overs undid the good work.",
        "The innings imploded late, %s wickets down.",
        "A wretched finish, losing %s wickets.",
        "They surrendered %s wickets in the closing overs.",
        "The last few overs cost them %s wickets.",
    ]

    # death overs - couldn't accelerate
    commentary_phase_death_quiet = [
        "They couldn't get going in the closing overs.",
        "The acceleration never came at the death.",
        "A flat finish to the innings.",
        "They failed to cash in at the end.",
        "The death overs brought far too few runs.",
        "The bowlers nailed their yorkers at the death.",
        "They ran out of steam in the closing overs.",
        "A disappointing finish with the bat.",
        "The final overs were a damp squib.",
        "They could not find the boundary late on.",
        "The innings petered out at the end.",
        "No late fireworks from this batting side.",
        "The closing overs were surprisingly quiet.",
        "They were kept in check right to the end.",
        "A tame finish to the innings.",
        "The death overs were expertly bowled.",
        "They never managed to shift through the gears.",
        "The scoring stalled when it mattered most.",
        "A muted end to the innings.",
        "They left runs out there at the death.",
    ]

    # ---- how the match was won/lost (final innings of a limited-overs game)
    # nail-biting finish
    commentary_margin_thriller = [
        "What a thriller - that went right to the wire!",
        "A nerve-shredding finish!",
        "That could not have been any closer!",
        "An absolute classic, decided at the death!",
        "Heart-stopping stuff right to the final ball!",
        "A cliffhanger of the highest order!",
        "That was cricket at its most gripping!",
        "A breathless finish nobody will forget!",
        "Down to the wire - what a contest!",
        "The tension was unbearable at the end!",
        "A thriller that had everything!",
        "Decided by the finest of margins!",
        "What a way to finish a game of cricket!",
        "A last-gasp finish for the ages!",
        "That one will be talked about for years!",
        "Drama to the very last delivery!",
        "An epic finish - both sides gave everything!",
        "A pulsating end to a terrific contest!",
        "The margin was wafer-thin!",
        "Sensational drama in the closing moments!",
    ]

    # routine, comfortable result. NOTE: these lines sit on the chasing side's
    # analysis card whether the chase succeeded or failed, so they describe the
    # contest rather than a "they" - a winner-voiced line would read wrong on a
    # losing card (and vice versa).
    commentary_margin_comfortable = [
        "A comfortable result in the end.",
        "That was settled with plenty to spare.",
        "A professional, no-fuss finish.",
        "Never really in doubt once it settled.",
        "A composed and controlled contest.",
        "The job was done without alarms.",
        "A straightforward outcome in the end.",
        "Efficiently settled, with something in hand.",
        "A workmanlike affair.",
        "Comfortably decided in the end.",
        "Comfortable, if not spectacular.",
        "A tidy result with room to spare.",
        "The outcome never looked in serious doubt.",
        "A measured, assured contest.",
        "Settled without any real drama.",
        "One side controlled this throughout.",
        "A convincing enough result.",
        "Safely negotiated in the end.",
        "A calm and collected finish.",
        "The better side on the day came through.",
    ]

    # one-sided thrashing - kept perspective-neutral for the same reason
    commentary_margin_crushing = [
        "A crushing, one-sided result.",
        "An absolute demolition job.",
        "That was a thrashing, plain and simple.",
        "Utterly one-sided from start to finish.",
        "A humiliating margin.",
        "One side was blown away completely.",
        "A comprehensive, emphatic result.",
        "No contest whatsoever.",
        "A brutal, one-sided beating.",
        "That was as one-sided as it gets.",
        "An emphatic statement of a result.",
        "One side was outclassed in every department.",
        "A hammering from first ball to last.",
        "Total domination - not a contest.",
        "A chastening result to swallow.",
        "One side never laid a glove on the other.",
        "A ruthless, clinical destruction.",
        "The gulf between the sides was enormous.",
        "A landslide result.",
        "One side was overwhelmed in every facet.",
    ]

    commentary_all_out_good_score = [
        "theyve managed to build a good total though!",
    ]

    commentary_all_out_bad_score = [
        "theyve failed to build a competitive total!",
    ]

    # LAST OVER/MATCH/INNS
    commentary_last_ball_match = [
        "this is it.. the last ball of the match!",
        "we are down to the last ball of the match",
        "last ball of this match coming up!",
    ]
    commentary_last_ball_innings = ["last ball of this innings !"]
    commentary_last_over_match = [
        "This is the last over of the match!",
        "the final over of the match!!",
        "match comes down to last over!!",
        "everything comes down to last over!",
        "what an exciting finish!!",
        "This is going to be a nerve-wracking last over!!",
    ]
    commentary_last_over_innings = [
        "last over of this innings coming up",
        "we are down to the last over!",
        "last over of the innings!",
    ]

    # chasing and lost
    commentary_lost_chasing = [
        "end of the match.. end of the chase tough luck %s, well played %s!!",
        "afraid to say that's the end of the chase for %s! magnificent performance %s",
        "%s! they have failed in this chase!.. good bowling %s",
        "%s fought well, but the %s bowlers dominated today!",
        "the pressure was too much for %s!.. well played %s",
        "the %s bowling team was too good for %s!",
        "%s was totally outsmarted by %s!",
        "Well %s, they have succumbed to pressure.. well played %s!",
    ]

    # over
    commentary_expensive_over = [
        "what an expensive over by %s!",
        "oh dear! %s.. this is a costly over.. they will have to pay for this!",
        "an expensive over by %s! this could turn the course of the match!",
        "costly over from %s.. this could change the match!",
        "expensive over.. %s is shattered!",
        "poor bowling by %s.. expensive over!",
        "expensive over! %s is totally battered!",
        "that's an expensive over from %s!",
    ]
    commentary_economical_over = [
        "what an over from %s.. very economical!",
        "magnificent over from %s..!",
        "superb over %s!.. very disciplined!",
        "very economical bowling from %s!",
        "an economical over by %s!",
    ]
    commentary_bowler_finished_spell = [
        "thats the end of %s's spell",
        "end of the spell for %s",
        "%s has finished his spell!",
    ]
    commentary_maiden_over = [
        "Excellent over from %s... that's a maiden over!",
        "brilliant bowling from %s... no runs from this over!",
        "superb bowling from %s... that's a maiden over!",
    ]

    # bowler's last over
    commentary_bowler_last_over = [
        "this is the last of his allotted overs!",
        "bowling his last over!",
        "he is going to bowl the last of his allotted overs",
        "bowler with his last over!",
        "he is gonna bowl his last over!",
    ]
    # check if bowler had a good spell
    commentary_bowler_good_spell = [
        "he had a terrific spell so far!",
        "he was in good form today!",
        "he bowled really well today!",
        "he had a nice spell so far!",
        "he had a good day with the ball!",
    ]
    commentary_bowler_bad_spell = [
        "he didn't have a good day so far!",
        "he was very expensive today!",
        "he was not in form today!.. too expensive",
        "he was not in good touch today!",
        "he didn't have a good day with the ball",
    ]

    # good/bad bowler to bat
    commentary_good_bowler_to_bat = [
        "he had really good day with the ball.. can he bat too?",
        "he had a terrific time with the ball earlier, lets see if he can bat too",
    ]

    commentary_bad_bowler_to_bat = [
        "he didn't have a good day with the ball.. can he bat now?",
        "he had a horrible time with the ball earlier, lets see if he can bat",
    ]

    # check if bowler is spinner
    commentary_spinner_into_attack = [
        "the spinner, to start the over!",
        "spinner into the attack!.. lets see if he gets the ball to turn!",
        "we have a spin bowler into the attack",
        "the spinner to start his over",
        "we have a spinner to bowl this over",
        "the spin bowler to start the over",
    ]
    commentary_pacer_into_attack = [
        "a pacer into the attack now!",
        "a pacer into the attack!.. lets see if he can get some swing",
        "seamer to start a new over",
        "a fast bowler to start a new over!",
        "a quick bowler into the attack here",
        "the seamer to begin a new over.. ",
        "we have a fast bowler into the attack",
    ]
    commentary_medium_into_attack = [
        "medium pacer into the attack",
        "a medium pacer, to start a new over",
        "the medium pacer to start the over.. lets see if he can induce a wicket",
        "we have a medium bowler into the attack",
    ]
    commentary_captain_to_bowl = [
        "the skipper to bowl a new over",
        "captain to start a new over here!",
        "the skipper, to begin a new over",
        "the captain to bowl now!",
        "lets see if the captain can make an impact!",
        "captain is going to try an over now!",
        "captain coming on to bowl this over!",
    ]

    # rain
    commentary_rain_cloudy = [
        "well it looks cloudy and looks like it might rain..",
        "oops.. there are some rain clouds above us.. ",
        "weather doesnt look good.. can see the rain clouds developing....",
    ]
    commentary_rain_drizzling = [
        "this is not looking good, a slight drizzle.. we can see raincoats among the crowd",
        "it started drizzling a little now.. tougher for the players",
        "slight drizzle, and fielding is getting tougher!.. we could see the spectators getting their coats",
    ]
    commentary_rain_heavy = [
        "this is bad.. it started pouring!.. Umpires looking concerned",
        "oops it has started pouring!.. Umpires are having a chat with the players",
        "Its raining.. !!",
    ]
    commentary_rain_interrupt = [
        "heavy rain I am afraid to say the match might have to be called off!",
        "this is an unfortunate end ! Rain has forced to call off the match",
        "heavy rains.. and the umpires and the match referee have decided to call off the match",
    ]

    # umpire gives a run-out/stumping out on the spot (no referral)
    commentary_given_out = [
        "that's out by a mile! the finger goes up straightaway!",
        "no doubt about that one, given out on the spot!",
        "the umpire didn't even need a replay for that, that's out!",
        "comfortably out! the umpire's finger is up in a flash!",
        "easy decision that, he's well short and given out!",
    ]

    # stumping sent upstairs to the third umpire
    commentary_referred_stumped = [
        "oh, big appeal for the stumping! the keeper whips off the bails, the umpire is unsure and sends it upstairs",
        "the keeper thinks he's got him stumped! the umpire is doubtful and calls for the third umpire",
        "close one this! was the foot behind the line? over to the third umpire for the stumping",
        "the bails are off and the keeper is appealing hard.. the umpire wants a closer look upstairs",
    ]

    # run-out sent upstairs to the third umpire
    commentary_referred_runout = [
        "direct hit! and the umpire goes upstairs to check the run out",
        "oh that's close! the run-out decision is referred to the third umpire",
        "the throw hits the stumps, and the umpires check with the third umpire",
        "there could be a run out here! the on-field umpire is unsure and sends it up",
    ]

    # third umpire's verdict - out
    commentary_third_umpire_out = [
        "the replays confirm it, he's out!",
        "the red light is on! the batsman has to walk back!",
        "third umpire says out! good decision in the end",
        "the replays are conclusive, that's out!",
    ]

    # third umpire's verdict - not out (a reprieve)
    commentary_third_umpire_not_out = [
        "the green light! he's made his ground, not out!",
        "replays show he just got back in time, the batsman survives!",
        "not out says the third umpire! a huge reprieve for the batsman",
        "he's in! the bat was grounded behind the line, not out!",
    ]
