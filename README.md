[//]: # (If not on github, you can view this markdown file with the Chrome extension "Markdown Preview Plus")

![Pando Logo](./images/PANDO_logo.png) 
![MesoWest Logo, why doesn't this work??](./images/MesoWest_20th_black.png "Powered by MesoWest") 


# Using the Horel S3 Archive Buckets on Pando  
**Author:** Brian Blaylock  
**Date:** February 22, 2017  
_updated September 22, 2017_  
_updated February 6, 2018: New Pando rebuild_  
_updated May 3, 2019: added GOES17 and GLM data_  

## References

> ### 📄 Cloud archiving and data mining of High-Resolution Rapid Refresh forecast model output.
>> Blaylock, B. K., J. D. Horel, S. T. Liston, 2017: Cloud archiving and data mining of High-Resolution Rapid Refresh forecast model output. _Computers and Geosciences_. **109**, 43-50. https://doi.org/10.1016/j.cageo.2017.08.005.   (PDF available in this repository.)

> ### 📄 Archive Solutions at the Center for High Performance Computing 
>> Sam Liston: https://www.chpc.utah.edu/documentation/white_papers/ArchiveSolutionattheCenterforHighPerformanceComputing.pdf

> ### 📄 Efficient Storage and Data Mining of Atmospheric Model Output Using the CHPC Pando Archive
>> Brian Blaylock and John Horel: https://www.chpc.utah.edu/news/newsletters/CHPC%20Newsletter%20-%20Spring%202017.pdf

## Introduction
Pando is an object-storage system at the University of Utah, similar to Amazon Web Services S3. [Pando](https://en.wikipedia.org/wiki/Pando_%28tree%29), latin for _I spread_, is named after the vast network of aspen trees in Utah, thought to be the largest and oldest living organism on earth; a fitting name for an archive system.

In January 2017, CHPC allocated the Horel Group 60 TB on the Pando S3 (Simple Storage
Service) archive space and an additional 70 TB in August 2018 for a **total of 130 TB**. This space is used primarily for the Horel Group archive of High-Resolution Rapid Refresh (HRRR) model output and GOES-16/17 ABI and GLM data at the University of Utah. Presently, it houses the HRRR archive (> 70 TB), and GOES-16/17 archive (> 13 TB).

 [Pando failed](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/Pando_archive/Pando_Failure.html) in January 2018, and the entire archive was lost. The archive was rebuilt, old HRRR files were restored, and we continued to archive HRRR and GOES data. We thank [The Climate Corporation](https://climate.com/) for supporting this service through the contribution of their NOAA HRRR archive prior to 2018. Because of them, we restored about 75% of what was lost.

You can view and access data objects on Pando a number of ways:
- `rclone` in your linux terminal (you can also get rclone for your PC)
- Your browser also allows access to the public files...
  - HRRR
    - S3 Bucket URL: [http://pando-rgw01.chpc.utah.edu/hrrr](http://pando-rgw01.chpc.utah.edu/hrrr)
    - [Interactive Download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_download.cgi)
    - [Alternative Download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=hrrr)
  - GOES16  
    - S3 Bucket URL: [http://pando-rgw01.chpc.utah.edu/GOES16](http://pando-rgw01.chpc.utah.edu/GOES16)
    - [Interactive Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi)
    - [Alternative Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=GOES16)
  - GOES17  
    - S3 Bucket URL: [http://pando-rgw01.chpc.utah.edu/GOES17](http://pando-rgw01.chpc.utah.edu/GOES17)
    - [Alternative Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=GOES16)

> **For generic access to all buckets and objects on Pando via a web browser:**  
[http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi)


## Access data via `rclone`
`rclone` (http://rclone.org/) allows you to sync files and directories between
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
| copy file from your computer to S3          | `rclone copy ./file/name/on/linux/system horelS3:path/you/want/to/copy/to/`| You have to use the newest version of rclone to rename files when you copy. With version 1.39 (not installed on the meso boxes), use `copyto` or `moveto` in order to rename files when transferring to Pando|
| copy file from S3 to your current directory  | `rclone copy horelS3:HRRR/oper/sfc/20161201/hrrr.t12z.wrfsfcf16.grib2 .` |
| delete a file or directory on S3 | *I'm not going to tell you how to do this because there is no undo button!!!* |

With rclone version 1.39, you can do a little more like rename a file on S3. This version is not an installed module on the meso boxes because they don't have the updated RedHat software. But you can use **rclone-v1.39** that is located here: `/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone`

|      What do you want to do?             |       Command     | Notes  |
|------------------------------------------|-------------------|--------|
| move file from computer to S3 and rename | `./rclone-v1.39/rclone moveto /this/path/and/file horelS3:HRRR/path/and/new-name` | will overwrite existing file? |
| copy file from computer to S3 and rename | `./rclone-v1.39/rclone copyto /this/path/and/file horelS3:HRRR/path/and/new-name` | will not overwrite if file exists?? |


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
|2019-Feb| Began archiving GOES-17| Archive ABI multichannel and GLM datasets|

### **`horelS3:GOES16/`**
GOES-16 Level 2 data (multiband format) from the [Amazon AWS NOAA archive](https://aws.amazon.com/public-datasets/goes/).
* #### **`ABI-L2-MCMIPC/`** Advanced Baseline Imager, Level 2, multiband format Cloud Moisture products
  * _**`YYYYMMDD/`**_  
     Example File: `OR_ABI-L2-MCMIPC-M3_G16_s20172631727215_e20172631729588_c20172631730098.nc`  
     File description on [Amazon](https://aws.amazon.com/public-datasets/goes/).
* **`GLM_L2_LCFA`** Geostationary Lightning Mapper, Level 2, Events/Groups/
Flashes
  * _**`YYYYMMDD/HH/`**_  
    Example File: `OR_GLM-L2-LCFA_G16_s20190382239200_e20190382239400_c20190382239426.nc`


### **`horelS3:GOES17/`**
GOES-17 Level 2 data (multiband format) from the [Amazon AWS NOAA archive](https://aws.amazon.com/public-datasets/goes/).
* #### **`ABI-L2-MCMIPC/`** Advanced Baseline Imager, Level 2, multiband format Cloud Moisture products
  * _**`YYYYMMDD/`**_  
     Example File: `OR_ABI-L2-MCMIPC-M3_G16_s20172631727215_e20172631729588_c20172631730098.nc`  
     File description on [Amazon](https://aws.amazon.com/public-datasets/goes/).
* **`GLM_L2_LCFA`** Geostationary Lightning Mapper, Level 2, Events/Groups/
Flashes
  * _**`YYYYMMDD/HH/`**_  
    Example File: `OR_GLM-L2-LCFA_G17_s20190382239200_e20190382239400_c20190382239426.nc`

### **`horelS3:hrrr/`** Operational HRRR
  * **`sfc/`** Surface fields
    * _**`YYYYMMDD/`**_
      * Analysis and forecast hours (f00-f18) for all hours (00-23).
      * File example: `hrrr.t00.wrfsfcf00.grib2`

  * **`prs/`** Pressure fields
    * **_`YYYYMMDD/`_**
      * Analysis hour (f00) only for all hours (00-23).
      * File example: `hrrr.t00.wrfprsf00.grib2`
 
### **`hrrrX/`** Experimental HRRR
  * **`sfc/`** Surface fields
    * **_`YYYYMMDD/`_**
      * Analysis hour (f00) for all hours, if available.
      * File example: `hrrrX.t00.wrfsfcf00.grib2`

### **`hrrrak/`** HRRR Alaska (Operational after 12 July 2018)
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

## Contents of this repository

### **`GOES_downloads/`**
Download scripts for the GOES-16 and GOES-17 data from the `noaa-goes16` and `noaa-goes17` bucket on Amazon S3. Run by cron every 15 minutes on `meso1` by mesohorse user.
  - `download_GOES_16-17.py` downloads GOES 16 and GOES17 data.
  - `download_GOES16_GLM.py` downloads GLM data.  

I want to consolidate these download into one script, but need to change the directory structure of GOES16 ABI to the same as it is organized on Amazon (I was young and inexperienced when I started downloading GOES16 and thought I new a better way to organize things. I have since learned my lesson.)


### **`HRRR_downloads/`**
Download scripts for the HRRR data. These are run by cron every three hours (00:29, 03:29, 06:29, 09:29, 12:29, 15:29, 18:29, 21:29) 
  - `hrrr_download_manger.py` main download script
  - `download_operational_hrrr.py` controls HRRR downloads from NOMADS
  - `download_experimental_hrrr.py` controls HRRR downloads from ESRL
  - `email_log.py`: sends me an email to confirm the files are now on the Pando archive.
  - `look_for_bad_idx_files.py` finds files that do not match the .idx files we expect.
  - `risk_old_hrrr.py` deletes backup files located on `horel-group7`. This is necessary because horel-group7 only has 60 TB of space and our Pando allocation is 130 TB.

### `rclone-v1.39-linux-386/`
Contains the version of rclone you should use so we don't get stuck when CHPC updates rclone versions.

### `s3cmd-2.0.1/` 
Contains `s3cmd` which is used to change permissions of files on S3 from private to public, and vice versa. (see below Q&A for usage)

### `Old_Pando/`
Old scripts used before the Pando Failure in January 2018

### `scripts_from_archive_users/`
Scripts shared to me by users of the archive

#### Other scripts:
- `just_download_hrrr_from_nomads.py`
- `list_missing_files.py`
- `purge_files_from_PANDO.py`

---
---


# Other Questions and Answers:

## How do I rename a file when I copy it to S3?
Use the `copyto` and `moveto` commands. These are only available in the newest rclone version. The rclone version best to use is the one installed here or newer: `/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone`

## How do I list files on Pando in alpha-numeric order with `rclone`?
rclone will not sort file names for you, but you can pipe the output to the sort command.
For example:  

    rclone ls horelS3:HRRR/oper/sfc/20170109/ | sort -k 2`

Where the "k" specifies which field to sort by. The first field is file size and
the second field (2) is the file name.

You can sort directory contents like this:

    rclone lsd horelS3:HRRR/oper/sfc | sort -k 4

## How do you get the total size of a bucket or directory?
With some creative linux commands...

How big is a bucket, in Terabytes?

    rclone ls horelS3:HRRR | cut -c 1-10 | awk '{total += $0} END{print "sum(TB)="total/1000000000000}'

How big is a directory, in Gigabytes?

    rclone ls horelS3:HRRR/oper/sfc/20161213 | cut -c 1-10 | awk '{total += $0} END{print "sum(GB)="total/1000000000}'

## How do you make a directory or files public/private?
You have to use `s3cmd` to change the files from public to private. You would want to do this for each file added to the S3 archive that you want to be downloadable from the download URL.

s3cmd is installed here: `/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd`  

> _NOTE: In order to set bucket names that are all lower case to public, I had to modify the configuration file.  In my `.s3cfg` file on the `host_bucket` line, remove the “s” after `$(bucket)`.  Once I did this I can could and make public whatever bucket name I want._

First navigate to `/uufs/chpc.utah.edu/common/home/horel-group/archive_s3/s3cmd-2.0.1` directory.

#### Make public
Make a bucket public:

     ./s3cmd setacl s3://GOES16 --acl-public

Make a file public:

     ./s3cmd setacl s3://hrrr/sfc/20180101/filename.grib2 --acl-public

Make a directory public:

     ./s3cmd setacl s3://hrrr/sfc/20180101/ --acl-public --recursive

#### Make private

Make a bucket private:
    
    ./s3cmd setacl s3://GOES16 --acl-private

Make a file private:
    
    ./s3cmd setacl s3://hrrr/sfc/20180101/filename.grib2 --acl-private

Make a directory private: 

    ./s3cmd setacl s3://hrrr/sfc/20180101/ --acl-private --recursive


## How is `rclone` and `s3cmd` configured?
Configuration files for the mesohorse user:  
`/scratch/local/mesohorse/.s3cfg`  
`/scratch/local/mesohorse/.rclone-conf`

For `rclone`, it is set up like this for the mesohorse user. The access keys are kept safe and I won't display them here.

    [horelS3]
    type = s3
    env_auth = false
    access_key_id = [THIS IS A SECRET]
    secret_access_key = [THIS IS A SECRET]
    region = 
    endpoint = https://pando-rgw01.chpc.utah.edu
    location_constraint =


## How much space is left and when will the S3 archive fill up?
The [Pando Allocation Web Display (PAWD)](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/Pando_archive/) shows the Pando allocation and usage for each bucket. The script that creates this display is run once a day by Brian on meso4 and is located on [GitHub](https://github.com/blaylockbk/Web-Homepage/blob/master/Pando_archive/daily_usage.py).

![Pando Allocation](./images/screenshot_allocation.png "Pando Allocation Web Display")


## Where can I find examples on how to download HRRR data with a script?
Check out the scripting tips here: [Scripting Tips](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_script_tips.html)

## How do I configure `rclone` to access the NOAA's GOES-16 archive on Amazon AWS?
Since the NOAA GOES-16 archive is a public and free bucket, it is really easy to access the data via `rclone`.

Configure `rclone`

    rclone config

1. Name the remote something like `AWS`. 
2. Select `2` for Amazon S3 access and press enter to select empty or default values for the remaining options.
3. When asked if it is right, type `y` for yes.

For example, your `.rclone.conf` file should have this in it:

    [AWS]
    type = s3
    env_auth =
    access_key_id =
    secret_access_key =
    region =
    endpoint =
    location_constraint =


You are now on your way to accessing the Amazon GOES16 archive. To list the buckets in the `noaa-goes16` bucket, type:

    rclone lsd AWS:noaa-goes16 

    rclone lsd AWS:noaa-goes17

---
---

# Pando Operational Download Tasks and Troubleshooting
The script `script_download_hrrr.csh` runs the HRRR download manager script which is responsible for initiating downloads for HRRR, HRRR-AK, and HRRR-X. The script runs on the `meso1` crontab by the mesohorse user every three hours.

To log onto `meso1.chpc.utah.edu` as the mesohorse user, you need permission. Ask John Horel about getting this permission and CHPC will grant it. To become the mesohorse user, you need to do the following:

    sudo su - mesohorse

In my `.aliases` file, this is set up as an alias, `alias horse 'sudo su - mesohorse'` so that when I type `horse`, it makes me the mesohorse user.


The crontab for the download is as follows:

    ## PANDO HRRR Download
    29 0,3,6,9,12,15,18,21 * * * /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/HRRR_downloads/script_download_hrrr.csh >& /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/HRRR_downloads/testtest_123.txt

    ## PANDO GOES16 Download
    1,16,31,46 * * * * /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/GOES_downloads/script_download_GOES16.csh >& /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/GOES_downloads/crontab_goes16.txt

## Troubleshooting

There are a few defensive measures to help prevent script and download failures.

1. **The Emailed Log**: If the downloads successfully finish, then an emailed receipt is sent to my email that show which files are on the Pando archive. This is the first line of defense. I mostly ignore the emails, but if that email doesn't come every three hours or if files are missing, then there may be a problem with Pando.
2. **Restart Download**: The `script_download_hrrr.csh` script writes a temporary file before anything else called `hrrr.status`. If a previous download task is still running or got stuck, then the script will attempt to kill the old process and restart it again. An email notifies if this occurred. If the downloads finish successfully before the next scheduled task, then the `hrrr.status` file is deleted.
3. **Run Script Manually**: If there has been trouble, try running the `script_download_hrrr.csh` script or `hrrr_download_manager.py` manually.

If the download script is having trouble, there may be a few reasons for this:

1. Is the `meso1` box available? Can you log onto it? Are there too many processes running that are bogging the machine down?    
2. Is the HRRR data available? Is NOMADS having server issues? See if the website works and if it is running slow: https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/
3. Is the Pando allocation full? Can you move any files to Pando using the Horel-Group allocation? Are you getting an error that says **`QuotaExceeded`**? This means the Pando allocation is run up. Contact Sam Liston about this error if you believe the quota hasn't been reached. In the past, our allocation has appeared bloated because there are many small .idx files. It's weird.
    - From an email on 8 March 2018: _Interesting issues with our data on Pando being bloated. Our objects are taking up 36 TB, but Pando thinks we are using 100+ TB. Sam removed our allocation for now and he will keep an eye on it and continue investigating the issue._
4. Are the tasks scheduled in crontab? It might be possible that a machine reset messed up the crontab, so check that the tasks are running properly.

Handy commands to check on things...

    # Check the processes running a Pando related script
    ps -ef | grep Pando

    # Check the processes run by mesohorse user
    ps -ef | grep 30067

    # Kill a process (as the mesohorse user)
    kill -9 [PID]

___
#### For questions, contact  Brian Blaylock  (brian.blaylock@utah.edu)
![](./images/wxicon_medium.png)
