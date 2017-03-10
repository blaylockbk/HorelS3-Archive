#!/usr/bin/perl
use Time::Local;

$yr = $ARGV[0];
$mo = $ARGV[1];
$mo=$mo-1;
$dy = $ARGV[2];
$yr = $yr + 2000;
$mytime = timegm(0,0,0,$dy,$mo,$yr);
($sec,$min,$hour,$mday,$mon,$year,$wday,$jul,$isdst) = gmtime($mytime);
print "$yr $mytime $mytimej $mon $jul \n";

