# Brian Blaylock
# March 13, 2017

"""
Answers these thought provoking questions...
How much space is there remaining on the S3 Archive?
How many days left until the S3 archive is filled?
(Uses files from a single day as an estimate of how much space is used)
"""

import os
from datetime import date, timedelta
import numpy as np

# ------ Stuff you may want to change -----------------------------------------
# Date (file sizes for this date are used to estimate a daily usage)
DATE = date.today() - timedelta(days=1)

# Allocation (30 TB initially issued January 2017, added 30 TB June 2017)
allocation = (30+30) * 10**12
# -----------------------------------------------------------------------------

# Units
TB = 10.**12
GB = 10.**9
MB = 10.**6

# Get the current byte size (this takes awhile)
print "Getting total S3 size (this takes awhile)"
print "using %s as an estimate of daily usage" % (DATE)


cmd_total_size = "rclone ls horelS3:GOES16 | cut -c 1-10"
file_sizes = os.popen(cmd_total_size).read().split(' \n')
file_sizes = np.array(file_sizes[:-1]).astype(int)
GOES16_total_bytes = np.sum(file_sizes)

cmd_total_size = "rclone ls horelS3:HRRR | cut -c 1-10"
file_sizes = os.popen(cmd_total_size).read().split(' \n')
file_sizes = np.array(file_sizes[:-1]).astype(int)
HRRR_total_bytes = np.sum(file_sizes)

total_bytes = GOES16_total_bytes+HRRR_total_bytes

# Get daily HRRR size for each model
model = ['oper', 'exp', 'alaska']
variables = ['sfc', 'prs', 'buf', 'subh']

sizes = {}

for m in model:
    sizes[m] = {}
    for v in variables:
        sizes[m][v] = {}
        day_size = 0
        cmd_day = "rclone ls horelS3:HRRR/%s/%s/%04d%02d%02d/ | cut -c 1-10" \
                   % (m, v, DATE.year, DATE.month, DATE.day)
        day_size = os.popen(cmd_day).read().split(' \n')
        day_size = np.sum(np.array(day_size[:-1]).astype(int))
        sizes[m][v] = day_size

cmd_goes_day = cmd_day = "rclone ls horelS3:GOES16/ABI-L2-MCMIPC/%s/ | cut -c 1-10" \
                   % (DATE.strftime('%Y%m%d'))
goes_day_size = os.popen(cmd_goes_day).read().split(' \n')
goes_day_size = np.sum(np.array(goes_day_size[:-1]).astype(int))

print ""
print "  Horel Pando Usage"
print "  =================================="
print "  Allocation : %.2f TB" % (allocation/TB)
print "  Total size : %.2f TB" % (total_bytes/TB)
print "  Remaining  : %.2f TB" % (allocation/TB - total_bytes/TB)
print "  =================================="
print ""
print "GOES16: %.3fTB (%.2f%% of allocation)" % (GOES16_total_bytes/GB, GOES16_total_bytes/float(allocation)*100)
print "HRRR  : %.3fTB (%.2f%% of allocation)" % (HRRR_total_bytes/TB, HRRR_total_bytes/float(allocation)*100)
print ""
print "  =================================="
print "  Usage on %s" % DATE
sum_day = 0
for m in model:
    for v in variables:
        print "    %-6s %-6s: %0.2f GB" % (m, v, sizes[m][v]/GB)
        sum_day += sizes[m][v]

print ""
print "    GOES16       : %0.2f GB" % (goes_day_size/GB)
print ""

# Days remaining before S3 is full
days_remaining = (allocation-total_bytes)/sum_day

# When will we run out of space?
print ""
print "  Approx. %s days until full" % (days_remaining)
print "  Pando will fill up on %s with present usage" % (date.today() + timedelta(days=days_remaining)).strftime('%B %d, %Y')
print "  =================================="
