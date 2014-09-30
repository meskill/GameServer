__author__ = 'meskill'
__date__ = '30.09.2014 19:10'

class Player:
    def __init__(self,id,sock):
        self.id=id
        self.socket=sock

    def send(self,message):
        self.socket.wfile.write(message)