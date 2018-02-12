# Brian Blaylock
# November 17, 2017

"""
Find missing .idx files in the HRRR archive
"""

import os
from datetime import date, timedelta


MODEL = 'hrrr'  # 'hrrr', 'hrrrak', 'hrrrX'
fxx = 0
field = 'sfc'
hours = range(0,24)

sDATE = date(2015, 4, 18)
eDATE = date.today()
days = (eDATE-sDATE).days
DATES = [sDATE + timedelta(days=d) for d in range(days)]

for D in DATES:
    for h in hours:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/%s/%s/%s/' % (MODEL, field, D.strftime('%Y%m%d'))
        FILE = '%s.t%02dz.wrf%sf%02d.grib2' % (MODEL, h, level, fxx)

        if not os.path.exists(DIR+FILE):
            print "FILE DOES NOT EXIST:", DIR+FILE
