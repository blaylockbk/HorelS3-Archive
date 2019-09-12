**Brian Blaylock**  
**September 12, 2019**

# Accessing Data from Pando

The purpose of this document is to describe how to access data from the Pando archive.

## Web interface

|URL Link|Description|
|--|--|
|[HRRR download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_download.cgi)| Buttons illuminated if file is available. Option to download the GRIB2 file, the metadata file, or view a sample image. More information can be found at the FAQ page http://hrrr.chpc.utah.edu/.
|[_Alternative_ HRRR download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=hrrr)|Alternative page to download HRRR files from Pando (in list form)|
|[GOES on Pando download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi)|Buttons illuminated if file is available. Over over button to view a sample image of the file (for CONUS and Utah). Click button to download the file.
|[_Alternative_ GOES16 download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=GOES16)|Alternative page to download GOES files from Pando (in list form)|
|[_Alternative_ GOES17 download page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_pando_download.cgi?BUCKET=GOES17)|Alternative page to download GOES files from Pando (in list form)|
|[Amazon AWS Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/generic_AWS_download.cgi)|Download interface for Amazon S3 buckets (GOES, NEXRAD, etc.|
|[_Alternative_ Amazon AWS GOES Download Page](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_download.cgi)|NOT PANDO. Download interface for Amazon AWS GOES S3 buckets|


## Scripting
A good place to start is the [Script Tips Website](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_script_tips.html). There you will find information for accessing the data with `cURL`--most importantly how to do a range-get to retrieve a single variable rather than the entire grib2 file--and different Python methods as well as an introduction to the `s3fs` Python module.