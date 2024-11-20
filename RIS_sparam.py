
import os 
import matplotlib.pyplot as plt
import skrf as rf
import math
import numpy as np

def main():

    rf.stylely()

    pathSim  = '../RIS_sparam/Simulation/UnitCell/'
    # voltages = [0.01, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 19.8]
    voltages = [0.01]
    # voltages = [5]

    Sowner = 'Kyiv' # owner of the S-parameters: Kyiv or Braunschweig
    Sfile = 's1p'   # Depends on the measurement system: s1p or s2p
    Sparam = 's11'  # Select the Sparam to apply the Time Analyzis

    # new_freq = rf.Frequency(7,13,60001,'ghz')

    if Sowner == 'Braunschweig':
        pathMeas = '../RIS_sparam/Measurement/Braunschweig/VNA/Calibrated_until_Antenna_0_20V/'
        postfix = '_1'
        startT = 3.5
        stopT = 6
    elif Sowner == 'Kyiv':

        ### 1) Initial test: a single-port system. The RIS is positioned at distances of 120 mm and 320 mm.
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/single port/RIS_27082024_130mm/'
        # startT = 0
        # stopT = 3
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/single port/RIS_27082024_320mm/'
        # startT = 1
        # stopT = 4

        ### 2) The test was conducted near the WR90. Another test was performed at a far distance of 3300 mm using two antennas.
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/single port/RIS_04092024_3300mm_ant1/'
        pathMeas = '../RIS_sparam/Measurement/Kyiv/single port/RIS_04092024_3300mm_ant2/'
        startT = 15
        stopT = 30
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/single port/RIS_04092024_near_openWR90/'
        # startT = -2
        # stopT = 2

        ### 3) The two-port system was used at the expected far-field distance for the antenna.
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/two port/Hor_06092024_130mm/'
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/two port/Ver_06092024_130mm/'
        # startT = -1
        # stopT = 3

        ### The latest test focused on the antenna's maximum bandwidth at a distance of 320 mm.
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/new_meas/1port_24092024/'
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/new_meas/Ver_2port_24092024/'
        # pathMeas = '../RIS_sparam/Measurement/Kyiv/new_meas/Hor_2port_24092024/'
        # startT = 2.3
        # stopT = 4.8

        postfix = ''
        

    unitT = 'ns'
    modeT = 'bandpass'
    windowT = ('kaiser',5) # 'boxcar' or 'hann' or 'hamming'
    #windowT = 'boxcar'
    methodT = 'fft'

    noDUT_sim_UC = rf.Network(pathSim+'noDUT.s1p')
    metal_sim_UC = rf.Network(pathSim+'metal.s1p')
    noDUT_sim_UC = noDUT_sim_UC.s11
    metal_sim_UC = metal_sim_UC.s11

    noDUT_meas  = rf.Network('{pathmeas}noDUT{postf}.{sfile}'.format(pathmeas=pathMeas, postf=postfix, sfile=Sfile))
    metal_meas  = rf.Network('{pathmeas}metal{postf}.{sfile}'.format(pathmeas=pathMeas, postf=postfix, sfile=Sfile))
    if Sparam == 's11':
        noDUT_meas = noDUT_meas.s11
        metal_meas = metal_meas.s11
    elif Sparam == 's21':
        noDUT_meas = noDUT_meas.s21
        metal_meas = metal_meas.s21
    elif Sparam == 's12':
        noDUT_meas = noDUT_meas.s12
        metal_meas = metal_meas.s12
    elif Sparam == 's22':
        noDUT_meas = noDUT_meas.s22
        metal_meas = metal_meas.s22

    # noDUT_meas.windowed()
    # metal_meas.windowed()
    # noDUT_meas.interpolate(new_freq, kind = 'cubic')
    # metal_meas.interpolate(new_freq, kind = 'cubic')
    noDUT_meas_gated = noDUT_meas.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)
    metal_meas_gated = metal_meas.time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT)


    V_sim_UC = []
    R_sim_UC = []

    V_meas = []
    V_meas_gated = []

    R_meas = []
    R_meas_gated = []

    R_deg_simUC = []
    R_deg_meas = []
    R_deg_meas_gated = []


    for i in range(len(voltages)):

        pathUC = "{path}{voltage}.s1p".format(path=pathSim, voltage=voltages[i])
        VsimUC = rf.Network(pathUC)
        V_sim_UC.insert(i, VsimUC.s11)
        R_sim_UC.insert(i, (V_sim_UC[i]/noDUT_sim_UC))
        R_sim_UC[i].name = "R sim UC {voltage}V".format(voltage=voltages[i])


        pathV = "{path}{voltage}{postf}.{param}".format(path=pathMeas, voltage=voltages[i], param = Sfile, postf = postfix)
        Vmeas = rf.Network(pathV)
        if Sparam == 's11':
            V_meas.insert(i, Vmeas.s11)
        elif Sparam == 's21':
            V_meas.insert(i, Vmeas.s21)
        elif Sparam == 's12':
            V_meas.insert(i, Vmeas.s12)
        elif Sparam == 's22':
            V_meas.insert(i, Vmeas.s22)
        # V_meas[i].windowed()
        # V_meas[i].interpolate(new_freq, kind = 'cubic')
        V_meas_gated.insert(i, V_meas[i].time_gate(start=startT, stop=stopT, t_unit=unitT, mode=modeT, window=windowT, method=methodT))

        R_meas.insert(i,       getRcoeff(V_meas[i], noDUT_meas, metal_meas))
        R_meas_gated.insert(i, getRcoeff(V_meas_gated[i], noDUT_meas_gated, metal_meas_gated))

        R_meas[i].name = "R meas {voltage}V".format(voltage=voltages[i])
        R_meas_gated[i].name = "R meas gated {voltage}V".format(voltage=voltages[i])

        R_deg_simUC.insert(i, getUdeg(R_sim_UC[i]))
        R_deg_meas.insert(i, getUdeg(R_meas[i]))
        R_deg_meas_gated.insert(i, getUdeg(R_meas_gated[i]))

        ### For the Latest measurement
        if Sowner == 'Kyiv':
            if voltages[i] == 0.01:
                R_deg_meas[i] = R_deg_meas[i] + 50
                R_deg_meas_gated[i] = R_deg_meas_gated[i] + 50
            elif voltages[i] == 5:
                R_deg_meas[i] = R_deg_meas[i] + 50
                R_deg_meas_gated[i] = R_deg_meas_gated[i] + 50
            elif voltages[i] == 10:
                R_deg_meas[i] = R_deg_meas[i] + 50
                R_deg_meas_gated[i] = R_deg_meas_gated[i] + 50
            elif voltages[i] == 15:
                R_deg_meas[i] = R_deg_meas[i] + 360 + 50
                R_deg_meas_gated[i] = R_deg_meas_gated[i] + 50
            elif voltages[i] == 19.8:
                R_deg_meas[i] = R_deg_meas[i] + 360 + 50
                R_deg_meas_gated[i] = R_deg_meas_gated[i] + 50

        elif Sowner == 'Braunschweig':
            ### Only for Sparam == 's21'
            if voltages[i] == 0.01:
                R_deg_meas[i] = R_deg_meas[i] + 700
                R_deg_meas_gated[i] = R_deg_meas_gated[i] - 20
            elif voltages[i] == 5:
                R_deg_meas[i] = R_deg_meas[i] - 1100
                R_deg_meas_gated[i] = R_deg_meas_gated[i] - 20
            elif voltages[i] == 10:
                R_deg_meas[i] = R_deg_meas[i]- 40
                R_deg_meas_gated[i] = R_deg_meas_gated[i] - 40
            elif voltages[i] == 15:
                R_deg_meas[i] = R_deg_meas[i] - 780
                R_deg_meas_gated[i] = R_deg_meas_gated[i] - 50
            elif voltages[i] == 19.8:
                R_deg_meas[i] = R_deg_meas[i] + 2090
                R_deg_meas_gated[i] = R_deg_meas_gated[i] + 300

        

        print(pathUC)
        print(pathV)

    freq_meas = (V_meas[i].f)/1e9
    freq_sim = (V_sim_UC[i]).f/1e9


    # Time domain analyzis
    plt.figure(1)
    plt.subplot(221)
    plotTimeDomain([],[], V_meas, noDUT_meas, metal_meas, voltages)
    plt.subplot(222)
    plotTimeDomain([startT-5,stopT+5],[], V_meas, noDUT_meas, metal_meas, voltages)
    plt.subplot(223)    # gated
    plotTimeDomain([],[], V_meas_gated, noDUT_meas_gated, metal_meas_gated, voltages)
    plt.subplot(224)    # gated
    plotTimeDomain([startT-5,stopT+5],[], V_meas_gated, noDUT_meas_gated, metal_meas_gated, voltages)

    # Reflection coefficient using Skrf build-in functions
    plt.figure(2)
    plt.subplot(221)
    plotRdeg([7e9, 13e9], [], R_meas, R_sim_UC, voltages)
    plt.subplot(222)
    plotRmag([7e9, 13e9], [0,5], R_meas, R_sim_UC, voltages)
    plt.subplot(223)
    plotRdeg([7e9, 13e9], [], R_meas_gated, R_sim_UC, voltages)
    plt.subplot(224)
    plotRmag([7e9, 13e9], [0,5], R_meas_gated, R_sim_UC, voltages)

    # Reflection coefficient phase using manual normalization
    plt.figure(3)
    plt.subplot(221)
    legenda = []
    for i in range(len(voltages)):
        plt.plot(freq_meas, R_deg_meas[i], ls=':', lw=2)
        legenda.insert((i), '{voltage}'.format(voltage=voltages[i]))
    plt.legend(legenda)
    plt.title("R meas", fontsize=10)
    plt.ylabel("Phase [deg]")
    plt.xlim([7, 13])
    plt.ylim([-500, 100])

    plt.subplot(222)
    legenda = []
    for i in range(len(voltages)):
        plt.plot(freq_meas, R_deg_meas_gated[i], ls='--', lw=3)
        legenda.insert((i), '{voltage}'.format(voltage=voltages[i]))
    plt.legend(legenda)
    plt.title("R meas gated", fontsize=10)
    plt.ylabel("Phase [deg]")
    plt.xlim([7, 13])
    plt.ylim([-500, 100])

    plt.subplot(223)
    legenda = []
    for i in range(len(voltages)):
        plt.plot(freq_sim, R_deg_simUC[i], lw=2)
        legenda.insert((i), '{voltage}'.format(voltage=voltages[i]))
    plt.legend(legenda)
    plt.title("R sim UC", fontsize=10)
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Phase [deg]")
    plt.xlim([7, 13])
    plt.ylim([-500, 100])

    plt.subplot(224)
    legenda = []
    for i in range(len(voltages)):
        plt.plot(freq_meas, R_deg_meas_gated[i], ls='--', lw=3)
        plt.plot(freq_sim, R_deg_simUC[i], lw=2)
        legenda.insert((1+3*i), '{voltage} R meas gated '.format(voltage=voltages[i]))
        legenda.insert((2+3*i), '{voltage} R sim UC '.format(voltage=voltages[i]))
    plt.legend(legenda)
    plt.title("R meas gated + R sim UC", fontsize=10)
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Phase [deg]")
    plt.xlim([7, 13])
    plt.ylim([-400, 100])


    plt.show()


