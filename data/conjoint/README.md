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

## Scripts

Each script takes `<raw dir> <output dir>` and reads only the files named in its header. Downloads are untrusted: no code shipped with a deposit is ever run.
