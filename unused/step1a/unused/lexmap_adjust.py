""" lexmap_adjust.py Oct 6, 2014
 Reads prevlexmap and write lexmap
 simplifying the normalized lex
"""
import sys, re,codecs

def norm_order(p1,p2):
 """ p = x or p = x#y, where x = m,f,n or ind
 Say m<f<n<ind
 """
 t = p1.split('#')
 x1 = t[0]
 t = p2.split('#')
 x2 = t[0]
 h = {'m':1,'f':2,'n':3,'ind':4}
 y1 = h[x1]
 y2 = h[x2]
 if y1 != y2:
  return y1 - y2
 return len(p1) - len(p2)

def norm_adjust(norm):
 norm = norm.rstrip(':')
 parts = norm.split(':')
 # remove dups
 partset = set(parts)
 parts1 = list(partset)
 parts2 = sorted(parts1,cmp=norm_order)
 ans = ':'.join(parts2)
 return ans

def main(filein,fileout):
 f = codecs.open(filein,"r",'utf-8')
 fout = codecs.open(fileout,"w",'utf-8')
 n = 0
 for line in f:
  n = n + 1
  line=line.rstrip('\r\n')
  try:
   (form,norm)=line.split('\t')
  except:
   print "error 1 at line",n,line
   exit(1)
  try:
   norm = norm_adjust(norm)
  except:
   print "error 2 at line",n,line
   exit(1)

  fout.write("%s\t%s\n" % (form,norm))
 f.close()
 fout.close()

if __name__=="__main__": 
 filein = sys.argv[1] #  prevnormlex.txt
 fileout = sys.argv[2] # normlex.txt
 main(filein,fileout)
