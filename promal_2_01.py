import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!
import numpy as np  #to taka biblioteka z funkcjami numerycznymi jak tablice i inne takie tam
import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy

# from scipy.interpolate import spline
# from scipy.interpolate import InterpolatedUnivariateSpline

from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.animation as animation

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

import pandas as pd

#importing our own library
from thermalModelLibrary import functionsLibrary as tml
from thermalModelLibrary import geometryLib as gml

from os import path


localDir = path.dirname(__file__)

# Odczytanie danych o ambient temp i krokaach czasu z pliku csv

plik = path.join(localDir, 'dataSrc/Promal_test2_round_01.csv')
dfSrc = pd.read_csv(plik)
dfSrc = dfSrc.replace({',': '.'}, regex=True)
dfSrc.drop(['Date', 'hour'], axis=1, inplace=True)
dfSrc = dfSrc.astype(float)
time = np.array(dfSrc['[s]'])

dfSrc.set_index('[s]', inplace=True)

wielkoscSzyn = ['30x500', '40x500', '80x300', '100x100']

HTC = np.array([10, 4, 100, 30, 20])

tx0 = 400
tx1 = 2425  # czas wyjazdu z pieca
tx2 = 2445
tx3 = 2350

# Zakres czasu kreslenia
start = 0
end = 2500

aHTC = np.ones(time.shape[0])*HTC[1]
aHTC[:tx0] = np.linspace(start=HTC[0], stop=HTC[1], num=np.where(time==tx0)[0])
aHTC[tx1:tx2]=np.linspace(start=HTC[2], stop=HTC[3],num=np.where(time==tx2)[0]-np.where(time==tx1)[0])
# aHTC[np.where(time==tx2)[0]:]=HTC[4]
aHTC[tx2:]=np.linspace(start=HTC[3], stop=HTC[4],num=len(time)-np.where(time==tx2)[0])

epsilon = np.ones(time.shape[0])*0.35
# epsilon[np.where(time==tx1)[0]:]=0.4

dfSrc['HTC'] = aHTC

ambientTemp=np.ones(time.shape[0])*190
ambientTemp[:tx0]=np.linspace(start=50, stop=190, num=np.where(time==tx0)[0])
ambientTemp[tx1:]=19

ambientTemp = dfSrc['CH10']
barStartTemp = ambientTemp[0]

dfSrc.rename(columns={'CH10': 'Real Ambient'}, inplace=True)
dfSrc['Analysis Ambient'] = ambientTemp


# Zerowy wektor prądu
current = np.zeros(time.size)


masterResultsArray = [] # Superzestaw wszytskich wyników
masterIndex = 0 # Indeks

tempMaxArray = []
segmentsArray = []
segmentsXpositionArray = []


for bar in wielkoscSzyn:

    bH = float(bar.split('x')[0])
    bL = float(bar.split('x')[1])

    copperBarGeometry = np.array([\
                                  [bH,10,bL-10,0],\
                                  [bH,10,10,0],\
                                  ])
    print('Elementów szyny: '+str(len(copperBarGeometry)))

    masterResultsArray.append(tml.mainAnalysis(
                              analysisName='Analiza dla szyny[{}]'.format(bar),
                              geometryArray=copperBarGeometry,
                              timeArray=time,
                              currentArray=current,
                              HTC=aHTC, Emiss=epsilon,
                              ambientTemp=ambientTemp,
                              barStartTemperature=barStartTemp,
                              thermalConductivity=401,
                              materialDensity=8920,
                              materialCp=385))



plt.style.use('bmh')


title_font = { 'size':'11', 'color':'black', 'weight':'normal'} # Bottom vertical alignment for more space
axis_font = { 'size':'10'}


masterResultsArray = np.array(masterResultsArray)


np_array =[]
for x in range(masterResultsArray.shape[0]):
    for y in range(0,masterResultsArray.shape[2],2):
        np_array.append(masterResultsArray[x,:,y])

np_array = np.transpose(np_array)

df = pd.DataFrame(np_array)
df.columns = wielkoscSzyn
df.insert(0,'time[s]',time)
df = df.set_index('time[s]')



summaryDf = pd.concat([dfSrc,df],axis=1,)
realLife = ['CH{}'.format(index) for index in range(1,10)]
summaryDf['RealLifeAver']=summaryDf[realLife].mean(axis=1)

analysisLife = wielkoscSzyn
summaryDf['AnalysisAver']=summaryDf[analysisLife].mean(axis=1)

realLife = analysisLife + realLife
# new data frame with the particular bars

barsDf = summaryDf[realLife]
barsDf.insert(0,'time[s]',time)
barsDf.set_index('time[s]', inplace=True)


summaryDf = summaryDf.drop(realLife, axis=1)
print(summaryDf.head())



dataTimeStart = np.where(time == start)[0][0]
if end > len(time):
    dataMaxNum = len(time)
else:
    dataMaxNum = end


# dfSrc.plot()
f1 = plt.figure('Analiza 1')
ax1 = f1.add_subplot(111)
ax1.set_title('HTC='+str(HTC)+'[$\\frac{W}{m^2K}$] emiss='+str(epsilon[0])+' ', **title_font)

style=['','o-','o-','','o-','']
summaryDf.iloc[dataTimeStart:dataMaxNum].plot(ax=ax1, style=style, alpha=0.25)

for i in range(10):
    ax1.axvline(x=tx1 + i * 10, ls='--', linewidth=1, color='red')

f2 = plt.figure('Analiza 2')
ax2 = f2.add_subplot(111)
ax2.set_title('HTC='+str(HTC)+'[$\\frac{W}{m^2K}$] emiss='+str(epsilon[0])+' ', **title_font)

for i in range(10):
    ax2.axvline(x=tx1 + i * 10, ls='--', linewidth=1, color='red')

style=['o-','o-','o-','o-']
barsDf.iloc[dataTimeStart:dataMaxNum].plot(ax=ax2, style=style, alpha=0.25)


plt.ylabel('Temperature [$^o$C]', **axis_font)
plt.show()
