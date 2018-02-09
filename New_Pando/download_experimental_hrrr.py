# Brian Blaylock
# brian.blaylock@utah.edu 
#
# February 2, 2018                                "It's Groundhog Day...again."

"""
Download experimental HRRR files from ESRL
"""

from ftplib import FTP
import os
import stat
import numpy as np
from datetime import datetime

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
sys.path.append('B:/pyBKB_v2')
from BB_MesoWest.get_token import get_ESRL_credentials

def create_png():
    """
    Create a sample image to store with the data
    """
    print "Make a sample image -- COMING SOON --"


def create_idx(for_this_file):
    """
    If there isn't a NOMADS .idx file, then use this to create a .idx file that
    matches the NOMADS format
    """
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')
    print "--> Created idx file:", for_this_file

def get_grib2(model, model_params, DIR, idx=True, png=True):
    """
    Download EXPERIMENTAL HRRR from NOAA ESRL via FTP
    ftp://gsdftp.fsl.noaa.gov/

    Input:
        DATE  - Python datetime object for the day and hour requested
        model - [hrrrX, hrrrakX, hrrreX, hrrrsmokeX, hrrrhiX, hrrrwfip2X]
        field - [sfc, prs, nat, subh]
        fxx   - Forecast hours desired
                    range(0,19) or 
                    range(0,37) if model == hrrrak
                    range(0,37) if model == hrrr and hour == 0, 6, 12, or 18
        DIR   - Where should I save the files?
        idx   - Should I download/create an .idx file?
        png   - Should I create an .png sample image?
    """
    # Credentials for logging into ESRL FTP database
    user, password = get_ESRL_credentials()

    # Models are named slightly different on ESRL than on NOMADS. I want to
    # preserve my nameing convention for the files downloaded from ESRL.
    if model == 'hrrrX':
        ESRL = 'hrrr/conus/'
    elif model == 'hrrrak':
        ESRL = 'hrrr_ak/alaska/'
    for field in model_params['fxx']:
        # Download requested surface fields
        # Get surface fields file list
        ftp = FTP('gsdftp.fsl.noaa.gov')
        ftp.login(user, password)
        if field == 'sfc':
            ftp.cwd('%s/wrftwo' % ESRL)
        elif field == 'prs':
            ftp.cwd('%s/wrfprs' % ESRL)
        elif field == 'nat':
            ftp.cwd('%s/wrfnat' % ESRL)
        # Get a list of the files...
        ftp_filenames = ftp.nlst()
        ftp.quit()

        # Only check items that are digits
        for i in filter(lambda x: x.isdigit(), ftp_filenames):
            # I only have success if I download one file every time
            # I log into the FTP site.
            ftp = FTP('gsdftp.fsl.noaa.gov')
            ftp.login(user, password)
            if field == 'sfc':
                ftp.cwd('%s/wrftwo' % ESRL)
            elif field == 'prs':
                ftp.cwd('%s/wrfprs' % ESRL)
            elif field == 'nat':
                ftp.cwd('%s/wrfnat' % ESRL)
            # What is the initialized hour and forecast?
            DATE = datetime.strptime(i[:-4], '%y%j%H%M')
            fxx = int(i[-4:-2])
            # Only download the file if the fxx is requested
            if fxx in model_params['fxx'][field]:
                print fxx
                # Where should I put this file?
                PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
                FILE = '%s.t%02dz.wrf%sf%02d.grib2' % (model, DATE.hour, field, fxx)
                print DIR+PATH+FILE
                # If the destination DIR path does not exist, then create it
                if not os.path.exists(DIR+PATH):
                    os.makedirs(DIR+PATH)
                
                if not os.path.isfile(DIR+PATH+FILE) or os.path.getsize(DIR+PATH+FILE) < 5*10e6:
                    print "Downloading:", DIR+PATH+FILE
                    ftp.retrbinary('RETR '+ i, open(DIR+PATH+FILE, 'wb').write)
                    print "Saved:", DIR+PATH+FILE
                else:
                    print "looks like that file already exists", DIR+PATH+FILE
                
            ftp.quit()

if __name__ == '__main__':
    models = {'hrrr':{'name':'Operational HRRR',
                    'source':'NOMADS',
                    'hours':range(0,24),
                    'fxx':{'sfc':range(0,19),
                            'prs':range(0,1),
                            'nat':[],
                            'subh':[]}},
            'hrrrak':{'name':'Operational HRRR Alaska',     # temporary download "operational" alaska from ESRL before it becomes operational
                        'source':'ESRL',
                        'hours':range(0,24,3),
                        'fxx':{'sfc':[],
                            'prs':[0]}},
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
    get_grib2('hrrrX', models['hrrrX'], DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/')




