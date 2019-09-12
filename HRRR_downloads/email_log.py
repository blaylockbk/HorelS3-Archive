# Brian Blaylock
# March 13, 2017

"""
Check the HRRR files made it to the S3 archive and email a list to myself
"""

import sys
import smtplib
import os
from datetime import date, datetime, timedelta
import subprocess

print "Checking files were downloaded and composing email"

# If the current time is before 0600 UTC, finish downloading files from
# yesterday. Else, download files from today.
if datetime.utcnow().hour < 3:
    DATE = datetime.utcnow()-timedelta(days=1)
else:
    DATE = datetime.utcnow()

# DATE = datetime(2017, 1, 1)                                                  # Check a custom date

model = ['hrrr', 'hrrrX', 'hrrrak']
variable = ['sfc', 'prs']

rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'

checked = ''
for m in model:
    for v in variable:
        # Don't check for files that are known to not exist
        if (m == 'hrrrX' or m == 'hrrrak') and v == 'buf':
            continue
        if m == 'hrrrX' and v == 'prs':
            continue
        if m in ['hrrrX', 'hrrrak'] and (v == 'subh' or v == 'nat'):
            continue

        # Special forecast and hour ranges for each model type
        if m == 'hrrr':
            hours = range(0, 24)
            forecasts = range(0, 19)
            name = 'hrrr'
        elif m == 'hrrrX':
            hours = range(0, 24)
            forecasts = range(0, 1)
            name = 'hrrrX'
        elif m == 'hrrrak':
            hours = range(0, 24, 3)
            forecasts = range(0, 37)
            name = 'hrrrak'

        # Make a list of the files from the HRRR S3 archive
        s3_list = os.popen('%s ls horelS3:%s/%s/%04d%02d%02d/ | cut -c 11-' \
                            % (rclone, m, v, DATE.year, DATE.month, DATE.day)).read().split('\n')

        checked += '\n\nChecking %s %s %s in S3\n---------------------\n' % (m, v, DATE)
        for h in hours:
            if v == 'buf' and m == 'hrrr':
                checked += 'Hour %02d:' % (h)
                for s in ['kslc', 'kogd', 'kpvu']:
                    look_for_this = '%s_%04d%02d%02d%02d.buf' % (s, DATE.year, DATE.month, DATE.day, h)
                    if look_for_this in s3_list:
                        checked += '[%s]' % (s)
                    else:
                        checked += '[    ]'
                checked += '\n'
            else:
                checked += 'Hour %02d:' % (h)
                for f in forecasts:
                    look_for_this = '%s.t%02dz.wrf%sf%02d.grib2' \
                                    % (name, h, v, f)
                    if look_for_this in s3_list:
                        checked += '[f%02d]' % (f)
                    else:
                        checked += '[   ]'

                checked += '\n'

# Check missing files based on correct .idx line number
missing = subprocess.check_output('python /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/HRRR_downloads/look_for_bad_idx_files.py', shell=True)

# Send the Email
sender = 'atmos-mesowest@lists.utah.edu'
receivers = ['blaylockbk@gmail.com', 'atmos-mesowest@lists.utah.edu']

message = """From: Check HRRR moved to S3 <atmos-mesowest@lists.utah.edu>
To: HRRR Check <atmos-mesowest@lists.utah.edu>
Subject: Check HRRR moved to Pando archvie %s

""" % (DATE) +'\nMissing in HRRR:\n'+missing +'\n\nChecked'+ checked + '\n\nFinished:%s' % (datetime.now()) 

try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, message)
    print "Successfully sent email"
except SMTPException:
    print "Error: unable to send email"
