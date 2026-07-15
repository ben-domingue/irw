# IRW Data Standard: Agent Processing Guide

This document tells an agent exactly what to produce when converting a raw dataset into IRW format. Read it before writing a single line of code.

---

## Before you start

**Verify the license first.** The license must be explicitly open — CC0, CC BY, or CC BY-SA — as stated on the source page. A missing license, an unresolvable UUID, a "contact author" notice, or any NC/ND restriction means **stop**: do not write a processing script. Only proceed once you have confirmed a named open license.

**Check for duplicates.** Search the IRW dictionary before processing to make sure the dataset is not already in the warehouse.

**Assess complexity.** A dataset with 50 participants and opaque column names in a non-standard format may not be worth the time. Large, well-structured datasets are higher priority.

---

## The required output schema

Every IRW file is a CSV in long format with one row per person-item observation.

| Column | Required | Rules |
|--------|----------|-------|
| `id` | yes | Identifier for the focal unit being measured — typically a person, but sometimes another entity (e.g., a word in a lexical task). Integer or string. Must be unique per focal unit (not per row). |
| `item` | yes | Item identifier. String. Use original column names when they are meaningful; use `item_1`, `item_2`, … when they are not. Item names should be chosen to allow straightforward downstream matching with item text — prefer names that correspond directly to identifiers used in the source instrument or codebook (e.g., `BDI_1`, `PHQ_3`) over generic positional labels whenever such identifiers exist. |
| `resp` | yes | Response value. Must be numeric. Higher values represent a consistent directional change **within** each item, but direction may vary **across** items — do not recode reverse-scored items unless you have specific reason to. Remove imputed values. Continuous responses are acceptable (e.g. a 0–100 slider, "how well does this describe you?") — keep `resp` as a float and don't coerce to integer. Don't confuse this with an *aggregate* score summed/averaged across items; that's a composite, not a response, and doesn't belong in `resp` (see "Subscale aggregate columns" below). |
| `cov_*` | no | Covariates that are invariant to the focal unit (e.g., a person's gender or age). Always prefix with `cov_`. |
| `itemcov_*` | no | Covariates invariant to measurement probes (item-level attributes). Always prefix with `itemcov_`. |
| `wave` | no | Longitudinal wave indicator. Larger values indicate later collection. Use when the same focal unit appears at multiple time points. |
| `treat` | no | Treatment group assignment in experimental studies. `1` = treatment, `0` = control. |
| `rt` | no | Response time. **Seconds only** — convert from milliseconds if needed. |
| `date` | no | Calendar time in seconds — either seconds elapsed since data collection start (relative) or Unix time (absolute). Do not use other time units. |
| `qmatrix1`…`qmatrixN` | no | Item classifications for cognitive diagnostic modeling (Q-matrix). One column per attribute. |
| `rater` | no | Observer identifier in scenarios where items are rated by an external observer rather than self-reported. |
| `item_family` | no | Groups items that may violate local independence — testlets, clones, or clusters of similar items. |

Column order in the output file: `id`, `item`, `resp`, then optional response-level columns (`wave`, `treat`, `rt`, `date`), then `cov_*` and `itemcov_*` columns, then `qmatrix*`, `rater`, and `item_family` if present.

**Common mistake:** When melting with `id_vars=["id"] + cov_cols`, pandas places covariates immediately after `id` in the output — before `item` and `resp`. Always reorder explicitly after melting:
```python
out_cols = ["id", "item", "resp"] + [c for c in long.columns if c in ("wave","treat","rt","date")] + cov_cols
long = long[out_cols]
```

---

## One file per scale

Each measurement instrument (or subscale treated as a distinct construct) becomes a **separate CSV file**. If a raw file contains a depression scale and an anxiety scale, produce two output files. Do not mix items from different scales in the same file.

---

## File naming

Output files follow the pattern `authorname_year_construct.csv`, all lowercase, underscores for spaces. Examples:

```
che_2026_social_support.csv
ren_2019_ypic.csv
senosy_2025_anxiety_state.csv
```

Use the first author's last name, publication year, and a short construct label. For multi-scale papers, append the scale name or abbreviation.

**Table names must be 40 characters or fewer** (excluding `.csv`). If the natural name exceeds 40 characters, shorten the construct label — use standard abbreviations (e.g., `pos` for Perceived Organizational Support, `gad7` for GAD-7) or truncate. Never shorten the author name or year.

---

## Output location

Finalized output files go to:
```
automated_finding/irw_output/
```
(There is no `queue/` or `cleaned/` subdirectory — that intermediate stage was eliminated. Everything in `irw_output/` is upload-ready.)

---

## Step-by-step processing

### 1. Load the raw data

Accept any tabular format — the list below is illustrative, not exhaustive. Detect the format from the file extension and use the appropriate reader:

| Format | Extension(s) | Reader |
|--------|-------------|--------|
| CSV / TSV | `.csv`, `.tsv` | `pd.read_csv` |
| Excel | `.xlsx`, `.xls` | `pd.read_excel` |
| SPSS | `.sav`, `.zsav` | `pd.read_spss` or `pyreadstat.read_sav` |
| Stata | `.dta` | `pd.read_stata` |
| SAS | `.sas7bdat`, `.xpt` | `pd.read_sas` |
| R data | `.RData`, `.rds`, `.rda` | `pyreadr.read_r` |

For SPSS files, value labels embedded in the file (e.g., `1 = "Strongly disagree"`) are often useful for identifying covariate values — inspect them with `pyreadstat` metadata when available. Use numeric codes as the `resp` values; do not replace codes with label strings.

For Excel files with multiple sheets, inspect the sheet names and load the one containing response data (usually the first, or a sheet named "Data").

If the first row appears to be a label row rather than column headers (e.g., if cell A1 cannot be coerced to a number and looks like question text), skip it and use the second row as the header.

### 2. Identify and set the person ID column

Look for a column named `ID`, `id`, `SubjectID`, `participant`, `Participants ID`, `no`, or similar. Rename it to `id`. Coerce to numeric where possible; drop rows where `id` is NaN.

Before trusting this column as unique, verify it: `df["id"].nunique() == len(df)`. A same-named column that looks like an identifier (e.g. a source `randomid`) can still have far fewer unique values than rows. This matters most when the id is later used to merge item-slices with a covariate-slice — merging on a non-unique key produces a silent cartesian product (rows multiply, no error), not a crash, so it's easy to ship without noticing. If the check fails, use the row index instead (see below), not the non-unique column.

If no person ID column exists, create one from the row index:
```python
df = df.reset_index(drop=True)
df.insert(0, "id", df.index + 1)
```

If existing IDs are non-numeric strings (e.g., `"1b"`, `"2b"`), use the row index instead.

### 3. Identify covariates

Columns that describe the person (age, gender, education, region, group, etc.) are covariates. Rename them with the `cov_` prefix and lowercase:
```python
cov_rename = {"Age": "cov_age", "Gender": "cov_gender", "Education": "cov_education"}
df = df.rename(columns=cov_rename)
```

Keep covariate columns aside; they will be carried through `melt` as `id_vars`.

### 4. Identify item columns

Item columns are the ones that contain actual responses to questionnaire items. Exclude:
- The `id` column
- All `cov_*` columns
- Aggregate/subscale sum columns (e.g., columns whose names end in `_total`, `_sum`, or contain `_TT`, `_FAMIL`, `_FRIEN`; or columns with suspiciously large values inconsistent with the item scale)
- Open-text columns (free-response strings)
- Timestamps, metadata columns

When a file contains multiple scales, identify each by column prefix or naming convention (e.g., `SS01`–`SS08` for Social Support, `EI01`–`EI16` for Emotional Intelligence). Use regex patterns or prefix matching to separate them.

### 5. Pivot to long format

```python
long = df.melt(
    id_vars=["id"] + cov_cols,
    value_vars=item_cols,
    var_name="item",
    value_name="resp"
)
```

### 6. Clean responses

```python
long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
long = long.dropna(subset=["resp"]).reset_index(drop=True)
```

**Filter sentinel/missing-value codes.** Many datasets use sentinel values (999, 99, 9) to indicate missingness. If you know the valid response range (e.g., 1–4), filter:
```python
long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
```

**A sentinel can hide inside the valid range, and `dropna()` will not catch it.** Check the codebook (variable-description file, OSF wiki, or paper) for every response scale before trusting raw codes as `resp`. A source column can be pure `int64` with zero `NaN`s and still be wrong: a category like "don't know" / "not applicable" / "refused" is a non-response, not a step on the ordinal scale, even though it's stored as an in-range integer — e.g. a 3-item financial-literacy quiz coded `0=incorrect, 1=correct, 2=don't know`; `2` is not "more correct" than `1`. Identify these values from the codebook and filter out those specific item-responses (don't recode them to 0 and don't drop the person entirely) before the file is considered ordinal and upload-ready.

**Parse text-coded responses.** Some datasets store responses as strings like `"3 - Sometimes"` or `"Strongly agree (5)"`. Extract the leading integer:
```python
long["resp"] = long["resp"].str.extract(r"(\d+)").astype(float)
```

### 7. Enforce column order and save

```python
out_cols = ["id", "item", "resp"] + cov_cols  # add wave/treat/rt/date if present
long = long[out_cols]
long.to_csv(path, index=False)
```

Print a summary line for each file:
```python
print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
      f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")
```

---

## Script structure

Write a standalone Python script named after the output dataset(s). Include a comment block at the top with the source URL and DOI. Define `OUT_DIR` relative to the script's location so the script works from any working directory:

```python
#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/XXXXXXX
# DOI: 10.XXXX/...

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

def convert():
    # ... processing logic ...
    pass

if __name__ == "__main__":
    convert()
```

Use `{"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}` as the request header when fetching from remote APIs.

---

## Common edge cases and how to handle them

### Multiple scales in one file
Define a `SCALES` dict mapping output name → item column list (or regex pattern). Loop over it, melt, and write one file per entry. See `che_2026_social_support.py` for a pattern using `re.compile` prefix matching, and `ren_2019_psychopathy_children.py` for a `(prefix, valid_max, out_name)` tuple approach.

### No meaningful item labels
When source column names are opaque (`V1`, `Q3`, column indices), assign generic labels:
```python
item_names = [f"item_{i:02d}" for i in range(1, n_items + 1)]
```
Map source columns to these names before melting. When generic labels are necessary, preserve the mapping from original column name to assigned label in a comment or a separate lookup so that item text can be matched later if it becomes available.

### Non-Latin item text in column names
If column names are in a non-English language, create a mapping to `item_1`, `item_2`, … and optionally attach `item_text` and `item_text_translated` columns in the output for documentation purposes (see `bakumenko_2023_adyghe_values.py`).

### Subscale aggregate columns
Aggregate columns often share a prefix with item columns but have a suffix like `_total`, `_TT`, `_FAMIL`, `_001`, `_002`. Exclude them explicitly by checking for these suffixes before building the item column list.

### Response time data
Convert to seconds if the source is in milliseconds:
```python
rt = rt_ms / 1000
```
Include as an `rt` column in the output. Do not include it in the `item`/`resp` melt — it is a response-level attribute alongside `resp`.

### Longitudinal / repeated-measures data
When the same focal unit appears at multiple time points, include a `wave` column (integer, with larger values indicating later collection). This is always its own column named `wave` — **never** a `cov_`-prefixed one (e.g. not `cov_wave`), even though it looks like a covariate. If calendar timestamps are available, store them as `date` in seconds — either relative (seconds since data collection began) or Unix absolute time; do not use milliseconds, minutes, or other units. Duplicate `id`+`item` pairs are valid when a `wave` column is present.

### Experimental / RCT treatment data
Include a `treat` column with values `1` (treatment) and `0` (control). This applies to any experimental design, not only RCTs. Do **not** encode this as a `cov_group` covariate — it belongs in `treat` so downstream tools can identify it. Map whatever coding the source uses (e.g., 1/2) to the standard 0/1 encoding:
```python
df["treat"] = (df["original_group_col"] == treatment_value).astype(int)
df = df.drop(columns=["original_group_col"])
```

### Missing person ID — use row index
```python
df = df.reset_index(drop=True)
df.insert(0, "id", df.index + 1)
```

### Text IDs that cannot be made numeric
If IDs are strings like `"sub-01"` that identify distinct people, keep them as strings. Do not force numeric conversion if it would destroy the identifier.

### PII columns
Some raw files include real names, email addresses, IP addresses, GPS coordinates, dates of birth, or national ID-card numbers (not to be confused with an anonymous study-assigned participant ID). Drop these columns entirely — do not carry them into `cov_*`, do not use them as `id`, and never print/materialize their values while inspecting the file (check `.notna().sum()` counts instead of viewing actual values). If a source ID-card or similar column is the only candidate for `id`, treat it the same as any other unusable ID (see "Missing person ID" above) — use row index instead, not the PII column.

### Data entry errors at known values
If a single out-of-range value is clearly a data entry error (e.g., a single `0` in a scale scored 1–7), set it to NaN and drop:
```python
long.loc[long["resp"] == 0, "resp"] = float("nan")
long = long.dropna(subset=["resp"]).reset_index(drop=True)
```

### Excel files with header rows above the column names
Some spreadsheets have banner rows or merged cells above the actual column headers. Use `header=None` when reading, then slice:
```python
raw = pd.read_excel(src, header=None)
data = raw.iloc[2:].reset_index(drop=True)  # skip rows 0 and 1
```

### Item-level covariates (`itemcov_*`)
When the source data includes attributes of the items themselves (e.g., item difficulty category, domain, modality) rather than attributes of the person, prefix those columns with `itemcov_` rather than `cov_`. They should still be consistent within each item across all rows for that item.

### Q-matrix / cognitive diagnostic data
If the dataset includes item-by-attribute classifications for cognitive diagnostic modeling, encode them as separate columns named `qmatrix1`, `qmatrix2`, … (one column per attribute). These are item-level columns, not response-level.

### Rater data
When items are scored by an external observer (rather than self-reported), include a `rater` column identifying the observer. This is distinct from `id` (the focal unit being measured).

### Item families (local independence violations)
If items are organized into testlets, clones, or clusters that may violate local independence, include an `item_family` column grouping them. Use a consistent label (string or integer) for items within the same family.

### Process data and trials
Some experimental datasets capture fine-grained behavioral traces (e.g., clickstreams, response sequences within a single item, eye-tracking events). The standard row structure — one row per person-item observation — does not accommodate these directly. Flag such datasets for human review rather than attempting to force them into the standard schema.

### Detecting the right file when multiple files exist on a landing page
For Figshare, Dataverse, OSF, and Zenodo, iterate over the file list returned by the repository API and select the file matching any supported tabular format (`.csv`, `.xlsx`, `.sav`, `.dta`, `.sas7bdat`, `.RData`, etc.). Prefer the main data file over codebooks, README files, or supplement tables. When multiple data files exist, flag this for human review rather than guessing.

---

## What to verify before saving

1. **`id` column** — unique per person (no NaN, no accidental item-level IDs). Confirm with `nunique() == len(df)` on the pre-merge frame, not just an eyeball check — a non-unique id used in a merge/join silently multiplies rows instead of erroring.
2. **No PII** — no real names, emails, IP/GPS, birthdates, or national ID numbers in `id` or any `cov_*` column.
3. **`item` column** — no covariate columns accidentally melted in as items (check for names like `Age`, `Gender`, `Sex`, `Education`).
4. **`resp` range** — matches the documented scale (e.g., 1–4 for a Likert scale). Unexpected values (0s, 99s, 999s) indicate unfiltered sentinels.
5. **`resp` is numeric** — no string values remaining.
6. **One scale per file** — if item names suggest two instruments, split the file.
7. **`resp` direction within items** — within each item, higher values must represent a consistent directional change (the scale cannot reverse mid-item). However, direction is allowed to vary across items, so reverse-scored items do not need to be recoded. What matters is that imputed values are removed and no sentinel codes remain.
8. **No aggregate/subscale totals in the item list** — check that `n_items` in your summary line is plausible for the instrument.
9. **`rt` in seconds** — if response times are included, verify the scale (values in the thousands likely indicate milliseconds).

---

## Summary of the pipeline

```
raw file → load → identify id / covariates / items
         → (split by scale) → melt to long
         → clean resp (numeric, drop NaN, filter sentinels)
         → enforce column order
         → save to automated_finding/irw_output/<name>.csv
         → print summary line
```
