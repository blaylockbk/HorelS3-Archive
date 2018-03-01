# Brian Blaylock
# February 22, 2018

"""
rclone : sync a directory on horel-group7 to Pando
s3cmd  : set acl as public for bucket contents
"""

import os
from datetime import datetime, timedelta


sDATE = datetime(2016, 7, 15)
eDATE = datetime(2017, 12, 28)
DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

model = 'hrrr'
fields = ['prs', 'sfc']

DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'
S3 = 'horelS3:'

for DATE in DATES:
    for field in fields:
        PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
        if os.path.isdir(DIR+PATH):
            rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
            s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
            
            print 'Move to Pando: %s sync %s %s' % (rclone, DIR+PATH, S3+PATH)
            os.system('%s sync %s %s' % (rclone, DIR+PATH, S3+PATH))

            print 'Set acl public: %s setacl s3://%s --acl-public --recursive' % (s3cmd, PATH)
            os.system('%s setacl s3://%s --acl-public --recursive' % (s3cmd, PATH))
            
        else:
            print "DOES NOT EXIST:", DIR+PATH
