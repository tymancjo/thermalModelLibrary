# script file for thermal solver
# for performance measurement
from datetime import datetime
startTime = datetime.now()

import matplotlib.pyplot as plt 
import matplotlib as mpl
import numpy as np

import copy

# from thermalModelLibrary import tntObjects as tntO
# from thermalModelLibrary import tntPanel as tntP
from thermalModelLibrary import elements as el

from thermalModelLibrary import panels as p

from thermalModelLibrary import tntPanelsSolver as tntS
from thermalModelLibrary import tntPanel as tntP





# Defining analysis elements objects
T0=25

v2bel = copy.deepcopy(el.VBB_F2_2k5)
v2bel.rotate(180)
# MBBs

MBB1 = tntS.generateNodes([(el.SMB_21, 800, 11)])
MBB2 = tntS.generateNodes([(el.SMB_21, 800, 11)])

# defining the panel VBBs
# 2xACB 2500
V1      =      [(el.VBB_F2_2k5, 350, 5)]
V2      =      [(el.VBB_F2_2k5, 500, 8),(v2bel, 200, 4)]
V3      =      [(el.VBB_F2_2k5, 350, 5)]
V4      =      [(el.VBB_F2_2k5, 200, 4), 
                (el.CT_1x100, 130, 3), 
                (el.VBB_F2_2k5, 200, 4)]

#  ACB's
acbTop = copy.deepcopy(el.EG_F2)
acbTop.HTC = 2

acbBtm = copy.deepcopy(el.EG_F2)
acbBtm.HTC = 10

ACB1 = [(acbTop, 200, 4)]
ACB2 = [(acbBtm, 200, 4)]
                
# Generating the proper elements list

mbb1a = MBB1[:6]
mbb1b = MBB1[6:]

mbb2a = MBB2[:6]
mbb2b = MBB2[6:]

v1 = tntS.generateNodes(V1)
v2 = tntS.generateNodes(V2)
v3 = tntS.generateNodes(V3)
v4 = tntS.generateNodes(V4)

acb1 = tntS.generateNodes(ACB1)
acb2 = tntS.generateNodes(ACB2)

# making in list connections
tntP.prepareNodes(mbb1a)
tntP.prepareNodes(mbb1b)
tntP.prepareNodes(mbb2a)
tntP.prepareNodes(mbb2b)
tntP.prepareNodes(v1)
tntP.prepareNodes(v2)
tntP.prepareNodes(v3)
tntP.prepareNodes(v4)
tntP.prepareNodes(acb1)
tntP.prepareNodes(acb2)

# setting currents for each part
I1 = 2100
I2 = 1600

tntP.setCurrent(mbb1b, I1)
tntP.setCurrent(v1, I1)
tntP.setCurrent(acb1, I1)
tntP.setCurrent(v2, I1)

tntP.setCurrent(mbb2a, I1 + I2)

tntP.setCurrent(v3, I2)
tntP.setCurrent(acb2, I2)
tntP.setCurrent(v4, I2)



# Making connections
tntS.joinNodes(mbb1a, mbb1b, -1)
tntS.joinNodes(mbb2a, mbb2b, -1)

tntS.joinNodes(mbb1a, v1, -2)
tntS.joinNodes(v1, acb1, -1)
tntS.joinNodes(acb1, v2, -1)
tntS.joinNodes(v2, acb2, -1)
tntS.joinNodes(acb2, v4, -1)

tntS.joinNodes(mbb2a, v3, -2)
tntS.joinNodes(v3, acb2, -1)

#  some placement xy fixes
mbb2a[0].x = -800
mbb2a[0].y = -4*160 + 0
# Preparing one summary list
Nodes = []

Nodes.extend(mbb1a)
Nodes.extend(mbb1b)
Nodes.extend(v1)
Nodes.extend(acb1)
Nodes.extend(v2)
Nodes.extend(mbb2a)
Nodes.extend(mbb2b)
Nodes.extend(v3)
Nodes.extend(acb2)
Nodes.extend(v4)

#  making the Panel object
P = tntP.AnyPanel(Nodes= Nodes,
                  In=mbb1a[0],
                  Out=mbb2b[-1],
                  AirSort=1)



# Filling elements positions
# tntS.nodePosXY(Nodes)


# solving thermally
Time, T, Stp, Nodes = tntS.PanelSolver([P], T0, 5*60*60, 
                iniTimeStep = 1,
                tempStepAccuracy = 0.1)



# Plotting results
b = np.array(T)
b = b - T0

t = np.array(Time) / (60*60)

figG = plt.figure('Geometry thermal map ')
axG = figG.add_subplot(111, aspect='equal')
tntS.drawElements(axG,Nodes,np.array(b[-1,:]), Text=True, T0=T0)

figT = plt.figure('Time rise curves')
axT = figT.add_subplot(111)
axT.plot(t, b)

plt.show()
