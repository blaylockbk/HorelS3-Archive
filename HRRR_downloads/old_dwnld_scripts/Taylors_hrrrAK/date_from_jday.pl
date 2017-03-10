#!/usr/bin/perl
use Time::Local;

$yr = $ARGV[0];
$yr = $yr + 2000;
$jday = $ARGV[1];
$mytime = timegm(0,0,0,1,0,$yr);
$mytimej = $mytime + ( 86400 * ($jday - 1) ) ;
#print "$yr $jday $mytime $mytimej\n";
($sec,$min,$hourz,$dayz,$monz,$yrz) = gmtime($mytimej); 
$monz = $monz + 1;
$yrz = $yrz - 100;
# printf("%02d %02d %02d %02d \n", $yrz, $monz, $dayz, $hourz);
 printf("%02d %02d\n", $monz, $dayz);

