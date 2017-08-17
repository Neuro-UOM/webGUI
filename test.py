import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from IPython import get_ipython
import seaborn as sns
import glob
import pandas as pd
from scipy import signal


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def Fourier_Thread(O2_array):
    # specifying the O2 node for the value
    y = O2_array
    y = butter_highpass_filter(y,5,132,5)

    ps = np.abs(np.fft.fft(y))**2

    time_step = float(1)/128
    freqs = np.fft.fftfreq( y.size , time_step )
    idx = np.argsort(freqs)

    return freqs[idx] , ps[idx]

print Fourier_Thread([23,23,423,4,34,32,4,324,3,4,234,234,23,4,324,324,23,4,234,234,32,423,4,252,23,4,234,23,42,34,23,42,34,23,4,234,23,4,234,23,42,34,23,4,234,23,42,34,23,4])