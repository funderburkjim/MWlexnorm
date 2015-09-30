""" lexcat.py
  Concatenate the two lexnorm files from lgtab, and
  make the result in lnum order.
  Sep 20, 2015
"""
import sys,re,codecs

class Lexnorm(object):
 """
  The format of a line of lexnorm.txt is now 4 tab-delimited fields:
  lnum, key1, key2, lexinfo
  And, the lexinfo field has form of 1 or more colon-delimited fields, each
  of which has one of two forms:
  gender OR  gender#ending
 """
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line = line
  (self.lnum,self.key1,self.key2,self.lexnorm) = re.split('\t',line)

def init_lexnorm(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Lexnorm(x) for x in f]
 return recs

if __name__ == "__main__":
 filein = sys.argv[1] # lexnorm.txt
 filein1 = sys.argv[2] # lexnorm-other.txt
 fileout = sys.argv[3] # lexnorm-all.txt
 # There are also print statements
 lexnormrecs = init_lexnorm(filein)
 lexnormrecs1 = init_lexnorm(filein1)
 recs = lexnormrecs + lexnormrecs1  # concatenate lists
 recs1 = sorted(recs,key=lambda(rec):float(rec.lnum))
 print len(lexnormrecs),len(lexnormrecs1),len(recs1)
 with codecs.open(fileout,"w","utf-8",fileout) as f:
  for rec in recs1:
   f.write("%s\n" % rec.line)

