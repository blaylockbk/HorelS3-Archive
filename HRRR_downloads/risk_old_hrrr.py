# Brian Blaylock
# 28 August 2018

# Updated on September 16, 2019
# There are 20 TB of free space on HG7. This should hold you over for awhile.

"""
Pando allocation is at 130 TB, but horel-group7 (HG7), the Pando backup, only
has 60 TB. Hence, we need to remove some files from Pando routinely.
I am willing to risk a few of the forecasts to reduce the amount of files on
horel-group7. These files will still be available on Pando, as long as Pando
does not die again.

!! WARNING !! DO NOT SYNC HG7 TO PANDO AFTER FILES ARE REMOVED ON HG7

I am KEEPING the following surface files (sfc) on HG7:
    hrrr: F06, F12
    hrrrak: F00, F01, F06, F12

I am KEEPING the following pressure files (prs) for hrrr on HG7:
    T00, T03, T06, T09, T12, T15, T18, T21

The risk files will only be removed if they are older than 180 days (6 months)

NOTE: The F00 `sfc` file is risked for the hrrr because that data is contained
      in the `prs` F00 file, which we are keeping every 3rd hour.

NOTE: Other ways to save data on HG7:
    - Risk additional sfc files for specific hours (maybe just keep every
      3rd hour, like we do for the prs files).
    - Maybe risk all hours except every 6th hour?
    - Risk files older than 4 months.
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
    print "--> Please run this the risk_old_hrrr.py script with the mesohorse user on meso1."
    exit()

def risk_sfc(DATES, model, verbose=True, remove=True):
    """
    In each DATE directory, remove the sfc files we want to risk

    Input:
        DATES   - list of python datetime objects
        model   - String of 'hrrr', 'hrrrak', or 'hrrrX'
        verbose - print the command used to remove the files
        remove  - if True, the remove command is executed.
                - if False, the remove command is not executed (use for testing).         
    """

    # List of forecast files to remove
    if model == 'hrrr':
        RISK = ['f00', 'f01', 'f02', 'f03', 'f04', 'f05', 'f07', 'f08', 'f09', 'f10', 'f11', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18']
    if model == 'hrrrak':
        RISK = ['f%02d' % f for f in range(2,6)] + ['f%02d' % f for f in range(7,12)] + ['f%02d' % f for f in range(13,37)]
        

    print "\n    !!! (Pando Risk) REMOVING these files from horel-group7..."
    for D in DATES:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/%s/sfc/%s/' % (model, D.strftime('%Y%m%d'))
        print DIR
        for r in RISK: 
            remove_argument = '*%s.grib2*' % r
            if verbose: print('remove this: %s' % (DIR+remove_argument))
            if remove: os.system('rm %s' % (DIR+remove_argument))


def risk_prs(DATES, model, verbose=True, remove=True):
    """
    Same as above, except for the prs field we are removing the model run hours
    For instance, t00 is hour 00 UTC.
    """
    
    # List of hours to remove.
    RISK = ['t01', 't02', 't04', 't05', 't07', 't08', 't10', 't11', 't13', 't14', 't16', 't17', 't19', 't20', 't22', 't23']  

    print "\n    !!! (Pando Risk) REMOVING these files from horel-group7..."
    for D in DATES:
        DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/%s/prs/%s/' % (model, D.strftime('%Y%m%d'))
        print 'Working on:', DIR
        for r in RISK: 
            remove_argument = '*%sz.wrfprs*.grib2*' % r
            if verbose: print('remove this: %s' % (DIR+remove_argument))
            if remove: os.system('rm %s' % (DIR+remove_argument))



if __name__ == '__main__':

    # Create list of dates we want to risk on the Pando archive and not backup
    # on horel-group7.
    
    # Date of beginning of archive: Uncomment below if you want to delete more
    # than we have already done all the way back to the record start.
    #sDATE = datetime(2016, 7, 15)

    # Remove files older than 180 days (180, 181, and 182 days ago, just to
    # make sure they are getting deleted in case of a download hang-up).
    sDATE = datetime.now()-timedelta(days=182)
    eDATE = datetime.now()-timedelta(days=180)
    
    DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

    risk_sfc(DATES, 'hrrr')
    risk_sfc(DATES, 'hrrrak')

    risk_prs(DATES, 'hrrr')