# Solver procedures for thermal Modeling Library

"""
Plan for solver actions

Start time = 0
setTImeStep = 1 [s]

we get the array of thermalElement objects
elements =[]

plan of algorithm:
	loop over time
		loop over elements
			figuring out Energy in element
			- solve elements for DT from internal heat (based on prev T)
			- solve for heat conduction from prev and next (based on prev T)
			- solve for heat transmitted via convection (based on prev T)
			- solve for heat transmitted by radiation (based on previous T)

			Having the total heat in element -> calculate energy -> calculate DT
			calculate Temperature = Previous temp + DT
"""
# Importing external library
import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
import matplotlib.patches as patches
import matplotlib.lines as mlines
from matplotlib.collections import PatchCollection
import matplotlib as mpl
import numpy as np
import math

# to be able to make the deep copy of each object
import copy

# self made library for Air model
from thermalModelLibrary import tntAir as tntA
from thermalModelLibrary import tntPanel as tntP


def PanelSolver(Panels, T0, EndTime, iniTimeStep = 1, tempStepAccuracy = 0.1):
	# Preparing list to capture all elements
	Elements = []

	# first we need to prepare our system to be solved as separate panels
	# We will go over panels we got and make required things.

	# to be able to do anything further need to set the XY positions for all elements in all panels to do so we need to make sure we will set properly the between panels connections.


	for idx,this_panel in enumerate(Panels):

		# This should take care of binding elements between panels
		if idx > 0: # if this is not the first one
			prev_panel = Panels[idx-1]
			# Current panel input takes prev output
			this_panel.In.inputs.append(prev_panel.Out) 
			# previous output takes this input
			prev_panel.Out.outputs.append(this_panel.In)

		if idx < len(Panels)-1: # if this is not the last one
			next_panel = Panels[idx+1]
			# Current panel output takes next input
			this_panel.Out.outputs.append(next_panel.In) 
			# Next panel input takes this output
			next_panel.In.inputs.append(this_panel.Out)
		
		Elements.extend(this_panel.nodes)

		# debug print
		# print('In:',Elements.index(this_panel.In),' Out:',Elements.index(this_panel.Out))

	
	# for x,this_panel in enumerate(Panels):
	# 	if len(this_panel.In.inputs) > 0:
	# 		print(x,' InIn:',Elements.index(this_panel.In.inputs[-1]))
		
	# 	if len(this_panel.Out.outputs) > 0:
	# 		print(x,' OutOut:',Elements.index(this_panel.Out.outputs[-1]))

	# Having the final list of elements we calculate the total XY
	# Filling elements positions
	nodePosXY(Elements)

	for this_panel in Panels:
			# Now we can solve Air for each Panel preparing for thermal solving
			for node in this_panel.nodes: # For each node in this panel
				# Collecting all input power to Air model 
				this_panel.Air.addQ(node.y, node.Power(node.current, T0))

				# And we make a reference in each node to the panel 
				# air model
				node.air = this_panel.Air

			# Having all the input for this panel Air we can solve it
			this_panel.Air.solveT(1) # Solving with sorting


	# Preparing the starting temperatures 
	elementsHaveT = True
	for element in Elements:
		if not element.T:
			elementsHaveT = False
			break

	# Checking if Elements have already a internal temperature not eq to Null
	# if yes then use this as starting temperature (this allows continue calc from previous results)
	# if no - we assume the T0

	if not elementsHaveT:
		for element in Elements:
			element.T = T0
	
	Temperatures = [x.T for x in Elements]  # array of temperatures iof elements in given timestep

	# preparing some variables
	GlobalTemperatures = [Temperatures] # array of temperature results
	Time = [0]
	SolverSteps = 0

	timestepValid = True  # assuming very first timestep will be ok

	while (Time[-1] <= EndTime):
		# Main loop over time
		SolverSteps += 1 #  to keep track how real solver iterations was done


		if timestepValid:
			deltaTime = iniTimeStep # just to be ready for non cons timestep
			proposedDeltaTime = []  # keeper for calculated new delta time reset
		else:
			# deltaTime /= 2 # we drop down delta time by half
			deltaTime = min(proposedDeltaTime) # choosing minimum step from previous calculations for all elements that didn't meet accuracy
			proposedDeltaTime = []  # keeper for calculated new delta time reset

		currentStepTemperatures = [] # empty array to keep this timestep

		timestepValid = True  # assuming this timestep will be ok
		index = 0

		for element in Elements:
			# Getting the Tamb for this element:
			# Depending if this given by function of y or just value
			elementTamb = element.air.T(element.y)

			# capturing the previous element temperature
			elementPrevTemp = element.T
			# solve for internal heat generaion
			# using element current if existing:
			if element.current is not False:
				# checking if the element current is a function
				# if yes its assumed that is a f(time)
				if callable(element.current):
					Q = element.Power(element.current(Time[-1]), elementPrevTemp)
				else:
					Q = element.Power(element.current, elementPrevTemp)

			else:
				# if not using current delivered by solver
				# checking if solver current is a function
				if callable(current):					
					Q = element.Power(current(Time[-1]), elementPrevTemp)
				else:
					Q = element.Power(current, elementPrevTemp)
		
			# solving for the convection heat taken out
			Qconv = element.Qconv(elementPrevTemp, elementTamb)
			Q -= Qconv
			# preparing for Air update basd on Qconv for all elements
			# air.addQ(element.y, Qconv)
			# this is disabled becouse was unstable

			#  solving for the radiation heat taken out
			Q -= element.Qrad(elementPrevTemp, elementTamb)

			# ###################################################
			# solving the conduction heat transfer
			# based on the element internal lists of neighbours

			# incoming heat transfer (as per arrows in scheme)
			if len(element.inputs) > 0:
				# checking previous elements
				for prevElement in element.inputs:
					# delta TEmperature previous element minus this one
					deltaT = prevElement.T - element.T

					Rth = 0.5 * element.Rth() + 0.5 * prevElement.Rth()
					Q += deltaT / Rth

			# if we are not the last one of the list
			if len(element.outputs) > 0:
				# checking next element
				for prevElement in element.outputs:
					# delta TEmperature previous element minus this one
					deltaT = element.T - prevElement.T

					Rth = 0.5 * element.Rth() + 0.5 * prevElement.Rth()
					Q -= deltaT / Rth

			# having the total power calculating the energy
			# print(Q) # just for debug

			elementEnergy = Q * deltaTime

			temperatureRise = elementEnergy / (element.mass() * element.material.Cp)

			# in case of big temp rise we need to make timestep smaller
			if abs(temperatureRise) > tempStepAccuracy:
				timestepValid = False # Setting the flag to ignore this step

				# calculating the new time step to meet the tempStepAccuracy
				# for this element
				newDeltaTime = 0.9 * abs((tempStepAccuracy * element.mass() * element.material.Cp) / Q)

				# adding this new calculated step to array for elements in this step
				proposedDeltaTime.append( newDeltaTime )

			currentStepTemperatures.append(elementPrevTemp + temperatureRise)

			# inceasing the index of element
			index += 1

		#  Adding current timestep solutions to master array
		if timestepValid: #  only if we take this step as valid one
			Time.append(Time[-1] + deltaTime) #adding next time step to list
			GlobalTemperatures.append(currentStepTemperatures)

			# adding the previous step T as internal T for each element
			for index, element in enumerate(Elements):
				element.T = GlobalTemperatures[-1][index]


	return Time, GlobalTemperatures, SolverSteps, Elements


