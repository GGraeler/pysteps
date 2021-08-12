#!/usr/bin/python -tt
from multiprocessing import Pool, cpu_count
from itertools import product
import pandas as pd
from tdating import Tracks
from datetime import datetime

def mp(ran, overwrite = False):
	# Minimum dBZ threshold for tracks
	dBZ_threshold = 40.0

	# Convert dBZ threshold to rainfall rate
	a, b = 200.0, 1.6
	Z_threshold = 10**(dBZ_threshold/10)
	R_threshold = (Z_threshold/a)**(1/b)

	# Read in list of MRMS files
	df = pd.read_csv('/usr1/home/emsuser/DF2016.csv', parse_dates=['DateTime'])
	df = df.sort_values('DateTime')

	# Filter DataFrame to start_date and end_date
	df = df.loc[(df.DateTime >= start_date) & (df.DateTime <= end_date)]

	# Filter DataFrame files that exceeed the dBZ threshold
	df = df.loc[df.PrecipRate >= R_threshold]

	#Check if anything is in list
	print('Size of DF=', df.size)
	print(R_threshold)

	# Get list of MRMS files
	files = []
	for t in df.DateTime:
		s = f'/usr1/home/nas-qnap/MRMS/{t:%Y/%m/%d}/MRMS_PrecipRate_00.00_{t:%Y%m%d}-{t:%H%M%S}.grib2'
		files.append(s)

	# Create tuple with a list of file names and list of valid times
	metadata = (files, df.DateTime.to_list())

	# Get tracks
	data = Tracks(metadata, importer_kwargs={"extent":[244, 253, 30, 38], "window_size":1})
	data.execute()

	# Write tracks to csv
	data.df.to_csv(f'/usr1/home/nas-qnap/MRMS/Tracks_{start_date:%Y%m%d-%H%M}_{end_date:%Y%m%d-%H%M}.csv', index=False)
	print(data)

if __name__ == '__main__':
	start_date = datetime(2016, 9, 7, 15, 00)
	end_date   = datetime(2016, 9, 8, 14, 58)
	ran = [start_date, end_date]
	p = Pool()
	result = p.map(mp, ran)
	p.close()
	p.join()
