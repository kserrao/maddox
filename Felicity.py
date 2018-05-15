from Player import Player
from Hand import Hand
from Node import Node
from Rollouts import Rollouts
from random import randint
import math

numIterations = 25
expansionDepth = 1
clubs = 0
diamonds = 1
spades = 2
hearts = 3
suits = ["c", "d", "s", "h"]

class Felicity(Player):
	def __init__(self, name):
		self.name = "Felicity"
		self.hand = Hand()
		self.score = 0
		self.roundScore = 0
		self.tricksWon = []

	def play(self, option='play', c=None, auto=False, state=None):
		if not c is None:
			return self.hand.playCard(c)

		# if we are playing, not passing, be strategic about card choice
		if not option is 'pass':
			# if we have the 2 of clubs, we must play it
			if self.hand.contains2ofclubs:
				return self.hand.clubs[0]
			# if we only have one card left, play that card
			# inefficiently written but the Hand object is annoying
			elif self.hand.size() == 1:
				if len(self.hand.clubs) > 0:
					return self.hand.clubs[0]
				elif len(self.hand.diamonds) > 0:
					return self.hand.diamonds[0]
				elif len(self.hand.spades) > 0:
					return self.hand.spades[0]
				elif len(self.hand.hearts) > 0:
					return self.hand.hearts[0]
			# otherwise, use the MCTS algorithm to pick a card
			else:
				return self.runMCTS(state)

		# if we are passing, just return a random card
		else:
			return self.hand.getRandomCard()

	def runMCTS(self, state):
		handArray = self.arrangeHand()

		for i in range(0, numIterations):
			print("size of Felicity's hand is: " + str(self.hand.size()))
			rootNode = Node(self.hand, state)
			print("RUNNING ITERATION " + str(i))
			expanded = self.treePolicy(rootNode, handArray)
			rollout = Rollouts(expanded.state, self, expanded)
			# if Felicity won the simulated game, reward the selected node
			if rollout.simulate(rollout) == "FelicityCopy":
				self.backPropogate(expanded, 1.0)
			else:
				self.backPropogate(expanded, 0.0)

		bestIndex = self.bestRewardChild(rootNode)
		bestChild = rootNode.children[bestIndex]
		card = bestChild.card
		return card

	def arrangeHand(self):
		handArray = []
		for suit in self.hand.hand:
			for card in suit:
				handArray.append(card)
		return handArray

	def treePolicy(self, rootNode, handArray):
		thisNode = rootNode
		print("the size of my NODE hand is now " + str(thisNode.hand.size()))
		while (thisNode.hand.size() > 0 and thisNode.depth < expansionDepth):
			print("entering the while loop w depth of " + str(thisNode.depth))
			trump = thisNode.state.currentTrick.suit
			size = thisNode.hand.size()
			firstIndex = 0
			lastIndex = -1

			# if this is the first move
			if trump.iden == -1:
				# if hearts has been broken or we only have hearts, can play anything
				if (thisNode.state.heartsBroken or thisNode.hand.hasOnlyHearts):
					firstIndex = 0
					lastIndex = size
				# if hearts has not been broken and we have non-hearts, restrict choice
				else:
					# if we have no hearts, we can play anything
					if len(thisNode.hand.hearts) < 1:
						firstIndex = 0
						lastIndex = size
					# otherwise, cut out the Hearts
					else:
						firstIndex = 0
						lastIndex = size - len(thisNode.hand.hearts)

			# if we don't have any cards of the trump suit, can play anything
			elif len(thisNode.hand.hand[trump.iden]) < 1:
					firstIndex = 0
					lastIndex = size

			# otherwise, we must play a card of the trump suit
			else:
				# trump suit is clubs
				if trump.iden == 0:
					firstIndex = 0
					lastIndex = firstIndex + len(thisNode.hand.clubs)
				# trump suit is diamonds
				elif trump.iden == 1:
					firstIndex = len(thisNode.hand.clubs)
					lastIndex = firstIndex + len(thisNode.hand.diamonds)
				# trump suit is spades
				elif trump.iden == 2:
					firstIndex = len(thisNode.hand.clubs) + len(thisNode.hand.diamonds)
					lastIndex = firstIndex + len(thisNode.hand.spades)
				# trump suit is hearts
				elif trump.iden == 3:
					firstIndex = size - len(thisNode.hand.hearts)
					lastIndex = size
				else:
					print("TRUMP SUIT ERROR: " + str(trump.iden))

			# visit all children (valid moves) at least once
			indexRange = lastIndex - firstIndex
			if len(thisNode.children) < indexRange:
				for i in range(0, indexRange):
					if len(thisNode.children) < (i + 1):
						return self.expandTree(thisNode, handArray, i, firstIndex)

			# once we've visited all valid children, visit only the best ones
			r = randint(0,1)
			if r:
				thisNode = self.greedyChild(rootNode)
				print("GREEDY choice is " + str(thisNode.card))
			else:
				thisNode = self.bestUCTChild(rootNode, 0.1)
				print("UCT choice is " + str(thisNode.card))
		return thisNode

    # uses a greedy heuristic to select which child to expand
	def greedyChild(self, rootNode):
		trump = rootNode.state.currentTrick.suit
		# if this is the first move, return our lowest card
		if trump.iden == -1:
			return self.lowestCard(rootNode)
		# if it's not the first move
		else:
			# if we don't have the trump suit
			if len(rootNode.hand.hand[trump.iden]) < 1:
				# if we can play the Queen of Spades, play it
				queen = rootNode.hand.containsCard(12, 2)
				if not queen is None:
					for i in range(0, len(rootNode.children)):
						if rootNode.children[i].card == queen:
							return rootNode.children[i]
				# otherwise, if we have hearts, play our largest hearts card
				elif len(rootNode.hand.hearts) > 0:
					c = self.highestHeart(rootNode)
					for i in range(0, len(rootNode.children)):
						if rootNode.children[i].card == c:
							return rootNode.children[i]
				# otherwise, pick our largest card
				else:
					return self.highestCard(rootNode)
			# if we do have the trump suit
			else:
				# if we are not the last player
				if rootNode.state.currentTrick.cardsInTrick < 3:
					return self.lowestCard(rootNode)
				else:
					return self.highestCard(rootNode)

	# uses the UCT function to select the statistically best child to visit
	def bestUCTChild(self, rootNode, weight):
		bestIndex = 0
		bestVal = -999999 #impossibly low
		totalVisits = rootNode.visits
		for i in range(0, len(rootNode.children)):
			if not rootNode.children[i] is None:
				child = rootNode.children[i]
				childVisits = child.visits
				reward = child.getReward()
				valUCT = reward + weight * math.sqrt((2*math.log(totalVisits))/childVisits)
				if valUCT > bestVal:
					bestVal = valUCT
					bestIndex = i
		return rootNode.children[bestIndex]

	# create a child for the root node corresponding to a valid move(card to play)
	def expandTree(self, rootNode, handArray, i, firstIndex):
		rootNode.createChild(rootNode.hand, rootNode.state)
		rootNode.children[i].card = handArray[firstIndex + i]
		print("NEW choice is" + str(rootNode.children[i].card))
		rootNode.children[i].hand.removeCard(rootNode.children[i].card)
		return rootNode.children[i]

	# propogate the simulated reward back up the tree
	def backPropogate(self, baseNode, reward):
		node = baseNode
		while not node is None:
			node.updateCounter(reward)
			node = node.parent

	# pick the child of the root node with the highest win/visit ratio
	def bestRewardChild(self, rootNode):
		highestReward = -999999; #impossibly low
		bestChildIndex = 0;
		for i in range(0, len(rootNode.children)):
			if not rootNode.children[i] is None:
				reward = rootNode.children[i].getReward()
				if reward > highestReward:
					highestReward = reward
					bestChildIndex = i
		return bestChildIndex

	def highestCard(self, rootNode):
		high = rootNode.children[0]
		for i in range(1, len(rootNode.children)):
			if rootNode.children[i].card.rank.rank > high.card.rank.rank:
				high = rootNode.children[i]
		return high

	# GREEDY ALG: returns the node corresponding to our lowest legal card
	def lowestCard(self, rootNode):
		low = rootNode.children[0]
		for i in range(1, len(rootNode.children)):
			if rootNode.children[i].card.rank.rank < low.card.rank.rank:
				low = rootNode.children[i]
		return low

	# GREEDY ALG: returns the node corresponding to the lowest legal card of a given suit
	def lowestInSuit(self, rootNode, suit):
		return rootNode.hand.hand[suit.iden][0]

	# GREEDY ALG: returns the node corresponding to the highest legal card of a given suit
	def highestHeart(self, rootNode):
		lastIndex = len(rootNode.hand.hearts) - 1
		return rootNode.hand.hearts[lastIndex]
