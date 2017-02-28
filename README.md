[//]: # (You can view this markdown file with the Chrome extention "Markdown Preview Plus")

![MesoWest Logo, why doesn't this work??](MesoWest_20th_black.png "Powered by MesoWest")

# Using the Horel S3 Archive Buckets  
Brian Blaylock  
_February 22, 2017_

## Introduction
In January 2017, CHPC allocated the Horel Group 30 TB on the S3 (Simple Storage
Service) archive space. This space is used for the Horel archive. Presently, it 
only houses the HRRR archive (> 12 TB), but more data will be moved to S3. 

You can copy/move/get data on cloud servers via `rclone` in your linux terminal
(you can even download rclone for your PC). Someday, you might be able to
explore the files and use curl commands to get data from a web URL: 
[http://pando-rgw01.chpc.utah.edu](http://pando-rgw01.chpc.utah.edu).

## rclone
[rclone](http://rclone.org/) allows you to sync files and directories between
your linux computer and the S3 buckets (and other cloud services).
Before getting started, first review the CHPC rclone tutorial 
**[here](https://www.chpc.utah.edu/documentation/software/rclone.php)**.

### Configuration
1. You must have 
[modules](https://chpc.utah.edu/documentation/software/modules.php) 
set up on your CHPC account. Load rclone (I do this is in my `.custom.csh` file):
    
    `module load rclone`

2. Set up the config file: **Note: These are the settings used for the meteo19 ldm user**

    Type `rclone config`. You will be asked a series of questions. Use these options:  
              
      1. Select `n` for new remote.  
      2. Enter a name. You will reference the S3 archive with this name. I used `horelS3`.
      3. Type: Select option `2` for S3.  
      4. Select `false` when asked to "Get AWS credientials from runtime."  
      5. Enter the access key. Ask me or John for this, unless you know where to find it.
      6. Enter the secret key. You'll have to ask for this, too.
      7. Region: Choose "other-v2-signature" (option `10`).  
      8. Endpoint: Enter `https://pando-rgw01.chpc.utah.edu`.
      9. Location: Seclection option `1` for none.
    
### Basic Examples
These examples can be used if you named the archive source `horelS3` (like I did
for the meteo19 ldm user). If you named your source differently when you
configured rclone, simple replace the name before the colon.

|      What do you want to do?                |       Command     | Notes  |
|---------------------------------------------|-------------------|--------|
| make a new bucket                           | `rclone mkdir horelS3:HRRR` |
| make a new bucket/path                      | `rclone mkdir horelS3:HRRR/oper/sfc/` | `copy` will make the directory if it doesn't exist, so it isn't necessary to mkdir before copying|
| list top-level buckets                      | `rclone lsd horelS3:` | `lsd` Only lists the directories |
| list buckets in bucket                      | `rclone lsd horelS3:HRRR` |
| list buckets in path                        | `rclone lsd horelS3:HRRR/oper` |
| list bucket contents                        | `rclone ls horelS3:HRRR` | `ls` will list everything in the bucket including all directory's contents, so this particular example isn't very useful |
| list bucket/path contents                   | `rclone ls horelS3:HRRR/oper/sfc/20171201` | currently, no way to sort alpha-numerically, unless you pipe the output to `sort -k 2` |
| list bucket contents                        | `rclone lsl horelS3:HRRR/oper/sfc/20161213` | `lsl` will list more details than `ls`|
| copy file from your computer to S3          | `rclone copy ./file/name/on/linux/system horelS3:path/you/want/to/copy/to/`| You can't rename the files yet. You'll have to use rclone beta commands `copyto` and `moveto` functions available in rclone-beta.|
| copy file from S3 to your curent directory  | `rclone copy horelS3:HRRR/oper/sfc/20161201/hrrr.t12z.wrfsfcf16.grib2 .` |

You can do a little more, like rename a file on S3, with **rclone-beta**. This version is currently located 
here: `/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-beta/`

|      What do you want to do?             |       Command     | Notes  |
|------------------------------------------|-------------------|--------|
| move file from computer to S3 and rename | `/path/to/rclone-beta/rclone moveto /this/path/and/file horelS3:HRRR/path/and/new-name` | will overwrite existing file? |
| copy file from computer to S3 and rename | `/path/to/rclone-beta/rclone copyto /this/path/and/file horelS3:HRRR/path/and/new-name` | will not overwrite if file exists?? |

## S3 Archive Contents


### `horelS3:HRRR/`
|      Important Dates            |   What happened?  | Notes  |
|---------------------------------|-------------------|--------|
| 2015-Apr-18 | Began downloading HRRR sfc and prs analyses | HRRRv1 Some days/hours may be missing|
| 2015-May-30 | Began downloading HRRR Bufr soundings for KSLC, KODG, and KPVU|
| 2016-Jul-27 | Began downloading HRRR sfc 15 hr forecasts| |
| 2016-Sep-01 | Taylor began downloading HRRR-Alaska prs analyses and sfc 36 hr forecasts| Runs occur every three hours, but becuase it's an experimental model, runs are not always availalbe.|
| 2016-Aug-23 | HRRRv2 implemented at NCEP starting with 12z run|
| 2016-Aug-24 | Began downloading HRRR sfc 18 hr forecasts| HRRRv2 increased forecasts from 15 to 18 hours.|
| 2016-Dec-01 | Began downloading experimental HRRR sfc analyses| HRRRv3: Runs aren't always available becuase this is an experimental model.|

* #### `oper/` Operational HRRR
  * `sfc/` Surface fields
    * _`YYYYMMDD/`_
      * Analysis and forecast hours (f00-f18) for all hours (00-23).
      * File example: `hrrr.t00.wrfsfcf00.grib2`

  * `prs/` Pressure fields
    * _`YYYYMMDD/`_
      * Analysis hour (f00) only for all hours (00-23).
      * File example: `hrrr.t00.wrfprsf00.grib2`
  * `buf/` Bufr soundings
    * _`YYYYMMDD/`_
      * All hours (00-23). Each file contains analysis and forecast soundings.
      * Only for Salt Lake City (kslc), Ogden (kogd), and Provo (kpvu)
      * File example: `kslc_2017010100.buf`
 
* #### `exp/` Experimental HRRR
  * `sfc/` Surface fields
    * _`YYYYMMDD/`_
      * Analysis hour (f00) for all hours, if available.
      * File example: `hrrrX.t00.wrfsfcf00.grib2`

* #### `alaska/` HRRR Alaska (Experimental)
  * `sfc/` Surface fields
    * _`YYYYMMDD/`_
      * Analysis and 36 hour forecasts (f00-f36), if available. Runs initialize
      every three hours at 0z, 3z, 6z, 9z, 12z, 15z, 18z, 21z.
      * File example: `hrrrAK.t00.wrfsfcf00.grib2`
  * `prs/` Pressure fields
    * _`YYYYMMDD/`_
      * Analysis hours (f00) for run hours, if available
      * File example: `hrrrAK.t00.wrfsfcf00.grib2`

More details about the HRRR archive **[here](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html)**.


## Scripts
### `move_HRRR_to_horelS3_multipro.py`
A python script that utilizes multiprocessing to simultaneously execute an rclone 
command that copies HRRR files from the `horel-group/archive/models/hrrr` to
the `horelS3:HRRR` archive buckets. Default is to use 4 processors, but could
bump this up to 24. (Hummm, would that increase the speed?? Or is that I/O like
rush hour traffic at point of the mountain jamming those copper wires??)
The idea is to sustain a continuous data transfer even while one process is creating
the .ctl and .idx files, which takes a second or two. So, it seems using just 
four processors makes the most sense.

For a range of dates (different day on each processor:  
  1. Loops through all data types (sfc, prs, buf), hours of the day, and forecast
  hours.
  2. Checks if files exist in horel-group/archive.
  3. Creates .idx and .ctl files for .grib2 files.
  4. Copys the files to horelS3:HRRR to the appropriate directory
  5. Creates a log of files that were found. Find log files [here](https://github.com/blaylockbk/HorelS3-Archive/tree/master/logs).

>**A note about log files: This script creates a log file for each day located in the
[logs](https://github.com/blaylockbk/HorelS3-Archive/tree/master/logs) 
directory. Use these log files to review what is available. 
Files are organized and named by the model type and the date 
(e.g. `logs/hrrr_2017-01/hrrr_2017-01-01.txt`). The file shows a check box for all the 
forecast hours and hours of the day that were found in the horel-group/archive.
An attempt to move the file to the S3 archive was made. However, a check mark 
in the log file does not garuntee the file was successfully moved to the S3 archive.**

 **This script should be run by the meteo19 ldm user.**
When you log into meteo19 as ldm, you must:
* `module load rclone`
* `module load grads` (required to create .idx files)

### `move_HRRR_to_horelS3_serial.py`
Same as above, but run in serial (one date at at time) with a while loop.

### `daily_move_HRRR_to_horelS3_serial.py`
Same as above, but this script will only move yesterday's HRRR data to the S3
archive. This script is (will be) called by gl1 crontab?

### `untar_move_HRRR_to_horelS3.py`
This is a modified version of the top script with the added function to
untar HRRR files from the compressed archive directory.
**This script must be run on wx4**
  1. Untars HRRR files into a temporary directory on WX4 (`/scratch/local/Brian_untar_HRRR/`).
  2. Moves to S3 (same as above).
  3. Removes the uncompressed files.

This script doesn't use multiprocessing because we have to untar a bunch of 
files in the scratch space. Since I don't want to fill this all up so fast
we'll only do one day at a time with a while loop.

### `g2ctl.pl`
A pearl script that creates the .idx and GrADS .ctl files for a grib2 file.
You don't have to do anything with this. Just know it's here and that it is 
required to create those grib2 index files.
When I copy the grib2 file to the S3 archive, I create these index files and 
move them to the S3 archive. This script is called by the above python scripts.

---
## Answers to other questions you might have...
### How do I rename a file when I copy it to S3?
You have to use the rclone-beta version if you want to rename files on the S3 
archive. Use the `copyto` and `moveto` commands.

### How do I list files in alpha-numeric order?
rclone wont do this for you, but you can pipe the output to the sort command.
For example:

`rclone ls horelS3:HRRR/oper/sfc/20170109/ | sort -k 2`

Where the "k" specifies which field to sort by. The first field is file size and
the second field (2) is the file name.

### How do you get the total size of a bucket or directory?
With some creative linux commands...

How big is a bucket, in Terabytes?  
`rclone ls horelS3:HRRR | cut -c 1-10 | awk '{total += $0} END{print "sum(TB)="total/1000000000000}'`

How big is a directory, in Gigabytes?  
`rclone ls horelS3:HRRR/oper/sfc/20161213 | cut -c 1-10 | awk '{total += $0} END{print "sum(GB)="total/1000000000}'`

____
## To do list:
* Implement a script to add new HRRR files to the S3 archive as soon as 
they are downloaded each day. (This whole download system needs to be more 
robust. I'd like to rewrite the download scripts in 
python becuase the datetime module is so much easier to use than shell
scripting dates.)
* Make file contents available online
* Come up with says to get data from the archive URL via curl comands.
____