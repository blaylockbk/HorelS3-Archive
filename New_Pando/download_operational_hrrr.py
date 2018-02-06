# Brian Blaylock
# brian.blaylock@utah.edu 
#
# February 2, 2018                                "It's Groundhog Day...again."

from datetime import datetime
import os
import urllib

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


def reporthook(a, b, c):
    """
    Print download progress in megabytes.
    Example:
        urllib.urlretrieve(URL, OUTFILE, reporthook=reporthook)
    """
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),


def get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True, PATH='default'):
    """
    Download OPERATIONAL HRRR from NOMADS via HTTP
    http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/

    Input:
        DATE  - Python datetime object for the day and hour requested
        model - [hrrr, hrrrak]
        field - [sfc, prs, nat, subh]
        fxx   - Forecast hours desired
                    range(0,19) or 
                    range(0,37) if model == hrrrak
                    range(0,37) if model == hrrr and hour == 0, 6, 12, or 18
        DIR   - Where should I save the files?
        idx   - Should I download/create an .idx file?
        png   - Should I create an .png sample image?
    """

    # HRRR Source Path
    NOMADS = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/%s.%s/' \
              % (model, DATE.strftime('%Y%m%d'))
    
    # HRRR Destination Path (same for horel-group7 directory and s3 object)
    PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
    
    # Look for this file
    FILE = '%s.t%sz.wrf%sf%02d.grib2' % (model, DATE.strftime('%H'), field, fxx)

    # If the destination DIR path does not exist, then create it
    if not os.path.exists(DIR+PATH):
        os.makedirs(DIR+PATH)
    
    # If the file does not exists or if it is smaller than 50 MB (maybe because
    # the file is incomplete), then download it.
    if not os.path.isfile(DIR+PATH+FILE) or os.path.getsize(DIR+PATH+FILE) < 5*10e6:
        # Build the URL string we want to download operational HRRR (HRRRv2+)
        URL = NOMADS+FILE
        # Only Download the file if it exists, if it's greater than 50 MB:
        if int(urllib.urlopen(URL).info()['Content-Length']) > 5e7:
            # Download and save the grib2 file and the .idx file
            print 'Downloading:', URL
            urllib.urlretrieve(URL, DIR+PATH+FILE, reporthook)
            urllib.urlretrieve(URL+'.idx', DIR+PATH+FILE+'.idx', reporthook)
            if idx:
                try:
                    urllib.urlretrieve(URL+'.idx', DIR+PATH+FILE+'.idx')
                except:
                    print "NEED TO MANUALLY CREATE .idx", DIR+PATH+FILE
                    create_idx(DIR+PATH+FILE)
            if png:
                create_png()
                print 'Saved:', DIR+PATH+FILE
        else:
            print 'DOES NOT EXIST: %s' % URL
        
    else:
        print "**File Exists**", DIR+PATH+FILE
