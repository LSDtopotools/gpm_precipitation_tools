'''
process_timeseries_files_pipeline.py

Processes precipitation timeseries data from raster files downloaded from the
NASA GPM mission.

Author: Marina Ruiz Sánchez-Oro
Date: 17/01/2022
'''

import numpy as np
import xarray as xr
import rioxarray
import datetime
import re
import sys
import argparse
import glob
import os
import pandas as pd
from shapely.geometry import Point
from shapely.ops import transform
import pyproj

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file_folder", dest = "file_folder", help="Folder with the files")
parser.add_argument("-c", "--crs", dest = "crs", help="Coordinate system in the format EPSG:XXXX")
parser.add_argument("-x", "--x_lon",dest = "longitude", help="Longitude of point", type=int)
parser.add_argument("-y", "--y_lat",dest ="latitude", help="Latitude of point", type=int)
parser.add_argument("-t", "--time",dest = "time", help="Date time in format %Y-%m-%d:%H%M%S")#, type=int)

args = parser.parse_args()

file_folder = args.file_folder
coordinate = args.crs
x_lon_to_slice = args.longitude
y_lat_to_slice = args.latitude
time_to_slice = args.time
print(time_to_slice)
time_to_slice = datetime.datetime.strptime(time_to_slice, "%Y-%m-%d:%H%M%S")
print(type(time_to_slice))
print(time_to_slice)

# extract all raster files from the given folder
os.chdir(file_folder)
file_names = []
for file in glob.glob("*.bil"):
    file_names.append(file)



print(f'These are the files I am going to process: {file_names}')
print(f'file folder: {file_folder},\
 longitude: {x_lon_to_slice},\
  latitude: {y_lat_to_slice}, \
  full_date: {time_to_slice}')


def sort_file_list(file_list):
    """
    Sort list of files based on date given on the filename.

    Parameters
    ----------
    file_list : list of str
        List of files to sort.

    Returns
    ----------
    file_list_sorted : list of str
        List of sorted files.

    Author: MRSO
    """
    file_list_sorted=[]
    timeformat = "%Y%m%d" # this is how your timestamp looks like
    regex = re.compile("Calib_rainfall_([0-9]{8})-S([0-9]{6})")
    #Calib_rainfall_20140110-S000000-bil
    def gettimestamp(thestring):
        m = regex.search(thestring)
        print(m)
        return datetime.datetime.strptime(m.groups()[0], timeformat)

    for fn in sorted(file_list, key=gettimestamp):
        file_list_sorted.append(fn)
    return file_list_sorted




def extract_datetime_from_file(file_name):
    """
    Extract date from a file name and convert it to a datetime object.

    Parameters
    ----------
    file_name : str
        Name of file to extract date from.

    Returns
    ----------
    date_formatted : datetime
        Date extracted from filename.
    """
    date_file_1 = re.search("([0-9]{8})", file_name)
    hour_file_1 = re.search("(S[0-9]{6})",file_name)
    date_number_1 = date_file_1.group(0)
    hour_file_1 = hour_file_1.group(0)

    year = int(date_number_1[0:4])
    month = int(date_number_1[4:6])
    day = int(date_number_1[6:8])
    hour = int(hour_file_1[1:3])
    minute = int(hour_file_1[3:5])
    second = int(hour_file_1[5:7])
    date_formatted = datetime.datetime(year, month, day, hour, minute, second)
    return date_formatted


def output_precipitation_timeseries(lon, lat, netcdf_filename):
    """
    Extract a precipitation timeseries from a netCDF file given a lat, lon point.

    Parameters
    ----------
    lon : int
        Longitude.
    lat : int
        Latitude.
    netcdf_filename : str
        Name of netCDF (.nc) file to extract date from.

    Returns
    ----------
    precip_timeseries : list of int
        Timeseries of precipitation for the given lat, lon coordinates.
    """
    joint_ds = xr.open_dataset(netcdf_filename, engine="rasterio")
    precip_timeseries = joint_ds.sel(x=lon, y = lat, method="nearest").precipitation.to_numpy().ravel()
    return precip_timeseries

