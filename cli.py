import random
import sqlite3
import argparse
import re

re._pattern_type = re.Pattern

from ygo import duel as dm
from ygo import globals as glb
from ygo import server
from ygo.language_handler import LanguageHandler
from ygo.duel_reader import DuelReader


class Connection:
    def __init__(self, pl):
        self.player = pl


class Response:
    def __init__(self, text, pl):
        self.text = text
        self.connection = Connection(pl)


class FakeRoom:
    def announce_draw(self):
        pass

    def announce_victory(self, player):
        pass

    def restore(self, player):
        pass

    def process(self):
        pass


class FakePlayer:
    def __init__(self, i, deck):
        self.deck = {"cards": deck}
        self.duel_player = i
        self.cdb = glb.server.db
        self.language = "english"
        self.watching = False
        self.seen_waiting = False
        self.soundpack = False

    _ = lambda self, t: t

    def notify(self, arg1, *args, **kwargs):
        if arg1 == DuelReader:
            func, options = args[0], args[1]
            s = input()
            func(Response(s, self))
        else:
            print(self.duel_player, arg1)

    @property
    def strings(self):
        return glb.language_handler.get_strings(self.language)


class RandomAI(FakePlayer):
    def notify(self, arg1, *args, **kwargs):
        if arg1 == DuelReader:
            func, options = args[0], args[1]
            print(self.duel_player, "options", options)
            s = random.choice(options)
            print(self.duel_player, "chose", s)
            caller = Response(s, self)
            func(caller)
        else:
            print(self.duel_player, arg1)


# from ygo/utils.py
def process_duel(d):
    while d.started:
        res = d.process()
        if res & 0x20000:
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deck1", help="deck for player 1", type=str, required=True)
    parser.add_argument("--deck2", help="deck for player 2", type=str, required=True)
    args = parser.parse_args()

    with open(args.deck1) as f:
        lines = f.readlines()
        deck1 = [int(line) for line in lines if line[:-1].isdigit()]

    with open(args.deck2) as f:
        lines = f.readlines()
        deck2 = [int(line) for line in lines if line[:-1].isdigit()]

    glb.language_handler = LanguageHandler()
    glb.language_handler.add("english", "en")
    glb.language_handler.set_primary_language("english")
    glb.server = server.Server()
    glb.server.db = sqlite3.connect("locale/en/cards.cdb")
    glb.server.db.row_factory = sqlite3.Row

    duel = dm.Duel()
    duel.room = FakeRoom()
    config = {"players": ["Alice", "Bob"], "decks": [deck1, deck2]}
    players = [RandomAI(0, config["decks"][0]), RandomAI(1, config["decks"][1])]
    for i, name in enumerate(config["players"]):
        players[i].nickname = name
        duel.load_deck(players[i])
    duel.players = players
    duel.set_player_info(0, 8000)
    duel.set_player_info(1, 8000)
    # rules = 0, Default
    # rules = 1, Traditional
    # rules = 4, Link
    rules = 1
    options = 0
    duel.start(((rules & 0xFF) << 16) + (options & 0xFFFF))
    process_duel(duel)
    print(duel.lp)


if __name__ == "__main__":
    main()
