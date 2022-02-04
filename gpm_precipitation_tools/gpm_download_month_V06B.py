
"""
gpm_download_month_V06B.py
Tools to download monthly data downloaded from NASA GPM mission website (This version is for the V06 of GESDIS).

The files in this tool are a modified version of the PPTs tool presented here: https://github.com/lapig-ufg/PPTs

Authors: Marina Ruiz Sánchez-Oro, Guillaume Goodwin
Date: 03/02/2022
"""



#http://stackoverflow.com/questions/10875215/python-urllib-downloading-contents-of-an-online-directory
#http://stackoverflow.com/questions/4589241/downloading-files-from-an-http-server-in-python
#http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
#http://stackoverflow.com/questions/34831770/download-a-file-in-python-with-urllib.request-instead-of-urllib
#http://stackoverflow.com/questions/25501090/how-to-get-wget-command-info-with-python


################################################################################
################################################################################
"""Import Python packages"""
################################################################################
################################################################################


import sys
import os
import re
import string
import datetime
import numpy as np
from urllib.request import urlopen

from Login_UI import retrieveLogin

def what_files_to_keep_case_1(mylist,start_month_download,end_month_download, items_to_keep):
    # for the first year of the data required, given the end date is also in that year and there is only one year to take data from
    for item in range(0,len(mylist)):
        month_of_file = int(mylist[item].split(".")[-3])
        item_name = mylist[item]
        if ((month_of_file >= start_month_download) and (month_of_file <= end_month_download)):
            print(f'i am keeping month{month_of_file}')
            print(f'item_name:{str(item_name)}')
            items_to_keep.append(item_name)
        else:
            print(f'i am not keeping{month_of_file}')
            print(f'item name: {item_name}')
    return items_to_keep


def what_files_to_keep_case_2(mylist, start_month_download, items_to_keep):
    # first year but there are more years to come. Download ends in month 12 instead in End_month.
    for item in range(0,len(mylist)):
        month_of_file = int(mylist[item].split(".")[-3])
        item_name = mylist[item]
        if ((month_of_file >= start_month_download)):
            print(f'i am keeping month{month_of_file}')
            print(f'item_name:{str(item_name)}')
            items_to_keep.append(item_name)
        else:
            print(f'i am not keeping{month_of_file}')
            print(f'item name: {item_name}')
    return items_to_keep

def what_files_to_keep_case_3(mylist,items_to_keep):
    # keep all files in that year - this is the case for an intermediate year in the given time period
    for item in range(0,len(mylist)):
        month_of_file = int(mylist[item].split(".")[-3])
        item_name = mylist[item]
        print(f'i am keeping month{month_of_file}')
        items_to_keep.append(item_name)
    return items_to_keep


def what_files_to_keep_case_4(mylist, end_month_download,items_to_keep):
    # last year of the period. Always starts in month 1 and finishes in end_month
    for item in range(0,len(mylist)):
        month_of_file = int(mylist[item].split(".")[-3])
        item_name = mylist[item]
        if ((month_of_file <= end_month_download)):
            print(f'i am keeping month{month_of_file}')
            print(f'item_name:{str(item_name)}')
            items_to_keep.append(item_name)
        else:
            print(f'i am not keeping{month_of_file}')
            print(f'item name: {item_name}')
    return items_to_keep



