# Chris Galli
# March 2, 2017

import commands
import re
from StringIO import StringIO

wget = '/usr/bin/wget '
wget_params = ' --connect-timeout=5 --tries=3 --retry-connrefused --waitretry=3 -nc -c '

sfile = 'http://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod/gfs.2017030118/gfs.t18z.pgrb2.0p25.f003'
outfile = 'tmp2m.grib2'

lines = commands.getoutput('wget '+wget_params+' -q -nv -O- ' + sfile + '.idx').split('\n')
var_to_match = ':TMP:2 m above ground:'
 
#grab surface vars
data=''
gcnt=0
for g in lines:
    expr = re.compile(var_to_match)
    if expr.search(g):
        print 'matched a variable', g
        parts = g.split(':')
        rangestart = parts[1]
        parts = lines[gcnt+1].split(':')
        rangeend = int(parts[1])-1
        print 'range:', rangestart, rangeend
        range = str(rangestart) + '-' + str(rangeend)
        gribvar = commands.getoutput('curl -s --range '+range+' '+ sfile)
        data+=gribvar
    gcnt+=1
            
#write out the surface grib file
f=open(outfile, 'wb')
f.write(StringIO(data).read())
f.close()