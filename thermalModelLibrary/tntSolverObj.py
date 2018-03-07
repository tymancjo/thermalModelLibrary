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
			- solve elements for DT from interal heat (based on prev T)
			- solve for heat conduction from prev and next (based on prev T)
			- solve for heat transmitted via convection (based on prev T)
			- solve for heat transmited by radiation (based on previous T)

			Having the total heat in element -> calculate energy -> calculate DT
			calculate Temperature = Previous temp + DT
"""
# Importing external library
import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib as mpl
import numpy as np
import math

# to be able to make the deep copy of each object
import copy

# self made library for Air model
from thermalModelLibrary import tntAir as tntA


def Solver(Elements, current, Tamb, T0, EndTime, iniTimeStep = 1, tempStepAccuracy = 0.1, sortAir=True):

	# # Filling the element.inputs and element.output lists
	# elementsForObjSolver(Elements) 
	# # Preparing some geometry data for each node element
	# # Calculating the each node 2D position based on the Elements vector
	# # XY = nodePosXY(Elements)
	
	# # calulating each element x and y
	# nodePosXY(Elements)
	
	# we will use this same loop as well to check if all elements have already T set
	elementsHaveT = True

	# and we will capture maxY value
	maxY = 0
	for element in Elements:
		maxY = max(maxY, element.y)

		if not element.T:
			elementsHaveT = False

	# Checking if Elements have already a internal temperature not eq to Null
	# if yes then use this as starting temperature (this allows continue calc from previous results)
	# if no - we assume the T0

	if elementsHaveT:
		Temperatures = [x.T for x in Elements]  # array of temperatures iof elements in given timestep
	else:
		Temperatures = [T0 for x in Elements]  # array of temperatures iof elements in given timestep

	# preparing some variables
	GlobalTemperatures = [Temperatures] # array of temperature results

	# Checking if the delivered Tamb is a function or a value
	# if it is a function, each element will have Tamb = f(element y position)
	# else is just a value
	if callable(Tamb):
		print('Tamb is a function')
		useF = True
		air = None

	else:
		# we create air based on library
		useF = True
		air = tntA.airObject( 20, 1.1 * maxY, Tamb)

		# generating sources to static solve Air
		for element in Elements:
			if element.current is not False:
				air.addQ(element.y, element.Power(element.current, Tamb))
			else:
				air.addQ(element.y, element.Power(current, Tamb))

		air.solveT(sortAir) # updating the Air temperature dist 1- sorted 0-unsorted by values from top
		print(air.aCellsT)
		Tamb = air.T

		# for now, we just solve the air once before everything
		# based only on the internal heat generation
		# later plan: do it on each step
		# or mabe Lets start from this second plan :)

	# lets assign initial T value for elements
	# if the leemnts don't have set up initial conditions
	
	if not elementsHaveT: 
		for element in Elements:
			# Getting the Tamb for this element:
			# Depending if this given by function of y or just value
			if useF:
				element.T = Tamb(element.y)


	Time = [0]
	SolverSteps = 0

	timestepValid = True  # assuming very first timestep will be ok

	while (Time[-1] <= EndTime):
		# Main loop over time
		SolverSteps += 1 #  to keep track how real solver iterations was done


		if timestepValid:
			deltaTime = iniTimeStep # just to be ready for non cons timestep
			proposedDeltaTime = []  # keeper for calculated new delata time reset
		else:
			# deltaTime /= 2 # we drop down deltatime by half
			deltaTime = min(proposedDeltaTime) # choosing minimumum step from previous calculations for all elements that didnt meet accuracy
			proposedDeltaTime = []  # keeper for calculated new delata time reset

		currentStepTemperatures = [] # empty array to keep this timestep

		timestepValid = True  # assuming this timestep will be ok
		index = 0

		for element in Elements:
			# Getting the Tamb for this element:
			# Depending if this given by function of y or just value
			if useF:
				elementTamb = Tamb(element.y)
			else:
				elementTamb = Tamb


			# capturing the previous element temperature
			elementPrevTemp = element.T
			# solve for internal heat generaion
			# using element current if existing:
			if element.current is not False:
				Q = element.Power(element.current, elementPrevTemp)
			else:
				# if not using current delivered by solver
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


	return Time, GlobalTemperatures, SolverSteps, nodePositions(Elements), None, air


def nodePositions(Elements):
    """
    This functions return list of the positions of the each temperature point (middle of element)
    in 1 dimension in [mm]
    """
    pos = [ (0.5*Elements[x-1].shape.l + 0.5*Elements[x].shape.l) for x in range(1, len(Elements))]
    pos.insert(0,Elements[0].shape.l/2)
    return [sum(pos[0:x]) for x in range(1,len(pos)+1)]

def nodePosXY(Elements):
	"""
	This claculates the pairs of x,y position for each node element
	and store this positions in each node object internal x,y 
	"""
	minY = 0.0

	Elements[0].x = 0
	Elements[0].y = 0

	
	for element in Elements:
		if len(element.inputs) == 0:
			if element.x == 0:
				element.x = element.shape.getPos()['x'] / 2
			if element.y == 0:
				element.y = element.shape.getPos()['y'] / 2
		else:
			element.x = element.inputs[-1].x + 0.5*element.inputs[-1].shape.getPos()['x'] + element.shape.getPos()['x'] / 2

			element.y = element.inputs[-1].y + 0.5*element.inputs[-1].shape.getPos()['y'] + element.shape.getPos()['y'] / 2


		minY = min(minY, element.y)

	# making shift to put onject minY to 0
	for element in Elements:
		element.y = element.y - minY
		




def drawElements(axis, Elements, Temperatures=None):
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
                    # (min(rx,rx+l), ry - cosin*(shapeH/2)),     # (x,y)
                    (rx , ry),			    # (x,y)
                    shapeW,				    # width
                    shapeH,    				# height
                )

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

            if maxY < ry:
            	maxY = ry

            if minX > rx:
                minX = rx

            if minY > ry:
            	minY = ry

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

    axis.set_title('Temp Rise Map')

    return my_patches

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
	ListB[0].inputs.append(ListA[JointPosInA])