# Brian Blaylock
# March 10, 2017

import commands
import re
from StringIO import StringIO
from datetime import date, timedelta
import os
import urllib2
import pygrib
import numpy as np

files = []

# === Modify these ============================================================
DATE = date(2017, 1, 1)
eDATE = date(2017, 1, 5)
hour = 0
fxx = 0
model_dir = 'oper'     # ['oper', 'exp', 'alaska']
model_name = 'hrrr'    # ['hrrr', 'hrrrX', 'hrrrAK']
field = 'sfc'          # ['sfc', 'prs']

var_to_match = ':TMP:2 m above ground:'

while DATE < eDATE:
    outfile = '%04d%02d%02d_tmp2m.grib2' % (DATE.year, DATE.month, DATE.day)
    # =============================================================================
    sfile = 'https://api.mesowest.utah.edu/archive/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2.idx' \
            % (model_dir, field, DATE.year, DATE.month, DATE.day, model_name, hour, field, fxx)

    pandofile = 'https://pando-rgw01.chpc.utah.edu/HRRR/%s/%s/%04d%02d%02d/%s.t%02dz.wrf%sf%02d.grib2' \
            % (model_dir, field, DATE.year, DATE.month, DATE.day, model_name, hour, field, fxx)


    idxpage = urllib2.urlopen(sfile)
    lines = idxpage.readlines()


    #grab surface vars
    data=''
    gcnt=0
    for g in lines:
        expr = re.compile(var_to_match)
        if expr.search(g):
            print 'matched a variable', g
            parts = g.split(':')
            rangestart = parts[1]
            parts = lines[gcnt+1].split(':')
            rangeend = int(parts[1])-1
            print 'range:', rangestart, rangeend
            range = str(rangestart) + '-' + str(rangeend)
            gribvar = commands.getoutput('curl -o '+outfile+' --range '+range+' '+ pandofile)
            files.append(outfile)
            data += gribvar
        gcnt += 1
    DATE += timedelta(days=1)

import matplotlib.pyplot as plt
for i in np.arange(0,len(files)):
    grbs = pygrib.open(files[i])
    temp = grbs[1].values
    plt.figure(i)
    plt.pcolormesh(temp, cmap='afmhot_r')

