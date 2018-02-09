[//]: # (If not on github, you can view this markdown file with the Chrome extention "Markdown Preview Plus")

![MesoWest Logo, why doesn't this work??](MesoWest_20th_black.png "Powered by MesoWest")

# Using the Horel S3 Archive Buckets  
**Author:** Brian Blaylock  
**Date:** February 22, 2017  
_updated September 22, 2017_  
_updated February 6, 2018 after New Pando rebuild_

## Introduction
In January 2017, CHPC allocated the Horel Group 60 TB on the Pando S3 (Simple Storage
Service) archive space. This space is used for the Horel archive. Presently, it 
houses the HRRR archive (> 45 TB), and GOES-16 archive. [Pando failed](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/Pando_archive/Pando_Failure.html) in January 2018, and the entire archive was lost. The archive has been rebuilt and we continued to archive HRRR and GOES data. We are currently working with [The Climate Corporation](https://climate.com/) who have generously offered to help us restore the lost HRRR sfc files. We hope to restore about 75% of what was lost.

[Pando](https://en.wikipedia.org/wiki/Pando_%28tree%29), latin for _I spread_, is named after the vast network of aspen trees in Utah, thought to be the largest and oldest living organism on earth.

You can view and access data objects on Pando via:
- `rclone` in your linux terminal (you can also get rclone for your PC)
- Your browser also allows access to the public files...
  - HRRR
    - URL: [http://pando-rgw01.chpc.utah.edu/hrrr](http://pando-rgw01.chpc.utah.edu/hrrr)
    - Archive FAQ and interactive download page: [http://hrrr.chpc.utah.edu/](http://hrrr.chpc.utah.edu/)
  - GOES16  
    - URL: [http://pando-rgw01.chpc.utah.edu/GOES16](http://pando-rgw01.chpc.utah.edu/GOES16)

**Generic web access to all buckets and objects on Pando:**  
[home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi](home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi)


## Access data via rclone
[rclone](http://rclone.org/) allows you to sync files and directories between
your linux computer and the S3 buckets (and other cloud services).
Before getting started, first review the [CHPC rclone tutorial](https://www.chpc.utah.edu/documentation/software/rclone.php).

### Configuration
1. The easiest way is to load rclone with [modules](https://chpc.utah.edu/documentation/software/modules.php). Load rclone (I do this is in my `.custom.csh` file). Some versions of rclone are different depending on the host's RedHat version.
    
    `module load rclone`
  
2. Set up the config file: **Note: These are the settings used for the mesohorse user**

    Type `rclone config`. You will be asked a series of questions. Use these options:  
              
      1. Select `n` for new remote  
      2. Enter a name. You will reference the S3 archive with this name. I used `horelS3`
      3. Type: Select option `2` for S3  
      4. "Get AWS credentials from runtime": Set to `False`  
      5. Enter the access key: _Ask Brian or John for this, unless you know where to find it_
      6. Enter the secret key: _You'll have to ask for this, too_
      7. Region: leave blank (press `enter` to skip)
      8. Endpoint: Enter `https://pando-rgw01.chpc.utah.edu`
      9. Location: Select option `1` for none

Completing this setup makes a `.rclone.conf` file in your home directory

### Basic Command Examples
The full usage documentation for rclone is found at [rclone.org](https://rclone.org/docs/). The following examples are some of the more useful. These examples can be used if you named the archive source `horelS3` as described in the configuration step above. If you named your source differently when you configured rclone, simply replace the name before the colon.

|      What do you want to do?                |       Command     | Notes  |
|---------------------------------------------|-------------------|--------|
| make a new bucket                           | `rclone mkdir horelS3:hrrr` |
| make a new bucket/path                      | `rclone mkdir horelS3:hrrr/oper/sfc/` | `copy` will make the directory if it doesn't exist, so it isn't necessary to mkdir before copying|
| list top-level buckets                      | `rclone lsd horelS3:` | `lsd` Only lists the directories in the path |
| list buckets in bucket                      | `rclone lsd horelS3:hrrr` |
| list buckets in path                        | `rclone lsd horelS3:hrrr/oper` |
| list bucket contents                        | `rclone ls horelS3:hrrr` | `ls` will list everything in the bucket including all directory's contents, so this particular example isn't very useful |
| list bucket/path contents                   | `rclone ls horelS3:hrrr/oper/sfc/20171201` | currently, no way to sort alpha-numerically, unless you pipe the output to sort. Add the following: `| sort -k 2` |
| list bucket contents                        | `rclone lsl horelS3:hrrr/oper/sfc/20161213` | `lsl` will list more details than `ls`|
| copy file from your computer to S3          | `rclone copy ./file/name/on/linux/system horelS3:path/you/want/to/copy/to/`| You have to use the newest version of rclone to rename files when you copy. With version 1.38 (not installed on the meso boxes), use `copyto` or `moveto` in order to rename files when transferring to Pando|
| copy file from S3 to your current directory  | `rclone copy horelS3:HRRR/oper/sfc/20161201/hrrr.t12z.wrfsfcf16.grib2 .` |
| delete a file or directory on S3 | *I'm not going to tell you how to do this because there is no undo button!!!* |

With rclone version 1.38, you can do a little more like rename a file on S3. This version is not an installed module on the meso boxes because they don't have the updated RedHat software. But you can use **rclone-beta** that is located here: `/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-beta/`

|      What do you want to do?             |       Command     | Notes  |
|------------------------------------------|-------------------|--------|
| move file from computer to S3 and rename | `/path/to/rclone-beta/rclone moveto /this/path/and/file horelS3:HRRR/path/and/new-name` | will overwrite existing file? |
| copy file from computer to S3 and rename | `/path/to/rclone-beta/rclone copyto /this/path/and/file horelS3:HRRR/path/and/new-name` | will not overwrite if file exists?? |


## Access via URL and curl commands
You can view _some_ of the file contents here: 
[http://pando-rgw01.chpc.utah.edu/hrrr](http://pando-rgw01.chpc.utah.edu/hrrr).
The trouble is that it shows everything in the HRRR bucket without letting you
view the files for each specific directory. Also, not every file is listed because the list is limited to 1000 files.

### Download a file:
#### Download a file from a browser URL
[https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2](`https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2`)

#### Download with wget  
    wget https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2

#### Download with cURL   
    curl -O https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2

#### Download with cURL and rename  
    curl -o hrrr20170101_00zf00.grib2 https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2

#### Download a single variable with cURL
GRIB2 files have a useful ability. If you know the byte range of the variable you are interested, you can get just that variable rather than the full file by using cURL. 

Byte ranges for each variable are located on Pando. Just add a `.idx` to the end of the file name you are interested:

    https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2.idx

For example, to get TMP:2 m temperature from a file:

    curl -o 20180101_00zf00_2mTemp.grib2 --range 34884036-36136433 https://pando-rgw01.chpc.utah.edu/hrrr/oper/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2

_NOTE: If you can't view the .idx files from Pando in your browser, and instead prompts a download, then you many need to remove the .idx file from your list of default apps. I had to remove .idx from my Windows registry._

----------

## Pando Archive Contents and URL Structure

### **`horelS3:GOES16/`**
GOES-16 Level 2 data (multiband format) from the [Amazon AWS NOAA archive](https://aws.amazon.com/public-datasets/goes/).
* #### **`ABI-L2-MCMIPC/`** Advanced Baseline Imager, Level 2, multiband format Cloud Moisture products
  * _**`YYYYMMDD/`**_  
     Example File: `OR_ABI-L2-MCMIPC-M3_G16_s20172631727215_e20172631729588_c20172631730098.nc`  
     File description on [Amazon](https://aws.amazon.com/public-datasets/goes/).

### **`horelS3:hrrr/`**
|      Important Dates            |   What happened?  | Notes  |
|---------------------------------|-------------------|--------|
| 2015-Apr-18 | Began downloading HRRR sfc and prs analyses | HRRRv1 Some days/hours may be missing|
| 2015-May-30 | Began downloading HRRR Bufr soundings for KSLC, KODG, and KPVU|
| 2016-Jul-27 | Began downloading HRRR sfc 15 hr forecasts| |
| 2016-Sep-01 | Taylor began downloading HRRR-Alaska prs analyses and sfc 36 hr forecasts| Runs occur every three hours, but becuase it's an experimental model, runs are not always availalbe.|
| 2016-Aug-23 | HRRRv2 implemented at NCEP starting with 12z run|
| 2016-Aug-24 | Began downloading HRRR sfc 18 hr forecasts| HRRRv2 increased forecasts from 15 to 18 hours.|
| 2016-Dec-01 | Began downloading experimental HRRR sfc analyses| HRRRv3: Runs aren't always available becuase this is an experimental model.|
| 2017-Oct-01 | Stopped downloading sub-hourly files| will start again when fire season begins (May 2018)|
| 2018-Jan | **Pando Failed and Rebuilt**| Start the archive again beginning January 1, 2018. Hope to recover past years with data from The Climate Company.|


* #### **`oper/`** Operational HRRR
  * **`sfc/`** Surface fields
    * _**`YYYYMMDD/`**_
      * Analysis and forecast hours (f00-f18) for all hours (00-23).
      * File example: `hrrr.t00.wrfsfcf00.grib2`

  * **`prs/`** Pressure fields
    * **_`YYYYMMDD/`_**
      * Analysis hour (f00) only for all hours (00-23).
      * File example: `hrrr.t00.wrfprsf00.grib2`
  * **`buf/`** Bufr soundings
    * **_`YYYYMMDD/`_**
      * All hours (00-23). Each file contains analysis and forecast soundings.
      * Only for Salt Lake City (kslc), Ogden (kogd), and Provo (kpvu)
      * File example: `kslc_2017010100.buf`
 
* #### **`exp/`** Experimental HRRR
  * **`sfc/`** Surface fields
    * **_`YYYYMMDD/`_**
      * Analysis hour (f00) for all hours, if available.
      * File example: `hrrrX.t00.wrfsfcf00.grib2`

* #### **`alaska/`** HRRR Alaska (Experimental)
  * **`sfc/`** Surface fields
    * **_`YYYYMMDD/`_**
      * Analysis and 36 hour forecasts (f00-f36), if available. Runs initialize
      every three hours at 0z, 3z, 6z, 9z, 12z, 15z, 18z, 21z.
      * File example: `hrrrAK.t00.wrfsfcf00.grib2`
  * **`prs/`** Pressure fields
    * **_`YYYYMMDD/`_**
      * Analysis hours (f00) for run hours, if available
      * File example: `hrrrAK.t00.wrfsfcf00.grib2`

**A visulatizaion of HRRR file available on the S3 archive can be explored on the [HRRR download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html).**

-----

## Scripts and contents of this repository

### `remaining_S3_disk_space.py`
+ A script that reports how much space is left on our Pando allocation, using 
total files from a single day as an estimate. Reports when the archive
will be filled up. Last I checked, I estimate S3 will be full mid-December. 

### **`GOES_downloads`** (directory)
Download scripts for the GOES-16 data from the noaa-goes16 bucket on Amazon S3.

### **`HRRR_downloads`** (directory)
Contents of this directory contain scripts for downloading HRRR data. These are
run by cron at 6:05 PM Mountain Time. These are the most up-to-date scripts.
- **old_dwnld_scirpts**: don't worry about these. They are old
- `HRRR_downloads.csh`: called by CRON at 6:05 on meso1 by the mesohorse user. Does the following:
  - loads modules
  - `download_hrrr_bufr.py`       Downloads bufr files from Penn State and copies to Pando.
  - `downlaod_hrrrAK_multipro.py` Download HRRR from ESRL and copies to Pando.
  - `downlaod_hrrrX_multipro.py`  Download HRRR from ESRL and copies to Pando.
  - `downlaod_hrrr_multipro.py`   Download HRRR from NOMADS and copies to Pando.
- `HRRR_check.csh`: call by CRON at 11:05 PM on meso1 by the mesohorse user.
  - `email_log.py`: sends me an email to confirm the files are now on the Pando archive.

### `rclone-beta` (directory)
Contains the beta version of rclone that allows you to rename files with copyto and moveto

### `s3cmd-1.6.1` (directory)
Contains `s3cmd` which is used to change permissions of files on S3 from private to public, and vice versa. (see below Q&A for usage)

### `s3cmd-2.0.1` (directory)
Contains `s3cmd` which is used to change permissions of files on S3 from private to public, and vice versa. (see below Q&A for usage)

### `temp` (directory)
A place that bufr soundings are temporarily downloaded to. They are deleted
the next time HRRR_download.csh is executed.

---

The following scripts were used to move large amounts of files from the horel-group/archive
to the Pando archive when we first got started.

### `move_HRRR_to_horelS3_multipro.py`
- A python script that utilizes multiprocessing to simultaneously execute an    rclone 
 command that copies HRRR files from the `horel-group/archive/models/hrrr` to
 the `horelS3:HRRR` archive buckets. Default is to use 4 processors, but could
 bump this up to 24. (Hummm, would that increase the speed?? Or is that I/O  like
 rush hour traffic at point of the mountain jamming those copper wires??)
 The idea is to sustain a continuous data transfer, so, it seems using just 
 four processors makes the most sense.  
- **This script should be run by the meso1 mesohorse user.**
 
- When you log into meso1 as the mesohorse user, remember to load modules:
  - `module load rclone`

- For a range of dates (different day on each processor):  
    1. Loops through all data types (sfc, prs, buf), hours of the day, and forecast
  hours.
    2. Checks if files exist in horel-group/archive.
    3. Copys the files to horelS3:HRRR to the appropriate directory


### `move_HRRR_to_horelS3_serial.py`
- Same as above, but run in serial (one date at at time) with a while loop.

### `daily_move_HRRR_to_horelS3_serial.py`
- Same as above, but this script will only move yesterday's HRRR data to the S3
archive.

### `untar_move_HRRR_to_horelS3.py`
- A modified version of the top script with the added function to
untar HRRR files from the compressed horel-group/archive directory.
- **This script must be run on wx4**. Remember to `module load rclone`.
  1. Untars HRRR files into a temporary directory on wx4: `/scratch/local/Brian_untar_HRRR/`.
  2. Moves to S3 (same as above).
  3. Removes the uncompressed files.

- This script doesn't use multiprocessing because we have to untar a bunch of 
files in the scratch space. Since I don't want to fill this all up so fast
we'll only do one day at a time with a while loop.

### `create_idx.py`
- Creates .idx files for each HRRR grib2 file for a range of dates.
These .idx files are stored in horel-group/archive/HRRR where is can be
accessed online here: [https://api.mesowest.utah.edu/archive/HRRR/](https://api.mesowest.utah.edu/archive/HRRR/).


---
---

# Q & A: Answers to other questions you might have...
## How do I rename a file when I copy it to S3?
You have to use the rclone-beta version if you want to rename files on the S3 
archive. Use the `copyto` and `moveto` commands.

rclone-beta is installed here:
`/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/rclone-beta/rclone`

## How do I list files in alpha-numeric order?
rclone sort file names for you, but you can pipe the output to the sort command.
For example:  
`rclone ls horelS3:HRRR/oper/sfc/20170109/ | sort -k 2`  
Where the "k" specifies which field to sort by. The first field is file size and
the second field (2) is the file name.

You can sort direcotry contents like this:  
`rclone lsd horelS3:HRRR/oper/sfc | sort -k 4`

## How do you get the total size of a bucket or directory?
With some creative linux commands...

How big is a bucket, in Terabytes?  
`rclone ls horelS3:HRRR | cut -c 1-10 | awk '{total += $0} END{print "sum(TB)="total/1000000000000}'`

How big is a directory, in Gigabytes?  
`rclone ls horelS3:HRRR/oper/sfc/20161213 | cut -c 1-10 | awk '{total += $0} END{print "sum(GB)="total/1000000000}'`

## How do you make a directory or files public/private?
You have to use `s3cmd` to change the files from public to private. You 
would want to do this for each file added to the S3 archive that you want 
to be downloadable from the download URL.

s3cmd is installed here: `/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1/s3cmd`  

_NOTE: In order to set bucket names that are all lower case to public, I had to modify the configuration file.  In my `.s3cfg` file on the `host_bucket` line, remove the “s” after `$(bucket)`.  Once I did this I can could and make public whatever bucket name I want._

First navigate to `/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1` directory.

#### Make public
A new bucket: `./s3cmd setacl s3://GOES16 --acl-public`  
A single file: `./s3cmd setacl s3://HRRR/oper/sfc/20170101/filename.grib2 --acl-public`  
A directory: `./s3cmd setacl s3://HRRR/oper/sfc/20170101/ --acl-public --recursive`  

#### Make private
A new bucket: `./s3cmd setacl s3://GOES16 --acl-private`  
A single file: `./s3cmd setacl s3://HRRR/oper/sfc/20170101/filename.grib2 --acl-private`  
A directory: `./s3cmd setacl s3://HRRR/oper/sfc/20170101/ --acl-private --recursive`  


## How is `rclone` and `s3cmd` configured?
Configuration files for the mesohorse user:  
`/scratch/local/mesohorse/.s3cfg`  
`/scratch/local/mesohorse/.rclone-conf`

## How much space is left and when will the S3 archive fill up?
My current estimates are that the 30 TB on S3 will fill up around mid-August.
For an update, run the script `remaining_S3_disk_space.py` which produces output like this...
> Horel S3 Usage  
  ==================================  
  Allocation : 30.00 TB  
  Total size : 19.11 TB  
  Remaining  : 10.89 TB  
  ==================================  
  Usage on 2017-03-13  
    oper   sfc   : 54.22 GB  
    oper   prs   : 8.88 GB  
    oper   buf   : 0.01 GB  
    exp    sfc   : 2.78 GB  
    exp    prs   : 0.00 GB  
    exp    buf   : 0.00 GB  
    alaska sfc   : 1.20 GB  
    alaska prs   : 1.66 GB  
    alaska buf   : 0.00 GB  
  Approx. 158 days until full  
  S3 will fill up on August 19, 2017 with present usage.  
  ==================================  

## Where can I find examples on how to download HRRR data?
Check out the scripting tips here: [Scripting Tips](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_script_tips.html)

## How do I configure `rclone` to access the NOAA's GOES-16 archive on Amazon AWS?
Since the NOAA GOES-16 archive is a public and free bucket, it is really easy to access the data via `rclone`.

Configure `rclone`

    rclone config

Name the remote something like `goes16AWS`. Select `2` for Amazon S3 access and press enter to select empty or default values. When asked if it is right, type `y` for yes.

You are now on your way to accessing the Amazon GOES16 archive. To list the buckets in the `noaa-goes16 archive`, type:

    rclone lsd goes16AWS:noaa-goes16 

___
___

###### Send questions to Brian Blaylock (brian.blaylock@utah.edu)
