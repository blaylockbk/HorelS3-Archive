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

def get_grib2(model, model_params, DIR, idx=True):
    """
    Download EXPERIMENTAL HRRR from NOAA ESRL via FTP
    ftp://gsdftp.fsl.noaa.gov/
    
    Files on the FTP site are only available for the last day.

    Input:
        model        - [hrrrX, hrrrakX]
        model_params - A dictionary of the model parameters:
                       {'hours': range(0,24),
                        'fxx':{'sfc':range(0,18),
                               'prs':range(0,1)}}
        DIR   - Where should I save the files?
        idx   - Should I download/create an .idx file?
    """

    # Credentials for logging into ESRL FTP database
    user, password = get_ESRL_credentials()

    # Models are named slightly different on ESRL than on NOMADS. I want to
    # preserve my nameing convention for the files downloaded from ESRL.
    if model == 'hrrrX':
        ESRL = 'hrrr/conus/'
        png = True
    elif model == 'hrrrak':
        ESRL = 'hrrr_ak/alaska/'
        png = False
    
    # For every requested field type, get a list of the available files
    requested_fields = [T for T in model_params['fxx'].keys() if len(model_params['fxx'][T]) > 0]
    for field in requested_fields:
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


        ## Filter list of files for files named with only digits
        ftp_filenames = filter(lambda x: x.isdigit(), ftp_filenames)

        ## Filter list of files by if the fxx was requested
        ftp_filenames = filter(lambda x: int(x[-4:-2]) in model_params['fxx'][field], ftp_filenames)

        ## Extract from each ftp_filenames the run datetime and forecast hour
        ftp_filenames_EXTRACT = map(lambda x: 
                                    (datetime.strptime(x[:-4], '%y%j%H%M'), x[-4:-2]),
                                    ftp_filenames)
        
        ## List the path and new file name for each ftp_filenames_EXTRACT
        ftp_filenames_NEW = map(lambda x:
                                '%s/%s/%s/%s.t%02dz.wrf%sf%s.grib2' %
                                 (model, field, x[0].strftime('%Y%m%d'),
                                  model, x[0].hour, field, x[1]),
                                 ftp_filenames_EXTRACT)

        ## Filter the ftp file list if the file has not been downloaded
        not_on_Pando = map(lambda x: not os.path.isfile(DIR+x) or os.path.getsize(DIR+x) < 5*10e6, ftp_filenames_NEW)
        ftp_filenames = [ftp_filenames[d] for d in range(len(not_on_Pando)) if not_on_Pando[d]]
        

        # Download each file, only if the file name is made of a digits
        for i in ftp_filenames:
            # I only have success downloading if I login to the FTP site each
            # time I download a file.
            ftp = FTP('gsdftp.fsl.noaa.gov')
            ftp.login(user, password)
            if field == 'sfc':
                ftp.cwd('%s/wrftwo' % ESRL)
            elif field == 'prs':
                ftp.cwd('%s/wrfprs' % ESRL)
            elif field == 'nat':
                ftp.cwd('%s/wrfnat' % ESRL)
            print "logged in for", i
            # What is the file's initialized hour and forecast?
            DATE = datetime.strptime(i[:-4], '%y%j%H%M')
            fxx = int(i[-4:-2])
        
            # Where should I put this file?
            PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
            FILE = '%s.t%02dz.wrf%sf%02d.grib2' % (model, DATE.hour, field, fxx)
            print DIR+PATH+FILE
            
            # If the destination DIR path does not exist, then create it
            if not os.path.exists(DIR+PATH):
                os.makedirs(DIR+PATH)
    
            print "Downloading:", DIR+PATH+FILE
            ftp.retrbinary('RETR '+ i, open(DIR+PATH+FILE, 'wb').write)
            print "Saved:", DIR+PATH+FILE
            ftp.quit()

            # Create the .idx file
            if idx:
                create_idx(DIR+PATH+FILE)


if __name__ == '__main__':
    
    # Test the download function

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
    get_grib2('hrrrak', models['hrrrak'], DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/')




