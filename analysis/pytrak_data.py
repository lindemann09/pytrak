import numpy as np
import csv

def convert_data2npz(filename):
    """converts csv data to npz
    filename     
    """
    varnames = None
    comment_char = "#"
    sensor_ids = [1, 2, 3, 4]

    #make empty dict
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
    print "Converting .. "
    sensor_ids = filter(lambda x: len(data[x])>0, sensor_ids)  # remove unused data_ids
    print "sensor ids: ", sensor_ids
    timestamps = np.array(timestamps)
    quality = map(lambda x: np.array(quality[x]), sensor_ids)
    data = np.array(map(lambda x: np.array(data[x]), sensor_ids))
    print "data:", np.shape(data)
    
    filename = filename.rsplit(".", 1)[ 0 ]
    with open(filename + ".npz", "w") as npzfile:
        np.savez(npzfile, timestamps=timestamps, 
                 data=data, sensor_ids = sensor_ids,
                 quality=quality)
                 
def load_npz(filename):
    """returns sensor_ids, data, timestamps, quality
    requires filename incluing suffix    
    """
    fl = np.load(filename)
    return fl['sensor_ids'], fl['data'], fl['timestamps'], fl['quality']


def find_boarder_crossings(xyz, coordinates=[1,2]):
    """find each row, where the sign of the two coordinates changes
    :returns
        numpy arrays with indies where a border crossing occurs

    """
    sign_diff_sum = np.sum(np.abs(np.diff(np.sign(xyz[:, coordinates]), axis=0)), axis=1)
    return np.where(sign_diff_sum >=4)[0] + 1

def correct_boarder_crossings(data, coordinates=[1,2]):
    for s, sensor_xyz in enumerate(data):
        print find_boarder_crossings(sensor_xyz)
        for idx in find_boarder_crossings(sensor_xyz, coordinates):
            data[s, idx:, :] = data[s, idx:, :] * -1
    return data

if __name__ == "__main__":
    convert_data2npz("demo_data2.csv")
    sensor_ids, data, timestamps, quality = load_npz("demo_data2.npz") 

