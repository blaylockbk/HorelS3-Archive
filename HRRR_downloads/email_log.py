# Brian Blaylock
# March 13, 2017

"""
Check the HRRR files made it to the S3 archive and email a list to myself.

NOTE: If files are not on Pando, they might be on horel-group7. Missing files
on Pando might be an indicator that Pando is having some issues.
You should check that you can copy a file to Pando with rclone and see if any 
of the following errors occur.
    1) "certificate has expired or is not yet valid"
    2) "Failed to copy:...multipart failed upload...QuotaExceeded: status code: 403"
In those cases, you will need to contact Sam Liston to see what's up. The other
thing to check is if the NOMADS server is bogged down.
"""

import smtplib
import os
from datetime import datetime, timedelta

# Use the rclone version installed in the Pando_Scripts directory...
rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'

# Specify the hours and forecasts you want to check (Ideally, these should be 
# the same numbers downloaded in hrrr_download_manager.py)
to_check = {'hrrr':{'hours':range(0,24),
                  'fxx':{'sfc':range(0,19),
                         'prs':range(0,1)}},
          'hrrrak':{'hours':range(0,24,3),
                    'fxx':{'sfc':range(0,37),  # 36 hour forecasts for 0, 6, 12, 18 UTC. 18 hour forecasts otherwise
                           'prs':[]}},
          'hrrrX':{'hours':range(0,24),
                   'fxx':{'sfc':range(0,1),
                          'prs':[]}}}


def check_and_email(DATE, models=['hrrr', 'hrrrak', 'hrrrX'], fields=['sfc', 'prs']):
    print "Checking files are on Pando and composing email report."
  
    checked = '(below) Visual check of HRRR files on Pando for %s' % DATE.strftime('%B %d, %Y')

    models_and_fields = [(m, v) for m in models for v in fields]

    return_this = []
    for m, v in models_and_fields:
        # Don't check for files that are known to not exist.
        # For instance, prs fields are not downloaded for hrrrX or hrrrak.
        if v == 'prs' and m in ['hrrrX', 'hrrrak']:
            continue

        # Hour ranges to check for each model type
        hours = to_check[m]['hours']
        forecasts = to_check[m]['fxx'][v]

        # Make a list of the files from the HRRR S3 archive
        s3_list = os.popen('%s ls horelS3:%s/%s/%s/ | cut -c 11-' % (rclone, m, v, DATE.strftime('%Y%m%0d')))
        s3_list = s3_list.read().split('\n')
        return_this += s3_list

        checked += '\n\nModel=%s      Field=%s\n-------------------------------\n' % (m.upper(), v)

        for h in hours:
            checked += 'Hour %02d:' % (h)
            for f in forecasts:
                look_for_this = '%s.t%02dz.wrf%sf%02d.grib2' % (m, h, v, f)
                if look_for_this in s3_list:
                    checked += '[f%02d]' % (f)
                else:
                    checked += '[   ]'
            checked += '\n'

    # Check missing/bad files based on number of lines in .idx files for last 5 days
    from look_for_bad_idx_files import find_bad_idx
    days = 5
    sDATE = datetime.now()-timedelta(days=days)
    eDATE = datetime.now()
    DATES = [sDATE + timedelta(days=d) for d in range((eDATE-sDATE).days)]
    idx_check, missing_list, bad_list = find_bad_idx(DATES)

    # sender = 'atmos-mesowest@lists.utah.edu'
    # receivers = ['blaylockbk@gmail.com', 'atmos-mesowest@lists.utah.edu']

    #sender = 'brian.blaylock@utah.edu'
    #receivers = ['blaylockbk@gmail.com']

    sender = 'atmos-mesowest@lists.utah.edu'
    receivers = ['atmos-mesowest@lists.utah.edu']

    message = 'Subject: Check HRRR Download to Pando -- {}\n\n'.format(DATE.strftime('%b %d %Y'))
    message += "{}\n{}\nFinished check: {} MT".format(idx_check, checked, datetime.now())

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)
        print "Successfully sent email"
    except SMTPException:
        print "Error: unable to send email"

    return return_this

if __name__ == '__main__':
    # The hrrr_download_manager.py script starts downloading "todays" data if
    # the UTC hour is after 0500 UTC. If the current time is between 0600 and 
    # 0900 UTC, then this script will send an email checking yesterday's HRRR
    # downloads. We only want to send this email once a day after the download
    # manager has finished downloading yesterdays HRRR data.
    if datetime.utcnow().hour in [6,7,8]:
        DATE = datetime.utcnow()-timedelta(days=1)
        s3_list = check_and_email(DATE)


    ## Check a specific date...
    #DATE = datetime(2019, 9, 1)  # Check a custom date
    #s3_list = check_and_email(DATE)
