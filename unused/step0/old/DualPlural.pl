#!/usr/bin/perl -w
#lgtab/DualPlural.pl
# 2008-02-28
#read -i input -o output
# reads lines of infile 
# lines like: sItormile	sItormilA	245092	f1d  (tab-separated)
# retrieve datakey stem L inflectid
# use L to get record from lgtab
# write to output file an update record, updating stem and adding inflectid.
# and print it to output

use Getopt::Std;
use strict;

use DBI;
my  $dbh = DBI->connect ("DBI:mysql:sanskrit-lexicon:mysql.rrz.uni-koeln.de",
			 "sanskrit-lexicon","IwdsgmVns")
             || die "Could not connect to database: "
             . DBI-> errstr;
our($opt_i,$opt_o);
getopt ('io');
if ((!$opt_o) || (!$opt_i)) {
    die "usage: perl DualPlural.pl -i INFILE -o OUTFILE\n";
}
print "-o -> $opt_o\n";
print "-i -> $opt_i\n";

my $fileout;
my $n=0;
my $x;
$fileout=$opt_o;
my $filein = $opt_i;
open(INFILE,  $filein)   or die "Can't open $filein: $! \n";
open(OUTFILE, ">$fileout") or die "Can't open $fileout: $!";
my $true = 0;
my $false = 1;
my $more=$true;
my ($lnum,$keym,$data,$keyin,$stem,$inflectid);
my $nout = 0;
my $numlines = 0;
while (($more == $true) && ($x=<INFILE>)){
    chomp($x);
    if (!($x =~ /^([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)$/)) {
	print STDERR "line skipped: $x\n";
    }else {
	$keyin = $1;
	$stem = $2;
	$lnum = $3;
	$inflectid = $4;
	process_line($keyin,$stem,$lnum,$inflectid);
	$numlines++;
	if (2 < $numlines) {
#	    $more = $false; # dbg
	}
    }
}
close(OUTFILE);
close(INFILE);
$dbh->disconnect;
print STDERR "$numlines  updates written to $fileout\n";
exit;
sub process_line {
    my $keyin = $_[0];
    my $stem = $_[1];
    my $lnum = $_[2];
    my $inflectid = $_[3];
#    my ($keyin,$stem,$lnum,$inflectid) = shift;
#    print STDERR "DBG: keyin = $keyin, stem = $stem, lnum = $lnum, inflectid = $inflectid \n";
    # find previous line satisfying the regular expression
    #    print "matching id = {$lnum}\n";
    # May 20,2008. $lnum converted to 10.2 format
    my $lnum1 = sprintf("%010.2f",$lnum);
    my $id = "MW-$lnum1";
    my $sql = "select `data` from `lgtab` WHERE `id` =  \"$id\" ";
    my $dbhout = $dbh->prepare($sql);
    $dbhout->execute;
    my $data;
    if (!($data=$dbhout->fetchrow_array)) {
	print STDERR "ERROR (not found): $keyin,$stem,$lnum,$inflectid\n";
	return;
    }
    chomp($data);
    my $dictkey = "NA";
    if ($data =~ /<dictkey>(.*?)<\/dictkey>/) {
	$dictkey = $1;
    }
    if (!($dictkey eq $keyin)) {
	print STDERR "ERROR (dictkey=$dictkey): $keyin,$stem,$lnum,$inflectid: $data\n";
	return;
    }
    $data =~ s/<stem>.*?<\/stem>/<stem>$stem<\/stem><inflectid>$inflectid<\/inflectid>/;
    print OUTFILE "Update\n";
    print OUTFILE "<id>$id<\/id>\n";
    print OUTFILE "$data\n";
    
}


