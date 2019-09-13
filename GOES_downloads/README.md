**Brian Blaylock**  
**September 12, 2019**

[**Back to Home**](../README.md)

# 🌎 GOES Downloads
Only the CONUS multi-band formatted ABI data and Level 2 GLM data are downloaded to horel-group7 and Pando.

I apologize for messing up the GOES-16 downloads (I was young and inexperienced when I started downloading GOES-16 and thought I knew a better way to organize things. I have since learned my lesson). I originally changed the directory structure from what AWS does because I wanted it to match the HRRR directory structure. Later, I realized it is much easier to use rclone to sync everything and retain the AWS directory structure. Thus,

- GOES16 on Pando follows the AWS structure for GLM and follows my new structure for ABI.
- GOES17 on Pando follows the same structure for both ABI and GLM.

GOES data is downloaded every 15 minutes. At this rate, you can preview recent images on the [website](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi).

    1,16,31,46 * * * * /uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/GOES_downloads/script_download_GOES16.csh

If the script runs when the previous process is still going, it attempts to kill the previous process and restart the current download attempt. This will throw you an email. It is more common for the GOES downloads to not finish than the HRRR downloads.

---

The downloads are managed by the main script `script_download_GOES.csh`. As explained earlier, the GOES16 downloads is a bit more comlicated than GOES17 due to my early directory organization. It performs the following tasks:

Note: `HG7` referes to `horel-group7`

1. `download_GOES16_GLM.py`: Download the GOES16 GLM data
    - Uses rclone to simply sync AWS directory to HG7, then sync HG7 to Pando.
1. `download_GOES16.py`: Download GOES16 ABI data
    - Download GOES16 ABI from AWS to HG7 and then sync to Pando _changing the original directory structure_. I regret doing this, but that's the way it is. This script puts the GOES16 ABI data in a directory by date. 
    - This script also creates a sample image for the CONUS domain and Utah subsection that corresponds with each file. This is very handy for [previewing the data](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi). Sample images are the ABI true color product with GLM flash points overlaid.
1. `download_GOES16-17.py`: Syncs ABI and GLM data from AWS for GOES-17.
    - Right now it only is downloading GOES-17 right now, but the script allows you to also sync GOES-16.
    - Technically, we could do all the syncing with this script, but again the GOES16 ABI directory structure is different than the way AWS organizes the data. Also, this script does not make the sample images for the satellite. 
    - It might be worthwhile to restructure the GOES-16 directories to match AWS. This would require deleating the GOES-16 contents and re-sync with AWS for all the dates. It would take some time, but might be worth it. If that is done, the web-based preview and download pages will need to be fixed.

## Do we need to archive GOES on Pando?
I don't think we need to archive GOES data because the data is available on Amazon. That archive looks stable, as long as the NOAA Big Data Project stays alive. My idea for this archive is to only retain sample images on Pando so you can browse the data via the [website](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/goes16_pando.cgi), but when you click the button to download, it would download the file from Amazon (not Pando). Removing the NetCDF files from Pando would save a about 15 TB of disk space at the time of this writing.  

**However, there is a case for keeping the data on Pando.** Data on Pando can be accessed more quickly because it is local and there is physically less copper to transfer the data from Pando to one of our compute nodes.