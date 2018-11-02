#!/bin/csh
#
#September 21, 2017                    Tamale Thursday at the Farmers Market!!!
#
# CRON tab on meso1 mesohorse user, runs every 5 minutes
# Downloads most resent GOES 16 data and move to Pando
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/GOES_downloads"

if (-e ${SCRIPTDIR}/goes16.status) then
	#echo "$dateStart PREVIOUS GOES PROCESS ON MESO1 STILL RUNNING" | mail -s "GOES Pando Download ERROR: Attempt to restart" blaylockbk@gmail.com
	#echo "Attempt to kill old processes that fail"
	#pkill -f ${SCRIPTDIR}/download_GOES16.py
	#pkill -f ${SCRIPTDIR}/download_GOES16_GLM.py
	#pkill -f ${SCRIPTDIR}/script_download_GOES16.csh
	#rm -f ${SCRIPTDIR}/goes16.status
	echo "Restart downloads"
endif

touch ${SCRIPTDIR}/goes16.status

# Load some modules
module load rclone
module load python/2.7.3          # until meso1 upgrades to centOS 7, then load python/2.7.11

# Download GOES16 data and move to Pando
python ${SCRIPTDIR}/download_GOES16_GLM.py
python ${SCRIPTDIR}/download_GOES16.py

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`

rm -f ${SCRIPTDIR}/goes16.status

exit
