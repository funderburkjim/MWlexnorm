python26 normlex_simplify.py prevnormlex.txt normlex.txt > simplify_log.txt
echo "check simplify_log.txt"
python26 process1a.py normlex.txt ../step0/lexicalgrammar.xml step1a.txt exclude.txt error.txt warn.txt > normerr.txt

