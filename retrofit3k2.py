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





# Defining analysis elements objects
T0=35
I = 3500

# defining the panel VBBs

# retrofit PC3200
PC_VBB =      [
                (el.VBB_F2_3k2, 900, 10), 
                (el.EG_F2, 200, 4),
                (el.VBB_F2_3k2, 200, 4), 
                (el.CT_2x100, 130, 3), 
                (el.VBB_F2_3k2, 200, 4), 
                ]

PC_VBB_rtf =    [
                (el.CT_3x100, 900, 10), 
                (el.EG_F2, 200, 4),
                (el.CT_3x100, 200, 4), 
                (el.CT_2x100, 130, 3), 
                (el.CT_3x100, 200, 4), 
                ]

PC_VBB_4kSTD =  [
                (el.CT_4x100, 900, 10), 
                (el.EG_F2_100, 200, 4),
                (el.CT_4x100, 200, 4), 
                (el.CT_3x100, 130, 3), 
                (el.CT_4x100, 200, 4), 
                ]

retrofit = copy.deepcopy(el.CT_4x100)
retrofit.rotate(0)

retrofit2 = copy.deepcopy(el.CT_4x100)
retrofit2.rotate(180)

PC_VBB_4kMOD =  [
                (el.CT_4x100, 900, 10), 
                (retrofit, 425, 5), 
                (el.EG_F2_100, 200, 4),
                (retrofit2, 425, 5), 
                (el.CT_4x100, 200, 4), 
                (el.CT_3x100, 130, 3), 
                (el.CT_4x100, 200, 4), 
                ]


PC3k = tntS.generateNodes(PC_VBB_rtf)
PC4k = tntS.generateNodes(PC_VBB_4kSTD)
PC4kRTF = tntS.generateNodes(PC_VBB_4kMOD)

bars = copy.deepcopy(el.CT_3x100)
bars.rotate(0)
MBB = tntS.generateNodes([(bars, 1000, 10)])

# making lineup & electrical solve
P = p.lineup(MBB, [(PC4k, 3700), (PC4kRTF,False)])

# printing currents just for check
for x in P:
    print('{}:{}:{}'.format(x.Iin,x.I,x.Iout))

# solving thermally
Time, T, Stp, Nodes = tntS.PanelSolver(P, T0, 5*60*60, 
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
