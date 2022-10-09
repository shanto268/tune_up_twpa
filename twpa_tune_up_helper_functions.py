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
import Labber



def calculate_mean_SNR_from_Labber_file(labber_data_file, cutOff = 10e3):
    """
    """
    lf = Labber.LogFile(labber_data_file)
    SA_channel_name = 'HP Spectrum Analyzer - Signal'


    signal = lf.getData(name = SA_channel_name)
    linsig = dBm2Watt(signal)

    SAxdata, SAydata = lf.getTraceXY(y_channel=SA_channel_name, entry=0) # gives last trace from SA
    
    snrs = 0
    for i in range(len(signal)):
        snrs += get_signal_stats(dBm2Watt(signal[i]), SAxdata, cutOff)[0]

    snr_mean = snrs / len(signal)
    return snr_mean



def outliers_removed(arr, std_dev=2):
    mean = np.mean(arr)
    standard_deviation = np.std(arr)
    distance_from_mean = abs(arr - mean)
    max_deviations = std_dev
    not_outlier = distance_from_mean < max_deviations * standard_deviation
    no_outliers = arr[not_outlier]
    return no_outliers

def get_signal_stats(linsig,SAxdata,cutOff=10e3):
    """
    inputs: (linsig:: array (SA Signal in Watts), std_dev:: int (cut off for outlier)
    returns: [float, float, float] :: [snr, signal_max, average_noise_floor] (all in dBm)
    """
    # James Style
    max_ind = np.argmax(linsig)
    max_val = np.max(linsig)
    mask = np.logical_or(SAxdata < SAxdata[max_ind]-cutOff, SAxdata > SAxdata[max_ind]+cutOff)
    noisetemp = linsig[mask]
    noise_floor = np.mean(noisetemp)
    snr = Watt2dBm(max_val) - Watt2dBm(noise_floor)
    noise_floor = Watt2dBm(noise_floor)
    max_signal = Watt2dBm(max_val)
    return [snr, max_signal, noise_floor]

    # peaks, peak_prop = find_peaks(linsig)
    # all_data = linsig[peaks]
    # noise_data = outliers_removed(linsig[peaks],std_dev)
    # noise_floor = Watt2dBm(noise_data.mean())
    # max_signal = Watt2dBm(max(all_data))
    # snr = max_signal - noise_floor
    # return [snr, max_signal, noise_floor]
    

def get_SNR_space_plot(signal,repeated, freq_range, power_range, pump_freq, pump_power, SAxdata, cutOff=10e3, title="TWPA Tune Up", xlabel='Pump Power (dBm)', ylabel='Pump Frequency (Hz)', zlabel='SNR', fig_type=".png", path="figures"):
    average_signal = get_average_of_N_traces(signal,repeated)
    average_lin_signal = dBm2Watt(average_signal)
    
    pump_freqs = np.linspace(pump_freq[0][0],pump_freq[-1][-1],freq_range)
    pump_powers = np.linspace(pump_power[0][0],pump_power[-1][-1],power_range)

    SNRs, max_signals, noise_floors = calculate_SNRs(average_lin_signal,SAxdata,cutOff)
    
    SNRs_reshaped = np.reshape(SNRs, (freq_range,power_range))
    
    create_heatmap(SNRs_reshaped, pump_powers, pump_freqs, title, xlabel, ylabel, zlabel,fig_type,path)
    
def get_high_SNR_regions(signal,repeated, freq_range, power_range,pump_freq, pump_power, SAxdata, cutOff=10e3, std_highSNR=1.75):
    average_signal = get_average_of_N_traces(signal,repeated)
    average_lin_signal = dBm2Watt(average_signal)

    pump_freqs = np.linspace(pump_freq[0][0],pump_freq[-1][-1],freq_range)
    pump_powers = np.linspace(pump_power[0][0],pump_power[-1][-1],power_range)

    SNRs, max_signals, noise_floors = calculate_SNRs(average_lin_signal,SAxdata,cutOff)
    SNRs_reshaped = np.reshape(SNRs, (freq_range,power_range))

    meanSNR = np.mean(SNRs_reshaped)
    region = get_config_for_high_SNR(SNRs_reshaped,x=pump_powers, y=pump_freqs,std_dev=std_highSNR)
    std_message = f"Region of High SNR\n[i.e SNR > mean(SNR) * std_dev(SNR)]\nmean(SNR) = {meanSNR:.3f}, std_dev(SNR) = {std_highSNR:.2f}"
    create_heatmap(region, pump_powers, pump_freqs, title = std_message, xlabel='Pump Power (dBm)', ylabel='Pump Frequency (Hz)', zlabel='SNR',)
    print_coordinates(get_coordinates(pump_powers, pump_freqs,region))
    return get_coordinates(pump_powers, pump_freqs,region)

def calculate_SNRs(average_lin_signal,SAxdata,cutOff=10e3):
    SNRs = []
    max_signals = []
    noise_floors = []

    for signal in average_lin_signal:
        snrs, max_signal, noise_floor = get_signal_stats(signal,SAxdata,cutOff)
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


def get_coordinates(x,y,z):
    mask = np.isfinite(z)
    xx,yy = np.array(np.meshgrid(x, y))
    masked_x = mask*xx
    masked_y = mask*yy
    x = masked_x[masked_x>0]
    y = masked_y[masked_y>0]
    z = z[np.isfinite(z)]
    return np.array((x,y,z)).T

def print_coordinates(arr):
    for i in range(arr.shape[0]):
        print(f"SNR = {arr[i][2]:.3f} for Power = {arr[i][1]}and Frequency = {arr[i][0]}")

# def create_heatmap(z, x, y, title="TWPA Tune Up", xlabel='Pump Power (dBm)', ylabel='Pump Frequency (Hz)', zlabel='SNR',fig_type=".png",path="figures"):
def create_heatmap(z, x, y, title="", xlabel='', ylabel='', zlabel='',fig_type=".png",path="figures"):
    heatmap, ax = plt.subplots(figsize=(8,6))
    
    im = ax.imshow(z,cmap='inferno',extent=[x[0],x[-1],y[0],y[-1]],interpolation='nearest',origin='lower',aspect='auto')
    
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.set_title(title,fontsize=14)
    cbar = heatmap.colorbar(im)
    cbar.ax.set_ylabel(zlabel)
    figname = figure_name_maker(title,fig_type,path)
    try:
        plt.savefig(figname)
    except:
        dt = datetime.now().strftime("_%m_%d_%Y_%H%M%S")
        uid_name = "_".join(figname.split("/")[-1].split("_")[:1]) + dt
        plt.savefig(path+"/"+f"{uid_name}"+fig_type)
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

    arr[arr < high_values] = np.nan
    return arr

    # mask = (arr > high_values)
    # indices = np.where(mask)
    
    # snrs = arr[indices]
    # xvals = x[indices[0]]
    # yvals = y[indices[1]]
        
    # return list(zip(xvals,yvals,snrs))

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
