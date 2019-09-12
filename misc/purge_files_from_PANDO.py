# Brian Blaylock
# July 20, 2017                 Rachel and I are getting Married in 3 Months :)

"""
WARNING: THIS SCRIPT WILL DELETE FILES FROM THE PANDO ARCHIVE. 
         EXECUTE WITH GREAT CARE
"""

from datetime import datetime, timedelta
import os

# =============================================================================
# Parameters. Will delete an entire day for the specified fields
# =============================================================================
model = 'hrrrak'
fields = ['prs', 'sfc']
sDATE = datetime(2016, 9, 1)
eDATE = datetime(2016, 12, 1)
# =============================================================================
# =============================================================================

# Create list of dates
DATES = [sDATE + timedelta(days=d) for d in range(0, (eDATE-sDATE).days)]

# Loop through all possible files. Print the file and delete/purge it from Pando
for D in DATES:
    for field in fields:
        FILE = "%s/%s/%s/" \
                % (model, field, D.strftime('%Y%m%d'))

        # Ask if you want to delete this day
        do_delete = raw_input('Should I delete: %s from Pando? [yes/no]' % FILE)
        if do_delete == 'yes':
            print "Ok, I'm deleting,", FILE
            # rclone list a file
            os.system('rclone purse horelS3:%s' % (FILE))
            print "It is gone forever.\n"
        if do_delete == 'no':
            pass
