readme.txt for lexnorm/step1a
Oct 6, 2014
Jim Funderburk
Oct 8, 2014
  Per Marcis request, the key2 value is now the 3rd element on each line.
  In the examples in this readme file, these key2 values are not shown.
  Also, since this data comes from mw.xml (and not monier.xml), the
  accents FOLLOW the vowel (in monier.xml accents PRECEDE the vowel).
  This is for consistency with a change in Scharf's SLP1 protocol.

Oct 10, 2014
 Provide PHP program 'simplify_lexnorm.php' to simplify the lexnorm output to
 just contain m,f,n,ind.
 php simplify_lexnorm.php lexnorm.txt lexnorm1.txt
--------------------------

The files lexnorm.txt  contains a normalization of the grammatical information 
present in lexicalgrammar.xml (which is described in file step0/readme.txt of 
this repository). File lexnorm.txt (and several other files) are created by the 
Python program process1a.py (see redo.sh):

python26 process1a.py lexmap.txt ../step0/lexicalgrammar.xml lexnorm.txt lexnorm-other.txt error.txt message.txt > normlog.txt

The grammatical information in lexicalgrammar.xml is in the complicated markup form as it appears in mw.xml. As a simple example, under headword akAma in
lexicalgrammar.xml, the grammatical information appears as:
`<lex>mf<p><s>A</s></p>n.</lex>`
This is simplified by process1a in two steps.
First, a sequence of regular expression substitutions reduces this to:
<lex>mf<s>A</s>n</lex>
Then, this process1a looks up this reduced form in the lexmap.txt input file,
finding 
<lex>mf<s>A</s>n</lex>	m:f#A:n:
Finally the normalized form is plucked out.
m:f#A:n:
Then, this normalized form, along with the lnum and key1 values from 
lexicalgrammar.xml are printed as a line in the lexnorm.txt output file,
using a tab-delimited format:
232	akAma	m:f#A:n:

The regular expression simplification details are shown in the 
lex_adjust and lex_adjust1 functions of process1a.py.

For those records of lexicalgrammar.xml identifed as pronouns, cardinal numbers,
loan words, or having an inflection id (see step0/DualPlural.txt), the records 
are output to lexnorm-other.txt (283 entries as per 15/10/2014). Here is a sample:
5	a	LEXID=pron,STEM=idam
886	agnAmarutO	INFLECTID=m1d,STEM=agnAmarut
14953	ayuta	LEXID=card,STEM=ayuta
243121	sArisTAKA	LOAN


The error.txt file contains records for which the simplification procedure
fails; currently, there are no such failures.

The normlog file contains various informational messages. Notably, it
identifies 61 records which were skipped. For instance:
Skipping: 824	agasti	NO ADJUSTED INFL DATA: <lex type="inh">m. <ab>pl.</ab></lex>

The message.txt file contains some useful summary information about 
lexnorm.txt. For instance, the first line is:
 64745 m <lex>m</lex>
indicating that the simplified grammatical information was '<lex>m</lex>',
normalized to 'm:', for 64745 lexicalgrammar.xml records. 
In other words, message.txt shows a frequency distribution for lexmap.txt,
sorted in descending order of frequency.

Moreover, for those lexmap forms occurring fewer than 10 times, all of
the instances are shown. For instance:
     9 m:f#U:n: <lex>mf<s>U</s>n</lex>
>>> 11479	patayAlu	m:f#U:n
>>> 143546	bahugu	m:f#U:n
>>> 158015	mayoBu	m:f#U:n
>>> 158017	mayoBU	m:f#U:n
>>> 180432	lakzaRoru	m:f#U:n
>>> 180509	lakzmaRoru	m:f#U:n
>>> 186795	varatanu	m:f#U:n
>>> 212588	SaPoru	m:f#U:n
>>> 240405	sahoru	m:f#U:n

Thus, in these 9 MW records, the simplified grammatical information was
'<lex>mf<s>U</s>n</lex>', with corresponding normalized form 'm:f#U:n:'.

Note on normalized forms.
The normalized forms are a colon (':') separated list of 1 or more items.
Each item has either the form 'x' or 'x#y', where 'x' is one of
'm', 'f', 'n', 'ind'. 'y', if present, is additional information which
MW shows for the declension.  In the most common cases, this is of the
form 'f#I'; when the headword stem ends in 'a', this indicates that the feminine
stem is to be formed from the headword stem by replacing the 'a' with 'I'.
However, for some other forms of 'y', a more complex transformation of
the given headword stem may be required.  Thus, for the purposes of
generating declensions, more work is required to know how to interpret 'y' in
the x#y forms.


Note on key2:
 To simplify the output, the sometimes rather complex 'key2' value from MW
was not printed.  However, it is believed that 'key2' may be useful in the
declension of some words.

Note on simplifying lexicalgrammar.
Perhaps the 'normalized' form should replace the full lexical information in
field 'dictlex' of lexicalgrammar.xml.
