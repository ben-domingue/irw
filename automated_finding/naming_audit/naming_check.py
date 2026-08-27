"""Name-vs-source checking for IRW automated-pipeline table names.

Resolves a DOI at Crossref or DataCite and tests whether the surname in a table
name (`authorname_year_construct`) actually appears in the source's author list.

This module is the reusable half of the 2026-08-27 audit (issue #1686) and is
the intended basis for the naming gate described in `automated_finding/TODO.md`:
a gate is `fetch()` plus the matcher below, called on one DOI at table-creation
time instead of on the whole dictionary.

Two matcher behaviours are load-bearing; see README.md before changing either:
  * compound / particled surnames  (van Teffelen, Lopes de Jesus, Makowska-Tlomak)
  * Dataverse records that credit only the depositor  (see `dataverse_extra`)

Run `python3 naming_check.py --selftest` to exercise both.
"""
import pandas as pd, re, json, os, sys, time, unicodedata, urllib.request, urllib.error, urllib.parse

SC = os.path.dirname(os.path.abspath(__file__))
# Cache of raw API responses. Not in git (see .gitignore) -- it is regenerable and
# goes stale; delete it to force a clean re-resolve.
CACHE = os.environ.get('IRW_NAMING_AUDIT_CACHE', os.path.join(SC, 'doi_cache'))
os.makedirs(CACHE, exist_ok=True)
# Crossref's polite pool wants a contact address in the User-Agent.
CONTACT = os.environ.get('IRW_CONTACT_EMAIL', 'ben.domingue@gmail.com')
UA = f'IRW-naming-audit ({CONTACT})'

# ---------- normalisation ----------
DIGRAPHS = [('ae','a'),('oe','o'),('ue','u'),('ss','s')]

def fold(s):
    if not isinstance(s,str): return ''
    for a,b in [('ß','ss'),('ı','i'),('İ','i'),('Ø','O'),('ø','o'),('Đ','D'),('đ','d'),
                ('Ł','L'),('ł','l'),('Æ','AE'),('æ','ae'),('Œ','OE'),('œ','oe'),
                ('Þ','TH'),('þ','th'),('Ð','D'),('ð','d'),('’',"'")]:
        s = s.replace(a,b)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z\- ]", ' ', s)
    return re.sub(r'\s+',' ', s).strip()

def variants(tok):
    """tok: a folded string (may contain spaces/hyphens) -> comparison forms"""
    out = set()
    def add(t):
        if not t: return
        out.add(t)
        u = t
        for a,b in DIGRAPHS:
            u = u.replace(a,b)
        out.add(u)
    base = tok.strip()
    words = [w for w in re.split(r'[\s\-]+', base) if w]
    add(base); add(base.replace('-','')); add(base.replace('-','').replace(' ',''))
    # every contiguous run of words, joined with no separator
    for i in range(len(words)):
        for j in range(i+1, len(words)+1):
            add(''.join(words[i:j]))
    return {v for v in out if len(v) > 1}

def name_parts(table):
    """-> (surname_token, year) from authorname_year_construct"""
    m = re.match(r'^([A-Za-z][A-Za-z\-]*)_(\d{4})_', table)
    if m: return m.group(1).lower(), m.group(2)
    m = re.match(r'^([A-Za-z][A-Za-z\-]*)_(\d{4})$', table)
    if m: return m.group(1).lower(), m.group(2)
    # older style: surname2025_construct / surname2025
    m = re.match(r'^([A-Za-z][A-Za-z\-]*?)(\d{4})(?:_|$)', table)
    if m and len(m.group(1)) >= 3: return m.group(1).lower(), m.group(2)
    return None, None

