from Player import Player
from Hand import Hand

class Dumb(Player):
	def __init__(self, name):
		self.name = name
		self.hand = Hand()
		self.score = 0
		self.roundScore = 0
		self.tricksWon = []



		def play(self, option='play', c=None, auto=False, state=None):
			print(state.currentTrick.suit.iden)
			if not c is None:
				return self.hand.playCard(c)
			elif auto:
				if state.currentTrick.cardsInTrick == 0:
					return self.lowestCard()
				else:
					suit = state.currentTrick.suit
					if self.hasSuit(suit):
						return self.lowestInSuit(suit)
					else:
						return self.lowestCard()
			else:
				card = self.getInput(option)
			return card


	def lowestCard(self):
		low = Card(20, 0)
		for suit in reversed(self.hand.hand):
			for card in suit:
				if card.rank.rank < low.rank.rank:
					low = card
		return low

	def lowestInSuit(self, suit):
		return self.hand.hand[suit.iden][0]
