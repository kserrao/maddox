from Player import Player
from Hand import Hand
import numpy as np

import random
import tensorflow as tf
tf.reset_default_graph()
n_s = 14
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

		s = np.zeros((2,n_s))[0:1]
		trump = state.currentTrick.suit.iden
		max_trump = 0
		for c in state.currentTrick.trick:
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
		s[0] = [trump, max_trump] + max_min_list
		a,allQ = self.Q.run([predict,Qout],feed_dict={inputs1:s})
		tmp = allQ[0][12]
		allQ[0][12] = -1
		for c in self.hand.spades:
			if c.rank.rank == 12:
				allQ[0][12] = tmp
		for i in range(4):
			if len(self.hand.hand[i]) == 0 or (len(self.hand.hand[trump]) > 0 and i != trump and trump != -1):
				allQ[0][3*i] = -1
				allQ[0][3*i + 1] = -1
				allQ[0][3*i + 2] = -1
				if i == 2:
					allQ[0][12] = -1

			# else:
			# 	allQ[0][3*i] += 1000
			# 	allQ[0][3*i + 1] += 1000
			# 	allQ[0][3*i + 2] += 1000
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
		# if (self.tricksplayed > 30000):
		suitlist = ["clubs", "diamonds", "spades", "hearts", "unset"]
		print("trump suit is " + suitlist[trump])
		print("highest of trump suit is " + str(max_trump))
		print("min/med/max of clubs:")
		print(max_min_list[:3])
		print("min/med/max of diamonds:")
		print(max_min_list[3:6])
		print("min/med/max of spades:")
		print(max_min_list[6:9])
		print("min/med/max of hearts:")
		print(max_min_list[9:])
		print("Q-values:")
		print(allQ)
		if a[0] == 12:
			print("Maddox plays the Queen of Spades")
		else:
			print("Maddox plays the " + str(max_min_list[a[0]]) + " of " + suitlist[a[0] // 3])
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
		self.lastAction = a[0]
		return self.hand.hand[suit][index]





	def eval(self, game):
		# print(game.losingPlayer)
		# print(game.losingPlayer.score)
		trick = game.currentTrick

		self.tricksplayed += 1
		r = 0
		if trick.winner == 1:
			# if self.roundScore == 26:
			# 	r = 26
			# else:
			r = -trick.points
		# if ((not game.losingPlayer is None) and game.losingPlayer.score >= 100):
		# 	if game.getWinner().name == "Maddox":
		# 		r = 100
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
		s[0] = [trump, max_trump] + max_min_list

		Q1 = self.Q.run(Qout,feed_dict={inputs1:s})
		# print(Q1)
		maxQ1 = np.max(Q1)
		targetQ = self.allQ
		targetQ[0,self.lastAction] = r + y*maxQ1
		# print(y*maxQ1)
		_,W1 = self.Q.run([updateModel,W],feed_dict={inputs1: s,nextQ:targetQ})

# with tf.Session() as sess:
#     sess.run(init)
#     for i in range(num_episodes):
#         #Reset environment and get first new observation
#         s = env.reset()
#         rAll = 0
#         d = False
#         j = 0
#         #The Q-Network
#         while j < 99:
#             j+=1
#             #Choose an action by greedily (with e chance of random action) from the Q-network
#             a,allQ = sess.run([predict,Qout],feed_dict={inputs1:np.identity(16)[s:s+1]})
#             if np.random.rand(1) < e:
#                 a[0] = env.action_space.sample()
#             #Get new state and reward from environment
#             s1,r,d,_ = env.step(a[0])
#             #Obtain the Q' values by feeding the new state through our network
#             Q1 = sess.run(Qout,feed_dict={inputs1:np.identity(16)[s1:s1+1]})
#             #Obtain maxQ' and set our target value for chosen action.
#             maxQ1 = np.max(Q1)
#             targetQ = allQ
#             targetQ[0,a[0]] = r + y*maxQ1
#             #Train our network using target and predicted Q values
#             _,W1 = sess.run([updateModel,W],feed_dict={inputs1:np.identity(16)[s:s+1],nextQ:targetQ})
#             rAll += r
#             s = s1
#             if d == True:
#                 #Reduce chance of random action as we train the model.
#                 e = 1./((i/50) + 10)
#                 break
#         jList.append(j)
#         rList.append(rAll)
