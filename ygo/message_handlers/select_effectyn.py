import io
from twisted.internet import reactor

from ygo.card import Card
from ygo.duel_reader import DuelReader
from ygo.utils import process_duel


def msg_select_effectyn(self, data):
    data = io.BytesIO(data[1:])
    player = self.read_u8(data)
    card = Card(self.read_u32(data))
    card.set_location(self.read_u32(data))
    desc = self.read_u32(data)
    self.cm.call_callbacks("select_effectyn", player, card, desc)
    return data.read()


def select_effectyn(self, player, card, desc):
    pl = self.players[player]
    old_parser = pl.connection.parser

    def r(caller):
        if caller.text.lower().startswith('y'):
            self.set_responsei(1)
        elif caller.text.lower().startswith('n'):
            self.set_responsei(0)
        else:
            pl.notify(question)
            pl.notify(DuelReader, r, restore_parser=old_parser)

    spec = card.get_spec(pl)
    question = pl._("Do you want to use the effect from {card} in {spec}?").format(
        card=card.get_name(pl), spec=spec
    )
    s = card.get_effect_description(pl, desc, True)
    if s != "":
        question += "\n" + s
    pl.notify(question)
    pl.notify(DuelReader, r, restore_parser=old_parser)


MESSAGES = {12: msg_select_effectyn}

CALLBACKS = {"select_effectyn": select_effectyn}
