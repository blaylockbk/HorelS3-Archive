**Brian Blaylock**  
**September 12, 2019**

# HRRR Downloads

The crontab 

## PANDO HRRR Download
crontab run on meso1 by the horse every three hours.

    29 0,3,6,9,12,15,18,21 * * * /uufs/chpc.utah.edu/common/home/horel-group7/Pando_                                                                         Scripts/HRRR_downloads/script_download_hrrr.csh >& /uufs/chpc.utah.edu/common/ho                                                                         me/horel-group7/Pando_Scripts/HRRR_downloads/testtest_123.txt

The main script `script_download_hrrr.csh`. This runs the following...

1. `hrrr_download_manager.py` manages the settings for running the following scripts
    - `download_operational_hrrr.py` Downloads operational HRRR and HRRR-ak files from NOAMDS site.
    - `download_experimental_hrrr.py` Downloads experimental HRRR-X from ESRL FTP site.
1. `email_log.py`: A script that checks what files were downloaded successfully and marks what is on horel-group7. An email with the data is sent to my email. These emails are the first line of defense for realizing that something is wrong.
1. `risk_old_hrrr.py`: To preserve limited space on horel-group7, we delete older HRRR files on horel-group7 with the hope that they will not be lost on Pando. If you get messages that horel-group7 is running low on disk space, then we have to risk more files by removing more from horel-group7. My approach has been to keep everything from the most recent months, and then risk the forecast hours for the sfc files for specified hours. I am keeping all the prs files backed up on horel-group7 at the moment but that might need to change. Maybe what horel-group7 should be is a "rolling archive" for the most recent 2 years, or something along those lines.

# `.idx` files
All grib2 files need to have a `.idx` file so that users can do a range-get for retrieving single variables from the files. These should be created in the download scripts, but if they are not, the `create_idx_for_grib2.py` can be used to generate these metadata files.

`.idx` files are made with the following command

    wgrib2 fileName.grib2 -t -var -lev -ftime > fileName.grib2.idx

The script `look_for_bad_idx_files.py` can help find .idx files that do not have enough lines in it.