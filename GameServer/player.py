__author__ = 'meskill'
__date__ = '30.09.2014 19:10'

import logging
from struct import unpack
from threading import Lock

from game import Game


END = b'\x80'  # mark of end of input

gamesLobby = {}
gamesIngame = {}
players = {}


def read_line(rfile):
    line = []
    while True:
        b = rfile.read(1)
        if b == END: break
        line.append(b)
    return b''.join(line)


def auth(id):
    return True


class Player:
    def login(self):
        '''Login
            params: id: str - id
            return: 0 - if not authorized
                    1 - if authorized
                    2 - 1 and id is a host of not started game
                    3 - 1 and id is a player in not started game
                    4 - 1 and id is playing now'''
        self.id = read_line(self.rfile)
        logging.debug('LoginID: %s', self.id)
        r = 0
        if auth(self.id):
            r = 1
            self.type = self.player
            if self.id in players:
                gameID = players[self.id]
                if gameID in gamesLobby:
                    r = 3
                    if gamesLobby[gameID].players[0] == self:
                        r = 2
                        self.type = self.host
                elif gameID in gamesIngame:
                    r = 4
        self.wfile.write(bytes((r,)))

    def get_gamesList(self):
        '''Get list of games lobby
            params: -
            return: list of lobbies'''
        self.rfile.read(1)  # END
        for game in gamesLobby.values():
            self.wfile.write(game.get_info() + b'\n')

    def create_game(self):
        '''Create new game
            params: n : int - size of map, m : int - max players in game
            return: -'''
        size, max_players = unpack('BB', self.rfile.read(2))
        logging.debug('Creating game: id=%s,size=%d, max_players=%d', self.id, size, max_players)
        self.rfile.read(1)  # END
        game = Game(self, size, max_players)
        gamesLobby[self.id] = game
        players[self.id] = self.id
        self.type = self.host

    def connect_game(self):
        '''Connect to existing game
            params: id: str - game id
            return: 1 if connected else 0'''
        gameID = read_line(self.rfile)
        game = gamesLobby[gameID]
        if self.id and len(game.players) < game.max_players:
            game.players.append(self)
            players[self.id] = gameID
            self.wfile.write(b'\x01')
        else:
            self.wfile.write(b'\x00')

    def start_game(self):
        '''Start game (Host only)
            params: -
            return: -'''
        gameID = players[self.id]
        game = gamesLobby[gameID]
        del gamesLobby[gameID]
        gamesLobby[gameID] = game

    def get_help(self):
        '''Get this help'''
        self.rfile.read(1)  # END
        for (i, x) in self.Commands.items():
            self.wfile.write(('%d : %s\n\n' % (i, x.__doc__)).encode())

    Commands = {0: get_help,
                1: login,
                11: create_game,
                12: get_gamesList,
                13: connect_game,
                21: start_game,
                42: lambda self: self.connection.wfile.write(b'fuck you, Stork!')}

    new = {0, 1, 42}
    player = new | {11, 12, 13, 21}
    host = player

    def __init__(self, rfile, wfile, client_address=None):
        self.id = None
        self.rfile = rfile
        self.wfile = wfile
        self.client_address = client_address
        self.lock = Lock()
        self.type = self.new

    def serve(self):
        try:
            while True:
                cmd = self.rfile.read(1)
                with self.lock:
                    self.wfile.write(cmd)
                    cmd = cmd[0]
                    logging.debug('Command: %d', cmd)
                    if cmd in self.type:
                        self.Commands[cmd](self)
                    else:
                        self.reject()
                    self.wfile.write(END)
        except Exception as e:
            logging.debug('Client disconnected: %s with Error: %s', self.client_address, e)

    def reject(self):
        pass

    def send(self, cmd, message):
        with self.lock:
            self.wfile.write(bytes((cmd,)) + message + END)