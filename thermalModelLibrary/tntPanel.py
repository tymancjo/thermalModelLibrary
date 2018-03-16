# The Panel object library fro tnt thermal solution system

'''
The idea of Panel for the thermal module.

1. Panel contain:
	1. Input - the incomer feed or feeder out 
	2. Connections - interface points to other systems
	3. Internal Path - the structure of the panel (electrical and thermal)

Maybe it need to have a defined one and one only set of nodes?

interfaces:
MBB: TopLeft TopRight MidLeft MidRight
inputs: input or output from feeders/incomers

how the solver may handle this stuff ?

solver -> loop(Panels-> loop elements)


'''

# self made library for Air model
from thermalModelLibrary import tntAir as tntA

class PCPanel:
	"""docstring for Panel"""

	def __init__(self, Nodes, In, Out, OutCurrent, Air=None, T0=20):

		self.nodes = Nodes # List of nodes for this panel
		self.Air = Air # Air object for this panel
		self.I = OutCurrent # The current
		self.T0 = T0

		# Need to define some interfaces
		self.In = In
		self.Out = Out 

		# Some check and initial preparation
		self.setup()

	def setup(self):
		
		# Checking if Air object is defined
		if not isinstance(self.Air, tntA.airObject):
			self.Air = tntA.airObject(100, 2200, self.T0) # Creating Air 2.2m 20C


