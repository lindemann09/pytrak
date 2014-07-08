import numpy as np
import sys, datetime
import csv

varnames = None
comment_char = "#"
comments = []

#make empty dict
sensor = {}
timestamps = []
quality = {}
for x in [1,2,3,4]:
	sensor[x] = []
	quality[x] = []
filename = "demo_data"
with open(filename + ".csv", "rb") as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)

	for row, record in enumerate(reader):
		if record[0].strip().startswith(comment_char):
			print record
		elif varnames is None:
			varnames = record
			print varnames
		else:
			s = int(record[1]) # sensor_id
			sensor[s].append(map(lambda x:np.float(x), record[2:5]))
			quality[s].append(np.float(record[5]))

			# timestamps
			t = np.int(record[0])
			try:
				if t !=timestamps[-1]:
					timestamps.append(t)
			except:
				timestamps.append(t)
print "Converting .. "
timestamps = np.array(timestamps)
sensor = map(lambda x:np.array(sensor[x]), [1,2,3,4]) 
quality = map(lambda x:np.array(quality[x]), [1,2,3,4]) 

for x in range(4):
	print np.shape(sensor[x])
	print np.shape(quality[x])
print("saving ...")

with open(filename + ".npz", "w") as npzfile:
	np.savez_compressed(npzfile, timestamps, sensor, quality)

	

