# Brian Blaylock
# July 21, 2017             # 3 more months until Rachel and I get married :)

"""
If a file is not on Pando, attempt to copy the file to Pando.

Requirements:
    rclone        <- module load rclone
    rclone-beta   <- should be here in this directory
    g2ctl.pl      <- should be here in this directory
    grads         <- module load grads
"""

from datetime import datetime, timedelta
import os
import numpy as np
import stat


# rclone config file
config_file = '/uufs/chpc.utah.edu/sys/pkg/ldm/.rclone.conf' # meteo19 LDM user

# Dictionary of model-specific parameters
version = {'hrrr':{'fxx' : {'sfc': range(0, 19),
                            'prs': range(0, 1)},
                   'hours' : range(0, 24), 
                   'field' : ['sfc', 'prs'],
                   'Pando DIR': 'oper',
                   'Local DIR': 'hrrr',
                   'File Name': 'hrrr'},
           'hrrrX':{'fxx' : {'sfc': range(0, 1)},
                    'hours' : range(0, 24), 
                    'field' : ['sfc'],
                    'Pando DIR': 'exp',
                    'Local DIR': 'hrrrX',
                    'File Name': 'hrrrX'},
           'hrrrAK':{'fxx' : {'sfc': range(0, 37),
                              'prs': range(0, 1)},
                     'hours' : range(0, 24, 3), 
                     'field' : ['sfc', 'prs'],
                     'Pando DIR': 'alaska',
                     'Local DIR': 'hrrr_alaska',
                     'File Name': 'hrrrAK'}}

def copy_to_horelS3_rename(from_here, to_there, new_name):
    """
    Uses rclone-beta release to make a copy and rename the file on the S3 archive.
    Copy the file to the horelS3: archive using rclone-beta
    Input:
        from_here - string of full path and file name you want to copy
        to_there  - string of path on the horelS3 archive
        new_name  - string of the renamed file for Pando

    NOTE: There is a difference between 'moveto' and 'copyto'
          'moveto' will replace the file in the destination?
          'copyto' will not replace the file if it exists?
    """
    beta_rclone = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-beta/rclone'

    # Copy the file from_here to_there
    os.system(beta_rclone +' --config %s copyto %s horelS3:%s%s' \
              % (config_file, from_here, to_there, new_name))

def create_idx(for_this_file, put_here, rename):
    """
    Create a .idx file and move to horel-group/archive/HRRR
    """
    file_name = rename
    idx_dir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/' + put_here
    if not os.path.exists(idx_dir):
        os.makedirs(idx_dir)
    idx_name = idx_dir + file_name + '.idx'
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + idx_name)
    print "created idx file:", idx_name


# =============================================================================
#    Parameters
# =============================================================================

# Date to transfer (yesterday's data)
sDATE = datetime(2017, 8, 14)
eDATE = datetime(2017, 8, 16)

# Select a version you want to move from local to Pando: 'hrrr', 'hrrrX', or 'hrrrAK'
model = version['hrrrX']

# =============================================================================
# =============================================================================

DATELIST = [sDATE+timedelta(days=d) for d in range(0, (eDATE-sDATE).days)]

for DATE in DATELIST:

    for field in model['field']:
        # 1) Build the local directory path:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/%s/models/%s/' \
            % (DATE.strftime('%Y%m%d'), model['Local DIR'])

        # 2) Build the Pando directory path: (e.g. HRRR/oper/sfc/20171201)
        DIR_S3 = 'HRRR/%s/%s/%s/' \
                % (model['Pando DIR'], field, DATE.strftime('%Y%m%d'))
        
        # 3) Get a list of what is currently in Pando
        s3_list = os.popen('rclone ls horelS3:%s | cut -c 11-' \
                            % (DIR_S3)).read().split('\n')

        # 4) Loop over each hour and forecast
        for h in model['hours']:
            for f in model['fxx'][field]:
                
                # 5) Naming convention
                rename = '%s.t%02dz.wrf%sf%02d.grib2' % (model['File Name'], h, field, f)

                # 6) If the file is already on Pando, then there is no need recopy.
                if rename in s3_list:
                    print rename, 'is FOUND on Pando. Moving on.'
                    continue

                # 6) Build the file name we are looking for...            
                # hrrr and hrrrx (e.g hrrr.t00z.wrfsfcf00.grib2)
                if model['File Name'] == 'hrrr' or model['File Name'] == 'hrrrX':
                    FILE = DIR + '%s.t%02dz.wrf%sf%02d.grib2' % (model['File Name'], h, field, f)

                # hrrrAK sfc files (e.g hrrr_ak_prs_17010203_0012.grib2)
                elif model['File Name'] == 'hrrrAK' and field == 'sfc':
                    FILE = DIR + 'hrrr_ak_%s_%s%02d_%04d.grib2' % (field, DATE.strftime('%y%m%d'), h, f)

                # hrrrAK prs files (e.g hrrr_ak_prs_17010203.grib2)
                elif model['File Name'] == 'hrrrAK' and field == 'prs':
                    FILE = DIR + 'hrrr_ak_%s_%s%02d.grib2' % (field, DATE.strftime('%y%m%d'), h)

                else:
                    print '\n! ERROR: Not sure what model you want a file for !\n'
                    continue
                
                # 7) Check if the grib2 file exists. If it does, and it's not on
                #    Pando, then copy the file to Pando.
                if os.path.isfile(FILE) and rename not in s3_list:              
                    copy_to_horelS3_rename(FILE, DIR_S3, rename)
                    create_idx(FILE, DIR_S3, rename)
                    print 'copied to Pando: %s as %s\n' % (FILE, DIR_S3+rename)
                elif os.path.isfile(FILE) is False:
                    print 'NOT FOUND:', FILE
                    continue

        # 8) Change permissions of S3 directory to public
        s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-1.6.1/s3cmd'
        os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % DIR_S3)
