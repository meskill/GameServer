__author__ = 'meskill'
__date__ = '28.09.2014 23:07'


class Game:
    LOBBY = 1
    INGAME = 2

    def __init__(self, host, size, max_players):
        self.players = [host]
        self.id = host.id
        self.size = size
        self.max_players = max_players
        self.status = self.LOBBY

    def send_all(self, message):
        for p in self.players:
            p.send(message)

    def get_info(self):
        return self.id + (',%d,%d,' % (self.size, self.max_players)).encode() + b','.join(
            map(lambda x: x.id, self.players))