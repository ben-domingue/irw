#!/usr/bin/env python3
"""Pass 1: internal three-way consistency of DOI / Reference / URL (no network)."""
import csv, re, json, collections

DOI_RE = re.compile(r'\b10\.\d{4,9}/[^\s"<>,;)\]]+', re.I)

def norm_doi(d):
    d = d.strip().rstrip('.').rstrip(')').rstrip(',').lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = re.sub(r'^doi:\s*', '', d)
    return d

def extract(text):
    out = []
    for m in DOI_RE.findall(text or ''):
        out.append(norm_doi(m))
    return out

rows = list(csv.DictReader(open('dict.csv')))
findings = []
for r in rows:
    doi = norm_doi(r['DOI (for paper)'] or '')
    if not doi:
        continue
    ref = r['Reference'] or ''
    url = r['URL (for data)'] or ''
    ref_dois = set(extract(ref))
    url_dois = set(extract(url))
    others = (ref_dois | url_dois) - {doi}
    if not others:
        continue
    # tolerate prefix/suffix relationships (e.g. trailing .v2, url-encoded)
    others = {o for o in others if not (o.startswith(doi) or doi.startswith(o))}
    if not others:
        continue
    findings.append({
        'table': r['table'], 'doi': doi,
        'competing_dois': ';'.join(sorted(others)),
        'in_reference': ';'.join(sorted(ref_dois - {doi})),
        'in_url': ';'.join(sorted(url_dois - {doi})),
        'reference': ref, 'url': url, 'contributor': r.get('Contributor',''),
    })
json.dump(findings, open('pass1.json','w'), indent=1)
print('pass1 flagged rows:', len(findings))
print('distinct dois:', len({f['doi'] for f in findings}))
for f in findings[:40]:
    print(f['table'], '|', f['doi'], '-> competing:', f['competing_dois'])
