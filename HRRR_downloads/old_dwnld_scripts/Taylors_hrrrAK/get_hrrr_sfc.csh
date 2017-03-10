#!/bin/tcsh
#
#
limit coredumpsize 0

setenv DATA /uufs/chpc.utah.edu/common/home/horel-group/archive
setenv SCRIPTDIR /uufs/chpc.utah.edu/sys/pkg/ldm/oper/models/hrrr_alaska/
 
#running after 0z the next day but still the current day
if ( $1 == "" ) then
set cyz  = `date +%C`
set yrz  = `date +%y`
set monz = `date +%m`
set dayz = `date +%d`
set julz = `date +%j`
else
# note that century is separate from year
set cyz = $1
set yrz = $2
set monz = $3
set dayz = $4
set julz = $5
endif


#set cyz = 20
#set yrz = 17
#set monz = 02
#set dayz = 21
#set julz = 052
#Dont comment out set dates
set dates = "${yrz}${julz}"

echo $cyz $yrz $monz $dayz $julz $dates

cd ${DATA}/$cyz$yrz$monz${dayz}/models
mkdir hrrr_alaska
chmod u+rwx hrrr_alaska
chmod go+r hrrr_alaska
cd hrrr_alaska
 
get sfc files 
ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}00*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}03*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}06*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}09*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}12*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}15*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}18*
quit
EOF

ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrftwo
mget ${dates}21*
quit
EOF


rm -f temp.temp 
ls ${yrz}${julz}* > temp.temp
foreach file ( `cat temp.temp` )
 rm -f mondy.temp
 echo $file
 set yr = ` echo $file | cut -c 1-2 `
 set jul = ` echo $file | cut -c 3-5 `
 set hr = ` echo $file | cut -c 6-7 `
 set fore = ` echo $file | cut -c 8-11 `
 echo $yr $jul $hr $fore
 $SCRIPTDIR/date_from_jday.pl $yr $jul > mondy.temp
 set mon = ` cat mondy.temp | cut -c1-2 `
 set dy = ` cat mondy.temp | cut -c4-5 `
 echo $mon $dy
 if  ( $monz == $mon && $dayz == $dy ) then
	cp $file hrrr_ak_sfc_$yr$mon$dy${hr}_${fore}.grib2
	echo "starting to truncate file $hr"
	/usr/local/bin/wgrib2 $file  -match '^(9|14|32|33|59|64|65|69|74):' -\grib hrrr_ak_sfc_$yr$mon$dy${hr}_${fore}.grib2
 endif 
end
rm -f temp.temp mondy.temp
rm -f ${yrz}${julz}* 


