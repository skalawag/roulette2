#! /usr/bin/env python
# coding=utf-8
"""
roulette.py - Phenny Russian Roulette Module
Copyright 2014, Mark Scala
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

from __future__ import division
import os, random, time, shelve, math

RELIEF = ["%s wipes the sweat from his brow.",
          "I think %s peed his pants.",
          "%s weeps a tear of relief.",
          "%s fainted!",
          "%s crapped his pants!",
          ]

EXCLAMATIONS = ["Holy, cow! %s blew his head off!",
                "OH SNAP! %s brain matter is everywhere!",
                "%s falls to the floor like a sack of flour!",
                "%s does the obituary mambo!",
                "No love for %s",
                "HAHAHAHA! %s lost!",
                ]
CHANGE = ["%s, it's your turn.", "%s, wipe that smirk off your face. It's your turn!"]

class Player():
    def __init__(self, name, wins=0, losses=0, seppuku=0):
        self.name = name
        self.wins = wins
        self.losses = losses
        self.seppuku = seppuku

    def save(self):
        db = shelve.open('roulette.db')
        try:
            record = db['roulette']
        except KeyError:
            record = {}
        me = self.__dict__.copy()
        me.pop('name')
        record[self.name] = me
        db['roulette'] = record
        db.close()

    def invisible(self):
        if self.seppuku:
            return True

    def can_play(self):
        if not self.seppuku:
            return True
        elif (time.time() - self.seppuku) > (60 * 60):
            self.seppuku = 0
            return True

    def percentage(self):
        if self.wins + self.losses > 0:
            return (self.wins / (self.wins + self.losses) * 100)
        else:
            return 0

def load_players():
    players = []
    db = shelve.open('roulette.db')
    if db.has_key('roulette'):
        for key, value in db['roulette'].iteritems():
            players.append(Player(key, **value))
    return players

players = load_players()

def seppuku(player):
    if player and not player.seppuku and player.wins + player.losses > 0:
        player.seppuku = time.time()
        player.wins = 0
        player.losses = 0
        player.save()
        return True

def get_player(name):
    for player in players:
        if player.name == name:
            return player
    return Player(name)

class GameState():
    def __init__(self):
        self.challenge = None # None|time.time()
        self.challenger = None
        self.challenged = None
        self.game_on = False

    def reset(self):
        self.challenge = None # None|time.time()
        self.challenger = None
        self.challenged = None
        self.game_on = False

game_state = GameState()

def display_players(phenny, input):
    for p in players:
        print p.name, p.wins, p.losses, p.seppuku
    print "game state"
    print game_state.__dict__
display_players.commands = ['show']

def challenge_allowed():
    if game_state.game_on:
        return False
    elif game_state.challenge:
        if time.time() - game_state.challenge > 60:
            game_state.challenge = time.time()
            return True
        else:
            return False
    else:
        game_state.challenge = time.time()
        return True

def roul_undo(phenny, input):
    """ .undo ::

    undo your previous challenge.
    """
    if input.nick == game_state.challenger.name:
        game_state.reset()
        phenny.say("%s has withdrawn the challenge." % input.nick)
roul_undo.commands = ['undo']

def get_champ():
    res = sorted(players, key=lambda x: x.percentage())
    res.reverse()
    if res:
        return res[0].name
    else:
        return None

def run_game(phenny, input):
    game_state.game_on = True
    playas = [game_state.challenger, game_state.challenged]
    random.shuffle(playas)
    phenny.say("A coin toss will decide the first player....")
    time.sleep(1)
    phenny.say("%s, you win!" % (playas[0].name))
    while 1:
        spin = random.choice([0,1])
        phenny.say("%s spins the cylinder..." % playas[0].name)
        time.sleep(1)
        phenny.say("%s pulls the trigger!" % playas[0].name)
        if spin == 0:
            phenny.say('CLICK')
            time.sleep(1)
            phenny.say(random.choice(RELIEF) % playas[0].name)
            playas.reverse()
        elif spin == 1:
            playas[1].wins += 1
            playas[1].save()
            playas[0].losses += 1
            playas[0].save()
            phenny.say(random.choice(['BANG!', 'KA-POW!', 'BLAMMO!', 'BOOM!',
                                      'BAM!']))
            time.sleep(1)
            phenny.say(random.choice(EXCLAMATIONS) % playas[0].name)
            phenny.say("Congratulations, %s, you are the winner." % playas[1].name)
            game_state.reset()
            global players
            players = load_players()
            break

def seppuku_time_left(nick):
    player = get_player(nick)
    # time left, in minutes
    return round((60.0 - (( time.time() - player.seppuku) / 60)),   1)

def roul_challenge(phenny, input):
    """ .r PLAYER ::

    challenge PLAYER to a game of Russian Roulette.
    """
    if not challenge_allowed():
        return None
    if input.nick == input.group(2):
        phenny.say("%s, suicide is not allowed!" % input.nick)
        return None

    # Verify that no player has seppuku'd too recently
    if not get_player(input.nick).can_play():
        # announce that this player is sidelined, clean up, and exit
        phenny.say("%s, you committed seppuku! You must wait %s minutes to play again." % (input.nick, seppuku_time_left(input.nick)))
        game_state.reset()
        return
    elif not get_player(input.group(2)).can_play():
        # announce that this player is sidelined, clean up,  and exit
        phenny.say("%s, %s committed seppuku! He cannot play for %s more minutes." % (input.nick, input.group(2), seppuku_time_left(input.group(2))))
        game_state.reset()
        return

    # set up players
    game_state.challenger = get_player(input.nick)
    game_state.challenger.save()
    game_state.challenged = get_player(input.group(2))
    game_state.challenged.save()

    if game_state.challenged.name == 'NO_IAM_BOT':
        phenny.say("NO_IAM_BOT accepts all challenges!")
        run_game(phenny, input)
    elif game_state.challenged.name == get_champ():
        phenny.say("The Champion always accepts!")
        run_game(phenny, input)
    else:
        phenny.say("%s, %s has challenged you to a game of Russian Roulette! Do you accept the challenge?" % (input.group(2), input.nick))
roul_challenge.commands = ['roulette', 'r']

def roul_accept(phenny, input):
    """ .pff | .yes | .acc | .die! ::

    accept a challenge with varing degrees of chutzpah.
    """
    if game_state.game_on:
        pass
    elif not game_state.challenge:
        phenny.say("%s, you dolt! You have not been challenged!" % input.nick)
    elif input.nick != game_state.challenged.name:
        phenny.say("%s, let %s speak for himself!" % (input.nick,
                                                      game_state.challenged.name))
    else:
        phenny.say("%s has accepted the challenge! Let the game begin!" % input.nick)
        run_game(phenny, input)
roul_accept.commands = ['accept', 'yes', 'acc', 'hell-yeah', 'pff', 'die!']

def roul_decline(phenny, input):
    """ .no ::

    decline a challenge like a yella dog.
    """
    insults = ['%s, %s is yella and will not play.',
           '%s, %s is a fraidy-cat, and will not play.',
           '%s, %s is going to run home and cry.',
           ]
    if not game_state.challenge:
        phenny.say("%s, there has been no challenge to Russian Roulette. Get a life!" % (input.nick))
    elif game_state.challenged.name != input.nick:
        phenny.say("%s, let %s speak for himself!" % (input.nick,
                                                      game_state.challenged.name))
    else:
        insult = random.choice(insults)
        phenny.say(insult % (game_state.challenger.name, input.nick))
        game_state.reset()
roul_decline.commands = ['decline', 'no', 'get-lost', 'buzz-off']

def roul_get_ranking(phenny, input):
    """ .rstats ::

    display the overall ranking of all players.
    """
    if game_state.game_on:
        pass
    else:
        global players
        players = load_players()
        res = sorted(players, key=lambda x: x.percentage())
        res.reverse()
        res = [p for p in res if not p.invisible()  and p.wins + p.losses > 0]
        if not res:
            phenny.say("Ain't no one here!")
        else:
            for player in res:
                phenny.say('%.3f%%  %s (total rounds: %s)' % (player.percentage(),
                                                              player.name,
                                                              player.wins + player.losses))
roul_get_ranking.commands = ['rranking', 'rall', 'rstats']

def player_exists(name):
    for player in players:
        if player.name == name:
            return True

def roul_seppuku(phenny, input):
    """ .seppuku ::

    Commit seppuku, and be reincarnated tomorrow.
    """
    if game_state.game_on:
        pass
    elif seppuku(get_player(input.nick.strip())):
        phenny.say("%s has committed seppuku!" % input.nick)
        phenny.say("%s, you can play again in %s minutes." % (input.nick, seppuku_time_left(input.nick)))
        global players
        players = load_players()
roul_seppuku.commands = ['seppuku']

def reboot(phenny, input):
    if input.nick != 'skalawag':
        phenny.say("%s, you do not have the auctoritas to do that!" % input.nick)
        return
    try:
        os.system('rm roulette.db')
        global players
        players = []
        phenny.say('Russian Roulette is rebooted!')
    except:
        phenny.say('Mmm. Something went wrong.')
reboot.commands = ['reboot']

if __name__ == '__main__':
    print __doc__
