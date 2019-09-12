# Brian Blaylock
# March 1, 2018                                         # GOES-S launches today

"""
Inventory expected files in Pando on horel-group7
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

    sDATE = datetime(2016, 7, 15)
    eDATE = datetime.now()

    DATES = [sDATE+timedelta(days=d) for d in range((eDATE-sDATE).days)]

    print "Missing %s Files:" % field

    for DATE in DATES:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))

        for h in hours:
            for f in fxx:
                FILE = '%s.t%02dz.wrf%sf%02d.grib2' % (model, h, field, f)
                
                # Check if file exists
                if not os.path.isfile(DIR+FILE):
                    print "DOES NOT EXIST", DIR+FILE
                    continue
                
                # Check if file size is large enough
                size = os.path.getsize(DIR+FILE)
                if size < 100000000:
                    print "INCOMPLETE FILE: %sMB %s" % (size/1000000., DIR+FILE)
                    continue
                
