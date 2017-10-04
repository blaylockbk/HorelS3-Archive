# Brian Blaylock
# September 29, 2017

"""
Download GOES-16 satellite data from Amazon AWS
https://aws.amazon.com/public-datasets/goes/

For a specific day
"""
import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"
import subprocess
from datetime import date, datetime, timedelta
import os
import stat
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_GOES16.get_GOES16 import get_GOES16_truecolor
from BB_basemap.draw_maps import draw_Utah_map


"""
Currently, I am only downloading the Multiband Level 2 formated data
All the band data is in that file, but eventually I may want to built
the capability to download specific bands at their full resolution.
"""

# ----------------------------------------------------------------------------
# rclone config file
config_file = '/scratch/local/mesohorse/.rclone.conf' # meso1 mesohorse user

# CONUS Map object
m = Basemap(projection='geos', lon_0='-89.5',
            resolution='i', area_thresh=1000,
            llcrnrx=-2684381.2,llcrnry=1524055.2,
            urcrnrx=2323658.2,urcrnry=4528077.5)

# Map of Utah
mU = draw_Utah_map()

# Load the Latitude and Longitude grid
GOES16_latlon = '/uufs/chpc.utah.edu/common/home/horel-group/archive/GOES16/goes16_conus_latlon.npy'
latlon = np.load(GOES16_latlon).item()

# ----------------------------------------------------------------------------


def delete_old(D):
    """
    Delete the download in the archive space
    Hopefully it has been moved to Pando.
    """
    DATE = D
    DELDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%s/BB_test/' \
             % (DATE.strftime('%Y%m%d'))
    if os.path.exists(DELDIR):
        os.system('rm -r '+DELDIR)
        print "DELETED:", DELDIR


def download_goes16(DATE,
                    domain='C',
                    product='ABI-L2-MCMIP',
                    bands=range(1,17),
                    replace=False):
    """
    Downloads GOES-16 NetCDF files from the Amazon AWS
    https://noaa-goes16.s3.amazonaws.com
    
    Input:
        DATE - a datetime object that includes.
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

        if replace==False:
            # Check if the AWS file exists on Pando already. If it does, go to next
            if i[3:] in Plist:
                print "Already in Pando:", i
                continue
    
        # Download the file from Amazon AWS and copy to horel-group/archive
        #os.system(rclone+' --config %s copy goes16AWS:%s %s' % (config_file, PATH_AWS+i, OUTDIR))
        os.system('rclone copy goes16AWS:%s %s' % (PATH_AWS+i, OUTDIR))
        print ""
        print "Downloaded from AWS:", PATH_AWS+i, 'to:', OUTDIR
        print ""

        # Copy the file to Pando (little different than the AWS path)
        #os.system(rclone + ' --config %s copy %s horelS3:%s' % (config_file, OUTDIR+i, PATH_Pando))
        os.system('rclone move %s horelS3:%s' % (OUTDIR+i[3:], PATH_Pando))
        print ""
        print "Moved to Pando:", PATH_Pando
        print ""

        try:
            # Create true color image of the file
            G = get_GOES16_truecolor(OUTDIR+i[3:], only_RGB=False, night_IR=True)
            plt.figure(1)
            plt.clf()
            plt.cla()
            m.imshow(np.flipud(G['TrueColor']))
            m.drawcoastlines()
            m.drawstates()
            m.drawcountries()
            plt.title('GOES-16 True Color\n%s' % i[3:])
            FIG = OUTDIR+i[3:-2]+'png'
            plt.savefig(FIG)
            # Move Figure to Pando
            os.system('rclone move %s horelS3:%s' % (FIG, PATH_Pando))
        
            # Draw Utah Map
            newmap = mU.pcolormesh(G['lon'], G['lat'], G['TrueColor'][:,:,1],
                                    color=G['rgb_tuple'],
                                    linewidth=0,
                                    latlon=True)
            newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
            mU.drawstates()
            mU.drawcounties()
            FIG = OUTDIR+i[3:-2]+'UTAH.png'
            plt.savefig(FIG)
            # Move Figure to Pando
            os.system('rclone move %s horelS3:%s' % (FIG, PATH_Pando))        
            
            print ""
            print 'FIGURE:', PATH_Pando, FIG
            print ""
        except:
            # What happened? Probably an error with the storage class,
            # i.e. the object is on AWS Glacier now, and can not be downloaded.
            # We will exit the function.
            print "\n\nERROR, PROBABLY WITH STORAGE CLASS. MOVE TO NEXT DAY\n\n"
            return None

    # Change permissions of S3 directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PATH_Pando)
    #

if __name__ == '__main__':

    print "\n============================================================"
    print " Downloading GOES-16 from NOAA AWS Archive and Copy to Pando  "
    print "=============================================================\n"

    
    base = datetime(2017, 9, 1)
    eDATE = datetime(2017, 9, 15)
    days = (eDATE - base).days
    DATES = np.array([base + timedelta(days=x) for x in range(0, days)])
        
    for D in DATES:
        print """
        ============== Working on: %s ===============
        """ % (D.strftime('%Y %B %d'))
        download_goes16(D, replace=True)
        delete_old(D)

