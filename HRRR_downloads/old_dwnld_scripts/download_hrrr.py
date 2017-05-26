# Brian Blaylock
# February 27, 2017

"""
Downloads the operational HRRR from NCEOP NOMADS server
A re-write of the "get_hrrr.csh" script in python.
"""

import urllib
from datetime import datetime, timedelta
import os
import stat

# ----------------------------------------------------------------------------
#                        Introductory Stuff
# ----------------------------------------------------------------------------
# download HRRR files from yesterday
yesterday = datetime.today() #-timedelta(days=1)

# Put the downloaded files in the horel-group/archive. Mkdir if it doesn't exist
OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/BB_test/models/hrrr/' \
    % (yesterday.year, yesterday.month, yesterday.day)
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)
    # Change directory permissions
    os.chmod(OUTDIR, stat.S_IRWXU | \
                     stat.S_IRGRP | stat.S_IXGRP | \
                     stat.S_IROTH | stat.S_IXOTH)
                   # User can read, write, execute
                   # Group can read and execute
                   # Others can read and execute
# ----------------------------------------------------------------------------
def reporthook(a,b,c): 
    # ',' at the end of the line is important!
    print "% 3.1f%% of %d bytes\r" % (min(100, float(a * b) / c * 100), c),
    #you can also use sys.stdout.write
    #sys.stdout.write("\r% 3.1f%% of %d bytes"
    #                 % (min(100, float(a * b) / c * 100), c)

def download_hrrr(DATE, field,
                  hour=range(0, 24), forecast=range(0, 19), OUTDIR='./'):
    """
    Downloads HRRR grib2 files from the nomads server
    http://nomads.ncep.noaa.gov/

    Input:
        DATE - a datetime object for which you wish to download
        fields - the field you want to download
                 Options are fields ['prs', 'sfc','subh', 'nat']
                 pressure fields (~350 MB), surface fields (~6 MB),
                 native fields (~510 MB)!
        hour - a list of hours you want to download
               Default all hours in the day
        forecast - a list of forecast hour you wish to download
                   Default all forecast hours (0-18)
        outpath - the outpath directory you wish to save the files.
    """
    # We'll store the URLs we download from and return them for troubleshooting
    URL_list = []

    # Build the URL string we want to download. One for each field, hour, and forecast
    # New URL for downloading HRRRv2+
    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/' \
          % (DATE.year, DATE.month, DATE.day)

    # Create a new array for each field to keep things organized.
    for h in hour:
        for f in forecast:
            FileName = 'hrrr.t%02dz.wrf%sf%02d.grib2' % (h, field, f)

            # Download and save the file
            print 'Downloading:', URL, FileName
            urllib.urlretrieve(URL+FileName, OUTDIR+FileName, reporthook)
            print 'Saved:', OUTDIR+FileName
            URL_list.append(URL+FileName)

    # Return the list of URLs we downloaded from for troubleshooting
    return URL_list

def download_hrrr_bufr(DATE,
                       stations=['725720'],
                       rename=['kslc'],
                       hour=range(0,24),
                       OUTDIR='./'):
    """
    Special case for downloading HRRR bufr soundings.
    """
    URL_list = []

    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/bufrsnd.t%02dz/' \
           % (DATE.year, DATE.month, DATE.day, DATE.hour)

    for h in hour:
        for i in range(len(stations)):
            FILE = 'bufr.%s.%04d%02d%02d%02d' \
                % (stations[i], DATE.year, DATE.month, DATE.day, h)
            NEWNAME = '%s_%04d%02d%02d%02d.buf' \
                    % (rename[i], DATE.year, DATE.month, DATE.day, h)
            urllib.urlretrieve(URL+FILE, OUTDIR+NEWNAME, reporthook)
            URL_list.append(URL+FILE)

    return URL_list

if __name__ == '__main__':

    # Download Surface fields: all hours and all forecast hours
    sfc_hxx = range(0, 24)
    sfc_fxx = range(0, 19)
    sfc_URLs = download_hrrr(yesterday,
                             field='sfc',
                             hour=sfc_hxx,
                             forecast=sfc_fxx,
                             OUTDIR=OUTDIR)

    # Download Pressure fields: all hours, only analysis hours
    prs_hxx = range(0, 24)
    prs_fxx = range(0, 1)
    prs_URLs = download_hrrr(yesterday,
                             field='prs',
                             forecast=prs_fxx,
                             hour=prs_hxx,
                             OUTDIR=OUTDIR)

    # Download bufr soundings: KSLC, KODG, KPVU
    stations = ['725720', '725724', '725750']
    rename = ['kslc', 'kpvu', 'kodg']
    bufr_URLs = download_hrrr_bufr(yesterday,
                                   stations=stations,
                                   rename=rename,
                                   OUTDIR=OUTDIR)

    ## Download subhourly
    #subh_hxx = range(0, 24)
    #subh_fxx = range(0, 19)
    #subh_URLs = download_hrrr(yesterday, field='subh', hour=sub_hxx, forecast=subh_fxx)
