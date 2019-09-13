**Brian Blaylock**  
**September 12, 2019**

[**Back to Home**](../README.md)

# ⚠ Potential Pando Issues

The purpose of this document is to describe potential issues that might come up while using the Pando archive.

<br>

## ❌Allocation errors
Our current allocation is 130 TB. For some unknown reason, the RADOS gateway and the `rclone size` command give different disk usage. Occasionally, this has caused our uploading to throw and error because the gateway thinks we have exceeded our allocation when we have not used it.

### Summary of emails
To Sam Liston March 2, 2018

> Sam, I am moving lots of data to Pando. We have 35.5 TB on it right now, but I'm getting a QuotaExceeded error when I try to sync additional files. I thought we had a 60 TB allocation. Or is this error caused by something else??  
> `2018/03/02 08:58:19 ERROR : hrrr.t08z.wrfsfcf07.grib2: Failed to copy: MultipartUpload: upload multipart failed upload id: 2~RvD_oripFZVAdWJaMqNPzFCXSron-r4 caused by: QuotaExceeded: status code: 403, request id: tx0000000000000000b9c9b-005a99749b-4e9d57-default, host id:`

From Sam Liston
> I’m not sure what to think about this.  First just to qualify this, through the rados layer I can only see raw usage and quotas are set according to raw usage, so your 60TB purchase is a 90TB quota to accommodate the erasure overhead.  According to a query of your usage through rados you are using  just over 100TB, but If I use rclone and do a size query of each of your buckets, you are only using ~36TB.  I can’t account for this discrepancy.  I know that you can get bloating if you put a ton of files in that are smaller than the minimum object size as it will use the full minimum object size worth of capacity, but I can’t imagine that it would be 3x.  I’ve disabled your quota for the moment, while I try to figure it out, but as far as rados is concerned you are using ~100TB even though my ceph monitoring software says only 74TB as being used system wide.

From Sam
> Brian, So as far as I can tell your usage is artificially inflated by around 41TB (raw).  I can’t find a way to have the rados layer re-inventory.  As an experiment, I have inflated your quota by 41TB raw (~25TB usable).  I am curious to see if as you put more data in, if you usage remains ~41TB inflated, or if it continues to over-inflate.  At any rate, please proceed and let’s see what happens.

<br>

## ❌RADOS Gateway certificate errors
The RADOS Gateway is the door in and out of Pando. On September 7th, the certificate 
expired for https://pando-rgw01.chpc.utah.edu/ and thus files could not be uploaded
to Pando or downloaded from Pando. A new certificate has since been acquired.

The alternative gateway did work: https://pando-rgw02.chpc.utah.edu. Sam Liston 
said that rgw02 was originally for the Globus transfers, but CHPC decided not
to pay for that plug in since it isn't used. This means we are free to use
`pando-rgw01` and `pando-rgw02` for uploading and downloading from Pando. If
one or the other stops working (for certificate issues or any other reason), 
there is a flag in the download scripts to change the gateway. Look for the line that says:

    rados_gateway = 1

### Summary of emails

To Sam Liston on September 8, 2019

> Hi Sam, I'm seeing this error when attempting to upload to Pando  
> `2019/09/08 18:22:00 ERROR : : error reading destination directory:   RequestError: send request failed caused by: Get https://pando-rgw01.chpc.utah.edu/hrrr?delimiter=%2F&max-keys=1000&prefix=sfc%2F20190908%2F: x509: certificate has expired or is not yet valid`

From Sam Liston on September 9, 2019

> Brian, Yes. The cert has expired, and campus with their new cert tools can’t give us the type of cert we need.  We are looking to purchase one today from a third party company.  It the meantime, if it is not to difficult you could redirect things to pando-rgw02.chpc.utah.edu. Sorry for the inconvenience

From Sam Liston on September 10, 2019

> Brian, We have a new cert in place for pando-rgw01.chpc.utah.edu.  We were forced to go with a simpler cert with just the hostname, vs. with a wildcard (i.e *.pando-rgw01.chpc.utah.edu).  The result of this is references to `bucket-name.pando-rgw01.chpc.utah.edu` throw a cert warning.  References to `pando-rgw01.chpc.utah.edu/bucket-name` still work great.  I’m hoping you are using the bucket name as a suffix vs a prefix.  If you are not you may have to add some logic to handle the cert warning.

