# Brian Blaylock
# May 30, 2018                                    Building a new deck this week

"""
Download : GOES-16 Geostationary Lightning Mapper (GLM)
    From : Amazon AWS
     URL : https://aws.amazon.com/public-datasets/goes/
"""

import subprocess
from datetime import datetime, timedelta
import os
import stat
import numpy as np


def download_goes16_GLM(DATE):
    """
    Downloads GOES-16 NetCDF files for the Geostation Lightning Mapper (GLM)
    from the Amazon AWS (https://noaa-goes16.s3.amazonaws.com)
    
    Input:
        DATE - a datetime object for the date that you want to download from.
    """
    print "\n============================================================="
    print "       Download GOES-16 Geostationary Lightning Mapper        "
    print "                         %s        " % DATE.strftime('%d %B %Y')
    print "=============================================================\n"
    
    product = 'GLM-L2-LCFA'

    AWS = 'goes16AWS:noaa-goes16/%s/%s/' % (product, DATE.strftime('%Y/%j'))
    HG7 = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/%s/%s/' \
            % (product, DATE.strftime('%Y%m%d'))
    PANDO = 'horelS3:GOES16/%s/%s/' % (product, DATE.strftime('%Y%m%d'))

    # Sync AWS and horel-group7, retaining hour directories
    rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
    print 'Syncing AWS --> horel-group7...'
    os.system('%s sync %s %s' % (rclone, AWS, HG7))
    print '        AWS --> horel-group7...DONE!'

    print 'Syncing horel-group7 --> Pando...'
    os.system('%s sync %s %s' % (rclone, HG7, PANDO))
    print '        horel-group7 --> Pando...DONE!'

    # Change permissions of PANDO directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PANDO.split(':')[1])
    

if __name__ == '__main__':
    
    #sDATE = datetime(2018, 10, 24)
    #eDATE = datetime(2018, 10, 26)
    #DATES = [sDATE  + timedelta(days=i) for i in range((eDATE-sDATE).days)]
    #for DATE in DATES:     
    #    download_goes16_GLM(DATE)

    DATE = datetime.utcnow()
    #DATE = datetime(2018, 10, 22, 1)
    download_goes16_GLM(DATE)

    if DATE.hour == 0 and DATE.minute < 20:
        yesterday = DATE-timedelta(days=1)
        download_goes16_GLM(yesterday)

    print "\nrun time: ", datetime.utcnow() - DATE
"""
# ----------------------------------
# GOES16 rclone and s3cmd commands
#------------------------------------
/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/GLM-L2-LCFA/ horelS3:GOES16/GLM-L2-LCFA/
/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd setacl s3://GOES16/GLM-L2-LCFA/ --acl-public --recursive
"""
