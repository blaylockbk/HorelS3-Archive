**Brian Blaylock**  
**September 12, 2019**

[**Back to Home**](../README.md)

# 🗺 HRRR Downloads

The cron job is run on meso1 by the horse every three hours at 29 minutes after the hour.

    29 0,3,6,9,12,15,18,21 * * * /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/HRRR_downloads/script_download_hrrr.csh

If the script runs when the previous process is still going, it attempts to kill the previous process and restart the current download attempt. This will throw you an email.

---

The main script is `script_download_hrrr.csh`. Note that a few `module load` commands are needed to set things up. The following python scripts are executed:

1. `hrrr_download_manager.py` manages the settings for running the following scripts
    - `download_operational_hrrr.py` Downloads operational HRRR and HRRR-AK files from NOAMDS site.
    - `download_experimental_hrrr.py` Downloads experimental HRRR-X from ESRL FTP site.
1. `email_log.py`: Checks the HRRR files that were downloaded yesterday and emails a report to atmos-mesowest@list.utah.edu. I think it is set up to only send the report once a day. The report uses two different checks: 1) Checks that the .idx files on horel-group7 exist and have the expected number of lines and 2) Checks what files are on Pando and displays the info in a table format. **These emails are the first line of defense for realizing that something is wrong.**
    - `look_for_bad_idx_files.py` is the script that perform the .idx file check.
1. `risk_old_hrrr.py`: To preserve limited space on horel-group7, we delete older HRRR files on horel-group7 with the hope that they will not be lost on Pando. If you get messages that horel-group7 is running low on disk space, then we have to risk more files by removing more from horel-group7. My approach has been to keep everything from the most recent months, and then risk the forecast hours for the sfc files for specified hours. I am keeping all the prs files backed up on horel-group7 at the moment, but that might need to change. Maybe what horel-group7 should be is a "rolling archive" for the most recent 2 years, or something along those lines. **This script doesn't take into account the GOES data. Perhaps older GOES data needs to be removed next.**

# A note on `.idx` files
All grib2 files need to have a `.idx` file so that users can do a range-get for retrieving single variables from the files. These should be created in the download scripts, but if they are not, the `../misc/create_idx_for_grib2.py` can be used to generate these metadata files.

`.idx` files are made with the following command

    wgrib2 fileName.grib2 -t -var -lev -ftime > fileName.grib2.idx

The script `look_for_bad_idx_files.py` can help find .idx files that do not have enough lines in it.