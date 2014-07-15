# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 13:47:59 2014

@author: oliver
"""
import numpy as np
from matplotlib import pyplot
import pytrak_data

colours = ['g', 'b', 'y', 'c']

def plot_sensors(axes, data, x, y):
    """
    Parameters
    ----------
    axes : pyplot axes

    data : data numpy array

    x_col : int
        data column x_achses

    y_col: int
        data column y_achses
    """


    n_sensors = np.shape(data)[0]
    for s in range(n_sensors):
        axes.plot(data[s,:,x], data[s,:,y], colours[s])

def plot_sensor_data(data, axes):
    n_sensors = np.shape(data)[0]
    for s in range(n_sensors):
        axes.plot(data[s,:,x], data[s,:,y], colours[s])


#pytrak_data.convert_data2npz("demo_data.csv")
sensor_ids, data, timestamps, quality = pytrak_data.load_npz("demo_data.npz")
print np.shape(data)

d = data[2,4800:5600,:]
coordinates=[1,2]
xsum = np.sum(np.abs(np.diff(np.sign(d[:, :]), axis=0)), axis=1)
xsum = np.append([0], xsum)
dd = np.concatenate((d, np.transpose([xsum])),1)
np.savetxt("test.txt", dd, fmt="%8.2f")


#fig = pyplot.Figure((15.0, 4.0))
#axes = fig.add_subplot(121)


#diff = np.diff(data[0,:,1])
#f = pyplot.hist(np.diff(timestamps), bins=1000)
#plot_sensors(axes, data, x=1, y=2)
#pyplot.show()
#print np.histogram(diff, bins=100)
#print np.median(diff)
