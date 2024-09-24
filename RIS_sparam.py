
import os 
# os.system('Measurement_PostProcessing_Braunsweig.py')
# os.system('Measurement_PostProcessing_Kyiv.py')


import matplotlib.pyplot as plt
import skrf as rf

rf.stylely()

pathMeas = 'C:/Work/PythonApps/RIS_sparam/Measurement/Kyiv/new_meas/Hor_2port_24092024/'
# pathMeas = '../RIS_measurements_Braunsweig/VNA/Calibrated_until_Antenna_0_20V/'
# voltages = [0.01, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 19.8]
voltages = [0.01, 5, 10, 15, 19.8]
#voltages = [0.01, 10]

startT = 1.7
stopT = 4.7
unitT = 'ns'
modeT = 'bandpass'
windowT = 'hann'
methodT = 'fft'

air     = rf.Network(pathMeas+'noDUT.s2p')
metal   = rf.Network(pathMeas+'metal.s2p')
air_21 = air.s21
metal_21 = metal.s21
R_metal = (metal_21-air_21)

air_21_gated    =   air_21.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)
metal_21_gated  = metal_21.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)
R_metal_gated   =  R_metal.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)

V = []
V_21 = []
V_21_gated = []
R_21 = []
R_21_gated = []
for i in range(len(voltages)):
    pathV = "{path}{voltage}.s2p".format(path=pathMeas, voltage=voltages[i])
    print(pathV)
    V.insert(i,rf.Network(pathV))
    V_21.insert(i, V[i].s21)
    V_21_gated.insert(i, V_21[i].time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT))

    R_21.insert(i, (V_21[i] - air_21)/(metal_21 - air_21))
    R_21_gated.insert(i, (V_21_gated[i] - air_21_gated)/(metal_21_gated - air_21_gated))
    R_21[i].name = "{voltage}".format(voltage=voltages[i])
    R_21_gated[i].name = "gated {voltage}".format(voltage=voltages[i])

# plot frequency and time-domain s-parameters
# plt.figure(0)
# plt.subplot(121)
# for i in range(len(voltages)):
#     # R_21_gated[i].plot_s_deg_unwrap()
#     R_21[i].plot_s_deg_unwrap()
# plt.title('Reflected Phase')
# plt.ylabel('Unwrapped phase [deg]')
# plt.xlabel('Frequency')

# plt.subplot(122)
# for i in range(len(voltages)):
#     # R_21_gated[i].plot_s_mag()
#     R_21[i].plot_s_mag()
# plt.title('Reflected Amplitude')
# plt.ylabel('Amplitude [1]')
# plt.xlabel('Frequency')
# plt.tight_layout()
# plt.show()

# # plot frequency and time-domain s-parameters
plt.figure(1)
plt.subplot(121)
for i in range(len(voltages)):
    R_21[i].plot_s_mag()
for i in range(len(voltages)):
    R_21_gated[i].plot_s_mag()
plt.ylabel('Amplitude [1]')
plt.xlabel('Frequency')
plt.xlim([9.5e9, 12.5e9])

plt.subplot(122)
for i in range(len(voltages)):
    R_21[i].plot_s_deg()
for i in range(len(voltages)):
    R_21_gated[i].plot_s_deg()
plt.title('Reflected Amplitude')
plt.ylabel('Amplitude [1]')
plt.xlabel('Frequency')
plt.xlim([9.5e9, 12.5e9])
plt.tight_layout()
plt.show()


print("finished")

# plt.subplot(122)
# air_21.plot_s_deg_unwrap()
# metal_21.plot_s_deg_unwrap()
# for i in range(len(voltages)):
#     # V_21[i].plot_s_db_time()
#     V_21[i].plot_s_deg_unwrap()
#     # V_21_gated[i].plot_s_db_time()
# # plt.title('Time Domain')
# plt.ylabel('Magnitude [dB]')
# plt.xlabel('Frequency')
# plt.show()
