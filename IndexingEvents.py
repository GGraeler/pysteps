import pandas as pd
import os
import glob
import csv
from datetime import datetime

new_csv = pd.DataFrame()

for file in glob.glob('/usr1/home/emsuser/Tracks/*.csv'):
    carter = pd.read_csv(file)
    new_csv = new_csv.append(carter)

new_csv.drop('cont', inplace=True, axis=1)
new_csv.to_csv('Tracks2015.csv')
print(new_csv)

