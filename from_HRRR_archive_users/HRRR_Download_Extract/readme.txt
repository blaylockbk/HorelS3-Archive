Frank Freedman
San Jose State University
November 2017

Main Script

rf_hrrr_download.sh:  Shell script (bourne shell) that downloads a day of HRRR files from Univ. Utah server, and uses ncl scripts to extract chosen variables and archives results in a external netcdf file for a chosen region.

Steps:

1) Download full CONUS HRRR files from server
2) Call ncl_convert2nc.ncl to read full CONUS files and write an intermediate file of particular variables to a netcdf file.
3) Call process_hrrr.ncl to read intermediate files and write variables to a file just for a chosen region (in our case California)

Other files

data_files.txt: The file of html links to a day of HRRR files. rf_hrrr_download.sh invokes a wget command on this file.

process_hrrr.ncl: An ncl script that reads intermediate file and writes to netcdf file for a particular location. 

hrrr.t00z.wrfsfcf00_CA.nc: An example output file. Contains just chosen variables over specific region (California)