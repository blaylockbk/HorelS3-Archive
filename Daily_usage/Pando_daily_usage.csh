#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point forecasts
# CRON job on Meso4, every hour
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 04/25/2017  First set into operations
#	bkb: 03/28/2019  Updated for Python 3
#   bkb: 09/24/2019  Set to run on cron with mesohorse
#--------------------------------------------------------------------------------------

limit coredumpsize 0


# Use Brian's python version 3 install of Python to run this script.
# NOTE: This script takes a long time to sum the total disk usage.
/uufs/chpc.utah.edu/common/home/u0553130/anaconda3/bin/python daily_usage.py

# Change permissions to others in the group can edit the files
chmod g+w remaining_space_plot.png
chmod g+w index.html
chmod g+w Pando_Space.csv

# Copy the image and webpage generated to the Pando_archive public_html in Brian's space
cp remaining_space_plot.png /uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/Pando_archive/
cp index.html /uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/Pando_archive/

exit
