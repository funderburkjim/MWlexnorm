
The MWlexnorm repository provides material for generation of declensions
for the nominal forms implied by the Monier-Williams Sanskrit-English Dictionary
of 1899.  It is based on the digital edition of this dictionary available at
the [Cologne Sanskrit Lexicon website](http://www.sanskrit-lexicon.uni-koeln.de/).

This work was begun approximately 2008 by Jim Funderburk, Malcolm Hyman, and
Peter Scharf. The current form of the work as represented in this repository
is due to Funderburk.

### Statement of the problem

Consider a particular example, the word *guru*.  

Here is how the underlying printed edition looks for the first part of the entry for *guru*:
![image](https://cloud.githubusercontent.com/assets/6393033/10209289/d49cc7e4-67a7-11e5-8146-a23a8aa5c3b4.png)

Here is a link to a display of [guru](http://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2014/web/webtc/indexcaller.php?key=guru) from the Cologne digital
edition.

For our purposes here, we are interested in only a small part of the 
information about this word available in the dictionary:

गुरु mf(वी)n. 

This tells us that guru is a Sanskrit word with inflected forms in each of
the three genders (masculine, feminine, and neuter).

When we look at part of the underlying xml structure of the digitization upon
which the display is based, we see the following arcane structure:
```
<H1><h><hc3>110</hc3><key1>guru</key1><hc1>1</hc1><key2>gur/u</key2></h><body> <lex>mf<p><s>vI</s></p>n.</lex> 
```

