# Brian Blaylock
# March 5, 2018

"""
Create a .idx file from a .grib2 file.

This is handy if you ever had to manually download some data that was skipped
or the .idx files were not created for whatever reason.
"""

import os
from datetime import datetime, timedelta
import multiprocessing


# Expected lines in the .idx file:
#   First number is lines in F00-F01 files
#   Second number is lines in F02-F18 files
expected = {'hrrr':{'sfc':[132, 135],
                    'prs':[684, 687]}}

def wgrib2_idx(for_this_file):
    """wgrib2 command to make the .idx file"""
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')

def create_idx(for_this_file):
    """
    Given the path of a grib2 file, create a .idx file.
    If there is currently a .idx file, check if it has the expected lines.
    If not, then remake the .idx file.
    """
    model = 'hrrr'
    if os.path.isfile(for_this_file+'.idx'):
        lines = sum(1 for line in open(for_this_file+'.idx'))
        fxx = int(for_this_file[-8:-6])
        field = for_this_file[-12:-9]  # 'sfc' or 'prs'
        if fxx in [0, 1] and lines < expected[model][field][0]:
            print lines, for_this_file+'.idx'
            wgrib2_idx(for_this_file)
            print "--> Created idx file:", for_this_file+'.idx'
            print 'NOW WITH ', sum(1 for line in open(for_this_file+'.idx')), 'LINES'
            print ''
        elif fxx in range(2,19) and lines < expected[model][field][1]:
            print lines, for_this_file+'.idx'
            wgrib2_idx(for_this_file)
            print "--> Created idx file:", for_this_file+'.idx'
            print 'NOW WITH ', sum(1 for line in open(for_this_file+'.idx')), 'LINES'
            print ''
    else:
        wgrib2_idx(for_this_file)
        print "--> Created idx file:", for_this_file+'.idx'
        print 'WITH ', sum(1 for line in open(for_this_file+'.idx')), 'LINES'
        print ''
        return None

def make_idx_for_date(DATE):
    """Create .idx files for all .grib2 in the directory for the given date."""
    print DATE
    model = 'hrrr'
    fields = ['prs', 'sfc']
    for field in fields:
        PATH = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/%s/%s/%s/' % (model, field, DATE.strftime('%Y%m%d'))
        files = os.listdir(PATH)
        files = filter(lambda x: x[-6:]=='.grib2', files)
        map(lambda x: create_idx(PATH+x), files)

if __name__ == '__main__':
    sDATE = datetime(2017, 8, 1)
    eDATE = datetime(2017, 9, 1)
    DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

    # Use multiprocessing :)    
    num_proc = multiprocessing.cpu_count()-2
    p = multiprocessing.Pool(num_proc)
    result = p.map(make_idx_for_date, DATES)
    p.close()
