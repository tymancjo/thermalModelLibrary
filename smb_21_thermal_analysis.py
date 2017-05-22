import matplotlib
import numpy as np  # to taka biblioteka z funkcjami numerycznymi jak macierze
import matplotlib.pyplot as plt  # to biblioteka pozwalajaca kreślić wykresy

# importing our own library
from thermalModelLibrary import functionsLibrary as tml

start = 0
end = 60*60*14


def smb_analysis(start=start, t1=60*60*8, dt_over=60*60*2, end=end,
                 norm_load_curr=4020, over_current=4020,
                 ambient=35, starting_temperature=35,
                 bars_h=30+40, bars_n=3):

    # Setting up the analysis time vector [s]
    time = np.arange(start, end+1, 1)

    # Setting up current vector [A]:
    current = np.ones(time.shape) * norm_load_curr
    current[t1:t1+dt_over] = over_current

    copperBarGeometry = np.array([[bars_h, bars_n * 10, 500, 0],
                                 [bars_h, bars_n * 10, 500, 0]])

    copper_temperature = tml.mainAnalysis(analysisName='SMB-21 Thermal Study',
                                          geometryArray=copperBarGeometry,
                                          timeArray=time,
                                          currentArray=current,
                                          HTC=2.33, Emiss=0.35,
                                          ambientTemp=ambient,
                                          barStartTemperature=starting_temperature,
                                          thermalConductivity=401,
                                          materialDensity=8920,
                                          materialCp=385,
                                          HTCpow=0.25,
                                          HTClinterp=None)

    copper_temperature = (copper_temperature[:, 0] + copper_temperature[:, 1]) / 2
    ambient = np.ones(time.size) * ambient
    return time, current, ambient, copper_temperature
# ##############################################################

time, current, ambient, copper_temperature = smb_analysis()

time2, current2, ambient2, copper_temperature2 = smb_analysis(norm_load_curr=3700,
                                                              over_current=4000,
                                                              ambient=40,
                                                              starting_temperature=40)
plt.style.use('bmh')  # Style used for plots

time_ticks = [x for x in range(int(time[0]), int(time[-1]+2*60*60), 60*60)]
time_labels = ['{}'.format(x // (60*60)) for x in time_ticks]

f2 = plt.figure('SMB-21')

ax1 = f2.add_subplot(221)
ax1.set_title('SMB-21 simulaiton 35$^o$C / 3700')
ax1.plot(time, copper_temperature, time, ambient)
ax1.set_ylim([min(copper_temperature)-10, max(copper_temperature)+10])
ax1.set_xlim(time[0], time[-1]+2*60*60)
plt.ylabel('Temperature [$^o$C]')
ax1.set_xticks(time_ticks)
ax1.set_xticklabels('')

ax2 = f2.add_subplot(223)
ax2.set_title('SMB-21 simulaiton [current A]')
ax2.plot(time, current, 'r--')
ax2.set_ylim([min(current)-100, max(current)+100])
ax2.set_xlim(time[0], time[-1]+2*60*60)
plt.ylabel('Current rms [A]')
plt.xlabel('time [h]')
ax2.set_xticks(time_ticks)
ax2.set_xticklabels(time_labels, rotation=45)


ax3 = f2.add_subplot(222)
ax3.set_title('SMB-21 simulaiton - 45$^o$C / 3700->4000@2h')
ax3.plot(time2, copper_temperature2, time2, ambient2)
ax3.set_ylim([min(copper_temperature2)-10, max(copper_temperature2)+10])
ax3.set_xlim(time[0], time[-1]+2*60*60)
plt.ylabel('Temperature [$^o$C]')
ax3.set_xticks(time_ticks)
ax3.set_xticklabels('')

ax4 = f2.add_subplot(224)
ax4.set_title('SMB-21 simulaiton [current A]')
ax4.plot(time2, current2, 'r--')
ax4.set_ylim([min(current2)-100, max(current2)+100])
ax4.set_xlim(time[0], time[-1]+2*60*60)
plt.ylabel('Current rms [A]')
plt.xlabel('time [min]')
ax4.set_xticks(time_ticks)
ax4.set_xticklabels(time_labels, rotation=45)

# plt.tight_layout()
plt.show()
