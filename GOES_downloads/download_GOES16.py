# Brian Blaylock
# September 20, 2017

"""
Download GOES-16 satellite data from Amazon AWS
https://aws.amazon.com/public-datasets/goes/
"""

import subprocess
from datetime import date, datetime, timedelta
import os
import stat

"""
Currently, I am only downloading the Multiband Level 2 formated data
All the band data is in that file, but eventually I may want to built
the capability to download specific bands at their full resolution.
"""

# ----------------------------------------------------------------------------
# rclone config file
config_file = '/scratch/local/mesohorse/.rclone.conf' # meso1 mesohorse user
# ----------------------------------------------------------------------------


def delete_old():
    """
    Delete the yesterday's download in the archive space
    Hopefully it has been moved to Pando.
    """
    yesterday = date.today()-timedelta(days=5)
    DELDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%s/BB_test/' \
             % (yesterday.strftime('%Y%m%d'))
    if os.path.exists('DELDIR'):
        os.system('rm -r '+DELDIR)

def download_goes16(DATE,
                    domain='C',
                    product='ABI-L2-MCMIP',
                    bands=range(1,17)):
    """
    Downloads GOES-16 NetCDF files from the Amazon AWS
    https://noaa-goes16.s3.amazonaws.com
    
    Input:
        DATE - a datetime object that includes the hour.
        OUTDIR - where you want to download the file to for short time local storage.
        domain - F = full disk
                 C = CONUS
                 M1 = Mesoscale 1
                 M2 = Mesoscale 2
        product - ABI-L1b-Rad = Advanced Baseline Imager Level 1, Radiances
                  ABI-L2-CMIP = ABI Level 2, Cloud Moisture Product, Reflectance
                  ABI-L2-MCMIP = same as above, but multi band format
        bands - a list between 1 and 16. Default all the bands.
                If you requested the multiband format, this doesn't do anything.
    """

    # List files in AWS bucket
    PATH_AWS = 'noaa-goes16/%s/%s/' % (product+domain[0], DATE.strftime('%Y/%j'))
    rclone = '/uufs/chpc.utah.edu/sys/installdir/rclone/1.29/bin/rclone'
    ls = ' ls goes16AWS:%s | cut -c 11-' % (PATH_AWS)
    rclone_out = subprocess.check_output(rclone + ls, shell=True)
    Alist = rclone_out.split('\n')
    Alist.remove('') # remove empty elements (last item in list)

    # List files in Pando bucket
    PATH_Pando = 'GOES16/%s/%s/' % (product+domain[0], DATE.strftime('%Y%m%d')) # Litte different than AWS path
    Pls = ' ls horelS3:%s | cut -c 11-' % (PATH_Pando)
    Prclone_out = subprocess.check_output(rclone + Pls, shell=True)
    Plist = Prclone_out.split('\n')
    Plist.remove('') # remove empty elements (last item in list)

    for i in Alist:
        # What date does this file belong in? (looking at the scan start time)
        scanDATE = datetime.strptime(i.split('_')[3], 's%Y%j%H%M%S%f')

        # Where shall I put the file on horel-group/archive        
        OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%s/BB_test/goes16/' \
                 % (scanDATE.strftime('%Y%m%d'))
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)
            # Change directory permissions
            os.chmod(OUTDIR, stat.S_IRWXU | \
                            stat.S_IRGRP | stat.S_IXGRP | \
                            stat.S_IROTH | stat.S_IXOTH)
                            # User can read, write, execute
                            # Group can read and execute
                            # Others can read and execute

        # Check if the AWS file exists on Pando already. If it does, go to next
        if i[3:] in Plist:
            print "Already in Pando:", i
            continue

        # Download the file from Amazon AWS and copy to horel-group/archive
        #os.system(rclone+' --config %s copy goes16AWS:%s %s' % (config_file, PATH_AWS+i, OUTDIR))
        os.system('rclone copy goes16AWS:%s %s' % (PATH_AWS+i, OUTDIR))
        print "Downloaded from AWS:", PATH_AWS+i, 'to:', OUTDIR

        # Copy the file to Pando (little different than the AWS path)
        #os.system(rclone + ' --config %s copy %s horelS3:%s' % (config_file, OUTDIR+i, PATH_Pando))
        os.system('rclone copy %s horelS3:%s' % (OUTDIR+i[3:], PATH_Pando))
        print "Moved to Pando:", PATH_Pando

    # Change permissions of S3 directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PATH_Pando)
    #

if __name__ == '__main__':

    print "\n================================================"
    print "    Downloading GOES-16 from NOAA AWS Archive"
    print "================================================\n"


    DATE = datetime.utcnow()                      

    download_goes16(DATE)
    delete_old()



