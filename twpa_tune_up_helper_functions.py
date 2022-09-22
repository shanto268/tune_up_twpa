import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import matplotlib

from datetime import datetime
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from scipy.signal import find_peaks, peak_prominences, peak_widths
from fitTools.utilities import Watt2dBm, dBm2Watt, VNA2dBm

def outliers_removed(arr, std_dev=2):
    mean = np.mean(arr)
    standard_deviation = np.std(arr)
    distance_from_mean = abs(arr - mean)
    max_deviations = std_dev
    not_outlier = distance_from_mean < max_deviations * standard_deviation
    no_outliers = arr[not_outlier]
    return no_outliers

def get_signal_stats(linsig,std_dev=2):
    """
    inputs: (linsig:: array (SA Signal in Watts), std_dev:: int (cut off for outlier)
    returns: [float, float, float] :: [snr, signal_max, average_noise_floor] (all in dBm)
    """
    peaks, peak_prop = find_peaks(linsig)
    all_data = linsig[peaks]
    noise_data = outliers_removed(linsig[peaks],std_dev)
    noise_floor = Watt2dBm(noise_data.mean())
    max_signal = Watt2dBm(max(all_data))
    snr = max_signal - noise_floor
    return [snr, max_signal, noise_floor]
    

def get_SNR_space_plot(signal,repeated, freq_range, power_range, pump_freq, pump_power, std_SNR=2.5, title="TWPA Tune Up", xlabel='Pump Power (dBm)', ylabel='Pump Frequency (Hz)', zlabel='SNR', fig_type=".png", path="figures"):
    average_signal = get_average_of_N_traces(signal,repeated)
    average_lin_signal = dBm2Watt(average_signal)
    
    pump_freqs = np.linspace(pump_freq[0][0],pump_freq[-1][-1],freq_range)
    pump_powers = np.linspace(pump_power[0][0],pump_power[-1][-1],power_range)

    SNRs, max_signals, noise_floors = calculate_SNRs(average_lin_signal,std_SNR)
    
    SNRs_reshaped = np.reshape(SNRs, (power_range,freq_range))
    
    create_heatmap(SNRs_reshaped, pump_powers, pump_freqs, title, xlabel, ylabel, zlabel,fig_type,path)
    
def get_high_SNR_regions(signal,repeated, freq_range, power_range,pump_freq, pump_power, std_SNR=2.5, std_highSNR=1.75):
    average_signal = get_average_of_N_traces(signal,repeated)
    average_lin_signal = dBm2Watt(average_signal)
    
    pump_freqs = np.linspace(pump_freq[0][0],pump_freq[-1][-1],freq_range)
    pump_powers = np.linspace(pump_power[0][0],pump_power[-1][-1],power_range)

    SNRs, max_signals, noise_floors = calculate_SNRs(average_lin_signal,std_SNR)
    SNRs_reshaped = np.reshape(SNRs, (power_range,freq_range))

    region = get_config_for_high_SNR(SNRs_reshaped,x=pump_powers, y=pump_freqs,std_dev=std_highSNR)

    print("="*20+"\nHigh SNR Regions:\n(power,frequency,SNR)\n\n"+str(region).replace("), ","),\n ")+"\n"+"="*20)
    return region 
    
def calculate_SNRs(average_lin_signal,std_SNR):
    SNRs = []
    max_signals = []
    noise_floors = []

    for signal in average_lin_signal:
        snrs, max_signal, noise_floor = get_signal_stats(signal,std_dev=std_SNR)
        SNRs.append(snrs)
        max_signals.append(max_signal)
        noise_floors.append(noise_floor)

    SNRs = np.array(SNRs)
    max_signals = np.array(max_signals)
    noise_floors = np.array(noise_floors)
    
    return SNRs, max_signals, noise_floors


def figure_name_maker(title,fig_type=".png",path="figures"):
    abs_path = os.getcwd()+f"/{path}/"
    try:
        os.mkdir(abs_path)
    except:
        pass
    now = datetime.now() # current date and time
    title=title.replace(" ", "_")
    dt = now.strftime("_%m_%d_%Y_%H%M%S")
    name = abs_path + title + dt + fig_type 
    return name

def create_heatmap(z, x, y, title="TWPA Tune Up", xlabel='Pump Power (dBm)', ylabel='Pump Frequency (Hz)', zlabel='SNR',fig_type=".png",path="figures"):
    heatmap, ax = plt.subplots(figsize=(8,6))
    
    im = ax.imshow(z,cmap='inferno',extent=[x[0],x[-1],y[0],y[-1]],interpolation='nearest',origin='lower',aspect='auto')
    
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_title(title,fontsize=14)
    cbar = heatmap.colorbar(im)
    cbar.ax.set_ylabel(zlabel)
    figname = figure_name_maker(title,fig_type,path)
    plt.savefig(figname)
    plt.show()
    
    
def get_2d_array_N_std_greater_than_mean(arr, std_dev=2):
    mean = np.mean(arr)
    standard_deviation = np.std(arr)
    distance_from_mean = abs(arr - mean)
    
    min_deviations = std_dev
    high_values = mean + min_deviations * standard_deviation    
    new_array = np.where(arr < high_values, 0, arr)
    return new_array

def get_config_for_high_SNR(arr,x,y,std_dev=2):
    mean = np.mean(arr)
    standard_deviation = np.std(arr)
    distance_from_mean = abs(arr - mean)
    
    min_deviations = std_dev
    high_values = mean + min_deviations * standard_deviation
    
    mask = (arr > high_values)
    indices = np.where(mask)
    
    snrs = arr[indices]
    xvals = x[indices[0]]
    yvals = y[indices[1]]
        
    return list(zip(xvals,yvals,snrs))

def get_index_for_high_SNR(arr,x,y,std_dev=2):
    mean = np.mean(arr)
    standard_deviation = np.std(arr)
    distance_from_mean = abs(arr - mean)
    
    min_deviations = std_dev
    high_values = mean + min_deviations * standard_deviation
    
    mask = (arr > high_values)
    indices = np.where(mask)

    return indices


def get_pump_power_and_frequency(pump_power,pump_freq,power_range,freq_range):
    """
    inputs:
        - pump_power from Labber
        - pump_freq from Labber
        - # of power points
        - # of frequency points
    returns:
        - pump_power ,  pump_freq (all 1D arr)
    """
    pump_freqs = np.linspace(pump_freq[0][0],pump_freq[-1][-1],freq_range)
    pump_powers = np.linspace(pump_power[0][0],pump_power[-1][-1],power_range)
    return pump_powers, pump_freqs

def get_column_from_2d_array(arr, n=0):
    """
    returns the nth column of the 2D array, arr
    """
    return arr[:,n]

def get_average_of_N_traces(signal, N):
    """
    inputs:
        - signal -> 2D array: from Labber Log File
        - N -> int: number of time a trace was taken for each config
    return:
        - averaged signal -> reduced 2D array
    """
    return signal.transpose().reshape(-1,N).mean(1).reshape(signal.shape[-1],-1).transpose()
