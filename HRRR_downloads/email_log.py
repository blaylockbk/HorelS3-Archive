# Brian Blaylock
# March 13, 2017                        Had Sunday dinner at Rachel's yesterday

"""
Check the HRRR files made it to the S3 archive and email a list to myself
"""

import sys
import smtplib
import os
from datetime import date, datetime, timedelta
from download_hrrr_multipro import download_hrrr, download_hrrr_subsection

# If comand line argment given to retry, then try to download missing files
try:
    if sys.argv[1] == 'retry':
        retry = True
    else:
        retry = False
except:
    retry = False

# If the current time is before 0600 UTC, finish downloading files from
# yesterday. Else, download files from today.
if datetime.utcnow().hour < 6:
    DATE = datetime.utcnow()-timedelta(days=1)
else:
    DATE = datetime.utcnow()

# DATE = datetime(2017, 1, 1)                                                  # Check a custom date

model = ['hrrr', 'hrrrX', 'hrrrak']
variable = ['sfc', 'prs', 'subh', 'buf']

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
        s3_list = os.popen('rclone ls horelS3:%s/%s/%04d%02d%02d/ | cut -c 11-' \
                            % (m, v, DATE.year, DATE.month, DATE.day)).read().split('\n')

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

                    # If the sfc or subh file doesn't exist, try downloading it again
                    #elif retry is True and m == 'oper' and (v == 'sfc' or v == 'subh'):
                    elif retry is True and m == 'hrrr' and v == 'sfc':
                        print "Did not find %s %s" % (DATE.strftime('%Y-%m-%d'), look_for_this)
                        download_hrrr(h, field=v, forecast=[f])
                        # Regenerate the s3_list and check
                        s3_list = os.popen('rclone ls horelS3:/%s/%s/%04d%02d%02d/ | cut -c 11-' \
                            % (m, v, DATE.year, DATE.month, DATE.day)).read().split('\n')
                        if look_for_this in s3_list:
                            checked += '[*f%02d]' % (f)
                        else:
                            checked += '[    ]'

                    # If the prs file doesn't exist, try downloading it again
                    elif retry is True and m == 'oper' and v == 'prs' and f == 0:
                        print "Did not find %s %s" % (DATE.strftime('%Y-%m-%d'), look_for_this), h
                        download_hrrr(h, field=v, forecast=[f])
                        # Regenerate the s3_list and check
                        s3_list = os.popen('rclone ls horelS3:HRRR/%s/%s/%04d%02d%02d/ | cut -c 11-' \
                            % (m, v, DATE.year, DATE.month, DATE.day)).read().split('\n')
                        if look_for_this in s3_list:
                            checked += '[*f%02d]' % (f)
                        else:
                            checked += '[    ]'

                    else:
                        checked += '[   ]'

                checked += '\n'


# Send the Email
sender = 'brian.blaylock@utah.edu'
receivers = ['blaylockbk@gmail.com','taylor.mccorkle@utah.edu']

message = """From: Check HRRR moved to S3 <brian.blaylock@utah.edu>
To: HRRR Check <brian.blaylock@utah.edu>
Subject: Check HRRR moved to Pando archvie %s

""" % (DATE) + checked + '\n\nFinished:%s' % (datetime.now())

try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, message)
    print "Successfully sent email"
except SMTPException:
    print "Error: unable to send email"
