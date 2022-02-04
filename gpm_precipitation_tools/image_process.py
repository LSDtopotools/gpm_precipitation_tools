"""
image_process.py
Tools to process the data downloaded from NASA GPM mission website.

The files in this tool are a modified version of the PPTs tool presented here: https://github.com/lapig-ufg/PPTs

Authors: Guillaume Goodwin, Marina Ruiz Sánchez-Oro
Date: 03/02/2022
"""
################################################################################
################################################################################
"""Import Python packages"""
################################################################################
################################################################################



import os
import sys
import string
import argparse
import time
import subprocess
import shutil
import string
import numpy
import re
import numpy as np
from osgeo import gdal, ogr, osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *


def process(out_dir,data_file,dataInfo):
	print ()
	print ('PROCESSING')
	print (out_dir)
	print (f'file name: {data_file}')
	print (dataInfo)
	print()


	hourFactor = None

	if dataInfo in ['GPM_D','GPM_30min']:
		hourFactor = 1

	elif dataInfo == 'GPM_M':
		# we need to split also the directory
		fileName = (str(data_file).split("\\")[-1]).split('/')[-1]#.split('"')[1].split('/')[-1]
		print(f'this is the filename: {fileName}')


		if str(fileName[20:28]) == '20140312':
			hourFactor = 456

		elif (int(fileName[20:24]) % 4) == 0:
					if (fileName[24:26]) == '02':
						hourFactor = 696

					elif (fileName[24:26]) in ['01','03','05','07','08','10','12']:
						hourFactor = 744

					elif (fileName[24:26]) in ['04','06','09','11']:
						hourFactor = 720

		elif (fileName[24:26]) == '02':
			hourFactor = 672

		elif (fileName[24:26]) in ['01','03','05','07','08','10','12']:

			hourFactor = 744

		elif (fileName[24:26]) in ['04','06','09','11']:
			hourFactor = 720



	fname = str(data_file)
	outname = str(out_dir)
	outfile =  outname #[:-4].replace(".", "")
	data_file_no_extension = os.path.splitext(data_file)[0]
	#outfile = outfile + '.bil'

	#####################################
	# 0. Make the HDF5 file into a .tif containing the calibrated precipitation
	#####################################
	print (f"data file name:{data_file}")
	print(f'This is the data file no extension: {data_file_no_extension}')
	#quit()
	if dataInfo == 'GPM_30min':
		os.system('gdal_translate -of GTiff HDF5:' + data_file + '://Grid/precipitationCal ' + data_file_no_extension + '.tif')
	elif dataInfo == 'GPM_D':
		os.system('gdal_translate -of GTiff HDF5:' + data_file + '://precipitationCal ' + data_file_no_extension + '.tif')
	else:
		os.system('gdal_translate -of GTiff HDF5:' + data_file + '://Grid/precipitation ' + data_file_no_extension + '.tif')

	print('done converting')
	print(' I can do my job up to here. I am not a complete failure yay!')


	#####################################
	# 1. The produced .tif file is rotated 90° so we must rotated back and assign a correct projection
	# While we're at it, let's amke it a .bil file
	#####################################

	print ('transposing and projecting into ', outfile)

	# Open the created .tif
	ds = gdal.Open(data_file_no_extension + '.tif')

	# Find out its transformation
	#gt=ds.GetGeoTransform()

	# Extract the band you need
	band = ds.GetRasterBand(1)
	print('done extracting band')



	arr = band.ReadAsArray()
	TPSGPM = rot90(arr,1)
	TPSGPM = ((TPSGPM.astype(float))> 0)*((TPSGPM.astype(float))*hourFactor) + ((TPSGPM.astype(float))< 0)*0

	# Set the driver
	driver = gdal.GetDriverByName("ENVI")
	print('set the driver')

	# Set the extents and pixel sizes. That will be the tricky part
	x_pixels = ds.RasterYSize  # number of pixels in x
	y_pixels = ds.RasterXSize  # number of pixels in y
	# WHY THE SWITCH? WE ROTATED THE TPSGPM ArrAY, REMEMBER?

	# x_min & y_max are like the "top left" corner. In WGS84, these are:
	x_min = -180; x_max = 180
	y_max = 90; y_min = -90

	# Pixels need to cover the entire extent
	X_PXL_SIZE = (x_max - x_min) / x_pixels # size of the X pixels
	Y_PXL_SIZE = (y_max - y_min) / y_pixels  # size of the Y pixels
	print('calculated raster properties')


	#wkt_projection = 'a projection in wkt that you got from other file'

	# Create the dataset
	dataset = driver.Create(
		outfile,
        x_pixels,
        y_pixels,
        1,
        gdal.GDT_Float32, )
	print('created driver')

	# Define the GeoTransform

	dataset.SetGeoTransform((
        x_min,    # 0
        X_PXL_SIZE,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        -Y_PXL_SIZE))



	# Define the target srs
	print('creating srs')
	srs = osr.SpatialReference()
	srs.ImportFromEPSG(4326)
	dataset.SetProjection(srs.ExportToWkt())
	print('writing to band')




	# Write array to band
	dataset.GetRasterBand(1).WriteArray(TPSGPM)
	print('save to disk')

	# Save to disk
	dataset.FlushCache()  # Write to disk.
	print('remove tif file')

	# remove the annoying tif file
	os.system('rm ' + data_file_no_extension + '.tif')
	print('Done removing')
	print('Script image_process.py is working fine')
