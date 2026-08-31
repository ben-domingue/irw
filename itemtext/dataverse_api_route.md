# Reaching WAF-blocked Harvard Dataverse sources via the API

Written under issue #1751. Method established in #1615 on `gilbert_meta_35`; measured across the
whole `BLOCKED` Dataverse set here.

## The finding

**The Harvard Dataverse web page is WAF-blocked to automated access; the API is not.** Measured
across 13 `BLOCKED` tables / 12 distinct records:

| | result |
|---|---|
| `dataset.xhtml?persistentId=...` (web page) | **13/13 returned HTTP 202 with 0 bytes** |
| `api/datasets/:persistentId` | **12/12 records with a resolvable DOI returned HTTP 200** |
| records holding ≥1 ingested file with an `originalFileFormat` | **11 of 12** |

The one failure is a dictionary gap, not a WAF one: `karajko2025_*` has no `persistentId`-style URL
in the dictionary, so no DOI could be resolved.

So a `BLOCKED` verdict reached by fetching a Dataverse page records the access method, not a
property of the source. Those verdicts should be re-taken through the API.

## The recipe

```bash
DOI="doi:10.7910/DVN/LUKGIA"
BASE="https://dataverse.harvard.edu"

# 1. the record, and its file listing (dataFile.id is what you need)
curl -sL "$BASE/api/datasets/:persistentId/?persistentId=$DOI"

# 2. a file. WITHOUT ?format=original you get Dataverse's ingested .tab, which has
#    NO variable labels -- the labels are the whole point, so always ask for original.
curl -sL -o source.dta "$BASE/api/access/datafile/<id>?format=original"
```

`?format=original` is the step that matters. Dataverse ingests `.dta`/`.sav`/`.xlsx` into a
tab-separated archival copy and strips the labels; the original round-trips intact. In the
`dataset.json` file listing, `dataFile.originalFileFormat` marks which files have one.

## What it does and does not buy you

It settles **access**. It does not settle **availability** — and on the first record tried, the two
came apart:

`doi:10.7910/DVN/LUKGIA` (Mosher & Kim 2025, `gilbert_meta_109`/`_110`/`_111`) is fully reachable —
6 files, the original `.dta` with labels, the replication do-file, the readme — and the item wording
still is not published anywhere in it. The `.dta` labels the codes only as `recall q1`,
`mid transfer q1` and so on, which pins the mapping without being the administered wording; the
do-file carries zero `label variable` statements; the readme describes the instruments and defers to
the paper; and the paper's openly available accepted manuscript (Harvard DASH) describes the measures
and reports their psychometrics without reproducing items. All three tables are now `UNAVAILABLE`
rather than `BLOCKED`, which is a settled answer instead of an unexamined block.

**Expect that mix.** The value of the route is that each table gets a real verdict, not that every
table yields text.

## Two audit-hygiene points this surfaced

- **Siblings from one source file were classified inconsistently.** `gilbert_meta_110` was already
  `UNAVAILABLE`, assessed from `data/gilbert_109through111.R` and the raw `.dta`, while `_109` and
  `_111` were `BLOCKED`, assessed from the web page — and `_111`'s verdict was inferred from `_109`'s
  rather than taken independently. One `data/*.R` script builds all three from one file, so they
  should share a verdict. Worth checking for the same pattern elsewhere.
- **A verdict can be right for a false reason.** `_110`'s note said no source paper could be located.
  The paper is cited in the dictionary and openly readable on Harvard DASH. `UNAVAILABLE` still held,
  but on that reasoning nobody would have retried it.

## Next

23 of the 36 Dataverse+WAF `BLOCKED` rows have no resolvable DOI in the dictionary and need one
before they can be re-audited this way. The 13 that do are listed in the #1751 thread.

Note the count discrepancy: #1696 cites "62 of the 217 BLOCKED" as Dataverse WAF bot-challenges. By
the audit's own text, 36 rows cite both a Dataverse/Harvard source and a WAF/bot-challenge; 53 cite
Dataverse, 46 cite WAF, and 63 cite either. The 62 appears to be the union.
