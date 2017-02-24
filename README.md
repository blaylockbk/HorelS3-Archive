[//]: # (You can view this markdown file with the Chrome extention "Markdown Preview Plus")

![MesoWest Logo, why doesn't this work??](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/images/MesoWest/MesoWest_20th_black.png "Powered by MesoWest")

# Using the Horel S3 Archive Buckets  
Brian Blaylock  
_February 22, 2017_

## Introduction
In January 2017, CHPC allocated the Horel Group 30 TB on the S3 (Simple Storage
Service) archive space. This space is used for the Horel archive. Presently, it 
only houses the HRRR archive, but more data will
be moved to S3. 

You can copy/move/get data on cloud servers via `rclone` in your linux terminal
(you can even download rclone for your PC). Someday, you might be able to
explore the directories and files at on the web: 
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
| list bucket contents                        | `rclone ls horelS3:HRRR` | `ls` will list everything in the bucket including all directory's contents |
| list bucket/path contents                   | `rclone ls horelS3:HRRR/oper/sfc/20171201` | currently, no way to sort alpha-numerically |
| list bucket contents                        | `rclone lsl horelS3:HRRR` | `lsl` will list more details than `ls`|
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
| Apr 18, 2015 | Began downloading HRRR sfc/prs/buf analyses HRRRv1 Some days/hours may be missing|
| Jul 27, 2016 | Began downloading HRRR sfc 15 hr forecasts| |
| Aug 23, 2017 | HRRRv2 implemented at NCEP starting with 12z run|
| Aug 24, 2017 | Began downloading HRRR sfc 18 hr forecasts| HRRRv2 runs a few extra hours|
| Summer 2016? | Taylor began downloading HRRR-Alaska prs analyses and sfc 36 hr forecasts| Runs occur every three hours, but isn't always availalbe.|
| Dec 1, 2017  | Began downloading experimental HRRR sfc analyses| HRRRv3: Runs aren't always available |

* #### `oper/` Operational HRRR
  * `sfc/` Surface fields
    * _`YYYYMMDD/`_
      * Analysis and forecast hours (f00-f18) for all hours (00-23).
      * `hrrr.t00.wrfsfcf00.grib2`

  * `prs/` Pressure fields
    * _`YYYYMMDD/`_
      * Analysis hour (f00) only for all hours (00-23).
      * `hrrr.t00.wrfprsf00.grib2`
  * `buf/` Bufr soundings
    * _`YYYYMMDD/`_
      * All hours (00-23). Each file contains analysis and forecast soundings.
      * Only for Salt Lake City (kslc), Ogden (kogd), and Provo (kpvu)
      * `kslc.2017010100.buf`
 
* #### `exp/` Experimental HRRR
  * `sfc/` Surface fields
    * _`YYYYMMDD/`_
      * Analysis hour (f00) for all available hours.
      * `hrrrX.t00.wrfsfcf00.grib2`

* #### `alaska/` HRRR Alaska (Experimental)
  * `sfc/` Surface fields
    * _`YYYYMMDD/`_
      * Analysis and 36 hour forecasts (f00-f36) if available. Runs initialize
      every three hours (0, 3, 6, 9, 12, 15, 18, 21).
      * `hrrrAK.t00.wrfsfcf00.grib2`
  * `prs/` Pressure fields
    * _`YYYYMMDD/`_
      * Analysis hours (f00) for run hours only (0, 3, 6, 9, 12, 15, 18, 21)
      * `hrrrAK.t00.wrfsfcf00.grib2`

More details about the HRRR archive **[here](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html)**.


## Scripts
### `move_HRRR_to_horelS3_multipro.py`

A python script that utilizes multiprocessing to simultaneously execute an rclone 
command that copies HRRR files from the `horel-group/archive/models/hrrr` to
the `horelS3:HRRR` archive buckets. Default is to use 12 processors, but could
bump this up to 24. (Hummm, would that increase the speed?? Or is that I/O like
rush hour traffic at point of the mountain jamming those copper wires??)

For a range of dates (different day on each processor:  
  1. Loops through all data types (sfc, prs, buf), hours of the day, and forecast
  hours.
  2. Checks if files exist in horel-group/archive.
  3. Creates .idx and .ctl files for .grib2 files.
  4. Copys the files to horelS3:HRRR to the appropriate directory
  5. Creates a log of files that were found.

>About the Log file: This script creates a log file for each day located in the
`logs` directory. These files are name by the model type and the date 
(e.g. logs/hrrr_2017-01-01.txt). The file shows a check box for all the 
forecast hours and hours of the day that were found on the horel-group/archive
space. An attempt to move the file was made. A check mark in the log file, 
however, does not garuntee the file was successfully moved to the S3 archive.
Instead, use these logs to review what is available.

 **This script should be run by the meteo19 ldm user.**
When you log into meteo19 as ldm, you must:
* `module load rclone`
* `module load grads` (required to create .idx files)


### `g2ctl.pl`
A pearl script that creates the .idx and GrADS .ctl files for a grib2 file.
You don't have to do anything with this. Just know it's here and that it is 
required to create those grib2 index files.
When I copy the grib2 file to the S3 archive, I create these index files and 
move them to the S3 archive. This script is called by the above python script.


## Gotchas
### Rename files on S3 
You have to use the rclone-beta version if you want to rename files on the S3 archive

### List files in alpha-numeric order
Yep, can't do this at all.