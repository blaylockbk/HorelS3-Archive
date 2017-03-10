#!/bin/csh
#
#
limit coredumpsize 0
#
setenv DATA /uufs/chpc.utah.edu/common/home/horel-group/archive
setenv PROC $DATA/proc
setenv SCRIPTDIR /uufs/chpc.utah.edu/sys/pkg/ldm/oper/models/hrrr_so3s
 
#running after 0z the next day but still the current day
if ( $1 == "" ) then
set cyz  = `date +%C`
set yrz  = `date +%y`
set monz = `date +%m`
set dayz = `date +%d`

else
# note that century is separate from year
set cyz = $1
set yrz = $2
set monz = $3
set dayz = $4
endif

echo $cyz $yrz $monz $dayz
 
cd ${DATA}/$cyz$yrz$monz${dayz}/models
mkdir hrrr
chmod u+rwx hrrr
chmod go+r hrrr
cd hrrr
/usr/local/bin/python ${SCRIPTDIR}/hrrr_bufr.py

foreach hr ( 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 )
#mkdir bufrsnd.t${hr}z
#chmod ugo+rwx bufrsnd.t${hr}z

# Old (before August 23 2016)
#set dirb = www.nomads.ncep.noaa.gov/pub/data/nccf/nonoperational/com/hrrr/prod/hrrr.$cyz$yrz$monz${dayz}/bufrsnd.t${hr}z/
#set dir = www.nomads.ncep.noaa.gov/pub/data/nccf/nonoperational/com/hrrr/prod/hrrr.$cyz$yrz$monz${dayz}/

# New (starting August 23, 2016)
set dirb = www.nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.$cyz$yrz$monz${dayz}/bufrsnd.t${hr}z/
set dir = www.nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/hrrr.$cyz$yrz$monz${dayz}/

/usr/bin/wget ${dirb}/bufr.725720.$cyz$yrz$monz$dayz$hr
/usr/bin/wget ${dirb}/bufr.725724.$cyz$yrz$monz$dayz$hr
/usr/bin/wget ${dirb}/bufr.725750.$cyz$yrz$monz$dayz$hr
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf00.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfprsf00.grib2
#get forecasts for surface fields
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf01.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf02.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf03.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf04.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf05.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf06.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf07.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf08.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf09.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf10.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf11.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf12.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf13.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf14.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf15.grib2
#after August 23, 2016 HRRRv2 provides 18hr forecasts
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf16.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf17.grib2
/usr/bin/wget ${dir}/hrrr.t${hr}z.wrfsfcf18.grib2



end
chmod u+rwx *
chmod go+r *
exit
