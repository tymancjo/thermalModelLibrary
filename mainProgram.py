#This is the main program script to use and test the library
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#importing our own library
from thermalModelLibrary import functionsLibrary as tml




# Definig the bar as segments of geometry
# the formula is for each ssegment
# [[SegmentHeight, SegmentThickness, SegmentLenght, CutoutHeight]]
# Cutout is assumed to be along entire segment lenght

copperBarGeometry = np.array([[30,10,170,0],[30,10,170,0],\
[1,1,1000,0],\
[100,10,72.5,0],[100,10,72.5,0]])

# end of Bar geometry definition

ResultsData = np.array(tml.mainAnalysis(analysisName='First Study',geometryArray=copperBarGeometry,\
timeArray=np.arange(0, 9980, 5), currentArray=np.ones(9980*2)*0, HTC=25, Emiss=0.2,\
ambientTemp=200, barStartTemperature=25,\
thermalConductivity=401, materialDensity=8920, materialCp=385))


tml.plotCurves(timeTable=np.arange(0, 9980, 5),dataArray=np.delete(ResultsData,[1,2,4],1),\
plotName='HTC=25.e=0.2',xLabel='time [s]',yLabel='Temperature [degC]',\
curvesLabelArray = ['30x10','100x10'])

plt.show()
