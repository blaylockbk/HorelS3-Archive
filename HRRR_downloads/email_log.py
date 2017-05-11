    # Brian Blaylock
# March 13, 2017                        Had Sunday dinner at Rachel's yesterday

"""
Check the HRRR files made it to the S3 archive and email a list to myself
"""

import smtplib
import os
from datetime import date, datetime, timedelta

# Variables
if datetime.now().hour < 12:
    # if it before noon (local) then get yesterdays date
    # 1) maybe the download script ran long and it's just after midnight
    # 2) mabye you need to rerun this script in the morning
    DATE = datetime.today() -timedelta(days=1)
else:
    # it's probably after 6 local
    DATE = datetime.today()


model = ['oper', 'exp', 'alaska']
variable = ['sfc', 'prs', 'subh', 'buf']

checked = ''
for m in model:
    for v in variable:
        # Don't check for files that are known to not exist
        if (m == 'exp' or m == 'alaska') and v == 'buf':
            continue
        if m == 'exp' and v == 'prs':
            continue
        if m in ['exp', 'alaska'] and v == 'subh':
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
                    look_for_this = '%s.t%02dz.wrf%sf%02d.grib2' \
                                    % (name, h, v, f)
                    if look_for_this in s3_list:
                        checked += '[f%02d]' % (f)
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
