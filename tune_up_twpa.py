import Labber
import os
import sys
from fitTools.utilities import Watt2dBm, dBm2Watt, VNA2dBm

from twpa_tune_up_helper_functions import *

if __name__ == "__main__":
    labber_data_file = str(input("File Location of TWPA Data: "))
    ref_data_file = str(input("File Location of Reference Data: "))

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

    ref_snr, ref_max_signal, ref_noise_floors = get_reference_data_SNR(ref_data_file,cutOff_around_SA_peak)

    print("\n\n"+"="*10+" REFERENCE DATA "+"="*10)
    print("Average SNR is {} dBm".format(ref_snr))
    print("Average Max Signal is {} dBm".format(ref_max_signal))
    print("Average of the noise floor is {} dBm".format(ref_noise_floors))
    print("="*40+"\n\n\n")


    get_SNR_space_plot(signal,repeated, freq_range, power_range, pump_freq,
                       pump_power, SAxdata, ref_snr, cutOff=cutOff_around_SA_peak,
                       xlabel=power_channel_name,
                       ylabel=freq_channel_name, zlabel='SNR', 
                       fig_type=".png", path="figures")


    print("\n\n"+"="*10+" TWPA Optimal Parameters"+"="*10)
    get_high_SNR_regions(signal,repeated, freq_range, power_range, pump_freq,
                         pump_power, SAxdata, ref_snr, cutOff=cutOff_around_SA_peak,
                         std_highSNR=std_highSNR)
