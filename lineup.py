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
from thermalModelLibrary import panels as p




# Defining analysis elements objects
T0=35
I = 3500

# making lineup & electrical solve
P = p.lineup(p.SMB21, [(p.VBB1600, 1000), (p.VBB4000, False),(p.VBB2000, 1700),(p.VBB1600, 900)])

# printing currents just for check
for x in P:
    print('{}:{}:{}'.format(x.Iin,x.I,x.Iout))

# solving thermally
Time, T, Stp, Nodes = tntS.PanelSolver(P, T0, 2*60*60, 
                iniTimeStep = 1,
                tempStepAccuracy = 0.1)


# Plotting results
b = np.array(T)
b = b - T0

figG = plt.figure('Geometry thermal map ')
axG = figG.add_subplot(111, aspect='equal')
tntS.drawElements(axG,Nodes,np.array(b[-1,:]), Text=True, T0=T0)

plt.show()
