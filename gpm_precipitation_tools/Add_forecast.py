"""
Add_forecast.py

Authors: Guillaume Goodwin
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
import pandas as pd


################################################################################
################################################################################
"""Import internal modules"""
################################################################################
################################################################################

#GPM MONTH
from gpm_download_month_V06B import gpm_month_download
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
"""Parse Arguments"""
################################################################################
################################################################################

args = fn.parse_add_rainfall_Arguments()

arglist = [args.base_r,args.supp_r,args.output_f]
print('Found the files to combine!')



# Read in the rainfall file and write to arrays
base_rain = pd.read_csv(arglist[0])
rain_time = base_rain['duration_s'].to_numpy()
rain_intensity = base_rain['intensity_mm_sec'].to_numpy()

# Read in the supplemental rainfall file
supp_rain = pd.read_csv(arglist[1])

# Check they are in the same same time durations
if supp_rain['duration_s'][0] == rain_time[0]:
    print("Both durations are the same, {} seconds".format(str(rain_time[0])))
else:
    print("The durations are different, base time is: {} and supplemental time is {} did you intend this?".format(str(rain_time[0]),str(supp_rain['duration_s'][0])))

# Append the new data
for i in range(0,len(supp_rain)):
    rain_time = numpy.append(rain_time,supp_rain['duration_s'][i])
    rain_intensity = numpy.append(rain_intensity,supp_rain['intensity_mm_sec'][i])
    print(i)

output_data =numpy.column_stack([rain_time, rain_intensity])
# Now save the stuff
with open(arglist[2], "w", newline="") as f:
	    writer = csv.writer(f)
	    writer.writerow(['duration_s','intensity_mm_sec'])
	    writer.writerows(output_data)
