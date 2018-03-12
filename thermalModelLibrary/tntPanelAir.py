# The soltion file for air thermal simulation
# this is empirical model for 2000mm height SWG Enclosures

import numpy as np


class airObject(object):
	"""docstring for airObject"""

	def __init__(self, nAir, hAir, T0):
		# grabbinng inputs here
		self.n = nAir
		self.h = hAir
		self.T0 = T0
		self.aCellsT = 'This is a 2000mm Empirical Air Model'

		self.update(T0)
		

	def update(self, T0):
		# doing some setum internal math
		self.Q = 0

	def resetQ(self):
		self.Q = 0

	def addQ(self, Y, Qin, phases=3):
		self.Q += Qin * phases

	def T(self, Y):
		# function returning the temperature at given height
		return self.T0 + ((0.0846 * self.Q + 6.25) * Y)/2000


	def solveT(self, srt=True):
		"""
		"""
		self.aCellsT = []
		for h in np.linspace(0, self.h, self.n):
			self.aCellsT.append(self.T(h))	
		
		

