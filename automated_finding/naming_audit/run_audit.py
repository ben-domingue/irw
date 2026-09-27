#!/usr/bin/env python3
"""Sweep the IRW Data Dictionary and verdict every automated-pipeline table name.

    python3 run_audit.py                      # full sweep, live dictionary
    python3 run_audit.py --date 6/23/2026     # one upload batch
    python3 run_audit.py --dict dict.csv      # from a saved copy, no sheet fetch

Writes audit_<tag>.csv (one row per table, every verdict including `ok`).
Feed that to finalize.py to produce the reviewed suspects file.

WHICH rows to audit comes from the dictionary's intake columns (`Contributor`,
`Date`), which only the entry surfaces carry: the sheet, plus
`dictionary_auto.csv`, whose rows need not ever be pasted into the sheet. WHAT each
row says -- its DOI and Reference -- comes from the published export,
`metadata/*biblio*.csv`, wherever the table has reached it (#2067). The export
carries corrections the sheet never receives, and an audit of the names users
see should read the citations users see. `values_from` in the output says
which record supplied each row.

Cost: ~1 HTTP GET per distinct DOI, throttled. A cold full sweep is ~1,900
requests / 4-6 min; with a warm doi_cache/ only new rows hit the network.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from naming_check import *
from doi_hygiene import classify
from published_dictionary import load_auto_rows, load_published

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

    # A data-repository DOI cannot support EITHER screen, so an adverse verdict
    # from one is not evidence about the table's name (#1690). Its creators are
    # the depositor -- for Dataverse frequently a different person from the
    # paper's authors, which is why `cavojova_2017_cfc` and `cosenza_2015_cfc`
    # both read as fabricated and both are correctly named -- and its year is a
    # deposit year, which produced 47 of this audit's 65 year_mismatch flags.
    #
    # Reported rather than dropped: the row still needs a real paper DOI, and
    # `ok` would say it had been checked.
    if out['verdict'] != 'ok' and classify(doi) == 'data_doi':
        out['verdict'] = 'data_doi_unverifiable'
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', help='restrict to one dictionary Date value (upload batch)')
    ap.add_argument('--dict', help='path to a saved dictionary CSV (default: fetch live sheet)')
    ap.add_argument('--contributor', default='automated')
    ap.add_argument('--out', help='output path (default: audit_<tag>.csv beside this script)')
    args = ap.parse_args()

    d = load_dictionary(args.dict)
    # dictionary_auto.csv rows need not be on the sheet; a sheet row wins where
    # both name a table, as it does in the export (dict_union.R).
    auto = pd.DataFrame(list(load_auto_rows().values()), dtype=str)
    if len(auto):
        seen = set(d['table'].fillna('').str.lower())
        auto = auto[~auto['table'].fillna('').str.lower().isin(seen)]
        d = pd.concat([d, auto[[c for c in auto.columns if c in d.columns]]],
                      ignore_index=True)
    a = d[d['Contributor'].fillna('') == args.contributor].copy()
    if args.date:
        a = a[a['Date'] == args.date].copy()
    print(f'dictionary rows: {len(d)} (incl. {len(auto)} from dictionary_auto.csv); '
          f'contributor={args.contributor!r}: {len(a)}', file=sys.stderr)

    published = load_published()
    rows, sources = [], {}
    for i, (_, r) in enumerate(a.iterrows()):
        rec = published.get(str(r['table']).strip().lower())
        if rec is not None:
            # A data DOI moved to its own column by the export is still the
            # row's only DOI; classify() below reports it as unverifiable.
            doi_raw, ref, src = rec['doi'] or rec['data_doi'], rec['reference'], rec['file']
        else:
            doi_raw = r['DOI (for paper)']
            ref = r['Reference'] if isinstance(r['Reference'], str) else ''
            src = 'dictionary entry (not yet exported)'
        row = verdict_row(r['table'], doi_raw, ref, r['Date'])
        row['values_from'] = src
        sources[src] = sources.get(src, 0) + 1
        rows.append(row)
        if (i + 1) % 100 == 0:
            print(f'{i+1}/{len(a)}', file=sys.stderr, flush=True)

    df = pd.DataFrame(rows)
    print('values from: ' + ', '.join(f'{k} {v}' for k, v in sorted(sources.items())),
          file=sys.stderr)
    tag = (args.date or 'all').replace('/', '-')
    out = args.out or os.path.join(SC, f'audit_{tag}.csv')
    df.to_csv(out, index=False)
    print(df['verdict'].value_counts().to_string())
    print(f'\nwrote {out} ({len(df)} rows)')

if __name__ == '__main__':
    main()
