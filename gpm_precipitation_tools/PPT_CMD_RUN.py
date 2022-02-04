"""
PPT_CMD_RUN.py
This is the master file for the command line tool.
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
import argparse
import time
import shutil
import re
import numpy
import tkinter
from tkinter import filedialog
import platform
import argparse
import datetime
from osgeo import gdal, ogr, osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import csv



################################################################################
################################################################################
"""Import internal modules"""
################################################################################
################################################################################

#GPM MONTH
#from gpm_download_month_V06B import gpm_month_download
from gpm_download_month_V06B import *
#GPM DAY
from gpm_download_day_V06B import gpm_day_download
#GPM 30min
from gpm_download_30min_V06B import gpm_30min_download

#AncillaryData
from image_process import process
#from get_info import get_info
import General_functions as fn




################################################################################
################################################################################
"""Identify system"""
################################################################################
################################################################################

def system_os():
	if platform.system() == 'Windows':
		return 1
	else:
		return 2

global backslh
global input_dir_data

if system_os() == 1:
	backslh = '\\'
else:
	backslh = '/'


################################################################################
################################################################################
"""Parse Arguments"""
################################################################################
################################################################################

args = fn.parseArguments()

if args.OP == '':
	args.OP == False

arglist = [args.ProdTP,args.StartDate,args.EndDate,args.ProcessDir,args.SptSlc,args.OP]
print(arglist)




################################################################################
################################################################################
"""Check Arguments"""
################################################################################
################################################################################


if arglist[3] == None:

	try:
		input_dir_data = filedialog.askdirectory(initialdir="/",title='Please choose an output directory')
		if len(input_dir_data) == 0:
			raise IOError
		if system_os() == 1:
			input_dir_data = str(input_dir_data).replace('/', '\\')
		else:
			input_dir_data = input_dir_data

	except:
		print ("ERROR! You did not choose a directory.")
		sys.exit(2)
else:

	if system_os() == 1:
		input_dir_data = str(arglist[3])
		input_dir_data = input_dir_data.replace('/',backslh)
	else:
		input_dir_data = str(arglist[3])



################################################################################
################################################################################
"""Create directory structure"""
################################################################################
################################################################################

download_dir = None
DirEnd = None

if arglist[0] == 'GPM_M':
	create_dir = 'GPM_RAW_MONTH_'+arglist[1]+'_'+arglist[2]; dwnld = gpm_month_download
elif arglist[0] == 'GPM_D':
	create_dir = 'GPM_RAW_DAY_'+arglist[1]+'_'+arglist[2]; dwnld = gpm_day_download
elif arglist[0] == 'GPM_30min':
	create_dir = 'GPM_RAW_30min_'+arglist[1]+'_'+arglist[2]; dwnld = gpm_30min_download
else:
	print ("Please tell me what to download")
	sys.exit(2)

try:
	os.mkdir(input_dir_data + backslh + create_dir)
except:
	pass

download_dir = input_dir_data + backslh + create_dir
print(f'this is the download dir: {download_dir,backslh,arglist[1],arglist[2]}')

if arglist[5] == False:
	dwnld(download_dir,backslh=backslh,Start_Date = arglist[1],End_Date = arglist[2])
DirEnd = create_dir

zero_dir = download_dir#[:-1]
process_dir = input_dir_data + backslh + DirEnd + "_processed"

try:
	os.mkdir(process_dir)
except:
	print (process_dir + "_processed"+": this directory already exists")



################################################################################
################################################################################
"""Download the files"""
################################################################################
################################################################################


zero_list = os.listdir(zero_dir)
zero_list = sorted(zero_list, key = lambda x: x.rsplit('.', 1)[0])
print(f'I am zero list: {zero_list}')
print(f'i am arglist {arglist}')

if arglist[0] == 'GPM_M': # We do not expect this case to arise in our use case
	for n in range(0,len(zero_list),1):
		fn.download_months(arglist, zero_list, zero_dir, process_dir, backslh, n)



elif arglist[0] == 'GPM_D': # We do not expect this case to arise in our use case
	print('hello from GPM_D')
	for n in range(0,len(zero_list),1):
		print('I shall start the downlad')
		fn.download_days(arglist, zero_list, zero_dir, process_dir, backslh, n)
		print('done with download_days')



elif arglist[0] == 'GPM_30min':
	for n in range(0,len(zero_list)-1,1):
		fn.download_hhs(arglist, zero_list, zero_dir, process_dir, backslh, n)
		print('done with download_hhs')



else:
	print ("ERROR")
	sys.exit(2)


#######################################################################
# Transform into a time series
#######################################################################

# Where are the .bil files?
working_dir = process_dir + backslh #'./1/'
print(f'working dir: {working_dir}')

fn.maps_to_timeseries(arglist, working_dir, arglist[0])

fn.move_files(working_dir, arglist[1], arglist[2])
print(f'input dir data: {input_dir_data}')
