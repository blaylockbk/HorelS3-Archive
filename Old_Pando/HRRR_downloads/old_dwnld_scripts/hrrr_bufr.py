###########################################
#
# GETBUFR.PY
#
# TREVOR ALCOTT 15 OCT 2013
# modified by jdh 5/18/15 for hrrr
# modified by bkb 5/20/15 only download hrrr for Salt Lake City (kslc) Ogden (kogd) and Provo (kpvu)
#modified by jdh 5/22/2015 for "operational" downloads
# loops through all hours, which means across a couple of utc days
#
# PROGRAM RETREIVES BUFR PROFILES FROM PSU
#
############################################

#
# INITIALIZATION
#
from string import *
from math import *
from time import *
from datetime import *
import os, sys, urllib, time, urllib2

SCRIPTDIR = '/uufs/chpc.utah.edu/sys/pkg/ldm/oper/models/hrrr_so3s/'
bufrdir='/uufs/chpc.utah.edu/sys/pkg/ldm/oper/models/hrrr_so3s/data/'
arcdir = '/uufs/chpc.utah.edu/common/home/horel-group/archive/'

models=['hrrr']
for x in range (1,len(sys.argv)):
  models.append(sys.argv[x])

# Get BUFR data
for model in models:
# if model == 'gfs':
#  sites = ['kslc','lo1','ksgu','kjac','kfca','kvel','krdd','klgu','kbzn','000298','856290']
  if model == 'hrrr':
    sites = ['kslc', 'kogd', 'kpvu']
#  else:
#    sites = ['kslc','alta','lo1','ksgu','kjac','kgpi','kvel','mhs','klgu','kbzn']
  for site in sites:
#remove all temp files jdh
    bufrfile = bufrdir + model + '_' + site + '*.buf'
    os.system('rm -f '+bufrfile)
#    hourlist = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    hourlist = [23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
#    hourlist = [21,18,15,12,9,6,3,0]
#weird problem with 2 digit hours jdh
#    hourlist = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
#    hourlist = ['10','11','12','13','14','15','16','17','18','19','20','21','22','23']
#    if model == 'nam12':
#      hourlist = [0,1]

    filelist=[]
    for hour in hourlist:
#      os.system('sleep 5')
      if model == 'hrrr':
        webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/HRRR/%02d'%hour+'/hrrr_'+site+'.buf'
#        webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/HRRR/'+hour+'/hrrr_'+site+'.buf'
#      if model == 'gfs':
#        webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/GFS/%02d'%hour+'/gfs3_'+site+'.buf'
#      if model == 'nam12':
#        if hour == 0:
#          webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/namm_'+site+'.buf'
#        else:
#          webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/nam_'+site+'.buf'
#      if model == 'nam4':
#        webfile = 'ftp://ftp.meteo.psu.edu/pub/bufkit/NAM4KM/%02d'%hour+'/nam4km_'+site+'.buf'

      localfile = bufrdir + '/' + site + 'temp%02d'%hour
#      localfile = bufrdir + '/' + site + 'temp'+hour

      try:
## bkb: ok, this is weird, but downloading the webfile using urllib produces an IOError [Errno ftp error]
## after ten files are  downloaded.
## Instead, let's "download" the file by reading the text using urllib2. This works with an addeded benefit...
## Reading the webpage text is about 50 times faster than downloading the file!!! Yippie!
        f = urllib2.urlopen(webfile)
        data = f.read()
        with open(localfile,'wb') as code:
          code.write(data)
       ## This is the old download method
       # urllib.urlretrieve(webfile,localfile)
      except:
        print 'BUFR file not found:',webfile

      if os.path.exists(localfile):
        print 'Downloaded',webfile,'as',localfile
        f=open(localfile,'r')
        ls=f.readlines()
        f.close()
        iyear=int((ls[4].split(' ')[8])[0:2])
        imonth=int((ls[4].split(' ')[8])[2:4])
        iday=int((ls[4].split(' ')[8])[4:6])
        ihour=int((ls[4].split(' ')[8])[7:9])
        print "time",iyear,imonth,iday,ihour
        archivedir = arcdir + '20%02d'%iyear + '%02d'%imonth + '%02d'%iday + '/models/' + model+'/'
        if os.path.exists(archivedir):
          archivefile = archivedir + site+'_20%02d'%iyear + '%02d'%imonth + '%02d'%iday + '%02d'%ihour + '.buf'
          os.system('mv ' + localfile + ' ' + archivefile)
        else: 
          os.system('mkdir ' + archivedir)
          os.system('mv ' + localfile + ' ' + archivefile)
# plot sounding
#  anl if analysis only
#  for if all hrrr times
	os.system('/usr/local/bin/python '+SCRIPTDIR+'sounding.py '+ model+' '+site+' 20%02d'%iyear + ' %02d'%imonth + ' %02d'%iday + ' %02d'%ihour+' anl' ) 
