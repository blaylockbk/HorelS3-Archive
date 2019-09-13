**Brian Blaylock**  
**September 13, 2019**

[**Back to Home**](../README.md)

# `s3cmd` and Pando

[Documentation for s3cmd](https://s3tools.org/usage)

## What is `s3cmd`

`s3cmd` is used to make buckets and contents of those buckets public or private. It it necessary to make buckets and files public so they can be accessed by others who don't have the keys to get into Pando. By setting the ACL to public, others can retrieve content from Pando.

## How do you make a directory or files public/private?
You have to use `s3cmd` to change the files from public to private. You would want to do this for each file added to the S3 archive that you want to be downloadable from the download URL.

s3cmd is installed here: `/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd`  

> _NOTE: In order to set bucket names that are all lower case to public, I had to modify the configuration file.  In my `.s3cfg` file on the `host_bucket` line, remove the “s” after `$(bucket)`.  Once I did this, I could and make public whatever bucket name I want. Not sure why, it's something Sam Liston tole me to do._

First navigate to the `/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/` directory.

## Make public
If you create a new bucket, that bucket needs to be made public before you make the files inside public.

    # Make a bucket public
    ./s3cmd setacl s3://GOES16 --acl-public

    # Make a file public
    ./s3cmd setacl s3://hrrr/sfc/20180101/filename.grib2 --acl-public

    # Make a directory public
    ./s3cmd setacl s3://hrrr/sfc/20180101/ --acl-public --recursive

## Make private

    # Make a bucket private
    ./s3cmd setacl s3://GOES16 --acl-private

    # Make a file private
    ./s3cmd setacl s3://hrrr/sfc/20180101/filename.grib2 --acl-private

    # Make a directory private 
    ./s3cmd setacl s3://hrrr/sfc/20180101/ --acl-private --recursive


<br>

# How is `s3cmd` configured?
Configuration files for the mesohorse user:  
`/scratch/local/mesohorse/.s3cfg`  

`.s3cfg` uses the RADOS Gateway #1. I have a config file for RADOS Gateway #2 located here: `u0553130/.s3cfg_rgw02`. To use that config file, you can use the `-c` option. This was necessary for a few days when the certificates for RADOS Gateway #1 were expired.

    ./s3cmd -c Path/to/u0553130/.s3cfg_rgw02 <commands you want to use>