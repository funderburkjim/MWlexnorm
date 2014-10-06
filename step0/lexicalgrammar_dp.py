""" lexicalgrammar_dp.py Sep 28, 2014
 Construct lexicalgrammar.xml from monier.xml (or mw.xml) and DualPlural.txt
 
"""
import sys, re,codecs

def lexicalgrammar_dp(filein,fileout,dpdict):
 fout = codecs.open(fileout,"w",'utf-8')
 fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
 fout.write('<!DOCTYPE lexicalgrammar SYSTEM "lexicalgrammar.dtd">\n')
 fout.write('<lexicalgrammar>\n')
 nfound=do_process1(filein,fout,dpdict)
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

def dp_adjust(data,dpdict):
 data = data.rstrip('\r\n')
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

def do_process1(filein,fout,dpdict):
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
    noninh = noninh+1
 if (noninh == 0):
  # this causes record to be omitted in output
  dictlex = ""
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
 fileout = sys.argv[3] # lexicalgrammar0.xml
 dpdict = parse_dualPlural(filein1)
 lexicalgrammar_dp(filein,fileout,dpdict)
