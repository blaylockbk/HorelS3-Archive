#!/bin/csh
#
#September 21, 2017                  Tamale Thursday at the Farmers Market!!!
#
# CRON tab on meso1 mesohorse user, run every 15 minutes
# Download most resent GOES 16 data and move to Pando
# ----------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/GOES_downloads"

# Load some modules
module load rclone
module load python/2.7.3          # until meso1 upgrades to centOS 7, then load python/2.7.11

# Download GOES16 data and move to Pando
echo 'hi'
python ${SCRIPTDIR}/download_GOES16.py

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`
exit
