__author__ = 'meskill'
__date__ = '30.09.2014 19:10'

from struct import unpack, pack
import logging

END = b'\x80'


class Player:
    def __init__(self, request_handler):
        self.request = request_handler

    def login(self):
        id = []
        while True:
            b = self.request.rfile.read(1)
            if b == END: break
            id.append(b)
        self.id = b''.join(id)
        logging.debug('LoginID: %s', self.id)

    def get_gamesList(self):
        pass

    def create_game(self):
        pass

    def serve_commands(self):
        while True:
            cmd = self.request.rfile.read(1)
            self.request.wfile.write(cmd)
            cmd, = unpack('B', cmd)
            logging.debug('Command: %d', cmd)
            if cmd == 1:
                self.login()
            elif cmd == 11:
                self.create_game()
            self.request.wfile.write(END)

    def send(self, message):
        self.socket.wfile.write(message)