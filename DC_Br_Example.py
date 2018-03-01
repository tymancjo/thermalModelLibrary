# script file for thermal solver

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib as mpl
import numpy as np
import math

import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolver as tntS

# Defining some materials
Cu = tntO.Material(alpha=0)
alteredCu = tntO.Material(thermalConductivity = 1e6)

# Defining some handy vellues
HTC = 5


# Defining analysis elements objects
Gerapid = tntO.thermalElement(
        shape = tntO.shape(10,40,200,1,90),
        HTC = 0,
        emissivity = 0,
        dP = False,
        source = 80,
        material = alteredCu)

Terminal = tntO.thermalElement(
        shape = tntO.shape(30,100,200),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

Terminal2 = tntO.thermalElement(
        shape = tntO.shape(30,100,200,1,180),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

Connection = tntO.thermalElement(
        shape = tntO.pipe(30,12.5,20,2),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

Connection2 = tntO.thermalElement(
        shape = tntO.pipe(30,12.5,20,2,180),
        HTC = HTC,
        emissivity = 0,
        material = Cu)


BB = tntO.thermalElement(
        shape = tntO.shape(10,100,300,4),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

BB2 = tntO.thermalElement(
        shape = tntO.shape(10,100,300,4,180),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

# Defining the analysis circuit/objects connection stream
# Elements = [BB2,BB2,BB2,Connection2, Terminal2, Gerapid, Terminal, Connection, BB, BB, BB]
Elements = [BB,BB,BB,
            Connection,
            Terminal,
            Gerapid,
            Terminal2,
            Connection2,
            BB2, BB2, BB2]

# Running the solver for
# Geometry from Elements list
# 4000 A
# 20 degC ambient
# 20 degC starting temperature
# 4h analysis end time
# 500s as the default and max timestep size - this is auto reduced when needed - see tntS.Solver object
# 0.01K maximum allowed temperature change in single timestep - otherwise solution accuracy - its used for auto timestep selection 
A,B,s, L2, XY= tntS.Solver(Elements,4000,20,20,4*60*60,500, 0.01)

# this returns:
#  A vector of time for each step
#  B array of temperature rises for each element in each step
#  s the total number of solver iterations (not neccessary the same as number of timesteps!)
#  L2 vector of positions in [mm] for each temperature calculations point (each object middle)
#  XY - vector of 2D vectors of XY position of each node


# Rest is just cleaning up data for plotting
t = np.array(A)
t = t / (60*60) # Time in hours

# preparing tem rises as results
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

ax2.plot(L2,b[-1,:],'bx--')
ax2.set_title('Temp Rise vs. 1D position')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Position [mm]')

ax1.grid()
ax2.grid()

# Defining the subplot for geometry heat map
ax3 = fig.add_subplot(122, aspect='equal')
# runs the defined procedure on this axis
tntS.drawElements(ax3,Elements,np.array(b[-1,:]))


plt.tight_layout()
plt.show()


