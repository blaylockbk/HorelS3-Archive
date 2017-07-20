# Brian Blaylock
# June 30, 2017                        Had all you can eat sushi yesterday-Yum!

"""
Check the HRRR files made it to the S3 archive and email a list to myself

!!! HRRR NATIVE SUBREGION !!!
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

# Variables
if datetime.now().hour < 12:
    # If it's before 5:00 PM (local) it's still work day, and I'm probably
    # trying to get yesterdays date still because the download script failed.
    DATE = datetime.today() -timedelta(days=1)
else:
    # it's probably after 3:00 PM
    DATE = datetime.today()


model = ['oper']
variable = ['nat']
sub = 'BRIANHEAD'       # Name of the Subregion (end text of file name)

checked = ''
for m in model:
    for v in variable:
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

        checked += '\n\nChecking %s %s %s in S3\nSubregion:%s\n---------------------\n' % (m, v, DATE, sub)
        for h in hours:
            checked += 'Hour %02d:' % (h)
            for f in forecasts:
                look_for_this = '%s.t%02dz.wrf%sf%02d.grib2.%s' \
                                % (name, h, v, f, sub)

                if look_for_this in s3_list:
                    checked += '[f%02d]' % (f)

                # If the nat file doesn't exist, try downloading it again
                elif retry is True and m == 'oper' and v == 'nat':
                    print "Did not find %s %s" % (DATE.strftime('%Y-%m-%d'), look_for_this), h
                    download_hrrr_subsection(h, field=v, forecast=[f])
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

message = """From: Check HRRR moved to S3 NATIVE <brian.blaylock@utah.edu>
To: HRRR Check <brian.blaylock@utah.edu>
Subject: Check HRRR NATIVE moved to Pando archvie %s

""" % (DATE) + checked + '\n\nFinished:%s' % (datetime.now())

try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, message)
    print "Successfully sent email"
except SMTPException:
    print "Error: unable to send email"
