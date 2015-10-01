
:construction: **This readme.md file is under construction.**

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
<H1><h><hc3>110</hc3><key1>guru</key1><hc1>1</hc1><key2>gur/u</key2></h><body>
 <lex>mf<p><s>vI</s></p>n.</lex> 
```

From a small familiarity with Sanskrit grammar,  we can infer three
pieces of information regarding the declension of *guru*:
* *guru* can be declined as a masculine noun ending in *u*, similar to 
   a model such as *taru* (tree, Deshpande, p. 79)
   guruH, gurU, guravaH  being the nominative case forms in the singular,
   dual, and plural numbers, respectively
   * NOTE 1: These words are spelled using the SLP1 transliteration of Sanskrit.
   * Note 2: Madhav M. Deshpande, A Sanskrit Primer, 2003.
   * Note 3: We can think of *guru* as the *stem* and *m_u* as the model.
* *guru* can be declined as a neuter noun ending in *u*, based on a model
   such as *maDu* (honey, Deshpande, p. 113)
   * Note: We can think of *guru* as the *stem* and *n_u* as the model.
* *guru* can be declined as a feminine noun. However, instead of being
  declined like a feminine noun ending in *u*, such as *Denu* (cow, Deshpande, p. 80), it is declined like a feminine noun ending in long i (I), such as
  *nadI* (river, Deshpande, p. 73).
  * Note: We can think of *gurvI* as the stem, and *f_I* as the model.

From this example of गुरु mf(वी)n, we have inferred, in a systematic way,
the stem and model according to which the declensions of this word may be
computed.   

The purpose of this repository is to write computer programs that carry
forth this systematic process of deriving stem and model for all the
nominal (and indeclineable) forms in the Monier Williams dictionary.

### Summary of the general method

We have divided this stem-model derivation process into three steps; each
of the steps is carried out by programs in the three subdirectories
step0, step1a, step1b.

#### step0:  lexicalgrammar.xml

  This step identifies each record in mw.xml whose markup has information in
  the `<lex>` tag, and summarizes this information in a structure form within
  the lexicalgrammar.xml file.  For our example of *guru*, this information
  looks like:
```
<gram><dict>MW</dict><dictref>0065987.00</dictref>
<dictkey2><![CDATA[guru/]]></dictkey2>
<dictkey>guru</dictkey>
<dictlex><![CDATA[<lex>mf<p><s>vI</s></p>n.</lex>]]></dictlex>
<stem>guru</stem></gram>
```
  Most of the records like like this, but for a few subcategories, we have
  added additional information.  Here are examples.
  * pronouns. Example ayam (this)
```
<gram><dict>MW</dict><dictref>0014749.00</dictref>
<dictkey2><![CDATA[aya/m]]></dictkey2>
<dictkey>ayam</dictkey>
<dictlex><![CDATA[]]></dictlex><stem>idam</stem><lexid>pron</lexid>
</gram>
```
  * cardinal numbers. Example azwan (eight)
```
<gram><dict>MW</dict><dictref>0020173.00</dictref>
<dictkey2><![CDATA[azwan]]></dictkey2><dictkey>azwan</dictkey>
<dictlex><![CDATA[]]></dictlex><stem>azwan</stem><lexid>card</lexid></gram>
```
  * dual or plural forms (here the MW headword is a dual or plural form).
    Example Aditya-candrO (sun and moon)
```
<gram><dict>MW</dict><dictref>0023917.00</dictref>
<dictkey2><![CDATA[Aditya/--candrO]]></dictkey2><dictkey>AdityacandrO</dictkey>
<dictlex><![CDATA[<lex>m. <ab>du.</ab></lex>]]></dictlex>
<stem>Adityacandra</stem><inflectid>m1d</inflectid></gram>
```
  * present active participle. Example arcat (shining, praising)
```
<gram><dict>MW</dict><dictref>0015704.00</dictref>
<dictkey2><![CDATA[arcat]]></dictkey2><dictkey>arcat</dictkey>
<dictlex><![CDATA[<lex>mfn.</lex>]]></dictlex>
<stem>arcat</stem><lexid>prap</lexid><rootclass>arc-1</rootclass>
</gram>
```

  * future active participle. Example akarizyat (not intending to do)
```
<gram><dict>MW</dict><dictref>0000171.10</dictref>
<dictkey2><![CDATA[a-karizyat]]></dictkey2><dictkey>akarizyat</dictkey>
<dictlex><![CDATA[<lex>mfn.</lex>]]></dictlex>
<stem>a-karizyat</stem><lexid>fap</lexid><rootclass>kf</rootclass>
</gram>
```

#### step1a: lexnorm.txt and lexnorm-other.txt

This step normalizes the information of the lexicalgrammar.xml file. 
Basically, the information of the lexicalgrammar.xml file is complicated to
parse. So a simpler, more uniform representation is desireable for further
computation.  

For our *guru* example, here is the simplification present in lexnorm.txt:
```
65987	guru	guru/	m:f#vI:n
```

We present the record number (65987), the headword (guru), the extended
headword (guru/, this is the dictkey2 field of lexicagrammar.xml), and a simplified
version of the dictlex field (m:f#vI:n).

For the special categories (pronouns, cardinals, dual-plurals, present and
future participles), the simplified records are written to the lexnorm-other.txt
file.
For examples:
```
14749	ayam	aya/m	LEXID=pron,STEM=idam
20173	azwan	azwan	LEXID=card,STEM=azwan
15704	arcat	arcat	LEXID=prap,STEM=arcat,ROOTCLASS=arc-1
171.1	akarizyat	a-karizyat	LEXID=fap,STEM=a-karizyat,ROOTCLASS=kf
```

#### step1b. filter1b_el.txt, etc.

As mentioned in the *guru* example, we want to carry out the specification
of *stem* and *model*; that's what is done by step1b..
