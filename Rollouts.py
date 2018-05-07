from Deck import Deck
from Card import Card, Suit, Rank
from Player import Player
from Trick import Trick
from random import randint
from Hand import Hand
from Dumb import Dumb
import copy

auto = True

totalTricks = 13
maxScore = 100
queen = 12
noSuit = 0
spades = 2
hearts = 3

class Rollouts:
	def __init__(self, state, felicity, node):

		self.roundNum = copy.deepcopy(state.roundNum)
		self.trickNum = copy.deepcopy(state.trickNum)
		self.dealer = copy.deepcopy(state.dealer)
		self.passes = copy.deepcopy(state.passes)
		self.currentTrick = copy.deepcopy(state.currentTrick)
		self.trickWinner = copy.deepcopy(state.trickWinner)
		self.heartsBroken = copy.deepcopy(state.heartsBroken)
		self.losingPlayer = copy.deepcopy(state.losingPlayer)
		self.deck = copy.deepcopy(state.deck)
		self.firstMove = True
		self.node = node

		# Make four simulation players (first is a copy of felicity)
		self.players = [Player("FelicityCopy"), Player("DumbCopy"), Player("DumberCopy"), Player("DumbestCopy")]

		#initialize the Felicity copy
		self.players[0].hand = copy.deepcopy(felicity.hand)
		self.players[0].score = copy.deepcopy(felicity.score)
		self.players[0].roundScore = copy.deepcopy(felicity.roundScore)
		self.players[0].tricksWon = copy.deepcopy(felicity.tricksWon)

		#initialize the 3 dumb copies
		self.players[1].hand = copy.deepcopy(state.players[1].hand)
		self.players[1].score = copy.deepcopy(state.players[1].score)
		self.players[1].roundScore = copy.deepcopy(state.players[1].roundScore)
		self.players[1].tricksWon = copy.deepcopy(state.players[1].tricksWon)

		self.players[2].hand = copy.deepcopy(state.players[2].hand)
		self.players[2].score = copy.deepcopy(state.players[2].score)
		self.players[2].roundScore = copy.deepcopy(state.players[2].roundScore)
		self.players[2].tricksWon = state.players[2].tricksWon

		self.players[3].hand = copy.deepcopy(state.players[3].hand)
		self.players[3].score = copy.deepcopy(state.players[3].score)
		self.players[3].roundScore = copy.deepcopy(state.players[3].roundScore)
		self.players[3].tricksWon = copy.deepcopy(state.players[3].tricksWon)


	def simulate(self, rollout):

        # simulate game until someone loses
		while (rollout.losingPlayer is None or rollout.losingPlayer.score < maxScore):
			while rollout.trickNum < totalTricks:
				if rollout.trickNum == 0:
					rollout.getTrickStarter(rollout)
				rollout.playSimTrick(rollout.trickWinner, rollout)
			rollout.roundSimScore(rollout)
			# tally scores
			rollout.handleSimScoring(rollout)

			# new round if no one has lost
			if (rollout.losingPlayer is None or rollout.losingPlayer.score < maxScore):
				rollout.newSimRound(rollout)

		#return the winner (used to determine node reward)
		return rollout.getSimWinner(rollout).name

	def handleSimScoring(self, rollout):
		p, highestScore = None, 0
		for player in rollout.players:
			if player.score > highestScore:
				p = player
				highestScore = player.score
			rollout.losingPlayer = p

	def newSimRound(self, rollout):
		rollout.deck = Deck()
		rollout.deck.shuffle()
		rollout.roundNum += 1
		rollout.trickNum = 0
		rollout.trickWinner = -1
		rollout.heartsBroken = False
		rollout.dealer = (self.dealer + 1) % len(self.players)
		rollout.dealCards(rollout)
		rollout.currentTrick = Trick()
		for p in rollout.players:
			p.discardTricks()

	def getTrickStarter(self, rollout):
		for i,p in enumerate(rollout.players):
			if p.hand.contains2ofclubs:
				rollout.trickWinner = i

	def dealCards(self, rollout):
		i = 0
		while(rollout.deck.size() > 0):
			rollout.players[i % len(rollout.players)].addCard(rollout.deck.deal())
			i += 1

	def evaluateTrick(self, rollout):
		rollout.trickWinner = rollout.currentTrick.winner
		p = rollout.players[rollout.trickWinner]
		p.trickWon(rollout.currentTrick)
		rollout.currentTrick = Trick()

	def roundSimScore(self, rollout):
		for p in rollout.players:
			p.score += p.roundScore


	def playSimTrick(self, start, rollout):
		shift = 0
		if rollout.trickNum == 0:
			startPlayer = rollout.players[start]
			# only try to play the 2 of clubs if it hasn't actually been played yet
			if not startPlayer.hand.containsCard(2, 0) is None:
				addCard = startPlayer.play(option="play", c='2c', state=rollout)
				startPlayer.removeCard(addCard)
				rollout.currentTrick.addCard(addCard, start)

			shift = 1 # alert game that first player has already played

		# have each player take their turn
		for i in range(start + shift, start + len(rollout.players)):
			curPlayerIndex = i % len(rollout.players)
			curPlayer = rollout.players[curPlayerIndex]

			# if this is the first move of the simulated game, we must play
			# the card associated with the node we're testing
			if (self.firstMove and curPlayerIndex == 0):
				addCard = self.node.card
				#print("FIRST MOVE playing " + str(addCard) + " and I am " + curPlayer.name)
				curPlayer.removeCard(addCard)
				self.firstMove = False
				rollout.currentTrick.addCard(addCard, curPlayerIndex)
			elif curPlayer.hand.size() > 0:
				addCard = None

				while addCard is None: # wait until a valid card is passed

					addCard = curPlayer.play(auto=auto, state=rollout) # change auto to False to play manually


					# the rules for what cards can be played
					# card set to None if it is found to be invalid
					if addCard is not None:

						# if it is not the first trick and no cards have been played,
						# set the first card played as the trick suit if it is not a heart
						# or if hearts have been broken
						if rollout.trickNum != 0 and rollout.currentTrick.cardsInTrick == 0:
							if addCard.suit == Suit(hearts) and not rollout.heartsBroken:
								# if player only has hearts but hearts have not been broken,
								# player can play hearts
								if not curPlayer.hasOnlyHearts():
									addCard = None
								else:
									rollout.currentTrick.setTrickSuit(addCard)
							else:
								rollout.currentTrick.setTrickSuit(addCard)

						# player tries to play off suit but has trick suit
						if addCard is not None and addCard.suit != rollout.currentTrick.suit:
							if curPlayer.hasSuit(rollout.currentTrick.suit):
								addCard = None
							elif addCard.suit == Suit(hearts):
								rollout.heartsBroken = True

						if rollout.trickNum == 0:
							if addCard is not None:
								if addCard.suit == Suit(hearts):
									rollout.heartsBroken = False
									addCard = None
								elif addCard.suit == Suit(spades) and addCard.rank == Rank(queen):
									addCard = None

						if addCard is not None and rollout.currentTrick.suit == Suit(noSuit):
							if addCard.suit == Suit(hearts) and not rollout.heartsBroken:
								addCard = None

						if addCard is not None:
							if addCard == Card(queen, spades):
								rollout.heartsBroken = True
							curPlayer.removeCard(addCard)

				rollout.currentTrick.addCard(addCard, curPlayerIndex)

		rollout.evaluateTrick(rollout)
		rollout.trickNum += 1

	def getSimWinner(self, rollout):
		minScore = 200 # impossibly high
		winner = rollout.players[0]
		for p in rollout.players:
			if p.score < minScore:
				winner = p
				minScore = p.score
		return winner
