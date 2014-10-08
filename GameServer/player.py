__author__ = 'meskill'
__date__ = '30.09.2014 19:10'

import logging
from struct import unpack
from threading import Lock

from game import Game


END = b'\x80'  # mark of end of input

players = {}


def read_msg(rfile):
    cmd = rfile.read(1)[0]
    line = []
    while True:
        b = rfile.read(1)
        if b == END: break
        line.append(b)
    return cmd, b''.join(line)


def auth(id):
    return True


class Player:
    def login(self, id):
        '''Login
            params: id: str - id
            return: 0 - if not authorized
                    1 - if authorized
                    2 - 1 and id is a host of not started game
                    3 - 1 and id is a player in not started game
                    4 - 1 and id is playing now'''
        self.id = id
        logging.debug('LoginID: %s for client %s', self.id, self.client_address)
        r = 0
        if auth(self.id):
            r = 1
            self.type = self.player
            if self.id in players:
                game = players[self.id]
                if game.status == Game.LOBBY:
                    r = 3
                    if game.players[0] == self:
                        r = 2
                        self.type = self.host
                elif game.status == Game.INGAME:
                    r = 4
        self.wfile.write(bytes((r,)))

    def get_gamesList(self, params):
        '''Get list of games lobby
            params: -
            return: list of lobbies'''
        for game in Game.gamesLobby:
            self.wfile.write(game.get_info() + b'\n')

    def create_game(self, params):
        '''Create new game
            params: n : int - size of map, m : int - max players in game
            return: -'''
        size, max_players = unpack('BB', params)
        logging.debug('Creating game: id=%s,size=%d, max_players=%d by %s', self.id, size, max_players,
                      self.client_address)
        game = Game(self, size, max_players)
        players[self.id] = game
        self.type = self.host

    def connect_game(self, gameID):
        '''Connect to existing game
            params: id: str - game id
            return: 1 if connected else 0'''
        game = Game.gamesLobby.get(gameID)
        if not game is None and self.id and len(game.players) < game.max_players:
            game.players.append(self)
            players[self.id] = gameID
            self.wfile.write(b'\x01')
        else:
            self.wfile.write(b'\x00')

    def start_game(self, params):
        '''Start game (Host only)
            params: -
            return: -'''
        game = players[self.id]
        game.start_game()

    def subscribe(self, params):
        '''Subscribe to changing in games
            params: -
            return: -'''
        Game.subscribers.add(self)

    def get_help(self, params):
        '''Get this help'''
        for (i, x) in self.Commands.items():
            self.wfile.write(('%d : %s\n\n' % (i, x.__doc__)).encode())

    Commands = {0: get_help,
                1: login,
                11: create_game,
                12: get_gamesList,
                13: subscribe,
                14: connect_game,
                21: start_game,
                42: lambda self: self.connection.wfile.write(b'fuck you, Stork!')}

    new = {0, 1, 42}
    player = new | {11, 12, 13, 14}
    host = player | {21}

    def __init__(self, rfile, wfile, client_address=None):
        logging.debug('New Client: %s', client_address)
        self.id = None
        self.rfile = rfile
        self.wfile = wfile
        self.client_address = client_address
        self.lock = Lock()
        self.type = self.new

    def serve(self):
        try:
            while True:
                cmd, msg = read_msg(self.rfile)
                with self.lock:
                    self.wfile.write(bytes((cmd,)))
                    logging.debug('Command: %d from %s', cmd, self.client_address)
                    if cmd in self.type:
                        self.Commands[cmd](self, msg)
                    else:
                        self.reject()
                    self.wfile.write(END)
        except Exception as e:
            logging.debug('Client disconnected: %s with Error: %s', self.client_address, e)

    def reject(self):
        self.wfile.write(b'reject')
        logging.debug('Command rejected to %s', self.client_address)

    def send(self, cmd, message):
        with self.lock:
            self.wfile.write(bytes((cmd,)) + message + END)