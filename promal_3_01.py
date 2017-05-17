import matplotlib
matplotlib.use('TkAgg') # <-- THIS MAKES IT FAST!
import numpy as np  #to taka biblioteka z funkcjami numerycznymi jak tablice i inne takie tam
import matplotlib.pyplot as plt #to biblioteka pozwalajaca nam wykreslać wykresy

import pandas as pd

#importing our own library
from thermalModelLibrary import functionsLibrary as tml
from thermalModelLibrary import geometryLib as gml

from os import path


localDir = path.dirname(__file__)

# Odczytanie danych o ambient temp i krokaach czasu z pliku csv
plik = path.join(localDir, 'dataSrc/New_Promal_01.csv')
dfSrc = pd.read_csv(plik)
dfSrc = dfSrc.replace({',': '.'}, regex=True)
dfSrc = dfSrc.astype(float)

# zapamiętanie wektora czasu do późniejszego użycia
time = np.array(dfSrc['Time [s]'])
dfSrc.set_index('Time [s]', inplace=True)

print(dfSrc.head())

bar1 = ['CH1','CH2','CH3']
bar2 = ['CH4','CH5','CH6']
realAmb = ['CH7','CH8','CH9','CH10']

dfSrc['BAR 1'] = dfSrc[bar1].mean(axis=1)
dfSrc['BAR 2'] = dfSrc[bar2].mean(axis=1)
dfSrc['Real Ambient'] = dfSrc[realAmb].mean(axis=1)

listToDrop = bar1 + bar2 + realAmb

dfSrc = dfSrc.drop(listToDrop, axis=1)

# Preparation of the analysis
tx0 = 3570 # Starting time of cooling process

# HTC is based on the formula HTC = aHTC*(Tx-Ta)**0.25
aHTC = 1 # Heat Transfer coeff used in analysis
# aHTC = np.ones(time.size) * 2

# epsilov value for emissivity coeff used in radiation equation
# epsilon = np.ones(time.shape[0])*0.35 # Set to be a vector of timesize
epsilon = 0.4

# The current values vector is set to 0 as we dont heat by current
current = np.zeros(time.size)

# Setting up the analysis busbars sizes
wielkoscSzyn = ['30x800', '100x800']

# Temperature value for bars starting point of analysis
barStartTemp = 20

# Setting up the analysis ambient temperature
ambientTemp = np.array(dfSrc['Real Ambient'])

# #########################################################
# Main analysis calculations
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

# #########################################################

# Setting up the plot time range
start = 0
end = 10000

# Results postprocessing and preparing to display

# Gathering the analysis results and formatting it as dataframe
masterResultsArray = np.array(masterResultsArray)
np_array =[]

for x in range(masterResultsArray.shape[0]):
    for y in range(0,masterResultsArray.shape[2],2):
        np_array.append(masterResultsArray[x,:,y])
np_array = np.transpose(np_array)

df = pd.DataFrame(np_array)
df.columns = wielkoscSzyn
df.insert(0,'Ambient Temp',ambientTemp)
df.insert(0,'time[s]',time)
df = df.set_index('time[s]')

summary = dfSrc
for bar in wielkoscSzyn:
  summary[bar] = df[bar]

# ##################################################
# Result displays starts here
plt.style.use('bmh')

print(dfSrc.head())
print(df.head())

# dfSrc.plot()
# plt.ylabel('Temperature [$^o$C]')

# df.plot()
# plt.ylabel('Temperature [$^o$C]')

f2 = plt.figure('Analiza 2')
ax2 = f2.add_subplot(111)
ax2.set_title('Comaprison Analysis vs. Promal Data \n emissivity={} HTC={}'
              .format(epsilon, aHTC))


style=['-','-','-','--','--']
summary.plot(alpha=0.5, style=style, ax=ax2)
plt.ylabel('Temperature [$^o$C]')

plt.show()
