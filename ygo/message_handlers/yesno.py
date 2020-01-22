import io
from twisted.internet import reactor

from ygo.card import Card
from ygo.duel_reader import DuelReader
from ygo.utils import process_duel


def msg_yesno(self, data):
    data = io.BytesIO(data[1:])
    player = self.read_u8(data)
    desc = self.read_u32(data)
    self.cm.call_callbacks("yesno", player, desc)
    return data.read()


def yesno(self, player, desc):
    pl = self.players[player]
    old_parser = pl.connection.parser

    def r(caller):
        if caller.text.lower().startswith('y'):
            self.set_responsei(1)
            reactor.callLater(0, process_duel, self)
        elif caller.text.lower().startswith('n'):
            self.set_responsei(0)
            reactor.callLater(0, process_duel, self)
        else:
            pl.notify(opt)
            pl.notify(DuelReader, r, restore_parser=old_parser)

    if desc > 10000:
        code = desc >> 4
        card = Card(code)
        opt = card.get_strings(pl)[desc & 0xF]
        if opt == "":
            opt = pl._("Unknown question from %s. Yes or no?") % (card.get_name(pl))
    else:
        opt = "String %d" % desc
        opt = pl.strings["system"].get(desc, opt)
    pl.notify(opt)
    pl.notify(DuelReader, r, restore_parser=old_parser)


MESSAGES = {13: msg_yesno}

CALLBACKS = {"yesno": yesno}
