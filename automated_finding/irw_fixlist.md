# IRW Pipeline — Implementation Changelog

All changes were made to `irw_triage_updated.py`, `irw_batch_updated.py`, and
`irw_discover_updated.py` in June 2026.

---

## P0 — Silent wrong output

**1. Melt now preserves all standard non-item columns**
`irw_triage_updated.py` → `coerce_to_irw`

Before the fix, `df.melt()` protected only `id_col`; every other column
(`wave`, `treat`, `cov_*`, `rt`, `date`, `itemcov_*`, `rater`, `item_family`,
`qmatrix*`) was silently treated as an item column or dropped.

Fix implemented: columns are now classified before melting into three categories:
- **Person-level** (`wave`, `treat`, `cov_*`): added to `id_vars`, carried through.
- **Item-level** (`itemcov_*`, `qmatrix*`, `item_family`, `rater`): excluded from
  both `id_vars` and `value_vars`; a QC `warn` (`item_level_cols*`) is emitted.
- **Response-level** (`rt`, `date`): if present in a wide source file, the melt
  is aborted and `human_assistance` is returned (Option A — these columns are
  structurally ambiguous in wide format).

Module-level constants `PERSON_LEVEL_COLS`, `ITEM_LEVEL_PREFIXES`, and
`RESPONSE_LEVEL_COLS` define these categories.

---

**2. `id_col` fallback now forces `confidence="low"`**
`irw_triage_updated.py` → `coerce_to_irw`

When no column passed the `_looks_like_id` heuristic (≥50% unique, non-float),
the code fell back to `df.columns[0]` but could still assign `confidence="high"`.

Fix: `id_fallback=True` is set on the fallback path and forces `confidence="low"`
unconditionally, plus adds an explicit Coercion note naming the fallback column.

---

## P1 — Missing checks that affect the `good`/`human_assistance` decision

**3. `resp_direction*` warn on every wide-to-long conversion**
`irw_triage_updated.py` → `run_qc`

Added a standing QC `warn` whenever `coercion_method == "wide-to-long"` reminding
that within-item coding direction cannot be auto-verified.

---

**4. Imputed values detection**
`irw_triage_updated.py` → `run_qc`

Two heuristics added:
- Column-name signal: any source column named with suffix `_imp`, `_imputed`,
  `_filled`, or `_flag` emits `imputed_values*` warn.
- Value-distribution signal: if any single resp value accounts for >60% of
  responses in an item (mean-imputation signature), emits `imputed_values*` warn.

---

**5. `date` column validation**
`irw_triage_updated.py` → `run_qc`

Added `date_numeric*` warn when >10% of `date` values are non-numeric, and
`date_range*` warn when the numeric max is < 1e8 (too small for Unix seconds).

---

**6. `rt` column validation**
`irw_triage_updated.py` → `run_qc`

Added `rt_numeric*` warn when >10% of `rt` values are non-numeric, `rt_units*`
warn when the median exceeds 60,000 (likely milliseconds, not seconds), and
`rt_negative*` warn when any value is negative.

---

## P2 — Detection gaps

**7. Multi-scale detection**
`irw_triage_updated.py` → `run_qc`

Added `multi_scale*` warn when item-name prefixes (split on digits and
underscores) cluster into 2+ groups of ≥3 items each, signalling that the
dataset likely contains multiple distinct scales that must be split.

---

**8. `trial_*` column detection**
`irw_triage_updated.py` → `coerce_to_irw`

If the source DataFrame has columns starting with `trial_`, the melt is aborted
and `human_assistance` is returned with a note explaining the trials-based
structure.

---

## P3 — Discovery / batch improvements

**9. OSF file resolver**
`irw_batch_updated.py` → `_osf_files` / `resolve_data_files`

Added `_osf_files(url)` using the OSF storage API:
`GET https://api.osf.io/v2/nodes/{node_id}/files/osfstorage/`. Wired into the
`resolve_data_files` dispatch under `src == "osf"`.

---

**10. Instrument names override the exclusion gate**
`irw_discover_updated.py` → `is_relevant`

Previously, the exclusion check (epi/medical study language) ran before the
instrument check, so a title like "Cross-sectional validation of the PHQ-9 in a
diabetes cohort" was blocked despite naming a real instrument.

Fix: `_RE_INSTRUMENT` is now checked first; a match returns `True` immediately
before the exclusion gate is applied.

---

## Post-P3 — Triage accuracy improvements

**11. `resp_ordinal*` on wide-to-long escalates to `human_assistance`**
`irw_triage_updated.py` → `triage_dataset`

Observation from reviewing the first batch run: most "good" rows with
`resp_ordinal*` (>50 unique response values after a melt) were wide matrices
of aggregate/continuous scores, not ordinal item responses. These were being
passed as `good` because warns alone did not escalate.

Fix: if `resp_ordinal*` is present in warns and `coercion_method == "wide-to-long"`,
`triage_dataset` now forces `flag = "human_assistance"` with an explanatory reason.

---

**12. Non-integer resp values as a content-gate soft signal**
`irw_triage_updated.py` → `looks_like_item_response`

Factor loading tables, correlation matrices, and continuous measurement outputs
were passing the content gate because their resp values happened to be numeric.
Ordinal item responses are almost always integers.

Fix: added a soft signal — if >50% of resp values have a non-zero decimal part
(`resp % 1 != 0`), the content gate records it. Two soft signals together push
the result to `not_item_response`.

---

**13. Supplementary file titles blocked at discovery**
`irw_discover_updated.py` → `is_relevant`

Frontiers journal papers (and others) upload individual tables, figures, and data
sheets as repository items with titles like `Table 1_<paper title>`, `Data Sheet
1_<paper title>`, `Supplementary file 1_<paper title>`. These reliably have no
downloadable tabular data file and were contributing ~38% of figshare results.

Fix: added `_RE_SUPPLEMENTARY` regex; matched titles are blocked unconditionally
in `is_relevant` before any other check.
