import matplotlib
matplotlib.use('Qt5Agg') # <-- THIS MAKES IT FAST!
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




# Zdefiniujmy sobie wektor czasu
time = np.arange(0, 60*1, 0.01)

#Zdefiniujmy funkcję opisująca prąd w czasie
def Icw(czas, czasMin,czasMax, iRMS):
    if czas <= czasMax and czas >= czasMin:
        return iRMS
    else:
        return 0

#Zwektoryzujmy nasza funkcję opisująca prąd (zapiszmy jako wektor)
Icw_vector = np.vectorize(Icw)
current = Icw_vector(time,15,30,5e3)


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
                                  [40,10,95,0],\
                                  [40,10,10,20],\
                                  [40,10,95,0],\
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





plt.style.use('bmh')
fig = plt.figure()


# title_font = {'fontname':'Arial', 'size':'11', 'color':'black', 'weight':'normal',
#               'verticalalignment':'bottom'} # Bottom vertical alignment for more space
# axis_font = {'fontname':'Arial', 'size':'10'}

title_font = { 'size':'11', 'color':'black', 'weight':'normal'} # Bottom vertical alignment for more space
axis_font = { 'size':'10'}


barSubPlot = fig.add_subplot(3,2,1)
prepareDrawCuShape(barGeometry=copperBarGeometry,barSubPlot=barSubPlot)
barSubPlot.set_title('Analyzed geometry', **title_font)
plt.ylabel('height [mm]', **axis_font)
plt.xlabel('lenght x [mm]', **axis_font)
plt.axis('scaled')

wykresIcwTime = fig.add_subplot(3,2,3)
wykresIcwTime.plot(time,current)
wykresIcwTime.set_xlim([time[0], time[-1]])
plt.ylabel('Current [A]', **axis_font)
plt.xlabel('Time [s]')

wykresTempTime = fig.add_subplot(3,2,5)
wykresTempTime.plot(time,masterResultsArray[0])
wykresTempTime.set_xlim([time[0], time[-1]])
plt.ylabel('Temperature [degC]', **axis_font)
#plt.xlabel('Time [s]')

#Z = np.transpose(masterResultsArray[0])
Z = masterResultsArray[0]
ax = fig.add_subplot(1,2,2)
im = ax.imshow(Z, cmap='jet', aspect="auto",extent=[\
segmentsXpositionArray[0][0],segmentsXpositionArray[0][-1],\
time[-1],time[0]], interpolation='spline16')
ax.set_title('TimeSpace temperature distribution', **title_font)
plt.xlabel('Position [mm]', **axis_font)
plt.ylabel('Time [s]', **axis_font)
fig.colorbar(im, orientation='horizontal',label='Temperature [degC]',alpha=0.5)#,\
#fraction=0.046, pad=0.2)
# fig.subplots_adjust(hspace = 0.3)

plt.tight_layout()
# plt.show()

y = np.arange(0,len(time),1)
x = np.arange(0,len(segmentsXpositionArray[0]))

fig = plt.figure()
ax = Axes3D(fig)
x, y = np.meshgrid(x, y)
p = ax.plot_surface(x, y, Z, rstride=40, cstride=1, cmap='jet', antialiased=True)
#cb = fig.colorbar(p, shrink=0.5)

plt.show()
