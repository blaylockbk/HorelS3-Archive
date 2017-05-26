# Brian Blaylock
# March 3, 2017                            I get to ski Sundance in two days :)

"""
Creates the .idx files for the grib2 data on the S3 archive.
1. Download a grib2 file from the S3 archive into a temporary directory.
2. Create a .idx file and put in the horel-group/archive/HRRR directory
3. Remove the grib2 file from the temporary directory.

Run this on wx1, wx2, wx3, and wx4 to test the S3 archive I/O
"""

import os
from datetime import date, datetime, timedelta
import numpy as np
import stat

DATE = date(2017, 1, 7)
eDATE = date(2017, 1, 8)

base = DATE
days = (eDATE - DATE).days
date_list = np.array([base + timedelta(days=x) for x in range(0, days)])

models = ['oper', 'alaska', 'exp']
types = ['sfc', 'prs']

timer1 = datetime.now()
for m in models:
    for d in date_list:
        for t in types:
            print "working on", m, t, d
            # Create a list of files for the day
            S3_DIR = 'HRRR/%s/%s/%04d%02d%02d/' \
                      % (m, t, d.year, d.month, d.day)
            s3_list = os.popen('rclone ls horelS3:%s | cut -c 11-' \
                            % (S3_DIR)).read().split('\n')

            # Only proceed if s3_list isn't empty
            if s3_list != ['']:

                # Create the directory in the horel-group/archive/HRRR space to
                # match the S3 directory structure.
                HG_DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/' + S3_DIR
                if not os.path.exists(HG_DIR):
                    os.makedirs(HG_DIR)
                    os.chmod(HG_DIR, stat.S_IRWXU | \
                        stat.S_IRGRP | stat.S_IXGRP | \
                        stat.S_IROTH | stat.S_IXOTH)

                # For each file in the list (that ends in .grib2), download the file.
                for f in s3_list:
                    if f[-6:] == '.grib2':
                        # Download from S3 with rclone
                        # (must use copyto becuase we are renameing the file)
                        dwnld_rename = '%s-%s-%04d%02d%02d.%s' \
                                        % (m, t, d.year, d.month, d.day, f)
                        cmd_copy = 'rclone-beta/rclone copyto horelS3:%s%s temp/%s' \
                                    % (S3_DIR, f, dwnld_rename)
                        print cmd_copy
                        os.system(cmd_copy)

                        # Make the idx file and put in horel-group/archive/HRRR
                        idx_name = f+'.idx'
                        cmd_create = 'wgrib2 temp/%s -t -var -lev -ftime > %s' \
                                    % (dwnld_rename, HG_DIR+idx_name)
                        print cmd_create
                        os.system(cmd_create)

                    # Remove the downloaded file
                    os.system('rm temp/%s' % (dwnld_rename))
            else:
                print "does not exist:", m, t, d

print "Month %s- Time to complete:" % (month), datetime.now()-timer1 
