# script file for thermal solver
# for performance measurement
from datetime import datetime
startTime = datetime.now()

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
# import matplotlib.patches as patches
# from matplotlib.collections import PatchCollection
import matplotlib as mpl
import numpy as np
import mpld3
# import math

# import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntPanelsSolver as tntS
from thermalModelLibrary import tntPanel as tntP

# Defining some materials
Cu = tntO.Material()
CuACB = tntO.Material(conductivity=5e6)
alteredCu = tntO.Material(thermalConductivity=100)

# Defining some handy values
# IP42 parameters 
HTC = 6
emmisivity = 0.35

# Environment and starting point
Tambient = 20


# Defining analysis elements objects
ACB = tntO.thermalElement(
        shape = tntO.shape(20,100,230/4,1,-90),
        HTC = HTC,
        emissivity = emmisivity,
        dP = True,
        source = 0,
        material = CuACB)

zwora = tntO.thermalElement(
        shape = tntO.shape(10,40,25,1,-90),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

VBB = tntO.thermalElement(
        shape = tntO.shape(10,40,100,4,-90),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

BottomVBB = tntO.thermalElement(
        shape = tntO.shape(10,40,100,4,180 + 15),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

Connection = tntO.thermalElement(
        shape = tntO.pipe(30,12.5,20,4,0),
        HTC = 0,
        emissivity = 0,
        material = Cu)

Connection2 = tntO.thermalElement(
        shape = tntO.pipe(30,12.5,20,4,180),
        HTC = 0,
        emissivity = 0,
        material = Cu)


TopVBB = tntO.thermalElement(
        shape = tntO.shape(10,40,100,4,-15),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

MBB = tntO.thermalElement(
        shape = tntO.shape(10,30,100,4,0),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

# Defining the analysis circuit/objects connection stream
PC_VBB =      [
                (VBB, 4),
                (TopVBB, 3),
                (VBB, 2),
                (Connection, 1),
                (ACB, 4),
                (Connection2, 1),
                (BottomVBB, 3),
                (VBB, 5)
                ]

PC_VBB_1 = tntS.generateList(PC_VBB) 
# Filling the element.inputs and element.output lists

PC_VBB_2 = tntS.generateList(PC_VBB) 
# Filling the element.inputs and element.output lists

PC_MBB = [
            (MBB,5)
        ] 

PC_MBB_1 = tntS.generateList(PC_MBB) 
PC_MBB_2 = tntS.generateList(PC_MBB) 

PC_MBB_3 = tntS.generateList(PC_MBB) 


tntS.elementsForObjSolver(PC_MBB_1, 0)
tntS.elementsForObjSolver(PC_VBB_1, 2500)
tntS.elementsForObjSolver(PC_MBB_2, 2500)

tntS.elementsForObjSolver(PC_VBB_2, 1500)
tntS.elementsForObjSolver(PC_MBB_3, 1000)

# Making thermal connections between lists of elements (branches)
tntS.joinNodes(PC_MBB_1, PC_VBB_1, -1)
tntS.joinNodes(PC_MBB_1, PC_MBB_2, -1)
# tntS.joinNodes(PC_MBB_2, PC_MBB_3, -1)

# tntS.joinNodes(PC_MBB_2, PC_VBB_2, -1)

# creating total list of all elements
Elements = []
Elements.extend(PC_MBB_1)
Elements.extend(PC_VBB_1)
Elements.extend(PC_MBB_2)

Panel = tntP.PCPanel(Nodes=Elements,
                 In=PC_MBB_1[0], 
                 Out=PC_MBB_2[-1], 
                 OutCurrent=0,
                 Air=None, T0=20)

Panel2 = tntP.PCPanel(Nodes=PC_MBB_3,
                 In=PC_MBB_3[0], 
                 Out=PC_MBB_3[-1], 
                 OutCurrent=0,
                 Air=None, T0=20)


Panel3 = tntP.PCPanel(Nodes=Elements,
                 In=PC_MBB_1[0], 
                 Out=PC_MBB_2[-1], 
                 OutCurrent=0,
                 Air=None, T0=120)


Panels = [Panel, Panel2, Panel3]



Time, T, Stp, Nodes = tntS.PanelSolver(Panels, 20, 1*60*60, 
                iniTimeStep = 1,
                tempStepAccuracy = 0.1)

print('execution time: ', datetime.now() - startTime)
print('time steps: ', len(Time))
print('solver steps: ', Stp)


# Rest is just cleaning up data for plotting
t = np.array(Time)
t = t / (60*60) # Time in hours

# preparing temp rises as results
b = np.array(T)
b = b - 20

# defining the main plot window
fig = plt.figure('Temperature Rise Analysis ')

# first subplot for the timecurves
ax1 = fig.add_subplot(231)
ax1.plot(t,b[:,:])
ax1.set_title('Temp Rise vs. Time')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Time [h]')

# Temperature rises from lats timepoint along the 1D model length
ax2 = fig.add_subplot(234)

ax2.plot(b[-1,:],'rx--')
ax2.set_title('Temp Rise vs. nodes')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Node')

ax1.grid()
ax2.grid()

# Defining the subplot for geometry heat map
ax3 = fig.add_subplot(132, aspect='equal')
# runs the defined procedure on this axis
tntS.drawElements(ax3,Nodes,np.array(b[-1,:]))

plt.tight_layout()

figG = plt.figure('Geometry thermal map ')
axG = figG.add_subplot(111, aspect='equal')
tntS.drawElements(axG,Nodes,np.array(b[-1,:]))


scatter = axG.scatter([element.x for element in Nodes],
            [element.y for element in Nodes],
            s=[element.T for element in Nodes],
            c=[element.T for element in Nodes],
            cmap=mpl.cm.jet, alpha=0.5)

# labels = [element.T-20 for element in Elements]
# tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
# mpld3.plugins.connect(figG, tooltip)

# mpld3.show()

plt.show()

# Function that describe ambient change with height
def ambientT(y, Q=0, T0 = 20):
    """
    y - in mmm
    output in degC
    """
    return T0 + y * (3/100)

def consT(y):
    return 20

