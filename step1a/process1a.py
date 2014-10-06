""" process1a.py Sep 27, 2014
 Construct step1a.txt from normlex.txt and lexicalgrammar.xml.
 Ancillary outputs are exclud.txt, error.txt, and warn.txt
 Mimics process1a.php
 Oct 5, 2014
 Write lexnorm frequency of occurence to message.txt
 Oct 6, 2014 - simplify the printed form of dictref, 
   e.g. from 0029224.00 to 29224.
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
  dictkey = m.group(3)
  idcode = "%s-%s" %(dictcode,dictref)
  data = lgtabline
  tup = process_record(data,normlex,normerrs)
  # print "DBG: %s, %s => %s" %(dictref,dictkey,tup)
  itype = tup[0]
  out = tup[1]
  if itype == -1:
   # skip this record
   print "Skipping: %s" % out
   continue
  # continue 
  i = itype - 1
  if i != 3:
   nrecs[i] = nrecs[i] + 1
   fouts[i].write("%s\n" % out)
  else:
   fouts[0].write("%s\n" % out)
   nrecs[0] = nrecs[0] + 1
   #also, warning message
   # Oct 4, 2014: don't write this
   #fouts[i].write("%s\n" % tup[2])
   #fouts[i].write("%s\n\n" % data)
   #if nrecs[i] > 10:
   # print "DBG stop. Too many errors"
   # break
 f.close()
 print "%s records processed from %s" % (n,filein1)
 n2=0
 for dictkey in iter(normlex):
  rec=normlex[dictkey]
  if rec.count == 0:
   n2 = n2 + 1
   print 'normlex unused: ',(rec.form,rec.norm)
 if n2 == 0:
  print 'All normlex records used'
 else: 
  print "%s normlex records not used" % n2
 # unmatched lexes print to stdout
 for lexadj in iter(normerrs):
  out = "normerrs: %6d: %s" %(normerrs[lexadj],lexadj)
  print out
 # write frequency information for normlex
 fout = fouts[3]
 def normlex_cmp(key1,key2):
  v1 = normlex[key1]
  v2 = normlex[key2]
  if v1.count != v2.count:
   return -(v1.count - v2.count) 
  return len(v1.norm) - len(v2.norm)

 dictkeys = normlex.keys() # a list
 dictkeys = sorted(dictkeys,cmp=normlex_cmp)
# for dictkey in iter(normlex):
 for dictkey in dictkeys:
  rec=normlex[dictkey]
  out = "%6d %s %s" %(rec.count,rec.norm,rec.form)
  #out = "%6d,%d %s %s" %(rec.count,len(rec.instances),rec.norm,rec.form)
  fout.write("%s\n" % out)
  if rec.count < 10:
   for x in rec.instances:
    fout.write(">>> %s\n" % x)
 # message on output file lengths
 for i in xrange(0,len(fileouts)):
  print "%s records written to file %s" %(nrecs[i],fileouts[i])
 # close all output files
 for fout in fouts:
  fout.close()

def lex_adjust(lex):
 ans = lex
 ans = re.sub(r'<lex type="inh">.*?</lex>','',ans)
 ans = re.sub(r'<lex type="hwalt">','<lex>',ans)
 ans = re.sub(r'<lex type="hw">','<lex>',ans)
 ans = re.sub(r'<lex type="hwifc">','<lex>',ans)
 return ans

def lex_adjust1(lex):
 ans = lex.strip()
 ans = re.sub(r'[ ~.,;_]','',ans)
 ans = re.sub(r'<ab>[^<]*</ab>','',ans)
 ans = re.sub(r'<c>[^<=]*</c>','',ans)
 ans = re.sub(r'<ls>[^<]*</ls>','',ans)
 ans = re.sub(r'<srs/>|<srs1/>','',ans)
 ans = re.sub(r'<p1?><s>','<s>',ans)
 ans = re.sub(r'</s></p1?>','</s>',ans)
 ans = re.sub(r'</s>[^<]*<s>','</s><s>',ans)
 ans = re.sub('<cf/>|<qv/>|<see/>|<sr1/>','',ans)
 ans = re.sub(r'<ls>.*?</ls>','',ans)
 #ans = re.sub('<b></b>','',ans)
 ans = re.sub(r'</?b>','',ans)
 ans = re.sub(r'<s>([^<]*)[/-]([^<]*)</s>','<s>\g<1>\g<2></s>',ans)
 ans = re.sub(r'</lex><lex>','',ans)
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
  self.dictlex_adj = lex_adjust1(self.dictlex_adj)
   
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
 # Oct 6 - simplify dictref for output
 dictref = datah.dictref
 dictref = dictref.strip('.0') # remove leading 0 and trail 0 or .
 outarr.append(dictref)
 outarr.append(datah.dictkey)
 #outarr.append(datah.dictkey2)  Don't show key2
 chklen = len(outarr)
 lexadj = datah.dictlex_adj
 if datah.stem:
  stem=datah.stem
 else:
  stem='NONE'
 if datah.loan:
  outarr.append("LOAN")
 if datah.lexid:
  outarr.append("LEXID=%s,STEM=%s" % (datah.lexid,stem))
 elif datah.inflectid:
  outarr.append("INFLECTID=%s,STEM=%s" % (datah.inflectid,stem))
 if len(outarr) != chklen:
  out = "\t".join(outarr)
  itype=2
  return (itype,out)
 if not lexadj:
  outarr.append("NO ADJUSTED INFL DATA: %s" % datah.dictlex)
  out = "\t".join(outarr)
  itype=-1
  return (itype,out)

 #try to match (adjusted) dictlex against normlex
 lex = datah.dictlex
 if lexadj in normlex:
  nlex = normlex[lexadj]
  norm=nlex.norm
  nlex.count = nlex.count + 1
  outsave = [x for x in outarr] # cheap copy of outarr
  if lex == lexadj:
   outarr.append(norm)
   out = '\t'.join(outarr)
   itype = 1
   if len(nlex.instances) < 10:
    nlex.instances.append(out)
   return (itype,out)
  else:
   outarr.append(norm)
   out = '\t'.join(outarr)
   outsave.append(lex)
   outwarn = '\t'.join(outsave)
   itype = 4
   if len(nlex.instances) < 10:
    nlex.instances.append(out)
   return (itype,out,outwarn)
 # error condition - lexadj unknown
 outarr.append(lexadj)
 outarr.append(lex)
 try:
  out = '\t'.join(outarr)
 except:
  print outarr
  print "Error 1"
  exit(1)
 itype = 3
 if lexadj not in normerrs:
  normerrs[lexadj]=0
 normerrs[lexadj] = normerrs[lexadj] + 1
 return (itype,out)

class Normlex(object):
 def __init__(self,n,t):
  self.n = n # line number of normlex file
  #self.count = t[0]
  self.count = 0 # Number of times this is used.
  self.form = t[0].strip() # adjusted lex
  self.norm = t[1] # 
  self.used = False
  self.instances = []

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
  rec.count = 0
  if rec.form in normlex:
   if rec.norm != normlex[rec.form].norm:
    print "Multiple values for rec.form=",rec.form
    print "old value = ",normlex[rec.form].norm
    print "new value = ",rec.norm
  normlex[rec.form] = rec # rec.norm
 f.close()
 return normlex

if __name__=="__main__": 
 filein = sys.argv[1] #  lexmap.txt
 filein1 = sys.argv[2] # lexicalgrammar.xml
 fileout1 = sys.argv[3] # lexnorm.txt
 fileout2 = sys.argv[4] # lexnorm-other.txt
 fileout3 = sys.argv[5] # error.txt
 fileout4 = sys.argv[6] # message.txt
 normlex= init_normlex(filein)
 process1a(filein1,fileout1,fileout2,fileout3,fileout4,normlex)
