# script file for thermal solver

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolver as tntS

Gerapid = tntO.thermalElement(
        shape = tntO.shape(10,10,10),
        HTC = 0,
        emissivity = 0,
        dP = False,
        source = 90)

Terminal = tntO.thermalElement(
        shape = tntO.shape(30,100,200),
        HTC = 15,
        emissivity = 0)

Connection = tntO.thermalElement(
        shape = tntO.shape(2 * 28,28,20),
        HTC = 0,
        emissivity = 0)



BB = tntO.thermalElement(
        shape = tntO.shape(10,4*100,1000),
        HTC = 15,
        emissivity = 0)

Elements = [Gerapid, Terminal, Connection, BB]

A,B = tntS.Solver(Elements,4000,20,20,8*60*60,100, 0.025)


# Just to have 1st dimensional reference 
l = [element.shape.l for element in Elements]
L = [sum(l[1:x]) for x in range(1,len(l)+1)]

t = np.array(A)
t = t / (60*60)

b = np.array(B)
b = b - 20

print('Solution steps: {}'.format(len(t)))

plt.plot(t,b[:,0],'r',label="Gerapid")
plt.plot(t,b[:,1],'b', label="Terminal")
plt.plot(t,b[:,2],'y', label="Connections")
plt.plot(t,b[:,3],'g', label="Busbar")

plt.ylabel('Temp Rise [K]')
plt.xlabel('Time [h]')

plt.legend()
plt.show()
