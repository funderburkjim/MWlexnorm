echo "downloading mwxml.zip"
curl -o mwxml.zip http://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2014/downloads/mwxml.zip
echo "unzipping mwxml.zip to folder xml"
unzip mwxml.zip
echo "renaming xml to mwxml"
rm -r mwxml
mv xml mwxml
echo "removing mwxml.zip"
rm mwxml.zip
