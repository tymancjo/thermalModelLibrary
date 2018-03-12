# script file for thermal solver

# IMPORTS
# for performance measurement
from datetime import datetime
# memorizing statrup time
startTime = datetime.now()

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy

import numpy as np

# Libraries ot the tnt model
from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolverObj as tntS

# Defining some materials
Cu = tntO.Material(conductivity=56e6)
CuACB = tntO.Material(conductivity=7e6)

# Defining some handy vallues
# IP42 parameters 
HTC = 6
emmisivity = 0.35

# Enviroment and starting point
Tambient = 20


# Defining analysis elements objects
ACB = tntO.thermalElement(
        # shape(width, height, length, number of bars in parrallel, pointing angle {0->right, 90->top, 180->left, 270-> down})
        shape = tntO.shape(20,100,200/4,1,-90), 
        HTC = HTC,
        emissivity = emmisivity,
        dP = True,
        source = 0,
        material = CuACB)

zwora = tntO.thermalElement(
        shape = tntO.shape(10,40,50,1,0), # one bar 40x10 50mm pointing right
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

VBB = tntO.thermalElement(
        shape = tntO.shape(10,40,50,4,-90), # 4 bars 40x10 100mm pointing down
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

VBB_hor_top = tntO.thermalElement(
        shape = tntO.shape(10,40,100,4,0),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

VBB_hor_btm = tntO.thermalElement(
        shape = tntO.shape(100,10,65,1,180+45),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

MBB = tntO.thermalElement(
        shape = tntO.shape(10,30,50,4,0),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)


# Defining the analysis circuit/objects connection stream
# this works like this:
#  (nodeElement, Number of such elemnts in serial)
PC_VBB =      [
                (MBB, 5),
                (VBB, int(900/50)), # ~900mm
                (ACB, 4),
                (VBB, 4), # ~200mm
                (VBB_hor_btm, 2), # Lashe for CT ~130mm
                (VBB, 4), # ~200mm
                (zwora, 2)
                ]

# This function clone the nodeelemnts based in tuples above
# and create final 1D list of elements 
PC_VBB = tntS.generateList(PC_VBB) 

# As the solver base on objects of nodes only we need to prepare
# for each of node element internal lists of
# element before and elements after
# its done below
tntS.elementsForObjSolver(PC_VBB)


# Filling elements positions x,y in each elemnt object
tntS.nodePosXY(PC_VBB)

# shifting the lowest part to 300mm as it is in real
for element in PC_VBB:
    element.y += 300



  
# Running the solver for
# Geometry from list PC_VBB
# 2500 A
# 20 degC ambient
# 20 degC starting temperature
# 4h analysis end time
# 500s as the default and max timestep size - this is auto reduced when needed - see tntS.Solver object
# 0.01K maximum allowed temperature change in single timestep - otherwise solution accuracy - its used for auto timestep selection 
A,B,s, L2, XY, air = tntS.Solver(PC_VBB,2000,20,20,8*60*60, 5, 0.01)

# this returns:
#  A vector of time for each step
#  B array of temperature rises for each element in each step
#  s the total number of solver iterations (not neccessary the same as number of timesteps!)
#  L2 vector of positions in [mm] for each temperature calculations point (each object middle)
#  depreciated: XY - vector of 2D vectors of XY position of each node - None is returened - as now each element have its x and y

# results from solver
print('execution time: ', datetime.now() - startTime)
print('time steps: ', len(A))
print('solver steps: ', s)
print('thermal nodes: ', len(PC_VBB))


# Rest is just cleaning up data for plotting
t = np.array(A)
t = t / (60*60) # Time in hours

# preparing temp rises as results
b = np.array(B)
b = b - 20


# defining the main plot window
fig = plt.figure('Temperature Rise Analysis ')

# first subplot for the timecurves
ax1 = fig.add_subplot(221)
ax1.plot(t,b[:,:])
ax1.set_title('Temp Rise vs. Time')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Time [h]')

# Temperature rises from lats timepoint along the 1D model length
ax2 = fig.add_subplot(223)

ax2.plot(b[-1,::-1],'rx--')
ax2.set_title('Temp Rise vs. 1D position')
plt.ylabel('Temp Rise [K]')
plt.xlabel('node')

ax1.grid()
ax2.grid()

# Defining the subplot for geometry heat map
ax3 = fig.add_subplot(122, aspect='equal')
# runs the defined procedure on this axis
boxes = tntS.drawElements(ax3,PC_VBB,np.array(b[-1,:]))

ax4 = ax3.twiny()
if air:
    ax4.plot(air.aCellsT, np.linspace(0,air.h,air.n) ,'b--', label='air')
else:
    ax4.plot(np.array([Ta(y) for y in np.linspace(0,max(L2),20)]), np.linspace(0,max(L2),20) ,'b--', label='air')

ax4.plot([element.T for element in PC_VBB],[element.y for element in PC_VBB],'r--', label='nodes')

plt.xlabel('Temp [degC]')
plt.legend()

plt.tight_layout()

plt.show()

