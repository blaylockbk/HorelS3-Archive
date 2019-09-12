**Brian Blaylock**  
**September 12, 2019**

# ⚠ Potential Pando Issues

The purpose of this document is to describe potential issues that might come up while using the Pando archive.

<br><br>

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

<br><br>

## ❌RADOS Gateway certificate errors
The RADOS Gateway is the door in and out of Pando. On September 7th, the certificate 
expired for https://pando-rgw01.chpc.utah.edu/ and thus files could not be uploaded
to Pando or downloaded from Pando. A new certificate has since been acquired.

The alternative gateway did work: https://pando-rgw02.chpc.utah.edu. Sam Liston 
said that rgw02 was originally for the Globus transfers, but CHPC decided not
to pay for that plug in since it isn't used. This means we are free to use
`pando-rgw01` and `pando-rgw02` for uploading and downloading from Pando. If
one or the other stops working (for certificate issues or any other reason), 
there is a flag in the scripts to change the gateway. Look for the line that says:

    rados_gateway = 1

### Summary of emails

To Sam Liston on September 8, 2019

> Hi Sam, I'm seeing this error when attempting to upload to Pando  
> `2019/09/08 18:22:00 ERROR : : error reading destination directory:   RequestError: send request failed caused by: Get https://pando-rgw01.chpc.utah.edu/hrrr?delimiter=%2F&max-keys=1000&prefix=sfc%2F20190908%2F: x509: certificate has expired or is not yet valid`

From Sam Liston on September 9, 2019

> Brian, Yes. The cert has expired, and campus with their new cert tools can’t give us the type of cert we need.  We are looking to purchase one today from a third party company.  It the meantime, if it is not to difficult you could redirect things to pando-rgw02.chpc.utah.edu. Sorry for the inconvenience

From Sam Liston on September 10, 2019

> Brian, We have a new cert in place for pando-rgw01.chpc.utah.edu.  We were forced to go with a simpler cert with just the hostname, vs. with a wildcard (i.e *.pando-rgw01.chpc.utah.edu).  The result of this is references to `bucket-name.pando-rgw01.chpc.utah.edu` throw a cert warning.  References to `pando-rgw01.chpc.utah.edu/bucket-name` still work great.  I’m hoping you are using the bucket name as a suffix vs a prefix.  If you are not you may have to add some logic to handle the cert warning.

<br><br>

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


<br><br>

## ❌ "`horel-group7` low on available disk space"
`horel-group7` is the "Pando Backup." As part of the HRRR download process, files are downloaded from NOMADS to horel-group7 before the files are synced to Pando. The oldest files for the forecast hours removed from horel-group7, ricking them to be lost if the Pando archive ever fails. As the archive length increases, the amount of "non-risked" files increases and uses all the disk space. When horel-group7 becomes full, you will need to decide what you want to keep backed up and what you want to risk keeping on Pando.

I would argue that the GOES data does not need to be backed up on horel-group7 (or Pando for that matter) at all because Amazon is doing a great job keeping that accessible. (Will that be true forever? I don't know.)