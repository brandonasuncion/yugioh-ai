from _duel import ffi, lib
import os
import io
import sqlite3
import struct
import random
import binascii
import callback_manager

deck = [int(l.strip()) for l in open('deck.ydk')]
db = sqlite3.connect('cards.cdb')
db.row_factory = sqlite3.Row
LOCATION_DECK = 1
LOCATION_HAND = 2
LOCATION_MZONE = 4
LOCATION_SZONE = 8

POS_FACEUP_ATTACK = 1
POS_FACEDOWN_DEFENSE = 8
QUERY_CODE = 1
QUERY_ATTACK = 0x100
QUERY_DEFENSE = 0x200

@ffi.def_extern()
def card_reader_callback(code, data):
	cd = data[0]
	row = db.execute('select * from datas where id=?', (code,)).fetchone()
	cd.code = code
	cd.alias = row['alias']
	cd.setcode = row['setcode']
	cd.type = row['type']
	cd.level = row['level']
	cd.attack = row['atk']
	cd.defense = row['def']
	cd.race = row['race']
	cd.attribute = row['attribute']
	return 0

lib.set_card_reader(lib.card_reader_callback)

scriptbuf = ffi.new('char[131072]')
@ffi.def_extern()
def script_reader_callback(name, lenptr):
	fn = ffi.string(name)
	if not os.path.exists(fn):
		lenptr[0] = 0
		return ffi.new('byte *', None)
	s = open(fn, 'rb').read()
	buf = ffi.buffer(scriptbuf)
	buf[0:len(s)] = s
	lenptr[0] = len(s)
	return ffi.cast('byte *', scriptbuf)

lib.set_script_reader(lib.script_reader_callback)

class Card(object):
	@classmethod
	def from_code(cls, code):
		row = db.execute('select * from datas where id=?', (code,)).fetchone()
		cd = cls()
		cd.code = code
		cd.alias = row['alias']
		cd.setcode = row['setcode']
		cd.type = row['type']
		cd.level = row['level']
		cd.attack = row['atk']
		cd.defense = row['def']
		cd.race = row['race']
		cd.attribute = row['attribute']
		row = db.execute('select * from texts where id=?', (code,)).fetchone()
		cd.name = row['name']
		cd.desc = row['desc']
		return cd

class Duel:
	def __init__(self):
		self.buf = ffi.new('char[]', 4096)
		self.duel = lib.create_duel(0)
		lib.set_player_info(self.duel, 0, 8000, 5, 1)
		lib.set_player_info(self.duel, 1, 8000, 5, 1)
		self.cm = callback_manager.CallbackManager()
		self.message_map = {
			90: self.msg_draw,
			40: self.msg_new_turn,
		41: self.msg_new_phase,
		11: self.msg_idlecmd,
		1: self.msg_retry,
		2: self.msg_hint,
		18: self.msg_select_place,
		50: self.msg_move,
		60: self.msg_summoning,
		16: self.msg_select_chain,
		61: self.msg_summoned,
		54: self.msg_set,
		10: self.msg_select_battlecmd,
		110: self.msg_attack,
		113: self.msg_begin_damage,
		114: self.msg_end_damage,
		111: self.msg_battle,
		91: self.msg_damage,
		}
		self.state = ''

	def load_deck(self, player, cards):
		random.shuffle(cards)
		for c in cards:
			lib.new_card(self.duel, c, player, player, LOCATION_DECK, 0, POS_FACEDOWN_DEFENSE);

	def start(self):
		lib.start_duel(self.duel, 0)

	def process(self):
		res = lib.process(self.duel)
		self.process_messages()
		return res

	def process_messages(self):
		l = lib.get_message(self.duel, ffi.cast('byte *', self.buf))
		data = ffi.unpack(self.buf, l)
