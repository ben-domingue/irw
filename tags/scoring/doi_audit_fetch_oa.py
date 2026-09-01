#!/usr/bin/env python3
"""Resolve every distinct dictionary DOI against OpenAlex (batched, polite pool)."""
import csv, re, json, time, sys, requests

MAILTO = "ben.domingue@gmail.com"
UA = {"User-Agent": f"irw-doi-audit/1.0 (mailto:{MAILTO})"}

def norm_doi(d):
    d = (d or '').strip().rstrip('.').lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = re.sub(r'^doi:\s*', '', d)
    return d.strip()

rows = list(csv.DictReader(open('dict.csv')))
dois = {}
for r in rows:
    d = norm_doi(r['DOI (for paper)'])
    if not d or ' ' in d or not d.startswith('10.'):
        continue
    dois.setdefault(d, []).append(r['table'])

keys = sorted(dois)
print('distinct resolvable DOIs:', len(keys), file=sys.stderr)

out = {}
B = 40
for i in range(0, len(keys), B):
    batch = keys[i:i+B]
    url = ("https://api.openalex.org/works?per-page=100&mailto=" + MAILTO +
           "&select=doi,title,publication_year,authorships,type,primary_location"
           "&filter=doi:" + "|".join("https://doi.org/" + d for d in batch))
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 200:
                break
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            time.sleep(3 * (attempt + 1))
    else:
        print('FAILED batch', i, file=sys.stderr); continue
    for w in r.json().get('results', []):
        d = norm_doi(w.get('doi') or '')
        auths = [a['author'].get('display_name') or '' for a in w.get('authorships', [])]
        loc = (w.get('primary_location') or {}).get('source') or {}
        out[d] = {'title': w.get('title'), 'year': w.get('publication_year'),
                  'authors': auths, 'type': w.get('type'),
                  'venue': loc.get('display_name')}
    print(f'{i+len(batch)}/{len(keys)} resolved so far {len(out)}', file=sys.stderr)
    time.sleep(0.6)

json.dump({'resolved': out, 'doi_tables': dois}, open('openalex.json','w'))
print('resolved', len(out), 'of', len(keys), file=sys.stderr)