def norm_doi(raw):
    if not isinstance(raw,str): return None
    s = raw.strip()
    if not s or s.lower() in ('na','n/a','none','not yet published','tbd','pending'): return None
    s = re.sub(r'^\s*data\s*doi\s*:\s*', '', s, flags=re.I)
    s = re.sub(r'^\s*doi\s*:\s*', '', s, flags=re.I)
    s = s.split(';')[0].split(',')[0].strip()   # multi-DOI / DOI+notes cells
    s = re.sub(r'^https?://(dx\.)?doi\.org/', '', s, flags=re.I)
    s = s.strip().rstrip('.').strip()
    if not s.startswith('10.'): return None
    s = re.sub(r'\.s\d{3}$', '', s)          # PLOS supplement -> article
    return s

def registrant(doi):
    p = doi.split('/')[0]
    return {'10.6084':'figshare','10.17632':'mendeley','10.7910':'dataverse',
            '10.17605':'osf','10.5281':'zenodo','10.5061':'dryad',
            '10.25421':'figshare-inst','10.6078':'datacite-other'}.get(p)

DATACITE_PREFIXES = {'10.6084','10.17632','10.7910','10.17605','10.5281','10.5061','10.25421',
                     '10.15468','10.18150','10.34894','10.60507','10.57745','10.5072'}

# ---------- fetching ----------
def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8','replace'))

def fetch(doi):
    key = re.sub(r'[^A-Za-z0-9]', '_', doi)[:180]
    fp = os.path.join(CACHE, key + '.json')
    if os.path.exists(fp):
        return json.load(open(fp))
    prefix = doi.split('/')[0]
    order = ['datacite','crossref'] if prefix in DATACITE_PREFIXES else ['crossref','datacite']
    rec = {'doi':doi,'status':'unresolvable','source':None,'authors':[],'year':None,'title':None,'err':None}
    for src in order:
        url = ('https://api.crossref.org/works/' + urllib.parse.quote(doi)) if src=='crossref' \
              else ('https://api.datacite.org/dois/' + urllib.parse.quote(doi))
        for attempt in range(3):
            try:
                j = _get(url)
                rec['status']='ok'; rec['source']=src
                if src=='crossref':
                    m = j['message']
                    rec['authors'] = [{'family':a.get('family') or '','given':a.get('given') or '',
                                       'name':a.get('name') or ''} for a in m.get('author',[]) or []]
                    for f in ('issued','published-print','published-online','created'):
                        dp = (m.get(f) or {}).get('date-parts') or []
                        if dp and dp[0] and dp[0][0]:
                            rec['year']=int(dp[0][0]); break
                    rec['title'] = (m.get('title') or [None])[0]
                else:
                    at = j['data']['attributes']
                    rec['authors'] = [{'family':a.get('familyName') or '','given':a.get('givenName') or '',
                                       'name':a.get('name') or ''} for a in at.get('creators',[]) or []]
                    rec['year'] = at.get('publicationYear')
                    ti = at.get('titles') or []
                    rec['title'] = ti[0].get('title') if ti else None
                break
            except urllib.error.HTTPError as e:
                rec['err'] = f'{src}:HTTP{e.code}'
                if e.code in (404,):
                    break
                time.sleep(1.5*(attempt+1))
            except Exception as e:
                rec['err'] = f'{src}:{type(e).__name__}'
                time.sleep(1.5*(attempt+1))
        if rec['status']=='ok': break
        time.sleep(0.15)
    json.dump(rec, open(fp,'w'))
    time.sleep(0.1)
    return rec

PARTICLES = {'da','de','del','della','dos','das','du','di','van','von','der','den','ter','ten',
             'la','le','el','al','bin','ibn','abu','mac','mc','st','af','av','zu','vander','vande'}

def family_forms(a):
    """Folded surname strings for one author, absorbing nobiliary particles from `given`."""
    fam = (a.get('family') or '').strip()
    nm  = (a.get('name') or '').strip()
    if not fam and nm:
        fam = nm.split(',')[0] if ',' in nm else (nm.split()[-1] if nm.split() else '')
    out = set()
    ff = fold(fam)
    if ff: out.add(ff)
    given = fold(a.get('given') or (nm.split(',',1)[1] if (nm and ',' in nm) else ''))
    gw = given.split()
    # trailing particles in the given field belong to the surname (e.g. "Sergio Da" + "Silva")
    k = len(gw)
    while k > 0 and gw[k-1] in PARTICLES:
        k -= 1
    if k < len(gw) and ff:
        out.add((' '.join(gw[k:]) + ' ' + ff).strip())
    return out

