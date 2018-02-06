# Brian Blaylock
# February 5, 2017

"""
Move HRRR from horel-group to horel-group7

Run this with the mesohorse user on meso2
Change permissions of each file to be group writeable
"""

import os
import shutil
import socket
import getpass
from datetime import datetime, timedelta
import multiprocessing.pool #:)

if getpass.getuser() != 'mesohorse' or socket.gethostname() != 'meso2.chpc.utah.edu':
    print "--> You are %s on %s" % (getpass.getuser(), socket.gethostname())
    print "--> Please run this script with the mesohorse user on meso2."
    exit()

def create_idx(for_this_file):
    """
    If there isn't a NOMADS .idx file, then use this to create a .idx file that
    matches the NOMADS format
    """
    os.system('wgrib2 ' + for_this_file + ' -t -var -lev -ftime > ' + for_this_file+'.idx')
    print "--> Created idx file:"

def work_on_copying_a_date(DATE):
    #MODELS = ['hrrr', 'hrrrX', 'hrrrak']
    MODELS = ['hrrr', 'hrrrX']
    for model in MODELS:
        if model == 'hrrr':
            HG_model = model
            HG_name = model
            fields = ['prs', 'sfc']
            fxx = range(0, 19)
        if model == 'hrrrX':
            HG_model = model
            HG_name = model
            fields = ['sfc']
            fxx = range(0, 1)
        elif model == 'hrrrak':         # Some differences in Alaska file names
            HG_model = 'hrrr_alaska'
            HG_name = 'hrrrAK'
            fields = ['prs', 'sfc']
            fxx = range(0, 37)    
        # Extract the hour
        h = DATE.strftime('%H')

        for field in fields:
            fromDIR = '%s/%s/models/%s/' % (HG, DATE.strftime('%Y%m%d'), HG_model)
            toDIR = '%s/%s/%s/%s/' % (HG7, model, field, DATE.strftime('%Y%m%d'))
            if not os.path.isdir(toDIR):
                # Create the destination directory if it doesn't exits
                os.makedirs(toDIR)
                print "Created:", toDIR
                print ""
            for f in fxx:
                if model in ['hrrr', 'hrrrX']:
                    FILE = '%s.t%sz.wrf%sf%02d.grib2' % (HG_name, h, field, f)
                elif model == 'hrrrak':
                    FILE = 'hrrr_ak_%s_%s%s_%04d.grib2' % (field, DATE.strftime('%y%m%d'), h, f)
                # Name of new file
                newFILE = '%s.t%sz.wrf%sf%02d.grib2' % (model, h, field, f)
                # Copy file
                if os.path.exists(fromDIR+FILE) and not os.path.exists(toDIR+FILE):
                    # shutil.copy2() preseves the file metadata like creation time
                    shutil.copy2(fromDIR+FILE, toDIR+FILE)
                    print "copied:", fromDIR+FILE
                    print "to    :", toDIR+FILE 
                # Create .idx file
                if os.path.exists(toDIR+FILE) and not os.path.exists(toDIR+FILE+'.idx'):
                    create_idx(toDIR+FILE)
    return 1

# Directories to move data from
HG = '/uufs/chpc.utah.edu/common/home/horel-group/archive'
HG7 = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando' 

# Date range to move from
sDATE = datetime(2017, 12, 28)
eDATE = datetime(2018, 2, 1)
DATES = [sDATE+timedelta(hours=D) for D in range(0, (eDATE-sDATE).days*24)]

# Multithreading: Give each thread it's own hour to work on
timer = datetime.now()

def thread(DATE):
    try:
        work_on_copying_a_date(DATE)
    except:
        work_on_copying_a_date(DATE)

p = multiprocessing.pool.ThreadPool(4)
result = p.map(thread, DATES)
p.close()
p.join()

#for D in DATES:
#    work_on_copying_a_date(D)

print datetime.now()-timer