def plotRmag(xlim, ylim, Rmeas, RsimUC, voltages):
    for i in range(len(voltages)):
        Rmeas[i].plot_s_mag()
        RsimUC[i].plot_s_mag()
    if xlim:
        plt.xlim(xlim)
    if ylim:
        plt.ylim(ylim)

def plotRdeg(xlim, ylim, Rmeas, RsimUC, voltages):
    for i in range(len(voltages)):
        Rmeas[i].plot_s_deg()
        RsimUC[i].plot_s_deg()
    if xlim:
        plt.xlim(xlim)
    if ylim:
        plt.ylim(ylim)

def plotTimeDomain(xlim, ylim, DUT, noDUT, metal, voltages):
    noDUT.plot_s_time_db()
    metal.plot_s_time_db()
    for i in range(len(voltages)):
        DUT[i].plot_s_time_db()
    if xlim:
        plt.xlim(xlim)
    if ylim:
        plt.ylim(ylim)
    plt.tight_layout()

def getUdeg(network):
    phase = network.s_deg.flatten()
    phase_u = np.unwrap(phase*(math.pi/180)) * (180/math.pi);
    return phase_u

def getMag(network):
    amplitude = network.s_mag.flatten()
    return amplitude

def getRcoeff(DUT, noDUT, metal):
    metal_norm = (metal-noDUT)
    DUT_norm = (DUT-noDUT)
    return DUT_norm/metal_norm

if __name__ == "__main__":
    main()

