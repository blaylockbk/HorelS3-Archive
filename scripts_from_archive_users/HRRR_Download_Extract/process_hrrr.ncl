load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

begin

latS   = 30.0                      ; California
latN   = 42.0
lonW   = -128.40
lonE   = -112.00

;latS   = 33.75                      ; Riverside
;latN   = 34.25
;lonW   = -117.80
;lonE   = -117.30

;latS   = 32.55                      ; Imperial
;latN   = 33.25
;lonW   = -115.75
;lonE   = -115.25

qlat = (/latS, latN, latN, latS, latS/)
qlon = (/lonW, lonW, lonE, lonE,lonW/)
  filename = "hrrr.t13z.wrfsfcf00"
;filename = "1713917000000"

narr_file_hpbl = addfile(filename+".nc","r")
lat2d_all = narr_file_hpbl->gridlat_0
lon2d_all = narr_file_hpbl->gridlon_0

ji = region_ind (lat2d_all,lon2d_all, latS, latN, lonW, lonE)
jStrt = ji(0)      ; lat start
jLast = ji(1)      ; lat last
iStrt = ji(2)      ; lon start
iLast = ji(3)      ; lon last

hpbl_all  = narr_file_hpbl->HPBL_P0_L1_GLC0
uwnd  = narr_file_hpbl->UGRD_P0_L103_GLC0
vwnd  = narr_file_hpbl->VGRD_P0_L103_GLC0
shflx_all = narr_file_hpbl->SHTFL_P0_L1_GLC0
us_all   = narr_file_hpbl->FRICV_P0_L1_GLC0
tmp_all  = narr_file_hpbl->TMP_P0_L103_GLC0
sph_all  = narr_file_hpbl->SPFH_P0_L103_GLC0
tcld_all = narr_file_hpbl->TCDC_P0_L10_GLC0

hpbl     = hpbl_all(jStrt:jLast,iStrt:iLast)
uwnd_sfc = uwnd(0,jStrt:jLast,iStrt:iLast)
vwnd_sfc = vwnd(0,jStrt:jLast,iStrt:iLast)
uwnd_80m = uwnd(1,jStrt:jLast,iStrt:iLast)
vwnd_80m = vwnd(1,jStrt:jLast,iStrt:iLast)
shflx    = shflx_all(jStrt:jLast,iStrt:iLast)
ustar    = us_all(jStrt:jLast,iStrt:iLast)
tmp_sfc  = tmp_all(jStrt:jLast,iStrt:iLast)
sph_sfc  = sph_all(jStrt:jLast,iStrt:iLast)
tcld  = tcld_all(jStrt:jLast,iStrt:iLast)
lat2d    = lat2d_all(jStrt:jLast,iStrt:iLast)
lon2d    = lon2d_all(jStrt:jLast,iStrt:iLast)

delete(narr_file_hpbl)

;utc_date = cd_calendar(time, 0)
;str_yr = tostring(floattointeger(utc_date(:,0))) 
;str_mo = sprinti("%0.2i",floattointeger(utc_date(:,1)))
;str_dy = sprinti("%0.2i",floattointeger(utc_date(:,2)))
;str_hr = sprinti("%0.2i",floattointeger(utc_date(:,3)))

;nt = dimsizes(time)
;date_hr_string = new(nt,"string")
;date_hr_string = str_mo+"/"+str_dy+"/"+str_yr+" "+str_hr+":00:00"

;delete(utc_date)
;delete(str_yr)
;delete(str_mo)
;delete(str_dy)
;delete(str_hr)

filename_CA = filename+"_CA.nc"
;filename_LL = "hrrr_latlonCA.nc"
system("/bin/rm -f "+filename_CA)
ncdf = addfile(filename_CA,"c")
;lcdf = addfile(filename_LL,"c")
;lcdf->lat2d = lat2d
;lcdf->lon2d = lon2d
ncdf->hpbl = hpbl
ncdf->uwnd_sfc = uwnd_sfc
ncdf->vwnd_sfc = vwnd_sfc
ncdf->uwnd_80m = uwnd_80m
ncdf->vwnd_80m = vwnd_80m
ncdf->shflx = shflx
ncdf->ustar = ustar
ncdf->tmp_sfc = tmp_sfc
ncdf->sph_sfc = sph_sfc
ncdf->tcld = tcld

end
