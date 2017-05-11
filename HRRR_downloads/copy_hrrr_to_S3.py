# Brian Blaylock
# March 1, 2017                                          Toothaches are not fun

"""
Use python to execute an rclone command that copies HRRR files from the 
horel-group/archive/models/ to the horelS3:HRRR archive buckets.
This script should be run by the mesohorse user on meso1.

Requirements:
    rclone        <- module load rclone
    rclone-beta   <- should be installed in this horel-group/archive_s3 directory

What this script does:
1) For each model type [hrrr, hrrrX, hrrrAK], copy the file to the horelS3
   archive. Special cases for each model.
2) Changes permissions to public, so it can be downloaded via http
3) Create .idx file and save in hore-group/archive/HRRR
"""

from datetime import date, datetime, timedelta
import os
import multiprocessing #:)
import numpy as np

# =============================================================================
#                      Introductory Stuff
# =============================================================================
# Dates, start and end
if datetime.now().hour < 15:
    # if it before noon (local) then get yesterdays date
    # 1) maybe the download script ran long and it's just after midnight
    # 2) mabye you need to rerun this script in the morning
    DATE = date.today() -timedelta(days=1)
else:
    # it's probably after 6 local
    DATE = date.today()

# rclone config file
config_file = '/scratch/local/mesohorse/.rclone.conf' # meso1 mesohorse user

model_HG_names = {1:'hrrr', 2:'hrrrX', 3:'hrrrAK'} # name in horel-group/archive
model_S3_names = {1:'oper', 2:'exp', 3:'alaska'}   # name in horelS3:
file_types = ['sfc', 'prs', 'subh']                 # model file file_types
# =============================================================================

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

print "\n================================================"
print "Moving HRRR to S3"

for model_type in [1, 2, 3]:
    """
    Attempt to copy all possible hours, forecast hours, and variable types etc.
    for HRRR from thehorel-group/archive to the horelS3:HRRR archive.
    """
    timer1 = datetime.now()

    model = model_HG_names[model_type]

    # Build the current day directory and file to move
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/BB_test/models/%s/' \
        % (DATE.year, DATE.month, DATE.day, model)

    # HRRR and HRRRx have 18 hour forcasts, Alaska has 36 hour forecasts.
    # HRRR and HRRRx run every hour, Alaska runs every three hours.
    if model == 'hrrrAK':
        forecasts = np.arange(0, 37)
        hours = np.arange(0, 24, 3)
    else:
        forecasts = np.arange(0, 19)
        hours = np.arange(0, 24)

    # Open file for printing output log. Organize into directories by year and month.
#    log_path = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/logs/%s_%04d-%02d' \
#               % (model, DATE.year, DATE.month)
#    if not os.path.exists(log_path):
#        os.makedirs(log_path)

#    log = open('%s/%s_%04d-%02d-%02d.txt' % (log_path, model, DATE.year, DATE.month, DATE.day), 'w')
#    log.write('Moving %s files\nDate: %s\n' % (model, DATE))
#    log.write('Origin: ' + DIR)

    # Do lots of loops...file types (t), hour of day (h), forecast hour (f).

    # loop for each type: sfc, prs, buf
    for t in file_types:

        # Build the new S3 directory path name (e.g. HRRR/oper/sfc/20171201)
        DIR_S3 = 'HRRR/%s/%s/%04d%02d%02d/' \
                    % (model_S3_names[model_type], t, DATE.year, DATE.month, DATE.day)
#        log.write('  \n\nCopy to: horelS3:'+DIR_S3+'\n')
#        log.write("========== Checking for "+model + ' ' + t +" files ====================\n")

        # loop for each hour (0,24)
        for h in hours:
#            log.write('Hour %02d:' % (h))

            # loop for each forecast hour, depenent on model type.
            for f in forecasts:
                # Skip known condition that doesn't exist
                if t == 'buf' and f > 0:
                    # bufr files not dependent on the forecast hour becuase
                    # analysis and forecast are in the same file.
                    continue

                print ""
                print "===================================="
                print "  Where am I?"
                print "      Date  =", DATE
                print "      model =", model
                print "      type  =", t
                print "      hour  =", h
                print "      forec =", f

                # File format example: hrrr.t00z.wrfsfcf00.grib2
                FILE = DIR + '%s.t%02dz.wrf%sf%02d.grib2' % (model, h, t, f)
                # Check if the grib2 file exists.
                # If it does, then copy the file to S3 and create a .idx file.
                if os.path.isfile(FILE):
                    copy_to_horelS3(FILE, DIR_S3)
                    create_idx(FILE, DIR_S3)
#                    log.write('[f%02d]' % (f))
                else:
                    print ""
#                    log.write('[   ]')

#            log.write('\n')

        # Change permissions of S3 directory to public
        s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
        os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % DIR_S3)

#    log.close()
    print "Timer, copy from horel-gropu/archvie to S3:", datetime.now() - timer1
