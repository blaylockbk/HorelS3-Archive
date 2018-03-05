# Brian Blaylock
# February 22, 2018

"""
rclone : sync a directory on horel-group7 to Pando
s3cmd  : set acl as public for bucket contents
"""

import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

sDATE = datetime(2016, 7, 15)
eDATE = datetime.now()
DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

model = 'hrrr'
field = 'sfc'

DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'

def num_files(DATE):
    PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
    try:
        num = len(os.listdir(DIR+PATH))
    except:
        num = 0
    return num

files_date = map(num_files, DATES)

plt.figure(figsize=[16,6])
plt.bar(DATES, files_date, color='k')
plt.xlim(DATES[0], DATES[-1])
plt.ylabel("Number of Files")
plt.suptitle('%s%s/%s' % (DIR, model, field))
plt.title('Total Files: '+'{:0,.0f}'.format(np.sum(files_date)))
plt.grid()
plt.show()
