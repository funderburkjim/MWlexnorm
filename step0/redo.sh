echo "remake lexicalgrammar from mw.xml and DualPlural, participle"
python lexicalgrammar_dp.py ../../mwxml/mw.xml DualPlural.txt participle.txt lexicalgrammar.xml
echo "validating lexicalgrammar.xml with lexicalgrammar.dtd"
python validate.py lexicalgrammar.xml lexicalgrammar.dtd
