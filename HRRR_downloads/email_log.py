# Brian Blaylock
# March 13, 2017                        Had Sunday dinner at Rachel's yesterday

"""
Check the HRRR files made it to the S3 archive and email a list to myself
"""

import smtplib
import os
from datetime import date, datetime, timedelta
from download_hrrr_multipro import download_hrrr_sfc, download_hrrr_prs

# Variables
if datetime.now().hour < 18:
    # If it's before 3:00 PM (local) it's still work day, and I'm probably
    # trying to get yesterdays date still because the download script failed.
    DATE = datetime.today() -timedelta(days=1)
else:
    # it's probably after 6 local
    DATE = datetime.today()


model = ['oper', 'exp', 'alaska']
variable = ['sfc', 'prs', 'subh', 'buf', 'nat']

checked = ''
for m in model:
    for v in variable:
        # Don't check for files that are known to not exist
        if (m == 'exp' or m == 'alaska') and v == 'buf':
            continue
        if m == 'exp' and v == 'prs':
            continue
        if m in ['exp', 'alaska'] and (v == 'subh' or v == 'nat'):
            continue

        # Special forecast and hour ranges for each model type
        if m == 'oper':
            hours = range(0, 24)
            forecasts = range(0, 19)
            name = 'hrrr'
        elif m == 'exp':
            hours = range(0, 24)
            forecasts = range(0, 1)
            name = 'hrrrX'
        elif m == 'alaska':
            hours = range(0, 24, 3)
            forecasts = range(0, 37)
            name = 'hrrrAK'

        # Make a list of the files from the HRRR S3 archive
        s3_list = os.popen('rclone ls horelS3:HRRR/%s/%s/%04d%02d%02d/ | cut -c 11-' \
                            % (m, v, DATE.year, DATE.month, DATE.day)).read().split('\n')

        checked += '\n\nChecking %s %s %s in S3\n---------------------\n' % (m, v, DATE)
        for h in hours:
            if v == 'buf' and m == 'oper':
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
                    if v == 'nat':
                        look_for_this = '%s.t%02dz.wrf%sf%02d.grib2.BRIANHEAD' \
                                    % (name, h, v, f)
                    else:
                        look_for_this = '%s.t%02dz.wrf%sf%02d.grib2' \
                                    % (name, h, v, f)
                    if look_for_this in s3_list:
                        checked += '[f%02d]' % (f)

                    # If the sfc or subh file doesn't exist, try downloading it again
                    elif m == 'oper' and (v == 'sfc' or v == 'subh'):
                        print "Did not find %s %s" % (DATE.strftime('%Y-%m-%d'), look_for_this)
                        download_hrrr_sfc(h, field=v, forecast=[f])
                        # Regenerate the s3_list and check
                        s3_list = os.popen('rclone ls horelS3:HRRR/%s/%s/%04d%02d%02d/ | cut -c 11-' \
                            % (m, v, DATE.year, DATE.month, DATE.day)).read().split('\n')
                        if look_for_this in s3_list:
                            checked += '[*f%02d]' % (f)
                        else:
                            checked += '[    ]'

                    # If the prs file doesn't exist, try downloading it again
                    elif m == 'oper' and v == 'prs' and f == 0:
                        print "Did not find %s %s" % (DATE.strftime('%Y-%m-%d'), look_for_this), h
                        download_hrrr_prs(h, field=v, forecast=[f])
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
receivers = ['blaylockbk@gmail.com']

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
