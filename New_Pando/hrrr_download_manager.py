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
    1.2 Create .png sample of grib2 file
    1.3 Create .idx file for grib2 files from ESRL

2) Sync files to Pando and set bucket permission to public
"""

import os
import urllib
from datetime import datetime, timedelta
import multiprocessing #:)

import download_operational_hrrr
import download_experimental_hrrr

# ----------------------------------------------------------------------------
#                        Set up and definitions
# ----------------------------------------------------------------------------
# Build a dictionary of what to download from each model.
    # Note: The range of forecast hours you download are defined by each field
    # Note: The hrrrak model only runs every 6 hours, range(0,24,6)
models = {'hrrr':{'name':'Operational HRRR',
                  'source':'NOMADS',
                  'hours':range(0,24),
                  'fxx':{'sfc':range(0,19),
                         'prs':[],
                         'nat':range(0,1),
                         'subh':[]}},
          
          'hrrrak':{'name':'Operational HRRR Alaska',
                    'source':'NOMADS',
                    'hours':range(0,24,6),
                    'fxx':{'sfc':range(0,37),
                           'prs':range(0,1)}},
          
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


# ----------------------------------------------------------------------------
#                        Main Tasks
# ----------------------------------------------------------------------------
## 1) Download HRRR files from source
# 
#  --- Operational HRRR ---
#         Use multithreading for faster downloads
#         https://stackoverflow.com/questions/2846653/how-to-use-threading-in-python
#         https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.dummy
def oper_hrrr_multipro(args):
    DATE, model, field, fxx, DIR = args
    download_operational_hrrr.get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True)

oper_args = [[datetime(DATE.year, DATE.month, DATE.day, h), m, f, fxx, DIR] \
             for m in models.keys() if models[m]['source']=='NOMADS' \
             for h in models[m]['hours'] \
             for f in models[m]['fxx'].keys() if len(models[m]['fxx'][f]) > 0 \
             for fxx in models[m]['fxx'][f]]

# Multithreading
p = multiprocessing.pool.ThreadPool(4)
result = p.map(oper_hrrr_multipro, oper_args)
p.close()
p.join()


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


## 2) Copy each path directory to Pando
#     Should I convert this to use threading??
#     Note: Do not use sync, in case a file is removed from horel-group7
config_file = '/scratch/local/mesohorse/.rclone.conf'    # meso1 mesohorse user

# HRRR Destination Path we want to sync (same for directory and s3 bucket)
# Sync all model and field directories for the date.
for model in models:
    for field in models[model]['fxx']:
        PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
        os.system('rclone --config %s copy %s %s' \
                % (config_file, DIR+PATH, S3+PATH))

        # Set bucket permissions to public for URL access to each files
        s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
        os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PATH)              
