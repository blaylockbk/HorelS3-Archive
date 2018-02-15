# Brian Blaylock
# September 29, 2017

"""
Download GOES-16 satellite data from Amazon AWS
https://aws.amazon.com/public-datasets/goes/

For a range of days
"""
import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"
import subprocess
from datetime import date, datetime, timedelta
import os
import urllib
import stat
import socket
import getpass
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

if getpass.getuser() != 'mesohorse' or socket.gethostname() != 'meso2.chpc.utah.edu':
    print "--> You are %s on %s" % (getpass.getuser(), socket.gethostname())
    print "--> Please run this script with the mesohorse user on meso2."
    exit()

# ----------------------------------------------------------------------------
# rclone config file
config_file = '/scratch/local/mesohorse/.rclone.conf' # meso1 mesohorse user

# CONUS Map object After December 14, 2017
m1 = Basemap(projection='geos', lon_0='-75.0',
            resolution='i', area_thresh=1000,
            llcrnrx=-3626269.5, llcrnry=1584175.9,
            urcrnrx=1381770.0, urcrnry=4588198.0)

# CONUS Map object Before December 14, 2017
m0 = Basemap(projection='geos', lon_0='-89.5',
            resolution='i', area_thresh=1000,
            llcrnrx=-2684381.2,llcrnry=1524055.2,
            urcrnrx=2323658.2,urcrnry=4528077.5)

# Map of Utah
mU = draw_Utah_map()

# Load the Latitude and Longitude grid
GOES16_latlon0 = '/uufs/chpc.utah.edu/common/home/horel-group/archive/GOES16/goes16_conus_latlon_central.npy'
latlon0 = np.load(GOES16_latlon0).item()

GOES16_latlon1 = '/uufs/chpc.utah.edu/common/home/horel-group/archive/GOES16/goes16_conus_latlon_east.npy'
latlon1 = np.load(GOES16_latlon1).item()


def reporthook(a, b, c):
    """
    Print download progress in megabytes.
    Example:
        urllib.urlretrieve(URL, OUTFILE, reporthook=reporthook)
    """
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),

def make_plots(args):
    """
    Multiprocessing
    Create CONUS and Utah images for each GOES16 file
        FILE     - is the full path to the file to the NetCDF data file
        FULLPATH - is the directory to save the image files
        DATE     - datetime of interest
    """
    FILE, FULLPATH, DATE = args
    try:
        # Pick the correct satellite latitude
        if DATE > datetime(2017, 12, 14):
            m = m1
            latlon = latlon1
        else:
            m = m0
            latlon = latlon0

        # Name of file, stripped of extensions
        IMG_FILE = FILE[:-3]

        if not os.path.isfile(FULLPATH+IMG_FILE+'.png'):
            # Create true color image of the file
            print FULLPATH+FILE
            G = get_GOES16_truecolor(FULLPATH+FILE, only_RGB=False, night_IR=True)
            plt.figure(1)
            plt.clf()
            plt.cla()
            m.imshow(np.flipud(G['TrueColor']))
            m.drawcoastlines(linewidth=.25)
            m.drawstates(linewidth=0.25)
            m.drawcountries(linewidth=0.25)
            plt.title('GOES-16 True Color and Night IR\n%s' % (G['DATE'].strftime('%Y %B %d, %H:%M UTC')))
            plt.xlabel(FILE)
            FIG = FULLPATH+IMG_FILE+'.png'
            plt.savefig(FIG)
        
            # Draw Utah Map
            newmap = mU.pcolormesh(G['lon'], G['lat'], G['TrueColor'][:,:,1],
                                color=G['rgb_tuple'],
                                linewidth=0)
            newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
            mU.drawstates()
            mU.drawcounties()
            FIG = FULLPATH+IMG_FILE+'.UTAH.png'
            plt.savefig(FIG)
    except:
        print ""
        print "FAILED: ", FULLPATH+FILE
        print ""

# ----------------------------------------------------------------------------

def download_goes16(DATE,
                    domain='C',
                    product='ABI-L2-MCMIP',
                    bands=range(1,17)):
    """
    Downloads GOES-16 NetCDF files from the Amazon AWS
    https://noaa-goes16.s3.amazonaws.com
    
    Input:
        DATE - a datetime object that includes.
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

    # Copy AWS bucket to horel-group7
    rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
    
    AWS = 'goes16AWS:noaa-goes16/%s/%s/' % (product+domain[0], DATE.strftime('%Y/%j'))
    HG7 = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'
    PATH = 'GOES16/%s/%s/' % (product+domain[0], DATE.strftime('%Y%m%d'))
    if not os.path.exists(HG7+PATH):
                os.makedirs(HG7+PATH)

    # Easiest to sync horel-group7 with AWS, but AWS only keeps files from
    # last 60 days, so we'll need to download from OCC instead.
    if DATE > datetime.now()-timedelta(days=60):        
        for hour in range(0,24):
            # Do not sync, because it will overwrite files. Copy will keep everything.
            os.system('%s copy %s%02d/ %s' % (rclone, AWS, hour, HG7+PATH))
    else:
        # We need to download each file individually from OCC from the list of files on AWS
        ls = ' ls %s | cut -c 11-' % (AWS)
        rclone_out = subprocess.check_output(rclone + ls, shell=True)
        Alist = rclone_out.split('\n')
        Alist.remove('') # remove empty elements (last item in list)

        URL = 'https://osdc.rcc.uchicago.edu/%s' % (AWS.split(':')[1])
        for i in Alist:
            # Only download if it appears the file exists based on it's size.
            print URL+i
            try:
                if not os.path.exists(HG7+PATH+i.split('/')[1]):
                    if int(urllib.urlopen(URL+i).info()['Content-Length']) > 100000:
                        urllib.urlretrieve(URL+i, HG7+PATH+i.split('/')[1], reporthook)
                else:
                    print 'EXISTS:', HG7+PATH+i.split('/')[1]
            except:
                print 'none in', URL+i

    """
    # For every .nc file in HG7, create a png for CONUS and UTAH if it does not exist
    NC_FILES = filter(lambda x: x[-3:]=='.nc', os.listdir(HG7+PATH))
    
    # Create the Plots with Multiprocessing
    import multiprocessing
    p = multiprocessing.Pool(10)
    args = [[F, HG7+PATH, DATE] for F in NC_FILES]
    result = p.map(make_plots, args)            
    #for a in args:
    #    make_plots(a)
    """
    
    # Sync with Pando
    print ' -- rclone --'
    S3 = 'horelS3:'
    os.system('%s sync %s %s' % (rclone, HG7+PATH, S3+PATH))

    # Change permissions of S3 directory to public
    print ' -- s3cmd --'
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PATH)
    #

if __name__ == '__main__':

    print "\n============================================================"
    print " Downloading GOES-16 from NOAA AWS Archive and Copy to Pando  "
    print "=============================================================\n"   

    base = datetime(2017, 7, 12)
    eDATE = datetime(2018, 2, 6)
    days = (eDATE - base).days
    DATES = np.array([base + timedelta(days=x) for x in range(0, days)])
        
    for D in DATES:
        print """============== Working on: %s ===============""" % (D.strftime('%Y %B %d'))
        download_goes16(D)
