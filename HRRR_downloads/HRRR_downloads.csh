#!/bin/csh

# ----------------------------------------------------------------------------
# Brian Blaylock
# March 10, 2017               Everyone in the group is getting tacos for lunch
# 
# Download the HRRR files for "yesterday"
# Move HRRR Files to horelS3, create .idx, and change S3 directory to public
#
# CRON tab on meso1 mesohorse user, run at 6:10 PM local time
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/HRRR_downloads"

# Load some modules
module load rclone
module load python/2.7.3 # until meso1 upgrades to centOS 7, then load python/2.7.11
module load wgrib2

# Download HRRR to horel-group archive
python ${SCRIPTDIR}/download_hrrr_bufr.py
python ${SCRIPTDIR}/download_hrrrAK_multipro.py
python ${SCRIPTDIR}/download_hrrrX_multipro.py
python ${SCRIPTDIR}/download_hrrr_multipro.py

# Copy from horel-group/archive to Horel S3 archive, create .idx, and change permissions to public
python ${SCRIPTDIR}/copy_hrrr_to_S3.py

# Email the files that are now on S3
python ${SCRIPTDIR}/email_log.py

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`
exit
