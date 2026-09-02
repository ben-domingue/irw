import csv,io,os,re,collections,unicodedata
TXT='/tmp/claude-1000/itbf/text'
tg={r['table']:r for r in csv.DictReader(io.open('/tmp/claude-1000/itbf/targets.csv',encoding='utf-8'))}
SCRIPTS=[('CJK',r'[一-鿿]'),('Hangul',r'[가-힯]'),('Kana',r'[぀-ヿ]'),('Cyrillic',r'[Ѐ-ӿ]'),
 ('Arabic',r'[؀-ۿ]'),('Devanagari',r'[ऀ-ॿ]'),('Hebrew',r'[֐-׿]'),('Greek',r'[Ͱ-Ͽ]'),('Thai',r'[฀-๿]')]
EN=set("the a an of to and or is are you your i in for on with that this it not do does have has was were be been at as if any how much often when what which who please rate following statements agree disagree never always sometimes very my me we they he she her his am can will would should about from by".split())
def judge(t):
    """Return (verdict, script). Only positive evidence counts."""
    t=re.sub(r'\bNA\b','',t or '').strip()
    if not t: return 'blank',''
    sc=[n for n,p in SCRIPTS if len(re.findall(p,t))>2]
    if sc: return 'ADMIN',';'.join(sc)                    # non-Latin script: definitive
    dia=len([c for c in t if ord(c)>127 and unicodedata.category(c).startswith('L')])
    if dia>3: return 'ADMIN','latin-diacritic'            # Latin + diacritics: strong
    w=re.findall(r"[A-Za-z']+",t.lower())
    if len(w)<25: return 'ASCII_SHORT',''                 # too little text to judge
    r=sum(1 for x in w if x in EN)/len(w)
    if r>=0.15: return 'ENGLISH',''
    if r<0.05:  return 'ADMIN','latin-nonenglish'
    return 'ASCII_UNSURE',''
FIELDS=('item_text','option_text','instructions','section_prompt')
out=[]
for fn in sorted(os.listdir(TXT)):
    if not fn.endswith('.csv'): continue
    tb=fn[:-4]
    d=list(csv.DictReader(io.open(os.path.join(TXT,fn),encoding='utf-8')))
    if not d: out.append([tb,'EMPTY']+['-']*4+['','',tg.get(tb,{}).get('lang_tag','')]); continue
    per={}; scr=set()
    for c in FIELDS:
        if c not in d[0]: per[c]='missing'; continue
        v,s=judge(' '.join((r.get(c) or '') for r in d)); per[c]=v
        if s and not s.startswith('latin'): scr.add(s)
    it=per['item_text']                                    # item_text is the load-bearing field
    others=[per[c] for c in ('option_text','instructions','section_prompt') if per[c] in ('ADMIN','ENGLISH')]
    if   it=='ADMIN'   and 'ENGLISH' in others: v='ADMIN_ITEMS_ENG_PARTS'
    elif it=='ADMIN':                            v='ADMIN'
    elif it=='ENGLISH' and 'ADMIN' in others:    v='ENG_ITEMS_ADMIN_PARTS'
    elif it=='ENGLISH':                          v='ENGLISH'
    else:                                        v='INDETERMINATE'
    out.append([tb,v]+[per[c] for c in FIELDS]+[';'.join(sorted(scr)),tg.get(tb,{}).get('lang_tag','')])
w=csv.writer(io.open('/tmp/claude-1000/itbf/verdict.csv','w',encoding='utf-8',newline=''))
w.writerow(['table','verdict','item_text','option_text','instructions','section_prompt','scripts','lang_tag']); w.writerows(out)
for k,v in collections.Counter(r[1] for r in out).most_common(): print('  %-24s %d'%(k,v))
print('total',len(out))