#		print("received: %r" % data)
		while data:
			msg = int(data[0])
			print(msg)
			data = self.message_map[msg](data)

	def msg_draw(self, data):
		data = io.BytesIO(data[1:])
		player = self.read_u8(data)
		drawed = self.read_u8(data)
		cards = []
		for i in range(drawed):
			c = self.read_u32(data)
			card = Card.from_code(c)
			cards.append(card)
		self.cm.call_callbacks('draw', player, cards)
		return data.read()

	def msg_new_turn(self, data):
		tp = int(data[1])
		self.cm.call_callbacks('new_turn', tp)
		return data[2:]

	def msg_new_phase(self, data):
		phase = struct.unpack('h', data[1:])[0]
		self.cm.call_callbacks('phase', phase)
		return b''

	def msg_idlecmd(self, data):
		self.state = 'idle'
		data = io.BytesIO(data[1:])
		player = self.read_u8(data)
		summonable = self.read_cardlist(data)
		spsummon = self.read_cardlist(data)
		repos = self.read_cardlist(data)
		idle_mset = self.read_cardlist(data)
		idle_set = self.read_cardlist(data)
		idle_activate = self.read_cardlist(data, True)
		to_bp = self.read_u8(data)
		to_ep = self.read_u8(data)
		cs = self.read_u8(data)
		self.cm.call_callbacks('idle', summonable, spsummon, repos, idle_mset, idle_set, idle_activate, to_bp, to_ep, cs)
		return b''

	def read_cardlist(self, data, extra=False, extra8=False):
		res = []
		size = self.read_u8(data)
		for i in range(size):
			code = self.read_u32(data)
			card = Card.from_code(code)
			controller = self.read_u8(data)
			location = self.read_u8(data)
			sequence = self.read_u8(data)
			if extra:
				if extra8:
					x = self.read_u8(data)
				else:
					x = self.read_u32(data)
				res.append((card, controller, location, sequence, x))
			else:
				res.append((card, controller, location, sequence))
		return res

	def msg_retry(self, buf):
		print("retry")
		return ''

	def msg_hint(self, data):
		data = io.BytesIO(data)
		print(repr(data.read()))
		return b''

	def msg_select_place(self, data):
		data = io.BytesIO(data)
		msg = self.read_u8(data)
		player = self.read_u8(data)
		count = self.read_u8(data)
		flag = self.read_u32(data)
		self.cm.call_callbacks('select_place')
		return b''

	def msg_select_battlecmd(self, data):
		data = io.BytesIO(data[1:])
		player = self.read_u8(data)
		activatable = self.read_cardlist(data, True)
		attackable = self.read_cardlist(data, True, True)
		to_m2 = self.read_u8(data)
		to_ep = self.read_u8(data)
		self.cm.call_callbacks('select_battlecmd', player, activatable, attackable, to_m2, to_ep)
		return b''

	def msg_attack(self, data):
		data = io.BytesIO(data[1:])
		attacker = self.read_u32(data)
		target = self.read_u32(data)
		self.cm.call_callbacks('attack', attacker, target)
		return b''

	def msg_begin_damage(self, data):
		print("%r", data)
		self.cm.call_callbacks('begin_damage')

	def msg_end_damage(self, data):
		self.cm.call_callbacks('end_damage')

	def msg_battle(self, data):
		data = io.BytesIO(data[1:])
		attacker = self.read_u32(data)
		aa = self.read_u32(data)
		ad = self.read_u32(data)
		bd0 = self.read_u8(data)
		tloc = self.read_u32(data)
		da = self.read_u32(data)
		dd = self.read_u32(data)
		bd1 = self.read_u8(data)
		self.cm.call_callbacks('battle', attacker, aa, ad, bd0, tloc, da, dd, bd1)
		return b''

	def msg_damage(self, data):
		data = io.BytesIO(data[1:])
		player = self.read_u8(data)
		amount = self.read_u32(data)
		self.cm.call_callbacks('damage', player, amount)

	def msg_move(self, data):
		data = io.BytesIO(data[1:])
		code = self.read_u32(data)
		location = self.read_u32(data)
		print("Move: code=%d loc=%d" % (code, location))
		return b''

	def msg_summoning(self, data):
		data = io.BytesIO(data[1:])
		code = self.read_u32(data)
		location = self.read_u32(data)
		self.cm.call_callbacks('summoning', Card.from_code(code), location)
		return b''

	def msg_select_chain(self, data):
		data = io.BytesIO(data[1:])
		player = self.read_u8(data)
		size = self.read_u8(data)
		spe_count = self.read_u8(data)
		forced = self.read_u8(data)
		hint_timing = self.read_u32(data)
		other_timing = self.read_u32(data)
		self.cm.call_callbacks('select_chain', player, size, spe_count)
		return b''

	def msg_summoned(self, data):
		data = io.BytesIO(data[1:])
		print("summoned: %r" % data.read())
		return b''

	def msg_set(self, data):
		data = io.BytesIO(data[1:])
		code = self.read_u32(data)
		loc = self.read_u32(data)
		print("Set: code=%d loc=%d" % (code, loc))
		return b''

	def read_u8(self, buf):
		return struct.unpack('b', buf.read(1))[0]

	def read_u32(self, buf):
		return struct.unpack('I', buf.read(4))[0]

	def set_responsei(self, r):
		lib.set_responsei(self.duel, r)

	def set_responseb(self, r):
		buf = ffi.new('char[64]', r)
		lib.set_responseb(self.duel, ffi.cast('byte *', buf))

	def hand(self, player):
		cards = []
		ncards = lib.query_field_count(self.duel, player, LOCATION_HAND)
		for i in range(ncards):
			flags = QUERY_CODE
			bl = lib.query_card(self.duel, player, LOCATION_HAND, i, flags, ffi.cast('byte *', self.buf), False)
			buf = io.BytesIO(ffi.unpack(self.buf, bl))
			f = self.read_u32(buf)
			f = self.read_u32(buf)
			code = self.read_u32(buf)
			cards.append(Card.from_code(code))
		return cards

	def mzone(self, player):
		cards = []
		ncards = lib.query_field_count(self.duel, player, LOCATION_MZONE)
		for i in range(ncards):
			flags = QUERY_CODE | QUERY_ATTACK | QUERY_DEFENSE
			bl = lib.query_card(self.duel, player, LOCATION_HAND, i, flags, ffi.cast('byte *', self.buf), False)
			buf = io.BytesIO(ffi.unpack(self.buf, bl))
			f = self.read_u32(buf)
			f = self.read_u32(buf)
			code = self.read_u32(buf)
			card = Card.from_code(code)
			card.attack = self.read_u32(buf)
			card.defense = self.read_u32(buf)
			cards.append(card)
		return cards

	def get_card(self, player, loc, seq):
		flags = QUERY_CODE
		bl = lib.query_card(self.duel, player, loc, seq, flags, ffi.cast('byte *', self.buf), False)
		buf = io.BytesIO(ffi.unpack(self.buf, bl))
		f = self.read_u32(buf)
		f = self.read_u32(buf)
		code = self.read_u32(buf)
		return Card.from_code(code)

class TestDuel(Duel):
	def __init__(self):
		super(TestDuel, self).__init__()
		self.cm.register_callback('draw', self.on_draw)

	def on_draw(self, player, cards):
		print("player %d draw %d cards:" % (player, len(cards)))
		for c in cards:
			print(c.name + ": " + c.desc)

if __name__ == '__main__':
	d = TestDuel()
	d.load_deck(0, deck)
	d.load_deck(1, deck)
	d.start()

	while True:
		flag = d.process()
		if flag & 0x10000:
			resp = input()
			if resp.startswith('`'):
				b = binascii.unhexlify(resp[1:])
				d.set_responseb(b)
			else:
				resp = int(resp, 16)
				d.set_responsei(resp)