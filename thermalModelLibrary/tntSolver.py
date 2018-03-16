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


def Solver(Elements, current, Tamb, T0, EndTime, iniTimeStep = 1, tempStepAccuracy = 0.1):
	# Preparing some geometry data for each node element
	# Calculating the each node 2D position based on the Elements vector
	XY = nodePosXY(Elements)
	# putting the elements positions into elements
	# this will be helpfull for any specific handling and drawing results
	# we will use this same loop as well to check if all elements have already T set
	elementsHaveT = True

	# and we will capture maxY value
	maxY = 0
	for index, element in enumerate(Elements):
		element.x = XY[index][0]
		element.y = XY[index][1]
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
		air = tntA.airObject( 40, 1.1 * maxY, Tamb)

		for element in Elements:
			air.addQ(element.y, element.Power(current, Tamb))

		air.solveT(1) # updating the Air temperature dist 1- sorted 0-unsorted by values from top
		print(air.aCellsT)
		Tamb = air.T

		# for now, we just solve the air once before everything
		# based only on the internal heat generation
		# later plan: do it on each step
		# or mabe Lets start from this second plan :)



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

		# print('dT: {}'.format(deltaTime))  # just for debug

		currentStepTemperatures = [] # empty array to keep this timestep

		timestepValid = True  # assuming this timestep will be ok
		index = 0

		# air.solveT() # updating the Air temperature dist
		# air.resetQ() # clearing the air Qinput vector
		# print(air.aCellsT)

		for element in Elements:
			# Getting the Tamb for this element:
			# Depending if this given by function of y or just value
			if useF:
				elementTamb = Tamb(element.y)
			else:
				elementTamb = Tamb


			# capturing the previous element temperature
			elementPrevTemp = GlobalTemperatures[-1][index]
			# solve for internal heat generaion
			Q = element.Power(current, elementPrevTemp)
			# solving for the convection heat taken out
			Qconv = element.Qconv(elementPrevTemp, elementTamb)
			Q -= Qconv
			# preparing for Air update basd on Qconv for all elements
			# air.addQ(element.y, Qconv)
			# this is disabled becouse was unstable

			#  solving for the radiation heat taken out
			Q -= element.Qrad(elementPrevTemp, elementTamb)

			# solving the conduction heat transfer
			# if we are not the forst on ein te list
			if index > 0:
				# checking previous element
				prevElement = Elements[index - 1]
				prevElementTemp = GlobalTemperatures[-1][index - 1]
				# delta TEmperature previous element minus this one
				deltaT = prevElementTemp - elementPrevTemp

				Rth = 0.5 * element.Rth() + 0.5 * prevElement.Rth()
				Q += deltaT / Rth

			# if we are not the last one of the list
			if index < len(Elements) - 1:
				# checking next element
				prevElement = Elements[index + 1]
				prevElementTemp = GlobalTemperatures[-1][index + 1]
				# delta TEmperature previous element minus this one
				deltaT = elementPrevTemp - prevElementTemp

				Rth = 0.5 * element.Rth() + 0.5 * prevElement.Rth()
				Q -= deltaT / Rth

			# having the total power calculating the energy
			# print(Q) # just for debug

			elementEnergy = Q * deltaTime
			# print(elementEnergy) # just for debug

			temperatureRise = elementEnergy / (element.mass() * element.material.Cp)
			# print(temperatureRise) # just for debug

			# in case of big temp rise we need to make timestep smaller
			if abs(temperatureRise) > tempStepAccuracy:
				timestepValid = False # Setting the flag to ignore this step

				# calculating the new time step to meet the tempStepAccuracy
				# for this element
				newDeltaTime = 0.9 * abs((tempStepAccuracy * element.mass() * element.material.Cp) / Q)

				# adding this new calculated step to array for elements in this step
				proposedDeltaTime.append( newDeltaTime )
				# for debug:
				# print('[{}] : [{}] : [{}]'.format(SolverSteps, newDeltaTime, Time[-1]))

			currentStepTemperatures.append(elementPrevTemp + temperatureRise)

			# inceasing the index of element
			index += 1

		#  Adding current timestep solutions to master array
		if timestepValid: #  only if we take this step as valid one
			Time.append(Time[-1] + deltaTime) #adding next time step to list
			GlobalTemperatures.append(currentStepTemperatures)

	# Putting the last step temperatures into elements internal T variable
	# to make all results bounded with the elements and make it visible outside function
	for index, element in enumerate(Elements):
		element.T = GlobalTemperatures[-1][index]

	return Time, GlobalTemperatures, SolverSteps, nodePositions(Elements), XY, air


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
	This returns the pairs of x,y position for each node element
	"""
	posX = [ (0.5*Elements[i-1].shape.getPos()['x'] + 0.5*Elements[i].shape.getPos()['x']) for i in range(1, len(Elements))]
	posX.insert(0, 0.5*Elements[0].shape.getPos()['x'])

	posY = [ (0.5*Elements[i-1].shape.getPos()['y'] + 0.5*Elements[i].shape.getPos()['y']) for i in range(1, len(Elements))]
	posY.insert(0, 0.5*Elements[0].shape.getPos()['y'])

	sumX = [sum(posX[0:x]) for x in range(1,len(posX)+1)]
	sumY = [sum(posY[0:x]) for x in range(1,len(posY)+1)]

	return [ [sumX[i], sumY[i]] for i in range(len(posY))]


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
    rx=0
    ry=0

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

            # Drawig the rectangle
            r = patches.Rectangle(
                    (min(rx,rx+l), ry - cosin*(shapeH/2)),     # (x,y)
                    shapeW,				    # width
                    shapeH,    				# height
                )
            # Adding the rectangle shape into array
            # to display it later on plot
            my_patches.append(r)

            # updating the x & y position for next element
            rx += l
            ry += h

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
