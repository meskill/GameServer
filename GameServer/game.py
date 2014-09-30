__author__ = 'meskill'
__date__ = '28.09.2014 23:07'

from player import Player


class Game:
    def __init__(self, host_socket, id, size, max_players):
        self.players = [Player(id, host_socket)]
        self.id = id
        self.size = size
        self.max_players = max_players

    def send_all(self,message):
        for p in self.players:
            p.send(message)
