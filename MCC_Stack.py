# script file for thermal solver
# for performance measurement
from datetime import datetime
startTime = datetime.now()

import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
# import matplotlib.patches as patches
# from matplotlib.collections import PatchCollection
# import matplotlib as mpl

import numpy as np

from thermalModelLibrary import tntObjects as tntO
from thermalModelLibrary import tntSolverObj as tntS

# Defining some materials
Cu = tntO.Material()

# Defining some handy vellues
HTC = 6 * (135/105) * (108/105)
emmisivity = 0.35


# Defining analysis elements objects
SMB_21 = tntO.thermalElement(
        shape = tntO.shape(10,35,50,6,0),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

SMB_12 = tntO.thermalElement(
        shape = tntO.shape(10,30,50,4,0),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu) 

SMB_6 = tntO.thermalElement(
        shape = tntO.shape(10,30,50,2,0),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu) 

BB = tntO.thermalElement(
        shape = tntO.shape(20,35,25,1,-90),
        HTC = HTC,
        emissivity = emmisivity,
        material = Cu)

MD = tntO.thermalElement(
        shape = tntO.shape(10,20,30,1,0),
        HTC = HTC,
        emissivity = emmisivity,
        source = 0,
        dP = True,
        material = Cu)


# Defining the analysis circuit/objects connection stream

# using auto generator for input list based on tuples
MBB = [
        (SMB_12, 5)
        ]

MBB1 = tntS.generateList(MBB)

MBB = [
        (SMB_12, 15)
        ]

MBB2 = tntS.generateList(MBB)

vVBB = [
            (BB,20)
        ]

VBB1 = tntS.generateList(vVBB)
VBB2 = tntS.generateList(vVBB)
VBB3 = tntS.generateList(vVBB)
VBB4 = tntS.generateList(vVBB)

MOD = [
        (MD,10),
    ]

Mod1 = tntS.generateList(MOD)
Mod2 = tntS.generateList(MOD)
Mod3 = tntS.generateList(MOD)
Mod4 = tntS.generateList(MOD)

# preparing objects in list for solver
tntS.elementsForObjSolver(MBB1, 2000)
tntS.elementsForObjSolver(MBB2, 500)

tntS.elementsForObjSolver(VBB1, 1500)
tntS.elementsForObjSolver(Mod1, 400)

tntS.elementsForObjSolver(VBB2, 1100)
tntS.elementsForObjSolver(Mod2, 400)

tntS.elementsForObjSolver(VBB3, 700)
tntS.elementsForObjSolver(Mod3, 400)

tntS.elementsForObjSolver(VBB4, 300)
tntS.elementsForObjSolver(Mod4, 300)

# making connections
# VBB1[0].inputs.append(MBB1[-1])
tntS.joinNodes(MBB1, VBB1, -1)
# MBB2[0].inputs.append(MBB1[-1])
tntS.joinNodes(MBB1, MBB2, -1)

# VBB2[0].inputs.append(VBB1[-1])
tntS.joinNodes(VBB1, VBB2, -1)
# VBB3[0].inputs.append(VBB2[-1])
tntS.joinNodes(VBB2, VBB3, -1)
# VBB4[0].inputs.append(VBB3[-1])
tntS.joinNodes(VBB3, VBB4, -1)


# Mod1[0].inputs.append(VBB1[-1])
tntS.joinNodes(VBB1, Mod1, -1)
# Mod2[0].inputs.append(VBB2[-1])
tntS.joinNodes(VBB2, Mod2, -1)
# Mod3[0].inputs.append(VBB3[-1])
tntS.joinNodes(VBB3, Mod3, -1)
# Mod4[0].inputs.append(VBB4[-1])
tntS.joinNodes(VBB4, Mod4, -1)

# creating total list of all elements
Elements = []

Elements.extend(MBB1)
Elements.extend(MBB2)
Elements.extend(VBB1)
Elements.extend(VBB2)
Elements.extend(VBB3)
Elements.extend(VBB4)
Elements.extend(Mod1)
Elements.extend(Mod2)
Elements.extend(Mod3)
Elements.extend(Mod4)

# Filling elements positions
tntS.nodePosXY(Elements)



def calcThis(T0, Ta=20, Th=1, sort=True):
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
    A,B,s, L2, XY, air = tntS.Solver(Elements,0,Ta,T0,Th*60*60,500, 0.01, sort)

    # this returns:
    #  A vector of time for each step
    #  B array of temperature rises for each element in each step
    #  s the total number of solver iterations (not neccessary the same as number of timesteps!)
    #  L2 vector of positions in [mm] for each temperature calculations point (each object middle)
    #  XY - vector of 2D vectors of XY position of each node



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

    ax2.plot(b[-1,:],'rx--')
    ax2.set_title('Temp Rise vs. elements')
    plt.ylabel('Temp Rise [K]')
    plt.xlabel('nodes')

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

    figG = plt.figure('Geometry thermal map ')
    axG = figG.add_subplot(111, aspect='equal')
    tntS.drawElements(axG,Elements,np.array(b[-1,:]))

    plt.show()

    return B,t

def consT(y):
    return 20

def ambientT(y, T0 = 20):
    """
    y - in mmm
    output in degC
    """
    return T0 + y * (3/100)

B,t = calcThis(20, 20, 4, True)
