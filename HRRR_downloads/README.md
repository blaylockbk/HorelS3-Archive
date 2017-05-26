## HRRR Downloads

Brian Blaylock  
_Febuary 27, 2017_

A collection of download scripts for the MesoWest HRRR archive.
Downloads HRRR output from ESRL or NOMADS and copies to CHPC Pando archive.
These are run daily after 6:00 PM Mountain Time and downloads the "previous UTC
day."

#### Scripts download with multiprocessing or multithreading
* `download_hrrr_multipro.py`
* `download_hrrrX_multipro.py`
* `download_hrrrAK_multipro.py`

`CRON` will run the `HRRR_downloads.csh` at 6:00 PM. This takes about two hours.  
`CRON` then runs `HRRR_check.csh`, which emails a log of files on the Pando archive.

#### Some useful wgrib commands
Reduce a grib2 file to matched variables  
`wgrib2 original.grib2 -match '^(9|14|32|33):' -\grib new.grib2`

Requirments:
* `rclone`
* `s3cmd`