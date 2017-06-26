# Brian Blaylock
# June 23, 2017                             # Got back from a trip to San Diego

"""
Download a subregion from the native HRRR grid
"""

import os
from datetime import datetime, timedelta
import urllib
import pygrib
import matplotlib.pyplot as plt

# rclone config file
config_file = '/scratch/local/mesohorse/.rclone.conf' # meso1 mesohorse user
config_file = '~/.rclone.conf' # my home config file

def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),

def copy_to_horelS3(from_here, to_there):
    """
    Copy the file to the horelS3: archive using rclone
    Input:
        from_here - string of full path and file name you want to copy
        to_there  - string of path on the horelS3 archive
    """
    # Copy the file from_here to_there (the path will be created if it doesn't exist)
    os.system('rclone --config %s copy %s horelS3:%s' \
              % (config_file, from_here, to_there))

def create_idx(for_this_file, put_here):
    """
    Create a .idx file and move to horel-group/archive/HRRR
    """
    file_name = for_this_file.split('/')[-1]
    idx_dir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/' + put_here
    if not os.path.exists(idx_dir):
        os.makedirs(idx_dir)
    idx_name = idx_dir + file_name + '.idx'
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + idx_name)
    print "created idx file:", idx_name

def download_hrrr_nat_subsection(DATE, hour,
                                 latitude=37.716,
                                 longitude=-112.844,
                                 name='BRIANHEAD',
                                 subregion_size=2.5,
                                 field='nat',
                                 forecast=range(0, 19),
                                 OUTDIR='/uufs/chpc.utah.edu/common/home/u0553130/temp/'):
    """
    Downloads HRRR grib2 files from the nomads server
    http://nomads.ncep.noaa.gov/

    Input:
        hour - the hours you want to download
        latitude - the latitude of center point of the subsection (default SLC rawinsonde)
        longitude - the longitude of the center point of the subsection (default SLC rawinsonde)
        subregion_size - the size of the subregion to get. In degrees lat/lon,
                         we will get a box the size of 2*subregion_sizex2*subregion_size
                         centered over the latitude/longitude point.
        fields - the field you want to download
                 Options are fields ['prs', 'sfc','subh', 'nat']
                 pressure fields (~350 MB), surface fields (~6 MB),
                 native fields (~600 MB)!
        forecast - a list of forecast hour you wish to download from that hour
                   Default all forecast hours (0-18)
    """
    # We'll store the URLs we download from and return them for troubleshooting
    URL_list = []
    FileNames = []
    #
    # Build the URL string we want to download. One for each field, hour, and forecast
    # New URL for downloading HRRRv2+
    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/' \
          % (DATE.year, DATE.month, DATE.day)
    #
    for f in forecast:
        FileName = 'hrrr.t%02dz.wrf%sf%02d.grib2' % (hour, field, f)
        FileNames.append(OUTDIR+FileName)
        # Download and save the file
        print 'Downloading:', OUTDIR+FileName
        urllib.urlretrieve(URL+FileName, OUTDIR+FileName, reporthook=reporthook)
        print 'Saved:', OUTDIR+FileName
        URL_list.append(URL+FileName)

        os.system('wgrib2 %s -small_grib %s:%s %s:%s %s' % (OUTDIR+FileName, longitude-subregion_size, longitude+subregion_size, latitude-subregion_size, latitude+subregion_size, OUTDIR+FileName+'.'+name))
        os.system('rm '+ OUTDIR+FileName)

        # Move FILE to S3
        print "\nMoving %s to Pando" % (OUTDIR+FileName)
        FILE = OUTDIR+FileName+'.'+name
        DIR_S3 = 'HRRR/%s/%s/%04d%02d%02d/' \
                    % ('oper', field, DATE.year, DATE.month, DATE.day)
        if os.path.isfile(FILE):
            copy_to_horelS3(FILE, DIR_S3)
            create_idx(FILE, DIR_S3)
        else:
            print "%s does not exist" % FILE

    # Change permissions of S3 directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % DIR_S3)

    #
    # Return the list of URLs we downloaded from for troubleshooting
    return FileNames

if __name__ == "__main__":
    now = datetime.now()-timedelta(days=1)
    DATE = datetime(now.year, now.month, now.day) # UTC date
    hours = range(0, 24)                            # model run hour for the date
    for h in hours:
        FileNames = download_hrrr_nat_subsection(DATE, h, forecast=range(1, 19))
        print FileNames

    # There are 50 sigma levels in HRRR
    p1 = []
    p2 = []
    t1 = []
    t2 = []
    # Create a vertical temperature profile at a few points
    for f in FileNames:
        grbs = pygrib.open(f+'.small')
        pres = grbs.select(name='Pressure')
        temp = grbs.select(name='Temperature')
        #
        for l in range(0, 50):
            p1.append(pres[l].values[1, 1]/100)
            p2.append(pres[l].values[30, 30]/100)
            t1.append(temp[l].values[1, 1]-273.15)
            t2.append(temp[l].values[30, 30]-273.15)
            #
            plt.scatter(t1, p1, color='b')
            plt.plot(t1, p1, color='b')
            plt.scatter(t2, p2, color='r')
            plt.plot(t2, p2, color='r')

    plt.gca().invert_yaxis()
    plt.show()
