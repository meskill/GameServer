__author__ = 'meskill'
__date__ = '30.09.2014 19:10'

import logging
from struct import unpack
from threading import Lock

from game import Game


END = b'\x80'  # mark of end of input

games = {}
players = {}


class Player:
    def login(self):
        id = []
        while True:
            b = self.connection.rfile.read(1)
            if b == END: break
            id.append(b)
        self.id = b''.join(id)
        logging.debug('LoginID: %s', self.id)
        self.type = self.player

    def get_gamesList(self):
        self.connection.rfile.read(1)  # END
        for game in games.values():
            self.connection.wfile.write(game.get_info() + b'\n')

    def create_game(self):
        size, max_players = unpack('BB', self.connection.rfile.read(2))
        logging.debug('Creating game: id=%s,size=%d, max_players=%d', self.id, size, max_players)
        self.connection.rfile.read(1)  # END
        game = Game(self, size, max_players)
        games[self.id] = game
        players[self.id] = self.id
        self.type = self.host

    Commands = {1: login,
                11: create_game,
                12: get_gamesList,
                42: lambda self: self.connection.wfile.write(b'fuck you, Stork!')}

    new = {1, 42}
    player = new + {11, 12}
    host = player

    def __init__(self, request_handler):
        self.id = None
        self.connection = request_handler
        self.lock = Lock()
        self.type = self.new

    def serve(self):
        try:
            while True:
                cmd = self.connection.rfile.read(1)
                with self.lock:
                    self.connection.wfile.write(cmd)
                    cmd = cmd[0]
                    logging.debug('Command: %d', cmd)
                    if cmd in self.type:
                        self.Commands[cmd](self)
                    else:
                        self.reject()
                    self.connection.wfile.write(END)
        except Exception:
            logging.debug('Client disconnected: %s', self.connection.client_address)

    def reject(self):
        pass

    def send(self, message):
        with self.lock:
            self.connection.wfile.write(message)