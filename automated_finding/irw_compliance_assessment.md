# IRW Compliance Assessment — Status Snapshot (June 2026)

Comparison of the pipeline against the
[IRW Data Standard](https://itemresponsewarehouse.org/standard.html),
updated to reflect the current state of `irw_triage_updated.py`.

---

## Required elements — `id`, `item`, `resp`

### id

| | Status |
|---|---|
| Detected and renamed from wide format | ✅ handled |
| Float-dtype guard (rejects row-index columns) | ✅ `is_float_dtype` check |
| Fallback to `df.columns[0]` forces `confidence="low"` | ✅ fixed (was silent) |
| Verified as actually persistent (not a row counter) | ⚠️ heuristic only (≥50% unique) |

---

### item

| | Status |
|---|---|
| Renamed from wide column headers | ✅ handled |
| Minimum distinct items (≥ 2) checked | ✅ in `looks_like_item_response` |
| `trial_*` columns detected and melt aborted | ✅ fixed — returns `human_assistance` |

---

### resp

| | Status |
|---|---|
| Verified numeric | ✅ `resp_numeric` check |
| Checked for variation | ✅ `resp_variation*` check |
| Flagged when >50 unique values | ✅ `resp_ordinal*` warn; escalates to `human_assistance` after wide-to-long melt |
| Non-integer values flagged as soft content-gate signal | ✅ fixed |
| Consistent coding within item cannot be auto-verified | ✅ `resp_direction*` warn emitted on every wide-to-long conversion |
| Imputed values detected (column names + value distribution) | ✅ `imputed_values*` warn |
| Ordinal vs. nominal distinction | ⚠️ not checked — still a human judgment |

---

## Optional elements

### `rt` — response time

| | Status |
|---|---|
| Preserved if present in a long-format source | ✅ passes through |
| Blocked (with explanation) if present in a wide source file | ✅ melt aborted, `human_assistance` returned |
| Numeric check | ✅ `rt_numeric*` warn |
| Milliseconds-vs-seconds detection | ✅ `rt_units*` warn (median > 60,000) |
| Negative values flagged | ✅ `rt_negative*` warn |

---

### `date` — longitudinal timing

| | Status |
|---|---|
| Recognized as longitudinal column (affects dup check) | ✅ |
| Blocked if present in a wide source file | ✅ melt aborted, `human_assistance` returned |
| Numeric / Unix-range validation | ✅ `date_numeric*` and `date_range*` warns |

---

### `wave`

| | Status |
|---|---|
| Recognized as longitudinal column | ✅ |
| Preserved during melt (added to `id_vars`) | ✅ fixed — now in `PERSON_LEVEL_COLS` |
| Checked to be integer-valued | ⚠️ not checked |

---

### `treat`

| | Status |
|---|---|
| Checked for non-0/1 values | ✅ `treat_binary*` warn |
| Preserved during melt (added to `id_vars`) | ✅ fixed — now in `PERSON_LEVEL_COLS` |

---

### `cov_` and `itemcov_` — covariates

| | Status |
|---|---|
| Unrecognized columns flagged for prefixing | ✅ `cov_prefix` warn |
| `itemcov_` prefix recognized as valid | ✅ in `known_prefix` tuple |
| `cov_*` columns preserved during melt | ✅ fixed — detected and added to `id_vars` |
| `itemcov_*` columns excluded from melt with warning | ✅ fixed — `item_level_cols*` warn |

---

### `qmatrix`, `item_family`, `rater`

| | Status |
|---|---|
| Recognized as valid column names | ✅ in `known` / `known_prefix` sets |
| Excluded from melt with warning | ✅ fixed — `item_level_cols*` warn emitted |
| Correct post-melt alignment verified | ⚠️ still a human judgment |

---

## Structural compliance: the melt logic

| | Status |
|---|---|
| Person-level columns (`wave`, `treat`, `cov_*`) carried through melt | ✅ fixed |
| Item-level columns excluded from melt with warning | ✅ fixed |
| Response-level columns (`rt`, `date`) in wide file abort the melt | ✅ fixed |

---

## Multiple scales

| | Status |
|---|---|
| Item-name prefix clustering detected | ✅ `multi_scale*` warn (≥2 prefixes with ≥3 items each) |
| Automatic splitting into separate files | ⚠️ not implemented — still a human task |

---

## resp coding direction

| | Status |
|---|---|
| Standing warn on every wide-to-long conversion | ✅ `resp_direction*` warn |
| Automatic detection of unreversed items | ⚠️ not implemented — genuinely hard to automate reliably |

---

## Discovery pipeline

| | Status |
|---|---|
| Five repositories queried | ✅ Dataverse, Zenodo, OSF, Dryad, Figshare |
| Instrument names override exclusion gate | ✅ fixed |
| Supplementary file titles blocked at discovery | ✅ fixed (`_RE_SUPPLEMENTARY`) |
| OSF file resolver implemented | ✅ fixed |
| Zenodo query syntax (special characters) | ⚠️ 400 errors on queries containing hyphens — needs investigation |

---

## Remaining known gaps

The following are documented as not yet addressed; they require either
substantial engineering effort or genuine human judgment to resolve:

1. **Ordinal vs. nominal resp**: a nominal variable (A/B/C/D recoded 1/2/3/4)
   passes all checks.
2. **Unreversed item detection**: automatic flagging of items with strongly
   negative inter-item correlations is not implemented.
3. **`wave` integer check**: the `wave` column is not validated as ordered integers.
4. **Post-melt alignment of item-level columns**: `item_family`, `rater`, and
   `qmatrix*` are excluded from the melt but not re-joined — a human must verify
   alignment.
5. **Multi-file datasets**: when a landing page has multiple tabular files, only
   the first is triaged. Multi-file datasets are flagged via `n_other_files > 0`.
6. **Zenodo query syntax**: queries with hyphens (e.g. "PHQ-9") return 400 errors
   from the Zenodo API.
