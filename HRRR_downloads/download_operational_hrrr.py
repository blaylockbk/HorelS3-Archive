# Brian Blaylock
# brian.blaylock@utah.edu 
#
# February 2, 2018                                "It's Groundhog Day...again."

from datetime import datetime
import os
import urllib
import urllib2

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


def get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True, PATH='default', source='NOMADS'):
    """
    Download OPERATIONAL HRRR from NOMADS via HTTP:
    http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/

    Download EXPERIMENTAL HRRR from PARALLEL NOMADS via HTTP:
    http://para.nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/para/

    Input:
        DATE   - Python datetime object for the day and hour requested
        model  - [hrrr, hrrrak]
        field  - [sfc, prs, nat, subh]
        fxx    - Forecast hours desired
                     range(0,19) or 
                     range(0,37) if model == hrrrak
                     range(0,37) if model == hrrr and hour == 0, 6, 12, or 18
        DIR    - Where should I save the files?
        idx    - Should I download/create an .idx file?
        png    - Should I create an .png sample image?
        source - 'NOMADS' or 'PARA'
    """

    # HRRR Source Path
    if source == 'NOMADS':
        # Download from operational products directory
        if datetime.utcnow() < datetime(2018, 7, 12, 14):
            # HRRR version 2
            NOMADS = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/%s.%s/' \
                    % (model, DATE.strftime('%Y%m%d'))
        else:
            # HRRR version 3
            print "!!>> DOWNLOADING HRRR VERSION 3 <<!!"
            if model =='hrrrak':
                DOMAIN = 'alaska'
                SHORT = 'ak.'
            elif model == 'hrrr':
                DOMAIN = 'conus'
                SHORT = ''
            NOMADS = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%s/%s/' \
                    % (DATE.strftime('%Y%m%d'), DOMAIN)

    elif source == 'PARA':
        # Download from parallel products directory
        if model =='hrrrak':
            DOMAIN = 'alaska'
            SHORT = 'ak.'
        elif model == 'hrrr':
            DOMAIN = 'conus'
            SHORT = ''
        NOMADS = 'http://para.nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/para/hrrr.%s/%s/' \
                  % (DATE.strftime('%Y%m%d'), DOMAIN)
    
    # HRRR Destination Path (same for horel-group7 directory and s3 object)
    PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
    # If the destination DIR path does not exist, then create it
    if not os.path.exists(DIR+PATH):
        os.makedirs(DIR+PATH)

    # Look for this file, (and rename the file using our naming convention)
    if model == 'hrrr':
        FILE = '%s.t%02dz.wrf%sf%02d.grib2' % (model, DATE.hour, field, fxx)
        NEWFILE = FILE
    elif model == 'hrrrak':
        FILE = 'hrrr.t%02dz.wrf%sf%02d.ak.grib2' % (DATE.hour, field, fxx)
        NEWFILE = '%s.t%02dz.wrf%sf%02d.grib2' % (model, DATE.hour, field, fxx)

    # If the .idx file exists and has the expected line numbers, then download
    # the .idx file and the .grib2 file.
    try:
        idxpage = urllib2.urlopen(NOMADS+FILE+'.idx')
    except:
        idxpage = []
    lines = sum(1 for line in idxpage)
    print '%s Lines in File: %s.idx' % (lines, NOMADS+FILE)


    if datetime.utcnow() < datetime(2018, 7, 12, 14):
        # HRRR version 2
        IDX_LINES = {'hrrr':{'sfc': [132, 135],
                            'prs': [684, 687],
                            'nat': [1107, 1110]},
                    'hrrrak':{'sfc': [153, 156],
                            'prs': [698, 701],
                            'nat': [1121, 1124]}}
    else:
        # HRRR version 3
        IDX_LINES = {'hrrr':{'sfc': [148, 151],
                            'prs': [698, 701],
                            'nat': [1123, 1126]},
                    'hrrrak':{'sfc': [153, 156],
                            'prs': [698, 701],
                            'nat': [1121, 1124]}}

    if fxx < 2:
        expected_lines = IDX_LINES[model][field][0]
    else:
        expected_lines = IDX_LINES[model][field][1]


    if lines >= expected_lines:            
        # Download the .idx if it doesn't exist
        if not os.path.isfile(DIR+PATH+NEWFILE+'.idx'):
            urllib.urlretrieve(NOMADS+FILE+'.idx', DIR+PATH+NEWFILE+'.idx', reporthook)

        # If the file does not exists on horel-group7 or if our copy is smaller
        # than 90 MB (maybe because the file is incomplete), then download it.
        if model == 'hrrr':
            min_file_size = 9e7
        elif model == 'hrrrak':
            min_file_size = 10e6
        if not os.path.isfile(DIR+PATH+NEWFILE) or os.path.getsize(DIR+PATH+NEWFILE) < min_file_size:
            # Build the URL string we want to download operational HRRR
            URL = NOMADS+FILE
            # Only Download the file if it exists, if it's greater than 50 MB:
            if int(urllib.urlopen(URL).info()['Content-Length']) > min_file_size:
                # Download and save the grib2 file and the .idx file
                print 'Downloading:', URL
                urllib.urlretrieve(URL, DIR+PATH+NEWFILE, reporthook)
                if idx:
                    try:
                        urllib.urlretrieve(URL+'.idx', DIR+PATH+NEWFILE+'.idx')
                    except:
                        print "NEED TO MANUALLY CREATE .idx", DIR+PATH+NEWFILE, '...',
                        create_idx(DIR+PATH+NEWFILE)
                        print "DONE!"
                if png:
                    create_png()
                    print 'Saved:', DIR+PATH+NEWFILE
            else:
                print 'DOES NOT EXIST: %s' % URL
            
        else:
            print "**File Exists** %s. Moving on." % (DIR+PATH+NEWFILE)

if __name__ == '__main__':
    
    DATE = datetime(2018, 8, 29, 12)
    model = 'hrrr'
    field = 'sfc'
    fxx = 0
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'
    
    get_grib2(DATE, model, field, fxx, DIR, idx=True, png=True, source='NOMADS')
    