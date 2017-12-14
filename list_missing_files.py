# Brian Blaylock
# November 17, 2017

"""
Find missing .idx files in the HRRR archive
"""

import os
from datetime import date, timedelta


MODEL = 'hrrr'
fxx = 0
level = 'sfc'

if MODEL == 'hrrr':
    MODEL_dir = 'oper'
elif MODEL == 'hrrrX':
    MODEL_dir = 'exp'
elif MODEL == 'hrrrAK':
    MODEL_dir = 'alaska'

sDATE = date(2015, 4, 18)
eDATE = date.today()
days = (eDATE-sDATE).days
DATES = [sDATE + timedelta(days=d) for d in range(days)]

for D in DATES:
    for h in range(24):
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/HRRR/%s/%s/%s/' % (MODEL_dir, level, D.strftime('%Y%m%d'))
        FILE = '%s.t%02dz.wrf%sf%02d.grib2.idx' % (MODEL, h, level, fxx)

        if not os.path.exists(DIR+FILE):
            print "FILE DOES NOT EXIST:", '%s/%s/%s/' % (MODEL_dir, level, D.strftime('%Y%m%d')), FILE 



