# Brian Blaylock
# February 22, 2018

"""
Create a .idx file (Still need permissions set from Jeff to create these)
"""

import os
from datetime import datetime, timedelta


sDATE = datetime(2016, 10, 1)
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

            print '%s sync %s %s' % (rclone, DIR+PATH, S3+PATH)
            os.system('%s sync %s %s' % (rclone, DIR+PATH, S3+PATH))
        else:
            print "DOES NOT EXIST:", DIR+PATH
