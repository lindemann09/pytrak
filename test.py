# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 13:47:59 2014

@author: oliver
"""
from timeit import timeit
import numpy as np
from matplotlib import pyplot
from pytrak import analysis as pta


#pta.run_data_browser()
#pta.convert_data2npz("data/demo_data.csv")
sensor_ids, data, timestamps, quality = pta.load_npz("demo_data/demo_data.npz")
print np.shape(data)
print timeit(lambda : pta.moving_average_filter(data), number = 10 )
#np.savetxt("test.txt", timestamps, fmt="%8.2f")

#fig = pyplot.Figure((15.0, 4.0))
#axes = fig.add_subplot(121)


#diff = np.diff(data[0,:,1])
#f = pyplot.hist(np.diff(timestamps), bins=1000)
#plot_sensors(axes, data, x=1, y=2)
#pyplot.show()
#print np.histogram(diff, bins=100)
#print np.median(diff)