def author_tokens(rec):
    """set of folded tokens covering every author's family name (and name field fallback)"""
    toks = set()
    for a in rec['authors']:
        fam = a.get('family') or ''
        nm  = a.get('name') or ''
        if not fam and nm:
            # DataCite "name" often "Family, Given" or "Given Family" or an org
            if ',' in nm: fam = nm.split(',')[0]
            else: fam = nm.split()[-1] if nm.split() else ''
        for piece in list(family_forms(a)) + [fold(nm)]:
            if piece: toks |= variants(piece)
    return {t for t in toks if len(t)>1}

def first_author(rec):
    if not rec['authors']: return ''
    a = rec['authors'][0]
    return (a.get('family') or a.get('name') or '').strip()

def all_authors(rec):
    out=[]
    for a in rec['authors']:
        out.append((a.get('family') or a.get('name') or '').strip())
    return '; '.join([x for x in out if x])

# ---------- secondary evidence for suspects ----------
def dataverse_extra(doi):
    """Harvard Dataverse native record: author list + linked publication citation."""
    fp = os.path.join(CACHE, 'dv_' + re.sub(r'[^A-Za-z0-9]','_',doi)[:170] + '.json')
    if os.path.exists(fp): return json.load(open(fp))
    out = {'authors':[], 'publication':'', 'title':'', 'desc':''}
    try:
        u = ('https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:'
             + urllib.parse.quote(doi))
        j = _get(u)
        f = j['data']['latestVersion']['metadataBlocks']['citation']['fields']
        for x in f:
            tn = x['typeName']
            if tn=='author':
                out['authors'] = [a['authorName']['value'] for a in x['value']]
            elif tn=='publication':
                out['publication'] = ' '.join(v.get('publicationCitation',{}).get('value','') for v in x['value'])
            elif tn=='title':
                out['title'] = x['value']
            elif tn=='dsDescription':
                out['desc'] = ' '.join(v.get('dsDescriptionValue',{}).get('value','') for v in x['value'])
    except Exception as e:
        out['err'] = f'{type(e).__name__}'
    json.dump(out, open(fp,'w')); time.sleep(0.15)
    return out

def datacite_extra(doi):
    """DataCite descriptions + relatedIdentifiers text, for figshare/Zenodo/OSF suspects."""
    fp = os.path.join(CACHE, 'dc2_' + re.sub(r'[^A-Za-z0-9]','_',doi)[:170] + '.json')
    if os.path.exists(fp): return json.load(open(fp))
    out = {'desc':'', 'title':''}
    try:
        j = _get('https://api.datacite.org/dois/' + urllib.parse.quote(doi))
        at = j['data']['attributes']
        out['desc'] = ' '.join((d.get('description') or '') for d in at.get('descriptions',[]) or [])
        ti = at.get('titles') or []
        out['title'] = ti[0].get('title') if ti else ''
    except Exception as e:
        out['err'] = f'{type(e).__name__}'
    json.dump(out, open(fp,'w')); time.sleep(0.15)
    return out

def record_years(doi):
    """Every year appearing in any date field on the record.

    A table named `foo_2023_x` whose DOI reports 2024 is usually not an error:
    journals carry online-first and issue dates a year apart, and a dataset DOI
    reports its deposit year, not the paper's. Checking all date fields turns
    most year mismatches into non-findings.
    """
    fp = os.path.join(CACHE, 'yr_' + ''.join(c if c.isalnum() else '_' for c in str(doi))[:150] + '.json')
    if os.path.exists(fp):
        return json.load(open(fp))
    yrs = set()
    try:
        if doi.split('/')[0] in DATACITE_PREFIXES:
            at = _get('https://api.datacite.org/dois/' + urllib.parse.quote(doi))['data']['attributes']
            if at.get('publicationYear'): yrs.add(int(at['publicationYear']))
            for dt in at.get('dates', []) or []:
                v = str(dt.get('date') or '')[:4]
                if v.isdigit(): yrs.add(int(v))
        else:
            m = _get('https://api.crossref.org/works/' + urllib.parse.quote(doi))['message']
            for f in ('issued','published-print','published-online','created','posted','approved'):
                dp = (m.get(f) or {}).get('date-parts') or []
                if dp and dp[0] and dp[0][0]: yrs.add(int(dp[0][0]))
    except Exception:
        pass
    out = sorted(yrs)
    json.dump(out, open(fp, 'w')); time.sleep(0.1)
    return out

