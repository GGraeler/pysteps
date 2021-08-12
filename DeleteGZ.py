import os, glob
from multiprocessing import Pool, cpu_count

def delete(path):
	print(path)
	os.remove(path)
	
dir = '/usr1/home/nas-qnap/MRMS/*/*/*/'
filelist = glob.glob(os.path.join(dir, "*.gz"))

for f in filelist:
    delete(f)
""" 
pool = Pool(processes=cpu_count())
max_time_list = pool.map(os.remove, filelist)
pool.close()
"""
