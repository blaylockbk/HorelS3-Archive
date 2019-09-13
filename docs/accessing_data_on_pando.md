**Brian Blaylock**  
**September 12, 2019**

[**Back to Home**](../README.md)

# Accessing Data on Pando

This document describes how to access the data as a public user.

Access to Pando is made via two "gateways" or "endpoints":

    https://pando-rgw01.chpc.utah.edu
<!---->
    https://pando-rgw02.chpc.utah.edu

Bucket and file name is listed after the URL. The `hrrr`, `hrrrak`, `hrrrX`, `GOES16`, and `GOES17` buckets are public buckets.

For example: https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20190101/hrrr.t01z.wrfsfcf00.grib2

<br>

## Web interface

|URL Link|Description|
|--|--|
|[HRRR download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_download.cgi)| Buttons illuminated if file is available. Option to download the GRIB2 file, the metadata file, or view a sample image. More information can be found at the FAQ page http://hrrr.chpc.utah.edu/.
|[_Alternative_ HRRR download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=hrrr)|Alternative page to download HRRR files from Pando (in list form)|
|[GOES on Pando download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi)|Buttons illuminated if file is available. Over over button to view a sample image of the file (for CONUS and Utah). Click button to download the file.
|[_Alternative_ GOES16 download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=GOES16)|Alternative page to download GOES files from Pando (in list form)|
|[_Alternative_ GOES17 download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=GOES17)|Alternative page to download GOES files from Pando (in list form)|
|[Amazon AWS Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_AWS_download.cgi)|NOT PANDO. Download interface for Amazon S3 buckets (GOES, NEXRAD, etc.|
|[_Alternative_ Amazon AWS GOES Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_download.cgi)|NOT PANDO. Download interface for Amazon AWS GOES S3 buckets|

> **For generic access to all buckets and objects on Pando via a web browser:**  
[http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi)

## rclone
You can set up `rclone` and use in a Linux terminal (you can also get rclone for a PC). Use the gateways listed above during configuration. Follow the instructions here: https://github.com/blaylockbk/pyBKB_v3/blob/master/rclone_howto.md

## Scripting
A good place to start is the [Script Tips](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_script_tips.html). There you will find information for accessing the data with `cURL`--most importantly how to do a range-get to retrieve a single variable from HRRR rather than the entire grib2 file using the .idx files--and different Python methods as well as an introduction to the `s3fs` Python module.

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


<br>

# 🐍 Python: Access to bucket contents with `s3fs`
You can access bucket and files with the `s3fs` python package. 

    import s3fs
    # Access Pando
    fs = s3fs.S3FileSystem(anon=True, client_kwargs={'endpoint_url':"https://pando-rgw01.chpc.utah.edu/"})
    # List file objects in a path
    fs.ls('hrrr/sfc/20190101/')

Read the full documentation here: https://s3fs.readthedocs.io/en/latest/

<br><br>

# How do I configure `rclone` to access public Amazon AWS buckets (e.g. noaa-goes16)?
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
    rclone lsd AWS:noaa-nexrad-level2

<br>

> You might notice that buckets on Amazon are accessed with the bucket-prefix notation: `https://noaa-goes16.s3.amazonaws.com/`. Why can't you use this notation with Pando? For example, why does `https://hrrr.pando-rgw01.chpc.utah.edu/` not work? This is because the security certificates Sam Liston could acquire for Pando are different. That is why we use the `https://pando-rgw01.chpc.utah.edu/hrrr/` notation to access buckets on Pando.

