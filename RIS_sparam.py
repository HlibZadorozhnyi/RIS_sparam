
import os 
import matplotlib.pyplot as plt
import skrf as rf
import math

rf.stylely()

pathSim  = '../RIS_sparam/Simulation/UnitCell/'
pathMeas = '../RIS_sparam/Measurement/Kyiv/new_meas/1port_24092024/'
# pathMeas = '../RIS_sparam/Measurement/Braunsweig/VNA/Calibrated_until_Antenna_0_20V/'
# voltages = [0.01, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 19.8]
voltages = [19.8]
#voltages = [0.01, 10]

startT = 2
stopT = 5
unitT = 'ns'
modeT = 'bandpass'
windowT = 'hann'
methodT = 'fft'

noDUT_sim_UC = rf.Network(pathSim+'noDUT.s1p')
metal_sim_UC = rf.Network(pathSim+'metal.s1p')
noDUT_sim_UC_11 = noDUT_sim_UC.s11
metal_sim_UC_11 = metal_sim_UC.s11

noDUT_meas  = rf.Network(pathMeas+'noDUT.s1p')
metal_meas  = rf.Network(pathMeas+'metal.s1p')
noDUT_meas_21 = noDUT_meas.s11
metal_meas_21 = metal_meas.s11
noDUT_meas_21_gated = noDUT_meas_21.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)
metal_meas_21_gated = metal_meas_21.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)



V_meas = []
V_meas_21 = []
V_meas_21_gated = []
R_meas_21 = []
R_meas_21_gated = []

V_sim_UC    = []
V_sim_UC_11 = []
R_sim_UC_11 = []

for i in range(len(voltages)):

    pathUC = "{path}{voltage}.s1p".format(path=pathSim, voltage=voltages[i])
    V_sim_UC.insert(i,rf.Network(pathUC))
    V_sim_UC_11.insert(i, V_sim_UC[i].s11)
    R_sim_UC_11.insert(i, (V_sim_UC_11[i]/noDUT_sim_UC_11))
    R_sim_UC_11[i].name = "R Sim UC {voltage}V".format(voltage=voltages[i])

    pathV = "{path}{voltage}.s1p".format(path=pathMeas, voltage=voltages[i])
    V_meas.insert(i,rf.Network(pathV))

    V_meas_21.insert(i, V_meas[i].s11)
    R_meas_21.insert(i, (V_meas_21[i] - noDUT_meas_21)/(metal_meas_21 - noDUT_meas_21))
    R_meas_21[i] = R_meas_21[i] + (1j*pow(2,-0.5));
    R_meas_21[i].name = "Meas {voltage}".format(voltage=voltages[i])

    V_meas_21_gated.insert(i, V_meas_21[i].time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT))
    R_meas_21_gated.insert(i, (V_meas_21_gated[i] - noDUT_meas_21_gated)/(metal_meas_21_gated - noDUT_meas_21_gated))
    R_meas_21_gated[i] = R_meas_21_gated[i] + (1j*pow(2,-0.5));
    R_meas_21_gated[i].name = "Meas gated {voltage}".format(voltage=voltages[i])

    print(pathUC)
    print(pathV)

# plot frequency and time-domain s-parameters
plt.figure(1)
plt.subplot(121)
for i in range(len(voltages)):
    R_meas_21[i].plot_s_mag()
for i in range(len(voltages)):
    R_meas_21_gated[i].plot_s_mag()
for i in range(len(voltages)):
    R_sim_UC_11[i].plot_s_mag()
plt.title('Reflected Amplitude')
plt.ylabel('Amplitude [1]')
plt.xlabel('Frequency')
# plt.xlim([9.5e9, 12.5e9])

plt.subplot(122)
for i in range(len(voltages)):
    R_meas_21[i].plot_s_deg_unwrap()
for i in range(len(voltages)):
    R_meas_21_gated[i].plot_s_deg_unwrap()
for i in range(len(voltages)):
    R_sim_UC_11[i].plot_s_deg_unwrap()
plt.title('Reflected Phase')
plt.ylabel('Phase [deg]')
plt.xlabel('Frequency')
# plt.xlim([9.5e9, 12.5e9])
plt.tight_layout()
plt.show()




# plt.figure(1)
# plt.subplot(121)
# air_21.plot_s_db_time()
# metal_21.plot_s_db_time()
# for i in range(len(voltages)):
#     V_21[i].plot_s_db_time()
#     # V_21_gated[i].plot_s_db_time()
# plt.title('Time Domain')
# plt.ylabel('Phase [deg]')
# plt.xlabel('Frequency')

# plt.subplot(122)
# for i in range(len(voltages)):
#     R_21_gated[i].plot_s_deg()
# plt.ylabel('Magnitude [dB]')
# plt.xlabel('Frequency')
# plt.xlim([9.5e9, 12.5e9])
# plt.tight_layout()
# plt.show()


print("finished")
