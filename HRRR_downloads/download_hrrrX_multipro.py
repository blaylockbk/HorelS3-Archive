# Brian Blaylock
# 10 March 2017                                       Spring break is next week

"""
Download eXperimental HRRR (hrrr_X) files from ESRL via FTP

This script should be run by the mesohorse user on meso1.

Run the CRON job at 6:10 PM Mountain Time to get all fields for the
UTC "previous day". (i.e. Since 6:10 PM Mountain Time is the next day in UTC,
when I download from ESRL I am getting the data from "yesterday")

This Script does the following:
1) Downloads all available sfc analyses for the experimental HRRR from via FTP
   from ESRL
"""

from ftplib import FTP
from datetime import date, datetime, timedelta
import os
import stat
import multiprocessing

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
sys.path.append('B:/pyBKB_v2')
from BB_MesoWest.get_token import get_ESRL_credentials

# ----------------------------------------------------------------------------
#                      Stuff you may want to change
# ----------------------------------------------------------------------------
# fxx is a list of forecast hours we want to download for sfc and prs fields.
# f00 is the analysis hour. Forecasts go out 18 hours.
# Currently grabbing analyses for sfc files
sfc_fxx = [0]
#prs_fxx = [0] # Don't download any pressure fields.

# ----------------------------------------------------------------------------
#                        Introductory Stuff
# ----------------------------------------------------------------------------

# Date: "yesterday" is the previous day according to the UTC clock.
yesterday = date.today() #-timedelta(days=1)

# Directory to save the downloads. Create it if it doesn't exist
OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/BB_test/models/hrrrX/' \
        % (yesterday.year, yesterday.month, yesterday.day)
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)
    # Change directory permissions
    os.chmod(OUTDIR, stat.S_IRWXU | \
                     stat.S_IRGRP | stat.S_IXGRP | \
                     stat.S_IROTH | stat.S_IXOTH)
                    # User can read, write, execute
                    # Group can read and execute
                    # Others can read and execute

# Credentials for logging into ESRL FTP database
user, password = get_ESRL_credentials()
# ----------------------------------------------------------------------------

def download_hrrrX_sfc(item):
    """
    Download Surface 2D fields
        Download files that contain only numbers (these represent dates)
        and files for which the date matches the OUTDIR date. (We don't want
        to accidentally put "todays" data in "yesterdays" directory.)
    Input:
        item  - filename is in the form... YYJJJHH00FF00
                Year, Day of Year, Model Hour 00, Forecast 00
    """

    if item.isdigit() \
       and datetime.strptime(item[0:5], '%y%j').day == yesterday.day:
        # 1)
        # Log onto the FTP for each file downloaded (prevent timeout)
        # FTP login:
        ftp = FTP('gsdftp.fsl.noaa.gov')
        ftp.login(user, password)
        ftp.cwd('hrrr/conus/wrftwo')

        # What is the initalized hour and forecast?
        hour = item[5:7]
        forecast = item[9:11]

        # Save the file similar to the standard hrrr file naming convention
        # except insert an X to represent that this is the experimental version
        NEWFILE = 'hrrrX.t%sz.wrfsfcf%s.grib2' % (hour, forecast)
        ftp.retrbinary('RETR '+ item, open(OUTDIR+NEWFILE, 'wb').write)
        ftp.quit()

        print "Saved:", OUTDIR + NEWFILE

def download_hrrrX_prs(item):
    """
    Download Pressure (3D) Fields
        Download files that contain only numbers (these represent dates)
        and files for which the date matches the OUTDIR date. (We don't want
        to accidentally put "todays" data in "yesterdays" directory.)
    Input:
        item  - filename is in the form... YYJJJHH00FF00
                Year, Day of Year, Model Hour 00, Forecast 00
    """

    if item.isdigit() \
       and datetime.strptime(item[0:5], '%y%j').day == yesterday.day:
        # I need to log onto the FTP for each processor
        # FTP login:
        ftp = FTP('gsdftp.fsl.noaa.gov')
        ftp.login(user, password)
        ftp.cwd('hrrr/conus/wrfprs')

        # What is the initalized hour and forecast?
        hour = item[5:7]
        forecast = item[9:11]

        # Save the file similar to the standard hrrr file naming convention
        # except insert an X to represent that this is the experimental version
        NEWFILE = 'hrrrX.t%sz.wrfprsf%s.grib2' % (hour, forecast)
        ftp.retrbinary('RETR '+ item, open(OUTDIR+NEWFILE, 'wb').write)
        ftp.quit()

        print "Saved:", OUTDIR+NEWFILE

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    timer1 = datetime.now()

    # Multiprocessing :)
    num_proc = 3
    p = multiprocessing.Pool(num_proc)

    """
    Get a list of all available files from the FTP site, then
    regenerate the list for files that have the desired forecast hours (fxx).
    Download files from that list.
    """

    # Get surface fields file list
    ftp = FTP('gsdftp.fsl.noaa.gov')
    ftp.login(user, password)
    ftp.cwd('hrrr/conus/wrftwo')
    # Get a list of the files...
    sfc_filenames = ftp.nlst()
    ftp.quit()

    # Only list the files for the desired forecast hours
    sfc_flist = ['%02d00' % (f) for f in sfc_fxx]
    sfc_filenames = [sfc_filenames[i] for i in range(len(sfc_filenames)) \
                     if sfc_filenames[i][-4:] in sfc_flist]

    # Download from the list we collected
    p.map(download_hrrrX_sfc, sfc_filenames)

    print "Time to download hrrrX", datetime.now()-timer1


    """ # How to download pressure fields if you want to start getting those too
    # Get pressure fields
    ftp = FTP('gsdftp.fsl.noaa.gov')
    ftp.login(user, password)
    ftp.cwd('hrrr/conus/wrfprs')
    # List the files...
    prs_filenames = ftp.nlst()
    ftp.quit()

    # Only list the files for the desired forecast hours
    prs_flist = ['%02d00' % (f) for f in prs_fxx]
    prs_filenames = [prs_filenames[i] for i in range(len(prs_filenames)) \
                     if prs_filenames[i][-4:] in prs_flist]

    # Multiprocessing :)
    num_proc = 3
    p = multiprocessing.Pool(num_proc)
    p.map(download_hrrrX_prs, prs_filenames)
    """
