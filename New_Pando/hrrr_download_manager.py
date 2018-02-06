# Brian Blaylock
# brian.blaylock@utah.edu 
#
# February 2, 2018                                "It's Groundhog Day...again."


"""
Download HRRR, HRRRx, and HRRRak to New Pando: http://hrrr.chpc.utah.edu/

This script should be run by the mesohorse user on meso1. 
Run this 4 times a day to prevent any missing data from download failures.

Operational HRRR: http://nomads.ncep.noaa.gov/
Experimental HRRR: ftp://gsdftp.fsl.noaa.gov

What this script does:
1) Download .grib2 and .idx files and store on horel-group7
    1.1 Download grib2 file from source
    1.2 Create .idx file for grib2 files from ESRL
    1.3 Create .png sample of grib2 file
2) Sync files to Pando and set bucket permission to public
"""

import os
import urllib
import getpass
import socket
from datetime import datetime, timedelta
import multiprocessing.pool #:)

import download_operational_hrrr
import download_experimental_hrrr

if getpass.getuser() != 'mesohorse' or socket.gethostname() != 'meso1.chpc.utah.edu':
    print "--> You are %s on %s" % (getpass.getuser(), socket.gethostname())
    print "--> Please run this operational download script with the mesohorse user on meso1."
    exit()

# -----------------------------------------------------------------------------
#                           Download Controls
# -----------------------------------------------------------------------------
# The models dictionary describes what to download from each model.
#  Initial keys used in the file names: ['hrrr', 'hrrrak', 'hrrrX', 'hrrrakX']
#     name   : not used, only to describe to you what it is
#     source : 'NOMADS' for operational models, 'ESRL' for experimental models
#     hours  : The model run hours you want to download. Most hrrr models
#              run hourly, except the Alaska model runs every six hours.
#              i.e. range(0, 24, 6)
#     fxx    : The forecast hours you want to download is defined for each
#              grid type ['sfc', 'prs', 'nat', 'subh']. Leave as an empty 
#              list to not download any files for that field.

models = {'hrrr':{'name':'Operational HRRR',
                  'source':'NOMADS',
                  'hours':range(0,24),
                  'fxx':{'sfc':range(0,19),
                         'prs':range(0,1),
                         'nat':[],
                         'subh':[]}},
          'hrrrak':{'name':'Operational HRRR Alaska',
                    'source':'NOMADS',
                    'hours':range(0,24,6),
                    'fxx':{'sfc':[],
                           'prs':[]}},
          'hrrrX':{'name':'Experimental HRRR',
                   'source':'ESRL',
                   'hours':range(0,24),
                   'fxx':{'sfc':range(0,1),
                          'prs':[]}},
          'hrrrakX':{'name':'Experimental HRRR Alaska',
                   'source':'ESRL',
                   'hours':range(0, 24, 6),
                   'fxx':{'sfc':[],
                          'prs':[]}}
         }

# Define storage directories for horel-group7 and Pando S3
DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'
S3 = 'horelS3:'

# If the current time is before 0600 UTC, finish downloading files from
# yesterday. Else, download files from today.
if datetime.utcnow().hour < 6:
    DATE = datetime.utcnow()-timedelta(days=1)
else:
    DATE = datetime.utcnow()

# -----------------------------------------------------------------------------
#                           Main Tasks
# -----------------------------------------------------------------------------
## 1) Download HRRR files from source
# 
#  --- Operational HRRR ---
#         Use multithreading for faster downloads
#         https://stackoverflow.com/questions/2846653/how-to-use-threading-in-python
#         https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.dummy
def oper_hrrr_multipro(args):
    DATE, model, field, fxx = args
    try:
        download_operational_hrrr.get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True)
    except:
        # Try again...???
        download_operational_hrrr.get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True)

oper_args = [[datetime(DATE.year, DATE.month, DATE.day, h), m, f, fxx] \
             for m in models.keys() if models[m]['source']=='NOMADS' \
             for h in models[m]['hours'] \
             for f in models[m]['fxx'].keys() if len(models[m]['fxx'][f]) > 0 \
             for fxx in models[m]['fxx'][f]]

# Multithreading
p = multiprocessing.pool.ThreadPool(4)
result = p.map(oper_hrrr_multipro, oper_args)
p.close()
p.join()



"""
#  --- Experimental HRRR ---
#         Use multiprocessing because I've had issues with the ftp site timing
#         out when using multithreading
def exp_hrrr_multipro(args):
    DATE, model, field, fxx, DIR = args
    return [DATE, model, field, fxx, DIR]
    download_operational_hrrr.get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True)

exp_args = [[datetime(DATE.year, DATE.month, DATE.day, h), m, f, fxx, DIR] \
            for m in models.keys() if models[m]['source']=='ESRL' \
            for h in models[m]['hours'] \
            for f in models[m]['fxx'].keys() if len(models[m]['fxx'][f]) > 0 \
            for fxx in models[m]['fxx'][f]]

# Multiprocessing
p = multiprocessing.Pool(5)
result = p.map(exp_hrrr_multipro, exp_args)
p.close()
"""

## 2) Copy each path directory to Pando
#     Note: Do not use sync, in case a file is removed from horel-group7

# HRRR Destination Path we want to sync (same for directory and s3 bucket)
# Sync all model and field directories for the date.
rclone = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-v1.39-linux-386/rclone'
os.system('%s sync %s %s' % (rclone, DIR+'hrrr/', S3+'hrrr/'))

# Set bucket permissions to public for URL access to each files
s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd'
os.system(s3cmd + ' setacl s3://hrrr/ --acl-public --recursive')