<br>

## ❌ "Access Denied" when trying to download from Pando
This error is caused by not setting the bucket and the file to **public**. You can do this with the `s3cmd` command. 

`s3cmd` is installed in `.../horel-group7/Pando_Scripts/s3cmd-2.0.1/` and a config file is located in the users home directory `.s3cfg`.

    # Set a new bucket as public 
    ./s3cmd setacl s3://GOES16 --acl-public

To make the files in the bucket public...

    # Make a single file public
    ./s3cmd setacl s3://hrrr/sfc/20180101/filename.grib2 --acl-public

    # Make contents of a "directory" public:
    ./s3cmd setacl s3://hrrr/sfc/20180101/ --acl-public --recursive

> Note: The `.s3cfg_rgw02` config file in Brian's home directory can be used to use RADOS gateway02. 
> To use that config file, use the `-c` option   
> `./s3cmd -c PATH/.s3cfg_rgw02 setacl {etc.}`

<br>

## ❌ "`horel-group7` low on available disk space"
`horel-group7` is the "Pando Backup." As part of the HRRR download process, files are downloaded from NOMADS to horel-group7 before the files are synced to Pando. The oldest files for the forecast hours removed from horel-group7, ricking them to be lost if the Pando archive ever fails. As the archive length increases, the amount of "non-risked" files increases and uses all the disk space. When horel-group7 becomes full, you will need to decide what you want to keep backed up and what you want to risk keeping on Pando.

If horel-group7 is full, the download scripts will fail because HRRR data is first downloaded from NOMADS to horel-group7, then from horel-group7 to Pando.

I would argue that the GOES data does not need to be backed up on horel-group7 (or Pando for that matter) at all because Amazon is doing a great job keeping that accessible. (Will that be true forever? I don't know.)


<br>

## ❌ Is the NOMADS server responding slow?
Files not downloaded? Sometimes NOMADS goes down or is very slow to download from. 

<br>

## ❌ Are there any CHPC issues?
Files not downloaded? Is CHPC having any issues? Is the python path broke?

<br>

# 🚧‍ Troubleshooting

There are a few defensive measures to help prevent script and download failures.

1. **The Emailed Log**: For the HRRR files, once a day the `email_log.py` script runs and emails a summary of data checks. This is the first line of defense. It lists bad or missing .idx files on horel-group7 and shows a table of files available on Pando for the previous day.
    - If the table shows missing files on Pando, they might be on horel-group7 and just need to be re-synced. This error could occur because there is trouble getting access to Pando (allocation or certificate errors).
    - If the .idx files on horel-group7 are bad or missing, this means the files have not been downloaded or have downloaded incomplete. This likely is caused by an issue with the NOMADS server being down or slow OR CHPC is having issues.
2. **Restart Download**: The `script_download_hrrr.csh` script writes a temporary file before anything else called `hrrr.status`. If a previous download task is still running or got stuck, then the script will attempt to kill the old process and restart it again. An email notifies if this occurred. If the downloads finish successfully before the next scheduled task, then the `hrrr.status` file is deleted.
3. **Run Script Manually**: If there has been trouble, the first thing to try is running the `script_download_hrrr.csh` script or `hrrr_download_manager.py` manually. Then you can look at the printed output and see where the issue might be.

If the download script is having trouble, there may be a few reasons for this:

1. Is the `meso1` box available? Can you log onto it? Are there too many processes running that are bogging the machine down?
1. Is the HRRR data available? Is NOMADS having server issues? See if the website works and if it is running slow: https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/
1. Is the Pando allocation full? Can you move any files to Pando using the Horel-Group allocation? Are you getting an error that says **`QuotaExceeded`**? This means the Pando allocation is run up. Contact Sam Liston about this error if you believe the quota hasn't been reached. In the past, our allocation has appeared bloated because there are many small .idx files. It's weird.
1. Are the tasks scheduled in crontab? It might be possible that a machine reset messed up the crontab, so check that the tasks are running properly.

## Handy commands to check on things...

    # Check the processes running a Pando related script
    ps -ef | grep Pando

    # Check the processes run by mesohorse user
    ps -ef | grep 30067

    # Kill a process (as the mesohorse user)
    kill -9 [PID]