def nodePositions(Elements):
    """
    This functions return list of the positions of the each temperature point (middle of element)
    in 1 dimension in [mm]
    """
    pos = [ (0.5*Elements[x-1].shape.l + 0.5*Elements[x].shape.l) for x in range(1, len(Elements))]
    pos.insert(0,Elements[0].shape.l/2)
    return [sum(pos[0:x]) for x in range(1,len(pos)+1)]

def nodePosXY(Elements, base=300):
	"""
	This claculates the pairs of x,y position for each node element
	and store this positions in each node object internal x,y 
	"""
	minY = 0.0

	Elements[0].x = 0
	Elements[0].y = 0

	idx = 0
	for element in Elements:

		# if len(element.inputs) > 0:
		# 	inputs = Elements.index(element.inputs[-1])
		# 	xx = element.inputs[-1].x
		# 	# x1 = Elements.index(element.outputs[0])
		# else:
		# 	inputs = "nic"
		# 	xx = "nic"
		# 	x1 = "nic"

		# print(idx,':', inputs,':',xx,':',x1)
		# idx += 1



		if len(element.inputs) == 0 or element is Elements[0]:
			if element.x == 0:
				element.x = element.shape.getPos()['x'] / 2
			if element.y == 0:
				element.y = element.shape.getPos()['y'] / 2
		else:
			element.x = element.inputs[-1].x + 0.5*element.inputs[-1].shape.getPos()['x'] + element.shape.getPos()['x'] / 2

			element.y = element.inputs[-1].y + 0.5*element.inputs[-1].shape.getPos()['y'] + element.shape.getPos()['y'] / 2


		minY = min(minY, element.y)

	# making shift to put object minY to base
	for element in Elements:
		element.y = element.y - minY + base
		




