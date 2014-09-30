__author__ = 'meskill'
__date__ = '21.09.2014 18:29'

import socketserver
from struct import pack, unpack

import map_generator

END=b'\x80'

class myRequestHandler(socketserver.StreamRequestHandler):

    ids={}

    def __init__(self, request, client_address, server):
        socketserver.StreamRequestHandler.__init__(self, request, client_address, server)

    def return_map(self):
        n, m, l, t, tl, h, w, ot = unpack('b'*8, self.rfile.read(8))
        rmap = map_generator.generate_map(n, m, l, t, tl, h, w, ot)
        self.wfile.write(pack('b', 11) + pack('b', len(rmap)) + pack('b', len(rmap[0])))
        self.wfile.write(b''.join(b''.join(map(lambda x: pack('b', x), y)) for y in rmap))
        print(n, m, l, t, tl, h, w, ot)

    def return_stats(self):
        id=[]
        while True:
            b=self.rfile.read(1)
            if b==END: break
            id.append(b)
        id=b''.join(id)
        if id in self.ids:
            self.wfile.write(b'\x01')
        else:
            self.ids[id]=True
            self.wfile.write(b'\x00')
        print(id)

    def handle(self):
        print(self.client_address)
        c=self.rfile.read(1)
        self.wfile.write(c)
        c=unpack('b',c)[0]
        print(c, end=' :  ')
        if c==1:
            self.return_stats()
        elif c==11:
            self.return_map()
        self.wfile.write(END)
        self.rfile.close()
        self.wfile.close()


if __name__ == '__main__':
    srv = socketserver.TCPServer(('', 27000), myRequestHandler)
    srv.serve_forever()