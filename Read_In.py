import numpy as np
from MRMS import ldm_ingest, dataset
import pandas as pd
from multiprocessing import Pool, cpu_count

def max_value(val):
	print(val)
	R = dataset(val)
	R.load_dataset(engine='pygrib', extent=(30, 38, 244, 253))
	vals = R.dataset.PrecipRate.values
	maximum = np.max(vals)
	return R.valid, maximum

data_list = ldm_ingest('/usr1/home/nas-qnap/MRMS/2015/*/*', vars='PrecipRate')
#data_list.files.sort()

#max_time_list = []
"""
for file_path in data_list.files:
		max_time_list.append(max_value(file_path))
"""

pool = Pool(processes=cpu_count())
max_time_list = pool.map(max_value, data_list.files)
pool.close()

df = pd.DataFrame(max_time_list, columns = ['DateTime', 'PrecipRate'])
df.to_csv('DF2015.csv', index=False)
