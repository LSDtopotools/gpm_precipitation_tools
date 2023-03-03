"""
gpm_download_day_V06B.py
Tools to download daily data downloaded from NASA GPM mission website (This version is for the V06 of GESDIS).

The files in this tool are a modified version of the PPTs tool presented here: https://github.com/lapig-ufg/PPTs

Authors: Marina Ruiz Sánchez-Oro, Guillaume Goodwin
Date: 03/03/2023
"""



################################################################################
################################################################################
"""Import Python packages"""
################################################################################
################################################################################

import os
import sys
import argparse
import time
import shutil
import re
import numpy
import glob
import tkinter
from tkinter import filedialog
import platform
import argparse
import datetime
from osgeo import gdal, ogr, osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import csv
from pathlib import Path
import pandas as pd
import rasterio

################################################################################
################################################################################
"""Import internal modules"""
################################################################################
################################################################################

#GPM MONTH
from gpm_precipitation_tools.gpm_download_month_V06B import gpm_month_download
#GPM DAY
from gpm_precipitation_tools.gpm_download_day_V06B import gpm_day_download
#GPM 30min
from gpm_precipitation_tools.gpm_download_30min_V06B import gpm_30min_download

#AncillaryData
from gpm_precipitation_tools.image_process import process


################################################################################
################################################################################
"""Argument Parser"""
################################################################################
################################################################################

def parseArguments():

	parser = argparse.ArgumentParser(prog='Precipitation Processing Tool')

	parser.add_argument('--ProdTP', choices= ['GPM_M','GPM_D','GPM_30min'], default='GPM_30min', dest='ProdTP',  help='GPM_M: GPM Monthly (IMERGM v6);\n GPM_D: GPM Daily (IMERGDF v6); \n GPM_30min: GPM Half-hourly (IMERGHHE v6)\n')

	StartDF = '01-06-2000'
	parser.add_argument('--StartDate',dest='StartDate', help='Insert the start date',default=StartDF,type=str)

	EndDF = str((datetime.datetime.now()).strftime('%Y-%m-%d'))
	parser.add_argument('--EndDate',dest='EndDate', help='Insert the end date',default=EndDF,type=str)

	parser.add_argument('--ProcessDir',dest='ProcessDir', help='Insert the processing directory path',type=str)

	parser.add_argument('--SptSlc',dest='SptSlc', nargs="?", help='Insert the slice feature path',type=str)

	parser.add_argument('--OP', dest='OP',action="store_true", help='Call this argument if you only want to process the data. Make sure you have a directory with a raw files subfolder.')

	args = parser.parse_args();
	return args


################################################################################
################################################################################
"""Argument Parser"""
################################################################################
################################################################################

def parse_add_rainfall_Arguments():

	parser = argparse.ArgumentParser(prog='Precipitation Processing Tool')

	parser.add_argument('--base_rainfall', dest='base_r', help='Insert the pathway to the base rainfall file',type=str)

	parser.add_argument('--supp_rainfall', dest='supp_r', help='Insert the pathway to the supplemental rainfall file',type=str)

	parser.add_argument('--output_file', dest='output_f', help='Insert the pathway to the output file',type=str)

	args = parser.parse_args();
	return args


################################################################################
################################################################################
def ENVI_raster_binary_to_2d_array(file_name):
    """
    This function transforms a raster into a numpy array.
    Args:
        file_name (ENVI raster): the raster you want to work on.
        gauge (string): a name for your file
    Returns:
        image_array (2-D numpy array): the array corresponding to the raster you loaded
        pixelWidth (geotransform, inDs) (float): the size of the pixel corresponding to an element in the output array.
    Source: http://chris35wills.github.io/python-gdal-raster-io/
    """


    driver = gdal.GetDriverByName('ENVI')

    driver.Register()

    inDs = gdal.Open(file_name, GA_ReadOnly)

    if inDs is None:
        print ("Couldn't open this file: " + file_name)
        print ("Perhaps you need an ENVI .hdr file? ")
        sys.exit("Try again!")
    else:
        print ("%s opened successfully" %file_name)

        #print '~~~~~~~~~~~~~~'
        #print 'Get image size'
        #print '~~~~~~~~~~~~~~'
        cols = inDs.RasterXSize
        rows = inDs.RasterYSize
        bands = inDs.RasterCount

        #print "columns: %i" %cols
        #print "rows: %i" %rows
        #print "bands: %i" %bands

        #print '~~~~~~~~~~~~~~'
        #print 'Get georeference information'
        #print '~~~~~~~~~~~~~~'
        geotransform = inDs.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]

        #print "origin x: %i" %originX
        #print "origin y: %i" %originY
        #print "width: %2.2f" %pixelWidth
        #print "height: %2.2f" %pixelHeight

        # Set pixel offset.....
        #print '~~~~~~~~~~~~~~'
        #print 'Convert image to 2D array'
        #print '~~~~~~~~~~~~~~'
        band = inDs.GetRasterBand(1)
        #print band
        image_array = band.ReadAsArray(0, 0, cols, rows)
        image_array_name = file_name
        #print type(image_array)
        #print image_array.shape

        return image_array, pixelWidth, (geotransform, inDs)


