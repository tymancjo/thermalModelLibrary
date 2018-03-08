from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolverObj as tntS

import matplotlib.pyplot as plt
import numpy as np

Cu = tntO.Material()

conductor = tntO.thermalElement(
        	shape = tntO.shape(20,100,200,1,90), 
        	HTC = 5,
        	emissivity = 0.35,
        	dP = True,
        	source = 0,
        	material = Cu)

Elements = [ (conductor, 10) ]

Elements = tntS.generateList(Elements) 

tntS.elementsForObjSolver(Elements)

tntS.nodePosXY(Elements)

t,T,stp, linpos, XYpos, air = tntS.Solver(Elements, 2000, 20, 20, 4*60*60, 500, 0.01)


# Rest is just cleaning up data for plotting
t = np.array(t) # changing list t into np array type
t = t / (60*60) # recalculating timesteps to hours

# preparing temp rises as results
b = np.array(T)
b = b - 20 # subtracting the ambient to get temperature rises

# defining the main plot window
fig = plt.figure('Temperature Rise Analysis ')

# first subplot for the timecurves
ax1 = fig.add_subplot(221)
ax1.plot(t,b[:,:])
ax1.set_title('Temp Rise vs. Time')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Time [h]')

# Temperature rises from last timepoint for each node
ax2 = fig.add_subplot(223)
ax2.plot(b[-1,::-1],'rx--')
ax2.set_title('Temp Rise vs. 1D position')
plt.ylabel('Temp Rise [K]')
plt.xlabel('node')
ax1.grid()
ax2.grid()

# Defining the subplot for geometry heat map
ax3 = fig.add_subplot(122, aspect='equal')
# runs the defined procedure on this axis to draw the shape
tntS.drawElements(ax3,Elements,np.array(b[-1,:]))

plt.tight_layout()
plt.show()