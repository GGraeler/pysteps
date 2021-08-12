"""
Thunderstorm Detection and Tracking - DATing
============================================
This example shows how to use the thunderstorm DATing module. The example is based on
MRMS radar data and uses the Cartesian composite of reflectivity on a
1 km grid.

The first section demonstrates thunderstorm cell detection and how to plot contours.
The second section demonstrates detection and tracking in combination,
as well as how to plot the resulting tracks.

Original code by mfeldman
12 May 2021

Modified by Carter Humphreys, Greta Graeler
12 July 2021
"""

import os
import sys
from datetime import datetime
from pprint import pprint

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pysteps import io, rcparams
from pysteps.feature import tstorm as tstorm_detect
from pysteps.tracking import tdating as tstorm_dating
from pysteps.utils import to_reflectivity
from pysteps.visualization import plot_precip_field, plot_track, plot_cart_contour

class Tracks:

    def __init__(self, files, importer_name='mrms_grib', importer_kwargs=None, minref=40):
        """
        initializes track object with configuration
        """
        self.fns = files
        self.importer_name = importer_name
        self.importer_kwargs = importer_kwargs
        self.minref = minref

    def execute(self):
        """
        Handles the executation of the methods to generate storm tracks from MRMS data
        """
        # Load reflectivity from MRMS PrecipRate
        self.load_data()
        print('complete load_data')
        # Indentify cells
        self.cell_id(minref=self.minref)
        print('complete cell_id')
        # Calculate tracks
        self.calculate_tracks(minref=self.minref)
        print('complete calc_tracks')
        # Create plots
        #self.create_plot()

        # Generate output DataFrame
        self.build_dataframe()
        print('complete build_df')

    def load_data(self):
        """
        Runs importer MRMS grib importer to load data, then converts PrecipRate to reflectivity
        """
        # Run MRMS importer
        importer = io.get_method(self.importer_name, "importer")
        R, _, metadata = io.read_timeseries(self.fns, importer, **self.importer_kwargs)

        # Convert from PrecipRate to reflectivity
        Z, metadata = to_reflectivity(R, metadata)
        timelist = metadata["timestamps"]

        # Update instance variables with reflectivity and metadata
        self.Z = Z
        self.metadata = metadata

        pprint(self.metadata)

    def cell_id(self, minref, index=0):
        """
        Thunderstorm identification in a single timestep. The function tstorm_detect.detection requires
        a 2-D input image, all further inputs are optional.
        """
        input_image = self.Z[1, :, :].copy()
        time = self.metadata["timestamps"][index]

        # Get cells for timestamp
        data = tstorm_detect.detection(input_image, minsize=16, time=time, mindis=10, minref=minref)

        # Update instance variables
        self.cells_id, self.labels = data
        
        #print('SIZE: ', df.size)

    def calculate_tracks(self, minref):
        """
        Thunderstorm tracking over a timeseries. The tstorm-dating function requires the entire pre-loaded time series.
        The first two timesteps are required to initialize the flow prediction and are not used to compute tracks.
        """
        # Get storm tracks
        timelist = self.metadata["timestamps"]
        data = tstorm_dating.dating(input_video=self.Z, timelist=timelist, dyn_thresh=True, minsize=16, mindis=10, minref=minref)

        # Update instance variables
        self.track_list, self.cell_list, self.label_list = data

    def create_plot(self):
        """
        Creates plot of the resulting data
        """
        # Plot precipitation field
        plot_precip_field(self.Z[0, :, :], geodata=self.metadata, units=self.metadata["unit"])

        # Add the identified cells
        plot_cart_contour(self.cells_id.cont, geodata=self.metadata)

        # Filter the tracks to only contain cells existing in this timestep
        IDs = self.cells_id.ID.values
        track_filt = []
        for track in self.track_list:
            if np.unique(track.ID) in IDs:
                track_filt.append(track)

        # Add their tracks
        plot_track(track_filt, geodata=self.metadata)


        # Update instance variables
        self.plt = plt
        self.plt.show()

    def build_dataframe(self):
        """
        Builds a Pands DataFrame of output
        """
        # Calculation data
        track_list = self.track_list
        metadata = self.metadata

        # Constants
        Re = 637
        dLambda = (metadata['xpixelsize'] * np.pi) / 180.0
        dPhi = (metadata['ypixelsize'] * np.pi) / 180.0

        # Create an empty Pands DataFrame
        df = pd.DataFrame()

        # Get track IDs
        idList = []
        for p, i in zip(track_list, range(len(track_list))):
            sz=len(track_list[i])
            idList=np.concatenate((idList, i*np.ones((sz), dtype=int)), axis=None)
            df=df.append(p)
        
        # Calculate cell areas
        pixels = df['y'].tolist()
        areaList = []
        for w2 in pixels:
            area = 0
            for w3 in w2:
                ny=np.shape(w2)
                laty=np.pi/180.0*(np.ones(ny[0])*metadata['y2']-np.float(w3)*metadata['ypixelsize'])
                cos=np.cos(laty)
                area=area+sum((Re**2)*cos*dLambda*dPhi)
            areaList.append(int(area))

        # Create list of cell center longitudes
        cxList = []
        for cx in df.cen_x:
            cx2 = metadata['x1']+cx*metadata['xpixelsize']
            cxList.append('%.3f' % cx2)

        # Create list of cell center latitudes
        cyList = []
        for cy in df.cen_y:
            cy2 = metadata['y2']-cy*metadata['ypixelsize']
            cyList.append('%.3f' % cy2)

        # Add cell id, area, laitude, and longitude to DataFrame
        df['ID'] = idList
        df['area'] = areaList
        df['cen_x'] = cxList
        df['cen_y'] = cyList

        # Drop x and y lists from DataFrame
        df.drop('x', inplace=True, axis=1)
        df.drop('y', inplace=True, axis=1)
        df.drop('cont', inplace=True, axis=1)

        # Update instance DataFrame
        self.df = df
        
