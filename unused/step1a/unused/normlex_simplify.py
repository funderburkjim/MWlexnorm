""" normlex_simplify.py Oct 3, 2014
 Reads prev_normlex.txt and writes normlex.txt,
 removing the count, and simplifying the adjusted lex 
"""
import sys, re,codecs


def lex_adjust1(lex):
 ans = lex.strip()
 ans = re.sub(r'[ ~.,;]','',ans)
 ans = re.sub(r'<ab>[^<]*</ab>','',ans)
 ans = re.sub(r'<c>[^<=]*</c>','',ans)
 ans = re.sub(r'<ls>[^<]*</ls>','',ans)
 ans = re.sub(r'<srs/>|<srs1/>','',ans)
 ans = re.sub(r'<p1?><s>','<s>',ans)
 ans = re.sub(r'</s></p1?>','</s>',ans)
 ans = re.sub(r'</s>[^<]*<s>','</s><s>',ans)
 ans = re.sub(r'<cf/>|<qv/>|<see/>|<sr1/>','',ans)
 ans = re.sub(r'<b></b>','',ans)
 ans = re.sub(r'<s>([^<]*)[/-]([^<]*)</s>','<s>\g<1>\g<2></s>',ans)
 ans = re.sub(r'</lex><lex>','',ans)
 return ans

class Normlex(object):
 def __init__(self,n,t):
  self.n = n # line number of normlex file
  self.count = t[0]
  self.form = t[1].strip() # adjusted lex
  self.norm = t[2] # 
  self.used = False

def init_normlex_orig(filein):
 f = codecs.open(filein,"r",'utf-8')
 normlex={}
 n = 0
 for line in f:
  n = n + 1
  line=line.rstrip('\r\n')
  if line.startswith(';'): 
   # comment
   continue
  t = line.split('\t') # tab-delimited
  rec = Normlex(n,t)
  normlex[rec.form] = rec # rec.norm
 f.close()
 return (normlexrecs,normlexdict)

def init_normlex(filein):
 f = codecs.open(filein,"r",'utf-8')
 recs=[]
 n = 0
 for line in f:
  n = n + 1
  line=line.rstrip('\r\n')
  if line.startswith(';'): 
   # comment
   continue
  t = line.split('\t') # tab-delimited
  rec = Normlex(n,t)
  recs.append(rec)
 f.close()
 return recs

def adjust_norm(rec):
 old = rec.norm
 new = re.sub(r'([mfn])<s>(.*?)</s>','\g<1>#\g<2>',rec.form)
 new = re.sub(r'</?lex>','',new)
 new = re.sub(r'([mfn])([mfn])','\g<1>:\g<2>',new)
 rec.norm = new
 print 'adjust_norm: form=',rec.form,', old=',old,', new=',new

def main(filein,fileout):
 recs = init_normlex(filein)
 for rec in recs:
  rec.form = lex_adjust1(rec.form)
 
 fout = codecs.open(fileout,"w",'utf-8')
 formnorms = [] # for dup elimination
 ndup=0
 for rec in recs:
  if re.search('<lex>',rec.norm):
   adjust_norm(rec)
  out = "%s\t%s" % (rec.form,rec.norm)
  if out in formnorms:
   #print "duplicate formnorm:",out
   ndup = ndup + 1
  else:
   fout.write('%s\n' % out)
   formnorms.append(out)
 fout.close()
 print ndup,"duplicates removed"
if __name__=="__main__": 
 filein = sys.argv[1] #  prevnormlex.txt
 fileout = sys.argv[2] # normlex.txt
 main(filein,fileout)
