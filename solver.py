# script file for thermal solver

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolver as tntS

# Defining some materials
Cu = tntO.Material(alpha=0)
alteredCu = tntO.Material(thermalConductivity = 1e6)

# Defining some handy vellues
HTC = 5

Gerapid = tntO.thermalElement(
        shape = tntO.shape(10,10,10),
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

Connection = tntO.thermalElement(
        shape = tntO.shape(28,28,20,2),
        HTC = HTC,
        emissivity = 0,
        material = Cu)


BB = tntO.thermalElement(
        shape = tntO.shape(10,100,300,4),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

Elements = [Gerapid, Terminal, Connection, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB]

A,B,s, L2 = tntS.Solver(Elements,4000,20,20,4*60*60,500, 0.01)


# Just to have 1st dimensional reference for positions
#pos = [ 1000 * (0.5*Elements[x-1].shape.l + 0.5*Elements[x].shape.l) for x in range(1, len(Elements))]
#pos.insert(0,Elements[0].shape.l/2)
#L2 = [sum(pos[0:x]) for x in range(1,len(pos)+1)]



t = np.array(A)
t = t / (60*60)

b = np.array(B)
b = b - 20



fig = plt.figure('SMB-21')

ax1 = fig.add_subplot(211)

ax1.plot(t,b[:,0],'r',label="Gerapid")
ax1.plot(t,b[:,1],'b', label="Terminal")
ax1.plot(t,b[:,2],'y', label="Connections")
ax1.plot(t,b[:,3:],'g')

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


plt.tight_layout()
plt.show()


