import matplotlib
import numpy as np  # to taka biblioteka z funkcjami numerycznymi jak macierze
import matplotlib.pyplot as plt  # to biblioteka pozwalajaca kreślić wykresy

# importing our own library
from thermalModelLibrary import functionsLibrary as tml


start = 0  # Start of analysis [s]

t1 = 60*60*8  # Start of overcurrent [s]
t_over = 60*60*2  # duratuion of overcurrent [s]

end = 60*60*12  # end of analysis [s]

# Setting up the analysis time vector [s]
time = np.arange(start, end+1, 1, dtype=float)

# Setting up current vector [A]:
current = np.ones(time.shape) * 3700
current[t1:t1+t_over] = 4000

# Setting up ambient temperature [deg C]
ambient_temperature = 40
starting_temperature = 40

copperBarGeometry = np.array([[(30 + 40), 30, 500, 0],
                             [(30 + 40), 30, 500, 0]])


copper_temperature = tml.mainAnalysis(analysisName='SMB-21 Thermal Study',
                                      geometryArray=copperBarGeometry,
                                      timeArray=time,
                                      currentArray=current,
                                      HTC=2.35, Emiss=0.35,
                                      ambientTemp=ambient_temperature,
                                      barStartTemperature=starting_temperature,
                                      thermalConductivity=401,
                                      materialDensity=8920,
                                      materialCp=385,
                                      HTCpow=0.25,
                                      HTClinterp=None)

copper_temperature = (copper_temperature[:, 0] + copper_temperature[:, 1]) / 2

plt.style.use('bmh')  # Style used for plots

f2 = plt.figure('SMB-21 Analysis')
ax1 = f2.add_subplot(211)
ax1.set_title('SMB-21 simulaiton [temperature $^o$C]')
ax1.plot(time, copper_temperature)
ax1.set_ylim([min(copper_temperature)-10, max(copper_temperature)+10])
plt.ylabel('Temperature [$^o$C]')

ax2 = f2.add_subplot(212)
ax2.set_title('SMB-21 simulaiton [current A]')
ax2.plot(time, current)
ax2.set_ylim([min(current)-100, max(current)+100])
plt.ylabel('Current rms [A]')

plt.tight_layout()
plt.show()
