DAYS=31
#DAYS=5
for i in $(seq 1 $DAYS)

do

foo=$(printf "%02d" $i)
OLDERDATE="201701$foo" 
echo $OLDERDATE

mkdir $OLDERDATE

sed -i '1c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t00z.wrfsfcf00.grib2' data_files.txt
sed -i '2c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t01z.wrfsfcf00.grib2' data_files.txt
sed -i '3c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t02z.wrfsfcf00.grib2' data_files.txt
sed -i '4c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t03z.wrfsfcf00.grib2' data_files.txt
sed -i '5c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t04z.wrfsfcf00.grib2' data_files.txt
sed -i '6c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t05z.wrfsfcf00.grib2' data_files.txt
sed -i '7c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t06z.wrfsfcf00.grib2' data_files.txt
sed -i '8c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t07z.wrfsfcf00.grib2' data_files.txt
sed -i '9c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t08z.wrfsfcf00.grib2' data_files.txt
sed -i '10c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t09z.wrfsfcf00.grib2' data_files.txt
sed -i '11c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t10z.wrfsfcf00.grib2' data_files.txt
sed -i '12c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t11z.wrfsfcf00.grib2' data_files.txt
sed -i '13c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t12z.wrfsfcf00.grib2' data_files.txt
sed -i '14c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t13z.wrfsfcf00.grib2' data_files.txt
sed -i '15c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t14z.wrfsfcf00.grib2' data_files.txt
sed -i '16c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t15z.wrfsfcf00.grib2' data_files.txt
sed -i '17c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t16z.wrfsfcf00.grib2' data_files.txt
sed -i '18c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t17z.wrfsfcf00.grib2' data_files.txt
sed -i '19c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t18z.wrfsfcf00.grib2' data_files.txt
sed -i '20c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t19z.wrfsfcf00.grib2' data_files.txt
sed -i '21c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t20z.wrfsfcf00.grib2' data_files.txt
sed -i '22c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t21z.wrfsfcf00.grib2' data_files.txt
sed -i '23c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t22z.wrfsfcf00.grib2' data_files.txt
sed -i '24c\''https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/'$OLDERDATE'/hrrr.t23z.wrfsfcf00.grib2' data_files.txt

wget -i data_files.txt
mv hrrr*grib2 $OLDERDATE

for f in /home/freedman/sandbox/HRRR/FILES_UNIVUTAH/$OLDERDATE/hrrr.*f00.grib2
do
    CURHOUR=$(echo $f| cut -d'/' -f 8)
    echo $CURHOUR
    CURPATH=$(echo $f| cut -d'/' -f-7)
    ncl_convert2nc "$CURHOUR" -i "$CURPATH" -v UGRD_P0_L103_GLC0,VGRD_P0_L103_GLC0,TMP_P0_L103_GLC0,SPFH_P0_L103_GLC0,TCDC_P0_L10_GLC0,HPBL_P0_L1_GLC0,SHTFL_P0_L1_GLC0,FRICV_P0_L1_GLC0,gridlat_0,gridlon_0 -L
    NCFILE=$(echo $CURHOUR| cut -d'.' -f-3)
    sed -i '24c\''  filename = "'$NCFILE'"' process_hrrr.ncl
    ncl process_hrrr.ncl
    rm -f "$NCFILE".nc
done

mv hrrr*_CA.nc $OLDERDATE
cd $OLDERDATE
rm hrrr*grib2
cd ..

done




