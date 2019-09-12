## Brian Blaylock
## March 27, 2019

"""
Download GOES-16/17 from Amazon AWS to Horel-Group7 and copy to Pando archive.
     URL : https://aws.amazon.com/public-datasets/goes/
"""

from datetime import datetime, timedelta
import os

###############################################################################
# Rados Gateway
# Set to 1 or 2. This is an option if the certificate for the gateway URL 
# expires as it happened on September 8th, 2019.
# Rados Gateway 1 is the default and downloads from https://pando-rgw01.chpc.utah.edu
# Rados Gateway 2 is the alternative and downloads from https://pando-rgw02.chpc.utah.edu

rados_gateway = 2

###############################################################################

def download_goes(DATE, satellite, products=['ABI-L2-MCMIPC', 'GLM-L2-LCFA']):
    """
    Use rclone to downloads GOES-16 and GOES-17 NetCDF files for the Advanced
    Baseline Imager (ABI) and Geostationary Lightning Mapper (GLM) files
    available from Amazon AWS. Copy to horel-group7 and to Pando archive.
        https://noaa-goes16.s3.amazonaws.com
        https://noaa-goes17.s3.amazonaws.com
    
    Input:
        DATE      - A datetime object for the date that you want to download.
        satellite - Satellie name: 'goes16' or 'goes17'
        products  - A list of GOES products. Defaults explained below:
                       ABI-L2-MCMIPC : ABI Multichannel Product for CONUS
                       GLM-L2-LCFA   : Geostarionary Lightning Mapper
    """
    print "{:<80}".format("=====================================================================")
    print "{:^10}{:^10}{:<60}".format('Download', satellite.upper(), products)
    print "{:^80}".format(str(DATE))
    print "{:<80}".format("=====================================================================")


    ## Check data inputs
    # =========================================================================
    satellite = satellite.lower()
    assert satellite in ['goes16', 'goes17'], ('satellite argument must be "goes16" or "goes17"')
    
    # ABI files ending in 'C' are CONUS, 'F' are full disk, and 'M' are mesoscale domains.
    possible_products = ['ABI-L1b-RadC', 'ABI-L1b-RadF', 'ABI-L1b-RadM',    # Level 1 Radiance Data
                         'ABI-L2-CMIPC', 'ABI-L2-CMIPF', 'ABI-L2-CMIPM',    # Level 2 Data
                         'ABI-L2-MCMIPC', 'ABI-L2-MCMIPF', 'ABI-L2-MCMIPM', # Level 2 Data, Multi-Channel
                         'GLM-L2-LCFA']                                     # Level 2 GLM
    for p in products:
        assert p in possible_products, ('%s not in the list of possible products.') 
    # =========================================================================

    ## Sync each product from Amazon to Horel-Group7 and then copy to Pando.
    # Change the date directory to a human readable (not julian day of year)
    for p in products:
        AWS = 'AWS:noaa-%s/%s/%s/' % (satellite, p, DATE.strftime('%Y/%j'))
        HG7 = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/%s/%s/%s/' \
                % (satellite.upper(), p, DATE.strftime('%Y%m%d'))
        
        if rados_gateway == 1:
            PANDO = 'horelS3:%s/%s/%s/' % (satellite.upper(), p, DATE.strftime('%Y%m%d'))
        elif rados_gateway == 2:
            PANDO = 'horelS3_rgw02:%s/%s/%s/' % (satellite.upper(), p, DATE.strftime('%Y%m%d'))

        # Sync AWS and horel-group7. Retaining hour directories.
        rclone = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone'
        print 'Syncing AWS --> horel-group7...'
        os.system('%s sync %s %s' % (rclone, AWS, HG7))
        print '        AWS --> horel-group7...DONE!'

        # Sync horel-group7 to Pando.
        print 'Syncing horel-group7 --> Pando...'
        os.system('%s sync %s %s' % (rclone, HG7, PANDO))
        print '        horel-group7 --> Pando...DONE!'

        # Change permissions of PANDO directory to public
        print 'Set bucket contents to public...'
        if rados_gateway == 1:
            s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd'
        elif rados_gateway == 2:
            # Use config file in Brian's home directory
            s3cmd = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd -c /uufs/chpc.utah.edu/common/home/u0553130/.s3cfg_rgw02'

        os.system(s3cmd + ' setacl s3://%s --acl-public --recursive' % PANDO.split(':')[1])
    

if __name__ == '__main__':
    ## Loop many dates to backfill (going backwards)
    #sDATE = datetime(2019, 2, 7)
    #eDATE = datetime(2018, 12, 31)    # 7 Feb. 2019 is the first day GLM data was flowing from GOES-17.
    #DATES = [sDATE  - timedelta(days=i) for i in range((sDATE-eDATE).days)]
    #for DATE in DATES:     
    #    download_goes(DATE, 'goes17', products=['ABI-L2-MCMIPC', 'GLM-L2-LCFA'])

    timer1 = datetime.now()

    DATE = datetime.utcnow()
    #DATE = datetime(2018, 10, 31, 1)
    #download_goes(DATE, 'goes16', products=['ABI-L2-MCMIPC', 'GLM-L2-LCFA'])
    download_goes(DATE, 'goes17', products=['ABI-L2-MCMIPC', 'GLM-L2-LCFA'])

    if DATE.hour == 0 and DATE.minute < 20:
        yesterday = DATE-timedelta(days=1)
        download_goes(yesterday, 'goes17', products=['ABI-L2-MCMIPC', 'GLM-L2-LCFA'])

    print "\nDownload GLM run time: ", datetime.utcnow() - timer1

"""
---------------------------------------------------------------
    Manually do rclone and s3cmd commands for GOES16 bucket
---------------------------------------------------------------
/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/rclone-v1.39-linux-386/rclone sync /uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/GLM-L2-LCFA/ horelS3:GOES16/GLM-L2-LCFA/
/uufs/chpc.utah.edu/common/home/horel-group7/Pando_Scripts/s3cmd-2.0.1/s3cmd setacl s3://GOES16/GLM-L2-LCFA/ --acl-public --recursive
"""
