#!/bin/csh

# ----------------------------------------------------------------------------
# Brian Blaylock
# February 6, 2018               SpaceX just launched and landed a Falcon Heavy
#
# CRON tab on meso1, mesohorse user. Runs 4 times a day
# Download the available HRRR files and move to Pando
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/New_Pando/"

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
python ${SCRIPTDIR}/hrrr_download_manager.py

# Email a list of files that are now on S3.
# First send email of status, then retry missing files
python ${SCRIPTDIR}/email_log.py
python ${SCRIPTDIR}/email_log.py retry

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`

rm -f ${SCRIPTDIR}/hrrr.status

exit
