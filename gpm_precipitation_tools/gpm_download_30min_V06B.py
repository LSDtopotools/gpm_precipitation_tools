#ttp://stackoverflow.com/questions/10875215/python-urllib-downloading-contents-of-an-online-directory
#ttp://stackoverflow.com/questions/4589241/downloading-files-from-an-http-server-in-python
#ttp://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
#ttp://stackoverflow.com/questions/34831770/download-a-file-in-python-with-urllib.request-instead-of-urllib
#ttp://stackoverflow.com/questions/25501090/how-to-get-wget-command-info-with-python


"""
This version is for the V06 of GESDIS
"""

from urllib.request import urlopen
import http.cookiejar as cookielib

import sys
import os
import re
import string
import datetime
import urllib.request

from Login_UI import retrieveLogin

def gpm_30min_download(input_dir, Start_Date = None,End_Date = None, backslh ='\\'):

    print ('started the 30min data download')


    # Login!
    GetLoginInfo = list(retrieveLogin())

    #Get actual time
    try:
        Start_Date = list(map(int,Start_Date.split('-')))
        start_year = int(Start_Date[0])
        start_month = int(Start_Date[1])
        start_day = int(Start_Date[2])
    except:
        Start_Date = ['2000','06','01']
        start_year = int(Start_Date[0])
        start_month = int(Start_Date[1])
        start_day = int(Start_Date[2])
    try:
        End_Date =  list(map(int,(End_Date).split('-')))
        end_year = int(End_Date[0])
        end_month = int(End_Date[1])
        end_day = int(End_Date[2])
    except:
        End_Date = list(map(int,((datetime.datetime.now()).strftime('%Y-%m-%d')).split('-')))
        end_year = int(End_Date[0])
        end_month = int(End_Date[1])
        end_day = int(End_Date[2])


    str_Start_Date = list(map(str,Start_Date))
    str_End_Date = list(map(str,End_Date))



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


    #print str_Start_Date
    years = list(map(str,range(start_year,end_year+1)))

    #Download files
    #try:
    for i in range(0,len(years),1):

        y = int(years[i])

        day1 = datetime.datetime(y,1,1)
        dayx = datetime.datetime(y,12,31)

        if y == start_year: day1 = datetime.datetime(y,start_month,start_day)
        if y == end_year: dayx = datetime.datetime(y,end_month,end_day)

        start_d = day1-datetime.datetime(y,1,1); start_d = start_d.days + 1
        end_d = dayx-datetime.datetime(y,1,1); end_d = end_d.days + 1

        day = list(map(str,range(start_d,end_d+1)))
        days = list(map(lambda x: '0' + x if len(x)==1 else x,day))
        days = list(map(lambda x: '0' + x if len(x)==2 else x,days))

        print (days)



        for j in range(len(days)):
            #print months[j]
            url ='https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.06/'+years[i]+'/'+days[j]+'/'
            print (url)


            #Acess the URL
            try:
                urlpath =urlopen(url)
            except:
                continue

            #Decode the URL
            string = urlpath.read().decode('utf-8')

            #Extract HDF5 files and make an file list
            pattern = re.compile('3B.*?HDF5.*?')
            filelist = list(set(list(map(str,pattern.findall(string)))))
            filelist.sort()

            filteredList = filelist #= list(filter(lambda x: x not in os.listdir(input_dir),filelist))


            for item in range(0,len(filteredList)):

                os.system('wget --user=' + GetLoginInfo[0] + ' --password=' + GetLoginInfo[1] + ' --show-progress -c -q '+  url + filteredList[item] + ' -O ' + outputDir + backslh + filteredList[item])

    print ('\nDownloads finished')
