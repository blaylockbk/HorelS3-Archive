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

    product = 'GLM-L2-LCFA'

    # List files in AWS bucket. List of items include the hour of day.
    AWS = 'noaa-goes16/%s/%s/' % (product, DATE.strftime('%Y/%j'))
    rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
    ls = ' ls goes16AWS:%s | cut -c 11-' % (AWS)
    rclone_out = subprocess.check_output(rclone + ls, shell=True)
    Alist = rclone_out.split('\n')
    Alist.remove('') # remove empty elements (last item in list)


    # Path to horel-group7 and Pando that we want to put things...    
    HG7 = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/%s/%s/' \
            % (product, DATE.strftime('%Y%m%d'))
    PANDO = 'horelS3:GOES16/%s/%s/' \
            % (product, DATE.strftime('%Y%m%d'))


    # Create directory on horel-group7 for every hour if one doesn't exist
    for h in range(24):
        OUTDIR = '%s/%02d/' % (HG7, h)
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)


    # Download each file from Amazon AWS and copy to horel-group7
    #   Note: The item 'i' in Alist includes the hour directory
    for i in Alist:
        hour, FILE = i.split('/')    
        os.system(rclone + ' copy goes16AWS:%s %s' % (AWS+i, HG7+hour+'/'))
        print ""
        print "Downloaded"
        print "  AWS:", AWS+i,
        print "  HG7:", HG7+hour+'/'+FILE


    # Sync the files between horel-group7 and Pando
    os.system('%s sync %s %s' % (rclone, HG7, PANDO))
    print "rclone sync complete:", '%s sync %s %s' % (rclone, HG7, PANDO) 

    # Change permissions of PANDO directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PANDO)
    

if __name__ == '__main__':
    
    sDATE = datetime(2018, 5, 8)
    eDATE = datetime(2018, 5, 22)
    DATES = [sDATE  + timedelta(days=i) for i in range((eDATE-sDATE).days)]

    for D in DATES:    

        print "\n============================================================"
        print "       Download GOES-16 Geostationary Lightning Mapper        "
        print "                         %s        " % D.strftime('%d %B %Y')
        print "=============================================================\n"

        download_goes16_GLM(D)


"""
# ----------------------------------
# GOES16 rclone and s3cmd commands
#------------------------------------
/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/GLM-L2-LCFA/ horelS3:GOES16/GLM-L2-LCFA/
/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd setacl s3://GOES16/GLM-L2-LCFA/ --acl-public --recursive
"""
