import Labber
import os
import sys
from fitTools.utilities import Watt2dBm, dBm2Watt, VNA2dBm

from twpa_tune_up_helper_functions import *

if __name__ == "__main__":
    labber_data_file = str(sys.argv[1])
    repeated = int(input("Number of Repeations: "))
    power_range = int(input("Number of Points for Power: "))
    freq_range = int(input("Number of Points for Frequency: "))

    std_highSNR = 1.75 # cut off point
    std_SNR = 2.5 # for noise floor

    lf = Labber.LogFile(labber_data_file)

    power_channel_name = "10002F25 - Power"
    freq_channel_name = "10002F25 - Frequency"
    SA_channel_name = 'HP Spectrum Analyzer - Signal'

    pump_power = lf.getData(name = power_channel_name)
    pump_freq = lf.getData(name = freq_channel_name)  

    signal = lf.getData(name = SA_channel_name)
    linsig = dBm2Watt(signal)

    SAxdata, SAydata = lf.getTraceXY(y_channel=SA_channel_name) # gives last trace from SA

    plt.rcParams['savefig.facecolor']='white'

    get_SNR_space_plot(signal,repeated, freq_range, power_range, pump_freq, pump_power, std_SNR=std_SNR, title="TWPA Tune Up", xlabel='Pump Power (dBm)', ylabel='Pump Frequency (Hz)', zlabel='SNR', fig_type=".png", path="figures")


    get_high_SNR_regions(signal,repeated, freq_range, power_range, pump_freq, pump_power, std_SNR=std_SNR, std_highSNR=std_highSNR)
