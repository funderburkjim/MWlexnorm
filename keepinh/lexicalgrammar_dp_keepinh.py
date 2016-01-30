""" lexicalgrammar_dp_keepinh.py Jan 29, 2016
 Don't discard type="inh" records
 Construct lexicalgrammar.xml from monier.xml (or mw.xml) and DualPlural.txt
 Sep 27, 2015.  Revised to also use participle.txt 
"""
import sys, re,codecs

def lexicalgrammar_dp(filein,fileout,dpdict,partdict):
 fout = codecs.open(fileout,"wb",'utf-8')
 fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
 fout.write('<!DOCTYPE lexicalgrammar SYSTEM "lexicalgrammar.dtd">\n')
 fout.write('<lexicalgrammar>\n')
 nfound=do_process1(filein,fout,dpdict,partdict)
 print "nfound=",nfound
 fout.write('</lexicalgrammar>\n')
 fout.close()
 # status of dpdict usage
 n2=0
 for dictkey in iter(dpdict):
  rec=dpdict[dictkey]
  if not rec.used:
   n2 = n2 + 1
   print 'dp unused: ',(rec.key1,rec.stem,rec.L,rec.inflectid)
 if n2 == 0:
  print 'All DualPlural records used'
 else: 
  print "%s DualPlural records not used" % n2

 # status of partdict usage
 n2=0
 for dictkey in iter(partdict):
  rec=partdict[dictkey]
  if not rec.used:
   n2 = n2 + 1
   print 'particple line unused: ',rec.line
 if n2 == 0:
  print 'All participle records used'
 else: 
  print "%s participle records not used" % n2

def dp_adjust(data,dpdict):
 #data = data.rstrip('\r\n')
 if not data.startswith('<gram>'):
  return data
 m = re.search(r'<dictref>(.*?)</dictref>',data)
 dictref = m.group(1)  # assume match found
 if dictref not in dpdict:
  return data
 rec = dpdict[dictref]
 m = re.search(r'<dictkey>(.*?)</dictkey>',data)
 dictkey = m.group(1)
 if rec.key1 != dictkey:
  print "dictkey error",dictkey
  print "dprec=",(rec.key1,rec.stem,rec.L,rec.inflectid)
  print "lgdata=",data
  exit(1)
 data = re.sub(r'<stem>.*?</stem>',r'<stem>%s</stem><inflectid>%s</inflectid>' %(rec.stem,rec.inflectid),data)
 if rec.used:
  print "Duplicate error",dictkey
  print "dprec=",(rec.key1,rec.stem,rec.L,rec.inflectid)
  print "lgdata=",data
  exit(1)
 rec.used = True
 return data

def part_adjust(data,partdict):
 #data = data.rstrip('\r\n')
 if not data.startswith('<gram>'):
  return data
 m = re.search(r'<dictref>(.*?)</dictref>',data)
 dictref = m.group(1)  # assume match found
 if dictref not in partdict:
  return data
 rec = partdict[dictref]
 m = re.search(r'<dictkey>(.*?)</dictkey>',data)
 dictkey = m.group(1)
 if rec.key1 != dictkey:
  print "dictkey error",dictkey
  print "partrec=",(rec.key1,rec.root,rec.L,rec.inflectid)
  print "lgdata=",data
  exit(1)
 m = re.search(r'<dictlex>(.*?)</dictlex>',data)
 dictlex = m.group(0)  # assume match found

 lexid = rec.lexid
 rootclass = rec.rootclass
 stem = rec.stem
 L = rec.L
 dictref = "%010.2f" % float(L)
 dictkey2 = stem
 # construct output 
 linear=[]
 linear.append("<gram>")
 linear.append("<dict>MW</dict>" )
 linear.append("<dictref>%s</dictref>" % dictref)
 linear.append("<dictkey2><![CDATA[" + dictkey2 + "]]></dictkey2>")
 linear.append("<dictkey>%s</dictkey>" % dictkey)
 #linear.append("<dictlex><![CDATA[" + dictlex + "]]></dictlex>")
 linear.append(dictlex)
 linear.append("<stem>%s</stem>"%stem)
 linear.append("<lexid>%s</lexid>"%lexid)
 linear.append("<rootclass>%s</rootclass>"%rootclass)
 linear.append("</gram>") #close the xml
 data = ''.join(linear)
 if rec.used:
  print "Duplicate error",dictkey
  print "partrec=",rec.line
  print "lgdata=",data
  exit(1)
 rec.used = True
 return data

def do_process1(filein,fout,dpdict,partdict):
 nfound=0
 nfound1=0
 f = codecs.open(filein,"r",'utf-8')
 nfound1=0
 m = 1000000
 print "dbg m = ",m
 for data1 in f:
  data1 = data1.rstrip('\r\n')
  if not data1.startswith('<H'):
   continue
  nfound1= nfound1+ 1
  subdata = get_subdata(data1)
  if (subdata != ""):
   subdata1 = dp_adjust(subdata,dpdict)
   if subdata1 == subdata:  
    # no dp adjustment. Try participle adjustment
    subdata1 = part_adjust(subdata1,partdict)
   fout.write("%s\n" % subdata1)
   nfound = nfound + 1
  if nfound >= m: 
   break
 f.close()
 return(nfound)


