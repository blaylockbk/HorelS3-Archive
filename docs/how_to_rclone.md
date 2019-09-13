**Brian Blaylock**  
**September 13, 2019**

[**Back to Home**](../README.md)

# `rclone` and Pando

[Documentation for rclone](https://rclone.org/docs/)

## What is `rclone`
`rclone` (http://rclone.org/) allows you to sync files and directories between
your computer and cloud-based storage systems like S3 buckets, including Pando.
Before getting started, first review the [CHPC rclone tutorial](https://www.chpc.utah.edu/documentation/software/rclone.php).

Access to Pando is made via two gateways or endpoints. You can configure rclone with either.

    https://pando-rgw01.chpc.utah.edu
<!---->
    https://pando-rgw02.chpc.utah.edu

## Configuration
1. The easiest way is use rclone is to load it with [modules](https://chpc.utah.edu/documentation/software/modules.php). Available versions of rclone are different depending on the host's RedHat version. Type: `module load rclone` to import the default version.

1. Set up the config file: **Note: The following options are the settings used for the mesohorse user.** You may also want to set this up for yourself (i.e., your own uNID) becuase as long as you have the access and secret key you can upload file to Pando.

    Type `rclone config`. You will be asked a series of questions. Use these options:  
              
      1. Select `n` for new remote  
      2. Enter a name. You will reference the S3 archive with this name. I used `horelS3`
      3. Type: Select option `2` for S3  
      4. "Get AWS credentials from runtime": Set to `False`  
      5. Enter the access key: _Ask Brian or John for this, unless you know where to find it_
      6. Enter the secret key: _You'll have to ask for this, too_
      7. Region: leave blank (press `enter` to skip)
      8. Endpoint: Enter `https://pando-rgw01.chpc.utah.edu` (alternatively, you may use `pando-rgw02`)
      9. Location: Select option `1` for none

Completing this setup makes a `.rclone.conf` file in your home directory. (See the end of this document for how rclone is configured for mesohorse).

> NOTE: The version of rclone installed in `horel-group7/Pando_Scripts/rclone-v1.39-linus-386/rclone` is explicitly used by the download scripts. The reason is just in case CHPC changed the default rclone version that might be incompatible with the download scripts. I haven't run into problems for a long time, so when I want to use rclone, I just do the `module load rclone`. 

<br>

## Basic Command Examples
The full usage documentation for rclone is found at [rclone.org](https://rclone.org/docs/). The following examples are some of the more useful. These examples can be used if you named the archive source `horelS3` as described in the configuration step above. If you named your source differently when you configured rclone, simply replace the name before the colon.

|      What do you want to do?                |       Command     | Notes  |
|---------------------------------------------|-------------------|--------|
| list top-level buckets                      | `rclone lsd horelS3:` | `lsd` Only lists the directories in the path |
| list buckets in bucket                      | `rclone lsd horelS3:hrrr` |
| list buckets in path                        | `rclone lsd horelS3:hrrr/oper` |
| list bucket contents                        | `rclone ls horelS3:hrrr` | `ls` will list everything in the bucket including all directory's contents, so this particular example isn't very useful |
| list bucket/path contents                   | `rclone ls horelS3:hrrr/oper/sfc/20171201` | currently, no way to sort alpha-numerically, unless you pipe the output to sort. Add the following: `| sort -k 2` |
| list bucket contents                        | `rclone lsl horelS3:hrrr/oper/sfc/20161213` | `lsl` will list more details than `ls`|
| copy file from your computer to S3          | `rclone copy ./file/name/on/linux/system horelS3:path/you/want/to/copy/to/`| You have to use version 1.39+ to use `copyto` or `moveto` in order to rename files when transferring to Pando.
| copy file from S3 to your current directory  | `rclone copy horelS3:HRRR/oper/sfc/20161201/hrrr.t12z.wrfsfcf16.grib2 .` |
| delete a file or directory on S3 | *I'm not going to tell you how to do this because there is no undo button!!!* |
| make a new bucket                           | `rclone mkdir horelS3:hrrr` | Note: new buckets need to be set to public with `s3cmd` if you want public access to the contents.
| make a new bucket/path                      | `rclone mkdir horelS3:hrrr/oper/sfc/` | It isn't necessary to `mkdir` before copying because `copy` will make the directory if it doesn't exist


<br> 

----

# Q&A

## How do I rename a file when I copy it to S3?
Use the `copyto` and `moveto` commands. These are only available in version 1.39+. The rclone version best to use is the one installed here or newer: `/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone`

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

<br>

# How is `rclone` configured?
Configuration files for the mesohorse user:  
`/scratch/local/mesohorse/.rclone.conf`

These remotes are used for different purposes:
- `horelS3` remote is used to access Pando with RADOS Gateway #1
- `horelS3_rgw02` remote is used to access Pando with RADOS Gateway #2
- `AWS` remote is used to access Amazon AWS `noaa-goes16` and `noaa-goes17` buckets

Below is how rclone is configured for the mesohorse user. The access and secret keys are kept safe and I won't display them here.

    [horelS3]
    type = s3
    env_auth = false
    access_key_id = [THIS IS A SECRET]
    secret_access_key = [THIS IS A SECRET]
    region = 
    endpoint = https://pando-rgw01.chpc.utah.edu
    location_constraint =

    [horelS3_rgw02]
    type = s3
    env_auth = false
    access_key_id = [THIS IS A SECRET]
    secret_access_key = [THIS IS A SECRET]
    region = 
    endpoint = https://pando-rgw02.chpc.utah.edu
    location_constraint =

    [AWS]
    type = s3
    env_auth =
    access_key_id =
    secret_access_key =
    region =
    endpoint =
    location_constraint =


Try the following as mesohorse or as yourself:

    module load rclone
    rclone lsd horelS3:
    rclone lsd horelS3_rgw02
    rclone lsd AWS:noaa-goes16
    rclone lsd AWS:noaa-goes17
    rclone lsd AWS:noaa-nextrad-level2
