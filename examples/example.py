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


# Defining analysis elements objects
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
        shape = tntO.pipe(30,12.5,20,2),
        HTC = HTC,
        emissivity = 0,
        material = Cu)


BB = tntO.thermalElement(
        shape = tntO.shape(10,100,300,4),
        HTC = HTC,
        emissivity = 0,
        material = Cu)

# Defining the analysis circuit/objects connection stream
Elements = [Gerapid, Terminal, Connection, BB, BB, BB, BB, BB, BB, BB, BB, BB, BB]

# Running the solver for
# Geometry from Elements list
# 4000 A
# 20 degC ambient
# 20 degC starting temperature
# 4h analysis end time
# 500s as the default and max timestep size - this is auto reduced when needed - see tntS.Solver object
# 0.01K maximum allowed temperature change in single timestep - otherwise solution accuracy - its used for auto timestep selection 
A,B,s, L2 = tntS.Solver(Elements,4000,20,20,4*60*60,500, 0.01)

# this returns:
#  A vector of time for each step
#  B array of temperature rises for each element in each step
#  s the total number of solver iterations (not neccessary the same as number of timesteps!)
#  L2 vector of positions in [mm] for each temperature calculations point (each object middle)

# Rest is just cleaning up data for plotting
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


