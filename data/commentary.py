# all the commentary phrases are defined here

# commentary phrases
class commentary:
    intro_game = '*' * 50 + '\n' + '*' * 14 + 'Book Cricket Simulator' + '*' * 14 + '\n' + '*' * 50

    intro_dialogues = ['Welcome everybody, here we are at ',
                       'Hello everyone, here we are at ',
                       'Hello and welcome everyone to ',
                       'Electrifying atmosphere here at ',
                       'Warm welcome to everybody to ']

    # Run rates
    commentary_less_req_rate = ['looks easily gettable for %s',
                                'not a big task for %s at all!',
                                'target looks easy for %s but they are going to face some quality bowling attack!',
                                'looks like an easy target for %s!']
    commentary_high_req_rate = ['required rate is really high for %s!',
                                'this is gonna be a tough chase for %s!',
                                'a big target for %s and they will be facing a tough bowling attack too!',
                                'a himalayan task ahead for %s! need to bat really well!',
                                'that\'s a big task ahead for %s, and will be facing some quality pace attack too!']
    # comment situation based on Reqd RR
    commentary_situation_reqd_rate_low = ['%s well on course here!',
                                          'the required rate looks easily gettable for %s!',
                                          'this chase looks easy for %s!',
                                          'this chase is on.. good display %s!',
                                          '%s are cruising here!',
                                          '%s look relaxed as the asking rate is looking easy!',
                                          '%s really know their target.. well on course!',
                                          '%s are punishing the bowlers here! required rate is less than required',
                                          '%s can get home without any hurdles with this scoring rate!',
                                          '%s are chasing well here!', ]
    commentary_situation_reqd_rate_high = ['required rate is high!.. well %s, they need to gear up!',
                                           '%s need to push themselves hard to stay on course!',
                                           '%s need some big hits to boost up the run rate!',
                                           'singles and doubles wont take %s home!',
                                           '%s need to boost up the run rate!',
                                           'required rate is going higher for %s.. pressure building!',
                                           'bowlers are not giving %s room to cope up with the required rate!',
                                           '%s will have to struggle to get home with this scoring rate!',
                                           'chase looks pretty sluggish for %s!',
                                           '%s need some hard hitters to stay alive in this chase!',
                                           '%s really need to boost up the run rate here!']

    # comments for diff shots
    commentary_six = ['that\'s in the stands! ',
                      'he goes bang ! that\'s a big one!',
                      'smashed it out of the park!',
                      'where do you set fielders for this man!',
                      'oh what a shot! That has been smashed out of the ground!',
                      'stand and deliver!',
                      'picked up the slow ball well and hit really hard!',
                      'he has blazed that one! go fetch that!',
                      'that\'s gone miles in the air!',
                      'he is dealing in sixes here!',
                      'loose delivery and punished hard!',
                      'what a biggie! it has gone into the trees!',
                      'the batsman has decided that tonight\'s gonna be his night!',
                      'fielder in the deep will just watch it sail over the fence!',
                      'will this be taken in the deep.. no its 6!',
                      'that\'s a powerful shot.. will be a one bounce.. not its gone all the way for 6!',
                      'that\'s one of the biggest sixes ever!',
                      'that is gone, and forgotten! what a hit!',
                      'that\'s a flat six! beautifully hit!',
                      'that\'s big and the crowd will catch it! ',
                      'boy what a hit!',
                      'that\'s huge, its out of here!', ]
    commentary_four = ['what a shot!.. that will find the fence!',
                       'short and wide and punished hard!',
                       'that\'s the shot of the day for me!',
                       'oh will this be taken in the deep, oh he has dropped it.. and its 4!',
                       'the crowd is loving this!',
                       'fielder in pursuit... wont get there..',
                       'beautiful drive and the fielder has given up the chase!',
                       'into the gap for four!',
                       'pierced the gap for four!'
                       'smashed through the gap!',
                       'poor delivery and deserved to be hit!',
                       'long chase for the fielder... and the ball wins the race!',
                       'how do you set fields for this batsman!',
                       'bad ball and punished!..',
                       'bad delivery.. it had 4 written all over it!',
                       'well connected!.. that will go to the boundary',
                       'Great shot! Absolutely magnificent!. And the batsman has not moved an inch!',
                       'that will find the fence!',
                       'magnificent shot!.. ',
                       'oh unbelievable timing!',
                       'Beautiful shot.. oh sloppy fielding in the deep!',
                       'When He Hits It, It Stays Hit !',
                       'he is getting warmed up here!',
                       'boy what a shot!',
                       'right out of the middle of the bat!',
                       'what a smash!',
                       'He\'s a better player than his statistics suggest',
                       'that\'s a great lesson for any youngster watching !',
                       'Terrific batting this.. what would be the reply from the bowler?',
                       'Another one of those, and there will be a chat between the bowler and his captain!',
                       'he goes bang!']
    commentary_ground_shot = ['not timed well but will get some runs',
                              'found the gap well',
                              'good ball ! but well played into the gap',
                              'into the gap',
                              'good delivery and somehow the batsman manages to get some runs out of it',
                              'very quick running',
                              'he has to hurry!',
                              'well played into the gap',
                              'edged and dropped!!! oh what a miss',
                              'in the air, dropped! batsman will get some runs too!',
                              'poor fielding, that\'s gifting singles and doubles to the batsman!',
                              'sloppy fielding, useful singles and doubles for the batsman',
                              'Oooh! direct hit and he would\'ve gone!',
                              'that\'s quick running!',
                              'not timed well but lazy fielding, bowler is not happy!',
                              'singles and doubles will surely irritate the fielding captain']

    # if taken a wicket as well as scored runs in the first innings
    commentary_all_round_bowler = ['it was %s with the bat, now with the ball!',
                                   'oh %s is a brilliant all rounder!',
                                   'a brilliant bowler %s is, who had a great innings earlier today as well!',
                                   '%s had a good day with the bat, now he strikes with the ball too!', ]
    commentary_all_round_batsman = ['he had a good day with the bat and with the ball !',
                                    'he is a master all rounder!',
                                    'he is all over the ground today, earlier with the ball, now with the bat!']

    # first boundary of the innings
    commentary_first_four_team = ['first boundary of this innings!',
                                  'there is the first one to cross the fence!',
                                  'first 4 of the innings',
                                  'first boundary, and it came in style!',
                                  'that\'s the first boundary, no wonder it came from him!',
                                  ]

    commentary_first_six_team = ['first sixer of this innings!',
                                 'there is the first one to sail over the fence!',
                                 'first 6 of the innings!',
                                 'first six!, and it came in style!',
                                 'there is the first biggie.. it came in style!',
                                 'that\'s the first maximum, no wonder it came from his bat!',
                                 ]

    # four first  ball
    commentary_firstball_four = ['what a way to start the innings!',
                                 'glorious start to the innings!',
                                 'he starts with a bang! no pressure at all!',
                                 'explosive start! bowler is stunned!',
                                 'bowler feels the pressure now! first ball has been smoked!',
                                 'well what a start! the first ball has been hit for a boundary',
                                 'that\'s how you start an innings! pressure straightway on the bowler now!']
    commentary_firstball_six = ['six of the first ball!',
                                'would you believe it! six of the first ball!',
                                'explosive start! bowler is stunned!',
                                'bowler looks shell shocked! first ball has been smashed!',
                                'first ball and its dispatched! Beware bowlers!',
                                'bang! he has smashed the first ball out of here!',
                                'that\'s how you start an innings! pressure straightway on the bowler now!'
                                'that\'s hit off the first ball!.. ']

    # captain next:
    commentary_captain_to_bat_next = ['the captain walking out to the middle!',
                                      'the skipper to bat next!',
                                      'and now we have the captain at the crease',
                                      'the captain now has a job to do!',
                                      'crowd cheering as the captain walks out to bat',
                                      'the skipper, to walk into the ground now',
                                      'huge applause as the captain is going into the middle']
    # captain out
    commentary_captain_out = ['got rid of the skipper!',
                              'the captain goes!',
                              'got the skipper!',
                              'that\'s the end of the captain!',
                              'yes! the skippers is gone!']
    # captain leading
    commentary_captain_leading = ['captain leading from the front',
                                  'captain courageous!',
                                  'that\'s how you lead your team! bravo skipper!',
                                  'he is a perfect example of a brave leader!',
                                  'the skipper leading from the front here']

    # comments for wkts
    commentary_one_down = ['they draw first blood!',
                           'the opening stand is broken!',
                           'first one down!',
                           'the bowling team draw first blood!',
                           'one down!']
    # half the side is down
    commentary_five_down = ['half the side is back in the pavilion!',
                            'job half done!.. 5 wickets down!',
                            '5 down and i am afraid the flood gates have opened!',
                            'half down and the tail is exposed!']
    # commentary last man
    commentary_lastman = ['last man coming out to bat!',
                          '9 down, last wicket coming out to bat',
                          'now they will be trying to mop up the tail!',
                          'tail ender coming out into the middle!']

    # diff types of dismissals
    commentary_hit_wkt = ['gone! he has hit the stumps!']
    commentary_bowled = ['full and straight what a ball',
                         'what a yorker! he is on fire!',
                         'bowled him!',
                         'poor footwork!.. bowled him',
                         'got him! and the bowler lets out a roar!',
                         'perfect length, that has hit the top of off-stump!',
                         'Middle stump out of here',
                         'inside edge and bowled!',
                         'dragged on to the stumps',
                         'done him and shattered the stumps!',
                         'he has made an awful mess of the stumps!',
                         'knocked him over with a ripper!',
                         'oh hes played it on!.. Batsman would be so disappointed',
                         'oh what a delivery!.. Perfect line and length!',
                         'Bowled him!! comprehensively bowled!',
                         'knocked his stumps over!',
                         'off stump out of the ground!',
                         'bowled him! You beauty!',
                         'done him! peach of a delivery!',
                         'Knocked his middle stump out!... And there is a stare at the batsman!',
                         'Bowled him! And he is showing the batsman the way to the dressing room!',
                         'done him with a toe crushing yorker!',
                         'oh bowledimm!, an unplayable delivery!', ]
    commentary_in_a_row = ['that\'s 3 in a row!',
                           'three in a row now!, bowler is clueless here',
                           'three in a row!']
    commentary_reverse = ['Oh that\'s reversed!',
                          'the ball has reversed!',
                          'he gets it to reverse!',
                          'oh yes he gets it to reverse!',
                          'reverse swinging delivery !',
                          'magnificent reverse swinging delivery!',
                          'brilliant reverse swinger this!']
    commentary_swing = ['Terrific in-swinger!',
                        'superb in-swinger!',
                        'out-swinging delivery!',
                        'wild swinging delivery!',
                        'what a peach! that swung inside! ',
                        'beautiful seam position.. swinging in!',
                        'he has this ability to swing the ball both ways!',
                        'that\'s quick and it swung a long way!!',
                        'oh that swung a long way!',
                        'brilliant out swinger!',
                        'unbelievable swing!']
    commentary_turn = ['that ball turned a long way!',
                       'oh that spun a long way!',
                       'terrific spin bowling this!',
                       'terrific spin! the batsman cant believe it!',
                       'oh it turned a long way! surprised even the bowler!',
                       'what a turn! the batsman is stunned!',
                       'that spun like never before!',
                       'deceived by the googly!',
                       'that was the one which didn\'t turn!,, batsman is fooled!',
                       'that ball turned so sharp!!',
                       'that was the wrong-un!',
                       'a ripsnorter!',
                       'beautiful top spinner!',
                       'what a delivery!.. terrific spin!',
                       'oh what a turn! and the batsman is fooled completely!',
                       'what a turn! it has stunned the batsman!', ]
    commentary_runout = ['what a terrible mix up between %s and %s!',
                         'this is bizarre!.. terrible miscommunication between %s and %s',
                         'dead accurate throw from the fielder!.. poor call from %s and %s pays the price!',
                         'this is poor running from %s! that was a wrong call from %s!',
                         'magnificent fielding.. brilliant throw!.. and both %s and %s messed it up',
                         '%s, no! %s is calling for the second.. direct hit and gone!',
                         'that was a horrible call by %s and %s!',
                         'there was absolutely no run there! poor running between the wickets between %s and %s!',
                         'that is horrific! where was the run there %s?.. it was a call from %s',
                         'lazy running between the wickets at this stage of the match by %s and %s!',
                         'horrible running between the wickets by %s and %s!',
                         'magnificent throw and %s knows it! good fielding!.. poor call from %s',
                         'brilliant throw and good collection! umpire need not review this!.. terrible from %s and %s',
                         'there was no run there! this is bizarre!. was it %s s call? i think it was %s',
                         'rocket arm from the fielder! what a throw!.. and ends a partnership between %s and %s',
                         'direct hit and gone!.. both %s and %s will be kicking themselves',
                         'that\'s gone.. run out!! never run off a mis-field, %s and %s!',
                         'what was the batsmen thinking!?.. poor start by %s it was initiated by %s i guess!']
    commentary_stumped = ['swift work by the keeper %s!',
                          'that\'s out! stumped.. bravo %s!',
                          '%s takes the bails off in a flash!',
                          'that spun hard, batsman misses and quick work behind the stumps by %s!',
                          'tries for a wild shot and missed it.. quick stumping by %s!',
                          'batsman misses it and swift work %s!',
                          'stumped, %s looks confident, no need to refer it!',
                          '%s ''s fast hands behind the stumps!',
                          'very quick piece of stumping by %s!',
                          'terrific stumping by %s!!',
                          'quick stumping! %s appeals, umpire says out!',
                          'the keeper is lightning quick %s!']
    commentary_caught = ['in the air.. and taken by %s!',
                         'that\'s straight up in the air.. %s calls for it, taken!',
                         'bad shot.. leading edge and gone.. good take by %s!',
                         'outside edge and a magnificent catch! you beauty %s',
                         'that\'s not timed well and oh what a catch by %s!',
                         'in the air that\'s taken by %s! what a blinder!',
                         'brilliant catch! %s is a supreme athlete!',
                         'oh man! what a catch by %s! one of the best catches ever!',
                         'that\'s in the air, %s is underneath it, has he dropped it, no he hasn\'t! what a catch!',
                         'that\'s hit straight down the %s''s throat!',
                         'hit in the air and what a catch!...unbelievable catch by %s!',
                         'straight up in the air.. %s says mine.. takes it in the end!',
                         'hit very hard but straight to %s.. batsman cant believe what he has done!',
                         'magnificent catch by %s..! ..diving in the air!',
                         'in the air and taken by %s! batsman looks shell shocked! what a catch!',
                         'hit in the air...brilliant dive by %s! what a take! batsman looks stunned!',
                         'up in the air and oh what a catch! one handed by %s!',
                         'hit hard to the fielder and %s takes it!',
                         'hit straight down %s\'s throat!',
                         'in the air and oh! has he taken that? He has! %s! what a catch!']
    commentary_keeper_catch = ['edged.. and taken by the keeper %s!',
                               'got him, yes.. caught behind!.. good take by %s',
                               'there is an edge and what a catch by the keeper %s!',
                               'thin edge, big appeal by %s! given!',
                               'is there an edge? %s looks confident! Yes it is!',
                               'edged and brilliant dive by %s!',
                               'big deflection and yes! safely taken by %s',
                               'ooh there is an edge? %s appeals, bowler appeals...given!',
                               'outside edge and brilliantly taken by the %s!',
                               'oh is there a nick!? %s thinks so, Batsman is walking...!',
                               'straight up in the air, %s says mine and takes it!', ]
    commentary_return_catch = ['beautiful return catch by %s!',
                               'oh what a return catch by %s!',
                               'oh he has dropped.. no he hasn\'t! what a catch by %s!',
                               'that\'s out, caught n bowled by %s!',
                               'caught and bowled by %s! what a reflex!',
                               'what kind of reflexes by %s! That\'s taken!',
                               'full toss, and hit it straight back at the bowler! what a take %s',
                               'hit it hard but taken by the bowler himself!.. you beauty %s']

    # dramatic over
    commentary_dramatic_over = ['it has been a dramatic over so far!',
                                'really exciting over this for the crowd',
                                'the crowd loved this over so far! an entertainer',
                                'a dramatic over so far!',
                                ]

    # modify this as per DRS
    commentary_lbw_umpire = ['big appeal.. and %s\'s finger goes up!',
                             'that looks in line and %s says out!',
                             'looks plumb, and the %s\'s finger raises!',
                             'hit on the pads! and given out by %s!',
                             'looks dead straight to me... and %s says out!',
                             'that\'s a big appeal.. and finally given lbw by %s!!',
                             'the bowler pleads with %s, and finally given!',
                             'big appeal.. and the umpire %s says out! oh that looks like a harsh decision!', ]
    commentary_lbw_drs_taken = ['%s looks confused.. long chat with his partner %s.. and finally takes it upstairs!',
                                '%s is desperate here, long discussion with %s.. and finally decides to go for the DRS',
                                'Oh they had a quick chat, %s and %s, and they are going with the DRS.. looks like a review wasted?',
                                '%s is quickly having a chat with %s.. and decides to opt for the DRS',
                                'This is a tough call.. Will they waste a DRS chance here? %s looks confident, '
                                'but %s doesn\'t!',
                                'well, %s hasn\'t even discussed with %s, has gone upstairs instantly!',
                                'well %s has gone for the review instantly.. didn\'t even look at %s!']
    commentary_lbw_drs_not_taken = ['he is having a long chat with the non striker.. and finally he is walking off..',
                                    'it looked close to me, he discusses with the non striker, will not be wasting a '
                                    'DRS chance here',
                                    'Will he go upstairs,don\'t think so.. a nod at his partner, and he is walking off the field',
                                    'are they going for the DRS here? I don\'t think so they are interested..']
    commentary_lbw_decision_stays = [
        'Well it shows that the ball will be hitting the top of off!. Decision stays.. good on field call %s!',
        'Pitching in line, impact in line.. hitting middle.. %s gets it dead right!!',
        'missing leg? No! that\'s out.. %s gets it right again!',
        'Its pitching in-line! Hitting middle and leg.. %s''s decision stays! He has to go!']
    commentary_lbw_overturned = ['It shows the ball missing the stumps by an inch! not out!',
                                 'Impact in line, but wickets missing!',
                                 'pitching in line, impact in line, wickets.. missing! good review!',
                                 'Oh that\'s missing the top of off by inches!.. decision will be overturned!']
    commentary_lbw_edged_outside = ['DRS says there is bat involved! Overturned!.. well that saves them a review',
                                    'impact outside leg!.. this will be overturned',
                                    'impact outside off!...',
                                    'pitching outside off.. impact outside off!',
                                    'DRS says that\'s pitching outside leg! Not out!',
                                    'there is a slight nick!.. ',
                                    'Oh there is an inside edge...? This will be given not out!', ]
    commentary_lbw = ['trapped %s in front! ',
                      'given out, %s is not happy at all',
                      '%s doesnt look happy! he is shaking his head!',
                      '%s shakes his head',
                      'he knew it.. %s walks away..',
                      '%s looks unhappy, he thinks it was outside the line', ]
    commentary_lbw_nomore_drs = ['they do not have any more DRS reviews left!',
                                 'they have used all their review chances!',
                                 'No more reviews left!']

    commentary_dropped = ['that\'s hit straight up in the air, %s says mine.. oh and put down!',
                          'edged and dropped at first slip by %s! disappointment for the bowler.. oh dear!.. batsman is lucky !',
                          'in the air and oh.. ! put down by %s.. sigh of relief for the batsman!',
                          'good delivery, thats in the air but drops safe.. just bounces in front of %s',
                          'well bowled. he hits in the air and chance goes down! goodness me! catches win matches.. costly miss from %s',
                          'well bowled, that\'s in the air and this should be out. oh dropped by %s! goodness me, how lucky are you!!',
                          'very good ball. he has hit it straight up in the air, oh %s has dropped it!',
                          'in the air ..taken..? i think the fielder %s says the ball has touched the ground',
                          ]

    commentary_dropped_keeper = ['that\'s hit straight up in the air, keeper %s says mine.. oh and put down!',
                                 'that\'s in the air but put down by the keeper! oh what a miss from %s!!',
                                 'edged and taken.. no he has dropped it! oh %s... this could prove costly',
                                 'there is an edge, bowler appeals.. but looks like %s knows he has dropped it',
                                 ]

    # dot ball
    commentary_dot_ball_pacer = ['wild swing from %s and a miss from %s.. no run!',
                                 'its a short one from %s and hit %s on the shoulder!',
                                 'oh that is a nasty bouncer from %s! hit %s on the head!',
                                 'ooh what a ball %s!,.. it bounced and hit the batsman %s!',
                                 'oh terrific from %s .. that has hit the batsman on the helmet.. hope %s is fine!',
                                 'oh that\'s a quick delivery from %s.. %s looks unsettled!',
                                 'fast and swinging from %s, %s mistimes it.. no run!',
                                 'that looks close, but not out says the umpire! %s is unlucky and %s, you\'re a lucky man!',
                                 'beautiful slow ball from %s.. fooled %s!',
                                 'right in the block hole by %s! well negotiated by %s',
                                 'swings and misses.. a stare from %s! %s living dangerously!',
                                 'good ball from %s, %s hits well but straight to the man at short extra cover!..well fielded!',
                                 'well bowled %s, outside off and %s misses that!',
                                 'its fast and swinging dangerously from %s.. missed %s\'s off stump by inches!',
                                 'dangerous delivery from %s! batsman %s had no clue about it',
                                 'oh that was a quick one from %s, too good for %s!',
                                 'oh %s! that was perilously close to the off stump!, %s looking nervous here!',
                                 'that bounced too much from %s.. %s had no clue.. and well taken by the keeper too!',
                                 'dangerous short ball from %s.. %s didn\'t have a clue !', ]

    commentary_dot_ball = ['beautiful delivery from %s, missed %s \'s stumps by inches!',
                           'good from %s, that\'s very well defended by %s!',
                           'well bowled %s and that\'s a solid defence from %s',
                           'accurate from %s and that\'s a textbook defence from %s!',
                           'big big appeal from %s... but umpire shakes his head!.. %s looks relaxed',
                           'oh %s, He\'s Bowling a Good Line and Length.. %s looks unsettled',
                           'swings and misses.. a stare from %s %s living dangerously!',
                           'deceived the batsman.. and %s gives %s a stare!',
                           'big appeal from %s.. but umpire says not out! %s looks nervous',
                           'that looks close, but not out says the umpire! %s is unlucky and %s, you\'re a lucky man!',
                           'missed it, there is a stare from %s at %s',
                           'oh swing and a miss!.. well bowled %s! %s is looking nervous!',
                           'good ball from %s, %s hits well but straight to the man at short extra cover!.. well fielded!',
                           'magnificent delivery from %s.. just above %s \'s bails to the keeper!',
                           'oh what a ball from %s ! tantalizingly close to the stumps... a near miss for %s!',
                           '%s thinks there is an edge..? keeper is appealing.. %s looks unhappy! but the umpire shakes his head!',
                           'magnificent from %s, deceived %s and nearly missed the off stump',
                           'beautiful slow ball from %s.. fooled %s!',
                           'bad ball from %s but that\'s hit in the air by %s, but falls in no man\'s land',
                           'full from %s, driven nicely by %s but the fielder was lightning quick! saved a certain boundary!',
                           'a little short from %s, played well by %s but straight to the fielder!',
                           'slower ball from %s and %s misses it!']

    # MILESTONES
    commentary_partnership_milestone = ['this has been a terrific partnership between %s and %s!',
                                        'what a partnership this has been between %s and %s!',
                                        'what a useful partnership this by %s and %s!',
                                        'this was a magnificent partnership by %s and %s',
                                        'take a bow %s, %s, one of the best partnerships ever!',
                                        'ends a terrific partnership between these two.. good work %s, %s!']
    commentary_out_first_ball = ['Out first ball.. %s has to go!!',
                                 'gone! %s is out without tickling the scoreboard!',
                                 'gone... first ball wicket, and nightmare for %s!',
                                 'Disappointment for %s! gone for a duck!',
                                 'That\'s a slow walk back when you\'re out first ball, %s!',
                                 '%s is out without disturbing the scoreboard!', ]
    commentary_nineties = ['Oh %s will be so disappointed! Gone in the nervous nineties!',
                           'oh %s! what a shame! missed a deserving century!',
                           'gone in the nervous nineties! %s will be so disappointed here!',
                           'needless shot! lost a brilliant century from %s!',
                           'oh gone in the nineties.. %s will be kicking himself!',
                           'unlucky! gone in the nineties.. %s!',
                           'oh missed a well deserving ton.. well played %s!']

    commentary_forties = ['Oh %s.. has lost a fifty!',
                          'oh %s! what a shame! missed a deserving half century!',
                          'gone in the forties! %s will be so disappointed here!',
                          'needless shot! lost a brilliant half century from %s!',
                          'unlucky! lost a fifty.. %s!',
                          'oh missed a well deserving half century.. well played %s!']

    commentary_out_duck = ['The batsman will be so disappointed.. he is gone for nothing!',
                           'gone for a duck! His nightmare continues!',
                           'that\'s his second duck in a row in this season!',
                           'slow walk back when you\'re gone for a duck!',
                           'out for nothing!',
                           'gone for none! The scoreboard is undisturbed by him!',
                           'gone for zero.. disappointment for the batsman!',
                           'he hasn\'t troubled the scoreboard!']
    commentary_out_fifty = ['what a valuable innings from %s!',
                            'useful innings from %s comes to a close!',
                            'terrific from %s! he is out but the damage is done!',
                            'big applause from the crowd for %s!',
                            'standing ovation for %s here!',
                            'the crowd acknowledge this innings from %s! brilliant!',
                            'the party is over, the crowd loved the innings.. take a bow %s!',
                            'take a bow, what an innings it was from %s!',
                            'terrific knock comes to an end from %s!',
                            'end of an unbelievable innings from %s']
    commentary_wide = ['he has lost his line completely.. wide called by %s!',
                       'oh that\'s a harsh call from %s!',
                       'not good bowling from him!.. %s calls wide',
                       'this will irritate the captain!.. another wide called by umpire %s',
                       'he is leaking runs here!.. wide called again by %s',
                       'leg side.. umpire %s says wide!',
                       'poor bowling, wide delivery called by %s!',
                       'oh big appeal from the keeper but Wide says %s!',
                       'bowler under pressure here!.. %s signals wide again!', ]
    commentary_no_ball = ['good delivery , batsman misses it.. but No ball called!',
                          'well bowled.. but no ball!',
                          'he has lost his run up !',
                          'oh that\'s a dangerous beamer! no ball called!',
                          'bowler tries a full toss but that\'s way above the waist height!',
                          'bowler loses his rhythm! no ball called',
                          'bowled him! but oh that\'s a no ball!',
                          'in the air and taken!. but no ball called!!',
                          'oh that\'s a high full toss! no ball called!']
    commentary_milestone = ['Its been a terrific knock by %s today..!',
                            'what a performance by %s...!',
                            'Take a bow %s! What a knock!',
                            'Absolutely magnificent innings %s!',
                            '%s! he is playing a gem of an innings!',
                            'this man %s is on fire today!',
                            '%s decides tonight is going to be his night!',
                            'that\'s it! A brilliant knock under pressure by %s!',
                            '%s! he is on absolute fire here !']
    commentary_goingtolose = ['surely its all over now for %s!',
                              'its literally impossible to win for %s now!',
                              'that, I am sure, is the final nail on the coffin for %s!',
                              'that\'s the end of all hopes for %s now!',
                              'its surely all over for %s..!',
                              'oh %s, they need some miracle to win this match!',
                              'spare a thought for %s, one by one they are going down the drain!',
                              ]
    commentary_fifer = ['what a bowler he is!',
                        'he has totally rattled this batting team!',
                        'he is on absolute fire!',
                        'he has been on fire with the ball today!',
                        'that\'s a fantastic five-fer!',
                        'he has intimidated every batsmen today!',
                        'he has made an awful mess of this innings!', ]
    commentary_hattrick = ['that\'s it! that\'s a hat-trick !!',
                           'Hat-trick for the bowler!',
                           '3 in 3! This man is on absolute fire!',
                           'hat-trick for the bowler! what a performance from him!', ]
    commentary_on_a_hattrick = ['he is on a hattrick now!',
                                'two in two and he is on a hattrick here!',
                                'hattrick ball coming up.. crowd on their feet!', ]

    commentary_match_won = ['that\'s it, that\'s the end of the match!',
                            'that\'s it, they have won the match!',
                            'that\'s the end of the match!']
    commentary_all_out = ['that\'s it! they have been bowled out!',
                          'terrific bowling performance, they have been bowled out!',
                          'its all over for them!',
                          'done ! all out!']

    # LAST OVER/MATCH/INNS
    commentary_last_ball_match = ['this is it.. the last ball of the match!',
                                  'we are down to the last ball of the match',
                                  'last ball of this match coming up!']
    commentary_last_ball_innings = ['last ball of this innings !']
    commentary_last_over_match = ['last over of the match!',
                                  'last over! the crowd on their feet!',
                                  'we are all set to witness a last over thriller!',
                                  'here we go! last over of this match!',
                                  'this is what it has come down to! the last over!']
    commentary_last_over_innings = ['last over of this innings coming up',
                                    'we are down to the last over!',
                                    'last over of the innings!']

    # chasing and lost
    commentary_lost_chasing = ['end of the match.. end of the chase tough luck %s, well played %s!!',
                               'afraid to say that\'s the end of the chase for %s! magnificent performance %s',
                               '%s! they have failed in this chase!.. good bowling %s',
                               '%s fought well, but the %s bowlers dominated today!',
                               'the pressure was too much for %s!.. well played %s',
                               'the %s bowling team was too good for %s!',
                               '%s was totally outsmarted by %s!',
                               'Well %s, they have succumbed to pressure.. well played %s!']

    # over
    commentary_expensive_over = ['what an expensive over by %s!',
                                 'oh dear! %s.. this is a costly over.. they will have to pay for this!',
                                 'an expensive over by %s! this could turn the course of the match!',
                                 'costly over from %s.. this could change the match!',
                                 'expensive over.. %s is shattered!',
                                 'poor bowling by %s.. expensive over!',
                                 'expensive over! %s is totally battered!',
                                 'that\'s an expensive over from %s!', ]
    commentary_economical_over = ['what an over from %s.. very economical!',
                                  'magnificent over from %s..!',
                                  'superb over %s!.. very disciplined!',
                                  'very economical bowling from %s!',
                                  'an economical over by %s!']
    commentary_maiden_over = ['what a bowler %s is.. that\'s a maiden over!',
                              'maiden over from %s!!!.. brilliant!',
                              'that\'s it.. its a maiden over for %s.. brilliant!']

    # bowler's last over
    commentary_bowler_last_over = ['this is the last of his allotted overs!',
                                   'bowling his last over!',
                                   'he is going to bowl the last of his allotted overs',
                                   'bowler with his last over!',
                                   'he is gonna bowl his last over!']
    # check if bowler had a good spell
    commentary_bowler_good_spell = ['he had a terrific spell so far!',
                                    'he was in good form today!',
                                    'he bowled really well today!',
                                    'he had a nice spell so far!',
                                    'he had a good day with the ball!', ]
    commentary_bowler_bad_spell = ['he didn\'t have a good day so far!',
                                   'he was very expensive today!',
                                   'he was not in form today!.. too expensive',
                                   'he was not in good touch today!',
                                   'he didn\'t have a good day with the ball', ]

    # check if bowler is spinner
    commentary_spinner_into_attack = ['the spinner, to start the over!',
                                      'spinner into the attack!.. lets see if he gets the ball to turn!',
                                      'we have a spin bowler into the attack',
                                      'the spinner to start his over',
                                      'we have a spinner to bowl this over',
                                      'the spin bowler to start the over', ]
    commentary_pacer_into_attack = ['a pacer into the attack now!',
                                    'a pacer into the attack!.. lets see if he can get some swing',
                                    'seamer to start a new over',
                                    'a fast bowler to start a new over!',
                                    'a quick bowler into the attack here',
                                    'the seamer to begin a new over.. ',
                                    'we have a fast bowler into the attack', ]
    commentary_medium_into_attack = ['medium pacer into the attack',
                                     'a medium pacer, to start a new over',
                                     'the medium pacer to start the over.. lets see if he can induce a wicket',
                                     'we have a medium bowler into the attack', ]
    commentary_captain_to_bowl = ['the skipper to bowl a new over',
                                  'captain to start a new over here!',
                                  'the skipper, to begin a new over',
                                  'the captain to bowl now!',
                                  'lets see if the captain can make an impact!',
                                  'captain is going to try an over now!',
                                  'captain coming on to bowl this over!']

    # rain
    commentary_rain_cloudy = ['well it looks cloudy and looks like it might rain..',
                              'oops.. there are some rain clouds above us.. ',
                              'weather doesnt look good.. can see the rain clouds developing....']
    commentary_rain_drizzling = ['this is not looking good, a slight drizzle.. we can see raincoats among the crowd',
                                 'it started drizzling a little now..  tougher for the players',
                                 'slight drizzle, and fielding is getting tougher!.. we could see the spectators getting their coats']
    commentary_rain_heavy = ['this is bad.. it started pouring!.. Umpires looking concerned',
                             'oops it has started pouring!.. Umpires are having a chat with the players',
                             'Its raining.. !!']
    commentary_rain_interrupt = ['heavy rain I am afraid to say the match might have to be called off!',
                                 'this is an unfortunate end ! Rain has forced to call off the match',
                                 'heavy rains.. and the umpires and the match referee have decided to call off the match']
