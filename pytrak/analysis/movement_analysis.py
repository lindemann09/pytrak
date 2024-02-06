"""helpful functions to analyses pytrak data"""

__author__ = "Oliver Lindemann"

from scipy import signal
import numpy as np


def inch2cm(data):
    """converts numpy data in inch to cm"""
    return data * 2.54

def velocity(data, timestamps):
    """calculates velocity of data for all sensors
    data in cm, timestamps in ms
    velocity in m/sec
    """
    diff_meter = (data[:, 0:-1, :]-data[:, 1:,:])/100.0
    dist = np.sqrt(np.sum(diff_meter**2, axis=2))
    tdiff = np.diff(timestamps)/1000.0
    velocity = [np.concatenate(([0], x/tdiff)) for x in dist]
    return np.transpose(np.array(velocity))

def estimate_sample_rate(timestamps):
    """estimates to sampling rate in hz for the timestamps"""
    return 1000.0/np.mean(np.diff(timestamps))

## data filtering
def butter_lowpass(lowcut, sample_rate, order=3):
    """design lowpass filter
     Sample rate and desired cutoff frequencies (in Hz).
     """
    nyq = 0.5 * sample_rate
    low = lowcut / nyq
    b, a = signal.butter(N=order, Wn=low, btype='lowpass')
    return b, a

def butter_lowpass_filter(data, lowcut=10, order=3,
                           sample_rate=None):
    """filter data of all sensors"""
    print("filtering data")
    if sample_rate is None:
        sample_rate = estimate_sample_rate(data)
    b, a = butter_lowpass(lowcut, sample_rate, order=order)
    filtered = [signal.lfilter(b, a, x) for x in data]
    return np.array(filtered)

def moving_average_filter(data, window_size=5):
    """moving average filter / running mean

    Note
    -----
    see http://stackoverflow.com/questions/13728392/moving-average-or-running-mean
    or http://stackoverflow.com/questions/11352047/finding-moving-average-from-data-points-in-python
    """

    window= np.ones(int(window_size))/float(window_size)
    ma_filter = lambda x : np.convolve(x, window, 'same')

    dim = np.shape(data)
    for s in range(dim[0]):
        for x in range(dim[2]):
            first_values = np.copy(data[s,:window_size:,x])
            last_values = np.copy(data[s,-window_size:,x])
            data[s,:,x] = ma_filter(data[s,:,x])
            data[s,:window_size:,x] = first_values
            data[s,-window_size:,x] = last_values

    return np.array(data)