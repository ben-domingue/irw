# Task: audit IRW table names against their sources (issue #1686)

Work in `/home/ben/Dropbox/projects/irw/src`. Read `automated_finding/README.md` and
`CLAUDE.md` first for repo conventions.

## Background

IRW tables produced by the automated discovery pipeline are named
`authorname_year_construct`, where `authorname` is the source paper's first-author
surname. Nothing downstream can verify this: the name propagates into the Redivis
table, the `__items` item-text table, the dictionary sheet and the tags sheet, and
none of those hold the author independently. A wrong surname is silent and permanent.

Three tables have been confirmed wrong, and in each case the surname in the table
name appears **nowhere** in the source record — these are invented names, not a
wrong-field-selection bug:

| table | source's actual first author / year |
|---|---|
| `alomari_2025_student_questionnaire` | Xie, 2026 |
| `clifford_2018_police_blame` | Boudreau, 2019 |
| `nakano_2020_osce_contact_precautions` | Nagoshi, 2019 |

All three sit in the **6/23/2026** dictionary batch, as do all 16 automated rows
missing a `Reference` — no other batch has any. That batch is 43 rows.

Full write-up: https://github.com/ben-domingue/irw/issues/1686

## Your task

Produce the complete list of automated-pipeline tables whose name disagrees with
the source the DOI resolves to. **Produce the list only.** See Constraints below.

## Data sources — metadata only, nothing from Redivis

- **IRW Data Dictionary** (one read, ~3,900 rows):
  `gsheet::gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315')`
  Filter to `Contributor == "automated"` (~1,886 rows and growing).
- **Crossref**: `https://api.crossref.org/works/{doi}` — free, no key. Send a
  `User-Agent` with a mailto (`IRW-naming-audit (ben.domingue@gmail.com)`) to get
  the polite pool. ~1,461 of the DOIs.
- **DataCite**: `https://api.datacite.org/dois/{doi}` — free, no key. Needed for
  figshare (`10.6084`), Mendeley Data (`10.17632`), Harvard Dataverse (`10.7910`),
  OSF (`10.17605`), Zenodo (`10.5281`), Dryad (`10.5061`). ~416 of the DOIs.
  These 404 on Crossref, so route by prefix rather than trying Crossref first.

Budget ~1,900 HTTP GETs, 4-6 minutes at a polite throttle (~0.1s).

**Do not call `irw_fetch()` or read any Redivis table.** The Redivis account has a
200GB/30-day export cap against a 181.8GB corpus; this audit needs zero of it.

## Method — two screens, both already validated

**Screen 1 (free, no network): table name vs the dictionary's own `Reference` string.**
Extract the leading surname token from the table name and look for it in `Reference`.
Clears ~99.7% of rows. Two traps, both real:

- **Accent transliteration is NOT an error.** `Yandún-Cartagena`->`yandun`,
  `Lindström`->`lindstrom`, `Zähl`->`zaehl` are all correct namings. Fold accents
  (`iconv(x, "UTF-8", "ASCII//TRANSLIT")`) *and* the German/Nordic digraphs
  (ae->a, oe->o, ue->u, ss->s) before comparing, or you get ~111 false positives
  instead of a handful.
- **Hyphenated surnames.** A naive `^[A-Za-z]+` regex truncates `hen-herbst` to
  `hen` and flags three correct tables. Allow hyphens in the surname token.

Screen 1 has a fatal blind spot: it only catches a name that disagrees with the
`Reference` *in the same row*. A fabricated name written into both fields is
self-consistent and invisible, and 16 rows have no `Reference` at all — which is
precisely why `alomari_2025_student_questionnaire` never surfaced. **Screen 1 is a
cheap pre-filter, not the answer.**

**Screen 2 (the real check): resolve every DOI and compare against its author list.**
This is what found all three confirmed cases.

### Decision to make and surface

Match the table's surname against the **full author list**, not just the first
author, and flag only names absent from the list **entirely**. All three confirmed
failures fail that stricter test, so it loses no true positives, and it avoids
flagging tables legitimately named for a corresponding author or a dataset creator
who isn't first author. If you find tables named for a non-first author who IS on
the paper, report the count separately rather than as errors — that's a convention
question for Ben, not a defect.

Also compare the **year** in the table name against the DOI's issued year. Two of
the three confirmed cases have both wrong.

### Known data hygiene problems in the DOI column

Normalise before lookup:
- 11 rows are prefixed with the literal text `data doi: `
- 7 rows hold a full URL (`https://doi.org/10.7910/DVN/ZDNSFJ`)
- PLOS supplement DOIs carry an `.s001` suffix — strip it to get the article DOI
- 16 rows have a *dataset* DOI in the `DOI (for paper)` column

The last one is itself a finding for #1686; note it, don't silently repair the sheet.

## Correctness check before you trust a full run

Your pipeline must reproduce all three known cases. If it doesn't flag
`alomari_2025_student_questionnaire`, `clifford_2018_police_blame` and
`nakano_2020_osce_contact_precautions`, the pipeline is wrong — fix it before
running the sweep. `alomari` in particular has `Reference = NA`, so it exercises
the path Screen 1 misses.

## Priority

Audit the **43 rows dated 6/23/2026 first** and report on them before the full
sweep. Every confirmed error and every missing `Reference` is in that batch, so it
is either a bad batch or the only bad batch, and knowing which shapes everything
else. Check that batch's `Description`, `Reference` and license fields too, not
just names — a run that invented surnames may have invented other metadata.

## Constraints

- **Do not rename anything.** Do not write to Redivis. Do not cut or release a
  Redivis dataset version. Renames are being handled separately as a coordinated
  batch across four datasets, and an out-of-band rename breaks `irw_itemtext()`.
- **Do not edit the Google Sheets** (no tool here can write cells anyway).
- **Do not modify `automated_finding/` pipeline scripts.** Proposing a naming gate
  is in scope; implementing it is not, without asking first.
- Report what you could not check (unresolvable DOIs, missing DOIs, timeouts)
  explicitly. "Couldn't check" must not read as "checked and clean."

## Deliverables

1. `automated_finding/naming_audit_suspects.csv` — one row per suspect:
   `table, name_surname, name_year, resolved_first_author, resolved_all_authors,
   resolved_year, doi, registrant, verdict, batch_date`
   where `verdict` is one of `name_absent_from_authors` / `non_first_author` /
   `year_mismatch` / `unresolvable` / `no_doi`.
2. A comment on issue #1686 with: counts per verdict, the 6/23/2026 batch findings,
   the proposed corrected name for each confirmed error, and what could not be
   checked. Rank by confidence — a fabricated name is a different severity from a
   year that's off by one because the paper moved from online-first to issue.
3. Do **not** open new issues per table; everything goes on #1686.

## Note

The dictionary sheet is live and grew by ~200 automated rows in a single day, so
your result is a snapshot. Say so, and record the row count and date you ran it.
