# Brian Blaylock
# 28 August 2018

"""
Pando allocation is at 130 TB, but horel-group7 (HG7), the Pando backup, only
has 60 TB. Hence, we need to remove some files from Pando. I am willing to risk
a few of the forecasts to reduce the amount of files on horel-group7. These
files will still be available on Pando, as long as Pando stays a live and
doesn't die again.

!! WARNING !! DO NOT SYNC HG7 TO PANDO AFTER FILES ARE REMOVED ON HG7

I am KEEPING the following surface files (sfc):
    F06, F12

I am RISKING the following surface files (sfc):
    F00, F01, F02, F03, F04, F05,
    F07, F08, F09, F10, F11, F13,
    F14, F15, F16, F17, F18

The risk files will only be removed if they are older than 180 days (6 months)

NOTE: The F00 `sfc` file is risked that data is contained in the `prs` F00
      file, which we are keeping.

NOTE: Other ways to save data on HG7:
        - Risk some of the `prs` files. Perhaps start with risking all hours
          EXCEPT 0,3,6,9,12,15,18,21.
        - We could remove some of the Alaska HRRR `prs` and `sfc` files, but
          McCorkle is using that data from Horel-Group7, so check with her what
          she needs first, and find out if she accesses her Alaska files from
          Pando or from HG7.
        - Risk the GOES16 and GOES17 datasets because this is recoverable from
          AWS. I haven't done this yet because I still retrieve this data
          directly from HG7 instead of Pando because of ease. I would have to 
          redo some of my workflow if I remove GOES files from HG7.
"""

from datetime import datetime, timedelta
import os
import getpass
import socket

if getpass.getuser() != 'mesohorse' or socket.gethostname() != 'meso1.chpc.utah.edu':
    print "--> You are %s on %s" % (getpass.getuser(), socket.gethostname())
    print "--> Please run this operational download script with the mesohorse user on meso1."
    exit()

# List of dates from archive begining to 6 months ago. These are the dates we
# want to risk on the Pando archive and not backup on horel-group7.
sDATE = datetime(2016, 7, 15) # Begining of archive...
#sDATE = datetime.now()-timedelta(days=183)
eDATE = datetime.now()-timedelta(days=180)
DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

print sDATE
print eDATE

# In each DATE directory, remove the files we want to risk

RISK = ['f00', 'f01', 'f02', 'f03', 'f04', 'f05', 'f07', 'f08', 'f09', 'f10', 'f11', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18']

print "\n    !!! (Pando Risk) REMOVING these files from horel-group7..."
for D in DATES:
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrr/sfc/%s/' % D.strftime('%Y%m%d')
    print DIR
    for r in RISK: 
        #print os.system('ls %s*%s.grib2*' % (DIR, r))
        print('rm %s*%s.grib2*' % (DIR, r))
        os.system('rm %s*%s.grib2*' % (DIR, r))
