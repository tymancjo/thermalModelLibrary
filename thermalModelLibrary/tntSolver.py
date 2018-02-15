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

def Solver(Elements, current, Tamb, T0, EndTime, iniTimeStep = 1, tempStepAccuracy = 0.1):
	
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

	return Time, GlobalTemperatures, SolverSteps



		