def extract_rainfall_pxl_values(working_dir):

	# incomplete functionality...
	print('I am going to extract the rainfall values for each pixel for you')
	files = sorted(os.listdir(working_dir)); bilfiles = []

	for i in range(len(files)):
		ending = files[i][-4:]
		print(f"i am the ending: {ending}")
		if ending == '.bil':
			bilfiles.append(files[i])
	print(bilfiles)

	# make an empty csv files with the columns to be y_lat, x_lon, rainfall_mm_sec
	dir = Path(working_dir)

	#df=pd.DataFrame(columns=["lat","lon"])
	#df.to_csv(working_dir+'in.csv', index=False)
	incsvfile = working_dir+'in.csv'
	outcsvfile = working_dir+'out.csv'


	with open(incsvfile) as incsvfile, open(outcsvfile, 'w', newline='') as outcsvfile:
	    csvreader = csv.reader(incsvfile)
	    #print(csvreader)
	    csvwriter = csv.writer(outcsvfile)

	    fieldnames = next(csvreader)
	    print(fieldnames)
	    csvwriter.writerow(fieldnames)

	    datasets = [rasterio.open(dir/raster) for raster in bilfiles]
	    #print(dir/raster)
	    #print(datasets)

	    for lat, lon in csvreader:
	        print('hi')
	        values = []
	        for src in datasets:
	            values.append(next(src.sample([[float(lon), float(lat)]]))[0])
	            print(f'values: {values}')

	        csvwriter.writerow([lat, lon] + values)


#extract_rainfall_pxl_values('../../GPM_RAW_DAY_2016-01-01_2016-01-04_processed/run_start_2016-01-01_end_2016-01-04/')



def maps_to_timeseries(arglist, working_dir, data_product):
	# List the .bil files
	print('Got to the timeseries function')
	files = sorted(os.listdir(working_dir)); bilfiles = []

	for i in range(len(files)):
		ending = files[i][-4:]
		print(f"i am the ending: {ending}")
		if ending == '.bil':
			bilfiles.append(files[i])
	print(bilfiles)


	#Timelist = []
	#CumTimelist = []
	#Intlist = []
	Full_list = []
	thirty_one_day_months = [1,3, 5, 7, 8, 10, 12]
	thirty_day_months = [4, 6, 9, 11]
	february_special_month = [2]
	for i in range(len(bilfiles)):
		print (bilfiles[i])
		leap_year = False
		file_ending = bilfiles[i].split('/')[-1]
		if file_ending[-8:] == '_cut.bil':
			timer = datetime.datetime.strptime(bilfiles[i], 'Calib_rainfall_%Y%m%d-S%H%M%S-V06B_cut.bil')
			month = timer.month
			year = timer.year
			if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
				leap_year = True
		else:
			print('I am not the right file')
			pass
		# Add to the rainfall list
		Rainarr, pixelWidth, (geotransform, inDs) = ENVI_raster_binary_to_2d_array(working_dir + bilfiles[i])
		print(Rainarr)
		# takes the average over the whole raster image
		Rain = numpy.mean(Rainarr)
		if data_product == 'GPM_30min':
			converting_factor = 30*60 # seconds in 30 minutes
		elif data_product == 'GPM_D':
			converting_factor = 24*3600 # seconds in a day
		else:
			if month in thirty_day_months:
				converting_factor = 30*24*3600 # seconds in a month
				print('I have 30 days')
			elif month in thirty_one_day_months:
				converting_factor = 31*24*3600 # seconds in a month
				print('I have 31 days')
			else:
				if leap_year == True:
					print('I am february in a leap year ')
					converting_factor = 29*24*3600 # seconds in a month
				else:
					print('I am february in a non-leap year')
					converting_factor = 28*24*3600 # seconds in a month
		Intensity = Rain/(converting_factor) # Intensity of rainfall during the period (mm/sec) - converted from mm
		#Intlist.append(Intensity)

		# Save it all together
		Full_list.append([converting_factor, Intensity])

	# Now save the stuff
	with open(working_dir+arglist[1]+"_to_"+arglist[2]+"_"+arglist[0]+"_rainfall.csv", "w", newline="") as f:
	    writer = csv.writer(f)
	    writer.writerow(['duration_s','rainfall_mm_sec'])
	    writer.writerows(Full_list)
	print ('DOOOOONE')
	print (working_dir)


