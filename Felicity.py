from Player import Player
from Hand import Hand


class Felicity(Player):
    def __init__(self, name):
        self.name = "Felicity"
        self.hand = Hand()
        self.score = 0
        self.roundScore = 0
        self.tricksWon = []

    def play(self, option='play', c=None, auto=False):
        return self.hand.getRandomCard()
