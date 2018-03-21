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

## Idea:
If panel will clone the nodes this will allow to reuse defined elements


'''

# to be able to make the deep copy of each object
import copy

# self made library for Air model
from thermalModelLibrary import tntAir as tntA
from thermalModelLibrary.tntObjects import * 

class Panel:
	"""docstring for Panel"""

	def __init__(self, Nodes, In, Out, OutCurrent, Air=None, T0=20):

		self.Air = Air # Air object for this panel
		self.I = OutCurrent # The current
		self.Iin = 0
		self.Iout = 0
		self.T0 = T0

		# Need to define some interfaces
		self.In = In
		self.Out = Out 

		self.cloneNodes(Nodes) # List of nodes for this panel
		
		# Some check and initial preparation
		self.setup()

	def setup(self):
		
		# Checking if Air object is defined
		if not isinstance(self.Air, tntA.airObject):
			self.Air = tntA.airObject(100, 2200, self.T0) # Creating Air 2.2m 20C


	def cloneNodes(self, Nds):
		# Clearing the nodes list
		self.nodes=[]

		# cloning the entire list
		for node in Nds:
			# before we deepcopy we need to clean internal 
			# node inputs and outputs 
			# because otherwise it will clone those objects
			temp_inputs = node.inputs
			temp_outputs = node.outputs

			node.inputs = []
			node.outputs = []

			clone = copy.deepcopy(node)
			
			clone.inputs = temp_inputs
			clone.outputs = temp_outputs
			
			self.nodes.append(clone)
			
			# fixing the original node
			node.inputs = copy.copy(temp_inputs)
			node.outputs = copy.copy(temp_outputs)


		# this leaves the input and outputs of the nodes
		# still refer to the non clone nodes
		# fixing this universally is not that easy 
		# my attempt is below (other solution is to make connection after cloning)

		for idx, node in enumerate(self.nodes):
			# figuring out the inputs
			temp_inputs = []
			if len(node.inputs) > 0:
				for i,input_node in enumerate(node.inputs):
					# input_node is the original one
					# we need to figure out which clone to use
					# so we find the original one index
					oryginal_idx = Nds.index(input_node)
					# and we replace this node with clone from the same index
					# node.inputs[i] = self.nodes[oryginal_idx] 
					temp_inputs.append(self.nodes[oryginal_idx])
				node.inputs = temp_inputs

			# figuring out outputs the same way
			temp_outputs = []
			if len(node.outputs) > 0:
				for i,output_node in enumerate(node.outputs):
					oryginal_idx = Nds.index(output_node)
					# and we replace this node with clone from the same index
					# node.outputs[i] = self.nodes[oryginal_idx]
					temp_outputs.append(self.nodes[oryginal_idx])
				node.outputs = temp_outputs

		# Finally we just need to repoint the In and Out
		# to the adequate cloned nodes
		in_idx = Nds.index(self.In)
		out_idx = Nds.index(self.Out)

		self.In = None
		self.Out = None

		self.In = self.nodes[in_idx]
		self.Out = self.nodes[out_idx]

		# this should finalize making copy for all nodes

class PCPanel(object):
	"""docstring for PCPanel"""
	def __init__(self, MBB, VBB, Load=False, Air=None, T0=20, AirSort=1):
		# super(Panel, self).__init__() # I don't know yet how to use this
		self.T0 = T0
		self.Air = Air
		self.AirSort = AirSort
		self.I = Load
		self.Iin = 0
		self.Iout = 0

		self.setup()

		# MBB - list of nodes that describe MBB
		# VBB - list of nodes that describe VBB

		# Making independent clone of MBB nodes
		# and making internal links
		self.MBB = self.prepareNodes(self.cloneNodes(MBB))

		# the same for VBB
		if len(VBB) > 0:
			self.VBB = self.prepareNodes(self.cloneNodes(VBB))
		else:
			self.VBB = VBB

		# Setting up the interface points
		self.In = self.MBB[0]
		self.Out = self.MBB[-1]

		# finding middle of MBB list to attach VBB
		half = int(len(MBB)/2) - 1
		

		# joining the MBB and VBB
		if len(VBB) > 0:
			self.MBB[half].outputs.append(self.VBB[0])
			# self.VBB[0].inputs.append(self.MBB[half])
			# Just a try it should be generally the same thing
			self.VBB[0].inputs = [self.MBB[half]]

		# making two MBB list for easier manage
		self.MBB0 = self.MBB[:half+1]
		self.MBB1 = self.MBB[half+1:]

		print(len(self.MBB),len(self.MBB0), len(self.MBB1))

		# Preparing final internal list of nodes
		# To be compatible with solver

		self.nodes = []
		self.nodes.extend(self.MBB0)
		if len(VBB) > 0:
			self.nodes.extend(self.VBB)
		self.nodes.extend(self.MBB1)


	def setCurrent(self, current):
		for node in self.nodes:
			node.current = current

	def set3I(self,Iin,Iout,Ifeeder):
		# Fill currents info in each branch nodes

		for node in self.MBB0:
			node.current = Iin
		
		for node in self.MBB1:
			node.current = Iout

		if len(self.VBB) > 0:
			for node in self.VBB:
				node.current = Ifeeder


	def setup(self):
		
		# Checking if Air object is defined
		if not isinstance(self.Air, tntA.airObject):
			self.Air = tntA.airObject(100, 2200, self.T0) # Creating Air 2.2m 20C	

	def cloneNodes(self, Nodes):
		output = []

		for node in Nodes:
			temp_inputs = node.inputs
			temp_outputs = node.outputs

			node.inputs = []
			node.outputs = []

			output.append(copy.deepcopy(node))

			node.inputs = temp_inputs 
			node.outputs = temp_outputs
			 
			temp_inputs = None
			temp_outputs = None
		
		return output

	def prepareNodes(self, Elements):
		# This procedure update the Elements list 
		# to introduce each element neigbours into propper internal lists
	
		for index, element in enumerate(Elements):
			
			if index > 0:
				element.inputs.append(Elements[index-1])
			if index < len(Elements)-1:
				element.outputs.append(Elements[index+1]) 

		return Elements
		


class AnyPanel(object):
	"""docstring for PCPanel"""
	def __init__(self, Nodes, In, Out, Load=False, Air=None, T0=35, AirSort=1):
		# super(Panel, self).__init__() # I don't know yet how to use this
		self.T0 = T0
		self.Air = Air
		self.AirSort = AirSort
		self.I = Load
		self.Iin = 0
		self.Iout = 0

		self.setup()

		# Setting up the interface points
		self.In = In
		self.Out = Out

		# Preparing final internal list of nodes
		# To be compatible with solver
		
		self.nodes = Nodes


	def setup(self):
		
		# Checking if Air object is defined
		if not isinstance(self.Air, tntA.airObject):
			self.Air = tntA.airObject(30, 2200, self.T0) # Creating Air 2.2m 20C	

	def cloneNodes(self, Nodes):
		output = []

		for node in Nodes:
			temp_inputs = node.inputs
			temp_outputs = node.outputs

			node.inputs = []
			node.outputs = []

			output.append(copy.deepcopy(node))

			node.inputs = temp_inputs 
			node.outputs = temp_outputs
			 
			temp_inputs = None
			temp_outputs = None
		
		return output

	def prepareNodes(self, Elements):
		# This procedure update the Elements list 
		# to introduce each element neigbours into propper internal lists
	
		for index, element in enumerate(Elements):
			
			if index > 0:
				element.inputs.append(Elements[index-1])
			if index < len(Elements)-1:
				element.outputs.append(Elements[index+1]) 

		return Elements


# just some procedures
def prepareNodes(Elements):
		# This procedure update the Elements list 
		# to introduce each element neigbours into propper internal lists
	
		for index, element in enumerate(Elements):
			
			if index > 0:
				element.inputs.append(Elements[index-1])
			if index < len(Elements)-1:
				element.outputs.append(Elements[index+1]) 

def setCurrent(Elements, I):
	
	for element in Elements:
		element.current = I