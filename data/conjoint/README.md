# Conjoint experiments (`irw_conjoint`)

Processing scripts for the tables in the Redivis dataset `datapages.irw_conjoint`. This is an experimental source, like competitions and nominal. It is **not yet registered** in `metadata/redivis_config.R` or the packages. Until it is, tables go up with:

```
red_up . --dataset irw_conjoint --allow-unregistered --no-validate
```

Run that from a staging folder that holds only the files to upload. First check every file with

```
python3 -m irw_validate.conjoint *.csv
```

because the core validator does not apply to this layout. Once `conj` is registered, `red_up` runs these checks itself for the `irw_conjoint` target, and `--allow-unregistered --no-validate` go away.

## Layout (draft conjoint standard)

One row per respondent × task × profile.

| column | |
|---|---|
| `id` | respondent; never a platform worker ID |
| `task` | task index within respondent, in the order shown |
| `profile` | position within the task (1 = left or first) |
| `choice` | 1 if this profile was chosen, else 0. With an opt-out, both profiles can be 0. |
| `rating` | numeric rating of this profile, higher = more favourable |
| `choice_<name>`, `rating_<name>` | further outcomes asked about the same tasks (e.g. "which would you vote for" and "which would reduce corruption most"); same coding as `choice`/`rating` |
| `attr_<name>` | the level **as displayed**, as text (never a numeric code); blank = attribute not shown |
| `attrpos_<name>` | row position of the attribute, when attribute order was randomized |
| `cov_<name>` | respondent covariates; a survey weight is `cov_survey_weight` |
| `trial_<name>` | other task-level details, such as experiment arm |

Other rules:
- One experiment per table: one attribute set, one population, one fielding.
- Drop derived variables (dummy codings, "co-partisan" flags).
- Rows with no outcome are omitted.

## Intake rules

- **Licence.** CC0, CC BY or CC BY-SA, confirmed from the Dataverse API, with no restricted files. For a compilation that re-hosts other studies, the original study's licence governs.
- **At least 100 respondents** per table.
- **Strip identifying columns:** MTurk, Prolific or panel worker IDs, IP addresses, GPS coordinates, and free-text personal information. Re-key respondent IDs to integers when the source ID is a platform ID.
- **Labels are required.** Attribute levels must be the text respondents saw. If a deposit ships only numeric codes and no codebook maps them, hold it.
- **Table names** follow `author_year_topic`: lowercase, at most 40 characters. `red_up` refuses a name already used in another IRW source.

## Records kept for every table

- **The script** here. Its header gives the citation, the deposit DOI and licence, the files read, the outcome wording, opt-out, randomization restrictions, what was dropped, and any count discrepancy with the paper.
- **A dictionary row,** staged with `automated_finding/stage_dict_row.py --source conj`, which writes to `dictionary_auto_conj.csv`.
- **A processing note** in `metadata/data_notes.csv`.
- **A row in `candidates.csv`,** the ledger of every deposit considered. Its status is `todo`, `built`, `uploaded`, or `held: <reason>`.
- **A design record:** one row in `design_tables.csv` and one row per outcome column in `design_outcomes.csv` (below). `metadata/tests/test_conj_design.py` fails if a built or uploaded table has none.

## Design records

The tables share one layout but not one meaning: `choice` is "vote for" in one table and "admit" in another, and ratings run 1–7, 0–10 or 0–100. These two files make what the header says machine-readable, so that tables can be pooled. `metadata/16_conjoint.R` joins `design_tables.csv` into `conj_metadata.csv` and publishes `design_outcomes.csv` as `conj_outcomes.csv`, both without the `evidence` column. When no source states a fact, the value is `unknown`. Never guess one.

`design_tables.csv`, one row per table:

| column | |
|---|---|
| `country` | where it was fielded: ISO 3166 alpha-2, `;`-joined if the table pools countries |
| `display_language` | the language respondents saw: ISO 639-1, or ISO 639-3 for a language without a two-letter code (Lusoga is `xog`), `;`-joined |
| `label_language` | the language of the `attr_` text as stored. This can differ from `display_language` when only an English instrument survives. |
| `restrictions` | `none` when a source says levels were randomized independently and uniformly; `yes` when a source states prohibited combinations, conditional levels or non-uniform weights; `observed` when no source documents it but the table shows it (combinations that never occur, clearly unequal level shares); otherwise `unknown`. With `yes` or `observed`, the estimator has to account for the restriction (for example, by estimating within the allowed combinations); a plain difference in means across levels can mislead. |
| `restrictions_note` | the rule, when `restrictions` is `yes` or `observed` |
| `task_source`, `profile_source` | `recorded` (the deposit has the column), `inferred` (rebuilt from row order), or `unknown`. Position and task-order analyses should drop `inferred`. |
| `evidence` | where each value came from: header lines, codebook pages |

`design_outcomes.csv`, one row per table × outcome column:

| column | |
|---|---|
| `outcome`, `type` | the column name, and `choice` or `rating` |
| `question` | the wording, verbatim. If the source gives only a translation or a paraphrase, it ends with "(translated)" or "(paraphrase)". |
| `opt_out` | choice rows only: `yes` if respondents could choose neither profile, otherwise `no` |
| `scale_min`, `scale_max`, `low_anchor`, `high_anchor` | rating rows only: the stored range and the labels of its two ends |

## Scripts

Each script takes `<raw dir> <output dir>` and reads only the files named in its header. Downloads are untrusted: no code shipped with a deposit is ever run.
