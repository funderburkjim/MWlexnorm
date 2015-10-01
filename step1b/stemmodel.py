""" stemmodel.py
    Sep 20, 2015
    Adaptation of ejfcologne/lgtab1/filter1b_el.pl
    NOTE: sandhi_n has an 'adhoc' implementation.
"""
import sys,re,codecs
import sandhi_n


class Lexnorm(object):
 """
  The format of a line of lexnorm.txt is now 4 tab-delimited fields:
  lnum, key1, key2, lexinfo
  And, the lexinfo field has form of 1 or more colon-delimited fields, each
  of which has one of two forms:
  gender OR  gender#ending
 """
 def __init__(self,line):
  line = line.rstrip('\r\n')
  self.line=line
  (self.lnum,self.key1,self.key2,self.lexnormraw) = re.split('\t',line)

 def parse(self):
  # lexid, stem, normlex(?),ending,lexforms
  self.lexid=None
  self.stem=None
  self.ending=None
  self.lexforms=[]
  self.lexid = self.get_lexid()
  if self.lexid != "si":
   return 
  self.stem = self.get_stem()
  #if self.key1=='aTo':
  # print "DBG: parse. key1,lexid=",self.key1,self.lexid,"stem=",self.stem
  if not self.stem:
   return
  self.normlex=self.lexnormraw
  # get ending
  m = re.search(r'([a-zA-Z])$',self.stem)
  if not m:
   return
  self.ending = m.group(1)
  # get lexforms
  self.lexforms=self.get_lexforms()

 def get_lexid(self):
  lexnormraw=self.lexnormraw
  m = re.search(r'^LEXID=(.*),STEM=(.*)$',lexnormraw)
  if m:
   return 'OTHER' #m.group(1)
  if lexnormraw == 'LOAN':
   return 'OTHER'
  m = re.search(r'^INFLECTID=(.*),STEM=(.*)$',lexnormraw)
  if m:
   return 'OTHER'  # skip these, for some reason
  return "si" # for substantive or indeclineable

 def get_stem(self):
  lexnormraw=self.lexnormraw
  m = re.search(r'STEM=(.*)$',lexnormraw)
  if m:
   stem=m.group(1)
   if self.lexid in ['pron','card']:
    return stem
  if self.lexid != 'si':
   return None
  stem1 = self.key2mod()
  return stem1

 def get_lexforms(self):
  #if self.key1=='aTo':
  # print "DBG: get_lexforms",self.key1,self.lexnormraw
  forms = re.split(r':',self.lexnormraw)
  lexforms=[]
  for form in forms:
   form = re.sub(r'#','_',form)
   lexform = self.process_one_form(form)
   if lexform not in lexforms: # remove duplicates, which rarely occurs
    lexforms.append(lexform)
  return lexforms

 def process_one_form(self,form):
  ending = self.ending
  key = self.stem
  #if self.key1=='asvaka':
  # print "DBG: process_one_form",self.key1,form
  if (form == 'ind'):
   return "<f>%s %s</f>" %(key,form)
  # restate irregularities of form in MW
  if form in ["f_DA","f_lA","f_RA"]: 
   form="f_A"
  elif (form in ["f_kA"]) and (ending=="a"):
   form="f_A"
  elif (form == 'f_RI') and (key=='kzipaRi'):
   form='f_I'
  elif (form == 'f_RI') and (key=='parivAhin'):
   form='f' 
  elif (form in ['f_pUrvI','f_jvI','f_BvI','f_qvI']):
   form='f_vI'
  elif (form == 'f_pArzRI'):
   form='f_I'
  elif (form in ['f_SAsanA','f_SyetA']):
   form='f_A'
  # separate form into gender and formend
  formparts = re.split(r'_',form)
  if len(formparts)==2:
   (gender,formend) = formparts
  else:
   gender=formparts[0]
   formend=None
  # go through many cases, computing 'stem' and 'model' variables
  if (form == "f") and (ending == "a"):
   stem = re.sub(r'.$','A',key)
   model = '_'.join([form,'A'])
  elif (form in ['m','f','n']) and (ending in ['a','i','u']):
   stem = key
   model='_'.join([form,ending])
  elif (form == "f") and (ending in ['A','I','U']):
   stem = key
   model='_'.join([form,ending])
  elif (gender == "f") and (formend in ['A','I']):
   if sandhi_n.vowel_P(ending):  # Sep 23, 2015
    stem = re.sub(r'.$',formend,key)
   else:
    stem = key+formend
   model=form
  elif (gender == "f") and (formend in ['a','i','u','A','I','U']) and\
       (ending in ['a','i','u','A','I','U']):
   stem = re.sub(r'.$',formend,key)
   model=form
  elif (gender == "f") and (formend in ['ikA','akA']) and (re.search(r'aka$',key)):
   stem = re.sub(r'aka$','ikA',key)
   model="f_A"
  elif (gender == "f") and (formend in ['ikA','akA']) and re.search(r'a-ka$',key):
   stem = re.sub(r'a-ka$','ikA',key)
   model="f_A"
  elif (gender == "f") and (formend in ['ikA','ikI']) and re.search(r'ika$',key):
   (stem,model)=(re.sub(r'ika$',formend,key),'f_'+formend[2]) # f_A or f_I
  elif (form=='f_akI') and re.search(r'aka$',key):
   (stem,model)=(re.sub(r'aka$',formend,key),'f_I')
  elif (gender == "f") and (formend in ['ikA','akA']) and (re.search(r'a$',key)):
   (stem,model)= (re.sub(r'a$',formend,key),"f_A")
   #print "CHECK:",key," => ",stem  # these all looked fine.
  elif (form == "f_vI") and (ending in ['u','U']):
   (stem,model)= (re.sub(r'.$','vI',key),"f_I")
  elif (ending == 'n'):
   (stem,model)=self.process_one_ending_n(key,form)
  elif (ending == 'f'):
   (stem,model)=self.process_one_ending_f(key,form)
  elif (ending == 't'):
   (stem,model)=self.process_one_ending_t(key,form)
  elif (ending == 'c'):
   (stem,model)=self.process_one_ending_c(key,form)
  elif (ending == 's'):
   (stem,model)=self.process_one_ending_s(key,form)
  elif (form == 'm') and (ending == 'A'):
   # note: these will decline like gopA.
   # there are some exceptions (like hAhA) which must be
   # handled later. At the moment, hAhA will decline like gopA
   (stem,model)=(key,form+'_'+ending)
  elif (form == 'm') and (ending in ['I','U','O','o']):
   (stem,model)=(key,form+'_'+ending)
  elif (form == 'f') and (ending=='U'):
   (stem,model)=(key,form+'_'+ending)
  elif (form == 'n') and (ending in ['A','I','U']):
   # change stem to end in short vowel
   (stem,model)=(re.sub(r'.$',ending.lower(),key),form+'_'+ending)
  elif (ending in 'BDSzdhjkproOlTqvFxXEwW') and (form in ['m','f','n']):
   (stem,model)=(key,form+'_'+ending)
  # many special cases
  elif (form=='f_SAlyUhI'):
   (stem,model)=('SAlyUhI','f_I')
  elif (form=='f_ntI') and key.endswith('i'):  #Akidanti
   (stem,model)=(re.sub(r'i$','I',key),'f_I')
  elif (form=='f_stI') and (key=='Agastya'):
   (stem,model)=('AgastI','f_I')
  elif (form=='f_ArI') and (key=='Arya'):
   (stem,model)=('ArI','f_I')
  elif (form=='f_enikA') and (key=='etaka'):
   (stem,model)=('enikA','f_A')
  elif (form=='f_ikA') and (key=='dvArakA'):
   (stem,model)=('dvArikA','f_A')
  elif (form=='f_ikA') and (key=='SUrmi'):
   (stem,model)=('SUrmikA','f_A') 
  elif (form=='f_enI') and re.search(r'eta$',key):
   (stem,model)=(re.sub(r'eta$','enI',key),'f_I')
  elif (form=='f_AvI') and (key=='Avya'):
   (stem,model)=('avI','f_I')
  elif (form in ['f_apI','f_apyA']): # apya
   (stem,model)=(formend,'f_'+formend[-1]) 
  elif (form=='f_sI') and (key=='apasya'):
   (stem,model)=('apasI','f_I')
  elif form in ['f_patnI','f_tnI']: # aryapati, azwapati, Ayuzpati,vakpati
   (stem,model)=(re.sub(r'pati$','patnI',key),'f_I')
  elif (form=='f_padI'):
   if key.endswith('pad'):
    (stem,model) = (key+'I','f_I')
   elif key.endswith('pAda'):
    (stem,model) = (re.sub(r'a$','I',key),'f_I')
   else: # error, doesn't occur now
    (stem,model)=(None,None)    
  elif (form=='f_asatI') and (key=='asat'):
   (stem,model)=('asatI','f_I')
  elif (form=='f_asiknI') and (key=='asita'):
   (stem,model)=('asiknI','f_I')
  elif (form=='f_BArOhI') and (key=='BAra-vah'):
   (stem,model)=('BArOhI','f_I')
  elif (form=='f_BI') and (key=='nABi'):
   (stem,model)=('nABI','f_I')
  elif (form=='f_DU') and (key=='brahma-banDu'):
   (stem,model)=('brahma-banDU','f_U')
  elif (form=='f_IkA') and (key=='KuqqAka'):
   (stem,model)=('KuqqIkA','f_A')
  elif (form=='f_KarvikA') and (key=='Karvaka'):
   (stem,model)=('KarvikA','f_A')
  elif (form=='f_ReSI') and (key=='pUrRe-Sa'):
   (stem,model)=('pUrRe-SI','f_I')
  elif (form=='f_SAradI') and (key=='SArada'):
   (stem,model)=('SAradI','f_I')
  elif (form=='f_SI') and (key=='baliSa'):
   (stem,model)=('baliSI','f_I')
  elif (form=='f_SvenI') and (key=='Sveta'):
   (stem,model)=('SvenI','f_I')
  elif (form=='f_SyenI') and (key=='Syeta'):
   (stem,model)=('SyenI','f_I')
  elif (form=='f_aSiSu') and (key=='a-SiSu'):
   (stem,model)=('a-SiSu','f_u')
  elif (form=='f_aSiSvI') and (key=='a-SiSu'):
   (stem,model)=('a-SiSvI','f_I')
  elif (form=='f_adI') and (key=='Sata-pAd'):
   (stem,model)=('Sata-padI','f_I')
  elif (form=='f_adI') and (key=='sapta-pad'):
   (stem,model)=('sapta-padI','f_I')
  elif (form=='f_arI') and (key=='vi-BAva'):
   (stem,model)=('vi-BAvarI','f_I')
  elif (form=='f_cI') and (key=='marIci'):
   (stem,model)=('marIcI','f_I')
  elif (form=='f_cI') and (key=='sAMkuci'):
   (stem,model)=('sAMkucI','f_I')
  elif (form=='f_cIkA') and (key=='vi-paYcI'):
   (stem,model)=('vi-paYcIkA','f_A')
  elif (form in ['f_d/fSI','f_df/SI']) and (key=='su-dfS'):
   (stem,model)=('su-dfSI','f_I') # d/fSI is old accent form
  elif (form=='f_dAkU') and (key=='pfdAku'):
   (stem,model)=('pfdAkU','f_U')
  elif (form=='f_drI') and (key=='tandrI'):
   (stem,model)=('tandrI','f_I')
  elif (form=='f_gAnDarvI') and (key=='gAnDarva'):
   (stem,model)=('gAnDarvI','f_I')
  elif (form=='f_gayI') and (key=='SaM-gaya'):
   (stem,model)=('SaM-gayI','f_I')
  elif (form=='f_grI') and (key=='sAtyam-ugri'):
   (stem,model)=('sAtyam-ugrI','f_I')
  elif (form=='f_gryA') and (key=='sAtyam-ugri'):
   (stem,model)=('sAtyam-ugryA','f_A')
  elif (form=='f_hariRI') and (key=='harita'):
   (stem,model)=('hariRI','f_I')
  elif (form=='f_iRI') and (key=='Sukla-harita'):
   (stem,model)=('Sukla-hariRI','f_I')
  elif (form=='f_iRI') and (key=='rohita'):
   (stem,model)=('rohiRI','f_I')
  elif (form=='f_ikA') and (key=='mallikA'):
   (stem,model)=('mallikA','f_A')
  elif (form=='f_ikA') and (key=='vraRa-pawwikA'):
   (stem,model)=('vraRa-pawwikA','f_A')
  elif (form=='f_kI') and (key=='BallAtaka'):
   (stem,model)=('BallAtakI','f_I')
  elif (form=='f_kI') and (key=='dOvArika'):
   (stem,model)=('dOvArikI','f_I')
  elif (form=='f_kerI') and (key=='nAlikera'):
   (stem,model)=('nAlikerI','f_I')
  elif (form=='f_kyA') and (key=='pORiki'):
   (stem,model)=('pORikyA','f_A')
  elif (form=='f_kyA') and (key=='yOtaki'):
   (stem,model)=('yOtakyA','f_A')
  elif (form=='f_kzI') and (key=='SOcivfkzi'):
   (stem,model)=('SOcivfkzI','f_I')
  elif (form=='f_kzyA') and (key=='SOcivfkzi'):
   (stem,model)=('SOcivfkzyA','f_A')
  elif (form=='f_lI') and (key=='DUli'):
   (stem,model)=('DUlI','f_I')
  elif (form=='f_lI') and (key=='nArikela'):
   (stem,model)=('nArikelI','f_I')
  elif (form=='f_lI') and (key=='pattra-taRqulA'):
   (stem,model)=('pattrataRqulI','f_I')
  elif (form=='f_lI') and (key=='virudA-vali'):
   (stem,model)=('virudAvalI','f_I')
  elif (form=='f_lI') and (key=='SAlmali'):
   (stem,model)=('SAlmalI','f_I')
  elif (form=='f_li') and (key=='nArikela'):
   (stem,model)=('nArikeli','f_i')
  elif (form=='f_lohinI') and (key=='lohita'):
   (stem,model)=('lohinI','f_I')
  elif (form=='f_lohinikA') and (key=='lohitaka'):
   (stem,model)=('lohinikA','f_A')
  elif (form=='f_lyA') and (key=='SAlmali'):
   (stem,model)=('SAlmalyA','f_A')
  elif (form=='f_mA') and (key=='qiRqima'):
   (stem,model)=('qiRqimA','f_A')
  elif (form=='f_mahizI') and (key=='mahiza'):
   (stem,model)=('mahizI','f_I')
  elif (form=='f_makA') and (key=='a-lomaka'):
   (stem,model)=('a-lomakA','f_A')
  elif (form=='f_meTI') and (key=='meTi'):
   (stem,model)=('meTI','f_I')
  elif (form=='f_mikA') and (key=='a-lomaka'):
   (stem,model)=('a-lomikA','f_A')
  elif (form=='f_nA') and (key=='devA-rcana'):
   (stem,model)=('devA-rcanA','f_A')
  elif (form=='f_nI') and (key=='raktapItAsita-Syeta'):
   (stem,model)=('raktapItAsita-SyenI','f_I')
  elif (form=='f_nIkA') and (key=='padminI'):
   (stem,model)=('padminIkA','f_A')
  elif (form=='f_nIkA') and (key=='sTala-nalinI'):
   (stem,model)=('sTala-nalinIkA','f_A')
  elif (form=='f_naktA') and (key=='nakta'):
   (stem,model)=('naktA','f_A')
  elif (form in ['f_p/adI','f_pa/dI']) and (key=='su-pad'):
   # p/adI is old accent form
   (stem,model)=('su-padI','f_I')
  elif (form=='f_pA') and (key=='pa'):
   (stem,model)=('pA','f_A')
  elif (form=='f_pI') and (key=='pa'):
   (stem,model)=('pI','f_I')
  elif (form=='f_pad') and (key=='pad'):
   (stem,model)=('pad','f_d')
  elif (form=='f_padA') and (key=='tri-pada'):
   (stem,model)=('tri-padA','f_A')
  elif (form=='f_paliknI') and (key=='palita'):
   (stem,model)=('paliknI','f_I')
  elif (form in ['f_inI','f_tnI']) and (key == 'AyuH-pati'):
   # f_inI is wrong to be corrected
   (stem,model)=('AyuH-patnI','f_I')
  elif (form=='f_qI') and (key=='deva-tAqa'):
   (stem,model)=('deva-tAqI','f_I')
  elif (form=='f_rI') and (key=='vEdUrya'):
   (stem,model)=('vEdUrI','f_I')
  elif (form=='f_rU') and (key=='sahito-ru'):
   (stem,model)=('sahito-rU','f_U')
  elif (form=='f_rajjU') and (key=='rajju'):
   (stem,model)=('rajjU','f_U')
  elif (form=='f_riRI') and (key=='Barita'):
   (stem,model)=('BariRI','f_I')
  elif (form=='f_ryA') and (key=='kAYcana-kzIrI'):
   (stem,model)=('kAYcana-kzIryA','f_A')
  elif (form=='f_ryOhI') and (key=='turya-vah'):
   (stem,model)=('turyOhI','f_I')
  elif (form=='f_sOrI') and (key=='sOrya'):
   (stem,model)=('sOrI','f_I')
  elif (form=='f_sOryA') and (key=='sOrya'):
   (stem,model)=('sOryA','f_A')
  elif (form=='f_tIkA') and (key=='bfhatI'):
   (stem,model)=('bfhatIkA','f_A')
  elif (form=='f_takI') and (key=='kErAtaka'):
   (stem,model)=('kErAtakI','f_I')
  elif (form=='f_ti') and (key=='cuta'):
   (stem,model)=('cuti','f_i')
  elif (form=='f_tikA') and (key=='lohitaka'):
   (stem,model)=('lohitikA','f_A')
  elif (form=='f_tikA') and (key=='kErAtaka'):
   (stem,model)=('kErAtikA','f_A')
  elif (form=='f_tinI') and (key=='prati-prati'):
   (stem,model)=('prati-pratinI','f_I')
  elif (form=='f_ttyA') and (key=='yAjYa-datti'):
   (stem,model)=('yAjYa-dattyA','f_A')
  elif (form=='f_tyA') and (key=='bElvayata'):
   (stem,model)=('bElvayatyA','f_A')
  elif (form=='f_tyA') and (key=='cEkayata'):
   (stem,model)=('cEkayatyA','f_A')
  elif (form=='f_tyikA') and (key=='dAkziRAtyaka'):
   (stem,model)=('dAkziRAtyikA','f_A')
  elif (form=='f_vI') and (key=='Ekalavya'):
   (stem,model)=('EkalavI','f_I')
  elif (form=='f_vI') and (key=='try-avi'):
   (stem,model)=('try-avI','f_I')
  elif (form=='f_vi') and (key=='puro-gava'):
   (stem,model)=('puro-gavi','f_i')
  elif (form=='f_viSvOhI') and (key=='viSva-vah'):
   (stem,model)=('viSvOhI','f_I')
  elif (form=='f_vyadvarI') and (key=='vy-advara'):
   (stem,model)=('vy-advarI','f_I')
  elif (form=='f_wI') and (key=='pucCawi'):
   (stem,model)=('pucCawI','f_I')
  elif (form=='f_wI') and (key=='tulA-kowi'):
   (stem,model)=('tulA-kowI','f_I')
  elif (form=='f_yA') and (key=='dEva-yajYi'):
   (stem,model)=('dEva-yajYA','f_A')
  elif (form=='f_yanI') and (key=='brADnAyanya'):
   (stem,model)=('brADnAyanI','f_I')
  elif (form=='f_yikA') and (key=='su-nayaka'):
   (stem,model)=('su-nayikA','f_A')
  elif (form=='f_yonI') and (key=='yoni'):
   (stem,model)=('yonI','f_I')
  elif (form=='f_zI') and (key=='mazi'):
   (stem,model)=('mazI','f_I')
  elif (form=='f_zRI') and (key=='paruza'):
   (stem,model)=('paruzRI','f_I')
  elif (form=='f_kA') and (key == 'paYca-sahasrI'):
   (stem,model)=('paYca-sahasrIkA','f_A')
  elif (form=='ind_Sam') and (key=='vi-pAS'):
   (stem,model)=('vi-pASam','ind')
  elif (form=='ind_am') and (key=='muKa'):
   (stem,model)=('muKam','ind')
  elif (form=='ind_am') and (key=='sA-kzika'):
   (stem,model)=('sA-kzikam','ind')
  elif (form=='ind_nadam') and (key=='nada'):
   (stem,model)=('nadam','ind')

  elif (form=='m_Ra') and (key=='trAyamARA'):
   (stem,model)=('trAyamARa','m_a')
  elif (form=='m_SiYja') and (key=='SiYjA'):
   (stem,model)=('SiYja','m_')
  elif (form=='m_U') and (key=='BrU'):
   (stem,model)=('BrU','m_U')
  elif (form=='m_aha') and (key=='aha'):
   (stem,model)=('aha','m_a')
  elif (form=='m_cIka') and (key=='vi-paYcI'):
   (stem,model)=('vi-paYcIka','m_a')
  elif (form=='m_ka') and (key=='paYca-sahasrI'):
   (stem,model)=('paYca-sahasrIka','m_a')
  elif (form=='m_ka') and (key=='makzikA'): #?
   (stem,model)=('makzika','m_a')
  elif (form=='m_ka') and (key=='harItakI'): #?
   (stem,model)=('harItaka','m_a')
  elif (form=='m_mAna') and (key=='pAvamAnI'):
   (stem,model)=('pAvamAna','m_a')
  elif (form=='m_mela') and (key=='melA'):
   (stem,model)=('mela','m_a')
  elif (form=='m_nIka') and (key=='padminI'):
   (stem,model)=('padminIka','m_a')
  elif (form=='m_nIka') and (key=='sTala-nalinI'):
   (stem,model)=('sTala-nalinIka','m_a')
  elif (form=='m_rya') and (key=='kAYcana-kzIrI'):
   (stem,model)=('kAYcana-kzIrya','m_a')
  elif (form=='m_tIka') and (key=='bfhatI'):
   (stem,model)=('bfhatIka','m_a')
  elif (form=='m_u') and (key=='BrU'):
   (stem,model)=('Bru','m_u')

  elif (form=='n_Ra') and (key=='prod-GozaRA'):
   (stem,model)=('prod-GozaRa','n_a')
  elif (form=='n_Ra') and (key=='trAyamARA'):
   (stem,model)=('trAyamARa','n_a')
  elif (form=='n_Ri') and (key=='grAma-RI'):
   (stem,model)=('grAma-Ri','n_i')
  elif (form=='n_SAla') and (key=='SAlA'):
   (stem,model)=('SAla','n_a')
  elif (form=='n_a') and (key=='varatrA'):
   (stem,model)=('varatra','n_a')
  elif (form=='n_a') and (key=='vEra-yAtanA'):
   (stem,model)=('vEra-yAtana','n_a')
  elif (form=='n_cIka') and (key=='vi-paYcI'):
   (stem,model)=('vi-paYcIka','n_a')
  elif (form=='n_ga') and (key=='bahu-mArgI'):
   (stem,model)=('bahu-mArga','n_a')
  elif (form=='n_i') and (key=='lakzmI'):
   (stem,model)=('lakzmi','n_i')
  elif (form=='n_ka') and (key=='paYca-sahasrI'):
   (stem,model)=('paYca-sahasrIka','n_a')
  elif (form=='n_ka') and (key=='harItakI'):
   (stem,model)=('harItaka','n_a')
  elif (form=='n_la') and (key=='taralA'):
   (stem,model)=('tarala','n_a')
  elif (form=='n_nIka') and (key=='padminI'):
   (stem,model)=('padminIka','n_a')
  elif (form=='n_nIka') and (key=='sTala-nalinI'):
   (stem,model)=('sTala-nalinIka','n_a')
  elif (form=='n_na') and (key=='samBinna-vyaYjanA'):
   (stem,model)=('samBinna-vyaYjana','n_a')
  elif (form=='n_rya') and (key=='kAYcana-kzIrI'):
   (stem,model)=('kAYcana-kzIrya','n_a')
  elif (form=='n_saBa') and (key=='saBA'):
   (stem,model)=('saBa','n_a')
  elif (form=='n_sena') and (key=='senA'):
   (stem,model)=('sena','n_a')
  elif (form=='n_sura') and (key=='surA'):
   (stem,model)=('sura','n_a')
  elif (form=='n_tIka') and (key=='bfhatI'):
   (stem,model)=('bfhatIka','n_a')
  elif (form=='n_ta') and (key=='Bagavad-gItA'):
   (stem,model)=('Bagavad-gIta','n_a')
  elif (form=='n_tra') and (key=='pari-vastrA'):
   (stem,model)=('pari-vastra','n_a')
  elif (form=='n_u') and (key=='BrU'):
   (stem,model)=('Bru','n_u')

  elif (form=='f_si') and (key=='se'):
   (stem,model)=('si','f_i')
  elif (form in ['m','n']) and (key=='se'):
   (stem,model)=(key,form + '_e')
  elif (form=='m') and (key=='e'):
   (stem,model)=(key,'m_e')
  elif (form=='m') and (key=='pITe'):
   (stem,model)=(key,'m_e')

  elif (form in ['m','f','n']) and (key == 'banDu-pfC'):
   (stem,model) = (key,form+'_C')
  elif (form=='f_us') and key.endswith('u'):
   (stem,model)=(key+'s','f_us')
  elif (form in ['m','f','n']) and (key == 'su-valg'):
   (stem,model)=(key,form+'_g') # how to decline?
  elif (form in ['m','f','n']) and (key == 'pra-SAm'):
   (stem,model)=(key,form+'_m') # how to decline? Nom = praSAn
  elif (form in ['m','f','n']) and (key == 'pra-tAm'):
   (stem,model)=(key,form+'_m') # how to decline? Nom = pratAn
  elif (form=='m') and (key == 'pra-dAm'):
   (stem,model)=(key,form+'_m') # how to decline? Nom = pradAn
  elif (form=='m') and (key == 'dam'):
   (stem,model)=(key,form+'_m') # how to decline? gen. pl. = damAm
  elif (form=='f') and (key == 'saM-nam'):
   (stem,model)=(key,form+'_m') # how to decline? 
  elif (form=='f') and (key == 'kzam'):
   (stem,model)=(key,form+'_m') # how to decline?
  elif (form=='m') and (key == 'rAG'):
   (stem,model)=(key,form+'_G') # how to decline? nom = rAk
  elif (form=='f') and (key == 'saraG'):
   (stem,model)=(key,form+'_G') # how to decline? 
  elif (form=='f') and (key == 'klib'):
   (stem,model)=(key,form+'_b') # how to decline? 
  
  elif (form in ['m','f','n']) and (key == 'parA-R'):
   (stem,model)=(key,form+'_R') # how to decline?
  elif (form in ['m','f','n']) and (key == 'prA-R'):
   (stem,model)=(key,form+'_R') # how to decline?
  elif (form in ['m','f','n']) and (key == 'su-gaR'):
   (stem,model)=(key,form+'_R') # how to decline?

  # see discussion in https://github.com/sanskrit-lexicon/CORRECTIONS/issues/126
  elif (form=="f_is") and (key in ["kali","kavi","su-raBi"]):
   (stem,model)=(key,'f_i') # like mati
  elif (form=="f_iH") and (key == 'an-Api'):
   (stem,model)=(key,'f_i') # like mati
  elif (form in ['f_jYUs','f_Us']) and (key in ['asita-jYu','kamaRqalu','kaSeru','guggulu','guNgu','jatu']):
   (stem,model)=(re.sub(r'u$','U',key),'f_U') # like vaDU
  elif (form=='f_IH') and (key == 'a-durmaNgala'):
   (stem,model)=(re.sub(r'a$','I',key),'f_I1') # like DI
  elif (form=='f_Is') and (key in ['aruRI','tantrI']):
   (stem,model)=(key,'f_I1') # like DI

  else: # problem with form
   stem=None
  if not stem:
   return "<Q2>%s %s</Q2>" %(key,form)
  else: # form recognized
   return  "<f>%s %s</f>" %(stem,model)

 def process_one_ending_n(self,key,form):
  # returns either (None,None) or (stem,model)
  if re.search(r'in$',key) and (form in ['m','n']):
   return (key,form+'_in')
  if re.search(r'an$',key) and (form in ['m','n']):
   return (key,form+'_an')
  if (form=='f_DnI') and re.search(r'Dan$',key):
   return (re.sub(r'Dan$','DnI',key),'f_I')
  if (form in ['f_rzRI','f_zRI','f_SIrzRI']) and re.search(r'SIrzan$',key):
   return (re.sub(r'zan$','zRI',key),'f_I')
  if (form=='f_inI') and re.search(r'in$',key):
   return (key+'I','f_I')
  if (form=='f_jYI') and re.search(r'jan$',key):
   return (re.sub(r'jan$','jYI',key),'f_I')
  if (form=='f_iRI') and re.search(r'in$',key):
   return (re.sub(r'in$','iRI',key),'f_I')
  if (form in ['f_Gn/I','f_GnI/']) and re.search(r'han$',key):
   #Gn/I is old form,It will be corrected to GnI/
   # asurahan
   return (re.sub(r'han$','GnI',key),'f_I')
  if form=='f':
   stem=key
   if re.search(r'in$',stem):
    if '-' in stem:
     (pfx,sfx)=re.split(r'-',stem)
    else:
     (pfx,sfx)=('',stem)
    sfx1=sfx + 'I'
    sfx1 = sandhi_n.sandhi_n(sfx1)
    if pfx == '':  # Oct 1, 2015
     stem = pfx + sfx1
    else: # restore the '-'
     stem = pfx + "-" + sfx1;
    return (stem,'f_I')
   m=re.search(r'^(.*j)an$',stem)
   if m:
    return (m.group(1)+"YI",'f_I')  # rAjan -> rajYI
   m=re.search(r'^(.*rm)an$',stem)
   if m:
    return (m.group(1)+"aRI",'f_I')  # karman -> karmaRI
   return (stem+'I','f_I') # which cases?
  m = re.search(r'^f_(.*)$',form)
  if m:
   el = m.group(1)
   stem=key
   m = re.search(r'^(.*v)an$',stem)
   if m and (el == 'arI'):
    return (m.group(1)+el,'f_I')
   m = re.search(r'^(.*)van$',stem)
   if m and (el == 'varI'):
    return (m.group(1)+el,'f_I')
   m = re.search(r'^(.*)han$',stem)
   if m and (el == 'GnI'):
    return (m.group(1)+el,'f_I')
   m = re.search(r'^(.*)man$',stem)
   if m and (el == 'mnI'):
    return (m.group(1)+el,'f_I')
   m = re.search(r'^(.*)on$',stem)
   if m and (el == 'iRI'):
    return (m.group(1)+el,'f_I')
  # various other special cases
  if (form=='f_RI') and (key=='pari-vAhin'):
   return ('pari-vAhiRI','f_I')
  elif (form=='f_TI') and (key=='su-paTin'):
   return ('su-paTI','f_I')
  elif (form=='f_haRI') and (key=='vIra-han'):
   return ('vIra-haRI','f_I')
  elif (form=='f_hnI') and (key=='dIrGA-han'):
   return ('dIrGA-hnI','f_I')
  elif (form=='f_jA') and (key=='rAjan'):
   return ('rAjA','f_A')
  elif (form in ['f_jI','f_jYI']) and (key=='rAjan'):
   #f_jI is error.
   return ('rAjYI','f_I')
  elif (form=='f_mRI') and (key=='su-zAman'):
   return ('su-zAmRI','f_I')
  elif (form in ['f_minI','f_mnI']) and (key=='prati-nAman'):
   # f_minI is error in MW, to be corrected
   return ('prati-nAmnI','f_I')
  elif (form=='f_nI') and (key=='prativeSa-vAsin'):
   return ('prativeSa-vAsinI','f_I')
  elif (form=='f_nI') and (key=='prati-veSin'):
   return ('prati-veSinI','f_I')
  elif (form in 'f_yUnI') and (key=='yuvan'):
   return ('yUnI','f_I')
  elif (form=='f_yuvatI') and (key=='yuvan'):
   return ('yuvatI','f_I')
  elif (form=='f_yuvati') and (key=='yuvan'):
   return ('yuvati','f_i')
  elif (form in ['m','f','n']) and (key=='tajjalA-n'):
   # is this a present participle, of 'an' to breath?
   return ('tajjalAn',form+'_n')
  # default case
  return (None,None)

 def process_one_ending_f(self,key,form):
  # returns either (None,None) or (stem,model)
  if form in ['m','f','n']:
   return(key,form+'_f')
  m = re.search(r'^(.*t)f$',key)
  if m and (form == 'f_trI'):
   return (m.group(1)+'rI','f_I')
  elif (form=='f_attrI') and (key=='attf'):
   return('attrI','f_I')
  elif (form=='f_attrI') and (key=='attf'):
   return('attrI','f_I')
  elif (form=='f_f') and (key=='sapta-svasf'):
   return('sapta-svasf','f_f')
  elif (form=='f_metA') and (key=='metf'):
   return('metA','f_A')
  elif (form=='f_rI') and (key=='pari-vezwf'):
   return('pari-vezwrI','f_I')
  elif (form=='f_rI') and (key=='rabDf'):
   return('rabDrI','f_I')
  elif (form=='f_sanutrI') and (key=='sanutf'):
   return('sanutrI','f_I')
  elif (form in ['f_trI','f_wrI']) and (key=='yazwf'):
   # f_trI to be corrected in MW data
   return('yazwrI','f_I')
  elif (form=='f_yantrI') and (key=='yantf'):
   return('yantrI','f_I')
  elif (form=='f_zwrI') and (key=='jozwf'):
   return('jozwrI','f_I')
  elif (form in ['f_tF','f_trI']) and (key == 'Dartf'):
   # f_tF is an error in MW.
   return ('DartrI','f_I')
  return (None,None)

 def process_one_ending_t(self,key,form):
  # returns either (None,None) or (stem,model)
  m = re.search(r'^(.*)([mv]at)$',key)
  if m and (form in ['m','n']):
   return (key,form+'_'+m.group(2))
  if m and form == 'f':
   return (key+'I','f_I')
  m = re.search(r'^(.*)(at)$',key)
  if m and (form == 'f_antI'):
   return (m.group(1)+'antI','f_I')
  if m and (form == 'f_atI'):
   return (m.group(1)+'atI','f_I')
  m = re.search(r'[^a]t$',key)
  if m and (form in ['m','f','n']):
   return (key,form+'_t')
  m =  re.search(r'iyat$',key)
  if m and (form in ['m','n']):
   return (key,form+'_iyat')
  if m and (form == 'f'):
   return (key+'I',form+'_I')
  m =  re.search(r'(jagat)|(mahat)$',key)
  if m and (form in ['m','n']):
   return (key,form+'_at')
  if m and (form == 'f'):
   return (key+'I',form+'_I')
  m =  re.search(r'at$',key)
  # some of these forms will be wrong, as they are participles
  # declined with one stem.  This will have to be rectified later.
  if m and (form in ['m','n']):
   return (key,form+'_at1')
  if m and (form == 'f'):
   return (key+'I',form+'_at1')
  if form == 'f_ntI':
   return (re.sub(r't$','ntI',key),'f_I')
  if form == 'f_vatI':
   return (key + 'I','f_I') # antarvat, apivat
  if form == 'f_vatnI':
   return (key + 'nI','f_I') # antarvat
  if (form == 'f_AtI') and (key == 'ni-drAt'):
   return ('ni-drAtI','f_I')
  if (form == 'f_AntI') and (key == 'ni-drAt'):
   return ('ni-drAntI','f_I')
  if (form == 'f_tI') and (key in ['SaSvat','tAdfgrUpa-vat']):
   return (key+'I','f_I')
  if (form == 'f_SaSvatI') and (key == 'SaSvat'):
   return ('SaSvatI','f_I')
  if (form == 'f_Scat') and (key == 'a-saScat'):
   return (key,'f_t')
  if (form == 'f_asaScantI') and (key == 'a-saScat'):
   return ('a-saScantI','f_I')
  if (form in ['f_anti', 'f_antI']) and (key == 'lolat'):
   #f_anti is error, will be corrected
   return ('lolantI','f_I')
  if (form == 'f_asatI') and (key == 'a-sat'):
   return ('asatI','f_I')
  if (form == 'f_satI') and (key == 'sat'):
   return ('satI','f_I')
  
  # otherwise, a problem
  return (None,None)

 def process_one_ending_c(self,key,form):
  # returns either (None,None) or (stem,model)
  m = re.search(r'aYc$',key)
  if m:
   return (key,form+'_aYc')
  return (key,form+'_c')

 def process_one_ending_s(self,key,form):
  # returns either (None,None) or (stem,model)
  m = re.search(r'yas$',key) # comparative adjective
  if m:
   return (key,form+'_yas')
  if form in ['f_ajaGnuzI','f_GnuzI']: # 
   stems = {'jaGanvas':'jaGnuzI','a-jaGnivas':'ajaGnuzI',
            'jaGnivas':'jaGnuzI'}
   if key in stems:
    return (stems[key],'f_I')
   else: # unexpected. probably never occurs
    print "process_one_ending_s:",key,form
    return (None,None)
  m = re.search(r'vas$',key) # perfect active participle
  if m:
   return (key,form+'_vas')
  return (key,form+'_s') # everything else (uSas, yaSas, etc.)

 def key2mod(self):
  key = self.key2
  # Sep 22, 2015. for this purpose, treat <srs/> as a '-'.
  # example sandhi_n for f. of mfzAnuSAsin mf/zA<srs/><sr1/>nuSAsin
  key = re.sub(r'<srs/>','-',key)
  # remove xml elements 'tags'
  key = re.sub(r'<.*?>','',key)
  # remove unknown chars (such as accents)
  key = re.sub(r'[^a-zA-Z|-]','',key)
  # change multiple '-' to single
  key = re.sub(r'-[-]+','-',key)
  # remove all but the last '-'
  m = len(re.findall('-',key))
  if m>1:
   key = key.replace('-','',m-1)
  if key.endswith('-'): # case of aTo. Probable key2 markup error
   #print "DBG: key2mod. ends with '-'",self.key2," => ",key
   #print "      ",self.line
   key = re.sub('-','',key)
  return key

