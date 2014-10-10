<?php
/*
  simplify_lexnorm.php
  Usage php simplify_lexnorm.php lexnorm.txt lexnorm1.txt
  This changes lexnorm normalized form in certain ways.
  (a) changes forms like f#X to f
  (b) After this simplification, removes duplicate genders
     e.g., m:f:f:n => m:f:n
*/
error_reporting(E_ALL ^ E_NOTICE); // all errors except 'PHP Notice:'
$filein = $argv[1]; // input file, e.g. lexnorm.txt
$fileout = $argv[2]; // output file, e.g. lexnorm1.txt

$fpin = fopen($filein,"r") or die("Cannot open $filein\n");
$fpout = fopen($fileout,"w") or die("Cannot open $fileout\n");
$n = 0;
while (!feof($fpin)) {
 $n = $n + 1;
 $line = fgets($fpin);
 $line = trim($line); 
 if ($line == '') {
  // skip blank lines.
  // last line is usually blank 
  continue;
 }
 // $line is tab-delimited with 4 fields:
 $parts = preg_split('/\t/',$line); 
 // The fields are:
 // $L == $parts[0]
 // $key1 == $parts[1]
 // $key2 == $parts[2]
 // $norm = $parts[3]
 $norm = $parts[3];
 // $norm is colon-delimited with variable number of fields
 $fields = preg_split('/:/',$norm);
 // Loop through the fields and simplify to gender
 for($i=0;$i<count($fields);$i++) {
  $field = $fields[$i];
  // $field should have form 
  // (a) X or (X = m,f,n,ind)
  // (b) X#Y , Y = a non-empty string not containing '#'
  // check for error in $field
  if (preg_match('/#.*#/',$field)) {
   echo "norm error 1 $field\n";
  }
  $fparts = preg_split('/#/',$field);
  // There will be either 1 or 2 parts to the field
  // First is gender (or ind)
  $gender = $fparts[0];
  if (!preg_match('/(m|f|n|ind)$/',$gender)) {
   echo "norm error 2 $field at line $n\nline = $line\n";
  }
  // replace $field with $gender
  $field = $gender;
  // put new field back in $fields array
  $fields[$i] = $field;
 }
 // Make new array $newfields by removing duplicates (if any) from $fields
 $newfields = array_unique($fields);
 // Make a string from $newfields, with ':' as separator
 $newnorm = join(':',$newfields);
 // Put new normalized back into the parts
 $parts[3] = $newnorm;
 // Join the parts, with tab as separator
 // For some reason, tab neads representation as "\t", not '\t' in join
 $newline = join("\t",$parts);
 // Write the new line
 fwrite($fpout,"$newline\n");
}
fclose($fpin);
fclose($fpout);
?>
