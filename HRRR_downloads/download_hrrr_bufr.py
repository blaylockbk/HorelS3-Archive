# Brian Blaylock
# March 14, 2017                                  It's pi day (3.14)

from string import *
from math import *
from time import *
from datetime import *
import os, sys, urllib, time, urllib2
import stat

SCRIPTDIR = '/uufs/chpc.utah.edu/sys/pkg/ldm/oper/models/hrrr_so3s/'
temp = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/temp/'
arcdir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/HRRR/BB_test/oper/buf/'

model = 'hrrr'
sites = ['kslc', 'kogd', 'kpvu']


for site in sites:
    #remove all temp files in the temporary data space
    bufrfile = '%s*.buf' % (temp)
    os.system('rm -f '+bufrfile)

    for hour in range(0, 24):
        webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/HRRR/%02d/hrrr_%s.buf' % (hour, site)
        # Since we don't know the time yet, we save the file as this temporary name
        # and when we find the file's time we will move it to the archive with the
        # correct name.
        localfile = '%s%s_temp%02d.buf' % (temp, site, hour)
        try:
            # Errors using urllib, so use urllib2 and read to a file
            f = urllib2.urlopen(webfile)
            data = f.read()
            with open(localfile, 'wb') as code:
                code.write(data)
        except:
            print 'BUFR file not found:', webfile

        if os.path.exists(localfile):
            print 'Downloaded', webfile, 'as', localfile
            f = open(localfile, 'r')
            ls = f.readlines()
            f.close()
            iyear = int((ls[4].split(' ')[8])[0:2])
            imonth = int((ls[4].split(' ')[8])[2:4])
            iday = int((ls[4].split(' ')[8])[4:6])
            ihour = int((ls[4].split(' ')[8])[7:9])
            print "time:", iyear, imonth, iday, ihour
            HRRR_DIR = arcdir + '20%02d%02d%02d/' % (iyear, imonth, iday)
            S3_DIR = 'horelS3:HRRR/oper/buf/20%02d%02d%02d/' % (iyear, imonth, iday)
            if not os.path.exists(HRRR_DIR):
                os.makedirs(HRRR_DIR)
                os.chmod(HRRR_DIR, stat.S_IRWXU | \
                         stat.S_IRGRP | stat.S_IXGRP | \
                         stat.S_IROTH | stat.S_IXOTH)
            archivefile = HRRR_DIR + '%s_20%02d%02d%02d%02d.buf' \
                          % (site, iyear, imonth, iday, ihour)
            os.system('mv ' + localfile + ' ' + archivefile)
            print 'moved to:', archivefile

            # Copy to S3 archive
            from_here = archivefile
            to_here = S3_DIR
            os.system('rclone copy %s %s' % (from_here, to_here))
            print 'copied to S3 archive'

# plot sounding
#  anl if analysis only
#  for if all hrrr times
#    os.system('/usr/local/bin/python '+SCRIPTDIR+'sounding.py '+ model+' '+site+' 20%02d'%iyear + ' %02d'%imonth + ' %02d'%iday + ' %02d'%ihour+' anl' ) 
