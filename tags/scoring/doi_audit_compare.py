#!/usr/bin/env python3
import csv, re, json, unicodedata, collections

D = json.load(open('openalex.json'))
res, doi_tables = D['resolved'], D['doi_tables']
rows = list(csv.DictReader(open('dict.csv')))

def norm_doi(d):
    d = (d or '').strip().rstrip('.').lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    return re.sub(r'^doi:\s*', '', d).strip()

ref_by_doi, url_by_doi = {}, {}
for r in rows:
    d = norm_doi(r['DOI (for paper)'])
    if d:
        ref_by_doi.setdefault(d, set()).add((r['Reference'] or '').strip())
        url_by_doi.setdefault(d, set()).add((r['URL (for data)'] or '').strip())

def deacc(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(c))

STOP = set('a an the of and or in on for to with by from at as is are be into using use study data dataset '
           'replication using new its their our this that between among across effects effect analysis '.split())
def toks(s):
    return [w for w in re.findall(r"[a-z]+", deacc(s or '').lower()) if len(w) > 3 and w not in STOP]

DATA_PREF = ('10.7910/', '10.17605/', '10.31234/', '10.31219/', '10.5281/', '10.5061/',
             '10.6084/', '10.5255/', '10.3886/', '10.17632/', '10.34894/', '10.5683/',
             '10.48668/', '10.33009/', '10.32614/', '10.18712/', '10.4232/', '10.17026/',
             '10.57760/', '10.57903/', '10.17608/', '10.23668/', '10.7802/', '10.21979/',
             '10.60507/', '10.25349/', '10.24433/')

out = []
for doi, meta in res.items():
    tables = sorted(set(doi_tables.get(doi, [])))
    refs = [x for x in ref_by_doi.get(doi, set()) if x]
    if not refs:
        continue
    ref = max(refs, key=len)
    reflow = deacc(ref).lower()
    surnames = []
    for a in meta['authors']:
        parts = deacc(a).split()
        if parts:
            surnames.append(parts[-1].lower())
    auth_hit = any(re.search(r'\b' + re.escape(s) + r'\b', reflow) for s in surnames if len(s) > 2)
    tt = toks(meta['title'])
    rt = set(toks(ref))
    overlap = (sum(1 for w in tt if w in rt) / len(tt)) if tt else 0.0
    yrs = set(re.findall(r'(?:19|20)\d{2}', ref))
    yr_hit = (str(meta['year']) in yrs) if meta['year'] else False
    is_data = doi.startswith(DATA_PREF) or (meta.get('type') == 'dataset')
    out.append({'doi': doi, 'tables': tables, 'n_tables': len(tables),
                'oa_title': meta['title'], 'oa_year': meta['year'],
                'oa_authors': '; '.join(meta['authors'][:6]),
                'oa_venue': meta.get('venue'), 'oa_type': meta.get('type'),
                'reference': ref, 'url': sorted(url_by_doi.get(doi, {''}))[0],
                'auth_hit': auth_hit, 'title_overlap': round(overlap, 2),
                'year_hit': yr_hit, 'is_data_doi': is_data})

json.dump(out, open('compared.json','w'), indent=1)
sus = [o for o in out if not o['auth_hit'] and o['title_overlap'] < 0.34]
print('compared:', len(out))
print('suspects (no author match AND low title overlap):', len(sus),
      'tables:', sum(o['n_tables'] for o in sus))
print(' of which data-repo DOIs:', sum(1 for o in sus if o['is_data_doi']))
for o in sorted(sus, key=lambda x: -x['n_tables'])[:60]:
    print(f"{o['n_tables']:3d} {'D' if o['is_data_doi'] else ' '} {o['doi']}")
    print(f"     OA : {o['oa_title']} | {o['oa_authors'][:60]} | {o['oa_year']} | {o['oa_type']}")
    print(f"     REF: {o['reference'][:150]}")
