from Hand import Hand

class Player:
	def __init__(self, name):
			self.name = name
			self.hand = Hand()
			self.score = 0
			self.roundScore = 0
			self.tricksWon = []

	def addCard(self, card):
		self.hand.addCard(card)


	def getInput(self, option):
		card = None
		while card is None:
			card = raw_input(self.name + ", select a card to " + option + ": ")
		return card

	def play(self, option='play', c=None, auto=False):
		if not c is None:
			return self.hand.playCard(c)
		elif auto:
			card = self.hand.getRandomCard()
		else:
			card = self.getInput(option)
		if not auto:
			card = self.hand.playCard(card)
		return card


	def trickWon(self, trick):
		self.roundScore += trick.points

	def add26(self):
		self.score += 26

	def subtract26(self):
		self.score -= 26

	def hasSuit(self, suit):
		return len(self.hand.hand[suit.iden]) > 0

	def removeCard(self, card):
		self.hand.removeCard(card)

	def discardTricks(self):
		self.tricksWon = []

	def hasOnlyHearts(self):
		return self.hand.hasOnlyHearts()
