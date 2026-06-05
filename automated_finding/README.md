# IRW Automated Finding Pipeline

Tools for automatically discovering and screening candidate datasets for
contribution to the [Item Response Warehouse](https://datapages.github.io/irw/)
(IRW). The three scripts form a sequential pipeline:

```
irw_discover.py  →  irw_batch.py  →  (human review of flagged output)
                         ↑
                   irw_triage.py
                   (used internally)
```

---

## irw_discover.py — Cast a wide net

Searches five open-data repositories for datasets that might qualify for the
IRW, and writes a deduplicated list of candidates to a CSV.

**What it queries:** Harvard Dataverse, Zenodo, OSF, Dryad, Figshare.

**What it returns:** One row per candidate — source, title, DOI, publication
date, and landing-page URL. No file downloads, no scoring.

**Relevance filter (on by default):** Titles are matched against tiered keyword
lists — named instruments (PHQ-9, WAIS, BFI, …), strong psychometric terms
(item response, Rasch, Likert, …), and construct terms (ability, depression,
personality, …). Titles matching epidemiological/clinical study language
(`cross-sectional`, `odds ratio`, `meta-analysis`, …) are excluded. Use `--all`
to disable this filter entirely.

**Deduplication:** Candidates seen across multiple sources are merged by DOI;
falls back to source+title when no DOI is present.

**Excluding known IRW datasets:** Pass `--exclude irw_metadata.csv` to skip
DOIs already in the warehouse. Generate that file in R:
```r
library(irw)
write.csv(irw_metadata(), "irw_metadata.csv")
```

**Usage:**
```bash
python irw_discover.py "self-efficacy scale" "reading assessment"
python irw_discover.py --exclude irw_metadata.csv "item response"
python irw_discover.py --all "questionnaire"
```

**Output:** `irw_discovered.csv` (or `--out <path>`)

---

## irw_triage.py — Evaluate one candidate

Takes a single data file (local path or URL) and runs it through four steps:

1. **Download** — fetches `.csv`, `.tsv`, or `.xlsx` files by URL if needed.
2. **Coerce** — attempts a best-guess conversion to IRW long format
   (`id` / `item` / `resp` columns). Handles two cases automatically:
   - File already has `id`, `item`, `resp` columns → accepted as-is.
   - Wide person×item matrix → melted to long format.
   - Anything else → flagged for human review with the column names listed.
3. **QC** — runs checks mirroring the official IRW validator (`validate_irw.R`),
   plus extra heuristics: response scale sanity, `treat` column coding, and
   the IRW density metric.
4. **Flag** — produces one of:
   - `good` — confident mapping, no QC errors (may have soft notes to glance at).
   - `human_assistance` — got data, but mapping or QC needs a person.
   - `not_item_response` — data is structurally shaped like IRW format but
     isn't actually person×item response data (e.g. a results table from a paper).

Also computes IRW metadata: `n_responses`, `n_participants`, `n_items`,
`density`, and the response frequency distribution.

> **Note:** The coercion step is a heuristic, not a solver. `human_assistance`
> is the normal, expected outcome for ambiguous datasets — not a failure.

**Usage:**
```bash
python irw_triage.py path/to/data.csv
python irw_triage.py https://example.com/data.csv
```

**Output:** Printed report + best-guess IRW-formatted file
(`irw_formatted_<name>.csv`) if a conversion was possible.

---

## irw_batch.py — Process a whole discovery file

Runs `irw_triage.py` over every row of a `irw_discovered.csv` produced by
`irw_discover.py`, resolving each landing-page URL to actual data files and
writing a ranked triage summary.

**Resolution:** Each repository exposes its files differently; the batch runner
handles Zenodo, Figshare, Dryad, and Harvard Dataverse automatically. OSF
candidates currently require manual resolution.

**Flags produced** (sorted to top of output in this order):

| Flag | Meaning |
|---|---|
| `good` | Confident mapping + clean QC — start here |
| `human_assistance` | Got data, needs a human for mapping or QC |
| `not_item_response` | Structurally plausible but not response data |
| `no_usable_file` | No resolvable tabular file on the landing page |
| `download_failed` | Network or HTTP error fetching the file |
| `error` | Unexpected problem (message recorded) |

**Resumable:** Results are checkpointed to `irw_batch_checkpoint.jsonl` after
each row. A crash or disconnect at row 450 doesn't lose the first 449. Use
`--resume` to continue from where processing stopped.

**Converted tables** are saved under `irw_output/good/` and
`irw_output/human_assistance/` for direct review.

**Usage:**
```bash
# Always test on a small slice first
python irw_batch.py irw_discovered.csv --limit 5

# Full run
python irw_batch.py irw_discovered.csv

# Resume after an interruption
python irw_batch.py irw_discovered.csv --resume
```

**Output:** `irw_triage_summary.csv` (or `--out <path>`) + per-flag folders
under `irw_output/`.

---

## Suggested workflow

```
1. irw_discover.py  →  irw_discovered.csv     (hundreds of candidates)
2. irw_batch.py --limit 10                    (sanity-check on 10 rows)
3. irw_batch.py --resume                      (full run, resumable)
4. Open irw_triage_summary.csv, work 'good' rows first
5. Hand-review 'human_assistance' rows using the listed reasons
```
