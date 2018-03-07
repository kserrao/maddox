from Player import Player
from Hand import Hand


class Maddox(Player):
    def __init__(self, name):
        self.name = "Maddox"
        self.hand = Hand()
        self.score = 0
        self.roundScore = 0
        self.tricksWon = []

    def play(self, option='play', c=None, auto=False):
        if not c is None:
            return self.hand.playCard(c)
        return self.hand.getRandomCard()
