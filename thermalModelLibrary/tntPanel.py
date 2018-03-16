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

class PCPanel:
	"""docstring for Panel"""

	def __init__(self, Nodes, In, Out, OutCurrent, Air=None, T0=20):

		self.Air = Air # Air object for this panel
		self.I = OutCurrent # The current
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
			node.inputs = temp_inputs
			node.outputs = temp_outputs


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

		self.In = self.nodes[in_idx]
		self.Out = self.nodes[out_idx]

		# this should finalize making copy for all nodes

