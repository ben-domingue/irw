# Data Dictionary DOI/Reference/URL consistency audit

Audits the `DOI (for paper)` column of the [IRW Data Dictionary][sheet] against
each row's own `Reference` and `URL (for data)`. Run 2026-08-31. Findings and
proposed corrections: **issue #1764**. Artifact:
`doi_reference_mismatch_audit.csv`.

[sheet]: https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s

## Why

`irw-auto-tag` resolves a table's source by DOI and reads that paper to assign
tags. A wrong DOI does not fail loudly — the fetch succeeds, the content
verifies as a genuine article, and the table is tagged from an unrelated paper.
Nothing downstream detects it.

## Reproduce

All four scripts read/write in the working directory, so run them from one place.
Step 0 is required: `dict.csv` is not committed (the sheet is the source of truth
and changes daily).

```bash
# 0. snapshot the dictionary
curl -sL -A "irw-doi-audit/1.0 (mailto:you@example.com)" \
  "https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/export?format=csv&gid=0" \
  -o dict.csv

python3 doi_audit_pass1.py      # dict.csv            -> pass1.json
python3 doi_audit_fetch_oa.py   # dict.csv            -> openalex.json   (~30 network calls)
python3 doi_audit_compare.py    # + openalex.json     -> compared.json
python3 doi_audit_build_csv.py  # + hand-verified judgements -> the CSV
```

Set your own address in the `mailto:` of `doi_audit_fetch_oa.py` before
rerunning — OpenAlex's polite pool expects a real contact.

`doi_audit_build_csv.py` is **not** a pure derivation of `compared.json`. It
encodes the hand-verified conclusions (the four cluster head DOIs, the two
isolated cases) as literals. Re-verify those before reusing it on a later
snapshot.

## Method

**Pass 1 — no network.** Internal consistency: DOIs and repository accessions
embedded in a row's own `Reference`/`URL` versus its DOI column. Yielded little
on its own — most hits were the legitimate data-DOI/paper-Reference pairing. The
variant that *did* earn its keep is in `doi_audit_build_csv.py`'s grouping: rows
sharing one identical `Reference` but carrying **different** DOIs, which is a
contradiction by construction and needs no network.

**Pass 2 — network.** Every distinct DOI resolved against OpenAlex (batched 40
per request, polite pool), comparing returned title / author surnames / year
against the free-text `Reference`. A row is a candidate only when *no* author
surname appears in the Reference **and** title-token overlap is below 0.34.

## Results

| | |
|---|---|
| Rows / rows with a DOI | 4,309 / 3,720 |
| Distinct DOIs | 1,234 |
| Resolved | 1,099 |
| Unverifiable (404 / unindexed) — not mismatches | 135 DOIs, 461 tables |
| Raw pass-2 candidates | 45 |
| **Confirmed after hand-review** | **36 tables** (~20% FP rate on raw signal) |

34 of the 36 fall in four sequential-DOI clusters from one contributor, where a
batch's first row is correct and each later row was drag-filled +1. See #1764.

## Caveats

- **Not a pure heuristic output.** The CSV is the heuristic *after* hand-review;
  8 of 36 positives were individually re-resolved against OpenAlex, and the rest
  rest on two agreeing signals. One candidate (`polca_cheating`) was discarded on
  inspection — its DOI is a chapter of the very book its Reference cites.
- **The author check has false negatives.** `hyatt_2023_aggression_s3_bpaq`
  passed it because the unrelated paper it resolves to coincidentally shares an
  author with the cited one. Only the structural pass caught it. Do not run pass
  2 alone.
- **Excluded by design, not oversight:** dataset DOIs (Dataverse, OSF, Zenodo,
  Dryad, ICPSR, UKDA) paired with a Reference citing the companion article;
  book chapters and technical reports, where title matching is legitimately
  weak; and References that are a bare URL containing the DOI itself.
- The dictionary is read-only from code (#1708). Nothing here writes to the
  sheet; corrections are proposed in the issue for a human to apply.