def get_subdata(datain):
 data1 = datain
 line=""
 dict = "MW"
 dictref = 0 # L
 dictkey = '' # key1
 loan = "" # normally not present
 lexid = "" # normally not present
 dictlex = ""
 # key1
 m = re.search(r'<key1>(.*?)</key1>',data1)
 dictkey = m.group(1)

 # key2
 m = re.search(r'<key2>(.*?)</key2>',data1)
 dictkey2 = m.group(1)
 m = re.search(r'<loan/>',data1)
 if m:
  loan = m.group(0)
 # search through all lexes, keeping only those we want, namely
 # <lex>xxx</lex> or
 # <lex type="inh">xxx</lex> or
 # <lex type="hw">xxx</lex> or
 # <lex type="hwalt">xxx</lex> or
 # <lex type="hwifc">xxx</lex>
 # <lex type="extra">xxx</lex>  2008-08-08
 noninh=0
 # Sep 24, 2014 remove 'type="nhw"' cases to avoid 'nested lexes'
 #data1 = re.sub(r'<lex type="nhw">.*?</lex','',data1)
 for m in re.finditer(r'<lex([^>]*)>(.*?)</lex>',data1):
  lextype = m.group(1)
  lexdata = m.group(2)
  match = m.group(0)
  m = re.search(r'type="(.*)"',lextype)
  if not m:
   t = ""
  else:
   t = m.group(1)
  if t in ["","hw","inh","hwifc","hwalt","extra"]:
   dictlex = dictlex + match
   if t != "inh":
    noninh = noninh+1
   elif re.search(r'<ab>(pl|du|sg)[.]',lexdata):
    # Sep 27, 2015 Removed the next case. These are situations where
    # (a) t == "inh" and (b) there is also a pl., etc in lexdata.
    # I don't think these need to be considered for purpose of generating
    # declension data
    pass
    #noninh = noninh+1
 if (noninh == 0):
  # this causes record to be omitted in output
  #dictlex = ""
  pass  # Jan 29, 2016
 #-------------
 pron=""
 card=""
 stem=""
 m = re.search(r'<pron>(.*?)</pron>',datain)
 if m:
  pron = m.group(0)
  stem = m.group(1)
  lexid = "pron"
 else:
  m = re.search(r'<card>(.*?)</card>',datain)
  if m:
   card = m.group(0)
   stem = m.group(1)
   lexid = "card" 
 # finally, get L
 m = re.search(r'<L.*?>(.*?)</L>',data1)
 dictref=m.group(1)
 # the 'id' in the mysql file is dict-dictref.
 # to have this appear in same order as the numeric 'L', do the following:
 dictref = "%010.2f" % float(dictref)
 if ((dictlex == "") and (pron == "") and (card == "")) :
  return ""
 # otherwise, construct output 
 linear=[]
 linear.append("<gram>")
 linear.append("<dict>%s</dict>" % dict)
 linear.append("<dictref>%s</dictref>" % dictref)
 linear.append("<dictkey2><![CDATA[" + dictkey2 + "]]></dictkey2>")
 linear.append("<dictkey>%s</dictkey>" % dictkey)
 linear.append("<dictlex><![CDATA[" + dictlex + "]]></dictlex>")
 #   "<stem>dictkey</stem>"; # sets default stem
 if (loan != ""):
  linear.append("<stem>%s</stem><loan />" % dictkey)
 elif (pron != "") or (card != "") :
  linear.append("<stem>%s</stem><lexid>%s</lexid>" %(stem,lexid))
 else : # usual case, set default stem
  linear.append("<stem>%s</stem>" % dictkey)
 linear.append("</gram>") #close the xml
 line = ''.join(linear)
 return(line)

class Participle(object):
 def __init__(self,t,line):
  self.line=line
  self.L = t[0]
  self.stem = t[1]
  self.key1 = re.sub(r'-','',self.stem)
  self.rootclass = t[2] # root-class
  self.lexid = t[3] # prap or fap
  self.used = False

def parse_participle(filein):
 f = codecs.open(filein,"r",'utf-8')
 partdict={}
 for line in f:
  line=line.rstrip('\r\n')
  if line.startswith(';'): 
   # comment
   continue
  t = line.split(':')
  rec = Participle(t,line)
  dictref = '%010.2f' % float(rec.L)
  partdict[dictref] = rec
 f.close()
 return partdict

class DualPlural(object):
 def __init__(self,t):
  self.key1 = t[0]
  self.stem = t[1]
  self.L = t[2]
  self.inflectid = t[3]
  self.used = False

def parse_dualPlural(filein):
 f = codecs.open(filein,"r",'utf-8')
 dpdict={}
 for line in f:
  line=line.rstrip('\r\n')
  if line.startswith(';'): 
   # comment
   continue
  t = line.split(':')
  rec = DualPlural(t)
  dictref = '%010.2f' % float(rec.L)
  dpdict[dictref] = rec
 f.close()
 return dpdict

if __name__=="__main__": 
 filein = sys.argv[1] # monier.xml
 filein1 = sys.argv[2] # DualPlural.txt
 filein2 = sys.argv[3] # participle.txt
 fileout = sys.argv[4] # lexicalgrammar0.xml
 dpdict = parse_dualPlural(filein1)
 partdict = parse_participle(filein2)
 lexicalgrammar_dp(filein,fileout,dpdict,partdict)
