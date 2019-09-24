# Brian Blaylock 
# February 13, 2018

# Updated December 10, 2018 for Python 3 (Thanks J.Matt for sharing)

""" 
Download a single variable from the HRRR archive using cURL. 
More information at: https://hrrr.chpc.utah.edu 
""" 

import re 
from datetime import date, timedelta 
import os 
import requests

def download_HRRR_variable_from_pando(DATE, variable,
                                      hours=range(0, 24), fxx=[0],
                                      model='hrrr', field='sfc',
                                      more_vars=0,
                                      outdir='./'):
    """
    Download a partial grib2 file from the Pando archive (http://hrrr.chpc.utah.edu)
    by specifying the variable you wish to download. These single-variable
    grib2 files are about 1 MB in size. If you don't need the full grib2 file,
    retrieving only the variables you need can save you a lot in disk space.
    
    Input:
        DATE     - a python date object for the date you want to download
        variable - a string of the variable abbreviation and level that matches
                   the line in the .idx file you want to download from.
                   This string is used to search for the line in the grib2.idx
                   file so we can discover the byte range of the variable.
                   For example, if variable='TMP:2 m', we will search for that
                   line in the .idx file and use the byte range to do a partial
                   download from the full grib2 file to retrieve just that
                   field using cURL.
                   Check this URL for a sample .idx file:
                   https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20180101/hrrr.t00z.wrfsfcf00.grib2.idx
                   String must be unique enough to only occur once in the .idx
                   file, else it will download the last instance. Thus, include
                   both the variable abbreviation and the surface.
        hours    - a list of hours to download, within range(24).
        fxx      - a list of forecast hours to download, within range(19).
        model    - a string specifying the model you want to download.
                   Choose either 'hrrr', 'hrrrX', or 'hrrrak'
        field    - a string specifying the filed to download from.
                   Choose either 'sfc' for surface file or 'prs' for the
                   pressure file (prs includes many more variables than the sfc
                   file).
        more_vars- Tells how many lines to skip when looking for a byte range.
                   Default is zero, which downloads only the variable 
                   originally requested. You may be interested in downloading
                   additional variables, which is easy if they are adjacent to
                   each other in the grib2 file. For example, if you want both
                   the U and V 10 m wind components, you would set
                   variable = 'UGRD:10 m', and set more_vars=1 which will 
                   download the UGRD:10 m field and the next field, which is
                   the VGRD:10m field.
                   If you want all the variables at 500 mb, 
                   set variable='HGT:500 mb' and set more_vars=4, which will
                   download 'HGT:500 mb', 'TMP:500 mb', 'DPT:500 mb', 'UGRD:500 mb', and 'VGRD:500 mb'
                   in the same grib2 file.
        outdir   - A string specifying the directory to save the files retrived
        
    """

    # Check if the outdir exists. If not, create it.
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        print("Created new directory: %s" % outdir)

    # Download for all requested hours and forecast hours
    for h in hours:
        for f in fxx:

            # Rename the downloaded file based on the info from above
            if more_vars == 0:
                # e.g. HRRRfromPando_20170310_h00_f00_TMP_2_m.grib2
                outfile = '%s/%sfromPando_%s_h%02d_f%02d_%s.grib2' \
                       % (outdir, model.upper(), DATE.strftime('%Y%m%d'), h, f, variable.replace(':', '_').replace(' ', '_'))
            else:
                # e.g. HRRRfromPando_20170310_h00_f00_TMP_2_m-and-5.grib2 (if more_vars=5)
                outfile = '%s/%sfromPando_%s_h%02d_f%02d_%s-and-%s.grib2' \
                       % (outdir, model.upper(), DATE.strftime('%Y%m%d'), h, f, variable.replace(':', '_').replace(' ', '_'), more_vars)

            # URL to download the full grib2 file.
            # We will use the cURL comand to download the variable of interest
            # from this file using the byte range, in step 3.
            pandofile = 'https://pando-rgw01.chpc.utah.edu/%s/%s/%s/%s.t%02dz.wrf%sf%02d.grib2' \
                    % (model, field, DATE.strftime('%Y%m%d'), model, h, field, f)
            
            # URL for the grib2 .idx metadata file.
            # The metadata contains the byte range for each variable, which we
            # will need for a partial download, in Step 2.
            idxfile = pandofile+'.idx'
                            
            # 1) Open the Metadata URL and read the lines
            lines = requests.get(idxfile).text.split('\n')
            
            # Check if the variable requested is in the .idx file.
            if not any(variable in s for s in lines):
                print("\n   ERROR!!!")
                print("   Can not retrieve %s from %s." % (variable, idxfile))
                print("   Check that your variable name matches a line in the .idx file.\n")
                return

            # 2) Find the byte range for the variable requested.
            #    Need to first find which line the variable is located. Keep a count
            #    of what line we are on, gcnt, so we can get the end byte range
            #    from the next line.
            gcnt = 0
            for g in lines:
                expr = re.compile(variable)
                if expr.search(g):
                    parts = g.split(':')
                    rangestart = parts[1]
                    parts = lines[gcnt+1+more_vars].split(':')
                    rangeend = int(parts[1])-1
                    print(variable+' byte range:', rangestart, rangeend)
                    byte_range = str(rangestart) + '-' + str(rangeend)

                    # 3) When the byte range is discovered, use cURL to download.
                    try:
                        os.system('curl -s -o %s --range %s %s' % (outfile, byte_range, pandofile))
                        print('Downloaded %s \n' % outfile)
                    except:
                        print("\n   ERROR !!! Does the grib2 file exists: %s \n" % pandofile)
                        continue
                gcnt += 1

            """
            Note: If you don't give the variable string a unique enough name,
                  it will only grab the last instance of that variable.
                  For example, there are many 'TMP' variables at different levels.
                  If you set variable='TMP' it will download all the
                  fields that match TMP (i.e TMP:500 mb, TMP:700 mb) and
                  overwrite the file with the last instance. That is why you
                  need to also specify the variable abbreviation and surface
                  when you name the variable string.
            """
            
if __name__ == '__main__':
    '''
    # Example will download 2-m temperature analysis for all hours on January 1, 2018.
    download_HRRR_variable_from_pando(date(2018,1,1), 'TMP:2 m',
                                      hours=range(0, 24), fxx=[0],
                                      model='hrrr', field='sfc',
                                      more_vars=0,
                                      outdir='./')
    '''

    # === User change these parameters ================================
    # date range
    sDATE = date(2018, 8, 13)   # Start date
    eDATE = date(2018, 8, 20)   # End date (exclusive)
    
    # list of variables
    #variables = ['TMP:2 m', 'DPT:2 m', 'UGRD:10 m', 'VGRD:10 m'] 
    variables = ['HPBL:surface']
    # =================================================================

    days = (eDATE-sDATE).days
    DATES = [sDATE + timedelta(days=d) for d in range(days)]

    for variable in variables:
        for DATE in DATES:
            download_HRRR_variable_from_pando(DATE, variable,
                                            hours=range(0, 24), fxx=[0],
                                            model='hrrr', field='sfc',
                                            outdir='./')
    