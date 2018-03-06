# script file for thermal solver
# for performance measurement
from datetime import datetime
startTime = datetime.now()

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
# import matplotlib.patches as patches
# from matplotlib.collections import PatchCollection
# import matplotlib as mpl
import numpy as np
# import math

# import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolverObj as tntS

# Defining some materials
Cu = tntO.Material()
CuACB = tntO.Material(conductivity=5e6)
alteredCu = tntO.Material(thermalConductivity=100)

# Defining some handy vallues
# IP42 parameters 
HTC = 6
emmisivity = 0.35

# Enviroment and starting point
Tambient = 20


# Defining analysis elements objects
ACB = tntO.thermalElement(
        shape = tntO.shape(20,100,230/4,1,90),
        HTC = HTC,
        emissivity = emmisivity,
        dP = True,
        source = 0,
        material = CuACB)

zwora = tntO.thermalElement(
        shape = tntO.shape(10,40,25,1,90),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

VBB = tntO.thermalElement(
        shape = tntO.shape(10,40,25,4,90),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

BottomVBB = tntO.thermalElement(
        shape = tntO.shape(10,40,25,4,15),
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
        shape = tntO.shape(10,40,25,4,180 - 15),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

# Defining the analysis circuit/objects connection stream
Elements =      [
                (zwora, 4),
                (VBB, 10),
                (BottomVBB, 20),
                (VBB, 10),
                (Connection, 1),
                (ACB, 4),
                (Connection2, 1),
                (TopVBB, 20),
                (VBB, 20)
                ]

Elements = tntS.generateList(Elements) 
# Filling the element.inputs and element.output lists
tntS.elementsForObjSolver(Elements) 
# Filling elements positions
tntS.nodePosXY(Elements)

def calcThis(T0, Ta=20, Th=1):
    """
    Inputs:
        T0 - initial temperature, will be ignored if elements aready have internal temp
        Ta - ambient temperature as value or function of height Tamb = f(y[mm])
        Th - analysis time [h]

    Output:
        B,t
            B - array of temperatures for eachTimestep and element
            t - vector of time
    """
    
    # Running the solver for
    # Geometry from Elements list
    # 4000 A
    # 20 degC ambient
    # 20 degC starting temperature
    # 4h analysis end time
    # 500s as the default and max timestep size - this is auto reduced when needed - see tntS.Solver object
    # 0.01K maximum allowed temperature change in single timestep - otherwise solution accuracy - its used for auto timestep selection 
    A,B,s, L2, XY, air = tntS.Solver(Elements,2500,Ta,T0,Th*60*60,500, 0.01)

    # this returns:
    #  A vector of time for each step
    #  B array of temperature rises for each element in each step
    #  s the total number of solver iterations (not neccessary the same as number of timesteps!)
    #  L2 vector of positions in [mm] for each temperature calculations point (each object middle)
    #  XY - vector of 2D vectors of XY position of each node


    print('execution time: ', datetime.now() - startTime)
    print('time steps: ', len(A))
    print('solver steps: ', s)
    print('thermal nodes: ', len(Elements))


    # Rest is just cleaning up data for plotting
    t = np.array(A)
    t = t / (60*60) # Time in hours

    # preparing tem rises as results
    b = np.array(B)
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

    ax2.plot(L2,b[-1,:],'rx--')
    ax2.set_title('Temp Rise vs. 1D position')
    plt.ylabel('Temp Rise [K]')
    plt.xlabel('Position [mm]')

    ax1.grid()
    ax2.grid()

    # Defining the subplot for geometry heat map
    ax3 = fig.add_subplot(132, aspect='equal')
    # runs the defined procedure on this axis
    boxes = tntS.drawElements(ax3,Elements,np.array(b[-1,:]))

    ax4 = fig.add_subplot(133)
    if air:
        ax4.plot(air.aCellsT, np.linspace(0,air.h,air.n) ,'b--')
    else:
        ax4.plot(np.array([Ta(y) for y in np.linspace(0,max(L2),20)]), np.linspace(0,max(L2),20) ,'b--')

    ax4.set_title('Air Temp vs. height')
    plt.xlabel('Air Temp [degC]')
    plt.ylabel('Height [mm]')

    plt.tight_layout()
    plt.show()

    return B,t

# Function that describe ambient change with height
def ambientT(y, Q=0, T0 = 20):
    """
    y - in mmm
    output in degC
    """
    return T0 + y * (3/100)

def consT(y):
    return 20

B,t = calcThis(20, 20, 4)