def output_precipitation_raster(time_to_slice, netcdf_filename):
    """
    Slice a netCDF file from a timeslice and create new netCDF file with the sliced data.

    Parameters
    ----------
    time_to_slice : datetime
        Date and time to slice from the data.
    netcdf_filename : str
        Name of netCDF (.nc) file to extract date from.

    Returns
    ----------
    None
    """
    # could potentially increase functionality by adding output data format: netcdf or raster
    joint_ds = xr.open_dataset(netcdf_filename, engine="rasterio")
    sliced_joint_ds = joint_ds.sel(time=time_to_slice).precipitation
    date_string_name = time_to_slice.strftime('%Y%m%d-%H%M%S')
    sliced_joint_ds.to_netcdf(f'output_precipitation_raster_{date_string_name}.nc', mode='w', format='NETCDF3_64BIT')
    #return sliced_joint_ds


def concatenate_raster_files(dataset_names, output_joint_file_name):
    """
    Read from a list of raster files, concatenate them along the time direction\
    and create a netCDF file.

    Parameters
    ----------
    dataset_names : list of str
        Names of the raster files to concatenate.
    output_joint_file_name : str
        Name of output file.

    Returns
    ----------
    joint_ds : xarray dataset
        Concatenated raster files.
    date_list : list of datetime
        Dates corresponding to the raster files.
    """
    joint_ds_list = []
    date_list = []
    for i in range(len(dataset_names)):
        date_file = re.search("([0-9]{8})", dataset_names[i])
        hour_file = re.search("(S[0-9]{6})", dataset_names[i])

        date_file = extract_datetime_from_file(dataset_names[i])

        xds = xr.open_dataset(dataset_names[i], engine="rasterio")
        # the spatial reference is the coordinate system information
        expanded_ds = xds.expand_dims("time").assign_coords(time=("time", [date_file]))
        expanded_ds = expanded_ds.drop('band')
        expanded_ds = expanded_ds.rename({'band_data':'precipitation'})
        joint_ds_list.append(expanded_ds)
        date_list.append(date_file)

    joint_ds = xr.concat(joint_ds_list, dim='time')
    joint_ds['precipitation'].attrs = {'description':'precipitation amount in mm/s'}
    joint_ds.to_netcdf(output_joint_file_name, mode='w', format='NETCDF3_64BIT')

    return joint_ds, date_list

def convert_crs_point(point_x, point_y, in_proj, out_proj):
    """
    Change the coordinate system of a lat, lon point.

    Parameters
    ----------
    point_x : int
        Longitude coordinate.
    point_y : int
        Latitude coordinate.
    in_proj : str
        Coordinate system to transform from.
    out_proj : str
        Coordinate system to transform to.

    Returns
    ----------
    AoI_point : shapely Point
        Lat, lon point in new coordinate system.
    """
    in_pt = Point(point_x, point_y)
    in_proj = pyproj.CRS(in_proj)
    out_proj = pyproj.CRS(out_proj)
    project =  pyproj.Transformer.from_crs(in_proj, out_proj, always_xy=True).transform
    AoI_point = transform(project, in_pt)
    return AoI_point

# first we need to convert the point to the coordinate system that we want.
# need to first check what the coordinate system of the area is



file_names_sorted = sort_file_list(file_names)

print(f'These are the files I am going to concatenate: {file_names}')
output_joint_file_name = 'joint_ds_with_all_times.nc'


joint_ds, date_list = concatenate_raster_files(file_names_sorted, output_joint_file_name)
print(f'I have concatenated all your files and created a time series')

print(f'This is the date list: {date_list}')

# need to make this better as this is not necessarily the closest point
time_selected = joint_ds.sel(time=time_to_slice)

# first we need to convert the point to the coordinate system that we want.
# need to first check what the coordinate system of the area is

joint_ds = xr.open_dataset('joint_ds_with_all_times.nc', engine="rasterio")
raster_crs = joint_ds.rio.crs

converted_lat_lon = convert_crs_point(x_lon_to_slice, y_lat_to_slice, coordinate, raster_crs)
x_converted = round(converted_lat_lon.x, 2)
y_converted = round(converted_lat_lon.y,2)


timeseries=output_precipitation_timeseries(x_converted, y_converted, output_joint_file_name)

timeseries_df = pd.DataFrame(timeseries, columns=['precipitation_mm/s'])
# need to add time datetime column
timeseries_df['date'] = pd.to_datetime(date_list)
timeseries_df = timeseries_df.set_index('date')
timeseries_df = timeseries_df.sort_values(by='date')
print(timeseries_df.head)

timeseries_df.to_csv(f'precipitation_timeseries_point_lon_{x_lon_to_slice}_lat_{y_lat_to_slice}.csv')

output_precipitation_raster(time_to_slice, output_joint_file_name)
