readme.txt for lexnorm/step0
Oct 6, 2014
Jim Funderburk

The lexicalgrammar file structure was designed to contain grammatical 
information for headwords in a lexicon.  This work was begun in 2008 by
Peter Scharf and Jim Funderburk, with a contribution by Chandrashekar.

The work in this repository uses the xml data structure of the original work, 
as defined in the document type definition file lexicalgrammar.dtd.  The 
programmatic construction of lexicalgrammar.xml has been rewritten, with
some simplifications, in the Python programming language. 

The current lexicalgrammar data structure has provision to handle only Sanskrit
headwords which are substantives (nouns, adjectives)  or indeclineables; verbs
are not included.

The data structure was designed to be applicable for headwords drawn from any
lexicon. However, only the Monier-Williams (1899) dictionary (MW) has been used as a source of headwords, since this is the only dictionary with markup sufficiently complete to permit programmatic extraction of grammatical information. 

The lexicalgrammar.xml file contains a record for essentially every record which is a nominal; a more complete description of record selection is provided below.  As currently constituted, this file is constructed from two inputs: mw.xml and DualPlural.txt.  Some of the markup (to identify pronouns, cardinal numbers, and loan words) in mw.xml was added as metadata to mw.xml precisely for the purpose of lexicalgrammr.xml.  The non-inclusion in mw.xml of the meta-data present in DualPlural.txt is essentially an historical accident.

The construction of lexicalgrammar.xml is done by a single python program,

python26 lexicalgrammar_dp.py <mw.xml> DualPlural.txt lexicalgrammar.xml
<mw.xml> here indicates the file-system location of mw.xml, which is available
in the mwxml.zip download at url 
http://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2014/web/webtc/download.html

The redo.sh file in this repository contains, for <mw.xml>, the relative path
../../../pywork/mw.xml  on the system where this was run.  You will likely
need to replace this relative path with one appropriate for your system.

The use of python26 identifies the version of the Python interpreter  on the
system where this was run, and you may need to change this on your system.
Python version 2.7 will run fine.  To run with a version 3 of Python, you
would likely need to change the lexicalgrammar_dp.py.

One intended use of lexicalgrammar.xml was the creation of declensions. For the vast majority of nominal headwords (such as those whose stem ends in a short-vowel), the information in lexicalgrammar.xml is sufficient input for proper declension.  However, for a significant minority, additional information is required. For nominals whose stem ends in a consonant, including present active participles and future participles, further information is required.  Two attempts has been made to carry forth this declension constructure. The results are available
in the two inflected forms displays at http://www.sanskrit-lexicon.uni-koeln.de/.  While useful, neither of these constructions is completely accurate.

Here is description of the fields in lexicalgrammar.xml, as drawn from 
lexicalgrammar.dtd:
     dict has the constant value MW as its text.
     dictref contains the value of the <L> element for MW; this
       is a number, possibly with a decimal point: xxxxxxx.xx
     dictkey element has the dictionary key1. dictkey is deriveable
          from dictkey2, but the algorithm is complicated.
     dictkey2 has the 'expanded' key2 from dictionary in
          a CDATA structure. This is so the xml structures that
          may appear do not need to be specified in this DTD.
     dictlex element uses a CDATA structure to
      contain the lexical information from the dictionary. This is
      so that the xml structures that may appear do not need to be
      specified in this DTD.
     stem has default value equal to the value of 'dictkey'
     inflectid, if present, indicates that key1(2) is an inflected item.
      It's value is the Scharf-style (e.g., m1d)  inflection type of key1.
     loan, if present, indicates the word is a loan word and is
          indeclineable in Sanskrit.

Here is a description of the MW record selection and other logic of the
.py program:

There is one record for each record of monier.xml, PROVIDED one of the
 following conditions holds:
 (a) The record contains a <pron>stem</pron> element
 (b) The record contains a <card>stem</card> element
 (c) The record contains a <lex> element which satisfies one of the conditions:
  (i) the lex element has no type attribute (This is the most common case)
  (ii) the lex element has a type attribute which is one of
       hw,hwifc, hwalt, extra
       Note 1: the dtd for monier.xml allows the following attributes for lex:
         <!ATTLIST lex type (inh | phw | hw | hwifc | hwalt | nhw | hwinfo | 
           part | extra) #IMPLIED >
       Thus, lex elements are excluded which have type attribute with value
          of phw,nhw, hwinfo, part
       Note 2: Possibly, we should alter the logic in two ways:
        - exclude <lex type="inh"> elements (since they should be redundant)
        - include <lex type="part"> elements (part = participle)  This however
          seems to occur within root records, so maybe it is proper to exclude.
  (iii) the lex element has type="inh" and the contents of the element
        contains pattern '<ab>(pl|du|sg)[.]' 
        Comment: As of this 2014 writing, I question whether such records
        should be appear in this file; there are only 64 such records currently.

For such a record of MW, the lexical grammar file has a record with fields:
  dict = MW
  dictref = L (lnum, formatted as %010.2f)
  dictkey = key1
  dictkey2 = key2.  This item is included because (for MW, at least) it
       contains pada information which is believed to be relevant for
       some declensions (such as whether an internal sandhi change, such
       as 'ena' to 'eRa', is required).
  dictlex = concatenation of all acceptable lex elements within the record
  stem = (a) contents of <pron> element, if present; else
         (b) contents of <card> element, if present; else
         (c) key1
  lexid = 'pron' if pron element present, else
          'card' if card element present, else
          there is no lexid element
  loan  An empty element present if the <loan/> element present in mw record,
        else there is no loan element
Note: there is another optional element 'inflectid' in dtd for
lexicalgrammar; it is set for  records in DualPlural.txt.

The DualPlural.txt file contain 4 pieces of data:
  key1, stem, L, inflectid.

In MW, these records have the headword (key1) as a dual or plural inflected
form; by contrast, key1 is the inflectional stem for most MW records.
So, the DualPlural...txt file contains the inflectional stem and also 
provides the inflectional id (gender-case-number, e.g., 
m1d = masculine-1st-singular) of key1.  The prior lgtab record is updated
by (a) replacing the extant <stem> contents with the {stem} value from 
the DualPlural...txt file, and (b) inserting (after  <stem>{stem}</stem>) 
an <inflectid>{inflectid}</inflectid> element.
