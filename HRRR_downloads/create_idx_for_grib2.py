# Brian Blaylock
# February 22, 2018

"""
Create a .idx file (Still need permissions set from Jeff to create these)
"""

import os
from datetime import datetime, timedelta
import multiprocessing

def create_idx(for_this_file):
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')
    print "--> Created idx file:", for_this_file


sDATE = datetime(2016, 10, 1)
eDATE = datetime(2017, 2, 1)
DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

model = 'hrrr'
fields = ['prs', 'sfc']

DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'

for DATE in DATES:
    print DATE
    for field in fields:
        PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
        files = os.listdir(DIR+PATH)
        files = filter(lambda x: x[-6:]=='.grib2', files)
        map(lambda x: create_idx(DIR+PATH+x), files)
