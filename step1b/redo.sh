# 1 combine lexnorm.txt and lexnorm-other.txt into one file
echo "combine lexnorm and lexnorm-other"
python lexcat.py ../step1a/lexnorm.txt ../step1a/lexnorm-other.txt lexnorm-all.txt
# 2 make filter1b_el.txt etc.
echo "make filter1b_el.txt, filter1b_el_other, filter1b_el_log"
python filter1b_el.py lexnorm-all.txt filter1b_el.txt filter1b_el_other.txt > filter1b_el_log.txt
