#!/usr/bin/env python3
"""Turn run_audit.py's raw verdicts into the reviewed suspects file.

    python3 finalize.py [audit_all.csv] [-o naming_audit_suspects.csv]

Two things happen here that run_audit.py deliberately does not do:

  1. Automatic follow-ups -- resolve a DOI from the URL column when the DOI cell
     is empty, and downgrade a year mismatch when the name's year matches some
     other date field on the record (online-first vs issue).
  2. ADJUDICATIONS_2026_08_27 -- hand-checked, case-by-case calls.

*** The adjudications block is a SNAPSHOT OF ONE REVIEW, NOT POLICY. ***
Each entry was verified by reading the source record on 2026-08-27. It is
correct for that sweep and is kept so the published CSV is reproducible. It is
NOT a rule set: on a later sweep, re-derive these rather than assuming they
still hold, and do not extend the block without checking the source yourself.
"""
import sys, os, argparse, pandas as pd, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from naming_check import *

_ap = argparse.ArgumentParser()
_ap.add_argument('audit_csv', nargs='?', default=os.path.join(SC,'audit_all.csv'))
_ap.add_argument('-o','--out', default=os.path.join(SC,'naming_audit_suspects.csv'))
_ap.add_argument('--dict', default=None,
                 help='saved dictionary CSV; default fetches the live sheet')
ARGS = _ap.parse_args()

if not os.path.exists(ARGS.audit_csv):
    sys.exit(f"{ARGS.audit_csv} not found -- run `python3 run_audit.py` first "
             f"to produce it, or pass the path explicitly.")

d = pd.read_csv(ARGS.audit_csv, dtype=str)

# ===================== ADJUDICATIONS_2026_08_27 (snapshot, not policy) =========
CLEARED = {  # table-prefix -> reason (secondary evidence shows the name is correct)
 'cavojova_2017_cfc': 'Dataverse lists only depositor Jurkovic; linked publication is Cavojova & Jurkovic (2017)',
 'cosenza_2015_cfc' : 'Dataverse lists only depositor Nigro; linked publication is Cosenza & Nigro (2015)',
}
RECLASS = {
 'villarrealzegarra2026_trif': ('non_first_author',
   'Villareal-Zegarra is 2nd author; table spells it with -rr-, source record with -r-'),
 'duong_2025_tbl_experience': ('name_order_ambiguous',
   'Vietnamese name "Lan Duong Thi Ngoc" parsed by Crossref as family=Ngoc; Duong is plausibly the family name'),
 'duong_2025_tbl_confidence': ('name_order_ambiguous',
   'Vietnamese name "Lan Duong Thi Ngoc" parsed by Crossref as family=Ngoc; Duong is plausibly the family name'),
}
notes = {}
for t,(v,n) in RECLASS.items():
    d.loc[d.table==t,'verdict']=v; notes[t]=n
for t,n in CLEARED.items():
    d.loc[d.table==t,'verdict']='ok'; notes[t]=n
# goldberg_2018_* : ESCS corpus PI, deposits credited to Saucier
m = d.table.str.startswith('goldberg_2018_') & (d.verdict=='name_absent_from_authors')
d.loc[m,'verdict']='named_for_corpus_pi'
for t in d.loc[m,'table']:
    notes[t]='Eugene-Springfield Community Sample (Goldberg corpus); Dataverse creator of record is Gerard Saucier'

# ===================== end adjudications ======================================

# year-mismatch severity: table year present in some other date field on the record?
def yrs_for(doi):
    return record_years(str(doi))

for i,r in d[d.verdict=='year_mismatch'].iterrows():
    if int(r['name_year']) in yrs_for(r['doi']):
        d.loc[i,'verdict']='ok'
        notes[r['table']]='name year matches a non-issued date field (online-first / deposit date) on the record'
    else:
        notes[r['table']]='name year vs record year differ; DOI column often holds the dataset DOI, whose year is the deposit year'

# --- URL fallback for rows with no usable DOI cell ---
import urllib.parse as _up
_dic = load_dictionary(ARGS.dict).set_index('table')
for i, r in d[d.verdict=='no_doi'].iterrows():
    url = str(_dic.loc[r['table'], 'URL (for data)'])
    cand = None
    m = re.search(r'figshare\.com/articles/[^/]+/(?:.*?/)?(\d{6,})', url)
    if m: cand = '10.6084/m9.figshare.' + m.group(1)
    m2 = re.search(r'osf\.io/([a-z0-9]{5})', url)
    if not cand and m2: cand = '10.17605/osf.io/' + m2.group(1).upper()
    m3 = re.search(r'persistentId=doi:([^&\s]+)', url) or re.search(r'doi\.org/(10\.[^\s]+)', url)
    if not cand and m3: cand = _up.unquote(m3.group(1))
    if not cand:
        notes[r['table']] = 'no DOI in the sheet and none derivable from the URL column'; continue
    rec = fetch(cand)
    if rec['status'] != 'ok':
        d.loc[i,'verdict'] = 'no_doi_unverifiable'
        notes[r['table']] = f'DOI cell empty; URL implies {cand}, which is not registered with Crossref or DataCite'
        continue
    d.loc[i,'resolved_first_author'] = first_author(rec)
    d.loc[i,'resolved_all_authors']  = all_authors(rec)
    d.loc[i,'resolved_year']         = str(rec['year'] or '')
    d.loc[i,'doi']                   = cand
    if variants(fold(r['name_surname'])) & author_tokens(rec):
        d.loc[i,'verdict'] = 'ok'
        notes[r['table']] = f'DOI cell empty; name verified against {cand} derived from the URL column'
    else:
        d.loc[i,'verdict'] = 'name_absent_from_authors'
        notes[r['table']] = f'DOI cell empty; checked against {cand} derived from the URL column'

d['note']=d['table'].map(notes).fillna('')
SUSPECT = {'name_absent_from_authors','non_first_author','given_name_used','year_mismatch',
           'unresolvable','no_doi','no_doi_unverifiable','not_author_named','named_for_corpus_pi','name_order_ambiguous'}
out = d[d.verdict.isin(SUSPECT)].copy()
cols = ['table','name_surname','name_year','resolved_first_author','resolved_all_authors',
        'resolved_year','doi','registrant','verdict','batch_date','note']
for c in cols:
    if c not in out.columns: out[c]=''
order = {'name_absent_from_authors':0,'given_name_used':1,'non_first_author':2,'named_for_corpus_pi':3,
         'name_order_ambiguous':4,'year_mismatch':5,'no_doi':6,'no_doi_unverifiable':6,'unresolvable':7,'not_author_named':8}
out['_o']=out.verdict.map(order)
out = out.sort_values(['_o','table'])[cols]
out.to_csv(ARGS.out, index=False)
print(d.verdict.value_counts().to_string())
print('\nsuspects file rows:', len(out))
