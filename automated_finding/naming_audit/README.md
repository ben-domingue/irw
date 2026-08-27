# naming_audit

Checks a claim the pipeline makes everywhere and verifies nowhere: that the
`authorname` in a table named `authorname_year_construct` is really the source
paper's first author.

Nothing downstream can catch a wrong surname. The name propagates into the
Redivis table, the `__items` item-text table, the dictionary sheet and the tags
sheet, none of which independently store the author — so an invented name is
silent, and because renaming spans six systems with no transaction across them,
effectively permanent.

Built for the 2026-08-27 sweep behind
[issue #1686](https://github.com/ben-domingue/irw/issues/1686). Findings and the
decision that came out of it are in `../naming_audit_README.md` and
`../naming_audit_suspects.csv`.

## Use

```bash
python3 naming_check.py --selftest        # 22 matcher regression cases
python3 run_audit.py                      # full sweep against the live dictionary
python3 run_audit.py --date 6/23/2026     # one upload batch
python3 finalize.py audit_all.csv -o suspects.csv
```

`run_audit.py` fetches the dictionary sheet itself; `--dict path.csv` works from
a saved copy instead. Every API response is cached in `doi_cache/` (gitignored),
so a cold full sweep is ~1,900 requests / 4-6 min and a warm re-run only pays
for rows that are new.

Set `IRW_CONTACT_EMAIL` to change the User-Agent contact (Crossref's polite pool
wants one); `IRW_NAMING_AUDIT_CACHE` relocates the cache.

## How it works

**Screen 1** (free, no network) compares the surname to the dictionary's own
`Reference` string. It clears ~99.7% of rows but has a fatal blind spot: a
fabricated name written into *both* the table name and the `Reference` is
self-consistent and invisible. That is exactly what the 8/12/2026 batch did. It
is a pre-filter, never the answer.

**Screen 2** resolves the DOI — Crossref, or DataCite for figshare, Mendeley,
Dataverse, OSF, Zenodo and Dryad — and compares the surname against the **full**
author list, flagging only names absent from it entirely. That is what found
every real error.

Verdicts are documented in `../naming_audit_README.md`.

## Two things you must not "simplify"

Both produced real false positives during the sweep, and both fail *silently* —
a broken matcher does not error, it confidently accuses correctly-named tables.
`naming_check.py --selftest` covers both; run it after touching `fold()`,
`variants()` or `family_forms()`.

1. **Compound and particled surnames.** Matching only Crossref's `family` field
   falsely flags `van Teffelen`, `Lopes de Jesus`, `Makowska-Tłomak`,
   `von Hippel` and ~35 others. The matcher folds accents *and* German/Nordic
   digraphs, maps Turkish dotless `ı` explicitly (it has no NFKD decomposition),
   allows hyphens in the surname token, matches every contiguous run of surname
   words joined without separators, and absorbs trailing nobiliary particles
   from the `given` field so `Sergio Da` + `Silva` → `dasilva`.
2. **Dataverse credits only the depositor.** `cavojova_2017_cfc` and
   `cosenza_2015_cfc` look fabricated against the creator list but are correct
   per each record's linked publication — read via `dataverse_extra()`. A gate
   that reads only creators will produce confident false accusations.

Guarding against over-correction, the selftest also pins three cases that must
*keep* failing: `alomari`/Xie (fabricated), `divia`/Arifin (given name used as a
surname), `duong`/Ngoc (Vietnamese name order).

## The adjudications block

`finalize.py` carries `ADJUDICATIONS_2026_08_27` — hand-checked, case-by-case
calls made by reading source records on that date. **It is a snapshot of one
review, not policy.** It is kept so the published CSV is reproducible. On a
later sweep, re-derive rather than assume, and don't extend it without checking
the source yourself.

## Relation to the naming gate

The gate in `../TODO.md` is `fetch()` plus this matcher, called on one DOI at
table-creation time instead of on 1,945 rows — when the name is still free to
change and nothing references it yet. This module is meant to be its basis, so
the two traps above don't have to be rediscovered. **The gate is proposed, not
scheduled — don't implement it unprompted.**
