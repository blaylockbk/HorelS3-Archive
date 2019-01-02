# Brian Blaylock
# February 22, 2018

"""
rclone : sync a directory on horel-group7 to Pando
s3cmd  : set acl as public for bucket contents
"""

import os
from datetime import datetime, timedelta


sDATE = datetime(2018, 12, 26)
eDATE = datetime(2019, 1, 3)
DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

models = ['hrrr', 'hrrrak', 'hrrrX']
fields = ['prs', 'sfc']

DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'
S3 = 'horelS3:'

rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'

def sync_date(DATE):
    for model in models:
        for field in fields:
            PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
            if os.path.isdir(DIR+PATH):            
                print 'Move to Pando: %s sync %s %s' % (rclone, DIR+PATH, S3+PATH)
                os.system('%s sync %s %s' % (rclone, DIR+PATH, S3+PATH))

                print 'Set acl public: %s setacl s3://%s --acl-public --recursive' % (s3cmd, PATH)
                os.system('%s setacl s3://%s --acl-public --recursive' % (s3cmd, PATH))
                
            else:
                print "DOES NOT EXIST:", DIR+PATH


import multiprocessing
# Multiprocessing :)
num_proc = multiprocessing.cpu_count() # use all processors
num_proc = 1
p = multiprocessing.Pool(num_proc)
result = p.map(sync_date, DATES)
p.close()
