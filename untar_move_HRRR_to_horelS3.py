# Brian Blaylock
# February 24, 2017                 Roads were bad this morning because of snow

"""
Use python to execute an rclone command that copies HRRR files from the
the horel-group/archive/models/ to the horelS3:HRRR archive buckets.
This script should be run on wx4.
Just do this sequentually in a while loop. Don't use multiprocessing.

Requirements:
    rclone:      module load rclone
    rclone-beta: should be here in this directory
    g2ctl.pl:    should be here in this directory
    grads:       module load grads
"""

from datetime import datetime, timedelta
import os
import shutil
import numpy as np

# =============================================================================
#                      Stuff you can change :)
# =============================================================================

# Dates, start and end
DATE = datetime(2016, 9, 2)
eDATE = datetime(2016, 10, 1)

# Model type: 1) hrrr    2) hrrrX    3) hrrr_alaska)
model_type = 3

# =============================================================================
# =============================================================================

# rclone config file
config_file = '/uufs/chpc.utah.edu/sys/pkg/ldm/.rclone.conf' # meteo19 LDM user

# info about the models
model_options = {1:'hrrr', 2:'hrrrX', 3:'hrrr_alaska'} # name in horel-group/archive
model_S3_names = {1:'oper', 2:'exp', 3:'alaska'}       # name in horelS3:
types = ['sfc', 'prs', 'buf']                          # model file types


def untar_model_dir(DATE, model):
    """
    Run this on WX1
    untar the model directory and put it in the /temp directory
    Make sure you are in the directory you want to untar this stuff.
    """

    # Set the TAR directory/file path
    if DATE >= datetime(2016, 7, 1):
        TAR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%04d%02d%02d/models.tar.gz' \
            % (DATE.year, DATE.month, DATE.day)
    elif DATE >= datetime(2016, 1, 1):
        # its on horel group 5, but for some reason the date direcotries are
        # double layered. I don't know why.
        TAR = '/uufs/chpc.utah.edu/common/home/horel-group5/archive/%04d%02d%02d/%04d%02d%02d/models.tar.gz' \
            % (DATE.year, DATE.month, DATE.day, DATE.year, DATE.month, DATE.day)
    else:
        # It's on horel-group5
        TAR = '/uufs/chpc.utah.edu/common/home/horel-group5/archive/%04d%02d%02d/models.tar.gz' \
            % (DATE.year, DATE.month, DATE.day)
    # Set the destination to copy the files to
    DESTINATION = '-C /scratch/local/Brian_untar_HRRR/'

    # What is the folder name? It's the same as the date and the model (e.g. hrrr)
    FOLDER = '%04d%02d%02d/models/%s' % (DATE.year, DATE.month, DATE.day, model)
    print "!!!!"
    print 'tar -xzvf %s %s %s' % (TAR, DESTINATION, FOLDER)
    print "!!!!"
    os.system('tar -xzvf %s %s %s' % (TAR, DESTINATION, FOLDER))

    return DESTINATION[3:]

def create_grb_idx(this_file):
    """
    Create the .ctl and .idx file for the grib2 file.
    A few important notes:
    1. Uses the script 'g2ctl.pl', originally from Jim's processing
       /uufs/chpc.utah.edu/sys/pkg/ldm/oper/models/base/g2ctl.pl
    2. Requires GrADS, so make sure you "module load grads" before running the
       python script.
    """
    print ""
    print "========= Messages from creating .ctl and .idx files =============="
    # Create the .ctl file
    os.system('/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/g2ctl.pl ' + this_file + '>' + this_file + '.ctl')
    # Create the .idx file (gribmap is a GrADS function)
    os.system('gribmap -i ' + this_file +'.ctl -0')
    print "==================================================================="

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

    if from_here[-6:] == '.grib2':
        # Create the .idx and .ctl files and copy those to the horelS3.
        # (only create these for .grib2 files)
        create_grb_idx(from_here)
        os.system('rclone --config %s copy %s horelS3:%s' \
                  % (config_file, from_here+'.ctl', to_there))
        os.system('rclone --config %s copy %s horelS3:%s' \
                  % (config_file, from_here+'.idx', to_there))

def copy_to_horelS3_rename(from_here, to_there, new_name):
    """
    Uses rclone-beta release to make a copy and rename the file on the S3 archive.
    Copy the file to the horelS3: archive using rclone-beta
    Input:
        from_here - string of full path and file name you want to copy
        to_there  - string of path on the horelS3 archive
        DATE      - used to generate a new name for the Alaska file that follow
                    the rest of the file names.
    NOTE: There is a difference between 'moveto' and 'copyto'
          'moveto' will replace the file in the destination?
          'copyto' will not replace the file if it exists?
    """
    beta_rclone = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-beta/rclone'

    # Copy the file from_here to_there
    os.system(beta_rclone +' --config %s copyto %s horelS3:%s/%s' \
              % (config_file, from_here, to_there, new_name))

    if from_here[-6:] == '.grib2':
        # Create the .idx and .ctl files and copy those to the horelS3.
        # (only create these for .grib2 files)
        create_grb_idx(from_here)
        os.system(beta_rclone + ' --config %s copyto %s horelS3:%s' \
                  % (config_file, from_here+'.ctl', to_there+'/'+new_name+'.ctl'))
        os.system(beta_rclone + ' --config %s copyto %s horelS3:%s' \
                  % (config_file, from_here+'.idx', to_there+'/'+new_name+'.idx'))


