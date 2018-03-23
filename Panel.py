# script file for thermal solver
# for performance measurement
from datetime import datetime
startTime = datetime.now()

import matplotlib.pyplot as plt 
import matplotlib as mpl
import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntPanelsSolver as tntS
from thermalModelLibrary import tntPanel as tntP
from thermalModelLibrary import elements as el



# Defining analysis elements objects
T0=35
I = 1600
ACB = el.EG_F1
VBB = el.VBB_F1G_1k6
MBB = el.SMB_6
CT = el.CT_2x40

# New definition by: (Proto Node El, Length [mm], #nodes)
PC_VBB =      [
                (VBB, 900, 10), 
                (ACB, 200, 4),
                (VBB, 200, 4), 
                (CT, 130, 3), 
                (VBB, 200, 4), 
                ]


# New function to generate final list
PC_VBB = tntS.generateNodes(PC_VBB) 




# MBB for 1st panel
PC_MBB = tntS.generateNodes([(MBB, 1000, 10)]) 





Panel = tntP.PCPanel(MBB=PC_MBB,
                     VBB=PC_VBB,
                     Load=False,
                     Air=None,
                     T0=T0)



# Setting up currents in panel (manually for now)


Panel.set3I(Iin=I,
            Iout=0,
            Ifeeder=I)


# setup the lineup
Lineup = [Panel]

Time, T, Stp, Nodes = tntS.PanelSolver(Lineup, T0, 6*60*60, 
                iniTimeStep = 1,
                tempStepAccuracy = 0.1)


# below is plotting results
print('execution time: ', datetime.now() - startTime)
print('time steps: ', len(Time))
print('solver steps: ', Stp)

# Rest is just cleaning up data for plotting
t = np.array(Time)
t = t / (60*60) # Time in hours

# preparing temp rises as results
b = np.array(T)
b = b - T0

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

ax2.plot(b[-1,:],'rx--')
ax2.set_title('Temp Rise vs. nodes')
plt.ylabel('Temp Rise [K]')
plt.xlabel('Node')

ax1.grid()
ax2.grid()

# Defining the subplot for geometry heat map
ax3 = fig.add_subplot(122, aspect='equal')
# runs the defined procedure on this axis
tntS.drawElements(ax3,Nodes,np.array(b[-1,:]), Text=False)

plt.tight_layout()

figG = plt.figure('Geometry thermal map ')
axG = figG.add_subplot(111, aspect='equal')
tntS.drawElements(axG,Nodes,np.array(b[-1,:]), Text=True, T0=T0)


scatter = axG.scatter([element.x for element in Nodes],
            [element.y for element in Nodes],
            s=[element.T for element in Nodes],
            c=[element.T for element in Nodes],
            cmap=mpl.cm.jet, alpha=0.5)



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
