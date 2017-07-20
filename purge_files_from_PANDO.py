# Brian Blaylock
# July 20, 2017                 Rachel and I are getting Married in 3 Months :)

"""
WARNING: THIS SCRIPT WILL DELETE FILES FROM THE PANDO ARCHIVE. 
         EXECUTE WITH CARE
"""

from datetime import datetime, timedelta
import os

# =============================================================================
# Parameters. Will delete an entire day for the specified fields
# =============================================================================
model_dir = 'alaska'
model_file = 'hrrrAK'
fields = ['prs', 'sfc']
sDATE = datetime(2016, 9, 1)
eDATE = datetime(2016, 12, 1)
# =============================================================================
# =============================================================================


# Create list of dates
DATES = [sDATE + timedelta(days=d) for d in range(0, (eDATE-sDATE).days)]

# Loop through all posible files. Print the file and delete/purge it from Pando
for D in DATES:
    for field in fields:
        FILE = "HRRR/%s/%s/%s/" \
                % (model_dir, field, D.strftime('%Y%m%d'))

        # Print these off before you want to delete them
        print FILE

        # rclone list a file
        os.system('rclone ls horelS3:%s' % (FILE))

        # rclone purge a file
        """
        Are you really ready for this??? Better check one more time
        """
        #os.system('rclone purge horelS3:%s' % (FILE))
