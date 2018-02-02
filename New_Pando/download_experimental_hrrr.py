# Brian Blaylock
# brian.blaylock@utah.edu 
#
# February 2, 2018                                "It's Groundhog Day...again."

"""
Download experimental HRRR files from ESRL
"""

def get_grib2(model, hour, field, fxx, idx=True, png=True):
    """
    Download EXPERIMENTAL HRRR from NOAA ESRL via FTP
    ftp://gsdftp.fsl.noaa.gov/

    Input:
        model - [hrrr, hrrr_ak, hrrre, hrrr_smoke, hrrr_hi, hrrr_wfip2]
        hour  - range of hours desired
                hrrr range(0,24)
                hrrrak range(0,24,6)
        field - sfc, prs, nat, subh
        fxx   - forecast hours desired
                range(0,19) or range(0,37) if hour == 0, 6, 12, or 18
        idx   - should I create an .idx file?
        png   - should I create an .png sample image?
    """