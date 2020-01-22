import io
from twisted.internet import reactor

from ygo.card import Card
from ygo.constants import POSITION
from ygo.duel_reader import DuelReader
from ygo.parsers.duel_parser import DuelParser
from ygo.utils import process_duel


def msg_select_position(self, data):
    data = io.BytesIO(data[1:])
    player = self.read_u8(data)
    code = self.read_u32(data)
    card = Card(code)
    positions = POSITION(self.read_u8(data))
    self.cm.call_callbacks("select_position", player, card, positions)
    return data.read()


def select_position(self, player, card, positions):
    pl = self.players[player]
    m = pl.notify(pl._("Select position for %s:") % (card.get_name(pl),), no_abort="Invalid option.", persistent=True, restore_parser=DuelParser)

    def r(caller):
        if caller.text == "ua":
            self.set_responsei(1)
        elif caller.text == "da":
            self.set_responsei(2)
        elif caller.text == "ud":
            self.set_responsei(4)
        elif caller.text == "dd":
            self.set_responsei(8)
        else:
            pl.notify(DuelReader, r, no_abort=pl._("Invalid command"), restore_parser=DuelParser)

        reactor.callLater(0, process_duel, self)

    if positions & POSITION.FACEUP_ATTACK:
        pl.notify("ua: " + pl._("Face-up attack"))
    if positions & POSITION.FACEDOWN_ATTACK:
        pl.notify("da: " + pl._("Face-down attack"))
    if positions & POSITION.FACEUP_DEFENSE:
        pl.notify("ud: " + pl._("Face-up defense"))
    if positions & POSITION.FACEDOWN_DEFENSE:
        pl.notify("dd: " + pl._("Face-down defense"))

    pl.notify(DuelReader, r, no_abort=pl._("Invalid command"), restore_parser=DuelParser)


MESSAGES = {19: msg_select_position}

CALLBACKS = {"select_position": select_position}
