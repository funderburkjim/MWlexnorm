<?php
// mwupdate/lgtab1/mapnorm/2014/step1a/process1a.php
// Nov 25, 2012 ejf
// Sep 17, 2014 : Remove accents in step1a output
//   Use as input lexicalgrammar.xml (rather than mysql table lgtab)
error_reporting(E_ALL ^ E_NOTICE); // all errors except 'PHP Notice:'
/* Unneeded as reading from lexicalgrammar
$dir = dirname(__FILE__); //directory containing this php file
 $dirdocs = preg_replace('/docs\/.*$/','docs/',$dir);
 $dirphp = $dirdocs . 'php/';
require_once($dirphp . 'utilities.php');
$link = sanskrit_connect_mysql();
if (! $link) {
 die('mysql connection error: ' . mysql_error());
}
*/
$filein = $argv[1]; // normlex.txt
$filein1 = $argv[2]; // monier.xml
$fileout1 = $argv[3]; // main output
$fileout2 = $argv[4]; // excluded records (in summary form)
$fileout3 = $argv[5]; // error: un-matched records
$fileout4 = $argv[6]; // warn: warnings (of lex adjustments)

$fpout1 = fopen($fileout1,"w") or die("Cannot open $fileout1\n");
$fpout2 = fopen($fileout2,"w") or die("Cannot open $fileout2\n");
$fpout3 = fopen($fileout3,"w") or die("Cannot open $fileout3\n");
$fpout4 = fopen($fileout4,"w") or die("Cannot open $fileout4\n");

