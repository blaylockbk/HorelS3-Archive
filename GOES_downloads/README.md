**Brian Blaylock**  
**September 12, 2019**

# GOES Downloads
Only download the CONUS domain multi-band formatted ABI data and Level 2 GLM data.


I apologize for messing up the GOES16 downloads. I change the directory structure from what AWS does. This is an artifact of download just the ABI files and organizing it the way I wanted it (each date as a directory) and then later downloading GLM data and realizing that keeping the AWS directory structure greatly simplified the downloads. 

GOES17 on Pando follows the same structure for both ABI and GLM downloads, but GOES16 follows the AWS structor for GLM and my own structure for ABI.

## PANDO GOES16 Download
GOES data is downloaded every 15 minutes so that you can preview the recent images on the [website](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi).

    1,16,31,46 * * * * /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/GO                                                                         ES_downloads/script_download_GOES16.csh >& /uufs/chpc.utah.edu/common/home/horel                                                                         -group7/Pando_Scripts/GOES_downloads/crontab_goes16.txt

The downloads is managed by the main script `script_download_GOES.csh`. It performs the following tasks...

1. `download_GOES16_GLM.py`: Download the GOES16 GLM data
    - Uses rclone to simply sync AWS directory to HG7, then sync HG7 to Pando.
1. `download_GOES16.py`: Download GOES16 ABI data
    - Download GOES16 ABI from AWS to HG7 and then sync to Pando _changing the original directory structure_. I regret doing this, but that's the way it is. This script puts the GOES16 ABI data a single directory by date. It also creates a sample image for the CONUS domain and Utah subsection that corresponds with each file. This is very handy for [previewing the data](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi).
    - Sample images is the ABI true color with GLM flash points overlaid.
1. `download_GOES16-17.py`: Syncs ABI and GLM data from AWS for both GOES-16 and GOES-17.
    - Right now it only is downloading GOES-17 right now.
    - Technically, we could do all the syncing with this script, but again the GOES16 ABI directory structure is different than the way AWS organizes the data. Also, this script does not make the sample images for the satellite.

> I don't think we need to archive GOES data, because the data is available on Amazon. My idea for this archive is to retain sample images on Pando so you can browse the data in the [website](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi), but when you click the button to download, it would download the file from Amazon (not Pando). This would save a about 15 TB of disk space if we did not archive GOES data.  
>However, there is a case for keeping the data on Pando...that data can be accessed more quickly because it is local and there is physically less copper to transfer the data from Pando to one of our compute boxes. If you choose to keep the GOES data, it might be worthwhile simplifying the archive so that the GOES16 and GOES17 directory structure is the same. This would require deleting the GOES16 contents and re-sync with AWS for all the dates in the last few years. It would take some time, but maybe worth it?