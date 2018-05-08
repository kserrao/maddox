from Player import Player
from Hand import Hand
import numpy as np

import random
import tensorflow as tf
tf.reset_default_graph()
n_s = 16
n_a = 13
#
#These lines establish the feed-forward part of the network used to choose actions
inputs1 = tf.placeholder(shape=[1,n_s],dtype=tf.float32)
W = tf.Variable(tf.random_uniform([n_s,n_a],0,0.01))
Qout = tf.matmul(inputs1,W)
predict = tf.argmax(Qout,1)

#Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
nextQ = tf.placeholder(shape=[1,n_a],dtype=tf.float32)
loss = tf.reduce_sum(tf.square(nextQ - Qout))
trainer = tf.train.GradientDescentOptimizer(learning_rate=0.0001)
updateModel = trainer.minimize(loss)

init = tf.initialize_all_variables()
y = 0.99
e = 0.1


class Maddox(Player):
	def __init__(self, name):
		self.name = "Maddox"
		self.hand = Hand()
		self.score = 0
		self.roundScore = 0
		self.tricksWon = []
		self.Q = tf.Session()
		self.allQ = None
		self.lastAction = None
		self.Q.run(init)
		self.tricksplayed = 0

	#clubs, diamonds, spades, hearts

	def play(self, option='play', c=None, auto=False, state=None):
		if not c is None:
		    return self.hand.playCard(c)
		# initialize
		s = np.zeros((2,n_s))[0:1]

		# set trump
		trump = state.currentTrick.suit.iden
		# set max of trump
		max_trump = 0
		for c in state.currentTrick.trick:
			if (not isinstance(c, int)):
				if (c.suit.iden == trump):
					max_trump = max(c.rank.rank, max_trump)

		# set min,med,max of each suit in hand
		max_min_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		for i in range(4):
			if len(self.hand.hand[i]) > 0:
				l = len(self.hand.hand[i])
				max_min_list[3*i] = self.hand.hand[i][0].rank.rank
				max_min_list[3*i + 1] = self.hand.hand[i][l//2].rank.rank
				max_min_list[3*i + 2] = self.hand.hand[i][-1].rank.rank

		# concat
		s[0] = [trump, max_trump] + max_min_list + [state.heartsBroken,
		 											state.currentTrick.cardsInTrick]
		# do tf stuff
		a,allQ = self.Q.run([predict,Qout],feed_dict={inputs1:s})

		# change Q-val to -1 if cant play Qspades
		tmp = allQ[0][12]
		allQ[0][12] = -1
		for c in self.hand.spades:
			if c.rank.rank == 12:
				allQ[0][12] = tmp

		# change Q-val to -1 if cant play from a suit
		for i in range(4):
			if len(self.hand.hand[i]) == 0 or (len(self.hand.hand[trump]) > 0 and i != trump and trump != -1):
				allQ[0][3*i] = -1
				allQ[0][3*i + 1] = -1
				allQ[0][3*i + 2] = -1
				# Can't play QSpades
				if i == 2:
					allQ[0][12] = -1
				# Hearts are not broken
				if i == 3 and not s[0][14]:
					allQ[0][3*i] = -1
					allQ[0][3*i + 1] = -1
					allQ[0][3*i + 2] = -1

		# select chosen card
		index = 0
		suit = 0
		for i in range(len(allQ[0])):
			if allQ[0][i] > allQ[0][a[0]]:
				a[0] = i
		self.allQ = allQ
		if (a[0] < 12):
			suit = a[0] // 3
			index = 0
			if a[0] % 3 == 1:
				index = len(self.hand.hand[suit]) // 2
			elif a[0] % 3 == 0:
				index = 0
			else:
				index = -1
		else:
			suit = 2
			for i in range(len(self.hand.spades)):
				if self.hand.spades[i].rank.rank == 12:
					index = i

		# # debuggers
		# print(trump)
		# print(max_trump)
		# print(a[0])
		# print(max_min_list)
		# print(allQ)

		# noise/fixing problems that probably shouldn't even happen
		rep = False
		while np.random.rand(1) < e or len(self.hand.hand[suit]) == 0 or rep:
			a[0] = random.randint(0,n_a - 1)
			if rep:
				a[0] = random.randint(0, n_a - 2)
			if (a[0] < 12):
				suit = a[0] // 3
				index = 0
				if a[0] % 3 == 1:
					index = len(self.hand.hand[suit]) // 2
				elif a[0] % 3 == 0:
					index = 0
				else:
					index = -1
				rep = False
			else:
				rep = True
				suit = 2
				for i in range(len(self.hand.spades)):
					if self.hand.spades[i].rank.rank == 12:
						index = i
						rep = False
		# store action for later
		self.lastAction = a[0]
		# play from hand!
		return self.hand.hand[suit][index]





	def eval(self, state):
		trick = state.currentTrick

		self.tricksplayed += 1
		r = 0
		if state.players[trick.winner].name == "Maddox":
			# if self.roundScore == 26:
			# 	r = 26
			# else:
			r = -trick.points
		# if ((not state.losingPlayer is None) and state.losingPlayer.score >= 100):
		# 	if state.getWinner().name == "Maddox":
		# 		r = 1
		s = np.zeros((2,n_s))[0:1]
		trump = trick.suit.iden
		max_trump = 0
		for c in trick.trick:
			if (not isinstance(c, int)):
				if (c.suit.iden == trump):
					max_trump = max(c.rank.rank, max_trump)
		max_min_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		for i in range(4):
			if len(self.hand.hand[i]) > 0:
				l = len(self.hand.hand[i])
				max_min_list[3*i] = self.hand.hand[i][0].rank.rank
				max_min_list[3*i + 1] = self.hand.hand[i][l//2].rank.rank
				max_min_list[3*i + 2] = self.hand.hand[i][-1].rank.rank

		s[0] = [trump, max_trump] + max_min_list + [state.heartsBroken,
		 											state.currentTrick.cardsInTrick]

		Q1 = self.Q.run(Qout,feed_dict={inputs1:s})
		# print(Q1)
		maxQ1 = np.max(Q1)
		targetQ = self.allQ
		targetQ[0,self.lastAction] = r + y*maxQ1
		# print(y*maxQ1)
		_,W1 = self.Q.run([updateModel,W],feed_dict={inputs1: s,nextQ:targetQ})