$normlex = init_normlex($filein);
$normerr = array();
global $normerr;
// $sql = "select `id`,`data` from `lgtab` ORDER BY `id`";
$more = 1;
$nrec=0;
$nrec1=0;
$nrec2=0;
$nrec3=0;
$nrec4=0;
// read lexicalgrammar.xml one line at a time
$fpin = fopen($filein1,"r") or die("Cannot open $filein1\n");
while (!feof($fpin)) {
 $lgtabline = fgets($fpin);
 if (!preg_match('/^<gram><dict>(.*?)<\/dict> *<dictref>(.*?)<\/dictref>.*<dictkey>(.*?)<\/dictkey>.*<\/gram>$/',$lgtabline,$matches)) {
  print("Skipping line: $lgtabline\n");
  continue;
 }
 $dict = $matches[1];
 $dictref = $matches[2];
 $id = "$dict-$dictref"; 
 $data = trim($lgtabline);
 list($itype,$out,$outwarn) = process_record($data,$normlex);
 $out = trim($out);
 if ($itype == 1) {
  $nrec1++;
  fwrite($fpout1,"$out\n");
 } else if ($itype == 2) {
  $nrec2++;
  fwrite($fpout2,"$out\n");
 } else if ($itype == 3) {
  $nrec3++;
  fwrite($fpout3,"$out\n");
 } else if ($itype == 4) {
  // like 1, but also write a warning
  $nrec1++;
  fwrite($fpout1,"$out\n");
  $nrec4++;
  fwrite($fpout4,"$outwarn\n");
 } else {
  echo "internal error: type=$itype\n";
  $more = 0;
 }
 $nrec++; 
 //if ($nrec > 100) {$more=0;} // dbg
}
fclose($fpin);
echo "$nrec records read from lgtab\n";
echo "$nrec1 records written to $fileout1\n";
echo "$nrec2 records written to $fileout2\n";
echo "$nrec3 records written to $fileout3\n";
echo "$nrec4 warning records written to $fileout4\n";
fclose($fpout1);
fclose($fpout2);
fclose($fpout3);
fclose($fpout4);
// write out normerrors to stdout, in format of normlex.txt
foreach($normerr as $lexadj=>$n) {
 $out = sprintf("<n>% 6d</n>\t%s\t?",$n,$lexadj);
 echo "$out\n";
}
exit(1);
function process_record($data,$normlex) {
 global $normerr;
 $datah = parse_lgtab($data);
 $key = $datah['dictkey'];
 $key2 = $datah['dictkey2'];
 //$key2 = preg_replace('|[/\\^]|','',$key2);  // remove accents
 $outarr=array();
 $outarr[]=$key;
 $outarr[]=$key2;
 if($datah['loan']) {
  $outarr[]= "LOAN";
 }
 if ($datah['lexid']) {
  $outarr[] = "LEXID=" . $datah['lexid'];
 }
 if ($datah['inflectid']) {
  $outarr[] = "INFLECTID=" . $datah['inflectid'];
 }
 $lexadj = $datah['dictlex_adj'];
 if(!$lexadj) {
  $outarr[] = "NO ADJUSTED INFL DATA: " .  $datah['dictlex'];
 }
 if(count($outarr) !=2) {
  $out = join("\t",$outarr);
  $itype=2;
  return array($itype,$out);
 }
 // try to match (adjusted) dictlex against normlex

 $norm = $normlex[$lexadj];
 $lex = $datah['dictlex'];
 
 if ($norm) {
  $outsave=$outarr;
  if ($lex == $lexadj) {
   $outarr[] = $norm;
   $out = join("\t",$outarr);
   $itype=1;
   return array($itype,$out);
  }else {
   $outarr[] = $norm;
   $out = join("\t",$outarr);
   $outwarnarr = $outsave;
   $outwarnarr[] = $lex;
   $outwarn = join("\t",$outwarnarr);
   $itype=4;
   return array($itype,$out,$outwarn);
  }
 }
 // error condition: lexadj unknown
 $outarr[] = $lexadj;
 $outarr[] = $lex;
 $out = join("\t",$outarr);
 $itype=3;
 // also post in normerr
 $n = $normerr[$lexadj];
 $n++;
 $normerr[$lexadj]=$n;
 
 return array($itype,$out);
}
function parse_lgtab($data) {
 // parses xml into a hash table
 $ans=array(); // hash
 $regex = '|^<gram><dict>(.*?)</dict> *<dictref>(.*?)</dictref>' .
          ' *<dictkey2><!\[CDATA\[(.*?)\]\]></dictkey2> *<dictkey>(.*?)</dictkey>' .
	  ' *<dictlex><!\[CDATA\[(.*?)\]\]></dictlex> *<stem>(.*?)</stem>(.*?)</gram>$|';
 if (!preg_match($regex,$data,$matches)) {
  echo "parse_lgtab error: $data\n";
  exit(1);
 }
 $ans['dict']=$matches[1];
 $ans['dictref']=$matches[2];
 $ans['dictkey2']=$matches[3];
 $ans['dictkey'] = $matches[4];
 $ans['dictlex']=$matches[5];
 $dictlex = $ans['dictlex'];
 $ans['dictlex_adj'] = lex_adjust($dictlex);
 $ans['stem'] = $matches[6];
 $rest = $matches[7];
 if(preg_match('/<loan/',$rest)) {
  $ans['loan']=TRUE;
 }
 if(preg_match('|<lexid>(.*?)</lexid>|',$rest,$matches)) {
  $ans['lexid']=$matches[1];
 }
 if(preg_match('|<inflectid>(.*?)</inflectid>|',$rest,$matches)) {
  $ans['inflectid']=$matches[1];
 }
 return $ans;
}
function lex_adjust($lex) {
 $ans = trim($lex);
 $ans = preg_replace("|\r|","",$ans);
 $ans = preg_replace('|<lex type="inh">.*?</lex>|','',$ans);
 $ans = preg_replace('|<lex type="hwalt">|','<lex>',$ans);
 $ans = preg_replace('|<lex type="hw">|','<lex>',$ans);
 $ans = preg_replace('|<lex type="hwifc">|','<lex>',$ans);
 $ans = preg_replace('|[ ~]mfn|','mfn',$ans); // Dec 18, 2012
 return $ans;
}
function init_normlex($filein){
 $ans = array(); // 
 $lines = file($filein,FILE_SKIP_EMPTY_LINES);
 echo count($lines) . " read from $filein\n";
 foreach ($lines as $line) {
  list($count,$form,$norm) = preg_split("/\t/",$line);
  $form = trim($form);
  $ans[$form]=$norm;
 }
 return $ans;
}
?>
