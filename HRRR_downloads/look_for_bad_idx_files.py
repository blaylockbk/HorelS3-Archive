# Brian Blaylock
# February 20, 2018

"""
Look for bad or missing .idx files.

This is a good check because a user needs the .idx file to do a range-get on
the grib2 file. Also, if the .idx file is missing, then the .grib2 file
is likely also missing.

This also checks the number of lines in the .idx file, because if the lines
are less than what is expected, the file might be a partial download.

NOTE: This check is looking at .idx files on horel-group7, not on Pando.
      .idx files on horel-group7 does not guarantee files are on Pando.

F00-F01 forecasts have fewer variables in the output than F02-F18, and thus
have fewer lines in the .idx file. 

NOTE: The amount of lines in the .idx file is subject to change with version 
      changes

This script is used by the ./email_log.py script.
"""

from datetime import datetime, timedelta
import os


# Only checks the hrrr model, because that is the most important.
# Expected lines in the .idx file:
# First number is lines in F00-F01 files
# Second number is lines in F02-F18 files

expected = {'hrrr':{'sfc':[132, 135],
                    'prs':[684, 687]}}


def find_bad_idx(DATES, model='hrrr', hours=range(0,24)):
    """
    For a list of DATES, find if there are any bad or missing .idx files on horel-group7.
    
    Output info as readable text, list of missing files, and list of bad files.
    """

    text = ''
    bad_files = []
    missing_files = []

    # Keep track of the number of bad or missing .idx files
    count_bad = 0

    for field in expected[model].keys():
        if field == 'sfc':
            fxx = range(0,19)
        elif field == 'prs':
            fxx = [0]

        # Create list of all files to check
        FILES = ['hrrr.t%02dz.wrf%sf%02d.grib2.idx' % (h, field, f) for h in hours for f in fxx]

        text += "\nLines | File Path (%s)" % field

        for DATE in DATES:
            DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrr/%s/%s/' % (field, DATE.strftime('%Y%m%d'))
            for FILE in FILES:
                # Does the .idx file exist?
                if not os.path.isfile(DIR+FILE):
                    count_bad += 1
                    text += "DOES NOT EXIST, %s\n" % (DIR+FILE[:-4])
                    missing_files.append(DIR+FILE[:-4])
                    continue
                
                # Checking files by number of lines in .idx files
                lines = sum(1 for line in open(DIR+FILE))

                # What is the file's fxx?
                this_file_fxx = int(FILE[-12:-10])

                # If the .idx file doesn't have the expected lines, tell me how many lines it has...
                if this_file_fxx in [0, 1] and lines < expected[model][field][0]:
                    count_bad += 1
                    text += "Lines: %s/%s, %s\n" % (lines, expected[model][field][0], DIR+FILE[:-4])
                    bad_files.append(DIR+FILE[:-4])
                elif this_file_fxx in range(2,19) and lines < expected[model][field][1]:
                    count_bad += 1
                    text += "Lines: %s/%s, %s\n" % (lines, expected[model][field][1], DIR+FILE[:-4])
                    bad_files.append(DIR+FILE[:-4])
    if count_bad == 0:
        text = '**no bad or missing .idx files in last %s days on horel-group7\n' % (len(DATES))
    
    return text, missing_files, bad_files


if __name__ == '__main__':

    # Check for bad/missing files for last 5 days.
    days = 5
    sDATE = datetime.now()-timedelta(days=days)
    eDATE = datetime.now()
    DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]

    text, missing, bad = find_bad_idx(DATES)
    print(text)