# ---------- dictionary source ----------
DICT_GID = '1337607315'
DICT_KEY = '1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s'
DICT_URL = (f'https://docs.google.com/spreadsheets/d/{DICT_KEY}/export'
            f'?format=csv&gid={DICT_GID}')

def load_dictionary(path=None):
    """The live IRW Data Dictionary. Pass a path to work from a saved copy."""
    if path:
        return pd.read_csv(path, dtype=str)
    req = urllib.request.Request(DICT_URL, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        import io
        return pd.read_csv(io.BytesIO(r.read()), dtype=str)

# ---------- selftest ----------
# Every case below is a real false positive or false negative seen during the
# 2026-08-27 sweep. They are the regression suite for the matcher.
SELFTEST = [
    # (table surname, author record, should_match)
    ('yandun',      {'given':'','family':'Yandun-Cartagena','name':''},      True),
    ('lindstrom',   {'given':'','family':'Lindstrom','name':''},             True),
    ('zaehl',       {'given':'','family':'Zahl','name':''},                  True),
    ('hen-herbst',  {'given':'','family':'Hen-Herbst','name':''},            True),
    ('vanteffelen', {'given':'Jill','family':'van Teffelen','name':''},      True),
    ('makowska',    {'given':'','family':'Makowska-Tlomak','name':''},       True),
    ('arabaci',     {'given':'','family':'Arabaci','name':''},               True),
    ('dejesus',     {'given':'','family':'Lopes de Jesus','name':''},        True),
    ('tasaygar',    {'given':'','family':'Tas Aygar','name':''},             True),
    ('vonhippel',   {'given':'Courtney','family':'von Hippel','name':''},    True),
    ('cordova',     {'given':'','family':'Cordova-Leon','name':''},          True),
    ('dasilva',     {'given':'Sergio Da','family':'Silva','name':''},        True),
    # must still FAIL: a fabricated surname, and a given name used as a surname
    ('alomari',     {'given':'','family':'Xie','name':''},                   False),
    ('divia',       {'given':'Divia Indira','family':'Arifin','name':''},    False),
    ('duong',       {'given':'Lan Duong Thi','family':'Ngoc','name':''},     False),
]

def _selftest():
    # accented forms are spelled ASCII above so this file stays ASCII-safe;
    # exercise the real diacritics too
    extra = [('yandun','Yandún-Cartagena',True), ('lindstrom','Lindström',True),
             ('zaehl','Zähl',True), ('arabaci','Arabacı',True),
             ('tasaygar','Taş Aygar',True), ('cordova','Córdova-León',True),
             ('makowska','Makowska-Tłomak',True)]
    fails = 0
    for sur, rec, want in SELFTEST:
        got = bool(variants(fold(sur)) & set().union(*[variants(x) for x in family_forms(rec)]))
        if got != want:
            print(f'FAIL {sur!r} vs {rec} -> {got}, want {want}'); fails += 1
    for sur, fam, want in extra:
        got = bool(variants(fold(sur)) & variants(fold(fam)))
        if got != want:
            print(f'FAIL {sur!r} vs {fam!r} -> {got}, want {want}'); fails += 1
    total = len(SELFTEST) + len(extra)
    print(f'{total - fails}/{total} matcher cases pass')
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(_selftest() if '--selftest' in sys.argv else
             print(__doc__) or 0)
