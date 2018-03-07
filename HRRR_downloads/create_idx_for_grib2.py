# Brian Blaylock
# March 5, 2018

"""
Create a .idx file (Still need permissions set from Jeff to create these)
"""

import os
from datetime import datetime, timedelta
import multiprocessing

def create_idx(for_this_file):
    if os.path.isfile(for_this_file+'.idx'):
        lines = sum(1 for line in open(for_this_file+'.idx'))
        if for_this_file[-12:-9] == 'sfc':
            f00_f01 = 132
            f02_f18 = 135
        if for_this_file[-12:-9] == 'prs':
            f00_f01 = 684
            f02_f18 = 687
        
        fxx = int(for_this_file[-8:-6])
        if fxx in [0, 1] and lines < f00_f01:
            print lines, for_this_file+'.idx'
            os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')
            print "--> Created idx file:", for_this_file+'.idx'
            print 'NOW WITH ', sum(1 for line in open(for_this_file+'.idx')), 'LINES'
            print ''
        elif fxx in range(2,19) and lines < f02_f18:
            print lines, for_this_file+'.idx'
            os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')
            print "--> Created idx file:", for_this_file+'.idx'
            print 'NOW WITH ', sum(1 for line in open(for_this_file+'.idx')), 'LINES'
            print ''

    else:
        os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')
        print "--> Created idx file:", for_this_file+'.idx'
        print 'WITH ', sum(1 for line in open(for_this_file+'.idx')), 'LINES'
        print ''
        return None


sDATE = datetime(2017, 8, 1)
eDATE = datetime(2017, 9, 1)
DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

model = 'hrrr'
fields = ['prs', 'sfc']

DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/'

#for DATE in DATES:
def idx_date(DATE):
    print DATE
    for field in fields:
        PATH = '%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
        files = os.listdir(DIR+PATH)
        files = filter(lambda x: x[-6:]=='.grib2', files)
        map(lambda x: create_idx(DIR+PATH+x), files)


import multiprocessing
# Multiprocessing :)
num_proc = multiprocessing.cpu_count() # use all processors
num_proc = 1
p = multiprocessing.Pool(num_proc)
result = p.map(idx_date, DATES)
p.close()