# Brian Blaylock
# brian.blaylock@utah.edu 
#
# February 2, 2018                                "It's Groundhog Day...again."


"""
Download HRRR, HRRRx, and HRRRak to New Pando: http://hrrr.chpc.utah.edu/

This script should be run by the mesohorse user on meso1. 
Run this 4 times a day to prevent any missing data from download failures.

 Operational HRRR: http://nomads.ncep.noaa.gov/
    Parallel HRRR: http://para.nomads.ncep.noaa.gov/
Experimental HRRR: ftp://gsdftp.fsl.noaa.gov

What this script does:
1) Download GRIB2 files and store on horel-group7
    1.1 Download grib2 file from source
    1.2 Download or create .idx file for every grib2 files 
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
#    exit()

# -----------------------------------------------------------------------------
#                            Download Controls
# -----------------------------------------------------------------------------
# The models dictionary describes what to download from each model.
#  Initial keys used in the file names: ['hrrr', 'hrrrak', 'hrrrX', 'hrrrakX']
#     name   : not used, only to describe to you what it is
#     source : 'NOMADS' for operational models
#              'PARA' for parallel NOMADS
#              'ESRL' for experimental models
#     hours  : The model run hours you want to download. Most hrrr models
#              run hourly, except the Alaska model runs every three hours.
#              i.e. range(0, 24, 3)
#     fxx    : The forecast hours you want to download is defined for each
#              grid type using the keys ['sfc', 'prs', 'nat', 'subh'].
#              The the key value as an empty list to not download any files
#              for that field.

models = {'hrrr':{'name':'Operational HRRR',
                  'source':'NOMADS',
                  'hours':range(0,24),
                  'fxx':{'sfc':range(0,19),
                         'prs':range(0,1),
                         'nat':[],
                         'subh':[]}},
          'hrrrak':{'name':'Parallel HRRR Alaska',     # temporary download "operational" alaska from ESRL before it becomes operational
                    'source':'NOMADS',
                    'hours':range(0,24,3),
                    'fxx':{'sfc':range(0,37),          # 36 hour forecasts for 0, 6, 12, 18 UTC. 18 hour forecasts otherwise
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

# If the current time is before 0300 UTC, finish downloading files from
# yesterday. Else, download files from today.
if datetime.utcnow().hour < 5:
    DATE = datetime.utcnow()-timedelta(days=1)
else:
    DATE = datetime.utcnow()

#DATE = datetime(2019, 2, 21)

# -----------------------------------------------------------------------------
#                   Download GRIB2 files from NOMADS or PARA
# -----------------------------------------------------------------------------
#
# Download operational HRRR files
#       Use multithreading for faster downloads
#       https://stackoverflow.com/questions/2846653/how-to-use-threading-in-python
#       https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.dummy
def oper_hrrr_multipro(args):
    DATE, model, field, fxx, source = args
    try:
        download_operational_hrrr.get_grib2(DATE, model, field, fxx, DIR, idx=True, png=False, source=source)
    except:
       # Try again...
        try:
            download_operational_hrrr.get_grib2(DATE, model, field, fxx, DIR, idx=True, png=False, source=source)
        except:
            print "THIS DID NOT WORK", args

oper_args = [[datetime(DATE.year, DATE.month, DATE.day, h), m, T, fxx, models[m]['source']] \
             for m in models.keys() if models[m]['source']=='NOMADS' or models[m]['source']=='PARA' \
             for h in models[m]['hours'] \
             for T in models[m]['fxx'].keys() if len(models[m]['fxx'][T]) > 0 \
             for fxx in models[m]['fxx'][T]]

# Multithreading
p = multiprocessing.pool.ThreadPool(4)
result = p.map(oper_hrrr_multipro, oper_args)
p.close()
p.join()


# -----------------------------------------------------------------------------
#                       Download GRIB2 files from ESRL
# -----------------------------------------------------------------------------
#       Multiprocessing can be handled in the download function because
#       dealing with FTP is cumbersome.
exp_models = [m for m in models.keys() if models[m]['source']=='ESRL']
for m in exp_models:
    try:
        download_experimental_hrrr.get_grib2(m, models[m], DIR, idx=True)
    except:
        print "\n++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        print "         Could not reach FTP site."
        print "           ftp://gsdftp.fsl.noaa.gov/"
        print "         Is the government shutdown??"
        print "++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"


print ""
print "Finished what I can download."
print ""


# -----------------------------------------------------------------------------
#          Sync files to Pando and set bucket permission to Public
# -----------------------------------------------------------------------------
PATHS = ["%s/%s/%s/" % (i,j,DATE.strftime('%Y%m%d')) 
         for i in models 
         for j in models[i]['fxx'] if len(models[i]['fxx'][j]) > 0]

for PATH in PATHS:
    print PATH,
    # Sync all model and field directories for the date to Pando.
    # Use `copy` and not `sync` in case a file is removed from horel-group7
    print "- rclone -"
    rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
    os.system('%s sync %s %s' % (rclone, DIR+PATH, S3+PATH))

    # Set bucket permissions to public for URL access to each files
    print "- s3cmd -"
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PATH)

    print "DONE!"



"""
How to sync and set to public EVERYTHING in a bucket

# hrrr
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrr/ horelS3:hrrr/
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd setacl s3://hrrr/ --acl-public --recursive

# hrrrak
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrrak/ horelS3:hrrrak/
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd setacl s3://hrrrak/ --acl-public --recursive

# hrrrX
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrrX/ horelS3:hrrrX/
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd setacl s3://hrrrX/ --acl-public --recursive

# GOES16
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/ horelS3:GOES16/
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd setacl s3://GOES16/ --acl-public --recursive
"""
