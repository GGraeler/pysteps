#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed May 12 18:58:41 2021
 
@author: mfeldman
 
Thunderstorm Detection and Tracking - DATing
============================================
This example shows how to use the thunderstorm DATing module. The example is based on
MRMS radar data and uses the Cartesian composite of reflectivity on a
1 km grid.
The first section demonstrates thunderstorm cell detection and how to plot contours.
The second section demonstrates detection and tracking in combination,
as well as how to plot the resulting tracks.
@author: mfeldman
"""
################################################################################
# Import all required functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
import os
import sys
from datetime import datetime
from pprint import pprint
 
import matplotlib.pyplot as plt
import numpy as np
 
import pandas as pd
 
from pysteps import io, rcparams
from pysteps.feature import tstorm as tstorm_detect
from pysteps.tracking import tdating as tstorm_dating
from pysteps.utils import to_reflectivity
from pysteps.visualization import plot_precip_field, plot_track, plot_cart_contour
 
################################################################################
# Example with US MRMS data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# A series of 20 files containing MRMS Cartesian gridded rainrate are imported. Since the
# algorithm is tuned to Swiss max-reflectivity data, the rainrate is transformed to
# reflectivity.
# This example applies the algorithm that was developed on Swiss data to US MRMS data.
 
date = datetime.strptime("201908060020", "%Y%m%d%H%M")
data_source = rcparams.data_sources["mrms"]
 
root_path = data_source["root_path"]
path_fmt = data_source["path_fmt"]
fn_pattern = data_source["fn_pattern"]
fn_ext = data_source["fn_ext"]
importer_name = data_source["importer"]
importer_kwargs = data_source["importer_kwargs"]
timestep = data_source["timestep"]
 
###############################################################################
# Load the data from the archive
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
fns = io.archive.find_by_date(
    date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_next_files=2
)
print(fns)

importer = io.get_method(importer_name, "importer")
R, _, metadata = io.read_timeseries(fns, importer, **importer_kwargs)
#sh=np.shape(R)
#ARIZONA
# ln1=-116
# ln2=-107
# lt1=30
# lt2=38

Re=637
dLambda=(metadata['xpixelsize']*np.pi)/180.0
dPhi=(metadata['ypixelsize']*np.pi)/180.0
 
# x1=round((ln1-metadata['x1']+.005)/metadata['xpixelsize'])
# x2=round((ln2-metadata['x1']+.005)/metadata['xpixelsize'])
# y2=round((metadata['y2']-lt2+.005)/metadata['ypixelsize'])
# y1=round((metadata['y2']-lt1+.005)/metadata['ypixelsize'])
# print("COORDS", x1, x2, y2, y1)
# R_sub=R[:,y2:y1,x1:x2]
# lon1=metadata['x1']+x1*metadata['xpixelsize']
# lon2=metadata['x1']+x2*metadata['xpixelsize'
# lat1=metadata['y2']-y1*metadata['ypixelsize']
# lat2=metadata['y2']-y2*metadata['ypixelsize']
# print("LAT/LONS", lon1, lon2, lat1, lat2)
# sh=np.shape(R_sub)
# #
# metadata['x1']=lon
# metadata['x2']=lon2
# metadata['y1']=lat1
# metadata['y2']=lat2
 
# Method for calculating the lat/lon grid:

# import pyproj
# xr = np.arange(metadata["x1"], metadata["x2"], metadata["xpixelsize"])
# xr += 0.5 * (xr[1] - xr[0])
# yr = np.arange(metadata["y1"], metadata["y2"], metadata["ypixelsize"])
# yr += 0.5 * (yr[1] - yr[0])
# grid_x, grid_y = np.meshgrid(xr, yr)
# pr = pyproj.Proj(metadata["projection"])
# grid_lon, grid_lat = pr(grid_x, grid_y, inverse=True)
 
#Z, metadata = to_reflectivity(R_sub, metadata)
Z, metadata = to_reflectivity(R, metadata)
timelist = metadata["timestamps"]


 
pprint(metadata)
 
###############################################################################
# Example of thunderstorm identification in a single timestep.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The function tstorm_detect.detection requires a 2-D input image, all further inputs are
# optional.
 
 
input_image = Z[1, :, :].copy()
time = timelist[1]
cells_id, labels = tstorm_detect.detection(
    input_image, minsize=16, time=time, mindis=10, minref=40,
)
 
###############################################################################
# Example of thunderstorm tracking over a timeseries.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The tstorm-dating function requires the entire pre-loaded time series.
# The first two timesteps are required to initialize the
# flow prediction and are not used to compute tracks.
 
track_list, cell_list, label_list = tstorm_dating.dating(
    input_video=Z, timelist=timelist, dyn_thresh=True, minsize=16, mindis=10, minref=40,
)
 
###############################################################################
# Plotting the results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
# Plot precipitation field
plot_precip_field(Z[2, :, :], geodata=metadata, units=metadata["unit"])
 
# Add the identified cells
plot_cart_contour(cells_id.cont, geodata=metadata)
 
# Filter the tracks to only contain cells existing in this timestep
 
IDs = cells_id.ID.values
track_filt = []
for track in track_list:
    if np.unique(track.ID) in IDs:
        track_filt.append(track)

# Add their tracks
plot_track(track_filt, geodata=metadata)
plt.show()
"""
date2=str(date)
date3=date2[0:10]

count=0
c=[]
dfcopy=pd.DataFrame()
for p in track_list:
    sz=len(track_list[count])
    count=count+1
    c=np.concatenate((c, count*np.ones((sz), dtype=int)), axis=None)
    dfcopy=dfcopy.append(p)

 
pixels=dfcopy['y'].tolist()
areaList=[]
 
for w2 in pixels:
    area=0
    for w3 in w2:
        ny=np.shape(w2)
        laty=np.pi/180.0*(np.ones(ny[0])*metadata['y2']-np.float(w3)*metadata['ypixelsize'])
        cos=np.cos(laty)
        area=area+sum((Re**2)*cos*dLambda*dPhi)
    areaList.append(int(area))
    # pixelCount=len(w2)
    # pixelList.append(pixelCount)

cxlist=[]
for cx in dfcopy.cen_x:
    cx2=metadata['x1']+cx*metadata['xpixelsize']
    cxlist.append('%.3f' % cx2)

cylist=[]
for cy in dfcopy.cen_y:
    cy2=metadata['y2']-cy*metadata['ypixelsize']
    cylist.append('%.3f' % cy2)

dfcopy['ID']=c
dfcopy['area']=areaList
dfcopy.pop('cont')
dfcopy.pop('x')
dfcopy.pop('y')
dfcopy['cen_x']=cxlist
dfcopy['cen_y']=cylist
dfcopy.to_csv('Cell'+date3+'.csv',index=False)
"""
