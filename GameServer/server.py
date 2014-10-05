__author__ = 'meskill'
__date__ = '21.09.2014 18:29'

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(module)s - %(message)s')

import socketserver
from struct import pack, unpack
from player import Player
import map_generator

END = b'\x80'


class myRequestHandler(socketserver.StreamRequestHandler):
    def return_map(self):
        n, m, l, t, tl, h, w, ot = unpack('b' * 8, self.rfile.read(8))
        rmap = map_generator.generate_map(n, m, l, t, tl, h, w, ot)
        self.wfile.write(pack('b', 11) + pack('b', len(rmap)) + pack('b', len(rmap[0])))
        self.wfile.write(b''.join(b''.join(map(lambda x: pack('b', x), y)) for y in rmap))
        print(n, m, l, t, tl, h, w, ot)

    def handle(self):
        logging.debug('New Client: %s', self.client_address)
        p = Player(self)
        p.serve_commands()


if __name__ == '__main__':
    srv = socketserver.ThreadingTCPServer(('', 27000), myRequestHandler)
    logging.info('Server started')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        logging.debug('Server interrupted')