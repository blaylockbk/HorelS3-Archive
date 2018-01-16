# Brian Blaylock
# March 9, 2017

"""
Download archived HRRR files from MesoWest Pando S3 archive system.

Please register before downloading from our HRRR archive:
http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_download_register.html

For info on the University of Utah HRRR archive and to see what dates are 
available, look here:
http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html

Contact:
brian.blaylock@utah.edu
"""

import urllib
from datetime import date, datetime, timedelta
import time
import os

def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    # ',' at the end of the line is important!
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),


model = 'hrrr'
field = 'sfc'
hour = range(0,24)
fxx = range(0,19)
DATE = date(2018, 1, 15)

OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%s/BB_test/models/%s' % (DATE.strftime('%Y%m%d'), model)



# Loop through each hour and each forecast and download.
for h in hour:
    for f in fxx:
        # 1) Build the URL string we want to download.
        #    fname is the file name in the format
        #    [model].t[hh]z.wrf[field]f[xx].grib2
        #    i.e. hrrr.t00z.wrfsfcf00.grib2
        fname = "%s.t%02dz.wrf%sf%02d.grib2" % (model, h, field, f)
        
        URL = 'http://www.nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%s/%s' \
                % (DATE.strftime('%Y%m%d'), fname)
        print URL
        
        # 3) Download the file via https
        # Check the file size, make it's big enough to exist.
        check_this = urllib.urlopen(URL)
        file_size = int(check_this.info()['content-length'])
        if file_size > 10000:
            print "Downloading:", URL
            urllib.urlretrieve(URL, OUTDIR+fname, reporthook)
            print "\n"
        else:
            # URL returns an "Key does not exist" message
            print "ERROR:", URL, "Does Not Exist"