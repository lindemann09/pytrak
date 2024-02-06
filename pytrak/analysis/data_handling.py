"""helpful functions to handle pytrak data"""

__author__ = "Oliver Lindemann"

import csv
import numpy as np

from .movement_analysis import inch2cm, estimate_sample_rate

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
                print(record)
            elif varnames is None:
                varnames = record
                print(varnames)
            else:
                s = int(record[1])  # sensor_id
                data[s].append([np.float(x) for x in record[2:5]])
                quality[s].append(np.float(record[5]))

                # timestamps
                t = np.int(record[0])
                try:
                    if t != timestamps[-1]:
                        timestamps.append(t)
                except:
                    timestamps.append(t)
    sensor_ids = [x for x in sensor_ids if len(data[x])>0]  # remove unused data_ids

    timestamps = np.array(timestamps)
    quality = np.array([np.array(quality[x]) for x in sensor_ids])
    data = np.array([np.array(data[x]) for x in sensor_ids])
    print("data:", np.shape(data))
    print("estimated sample rate", estimate_sample_rate(data))
    return sensor_ids, data, timestamps, quality

def convert_data2npz(filename, correct_hemisphere_crossing=True,
                     convert_inch2cm=False):
    """TODO converts csv data to npz
    filename
    """
    sensor_ids, data, timestamps, quality = load_csv(filename)
    if convert_inch2cm:
        print("Converting inch to cm")
        data = inch2cm(data)
    if correct_hemisphere_crossing:
        print("correcting hemispherer crossing")
        data = correct_hemisphere_crossings(data, coordinates=[0,1,2])

    filename = filename.rsplit(".", 1)[ 0 ] + ".npz"
    print("save ", filename)
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
