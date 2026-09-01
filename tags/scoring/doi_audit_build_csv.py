#!/usr/bin/env python3
import csv, re, json

rows = list(csv.DictReader(open('dict.csv')))
oa = json.load(open('openalex.json'))['resolved']

def nd(d):
    d = (d or '').strip().rstrip('.').lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    return re.sub(r'^doi:\s*', '', d).strip()

by_table = {r['table']: r for r in rows}

# Confirmed mismatch clusters: batch head is correct, every later row drag-filled +1
CLUSTERS = {
    'goksel_2026_embarrassment':  ('10.1037/pspa0000477', 'Goksel/JPSP:PPID'),
    'hyatt_2023_aggression':      ('10.1002/ab.22088',    'Hyatt/Aggressive Behavior'),
    'west_2021_retaliatory':      ('10.1037/mot0000248',  'West/Motivation Science'),
    'kazarovytska_2026_ingroup':  ('10.1037/pspi0000513', 'Kazarovytska/JPSP:IRGP'),
}
SINGLETONS = {
    'andrich_mudfold': ('DOI resolves to Millsap 1988, a different article in the same '
                        'APM issue as the cited Andrich 1988 paper', 'high'),
    'cdm_timss03':     ('DOI resolves to Sia et al. 2018 (IJSME); Reference cites Su et al. '
                        '2013 CASMA technical report, an unrelated work', 'high'),
}

out = []
for tab, r in by_table.items():
    doi = nd(r['DOI (for paper)'])
    if not doi:
        continue
    meta = oa.get(doi)
    hit = None
    for pref, (correct, label) in CLUSTERS.items():
        if tab.startswith(pref) and doi != correct:
            hit = ('cluster', label, correct, 'high')
    if tab in SINGLETONS and hit is None:
        hit = ('singleton', SINGLETONS[tab][0], '', SINGLETONS[tab][1])
    if not hit:
        continue
    kind, label, proposed, conf = hit
    out.append({
        'table': tab,
        'cluster': label if kind == 'cluster' else '(isolated)',
        'tables_in_cluster': '',
        'doi_in_dictionary': doi,
        'openalex_title': (meta or {}).get('title', 'UNRESOLVED'),
        'openalex_authors': '; '.join((meta or {}).get('authors', [])[:5]),
        'openalex_year': (meta or {}).get('year', ''),
        'openalex_venue': (meta or {}).get('venue', ''),
        'reference': ' '.join((r['Reference'] or '').split()),
        'url_for_data': r['URL (for data)'],
        'contributor': r.get('Contributor', ''),
        'flagged_by': ('pass1-structural (same Reference+URL, sequential DOIs) + '
                       'pass2-openalex' if kind == 'cluster' else 'pass2-openalex'),
        'proposed_correction': proposed,
        'confidence': conf,
    })

counts = {}
for o in out:
    counts[o['cluster']] = counts.get(o['cluster'], 0) + 1
for o in out:
    o['tables_in_cluster'] = counts[o['cluster']]

out.sort(key=lambda o: (-o['tables_in_cluster'], o['cluster'], o['doi_in_dictionary']))
cols = list(out[0].keys())
path = '/home/ben/Dropbox/projects/irw/src/tags/scoring/doi_reference_mismatch_audit.csv'
with open(path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(out)
print('wrote', path, len(out), 'rows')
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {v:3d}  {k}')
