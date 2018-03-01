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


def Solver(Elements, current, Tamb, T0, EndTime, iniTimeStep = 1, tempStepAccuracy = 0.1):
	# Preparing some geometry data for each node element
	# Calculating the each node 2D position based on the Elements vector
	XY = nodePosXY(Elements)

	# preparing some variables
	Temperatures = [T0 for x in Elements]  # array of temperatures iof elements in given timestep
	GlobalTemperatures = [Temperatures] # array of temperature results

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
		for element in Elements:
			# capturing the previous element temperature
			elementPrevTemp = GlobalTemperatures[-1][index]
			# solve for internal heat generaion
			Q = element.Power(current, elementPrevTemp)
			# solving for the convection heat taken out
			Q -= element.Qconv(elementPrevTemp, Tamb)
			#  solving for the radiation heat taken out
			Q -= element.Qrad(elementPrevTemp, Tamb)

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

	return Time, GlobalTemperatures, SolverSteps, nodePositions(Elements), XY


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
	posX = [ 0.5*(Elements[i-1].shape.getPos()['x'] + 0.5*Elements[i].shape.getPos()['x']) for i in range(1, len(Elements))]
	posX.insert(0, 0.5*Elements[0].shape.getPos()['x'])

	posY = [ 0.5*(Elements[i-1].shape.getPos()['y'] + 0.5*Elements[i].shape.getPos()['y']) for i in range(1, len(Elements))]
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



    my_patches = []
    rx=0
    ry=0
    maxX = 0

    for i,element in enumerate(Elements):
            
            
            angle = element.shape.angle 

            l = element.shape.getPos()['x']
            h = element.shape.getPos()['y']


            r = patches.Rectangle(
                    (min(rx,rx+l), ry),     # (x,y)
                    abs(max(abs(l),10)),    # width
                    abs(max(abs(h),10)),    # height
                )

            my_patches.append(r)

            rx += l
            ry += max(abs(h),10)

            if maxX < rx:
                maxX = rx

    shapes = PatchCollection(my_patches, cmap=mpl.cm.jet, alpha=0.5)
    shapes.set_array(Temperatures)
    axis.add_collection(shapes)

    axes = plt.gca()
    axes.set_xlim([0, maxX+100])
    axes.set_ylim([0, ry+100])
    axis.grid()
    plt.ylabel('Position [mm]')
    plt.xlabel('Position [mm]')

    axis.set_title('Temp Rise Map')