def drawElements(axis, Elements, Temperatures=None, Text=False, T0=25):
    """
    This method draws a result as a defined shape
    """

    # Checking for the temperatures
    if len(Temperatures) == 0:
        Temperatures = np.zeros(len(Elements))


    # Preparing some data needed for matplotlib draw
    #list of particylar shapes
    my_patches = []

    # initial position of first element
    # rx=0
    # ry=0

    # initial values for plot bondary
    maxY = 0
    maxX = 0
    minX = 0
    minY = 0

    for element in Elements:
    	#  going for each element

            # gatherin data from element shape geometry
            angle = element.shape.angle
            # this is usefull for propper placing in Y
            cosin = abs(math.cos(angle))


            l = element.shape.getPos()['x']
            h = element.shape.getPos()['y']
            

            # figuring out the shape size to draw
            shapeW = abs(math.sin(element.shape.angle)) * element.shape.h
            shapeH = abs(math.cos(element.shape.angle)) * element.shape.h
            # reusing the same variables (recycling) :)
            shapeW = abs(max(abs(l)+shapeW,10))
            shapeH = abs(max(abs(h)+shapeH,10))

            rx = element.x - shapeW/2
            ry = element.y - shapeH/2

            # Drawig the rectangle
            r = patches.Rectangle(
                    (rx , ry),			    # (x,y)
                    shapeW,				    # width
                    shapeH,    				# height
                )

            # adding info text if needed.
            # calculating tx ty text positions
            if Text:
	            # tx = element.x - math.sin(angle)*max(shapeH, shapeW)
	            # ty = element.y + math.cos(angle)*max(shapeH, shapeW)
	            tx = element.x 
	            ty = element.y 
	            txt = '{}K'.format(round(element.T-T0,0))
	            
	            # l = mlines.Line2D([rx,tx], [ry,ty])
	            # axis.add_line(l)
	            trot = (180/math.pi)*element.shape.angle + 90
	            axis.text(tx, ty, txt, fontsize=6, rotation=trot)


            # Adding the rectangle shape into array
            # to display it later on plot
            my_patches.append(r)

            # # updating the x & y position for next element
            # rx += l
            # ry += h

            # checking for the graph limits
            # and updating if this element push them
            if maxX < rx:
                maxX = rx

            if maxY < ry + shapeH:
            	maxY = ry + shapeH

            if minX > rx:
                minX = rx

            if minY > ry - shapeH:
            	minY = ry - shapeH

    # some matplotlib mambo jambo to make the rect
    # colored according to the temp rise
    shapes = PatchCollection(my_patches, cmap=mpl.cm.jet, alpha=1)
    shapes.set_array(Temperatures)
    # puttig it all into subplot
    axis.add_collection(shapes)

    # final
    axes = plt.gca()
    axes.set_xlim([minX-100, maxX+100])
    axes.set_ylim([minY-100, maxY+100])
    axis.grid()
    plt.ylabel('Position [mm]')
    plt.xlabel('Position [mm]')

    # axis.set_title('Temp Rise Map')

    return my_patches

def generateNodes(Input):
	"""
	This fucntion prepare the nodes base on the reference one 
	for given lenght 
	Input:
	list of tuples
	[(El, Len, nodes), (El2, Len2, nodes), ...]
	where
		El - reference element
		Len - element lenght
		nodes - required number of thermal nodes in lenght
	"""
	# preparing internal emptylist
	output = []

	# the main loop
	for set in Input:
		for i in range(set[2]):
			tempEl = copy.deepcopy(set[0]) # Cloning the ref element
			tempEl.shape.l = set[1] / set[2] # setting the new clone length
			output.append(tempEl)

	return output



def generateList(Input):
	"""
	This functions return generated list of elements
	based on the given sets.
	Input:
	list of object with repetitnion count for each as list of list:
	example:
	[(Object1, Object1_count), (Object2, Object2_count)...]

	Output:
		List of elements ready for solver
	"""

	# preparing internal emptylist
	output = []

	# the main loop
	for set in Input:
		for i in range(set[1]):
			output.append(copy.deepcopy(set[0]))

	return output

def elementsForObjSolver(Elements, current=False):
	# This procedure update the Elements list 
	# to introduce each element neigbours into propper internal lists
	for index, element in enumerate(Elements):
		
		# noting down current value in element
		element.current = current

		if index > 0:
			element.inputs.append(Elements[index-1])
		if index < len(Elements)-1:
			element.outputs.append(Elements[index+1]) 
	# it makes updates in elements objects no return here

def joinNodes(ListA, ListB, JointPosInA):
	# Join two node list 
	# Join ListB into node of ListA at position JointPosIaA
	# ListA:
	#  [0]
	#  [1]
	#  [.]              listB
	#  [JointPos]  <--- [0][1][2][.][-1]
	#  [.]
	#  [-1]	

	ListA[JointPosInA].outputs.append(ListB[0])
	# ListB[0].inputs.append(ListA[JointPosInA])
	ListB[0].inputs = [ListA[JointPosInA]]