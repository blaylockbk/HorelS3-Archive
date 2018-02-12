#!/bin/csh

# ----------------------------------------------------------------------------
# Brian Blaylock
# March 23, 2017                         A new Surface Pro was announced today.
#
# CRON tab on meso1 mesohorse user, run at 11:30 PM local time 
# Check that the HRRR files were copied to S3
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/HRRR_downloads"

# Load some modules
module load rclone
module load python/2.7.3          # until meso1 upgrades to centOS 7, then load python/2.7.11
module load wgrib2

# Email a list of files that are now on S3
python ${SCRIPTDIR}/email_log.py

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`
exit
