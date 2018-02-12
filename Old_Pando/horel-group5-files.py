# Brian Blaylock
# December 13, 2017

"""
List zipped files in the horel-group archvie on horel-group5
"""

import os
from datetime import date
import numpy as np

hg5 = '/uufs/chpc.utah.edu/common/home/horel-group5/archive/'

dirs = os.listdir(hg5)

files = []
for d in dirs:
    try:
        # Some directories have double directories
        dd = os.listdir(hg5+d+'/'+d)
        files += dd
    except:
        dd = os.listdir(hg5+d)
        files += dd

Unique = np.unique(files)

# Pull out files with the .gz extension
gz = []
for i, item in enumerate(Unique):
    if item[-2:] == 'gz':
        gz.append(item)


# Move a mock file to Pando
years = range(2015,2018)
months = range(1,13)
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
MM = ['%02d_%s' % (months[i], MONTHS[i]) for i in range(len(months))]

for g in gz:
    for y in years:
        for m in MM:
            os.system('rclone copy hi.txt horelS3:horel-archive/%s/%s/%s/' % (g.split('.')[0], y, m))