def init_lexnorm(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Lexnorm(x) for x in f]
 return recs

def lnum_form(lnum):
 x = float(lnum)
 ans = "MW-%010.2f" %x
 return ans

def analyze_problems(probrecs,fout1):
 probforms=[]
 for rec in probrecs:
  recprobs=[x for x in rec.lexforms if x.startswith('<Q')]
  for f in recprobs:
   m = re.search(r'<Q2>(.*?) (.*?)</Q2>',f)
   if not m:
    print "ERROR: analyze_problems:",f
    continue
   probforms.append((m.group(2),rec))
 sortedprobs = sorted(probforms,key=lambda(t):t[0] + t[1].lnum)
 prev_t=""
 ncase=0
 for (t,rec) in sortedprobs:
  if t!= prev_t:
   fout1.write("\n")
   prev_t = t
   ncase=ncase+1
   fout1.write("CASE %s: %s\n" % (ncase,t))
   icase=0
  icase=icase+1
  outarr=[]
  outarr.append("%02d"%icase)
  outarr.append(lnum_form(rec.lnum))
  outarr.append(rec.key1)
  probformsmatch=[]
  recprobs=[x for x in rec.lexforms if x.startswith('<Q')]
  for y in recprobs:
   m = re.search(r'<Q2>(.*?) (.*?)</Q2>',y)
   ty = m.group(2)
   if ty == t:
    probformsmatch.append(y)
  lexformout = ''.join(probformsmatch)
  outarr.append(rec.lexnormraw)
  outarr.append(lexformout)
  out = '\t'.join(outarr)
  fout1.write("%s\n" % out)

