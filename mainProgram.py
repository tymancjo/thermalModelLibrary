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
time = np.arange(0, 60*10, 0.01)

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


for analiza in range(10,11,1):


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
                               HTC=25, Emiss=0.2,\
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

# temperatureDistributionAtTime
def tDAT(timeSample,analysis,xPositions,thermalResults):
    return xPositions[analysis], thermalResults[analysis][timeSample][:]

# fig = plt.figure('Summary')
# temperatureDistribution(300)
# plt.show()


# axis_color = 'grey'
# plt.style.use('fivethirtyeight')
#
# fig = plt.figure()
#
# # Draw the plot
# ax = fig.add_subplot(111)
# fig.subplots_adjust(left=0.25, bottom=0.25)
# ax.set_ylim([25, 145])
#
# startTimeSample = int(3/(time[1]-time[0]))
#
# segX = segmentsXpositionArray
# masR = masterResultsArray
# lenR = len(masR)-0.5 #zabezpieczenie przed przekroczeniem indeku maks
#
# [line] = ax.plot(tDAT(startTimeSample,0,segX, masR)[0],\
# tDAT(startTimeSample,0,segX, masR)[1])
#
# # Add two sliders for tweaking the parameters
# amp_slider_ax  = fig.add_axes([0.25, 0.15, 0.65, 0.03], facecolor=axis_color)
# amp_slider = Slider(amp_slider_ax, 'timeStep', 0, len(time)-1, valinit=startTimeSample)
#
# anl_slider_ax = fig.add_axes([0.25, 0.1, 0.65, 0.03], facecolor=axis_color)
# anl_slider = Slider(anl_slider_ax, 'Analiza', 0, lenR, valinit=0)
#
# ax.set_title('time='+str(round(time[int(amp_slider.val)],2))+\
# 's. BarSegments: '+str(segmentsArray[int(anl_slider.val)]))
#
# def sliders_on_changed(val):
#     line.set_xdata(tDAT(int(amp_slider.val),int(anl_slider.val),segX, masR)[0])
#     line.set_ydata(tDAT(int(amp_slider.val),int(anl_slider.val),segX, masR)[1])
#
#     ax.set_title('time='+str(round(time[int(amp_slider.val)],2))+\
#     's. BarSegments: '+str(segmentsArray[int(anl_slider.val)]))
#     fig.canvas.draw_idle()
#
# amp_slider.on_changed(sliders_on_changed)
# anl_slider.on_changed(sliders_on_changed)
#
#
# plt.show()
#
# fig = plt.figure()
# ax = fig.gca(projection='3d')
#
# # Make data.
# X = np.arange(0,len(segmentsXpositionArray[0]))
# Y = np.arange(0,len(time))
#
# X, Y = np.meshgrid(X, Y)
#
# # Plot the surface.masterResultsArray[analysis][timeSample][:]
# surf = ax.plot_surface(segmentsXpositionArray[0][X], time[Y], masterResultsArray[0][Y][X], cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)


plt.style.use('bmh')
fig, ax = plt.subplots()

Z = np.transpose(masterResultsArray[0])
print(Z.shape)

im = ax.imshow(Z, cmap='jet', aspect="auto",extent=[time[0],time[-1],\
segmentsXpositionArray[0][0],segmentsXpositionArray[0][-1]], interpolation='spline16')

ax.set_title('TimeSpace temperature distribution')
plt.ylabel('position [mm]')
plt.xlabel('time [s]')
fig.colorbar(im, orientation='vertical',label='Temperature [degC]')

plt.show()
