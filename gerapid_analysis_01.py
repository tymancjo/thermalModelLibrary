import matplotlib
# matplotlib.use('Qt5Agg') # <-- THIS MAKES IT FAST!
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

def prepareDrawCuShape(barGeometry,barSubPlot):

    numberOfSegments = barGeometry.shape[0]
    #checking for max bar height in all segments
    #and set the center of bar position y
    yMax = np.max(barGeometry, axis=0)[0]
    centerY = yMax/2

    currentX = 0

    colourOfBar = '#f49b42'

    for i in range(0,numberOfSegments,1):
        # Ploting main coppershape of the segment
        currentY = centerY-barGeometry[i, 0]/2
        segment = plt.Rectangle((currentX, currentY),barGeometry[i, 2]\
        ,barGeometry[i, 0], fc=colourOfBar, linestyle='dashed',\
        edgecolor='grey')

        barSubPlot.add_patch(segment)

        if barGeometry[i, 3] != 0:
            # Drawing the hole in segment
            hole = plt.Rectangle((currentX, \
            currentY+(barGeometry[i, 0]/2)-(barGeometry[i, 3]/2)),\
            barGeometry[i, 2],barGeometry[i, 3], fc='w')
            barSubPlot.add_patch(hole)

        currentX += barGeometry[i, 2]

    barSubPlot.set_ylim([0, yMax])
    barSubPlot.set_xlim([0, currentX])

    return


#Zdefiniujmy funkcję opisująca prąd w czasie
def Icw(czas, czasMin,czasMax, iRMS):
    if czas <= czasMax and czas >= czasMin:
        return iRMS
    else:
        return 0

# Zdefiniujmy sobie wektor czasu
time = np.arange(0, 3*60*60, 0.5)

#Zwektoryzujmy nasza funkcję opisująca prąd (zapiszmy jako wektor)
Icw_vector = np.vectorize(Icw)
current = Icw_vector(time,0,time[-1],4000)

masterResultsArray = [] # Superzestaw wszytskich wyników
masterIndex = 0 # Indeks

tempMaxArray = []
segmentsArray = []
segmentsXpositionArray = []

wielkoscSzyn = [100]

for barHeight in wielkoscSzyn:


    copperBarGeometry = np.array([\
                                  [6,10,20,0],\
                                  [100,30,50,0],\
                                  [100,30,50,0],\
                                  [100,30,50,0],\
                                  [100,30,50,0],\
                                  [2*30,20,10,0],\
                                  [2*30,20,10,0],\
                                  [2*30,20,10,0],\
                                  [barHeight,20,50,0],\
                                  [barHeight,20,50,0],\
                                  [barHeight,20,50,0],\
                                  [barHeight,20,50,0],\
                                  ])

    # copperBarGeometry = gml.slicer(copperBarGeometry)

    print('Elementów szyny: '+str(len(copperBarGeometry)))

    masterResultsArray.append(tml.mainAnalysis(analysisName='Analiza dla szyny['+str(barHeight)+']',
                               geometryArray=copperBarGeometry,
                               timeArray=time,
                               currentArray=current,
                               HTC=3.75, Emiss=0.35,
                               ambientTemp=20, barStartTemperature=20,
                               thermalConductivity=401, materialDensity=8920,
                               materialCp=385, HTClinterp=None))



    # Zapiszmy sobie pozycje X posczegolnych segmentow
    temporatyXpositionArray = []
    totalXsoFar = 0.0

    for segment in range(len(copperBarGeometry)):
        totalXsoFar += float(copperBarGeometry[segment][2])/2
        temporatyXpositionArray.append(totalXsoFar)
        totalXsoFar += float(copperBarGeometry[segment][2])/2

    segmentsXpositionArray.append(temporatyXpositionArray)


    tempMaxArray.append(np.amax(masterResultsArray[masterIndex]))
    segmentsArray.append(len(copperBarGeometry))

    masterIndex +=1

def temperatureDistribution(timeSample):

    maxTemp = np.amax(tempMaxArray)
    minTemp = 25

    fig.suptitle("Comparison of temperatures along bar fot t="+str(time[timeSample])+"s")

    for analysis in range(len(masterResultsArray)):
        wykres = fig.add_subplot(3,1,2)
        wykres.plot(segmentsXpositionArray[analysis], masterResultsArray[analysis][timeSample][:])
        localMinmum = min(masterResultsArray[analysis][timeSample][:])
        localMaximum = max(masterResultsArray[analysis][timeSample][:])
        # wykres.set_title('Segments: '+str(segmentsArray[analysis]))
        # wykres.set_ylim([minTemp, maxTemp])
        wykres.set_ylim([localMinmum-5, localMaximum+5])
        wykres.set_xlim([0, 450])






plt.style.use('bmh')
fig = plt.figure()

title_font = { 'size':'11', 'color':'black', 'weight':'normal'} # Bottom vertical alignment for more space
axis_font = { 'size':'10'}


barSubPlot = fig.add_subplot(3,1,1)
prepareDrawCuShape(barGeometry=copperBarGeometry,barSubPlot=barSubPlot)
barSubPlot.set_title('Analyzed geometry', **title_font)
plt.ylabel('height [mm]', **axis_font)
plt.xlabel('lenght x [mm]', **axis_font)
# plt.axis('scaled')

wykresTempTime = fig.add_subplot(3,1,3)
for analiza in range(masterIndex):

    wykresTempTime.plot(time,masterResultsArray[analiza], label = 'szyna: '+str(wielkoscSzyn[analiza]))

wykresTempTime.set_xlim([time[0], time[-1]])
plt.ylabel('Temperature [degC]', **axis_font)
plt.xlabel('Czas [s]', **axis_font)




# wykresIcwTime = fig.add_subplot(3,1,2)
# wykresIcwTime.plot(time,current)
# wykresIcwTime.set_xlim([time[0], time[-1]])
# plt.ylabel('Current [A]', **axis_font)
# plt.xlabel('Time [s]')

# plt.xlabel('Time [s]')

# Z = np.transpose(masterResultsArray[0])
# Z = masterResultsArray[0]
# ax = fig.add_subplot(1,2,2)

# im = ax.imshow(Z, cmap='jet', aspect="auto",extent=[\
# segmentsXpositionArray[0][0],segmentsXpositionArray[0][-1],\
# time[-1],time[0]], interpolation='spline16')
# ax.set_title('TimeSpace temperature distribution', **title_font)
# plt.xlabel('Position [mm]', **axis_font)
# plt.ylabel('Time [s]', **axis_font)

# fig.colorbar(im, orientation='horizontal',label='Temperature [degC]',alpha=0.5,
#                 fraction=0.046, pad=0.2)
# fig.subplots_adjust(hspace = 0.3)

temperatureDistribution(-1)

plt.tight_layout()
plt.show()
