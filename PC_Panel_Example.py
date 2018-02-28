# script file for thermal solver

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
import matplotlib.patches as patches
import numpy as np
import math

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolver as tntS

# Defining some materials
Cu = tntO.Material()
CuACB = tntO.Material(conductivity=5e6)
alteredCu = tntO.Material(thermalConductivity=100)

# Defining some handy vellues
# IP42 parameters 
HTC = 6
emmisivity = 0.35

# Enviroment and starting point
Tambient = 20


# Defining analysis elements objects
ACB = tntO.thermalElement(
        shape = tntO.shape(20,100,230,1,90),
        HTC = HTC,
        emissivity = emmisivity,
        dP = True,
        source = 0,
        material = CuACB)

BottomVBB = tntO.thermalElement(
        shape = tntO.shape(10,40,100,4,45),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

Connection = tntO.thermalElement(
        shape = tntO.pipe(30,12.5,300,4,0),
        HTC = 0,
        emissivity = 0,
        material = Cu)


TopVBB = tntO.thermalElement(
        shape = tntO.shape(10,40,100,4,90+45),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

# Defining the analysis circuit/objects connection stream
Elements =      [BottomVBB,BottomVBB,BottomVBB,BottomVBB,BottomVBB,
                BottomVBB,BottomVBB,BottomVBB,BottomVBB,BottomVBB,
                Connection,
                ACB,
                Connection,
                TopVBB,TopVBB,TopVBB,TopVBB,TopVBB,
                TopVBB,TopVBB,TopVBB,TopVBB,TopVBB]

# Running the solver for
# Geometry from Elements list
# 2500 A
# 20 degC ambient
# 20 degC starting temperature
# 5h analysis end time
# 500s as the default and max timestep size - this is auto reduced when needed - see tntS.Solver object
# 1K maximum allowed temperature change in single timestep - otherwise solution accuracy - its used for auto timestep selection 
A,B,s, L2 = tntS.Solver(Elements,2500,Tambient,Tambient,5*60*60,500, 0.1)

# this returns:
#  A vector of time for each step
#  B array of temperature rises for each element in each step
#  s the total number of solver iterations (not neccessary the same as number of timesteps!)
#  L2 vector of positions in [mm] for each temperature calculations point (each object middle)

# Rest is just cleaning up data for plotting
t = np.array(A)
t = t / (60*60) # Time in hours

b = np.array(B)
b = b - Tambient



fig = plt.figure('SMB-21')

ax1 = fig.add_subplot(211)

ax1.plot(t,b[:,7],'r',label="ACB")
ax1.plot(t,b[:,5],'b', label="Btm Terminal")
ax1.plot(t,b[:,10],'y', label="Top Terminal")
# ax1.plot(t,b[:,3:],'g')

plt.ylabel('Temp Rise [K]')
plt.xlabel('Time [h]')

ax2 = fig.add_subplot(212)

ax2.plot(L2,b[-1,:],'bx--')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Position [mm]')

ax1.legend()

print('Solution steps: {}'.format(len(t)))
print('Solver Steps: {}'.format(s))
print('Elements TempRises: {}'.format(b[-1,:]))

XY = tntS.nodePosXY(Elements)
print('XY', XY)


plt.tight_layout()
# plt.show()

# Drawing the boxes on node positions
fig1 = plt.figure('Geometry Sketch')
ax1 = fig1.add_subplot(111, aspect='equal')

for i,pos in enumerate(XY):
        ax1.add_patch(
            patches.Rectangle(
                (pos[0], pos[1]),   # (x,y)
                100,          # width
                100,          # height
            )
        )

        ax1.text(pos[0], pos[1], round(b[-1,i],2), fontsize=12)

axes = plt.gca()
axes.set_xlim([0,3000])
axes.set_ylim([0,3000])

plt.show()


