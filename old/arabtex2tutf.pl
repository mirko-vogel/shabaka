#!/usr/bin/perl -w

use Encode::Arabic ':modes';
use Encode::Arabic::ArabTeX ':simple';


use Data::Dumper;
use JSON;
$|=1;

foreach $line ( <STDIN> ) {
print encode "utf8", decode "arabtex", $line;
    #chomp( $line );
    #print "$line\n";
}

