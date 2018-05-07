import copy

class Node():
	def __init__(self, hand, state, parent=None):
		self.hand = copy.deepcopy(hand)
		self.visits = 1.0
		self.wins = 0.0
		self.children = []
		self.parent = parent
		self.state = state
		if (self.parent != None):
			self.depth = self.parent.depth + 1
		else:
			self.depth = 0
		if (self.parent is None):
			self.card = None
		else:
			self.card = parent.card

	def createChild(self, hand, child_state):
		child = Node(hand, child_state, self)
		self.children.append(child)

    #reward = 1 for win and 0 for false
	def updateCounter(self, reward):
		self.wins += reward
		self.visits += 1.0

	def getReward(self):
		return self.wins/self.visits
