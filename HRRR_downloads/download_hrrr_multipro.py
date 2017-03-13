# Brian Blaylock
# February 27, 2017

"""
Download operational HRRR (hrrr) files from NCEP NOMADS site

This script should be run by the mesohorse user on meso1.

Run the CRON job at 6:10 PM Mountain Time to get all fields for the
UTC "previous day". (i.e. Since 6:10 PM Mountain Time is the next day in UTC,
when I download from ESRL I am getting the data from "yesterday")

This Script does the following:
1) Downloads all sfc analyses and forecasts for the operational HRRR via HTTP
   from NOMADS.
2) Downloads analyses of prs fields for the operational HRRR
"""

import urllib
from datetime import datetime, timedelta
import os
import stat
import multiprocessing # :)

# ----------------------------------------------------------------------------
#                        Introductory Stuff
# ----------------------------------------------------------------------------
# download HRRR files from yesterday (if run after 6:00 PM local then today's
# UTC time is yesterday)
yesterday = datetime.today() #-timedelta(days=1)
DATE = yesterday

# Put the downloaded files in the horel-group/archive. Mkdir if it doesn't exist
OUTDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/BB_test/models/hrrr/' \
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
# ----------------------------------------------------------------------------

def reporthook(a, b, c):
    """
    Report download progress in megabytes
    """
    print "% 3.1f%% of %.2f MB\r" % (min(100, float(a * b) / c * 100), c/1000000.),

def download_hrrr_sfc(hour,
                      field='sfc',
                      forecast=range(0, 19)):
    """
    Downloads HRRR grib2 files from the nomads server
    http://nomads.ncep.noaa.gov/

    Input:
        hour - a list of hours you want to download
               Default all hours in the day
        fields - the field you want to download
                 Options are fields ['prs', 'sfc','subh', 'nat']
                 pressure fields (~350 MB), surface fields (~6 MB),
                 native fields (~510 MB)!
        forecast - a list of forecast hour you wish to download
                   Default all forecast hours (0-18)
    """
    # We'll store the URLs we download from and return them for troubleshooting
    URL_list = []

    # Build the URL string we want to download. One for each field, hour, and forecast
    # New URL for downloading HRRRv2+
    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/' \
          % (DATE.year, DATE.month, DATE.day)
    for f in forecast:
        FileName = 'hrrr.t%02dz.wrf%sf%02d.grib2' % (hour, field, f)
        print ""
        print "NOMADS:", URL+FileName
        # Download and save the file
        print 'Downloading:', OUTDIR+FileName
        urllib.urlretrieve(URL+FileName, OUTDIR+FileName)
        print 'Saved:', OUTDIR+FileName
        URL_list.append(URL+FileName)

    # Return the list of URLs we downloaded from for troubleshooting
    return URL_list

def download_hrrr_prs(hour,
                      field='prs',
                      forecast=[0]):
    """
    Downloads HRRR grib2 files from the nomads server
    http://nomads.ncep.noaa.gov/

    Input:
        hour - the hours you want to download
        fields - the field you want to download
                 Options are fields ['prs', 'sfc','subh', 'nat']
                 pressure fields (~350 MB), surface fields (~6 MB),
                 native fields (~510 MB)!
        forecast - a list of forecast hour you wish to download from that hour
                   Default all forecast hours (0-18)
    """
    # We'll store the URLs we download from and return them for troubleshooting
    URL_list = []

    # Build the URL string we want to download. One for each field, hour, and forecast
    # New URL for downloading HRRRv2+
    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/' \
          % (DATE.year, DATE.month, DATE.day)


    for f in forecast:
        FileName = 'hrrr.t%02dz.wrf%sf%02d.grib2' % (hour, field, f)

        # Download and save the file
        print 'Downloading:', OUTDIR+FileName
        urllib.urlretrieve(URL+FileName, OUTDIR+FileName)
        print 'Saved:', OUTDIR+FileName
        URL_list.append(URL+FileName)

    # Return the list of URLs we downloaded from for troubleshooting
    return URL_list

def download_hrrr_bufr(DATE,
                       stations=['725720'],
                       rename=['kslc'],
                       hour=range(0, 24)):
    """
    Special case for downloading HRRR bufr soundings.
    """
    URL_list = []

    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/bufrsnd.t%02dz/' \
          % (DATE.year, DATE.month, DATE.day, DATE.hour)

    for h in hour:
        for i in range(len(stations)):
            FILE = 'bufr.%s.%04d%02d%02d%02d' \
                % (stations[i], DATE.year, DATE.month, DATE.day, h)
            NEWNAME = '%s_%04d%02d%02d%02d.buf' \
                    % (rename[i], DATE.year, DATE.month, DATE.day, h)
            urllib.urlretrieve(URL+FILE, OUTDIR+NEWNAME)
            URL_list.append(URL+FILE)

    return URL_list

if __name__ == '__main__':

    print "\n================================================"
    print "Downloading operational HRRR"

    timer1 = datetime.now()

    # Multiprocessing :)
    # Each processor will work on a single hour at a time
    hour_list = range(0, 24)
    num_proc = 3
    p = multiprocessing.Pool(num_proc)

    # Download surface fields
    sfc_URLs = p.map(download_hrrr_sfc, hour_list)

    # Download pressure fields
    prs_URLs = p.map(download_hrrr_prs, hour_list)

    # Just download bufr soundings in serial. These are quick.
    # Download bufr soundings: KSLC, KODG, KPVU
    stations = ['725720', '725724', '725750'] #station numbers
    rename = ['kslc', 'kpvu', 'kodg']         #station labels
    bufr_URLs = download_hrrr_bufr(yesterday,
                                   stations=stations,
                                   rename=rename)

    print "Time to download operational HRRR:", datetime.now() - timer1

    import smtplib
    # Send the Email
    sender = 'brian.blaylock@utah.edu'
    receivers = ['blaylockbk@gmail.com']

    message = """From: Check HRRR moved to S3 <brian.blaylock@utah.edu>
    To: HRRR Check <brian.blaylock@utah.edu>
    Subject: Oper HRRR Download %s

    """ % (yesterday) + '\n\nFinished downloading hrrr: %s\nTotalTime: %s' % (datetime.now(), datetime.now()-timer1)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)
        print "Successfully sent email"
    except SMTPException:
        print "Error: unable to send email"