model = model_options[model_type]

while DATE < eDATE:
    """
    Attempt to copy all possible hours, forecast hours, etc. for HRRR from the
    horel-group/archive to the horelS3:HRRR archive.

    This Script utilized multiprocessing for faster moving.
    """

    # Build the current day directory and file to move
    # First, untar the model directory (function returns where files were saved)
    DEST = untar_model_dir(DATE, model)
    DIR = DEST + '%04d%02d%02d/models/%s/' % (DATE.year, DATE.month, DATE.day, model)


    # HRRR has 18 hour forcasts, Alaska has 36 hour forecasts
    if model == 'hrrr_alaska':
        forecasts = np.arange(0, 37)
    else:
        forecasts = np.arange(0, 19)

    # Open file for printing output
    log_path = 'logs/%s_%04d-%02d' % (model, DATE.year, DATE.month)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log = open('%s/%s_%04d-%02d-%02d.txt' % (log_path, model, DATE.year, DATE.month, DATE.day), 'w')
    log.write('Moving %s files\nDate: %s\n' % (model, DATE))
    log.write('Origin: ' + DIR)

    # loop for each type: sfc, prs, buf
    for t in types:
        # Known conditions that don't exist
        if t == 'buf' and (model == 'hrrr_alaska' or model == 'hrrrX'):
            # no bufer files for alaska for experimental HRRR, so don't even check
            continue

        # Build the new S3 directory path name (e.g. HRRR/oper/sfc/20171201)
        DIR_S3 = 'HRRR/%s/%s/%04d%02d%02d' \
                    % (model_S3_names[model_type], t, DATE.year, DATE.month, DATE.day)
        log.write('  \n\nCopy to: horelS3:'+DIR_S3+'\n')
        log.write("========== Checking for "+model + ' ' + t +" files ====================\n")

        # loop for each hour (0,24)
        for h in range(0, 24):
            log.write('Hour %02d:' % (h))

            # loop for each forecast hour, depenent on model type.
            for f in forecasts:
                # Known condition that doesn't exist
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

                # File path and name for hrrr and hrrrx (e.g hrrr.t00.wrfsfcf00.grib2)
                if model == 'hrrr' or model == 'hrrrX':
                    FILE = DIR + '%s.t%02dz.wrf%sf%02d.grib2' % (model, h, t, f)

                # File path and name for hrrr_alaska prs (e.g hrrr_ak_prs_17010203.grib2)
                if model == 'hrrr_alaska' and t == 'prs':
                    if f == 0:
                        # only get the prs field analysis hour
                        FILE = DIR + 'hrrr_ak_%s_%02d%02d%02d%02d.grib2' \
                                    % (t, DATE.year-2000, DATE.month, DATE.day, h)
                    else:
                        # Don't even try to get forecast prs fields
                        continue

                # File patha and name for hrrr_alaska sfc (e.g hrrr_ak_prs_17010203_0012.grib2)
                if model == 'hrrr_alaska' and t == 'sfc':
                    FILE = DIR + 'hrrr_ak_%s_%02d%02d%02d%02d_00%02d.grib2' \
                                % (t, DATE.year-2000, DATE.month, DATE.day, h, f)

                # Bufr files are a special, so do this stuff...
                if t == 'buf':
                    for b in ['kslc', 'kpvu', 'kogd']:
                        # File path and name for bufr soundings stations (e.g. kslc_2017010223.buf)
                        FILE = DIR + '%s_%04d%02d%02d%02d.buf' \
                                    % (b, DATE.year, DATE.month, DATE.day, h)
                        if os.path.isfile(FILE):
                            # If the bufr file exists, then copy to S3
                            copy_to_horelS3(FILE, DIR_S3)
                            log.write('[%s]' % b)
                        else:
                            log.write('[    ]')
                    continue

                # Check if the grib2 file exists. If it does, then copy the file to S3
                if os.path.isfile(FILE):
                    if model == 'hrrr_alaska':
                        # Rename the alaska files to match naming convention
                        rename_AK = 'hrrrAK.t%02dz.wrf%sf%02d.grib2' % (h, t, f)
                        copy_to_horelS3_rename(FILE, DIR_S3, rename_AK)
                    else:
                        copy_to_horelS3(FILE, DIR_S3)
                    log.write('[f%02d]' % (f))
                else:
                    log.write('[   ]')
            log.write('\n')
    log.close()

    # Remove the untared hrrr directory for the current date.
    remove_this = DEST + '%04d%02d%02d' % (DATE.year, DATE.month, DATE.day)
    shutil.rmtree(remove_this)

    DATE += timedelta(days=1)
