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
#set dayz = 14
#set julz = 045
#Dont comment out set dates
set dates = "${yrz}${julz}"

echo $cyz $yrz $monz $dayz $julz $dates
 
cd ${DATA}/$cyz$yrz$monz${dayz}/models
mkdir hrrr_alaska
chmod u+rwx hrrr_alaska
chmod go+r hrrr_alaska
cd hrrr_alaska





# pressure fields
ftp gsdftp.fsl.noaa.gov<<EOF
binary
prompt
cd hrrr_ak/alaska/wrfprs
mget ${yrz}${julz}*0000
quit
EOF

rm -f temp.temp
ls *0000 > temp.temp
foreach file ( `cat temp.temp` )
 rm -f mondy.temp
 echo $file
 set yr = ` echo $file | cut -c 1-2 `
 set jul = ` echo $file | cut -c 3-5 `
 set hr = ` echo $file | cut -c 6-7 `
 echo $yr $jul $hr
 $SCRIPTDIR/date_from_jday.pl $yr $jul > mondy.temp
 set mon = ` cat mondy.temp | cut -c1-2 `
 set dy = ` cat mondy.temp | cut -c4-5 `
 echo $mon $dy
 if  ( $monz == $mon && $dayz == $dy ) then
  cp $file hrrr_ak_prs_$yr$mon$dy${hr}.grib2
 endif
end
rm -f temp.temp mondy.temp
rm -f *0000
