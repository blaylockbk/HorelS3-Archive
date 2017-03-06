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
from datetime import datetime, timedelta

month = 11

DATE = datetime(2016, month, 1)
eDATE = datetime(2016, month+1, 1)

models = ['oper', 'alaska', 'exp']
types = ['sfc', 'prs']

timer1 = datetime.now()
while DATE < eDATE:
    for m in models:
        for t in types:
            # Create a list of files for the day
            S3_DIR = 'HRRR/%s/%s/%04d%02d%02d/' \
                      % (m, t, DATE.year, DATE.month, DATE.day)
            file_list_name = '%s-%s-%04d%02d%02d.txt' \
                              % (m, t, DATE.year, DATE.month, DATE.day)
            os.system('rclone ls horelS3:%s | cut -c 11- > temp/%s' \
                       % (S3_DIR, file_list_name))
            DATE += timedelta(days=1)

            # Create the directory in the horel-group/archive/HRRR space to
            # match the S3 directory structure.
            HG_DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/' + S3_DIR
            if not os.path.exists(HG_DIR):
                os.makedirs(HG_DIR)

            # For each file in the list (that ends in .grib2), download the file.
            f = open('temp/'+file_list_name)
            for line in f:
                line = line[:-1] # get rid of the /n at the end of each line.
                if line[-6:] == '.grib2':
                    # Download from S3 with rclone
                    dwnld_rename = '%s-%s-%04d%02d%02d.%s' \
                                    % (m, t, DATE.year, DATE.month, DATE.day, line)
                    cmd_copy = 'rclone-beta/rclone copyto horelS3:%s%s temp/%s' \
                                % (S3_DIR, line, dwnld_rename)
                    print cmd_copy
                    os.system(cmd_copy)

                    # Make the idx file and put in horel-group/archive/HRRR
                    idx_name = line+'.idx'
                    cmd_create = 'wgrib2 temp/%s -t -var -lev -ftime > %s' \
                                  % (dwnld_rename, HG_DIR+idx_name)
                    print cmd_create
                    os.system(cmd_create)

            # Remove the list and the downloaded file
            os.system('rm temp/%s' % (file_list_name))
            os.system('rm temp/%s' % (dwnld_rename))
    DATE += timedelta(days=1)

print "Month %s- Time to complete:" % (month), datetime.now()-timer1 
