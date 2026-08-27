#!/usr/bin/env python3
"""Sweep the IRW Data Dictionary and verdict every automated-pipeline table name.

    python3 run_audit.py                      # full sweep, live dictionary
    python3 run_audit.py --date 6/23/2026     # one upload batch
    python3 run_audit.py --dict dict.csv      # from a saved copy, no sheet fetch

Writes audit_<tag>.csv (one row per table, every verdict including `ok`).
Feed that to finalize.py to produce the reviewed suspects file.

Cost: ~1 HTTP GET per distinct DOI, throttled. A cold full sweep is ~1,900
requests / 4-6 min; with a warm doi_cache/ only new rows hit the network.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from naming_check import *

def verdict_row(tbl, doi_raw, ref, date):
    """Verdict one dictionary row. Pure apart from fetch()'s cached HTTP."""
    sur, yr = name_parts(tbl)
    doi = norm_doi(doi_raw)
    out = dict(table=tbl, name_surname=sur or '', name_year=yr or '',
               resolved_first_author='', resolved_all_authors='', resolved_year='',
               resolved_title='', doi=doi or '', registrant=registrant(doi) if doi else '',
               verdict='', batch_date=date, reference=ref, doi_raw=doi_raw or '')
    # Screen 1 (free): does the surname appear in the row's own Reference string?
    # Cheap pre-filter only -- a fabricated name written into BOTH fields is
    # self-consistent and invisible here. That is why Screen 2 exists.
    if sur and ref:
        reftoks = set()
        for w in fold(ref).split():
            reftoks |= variants(w.strip('-'))
        out['screen1_ref_match'] = bool(variants(fold(sur)) & reftoks)
    else:
        out['screen1_ref_match'] = None

    if sur is None:
        out['verdict'] = 'not_author_named'; return out
    if not doi:
        out['verdict'] = 'no_doi'; return out
    rec = fetch(doi)
    if rec['status'] != 'ok':
        out['verdict'] = 'unresolvable'; out['err'] = rec.get('err'); return out

    # Screen 2: compare against the resolved author list.
    out['resolved_first_author'] = first_author(rec)
    out['resolved_all_authors']  = all_authors(rec)
    out['resolved_year']         = rec['year'] or ''
    out['resolved_title']        = rec.get('title') or ''
    sv   = variants(fold(sur))
    toks = author_tokens(rec)                      # every author, surname forms
    fa   = set()                                   # first author only
    if rec['authors']:
        for piece in family_forms(rec['authors'][0]):
            fa |= variants(piece)
    given = set()                                  # given names, any author
    for au in rec['authors']:
        g = au.get('given') or ''
        if not g and au.get('name') and ',' in au['name']:
            g = au['name'].split(',', 1)[1]
        for w in fold(g).split():
            given |= variants(w)
    year_ok = (str(rec['year']) == yr) if rec['year'] else None

    if not (sv & toks):                out['verdict'] = 'name_absent_from_authors'
    elif not (sv & fa) and (sv & given):out['verdict'] = 'given_name_used'
    elif not (sv & fa):                out['verdict'] = 'non_first_author'
    elif year_ok is False:             out['verdict'] = 'year_mismatch'
    else:                              out['verdict'] = 'ok'
    out['year_ok'] = year_ok
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', help='restrict to one dictionary Date value (upload batch)')
    ap.add_argument('--dict', help='path to a saved dictionary CSV (default: fetch live sheet)')
    ap.add_argument('--contributor', default='automated')
    ap.add_argument('--out', help='output path (default: audit_<tag>.csv beside this script)')
    args = ap.parse_args()

    d = load_dictionary(args.dict)
    a = d[d['Contributor'].fillna('') == args.contributor].copy()
    if args.date:
        a = a[a['Date'] == args.date].copy()
    print(f'dictionary rows: {len(d)}; contributor={args.contributor!r}: {len(a)}', file=sys.stderr)

    rows = []
    for i, (_, r) in enumerate(a.iterrows()):
        rows.append(verdict_row(r['table'], r['DOI (for paper)'],
                                r['Reference'] if isinstance(r['Reference'], str) else '',
                                r['Date']))
        if (i + 1) % 100 == 0:
            print(f'{i+1}/{len(a)}', file=sys.stderr, flush=True)

    df = pd.DataFrame(rows)
    tag = (args.date or 'all').replace('/', '-')
    out = args.out or os.path.join(SC, f'audit_{tag}.csv')
    df.to_csv(out, index=False)
    print(df['verdict'].value_counts().to_string())
    print(f'\nwrote {out} ({len(df)} rows)')

if __name__ == '__main__':
    main()