def gpm_month_download(outputDir, Start_Date = None,End_Date = None, backslh ='\\'):

    GetLoginInfo = list(retrieveLogin())

    #Get actual time
    try:
        Start_Date = list(map(int,Start_Date.split('-')))
        start_year = int(Start_Date[0])
        start_month = int(Start_Date[1])
        start_day = 1
    except:
        Start_Date = ['2000','06','01']
        start_year = int(Start_Date[0])
        start_month = int(Start_Date[1])
        start_day = int(Start_Date[2])
    try:
        End_Date =  list(map(int,(End_Date).split('-')))
        end_year = int(End_Date[0])
        end_month = int(End_Date[1])
        end_day = 1
    except:
        End_Date = list(map(int,((datetime.datetime.now()).strftime('%Y-%m-%d')).split('-')))
        end_year = int(End_Date[0])
        end_month = int(End_Date[1])
        end_day = int(End_Date[2])


    str_Start_Date = list(map(str,Start_Date))
    str_End_Date = list(map(str,End_Date))
    print('hello')


    #Start month
    if len(str_Start_Date[1]) == 1:
        str_Start_Date[1] = '0' + str_Start_Date[1]
    #End month
    if len(str_End_Date[1]) == 1:
        str_End_Date[1] = '0' + str_End_Date[1]

    #Start day
    if len(str_Start_Date[2]) == 1:
        str_Start_Date[2] = '0' + str_Start_Date[2]
    #End day
    if len(str_End_Date[2]) == 1:
       str_End_Date[2] = '0' + str_End_Date[2]


    years = list(map(str,range(start_year,end_year+1)))
    print(f'years: {years}')
    items_to_keep = []
    start_datetime = datetime.datetime(Start_Date[0], Start_Date[1], Start_Date[2])
    end_datetime = datetime.datetime(End_Date[0], End_Date[1], End_Date[2])
    num_months = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month)
    full_file_list = []
    year_count = 0


    for i in range(0,len(years),1):
        #print(f'I am moving on to year {years[i]}')

        url ='https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGM.06/'+years[i]+'/'
        print(url)

        #Acess the URL
        try:
            urlpath =urlopen(url)
        except:
            continue

        #Decode the URL
        string = urlpath.read().decode('utf-8')

        #Extract HDF5 files and make a file list
        pattern = re.compile('3B.*?HDF5.*?')
        filelist = list(set(list(map(str,pattern.findall(string)))))
        filelist.sort()

        filteredList = filelist #= list(filter(lambda x: x not in os.listdir(outputDir),filelist))
        # extend to get a full list
        #full_file_list.extend(filteredList)
        start_month_download = int(str_Start_Date[1])
        end_month_download = int(str_End_Date[1])


        months_to_download = np.arange(int(start_month_download), int(end_month_download),1)
        #items_to_keep = []
        #print(f'this is year count {year_count}')
        #print(f'this is the length of years: {len(years)}')
        if (year_count == 0 and len(years)==1):
            # we start from the first year
            to_keep = what_files_to_keep_case_1(filteredList, start_month_download, end_month_download,items_to_keep)
            print('case 1: this is the first year and there are no more years to come')
            to_keep.extend(full_file_list)
        elif (year_count == 0 and len(years)!=1):
            # first year but there are more to come:
            to_keep = what_files_to_keep_case_2(filteredList,start_month_download,items_to_keep)
            to_keep.extend(full_file_list)
            print('case 2: this is the first year and there are more years to come')
        elif (year_count != 0 and len(years)!=(year_count+1)):
            #keep all files
            to_keep = what_files_to_keep_case_3(filteredList,items_to_keep)
            to_keep.extend(full_file_list)
            print('case 3: this is an intermediate year')
        else:
            # last year
            to_keep = what_files_to_keep_case_4(filteredList,end_month_download,items_to_keep)
            to_keep.extend(full_file_list)
            print('case 4: this is the last year')



        print(f'these are the items to keep: {items_to_keep}')
        year_count +=1
        print('Starting download')


        for item in range(0,len(items_to_keep)):
            os.system('wget --user=' + GetLoginInfo[0] + ' --password=' + GetLoginInfo[1] + ' --show-progress -c -q '+  url + filteredList[item] + ' -O ' + outputDir + backslh + filteredList[item])

            #os.system('wget --user=' + os.environ["NASA_USERNAME"] + ' --password=' + os.environ["NASA_PASSWORD"] + ' --show-progress -c -q '+  url + items_to_keep[item] + ' -O ' + outputDir + backslh + items_to_keep[item])

    #except:
        #print ('\nDownloads finished')

    #print ('\nDownloads finished')
