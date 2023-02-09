import Labber
import os
import sys
from fitTools.utilities import Watt2dBm, dBm2Watt, VNA2dBm

from twpa_tune_up_helper_functions import *

if __name__ == "__main__":
    labber_data_file = str(input("Labber File Location: "))
    lf = Labber.LogFile(labber_data_file)

    repeated = len(lf.getStepChannels()[0]["values"])
    power_range = len(lf.getStepChannels()[1]["values"])
    freq_range = len(lf.getStepChannels()[2]["values"])

    std_highSNR = 1.15 # cut off point for determining high SNR
    cutOff_around_SA_peak = 10e3 # Hz


    power_channel_name = lf.getStepChannels()[1]["name"]
    freq_channel_name = lf.getStepChannels()[2]["name"]
    SA_channel_name = lf.getLogChannels()[0]["name"]

    pump_power = lf.getData(name = power_channel_name)
    pump_freq = lf.getData(name = freq_channel_name)

    signal = lf.getData(name = SA_channel_name)
    linsig = dBm2Watt(signal)

    SAxdata, SAydata = lf.getTraceXY(y_channel=SA_channel_name) # gives last trace from SA

    plt.rcParams['savefig.facecolor']='white'

    get_SNR_space_plot(signal,repeated, freq_range, power_range, pump_freq,
                       pump_power, SAxdata, cutOff=cutOff_around_SA_peak,
                       title="TWPA Tune Up", xlabel='Pump Power (dBm)', 
                       ylabel='Pump Frequency (Hz)', zlabel='SNR', 
                       fig_type=".png", path="figures")


    get_high_SNR_regions(signal,repeated, freq_range, power_range, pump_freq,
                         pump_power, SAxdata, cutOff=cutOff_around_SA_peak, 
                         std_highSNR=std_highSNR)