def stemmodel(lexnormrecs,fileout,fileout1):
 m=100 # debug
 m = len(lexnormrecs) # production
 for irec in xrange(0,m):
  rec = lexnormrecs[irec]
  rec.parse()
 fout = codecs.open(fileout,"w","utf-8")
 fout1 = codecs.open(fileout1,"w","utf-8")
 nout=0
 nout1=0
 nout2=0
 probrecs=[]
 for irec in xrange(0,m):
  rec = lexnormrecs[irec]
  outarr=[]
  outarr.append(lnum_form(rec.lnum))
  outarr.append(rec.key1)
  lexformout = ''.join(rec.lexforms)
  #if rec.key1 == 'aTo':
  # print "DBG: line=",rec.line,"ans='%s'"%lexformout
  if rec.lexid == 'OTHER': # pronouns, dual-plural, etc.
   outarr.append(rec.lexnormraw)
   out = '\t'.join(outarr)
   fout1.write("%s\n" % out)
   nout1=nout1+1
  elif (lexformout == ''): # problem
   outarr.append(rec.lexnormraw)
   out = '\t'.join(outarr)
   print "?1",out
   #fout1.write("%s\n" % out)
   nout2=nout2+1
  elif re.search(r'<Q',lexformout): # problem
   probrecs.append(rec)
   outarr.append(rec.lexnormraw)
   outarr.append(lexformout)
   out = '\t'.join(outarr)
   print "?2",out
   #fout1.write("%s\n" % out)
   nout2=nout2+1
  else: # no problem
   outarr.append(lexformout)
   out = '\t'.join(outarr)
   fout.write("%s\n" % out)
   nout=nout+1
 fout.close()
 # further analysis of problem records
 #analyze_problems(probrecs,sys.stdout) #fout1
 fout1.close()
 print nout,"records written to",fileout
 print nout1,"records written to",fileout1
 print nout2,"Questionable records"

if __name__ == "__main__":
 filein = sys.argv[1] # lexnorm.txt
 fileout = sys.argv[2] # stemmodel.txt
 fileout1 = sys.argv[3] # stemmodel_other.txt
 # There are also print statements
 lexnormrecs = init_lexnorm(filein)
 print len(lexnormrecs)," records in",filein
 stemmodel(lexnormrecs,fileout,fileout1)