def move_files(path_to_target, start_date, end_date):
	files_to_move = []
	path_to_bil_file_list = glob.glob(path_to_target + '*bil' )
	path_to_hdr_file_list = glob.glob(path_to_target + '*hdr' )
	path_to_nc4_file_list = glob.glob(path_to_target + '*nc4' )
	path_to_hdf5_file_list = glob.glob(path_to_target + '*hdf5' )
	files_to_move.extend(path_to_bil_file_list)
	files_to_move.extend(path_to_hdr_file_list)
	files_to_move.extend(path_to_nc4_file_list)
	files_to_move.extend(path_to_hdf5_file_list)
	new_directory = path_to_target+'run_start_'+start_date+'_end_'+end_date

	# Check whether the specified path exists or not
	isExist = os.path.exists(new_directory)
	if not isExist:
		# Create a new directory because it does not exist
		os.mkdir(new_directory)
		print("The new directory is created!")

	for path_to_file in files_to_move:
		file_name = os.path.basename(path_to_file)
		shutil.move(path_to_file, new_directory+'/'+file_name)




################################################################################
################################################################################

def download_months(arglist, zero_list, zero_dir, fst_dir, backslh, n):
	if zero_list[n].endswith('.HDF5') > -1 and zero_list[n].find('.xml') == -1 and zero_list[n].find('.aux') == -1 and zero_list[n].find('.tfw') == -1:
			if 	zero_list[n].find('.HDF5') > -1:
				#extract_subdata = 'HDF5:"%s%s%s"://Grid/precipitation' % (zero_dir,backslh,zero_list[n])
				extract_subdata = "%s%s%s" % (zero_dir,backslh,zero_list[n])
				outfile = '%s%s%s.tif' % (fst_dir,backslh,zero_list[n][:-5])
				print(f'this is the outfile: {outfile}')

				process(outfile,extract_subdata,arglist[0])
				raster_crop(arglist, outfile)
				extract_subdata = outfile = None


def download_days(arglist, zero_list, zero_dir, fst_dir, backslh, n):
	if zero_list[n].endswith('.nc4') > -1 and zero_list[n].find('.xml') == -1 and zero_list[n].find('.aux') == -1 and zero_list[n].find('.tfw') == -1:
			#extract_subdata = 'HDF5:"%s%s%s"://precipitationCal' % (zero_dir, backslh, zero_list[n])
			extract_subdata = "%s%s%s" % (zero_dir,backslh,zero_list[n])
			print(f'this is extract_subdata: {extract_subdata}')
			outfile = '%s%s%s_precipitationCal.tif' % (fst_dir,backslh, zero_list[n][:-4])
			print(f'this is the outfile: {outfile}')

			process(outfile,extract_subdata,arglist[0])
			raster_crop(arglist, outfile)
			extract_subdata = outfile = None



def download_hhs(arglist, zero_list, zero_dir, fst_dir, backslh, n):
	if zero_list[n].endswith('.HDF5') > -1 and zero_list[n].find('.xml') == -1 and zero_list[n].find('.aux') == -1 and zero_list[n].find('.tfw') == -1:
		if 	zero_list[n].find('.HDF5') > -1:
			extract_subdata = "%s%s%s" % (zero_dir,backslh,zero_list[n])
			#extract_subdata = 'HDF5:"%s%s%s"://Grid/precipitation' % (zero_dir,backslh,zero_list[n])
			outfile = '%s%s%s.bil' % (fst_dir,backslh,zero_list[n][:-5])
			print(f'this is the outfile: {outfile}')

			process(outfile,extract_subdata,arglist[0])
			raster_crop(arglist, outfile)
			extract_subdata = outfile = None



########
# Crop the raster
########
def raster_crop(arglist, outfile):
	if arglist[4] != 'None':
		cutfile = arglist[4]
		to_cut = outfile
		print(f'cutfile file: {cutfile}')
		print(f'to_cut file: {to_cut}')
		cutted_file = outfile[:-4] + '_cut.bil'
		print(f'cutted file: {cutted_file}')

		# Find out the file path
		f_path_str = cutted_file.rsplit('/',1)[0]
		print(f'f_name {f_path_str}')
		f_path = f_path_str+'/'
		print(f'f_path {f_path}')

		# Create the file name from existing file
		f_name_str = cutted_file.rsplit('/',1)[-1]
		f_name_str_split = f_name_str.split('.')
		print(f_name_str_split)
		date_str = f_name_str_split[4][:16]
		print(f'date_str {date_str}')
		end_string = f_name_str_split[6]
		print(f'end_string {end_string}')
		# the end results of the cutted file should be:
		## A = split the file. we want only the stuff on the first chunk - this will have path info
		## AA = 1 (name directory where we find the data)
		## AAA = /1/ (add the slashes to make up the path)
		## B = 20180101 (the date) - we also want to include the time if it's 30m
		## BB = 'V06B_cut' - the final extension before the file type.



		cutted_file = f_path + 'Calib_rainfall_' + date_str + '-' + end_string + '.bil'

		# Cut the raster to your desired extent
		os.system('gdalwarp -overwrite -of ENVI -t_srs EPSG:4326 -cutline ' + cutfile + ' -crop_to_cutline ' + to_cut + ' ' + cutted_file)
		# Get rid of the big files
		os.system('rm ' + outfile)
		os.system('rm ' + cutted_file+'.aux.xml')
		os.system('rm ' + outfile[:-4] + '.hdr')
