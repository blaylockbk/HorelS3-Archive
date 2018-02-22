# Brian Blaylock
# February 20, 2018

"""
Look for bad .idx files
sfc .idx files should have 132 lines if f00-f01 or 135 lines if f02-f18
"""

from datetime import datetime, timedelta
import os


model = 'hrrr'
fields = ['sfc', 'prs']

hours = range(0,24)


for field in fields:
    if field == 'sfc':
        fxx = range(0,19)
    else:
        fxx = [0]

    sDATE = datetime(2017, 12, 28)
    eDATE = datetime.now()

    DATES = [sDATE+timedelta(days=d) for d in range((eDATE-sDATE).days)]

    print "Lines | File Path (%s)" % field

    for DATE in DATES:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrr/%s/%s/' % (field, DATE.strftime('%Y%m%d'))

        for h in hours:
            for f in fxx:
                FILE = 'hrrr.t%02dz.wrf%sf%02d.grib2.idx' % (h, field, f)
                
                if not os.path.isfile(DIR+FILE):
                    print "DOES NOT EXIST", DIR+FILE
                    continue
                
                lines = sum(1 for line in open(DIR+FILE))
                if field == 'sfc':
                    f00_f01 = 132
                    f02_f18 = 135
                if field == 'prs':
                    f00_f01 = 684
                    f02_f18 = 687

                if f in [0, 1] and lines < f00_f01:
                    print lines, DIR+FILE
                elif f in range(2,19) and lines < f02_f18:
                    print lines, DIR+FILE
