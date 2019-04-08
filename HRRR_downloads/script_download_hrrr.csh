#!/bin/csh

# ----------------------------------------------------------------------------
# Brian Blaylock
# February 6, 2018               SpaceX just launched and landed a Falcon Heavy
#
# CRON tab on meso1, mesohorse user. Runs 8 times a day (every 3 hours)
# Download the available HRRR files and move to Pando
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/HRRR_downloads"

if (-e ${SCRIPTDIR}/hrrr.status) then
	echo "$dateStart PREVIOUS HRRR PROCESS ON MESO1 STILL RUNNING" | mail -s "HRRR Pando Download ERROR: Attempt to restart" blaylockbk@gmail.com
	echo "Attempt to kill old processes that fail"
	pkill -f ${SCRIPTDIR}/hrrr_download_manager.py
	#####pkill -f ${SCRIPTDIR}/script_download_hrrr.csh # Whoops! Don't kill this process too!!!
	rm -f ${SCRIPTDIR}/hrrr.status
	echo "Restart downloads"
endif

touch ${SCRIPTDIR}/hrrr.status

# Load some modules
module load rclone
module load python/2.7.3          # until meso1 upgrades to centOS 7, then load python/2.7.11
module load wgrib2

# Download HRRR to horel-group7 archive and copy to Pando S3 archive
python ${SCRIPTDIR}/hrrr_download_manager.py

# Email a list of files that are now on S3.
# First send email of status, then retry missing files
python ${SCRIPTDIR}/email_log.py

# Remove old HRRR files that we want to risk (two years old)
python ${SCRIPTDIR}/risk_old_hrrr.py

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`

rm -f ${SCRIPTDIR}/hrrr.status

exit
