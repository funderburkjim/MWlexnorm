""" sandhi_n.py
    Sep 21, 2015
    Implement n->R sandhi.
    Conversion of code within 'decline.pm'
    Assumes Sanskrit text uses SLP1 transliteration
"""
import re
# some Sanskrit character classes.
shortsimplevowels = "aiufx"
longsimplevowels = "AIUFX"
simplevowels = shortsimplevowels + longsimplevowels
diphthongs = "eEoO"
vowels = simplevowels + diphthongs

simplegutturals = "kKgGN"
gutturals = simplegutturals + "hH"
simplepalatals = "cCjJY"
palatals = simplepalatals + "yz"
simplecerebrals = "wWqQR"
cerebrals = simplecerebrals + "rS"
simpledentals = "tTdDn"
dentals = simpledentals + "ls"
simplelabials = "pPbBm"
labials = simplelabials + "vH"
semivowels = "yrlvh"
sibilants = "SzsH"
anusvAra = "M"
consonants = simplegutturals + simplepalatals +\
    simplecerebrals + simpledentals + simplelabials +\
    semivowels + sibilants +\
    anusvAra

def sandhi_n(x):
 """
 # assume 'x' is a string
 # This is n->R sandhi. Probably a better implementation
 #  " Antoine 17
 #  When, in the same word, 'n' is preceded by 'f', 'F', 'r', or 'z' and
 #  followed by a vowel or by 'n', 'm', 'y', or 'v', then it is changed to
 #  'R' even when there are letters between the preceding 'f' (etc) and 'n'
 #  provided these intervening letters be vowel, gutturals, labials, 
 #  'y', 'v', h', or 'M' (anusvAra)."
 #   input is assumed to be a Python string
 """
 chars = list(x)
 n = len(chars)
 i=0
 while (i < n):
  x1 = chars[i]
  i = i+1
  if x1 in ['f','F','r','z']:
   i1=i
   i2=-1
   ok=False
   while (i < n):
    x2 = chars[i]
    i = i+1
    if (x2 == 'n') and (i<n):
     x3 = chars[i]
     if vowel_P(x3) or (x3 in ['n','m','y','v']):
      i=i-1
      i2=i
      i=n # break loop
   #
   i=i1
   if (0<=i2):
    # found a subsequent "n". Now check intervening letters
    ok=True
    while ok and (i<i2):
     y = chars[i]
     if vowel_P(y) or guttural_P(y) or labial_P(y) or (y in ['y','v','h','M']):
      i=i+1
     else:
      # intervening letter 'y' is wrong
      ok=False
    #
    if ok:
     # make the change n -> R
     chars[i2]="R"
     i = i2+1
   #
 return ''.join(chars)
def labial_P(x):
 return x in labials
def vowel_P(x):
 return x in vowels
def guttural_P(x):
 return x in gutturals
def consonant_P(x):
 return x in consonants
