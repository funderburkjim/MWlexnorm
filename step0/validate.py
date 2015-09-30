""" validate.py
    Sep 27, 2015
    python validate <xmlfile> <dtdfile>
"""
from lxml import etree
import sys,codecs

if __name__=="__main__": 
 filexml = sys.argv[1] # xml file
 filedtd = sys.argv[2] # dtd file

 dtd = etree.DTD(filedtd)
 print (dtd.error_log.filter_from_errors())
 print "dtd ok"
 parser = etree.XMLParser(dtd_validation=True)

 root = etree.parse(filexml,parser)
 print "parsed file"
 exit(0)
 xmlstring="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE lexicalgrammar SYSTEM "lexicalgrammar.dtd">
<lexicalgrammar>
<gram><dict>MW</dict><dictref>0000002.00</dictref><dictkey2><![CDATA[a--kAra]]></dictkey2><dictkey>akAra</dictkey><dictlex><![CDATA[<lex>m.</lex>]]></dictlex><stem>akAra</stem></gram>
</lexicalgrammar>
"""
 parser = etree.XMLParser(dtd_validation=True)
 root = etree.fromstring(xmlstring,parser)
 #root = etree.XML(filexml,parser)
 print "ok"
 exit(0)
 dtd = etree.DTD(filedtd)
 print (dtd.error_log.filter_from_errors())
 print "dtd ok"
 root = etree.XML(filexml)
 print (dtd.validate(root))
 exit(0)
 parser = etree.XMLParser(dtd_validation=True)
 root = etree.XML(filexml,parser)
 print "done"
 exit(0)
 tree = etree.parse(filexml,validation=True)
 print "done"
 exit(1)
 dtd = etree.DTD(filedtd)
 root = etree.XML(filexml)
 print (dtd.validate(root))
