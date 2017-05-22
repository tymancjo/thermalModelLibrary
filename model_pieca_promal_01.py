import matplotlib
import numpy as np  # to taka biblioteka z funkcjami numerycznymi jak macierze
import matplotlib.pyplot as plt  # to biblioteka pozwalajaca kreślić wykresy
import pandas as pd

# importing our own library
from thermalModelLibrary import functionsLibrary as tml
# from thermalModelLibrary import geometryLib as gml

from os import path
matplotlib.use('TkAgg')  # <-- THIS MAKES IT FAST!


localDir = path.dirname(__file__)

# Odczytanie danych o ambient temp i krokaach czasu z pliku csv
plik = path.join(localDir, 'dataSrc/New_Promal_01.csv')
dfSrc = pd.read_csv(plik)
dfSrc = dfSrc.replace({',': '.'}, regex=True)
dfSrc = dfSrc.astype(float)

# zapamiętanie wektora czasu do późniejszego użycia
time = np.array(dfSrc['Time [s]'])
print(time)
dfSrc.set_index('Time [s]', inplace=True)
# print(dfSrc.head())

# dfSrc.plot()
# plt.ylabel('Temperature [$^o$C]')

bar1 = ['CH1', 'CH2', 'CH3']
bar2 = ['CH4', 'CH5', 'CH6']
realAmb = ['CH7', 'CH8', 'CH9', 'CH10']

dfSrc['BAR 30x800 (promal)'] = dfSrc[bar1].mean(axis=1)
dfSrc['BAR 100x800 (promal)'] = dfSrc[bar2].mean(axis=1)
dfSrc['Ambient [$^o$C]'] = dfSrc[realAmb].mean(axis=1)

listToDrop = bar1 + bar2 + realAmb

dfSrc = dfSrc.drop(listToDrop, axis=1)

# Preparation of the analysis
tx0 = 4300  # Starting time of cooling process

# Setting up the plot time range
start = 0
end = 5000
time = np.arange(start, end+1, 1, dtype=float)

# HTC is based on the formula HTC = aHTC*(Tx-Ta)**HTCpow
aHTC = 5  # Heat Transfer coeff used in analysis
# aHTC = np.ones(time.size) * 2
HTCpow = 0.1

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
# ambientTemp = np.array(dfSrc['Ambient [$^o$C]'])
ambientTemp = np.ones(time.size) * 20
ambientTemp[20:150] = np.linspace(20, 170, 150-20)
ambientTemp[150:1000] = np.linspace(170, 240, 1000-150)
# ambientTemp[1000:1200] = 240
ambientTemp[1000:2900] = np.linspace(240, 200, 2900-1000)

ambientTemp[2900:tx0] = 200
ambientTemp[tx0:end] = 20


def analysis(HTC, HTCpow, HTClinterp, emiss):
    # #########################################################
    # Main analysis calculations

    masterResultsArray = []  # Superzestaw wszytskich wyników
    # masterIndex = 0  # Indeks

    # tempMaxArray = []
    # segmentsArray = []
    # segmentsXpositionArray = []

    for bar in wielkoscSzyn:

        bH = float(bar.split('x')[0])
        bL = float(bar.split('x')[1])

        copperBarGeometry = np.array([
                                      [bH, 10, bL-10, 0],
                                      [bH, 10, 10, 0],
                                      ])
        print('Elementów szyny: '+str(len(copperBarGeometry)))

        masterResultsArray.append(tml.mainAnalysis(
                                  analysisName='Analiza dla szyny[{}]'
                                  .format(bar),
                                  geometryArray=copperBarGeometry,
                                  timeArray=time,
                                  currentArray=current,
                                  HTC=HTC, Emiss=emiss,
                                  ambientTemp=ambientTemp,
                                  barStartTemperature=barStartTemp,
                                  thermalConductivity=401,
                                  materialDensity=8920,
                                  materialCp=385,
                                  HTCpow=HTCpow,
                                  HTClinterp=HTClinterp))
    return masterResultsArray
    # #########################################################

# Running the analysis procedure

epsilon = 0.35

aHTC = np.ones(time.size) * 1
aHTC[tx0:] = 0.50
# aHTC = 10  # Just in case we need one static value
HTCpow = 0.25
HTClinterp = [-0.009, 1.9]

masterResultsArray = analysis(aHTC, HTCpow, HTClinterp, epsilon)


# Results postprocessing and preparing to display

# Gathering the analysis results and formatting it as dataframe
masterResultsArray = np.array(masterResultsArray)
np_array = []

for x in range(masterResultsArray.shape[0]):
    for y in range(0, masterResultsArray.shape[2], 2):
        np_array.append(masterResultsArray[x, :, y])
np_array = np.transpose(np_array)

df = pd.DataFrame(np_array)
df.columns = wielkoscSzyn
df.insert(0, 'Ambient Temp', ambientTemp)
df.insert(0, 'time[s]', time)
df = df.set_index('time[s]')

summary = dfSrc
# Comment below line if you dont want real measurement data in plot
summary = pd.DataFrame()
for bar in wielkoscSzyn:
    summary[bar] = df[bar]
summary['TurbulanceRatio [%]'] = np.array(aHTC) * 100
summary['Analysis Ambient [$^o$C]'] = ambientTemp
# summary['dT 30x800 [K]'] = summary['30x800'] - max(summary['30x800'])
# summary['dT 100x800 [K]'] = summary['100x800'] - max(summary['100x800'])


# ##################################################
# Result displays starts here
plt.style.use('bmh')

print(dfSrc.head())
print(df.head())

# df.plot()
# plt.ylabel('Temperature [$^o$C]')

f2 = plt.figure('Analiza 2')
ax2 = f2.add_subplot(111)
ax2.set_title('Comaprison Analysis vs. Promal Data \n \
               emissivity={} \n HTC=TurbulanceRatio*BarHeight*{}*(DT)^{}\n'
              .format(epsilon, HTClinterp, HTCpow))

style = ['-', '-', '-', '--', '--', '--', '.-']
summary[start:end].plot(alpha=0.5, style=style, ax=ax2)
plt.ylabel('Temperature [$^o$C]')

# Plotting additional lines every 10s since tx0
for i in range(10):
    ax2.axvline(x=tx0 + i * 10, ls='--', linewidth=1, color='red', alpha=0.25)

for i in range(7):
    ax2.axvline(x=0 + i * 900, ls=':', linewidth=1, color='green', alpha=0.5)


plt.tight_layout()
plt.show()
