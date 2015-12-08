echo "mw.xml is in a directory 'mwxml' ABOVE MWlexnorm."
echo "This directory may be downloaded (in compressed form) by"
echo "curl -o mwxml.zip http://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2014/downloads/mwxml.zip"
echo 
echo "remake lexicalgrammar from mw.xml and DualPlural, participle"
python lexicalgrammar_dp.py ../../mwxml/mw.xml DualPlural.txt participle.txt lexicalgrammar.xml
echo "validating lexicalgrammar.xml with lexicalgrammar.dtd"
python validate.py lexicalgrammar.xml lexicalgrammar.dtd
