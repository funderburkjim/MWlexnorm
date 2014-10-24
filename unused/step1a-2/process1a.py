""" process1a.py Sep 27, 2014
 Construct step1a.txt from normlex.txt and lexicalgrammar.xml.
 Ancillary outputs are exclud.txt, error.txt, and warn.txt
 Mimics process1a.php
"""
import sys, re,codecs

def  process1a(filein1,fileout1,fileout2,fileout3,fileout4,normlex):
 fileouts = [fileout1,fileout2,fileout3,fileout4]
 fouts = [codecs.open(fileout,"w",'utf-8') for fileout in fileouts]
 f = codecs.open(filein1,"r",'utf-8')
 nrecs = [0 for x in fileouts] # records written
 normerrs = {}  # errors (unmatched lexes)
 n = 0
 for lgtabline in f:
  lgtabline = lgtabline.rstrip('\r\n')
  m = re.search(r'^<gram><dict>(.*?)</dict> *<dictref>(.*?)</dictref>.*<dictkey>(.*?)</dictkey>.*</gram>$',lgtabline)
  if not m:
   #print "Skipping line:",lgtabline
   continue
  n = n + 1
  if n > 1000000:
   print "dbg stop after n = %s" % n
   break
  dictcode = m.group(1)
  dictref = m.group(2)
  idcode = "%s-%s" %(dictcode,dictref)
  data = lgtabline
  tup = process_record(data,normlex,normerrs)
  itype = tup[0]
  out = tup[1]
  i = itype - 1
  nrecs[i] = nrecs[i] + 1
  if i != 3:
   fouts[i].write("%s\n" % out)
  else:
   fouts[0].write("%s\n" % out)
   nrecs[0] = nrecs[0] + 1
   #also, warning message
   fouts[i].write("%s\n" % tup[2])
   #fouts[i].write("%s\n\n" % data)
   #if nrecs[i] > 10:
   # print "DBG stop. Too many errors"
   # break
 f.close()
 for fout in fouts:
  fout.close()
 print "%s records processed from %s" % (n,filein1)
 for i in xrange(0,len(fileouts)):
  print "%s records written to file %s" %(nrecs[i],fileouts[i])
 n2=0
 for dictkey in iter(normlex):
  rec=normlex[dictkey]
  if not rec.used:
   n2 = n2 + 1
   print 'normlex unused: ',(rec.n,rec.form,rec.norm)
 if n2 == 0:
  print 'All normlex records used'
 else: 
  print "%s normlex records not used" % n2
 # unmatched lexes print to stdout
 for lexadj in iter(normerrs):
  out = "%6d: %s" %(normerrs[lexadj],lexadj)
  print out

def lex_adjust(lex):
 ans = lex.rstrip()
 ans = re.sub(r'\r','',ans) # probably done by prior rstrip
 ans = re.sub(r'<lex type="inh">.*?</lex>','',ans)
 ans = re.sub(r'<lex type="hwalt">','<lex>',ans)
 ans = re.sub(r'<lex type="hw">','<lex>',ans)
 ans = re.sub(r'<lex type="hwifc">','<lex>',ans)
 ans = re.sub(r'[ ~]mfn','mfn',ans)  # Dec 18, 2012
 #print "lex_adjust: %s  ==>  %s" %(lex,ans)
 return ans

class Lgtab(object):
 def __init__(self,data):
  m = re.search(r'<dict>(.*?)</dict> *<dictref>(.*?)</dictref>',data)
  if not m:
   print "Lgtab parsing error 1",data
   exit(1)
  self.dict = m.group(1)
  self.dictref = m.group(2)
  m = re.search(r'<dictkey2><!\[CDATA\[(.*?)\]\]></dictkey2>',data)
  if not m:
   print "Lgtab parsing error 2",data
   exit(1)
  self.dictkey2 = m.group(1)
  m = re.search(r'<dictkey>(.*?)</dictkey>',data)
  if not m:
   print "Lgtab parsing error 3",data
   exit(1)
  self.dictkey = m.group(1)
  m = re.search(r'<dictlex><!\[CDATA\[(.*?)\]\]></dictlex>',data)
  if not m:
   print "Lgtab parsing error 4",data
   exit(1)
  self.dictlex = m.group(1)
  # compute adjusted dictlex
  self.dictlex_adj = lex_adjust(self.dictlex)
  m = re.search(r'<stem>(.*?)</stem>(.*?)</gram>',data)
  if not m:
   print "Lgtab parsing error 5",data
   exit(1)
  self.stem = m.group(1)
  rest = m.group(2)
  self.loan = False
  self.lexid = None
  self.inflectid = None
  m = re.search(r'<loan',rest)
  if m:
   self.loan = True
  m = re.search(r'<lexid>(.*?)</lexid>',rest)
  if m:
   self.lexid = m.group(1)
  m = re.search(r'<inflectid>(.*?)</inflectid>',rest)
  if m:
   self.inflectid = m.group(1)

def process_record(data,normlex,normerrs):
 datah = Lgtab(data)
 outarr = []
 outarr.append(datah.dictkey)
 outarr.append(datah.dictkey2)
 if datah.loan:
  outarr.append("LOAN")
 if datah.lexid:
  outarr.append("LEXID=%s" % datah.lexid)
 if datah.inflectid:
  outarr.append("INFLECTID=%s" % datah.inflectid)
 lexadj = datah.dictlex_adj
 if not lexadj:
  outarr.append("NO ADJUSTED INFL DATA: %s" % datah.dictlex)

 if len(outarr) != 2:
  out = "\t".join(outarr)
  itype=2
  return (itype,out)
 #try to match (adjusted) dictlex against normlex
 lex = datah.dictlex
 if lexadj in normlex:
  norm=normlex[lexadj].norm
  outsave = [x for x in outarr] # cheap copy of outarr
  if lex == lexadj:
   outarr.append(norm)
   out = '\t'.join(outarr)
   itype = 1
   return (itype,out)
  else:
   outarr.append(norm)
   out = '\t'.join(outarr)
   outsave.append(lex)
   outwarn = '\t'.join(outsave)
   itype = 4
   return (itype,out,outwarn)
 # error condition - lexadj unknown
 outarr.append(lexadj)
 outarr.append(lex)
 out = '\t'.join(outarr)
 itype = 3
 if lexadj not in normerrs:
  normerrs[lexadj]=0
 normerrs[lexadj] = normerrs[lexadj] + 1
 return (itype,out)

class Normlex(object):
 def __init__(self,n,t):
  self.n = n # line number of normlex file
  self.count = t[0]
  self.form = t[1].strip()
  self.norm = t[2]
  self.used = False

def init_normlex(filein):
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
 return normlex

if __name__=="__main__": 
 filein = sys.argv[1] #  normlex.txt
 filein1 = sys.argv[2] # lexicalgrammar.xml
 fileout1 = sys.argv[3] # step1a.txt
 fileout2 = sys.argv[4] # exclude.txt
 fileout3 = sys.argv[5] # error.txt
 fileout4 = sys.argv[6] # warn.txt
 normlex = init_normlex(filein)
 process1a(filein1,fileout1,fileout2,fileout3,fileout4,normlex)
