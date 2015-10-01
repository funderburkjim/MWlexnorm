# 1 combine lexnorm.txt and lexnorm-other.txt into one file
echo "combine lexnorm and lexnorm-other"
python lexcat.py ../step1a/lexnorm.txt ../step1a/lexnorm-other.txt lexnorm-all.txt
# 2 make stemmodel.txt etc.
echo "make stemmodel.txt, stemmodel_other, stemmodel_log"
python stemmodel.py lexnorm-all.txt stemmodel.txt stemmodel_other.txt > stemmodel_log.txt
