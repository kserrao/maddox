from Player import Player
from Hand import Hand
import numpy as np

import random
import tensorflow as tf
tf.reset_default_graph()
#
#These lines establish the feed-forward part of the network used to choose actions
inputs1 = tf.placeholder(shape=[1,52],dtype=tf.float32)
W = tf.Variable(tf.random_uniform([52,13],0,0.01))
Qout = tf.matmul(inputs1,W)
predict = tf.argmax(Qout,1)

#Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
nextQ = tf.placeholder(shape=[1,13],dtype=tf.float32)
loss = tf.reduce_sum(tf.square(nextQ - Qout))
trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
updateModel = trainer.minimize(loss)

init = tf.initialize_all_variables()
y = .99
e = 0.1


class Maddox(Player):
	def __init__(self, name):
		self.name = "Maddox"
		self.hand = Hand()
		self.score = 0
		self.roundScore = 0
		self.tricksWon = []
		self.Q = tf.Session()
		self.Q.run(init)
		self.allQ = None
		self.lastAction = None

	#clubs, diamonds, spades, hearts
	def play(self, option='play', c=None, auto=False, state=None):
		realHand = self.hand.hand[0] + self.hand.hand[1] + self.hand.hand[2] + self.hand.hand[3]
		if not c is None:
		    return self.hand.playCard(c)
		s = np.zeros((2,52))[0:1]
		for c in self.hand.clubs:
			s[0][(c.rank.rank - 2)] = 1
		for c in self.hand.diamonds:
			s[0][(c.rank.rank - 2) * 2] = 1
		for c in self.hand.spades:
			s[0][(c.rank.rank - 2) * 3] = 1
		for c in self.hand.hearts:
			s[0][(c.rank.rank - 2) * 4] = 1
		a,allQ = self.Q.run([predict,Qout],feed_dict={inputs1:s})
		self.allQ = allQ
		if np.random.rand(1) < e or a[0] > len(realHand) - 1:
			a[0] = random.randint(0,len(realHand) - 1)
		# print("choice is: " + str(a[0]))
		# print("hand has " + str(len(realHand)) + " cards left")
		self.lastAction = a[0]
		return realHand[a[0]]


	def trickWon(self, trick):
		self.roundScore += trick.points
		r = -self.score
		s = np.zeros((2,52))[0:1]
		for c in self.hand.clubs:
			s[0][(c.rank.rank - 2)] = 1
		for c in self.hand.diamonds:
			s[0][(c.rank.rank - 2) * 2] = 1
		for c in self.hand.spades:
			s[0][(c.rank.rank - 2) * 3] = 1
		for c in self.hand.hearts:
			s[0][(c.rank.rank - 2) * 4] = 1
		Q1 = self.Q.run(Qout,feed_dict={inputs1:s})
		maxQ1 = np.max(Q1)
		targetQ = self.allQ
		targetQ[0,self.lastAction] = r + y*maxQ1


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
