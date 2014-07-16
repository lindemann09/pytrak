"""helpful functions to handle pytrak data"""

__author__ = "Oliver Lindemann"

from scipy import signal
import numpy as np
import csv

def load_csv(filename, comment_char = "#"):
    """TODO load csv file pytrak file"""

    varnames = None
    sensor_ids = [1, 2, 3, 4]

    #make empty dicts
    data = {}
    timestamps = []
    quality = {}
    for x in sensor_ids:
        data[x] = []
        quality[x] = []

    with open(filename, "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)

        for row, record in enumerate(reader):
            if record[0].strip().startswith(comment_char):
                print record
            elif varnames is None:
                varnames = record
                print varnames
            else:
                s = int(record[1])  # sensor_id
                data[s].append(map(lambda x: np.float(x), record[2:5]))
                quality[s].append(np.float(record[5]))

                # timestamps
                t = np.int(record[0])
                try:
                    if t != timestamps[-1]:
                        timestamps.append(t)
                except:
                    timestamps.append(t)
    sensor_ids = filter(lambda x: len(data[x])>0, sensor_ids)  # remove unused data_ids

    timestamps = np.array(timestamps)
    quality = np.array(map(lambda x: np.array(quality[x]), sensor_ids))
    data = np.array(map(lambda x: np.array(data[x]), sensor_ids))
    print "data:", np.shape(data)
    print "estimated sample rate", sample_rate(data)
    return sensor_ids, data, timestamps, quality

def convert_data2npz(filename, correct_hemisphere_crossing=True,
                     convert_inch2cm=False):
    """TODO converts csv data to npz
    filename
    """
    sensor_ids, data, timestamps, quality = load_csv(filename)
    if convert_inch2cm:
        print "Converting inch to cm"
        data = inch2cm(data)
    if correct_hemisphere_crossing:
        print "correcting hemispherer crossing"
        data = correct_hemisphere_crossings(data, coordinates=[0,1,2])

    filename = filename.rsplit(".", 1)[ 0 ] + ".npz"
    print "save ", filename
    with open(filename, "w") as npzfile:
        np.savez(npzfile, timestamps=timestamps,
                 data=data, sensor_ids = sensor_ids,
                 quality=quality)

def load_npz(filename):
    """TODO returns sensor_ids, data, timestamps, quality
    requires filename incluing suffix
    """
    fl = np.load(filename)
    return fl['sensor_ids'], fl['data'], fl['timestamps'], fl['quality']

def inch2cm(data):
    """converts numpy data in inch to cm"""
    return data * 2.54

def find_boarder_crossings(xyz, coordinates=[1,2]):
    """finds columns with hemisphere border crossing.
    Default: FORWARD hemisphere boarder detection ==> coordinates=[1,2]
            That is, function detects the sign change of the y & z values and
            adjusts the data
    :returns
        numpy arrays with indies where a border crossing occurs
    """
    sign_diff_sum = np.sum(np.abs(np.diff(np.sign(xyz[:, coordinates]), axis=0)),
                           axis=1)
    return np.where(sign_diff_sum >=4)[0] + 1

def correct_hemisphere_crossings(data, coordinates=[1,2]):
    """Adapts the trakstar data as regards the crossing of hemisphere border.
    Default: FORWARD hemisphere boarder detection ==> coordinates=[1,2]
            That is, function detects the sign change of the y & z values and
            adjusts the data
    :returns
        numpy arrays with corrected data
    """
    for s, sensor_xyz in enumerate(data):
        for idx in find_boarder_crossings(sensor_xyz, coordinates):
            data[s, idx:, :] = data[s, idx:, :] * -1
    return data

def velocity(data, timestamps):
    """calculates velocity of data for all sensors
    data in cm, timestamps in ms
    velocity in m/sec
    """
    diff_meter = (data[:, 0:-1, :]-data[:, 1:,:])/100.0
    dist = np.sqrt(np.sum(diff_meter**2, axis=2))
    tdiff = np.diff(timestamps)/1000.0
    velocity = map(lambda x: np.concatenate(([0], x/tdiff)),
                    dist)
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
    print "filtering data"
    if sample_rate is None:
        sample_rate = estimate_sample_rate(data)
    b, a = butter_lowpass(lowcut, sample_rate, order=order)
    filtered = map(lambda x: signal.lfilter(b, a, x), data)
    return np.array(filtered)

def moving_average_filter(data, window_size=5):
    """moving average filter / running mean

    Note
    -----
    see http://stackoverflow.com/questions/13728392/moving-average-or-running-mean

    """
    N = window_size
    ma_filter = lambda x :np.convolve(x, np.ones((N,))/N)[(N-1):]

    dim = np.shape(data)
    for s in range(dim[0]):
        for x in range(dim[2]):
            data[s,:,x] = ma_filter(data[s,:,x])
            data[s,-N:,x] = data[s,-N-1,x] # last N values should not be zero
                                             #  but -N-1
    return np.array(data)