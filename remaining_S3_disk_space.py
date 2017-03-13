# Brian Blaylock
# March 13, 2017

"""
How much space is there remaining on the S3 Archive?
How many days left until we are filled?
"""

import os
import numpy as np
from datetime import date, timedelta

# Date 
DATE = date.today() - timedelta(days=1)

# Units
TB = 10.**12
GB = 10.**9

# Allocation (30 TB)
allocation = 30 * 10**12

# Get the current byte size
cmd_total_size = "rclone ls horelS3:HRRR | cut -c 1-10"
file_sizes = os.popen(cmd_total_size).read().split(' \n')
file_sizes = np.array(file_sizes[:-1]).astype(int)

total_bytes = np.sum(file_sizes)

print "Allocation: %.2f TB" % (allocation/TB)
print "Total size: %.2f TB" % (total_bytes/TB)
print ""
# Get daily HRRR size for each model
model = ['oper', 'exp', 'alaska']
variables = ['sfc', 'prs', 'buf']

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

sum_day = 0
for m in model:
    for v in variables:
        print "%s %s: %.2f GB" % (m, v, sizes[m][v]/GB)
        sum_day += sizes[m][v]

# Remaining days 
days_remaining = (allocation-total_bytes)/sum_day

# When will we run out of space?
print "S3 will fill up on", date.today() + timedelta(days=days_remaining)
