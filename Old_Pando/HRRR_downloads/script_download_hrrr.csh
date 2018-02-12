#!/bin/csh

# ----------------------------------------------------------------------------
# Brian Blaylock
# August 3, 2017               Everyone in the group is getting tacos for lunch
#
# CRON tab on meso1 mesohorse user, run at 6:30 PM local time 
# Download the HRRR files for "yesterday" UTC
# Move HRRR Files to horelS3, create .idx, and change S3 directory files to public
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/HRRR_downloads"

if (-e ${SCRIPTDIR}/hrrr.status) then
	# mail -s "HRRR Processing: skipping process cycle" atmos-uunet@lists.utah.edu <<EOF
	# Skipping a HRRR Processing cycle on meso1: $yrz$monz$dayz/$hrz$min (UTC)
# EOF
	echo "PREVIOUS HRRR PROCESS ON MESO1 STILL RUNNING"
	echo "SEE YOU NEXT TIME!"
	exit
endif

touch ${SCRIPTDIR}/hrrr.status

# Load some modules
module load rclone
module load python/2.7.3          # until meso1 upgrades to centOS 7, then load python/2.7.11
module load wgrib2

# Download HRRR to horel-group archive and copy to Pando S3 archive
python ${SCRIPTDIR}/download_hrrr_multipro.py

# Email a list of files that are now on S3.
# First send email of status, then retry missing files
python ${SCRIPTDIR}/email_log.py
python ${SCRIPTDIR}/email_log.py retry

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`

rm -f ${SCRIPTDIR}/hrrr.status

exit
