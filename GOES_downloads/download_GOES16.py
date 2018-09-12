# Brian Blaylock
# September 20, 2017

"""
Download GOES-16 satellite data from Amazon AWS
https://aws.amazon.com/public-datasets/goes/

Updates/To Do:
[X] 12/14/2017 - Updated for GOES16 East Position
[ ]

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
import pyproj

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
sys.path.append('B:\pyBKB_v2')
from BB_GOES16.get_ABI import get_GOES16_truecolor, get_GOES16_firetemperature, file_nearest
from BB_GOES16.get_GLM import get_GLM_files_for_ABI, accumulate_GLM
from BB_basemap.draw_maps import draw_Utah_map


"""
I only download the Multiband Level 2 formated data.
"""

# ----------------------------------------------------------------------------
# CONUS Map object
m = Basemap(projection='geos', lon_0='-75.0',
            resolution='i', area_thresh=10000,
            llcrnrx=-3626269.5, llcrnry=1584175.9,
            urcrnrx=1381770.0, urcrnry=4588198.0)

# Map of Utah
mU = draw_Utah_map()

# Load the Latitude and Longitude grid
#GOES16_latlon = '/uufs/chpc.utah.edu/common/home/horel-group/archive/GOES16/goes16_conus_latlon.npy'
#latlon = np.load(GOES16_latlon).item()

# ----------------------------------------------------------------------------
def download_goes16(DATE,
                    domain='C',
                    product='ABI-L2-MCMIP'):
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
    """

    # List files in AWS bucket
    PATH_AWS = 'noaa-goes16/%s/%s/' % (product+domain[0], DATE.strftime('%Y/%j'))
    rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
    ls = ' ls goes16AWS:%s | cut -c 11-' % (PATH_AWS)
    rclone_out = subprocess.check_output(rclone + ls, shell=True)
    Alist = rclone_out.split('\n')
    Alist.remove('') # remove empty elements (last item in list)

    # List files in Pando bucket
    PATH_Pando = 'GOES16/%s/%s/' % (product+domain[0], DATE.strftime('%Y%m%d')) # Little different than AWS path
    Pls = ' ls horelS3:%s | cut -c 11-' % (PATH_Pando)
    Prclone_out = subprocess.check_output(rclone + Pls, shell=True)
    Plist = Prclone_out.split('\n')
    Plist.remove('') # remove empty elements (last item in list)

    for i in Alist:
        # What date does this file belong in? (looking at the scan start time)
        scanDATE = datetime.strptime(i.split('_')[3], 's%Y%j%H%M%S%f')
        print scanDATE

        # Where shall I put the file on horel-group/archive        
        OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/%s/%s/' \
                 % (product+domain[0], scanDATE.strftime('%Y%m%d'))
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)

        # Check if the AWS file exists on Pando already. If it does, go to next
        if i[3:] in Plist:
            print "Already in Pando:", i
            continue
    
        # Download the file from Amazon AWS and copy to horel-group7/Pando
        os.system(rclone + ' copy goes16AWS:%s %s' % (PATH_AWS+i, OUTDIR))
        print ""
        print "Downloaded from AWS:", PATH_AWS+i, 'to:', OUTDIR
        print ""

        # Copy the file to Pando (little different than the AWS path)
        os.system(rclone + ' copy %s horelS3:%s' % (OUTDIR+i[3:], PATH_Pando))
        print ""
        print "Moved to Pando:", PATH_Pando
        print ""

        # Create true color image of the file
        G = get_GOES16_truecolor(OUTDIR+i[3:], only_RGB=False, night_IR=True)
        FT = get_GOES16_firetemperature(OUTDIR+i[3:], only_RGB=False)
        max_RGB = np.nanmax([G['rgb_tuple'], FT['rgb_tuple']], axis=0)
        GLM = accumulate_GLM(get_GLM_files_for_ABI(i[3:]))
        plt.figure(1)
        plt.clf()
        plt.cla()
        m.imshow(np.flipud(G['TrueColor']))
        m.scatter(GLM['longitude'], GLM['latitude'], marker='+', color='yellow', latlon=True)
        m.drawcoastlines(linewidth=.25)
        m.drawstates(linewidth=0.25)
        m.drawcountries(linewidth=0.25)
        plt.title('GOES-16 True Color, Night IR, and Lightning (GLM)\n%s' % (G['DATE'].strftime('%Y %B %d, %H:%M UTC')))
        plt.xlabel(i[3:])
        FIG = OUTDIR+i[3:-2]+'png'
        plt.savefig(FIG)
        # Move Figure to Pando
        os.system(rclone + ' copy %s horelS3:%s' % (FIG, PATH_Pando))
    
        # Draw Utah Map
        newmap = mU.pcolormesh(G['lon'], G['lat'], G['TrueColor'][:,:,1],
                               color=max_RGB,
                               linewidth=0) # when plotting on cylindrical coordinates, dont set latlon=True. Only if plotting over HRRR domain
        newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
        mU.scatter(GLM['longitude'], GLM['latitude'], marker='+', color='yellow', latlon=True)
        mU.drawstates()
        mU.drawcounties()
        FIG = OUTDIR+i[3:-2]+'UTAH.png'
        plt.savefig(FIG)
        # Move Figure to Pando
        os.system(rclone + ' copy %s horelS3:%s' % (FIG, PATH_Pando))        
        
        print ""
        print 'FIGURE:', PATH_Pando, FIG
        print ""

    # Change permissions of S3 directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PATH_Pando)
    #

if __name__ == '__main__':

    print "\n============================================================"
    print " Downloading GOES-16 ABI from NOAA AWS Archive and Copy to Pando  "
    print "=============================================================\n"

    
    DATE = datetime.utcnow()
    #DATE = datetime(2018, 9, 10, 12)
    
    download_goes16(DATE)

    # Extra attempt to download yesterday's last hour due to day change,
    if DATE.hour == 0:
        yesterday = DATE-timedelta(days=1)
        download_goes16(yesterday)


"""
# GOES16
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/ horelS3:GOES16/
/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd setacl s3://GOES16/ --acl-public --recursive
"""