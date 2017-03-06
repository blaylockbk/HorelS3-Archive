# Brian Blaylock
# March 2, 2017                                      Thursday is bowling night.

"""
Remove the .ctl and .idx files from the S3 archive. Those are no good.
"""

import os

DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/HRRR/'

# Make a list of files on S3 archvie:
os.system('rclone ls horelS3:HRRR | cut -c 10- > file_list.txt')

# Remove .ctl and .idx from archive
f = open('file_list.txt')

for line in f:
    if line[-5:] == '.ctl\n' or line[-5:] == '.idx\n':
        cmd = 'rclone purge horelS3:HRRR/'+line[1:]
        print cmd
        os.system(cmd)
