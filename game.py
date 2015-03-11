__author__ = 'meskill'
__date__ = '28.09.2014 23:07'

from threading import Thread


class Game:
	'''
		All functions which should alert any players should return appropriate message in bytes
	'''

	LOBBY = 1
	INGAME = 2

	gamesLobby = set()
	gamesIngame = set()
	subscribers = set()

	def __init__(self, host, size, max_players):
		self.create_game(host, size, max_players)

	def create_game(self, host, size, max_players):
		'''Create new game
		params: host: Player, size:int - 1,2 or 3, max_players:int
		return: size, max_players
		'''
		self.players = [host]
		self.id = host.id
		self.size = size
		self.max_players = max_players
		self.status = self.LOBBY
		self.gamesLobby.add(self)
		return bytes((size, max_players))

	def start_game(self):
		'''Start game
			params: -
			return: -'''
		self.gamesLobby.remove(self)
		self.gamesIngame.add(self)
		self.status = Game.INGAME

	def add_player(self, player):
		'''Add player to game in lobby
			params: player
			return: -'''
		if len(self.players) < self.max_players:
			self.players.append(player)
			return b'\x00'
		return b'\x01'

	def send_all(self, message):
		for p in self.players:
			p.send(message)

	def get_info(self):
		return self.id + (';%d;%d;' % (self.size, self.max_players)).encode() + b','.join(
			map(lambda x: x.id, self.players))

	def __hash__(self):
		return hash(self.id)

	Commands = {101: create_game,
	            102: start_game,
	            103: add_player}

	alert_lobby = {101, 102, 103}
	alert_ingame = {}


def make_alertable(func, cmd, ls):
	def f(*args):
		msg = func(*args)
		if msg is None: msg = b''
		game = args[0]
		for p in getattr(game, ls):
			Thread(target=p.send(cmd, game.id + msg))

	return f


for i, f in Game.Commands.items():
	if i in Game.alert_ingame:
		setattr(Game, f.__qualname__[5:], make_alertable(f, i, 'players'))
	if i in Game.alert_lobby:
		setattr(Game, f.__qualname__[5:], make_alertable(f, i, 'subscribers'))