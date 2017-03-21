import numpy as np  #to taka biblioteka z funkcjami numerycznymi jak tablice i inne takie tam
import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy
from scipy.interpolate import spline
from scipy.interpolate import InterpolatedUnivariateSpline

from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.animation as animation

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

#importing our own library
from thermalModelLibrary import functionsLibrary as tml
from thermalModelLibrary import geometryLib as gml

# Zdefiniujmy sobie wektor czasu
time = np.arange(0, 60*1, 0.01)

#Zdefiniujmy funkcję opisująca prąd w czasie
def Icw(czas, czasMax, iRMS):
    if czas <= czasMax:
        return iRMS
    else:
        return 0

#Zwektoryzujmy nasza funkcję opisująca prąd (zapiszmy jako wektor)
Icw_vector = np.vectorize(Icw)
current = Icw_vector(time,3,25e3)


masterResultsArray = [] # Superzestaw wszytskich wyników
masterIndex = 0 # Indeks

tempMaxArray = []
segmentsArray = []
segmentsXpositionArray = []


for analiza in range(5,6,1):


    copperBarGeometry = np.array([\
                                  [40,10,10,0],\
                                  [40,10,15,14],\
                                  [40,10,15-analiza,0],\
                                  [40,10,200,0],\
                                  [40,10,15-analiza,0],\
                                  [40,10,15,14],\
                                  [40,10,10,0],\
                                  ])
    #if masterIndex > 0:
    copperBarGeometry = gml.slicer(copperBarGeometry)

    print('Elementów szyny: '+str(len(copperBarGeometry)))

    masterResultsArray.append(tml.mainAnalysis(analysisName='Analiza ['+str(analiza)+']',\
                               geometryArray=copperBarGeometry,\
                               timeArray=time,\
                               currentArray=current,\
                               HTC=250, Emiss=0.8,\
                               ambientTemp=25, barStartTemperature=25,\
                               thermalConductivity=401, materialDensity=8920, materialCp=385))



    # Zapiszmy sobie pozycje X posczegolnych segmentow

    temporatyXpositionArray = []
    totalXsoFar = 0.0

    for segment in range(len(copperBarGeometry)):
        totalXsoFar += float(copperBarGeometry[segment][2])/2
        temporatyXpositionArray.append(totalXsoFar)
        totalXsoFar += float(copperBarGeometry[segment][2])/2

    segmentsXpositionArray.append(temporatyXpositionArray)


    # tml.plotCurves(timeTable=time,\
    #           dataArray=masterResultsArray[masterIndex],\
    #           plotName='Symulacja'+str(analiza),xLabel='time [s]',yLabel='Temperature [degC]',\
    #           curvesLabelArray = False)


    tempMaxArray.append(np.amax(masterResultsArray[masterIndex]))
    segmentsArray.append(len(copperBarGeometry))

    masterIndex +=1

def temperatureDistribution(timeSample):

    maxTemp = np.amax(tempMaxArray)
    minTemp = 25

    fig.suptitle("Comparison of temperatures along bar fot t="+str(time[timeSample])+"s")

    for analysis in range(len(masterResultsArray)):
        wykres = fig.add_subplot(3,1+int(len(masterResultsArray)/3),analysis+1)
        wykres.plot(segmentsXpositionArray[analysis], masterResultsArray[analysis][timeSample][:])
        wykres.set_title('Segments: '+str(segmentsArray[analysis]))
        wykres.set_ylim([minTemp, maxTemp])



Z = np.transpose(masterResultsArray[0])


plt.style.use('bmh')
fig = plt.figure()

ax = fig.add_subplot(2,1,1)
im = ax.imshow(Z, cmap='jet', aspect="auto",extent=[time[0],time[-1],\
segmentsXpositionArray[0][0],segmentsXpositionArray[0][-1]], interpolation='spline16')
ax.set_title('TimeSpace temperature distribution')
plt.ylabel('Position [mm]')
plt.xlabel('Time [s]')
fig.colorbar(im, orientation='horizontal',label='Temperature [degC]',alpha=0.5,\
fraction=0.046, pad=0.2)

wykres = fig.add_subplot(2,1,2)
wykres.plot(time,masterResultsArray[0])
wykres.set_xlim([time[0], time[-1]])
plt.ylabel('Temperature [degC]')
plt.xlabel('Time [s]')

plt.show()
