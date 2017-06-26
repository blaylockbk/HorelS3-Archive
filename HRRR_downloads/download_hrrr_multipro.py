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
import urllib2
from datetime import date, datetime, timedelta
import os
import stat
import multiprocessing # :)
from queue import Queue
from threading import Thread


# ----------------------------------------------------------------------------
#                        Introductory Stuff
# ----------------------------------------------------------------------------
# download HRRR files from yesterday (if run after 6:00 PM local then today's
# UTC time is yesterday)
# Dates, start and end
if datetime.now().hour < 12:
    # if it before noon (local) then get yesterdays date
    # 1) maybe the download script ran long and it's just after midnight
    # 2) mabye you need to rerun this script in the morning
    yesterday = datetime.today() -timedelta(days=1)
else:
    # it's probably after 6 local
    yesterday = datetime.today()

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

# rclone config file
config_file = '/scratch/local/mesohorse/.rclone.conf' # meso1 mesohorse user

# Naming convention
model_HG_names = {1:'hrrr', 2:'hrrrX', 3:'hrrrAK'} # name in horel-group/archive
model_S3_names = {1:'oper', 2:'exp', 3:'alaska'}   # name in horelS3:
file_types = ['sfc', 'prs', 'subh']                 # model file file_types
# ----------------------------------------------------------------------------

## Delete the previous day's download
previous_day = yesterday-timedelta(days=1)
DELDIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/BB_test/' \
    % (previous_day.year, previous_day.month, previous_day.day)
os.system('rm -r '+DELDIR)

def create_idx(for_this_file, put_here):
    """
    Create a .idx file and move to horel-group/archive/HRRR
    """
    file_name = for_this_file.split('/')[-1]
    idx_dir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/' + put_here
    if not os.path.exists(idx_dir):
        os.makedirs(idx_dir)
    idx_name = idx_dir + file_name + '.idx'
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + idx_name)
    print "created idx file:", idx_name

def copy_to_horelS3(from_here, to_there):
    """
    Copy the file to the horelS3: archive using rclone
    Input:
        from_here - string of full path and file name you want to copy
        to_there  - string of path on the horelS3 archive
    """
    # Copy the file from_here to_there (the path will be created if it doesn't exist)
    os.system('rclone --config %s copy %s horelS3:%s' \
              % (config_file, from_here, to_there))

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
    Also can be used to download subh field.

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
    #
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

        # Move FILE to S3
        FILE = OUTDIR+FileName
        DIR_S3 = 'HRRR/%s/%s/%04d%02d%02d/' \
                    % ('oper', field, DATE.year, DATE.month, DATE.day)
        if os.path.isfile(FILE):
            copy_to_horelS3(FILE, DIR_S3)
            create_idx(FILE, DIR_S3)
        else:
            print "%s does not exist", FILE

    # Change permissions of S3 directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % DIR_S3)
    #
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
    #
    # Build the URL string we want to download. One for each field, hour, and forecast
    # New URL for downloading HRRRv2+
    URL = 'http://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.%04d%02d%02d/' \
          % (DATE.year, DATE.month, DATE.day)
    #
    for f in forecast:
        FileName = 'hrrr.t%02dz.wrf%sf%02d.grib2' % (hour, field, f)
        # Download and save the file
        print 'Downloading:', OUTDIR+FileName
        urllib.urlretrieve(URL+FileName, OUTDIR+FileName)
        print 'Saved:', OUTDIR+FileName
        URL_list.append(URL+FileName)

        # Move FILE to S3
        FILE = OUTDIR+FileName
        DIR_S3 = 'HRRR/%s/%s/%04d%02d%02d/' \
                    % ('oper', field, DATE.year, DATE.month, DATE.day)
        if os.path.isfile(FILE):
            copy_to_horelS3(FILE, DIR_S3)
            create_idx(FILE, DIR_S3)
        else:
            print "%s does not exist", FILE

    # Change permissions of S3 directory to public
    s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
    os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % DIR_S3)
    #
    # Return the list of URLs we downloaded from for troubleshooting
    return URL_list

def worker():
    """
    This is what the thread will do when called and given input.
    If the thread hangs, then try a second time.
    """
    while True:
        item = q.get()
        print "Work on:", item

        try:
            download_hrrr_sfc(item)
        except:
            try:
                print "\n>> I tried, so I'll try sfc again <<\n"
                download_hrrr_sfc(item)
            except:
                print "\n>> I tried, and tried, but couldn't get sfc <<\n"

        try:
            download_hrrr_prs(item)
        except:
            try:
                print "\n>> I tried, so I'll try prs again <<\n"
                download_hrrr_prs(item)
            except:
                print "\n>> I tried, and tried, but couldn't get prs <<\n"
        try:
            download_hrrr_sfc(item, field='subh', forecast=range(0, 19))
        except:
            try:
                print "\n>> I tried, so I'll try subh again <<\n"
                download_hrrr_sfc(item, field='subh', forecast=range(0, 19))
            except:
                print "\n>> I tried, and treid, but couldn't get subh <<\n"

        q.task_done()

if __name__ == '__main__':

    """
    Downloading with multithreading is more efficient and faster than
    downloading with multiprocessing.
    """

    print "\n================================================"
    print "Downloading operational HRRR"


    hour_list = range(0, 24)
    hour_list = [7]

    """# Download with Multiprocessing :)
    # Multiprocessing :) (Takes over a half hour!)
    # Each processor will work on a single hour at a time
    timer1 = datetime.now()
    num_proc = 3
    p = multiprocessing.Pool(num_proc)

    # Download surface fields
    sfc_URLs = p.map(download_hrrr_sfc, hour_list)

    # Download pressure fields
    prs_URLs = p.map(download_hrrr_prs, hour_list)

    print "Time to download operational HRRR (Multiprocessor):", datetime.now() - timer1
    """


    # Multithreading :P 
    # Much faster than multiprocessing when downloading, but threads will hang.
    timer1 = datetime.now()

    # Set up number of threads
    num_of_threads = 10
    # Initalize a queue for each thread. The Thread will do the "worker" function
    q = Queue()
    for i in range(num_of_threads):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    # Add a task to the queue
    for item in hour_list:
        q.put(item)

    q.join()       # block until all tasks are done

    print "Time to download operational HRRR (Threads):", datetime.now() - timer1

    exit()
