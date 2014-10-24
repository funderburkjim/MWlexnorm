#!/usr/bin/perl -w
#lexicalgrammar.pl
# 01-25-2008 ejf
# usage 
# constructs lexicalgrammar.xml file
#reads table 'monier' "in order"
# May 2008, process 'card' and 'pron'
# Nov 25, 2012 ejf. Slight adjustment regarding test to exclude type="inh"
# June 16, 2013 ejf. Read mwupdate/monier.xml rather than database.

#use DBI;
#use FindBin;
#use lib '../../libutil';
#use DBIconnect;
#my $dbh = DBIconnect();

$| = 1;

for (my $i=0; $i < @ARGV; $i++) {
    print "$i: $ARGV[$i] \n";
}
if (!$ARGV[0]) {
    die "usage: perl lexicalgrammar.pl monierXML XMLOUT (optional MAX)\n";
}
my $filein = $ARGV[0];
my $fileout = $ARGV[1];
my $max = $ARGV[2];
if (!($max)) {
 $max=1000000; # more than the number of records
}
print "max = $max\n";

my $line;
my $more= 1;
my ($nmax,$n);
my (@keydat, $key, $lnum, $data);
my $dbg=0; #0 for no dbg, 1 for dbg
my $numrec=0;
$nmax=0;
$lnum = 0;
my $nfound;
open(OUTFILE, ">$fileout") or die "Can't open $fileout: $!";
print OUTFILE '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
print OUTFILE '<!DOCTYPE lexicalgrammar SYSTEM "lexicalgrammar.dtd">' . "\n";
print OUTFILE '<lexicalgrammar>' . "\n";
$nfound=do_process1($filein);
print STDERR "$nfound\n";
print OUTFILE '</lexicalgrammar>' . "\n";
close(OUTFILE);
#$dbh->disconnect;
exit 0;
sub do_process1 {
    my $filein = $_[0];
    my $sql;
    my $sql1;
    my $lnum1;
    my $nfound=0;
    my $nfound1=0;
    my $subdata;
    open(INFILE, "<$filein") or die "Can't open $filein: $!";

    #$sql1 = "select `data` from `monier` ORDER BY `lnum` LIMIT 0,$max";
    #my $dbhout;
    #$dbhout = $dbh->prepare($sql1);
    #$dbhout->execute;
    $nfound1=0;
    #while(my($data1)=$dbhout->fetchrow_array) {
    while($data1 = <INFILE>) {
	chomp($data1);
        if(! ($data1 =~ /^<H/)) {next;}
#	print "$data1\n";
	$nfound1++;
	$subdata = get_subdata($data1);
	if ($subdata ne "") {
	    # print subdata
	    print OUTFILE "$subdata\n";
	    $nfound++
	}
    }
    close(INFILE);
    $nfound ;
}

sub get_subdata {
    my $datain = shift;
    my $data1 = $datain;
    my $line="";
    my $match;
    my $lexdata;
    my $lextype;
    my $dict = "MW";
    my $dictref; # L
    my $dictkey2;
    my $dictkey; # key1
    my $loan = ""; # normally not present
    my $lexid = ""; # normally not present
    my $dictlex = "";
    # key1
    $data1 =~ /<key1>(.*?)<\/key1>/;
    $data1 = $'; # string after match
    $dictkey = $1;

    # key2
    $data1 =~ /<key2>(.*?)<\/key2>/;
    $dictkey2 = $1;
    $data1 = $'; # string after match

    if ($data1 =~ /<loan\//) {
	$loan = $&;
	$data1 = $'; # string after match
    }
    # search through all lexes, keeping only those we want, namely
    # <lex>xxx</lex> or
    # <lex type="inh">xxx</lex> or
    # <lex type="hw">xxx</lex> or
    # <lex type="hwalt">xxx</lex> or
    # <lex type="hwifc">xxx</lex>
    # <lex type="extra">xxx</lex>  2008-08-08
    my $noninh=0;
    # Nov 25, 2012. Changed regexp slightly
    #while ($data1 =~ /<lex([^<]*)>(.*?)<\/lex>/) {
    while ($data1 =~ /<lex([^>]*)>(.*?)<\/lex>/) {
	$match = $&;
	$data1 = $'; # string after match
	$lextype = $1;
	$lexdata = $2;
	if (($lextype eq "") || ($lextype =~ /type="hw"/) ||
	    ($lextype =~ /type="inh"/) ||
	    ($lextype =~ /type="hwifc"/) ||
	    ($lextype =~ /type="hwalt"/) ||
	    ($lextype =~ /type="extra"/)) {
	    $dictlex .= $match;
	    if (!($lextype =~ /type="inh"/)) {
		$noninh++;
	    } elsif ($lexdata =~ /<ab>pl[.]/) {
		$noninh++;
	    } elsif ($lexdata =~ /<ab>du[.]/) {
		$noninh++;
	    } elsif ($lexdata =~ /<ab>sg[.]/) {
		$noninh++;
	    }
	    
	}
    }
    if ($noninh == 0) {
	# this causes record to be omitted in output
	$dictlex = ""; 
    }
    my $pron="";
    my $card="";
    my $stem="";
    if ($datain =~ /<pron>(.*?)<\/pron>/) {
	$pron = $&; # whole match
	$stem = $1;
	$lexid = "pron";
    }elsif ($datain =~ /<card>(.*?)<\/card>/) {
	$card = $&; # whole match
	$stem = $1;
	$lexid = "card";
    }
    # finally, get L
    $data1 =~ /<L.*?>(.*?)<\/L>/;
    $dictref = $1;
    # the 'id' in the mysql file is dict-dictref.
    # to have this appear in same order as the numeric 'L', do the following:
    $dictref = sprintf("%010.2f",$dictref);
    $data1 = $'; # string after match
    if (($dictlex ne "") || ($pron ne "") || ($card ne "")) {
	$line = "<gram>" .
	    "<dict>$dict</dict>" .
	    "<dictref>$dictref</dictref>" .
	    "<dictkey2><![CDATA[" . $dictkey2 . "]]></dictkey2>" .
	    "<dictkey>$dictkey</dictkey>" .
	    "<dictlex><![CDATA[" . $dictlex . "]]></dictlex>";
#	    "<stem>$dictkey</stem>"; # sets default stem
	if ($loan ne ""){
	    $line .= "<stem>$dictkey</stem><loan />";
	}elsif ($pron ne "") {
	    $line .= "<stem>$stem</stem><lexid>$lexid</lexid>";
	}elsif ($card ne "") {
	    $line .= "<stem>$stem</stem><lexid>$lexid</lexid>";
	}else { # usual case, set default stem
	    $line .= "<stem>$dictkey</stem>";
	}
	$line .= "</gram>"; #close the xml
    }
    $line;
}
