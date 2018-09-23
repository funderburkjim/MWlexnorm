# -*- coding: utf-8 -*-
""" lexcat2.py
  derive lexnorm file from revised mw.xml
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
 def __init__(self,L,key1,key2,lexnorm):
  (self.lnum,self.key1,self.key2,self.lexnorm) = (L,key1,key2,lexnorm)
  
 def toString(self):
  s = '\t'.join([self.lnum,self.key1,self.key2,self.lexnorm])
  return s

def key2_adjust(x):
 x = x.replace(u'—','-')  # mdash with hyphen
 x = x.replace('/','') # remove accents
 x = x.replace('^','')
 x = x.replace('\\','')
 x = x.replace('<srs>','')
 x = x.replace('<sr>','')
 return x

def init_lexnorm(line):
 """ line is a line of mw.xml
   return a Lexnorm record OR None
 """
 line = line.rstrip('\r\n')
 if not line.startswith('<H'):
  return None
 lexparts1 = re.findall(r'<info lex=.*?/>',line)
 lexparts1 = [p for p in lexparts1 if p != '<info lex="inh"/>']
 lexparts2 = re.findall(r'<info lexcat=.*?/>',line)
 if (len(lexparts1)==0) and (len(lexparts2) == 0):
  return None
 m = re.search(r'<key1>(.*?)</key1>',line)
 key1 = m.group(1)
 m = re.search(r'<key2>(.*?)</key2>',line)
 key2 = m.group(1)
 key2 = key2_adjust(key2)
 m = re.search(r'<L>(.*?)</L>',line)
 L = m.group(1)
 if (lexparts1!=[]) and (lexparts2!=[]):
  print("ERROR: both kinds of lex parts",L,key1)
  exit(1)
 if len(lexparts1)>1:
  print("too many lex:",L,key1)
  exit(1)
 if len(lexparts1) == 1:
  part = lexparts1[0]
  m=re.search(r'<info lex="(.*?)"/>',part)
  lexnorm = m.group(1)
 elif len(lexparts2) == 1:
  part = lexparts2[0]
  m=re.search(r'<info lexcat="(.*?)"/>',part)
  lexnorm = m.group(1)
 else:
  print("ERROR 3:",L,key1)
  exit(1)
 lexnorm = lexnorm.replace('/','')
 rec = Lexnorm(L,key1,key2,lexnorm)
 return rec
if __name__ == "__main__":
 filein = sys.argv[1] # mw.xml
 fileout = sys.argv[2] # lexnorm-all.txt
 fout = codecs.open(fileout,"w","utf-8",fileout)
 with codecs.open(filein,"r","utf-8") as f:
  for line in f:
   rec = init_lexnorm(line)
   if rec != None:
    fout.write('%s\n' % rec.toString())

