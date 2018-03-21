# The soltion file for air thermal simulation

import numpy as np

"""
The main idea is to create a model of air to make it simulate the temperatre rise vs. the height.

Solution finding steps:
1. make procrdure to map element Y to a best air cell element
2. make air cell elements heat transfer calulation - static model
3. make the model dynamic - air is moving

ad.1.
	lets assume fixed number of air elements in height
		nAir
	lest assume some height
		hAir
	Lets divide the height to air cells
	lets figure out sizes and position of eaxh air cell
	lest make a map function input: any Y -> output: air cell 
ad.2.
	lets prepare the Q object vector of lenghth as air cells number
	lets apply this vector as input element
	lest calculate the heat distribution base on the thermal G
"""
class airObject(object):
	"""docstring for airObject"""

	def __init__(self, nAir, hAir, T0):
		# grabbinng inputs here
		self.n = nAir
		self.h = hAir
		self.T0 = T0

		self.update(T0)
		self.setG()

	def update(self, T0):
		# doing some setum internal math
		self.aCellH = self.h / self.n
		self.aCellsT = np.array([T0 for i in range(self.n)])
		self.Q = np.zeros(self.n)

	def resetQ(self):
		self.Q *= 0

	def addQ(self, Y, Qin, phases=3):
		self.Q[self.airCell(Y)] += Qin * phases

	def airCell(self, Y):
		# pointing any Y to propper air cell number
		n = int(Y // self.aCellH)
		# return (self.n - min(n, self.n)) - 1 # need to really rethink this
		return min(n, self.n-1) # this oryginal logical one

	def T(self, Y):
		# function returning the temperature at given height
		return self.aCellsT[self.airCell(Y)]

	def setG(self, Gup=5, Gdwn=0, Gout=2):
	# def setG(self, Gup=0, Gdwn=0, Gout=1):
		# Gup is thermal cond to the top
		# Gdwn is thermal cond down
		# Gout is thermal cond out of system
		
		# generating the G matrix
		self.G = np.zeros((self.n, self.n)) # preparing the G empty matrix
		
		for i in range(self.n):
			for j in range(self.n):
				# lets treat j as row i as col
				if i == j: # the N case
					self.G[i][j] = +Gup +Gdwn +Gout
				elif i == j-1: # the N-1 case
					self.G[i][j] = -Gdwn
				elif i == j+1: # the N+1 case
					self.G[i][j] = -Gup

		self.invG = np.linalg.inv(self.G)



	def solveT(self, srt=True):
		"""
		this is about update internal T solve
		Q is the input power vector or lenght n
		
		"""
		dT = np.matmul(self.invG, self.Q)
		self.aCellsT = dT + self.T0
		if srt:
			self.aCellsT = np.sort(self.aCellsT)
		
		

