# Conjoint experiments (`irw_conjoint`, `irw_conjoint_2`, …)

Processing scripts for the tables in the conjoint data family (`source = "conj"`): the Redivis datasets listed in `IRW_CONJ_DATASETS` (`metadata/redivis_config.R`), `datapages.irw_conjoint` first. Redivis caps a dataset at 1000 tables, so the family is a **shard list** on the item-text pattern (`ARCHITECTURE.md` §2): both client packages read every shard and resolve a name newest-first, and a user never names a shard. Users fetch tables with `irw_fetch(name, source = "conj")` in R or `irw.fetch(name, source="conj")` in Python, and `irw_conj_long()` / `irw.conj_long()` give the core id/item/resp view. Upload from a staging folder that holds only the files to upload:

```
red_up . --dataset irw_conjoint
```

NEW conjoint tables go to the newest shard, `irw_conjoint_2` (`CONJ_DEFAULT = None` in `red_up/targets.py`, Ben 2026-10-09); `irw_conjoint` stays at its 806 tables, and its remaining room is for in-place repairs. `red_up` refuses an upload that would take any shard past 1000 tables. A table that already exists in another shard is updated **there**: `red_up` lists every shard first and offers "update where it lives" as the default, because a second copy in a different shard would shadow the first rather than replace it. `16_conjoint.R` and `irw_list_tables(source = "conj")` flag any name that does end up in two shards. Never move a table between shards. To register a new shard, follow "Adding a conjoint shard" in `Rpkg/inst/developer/warehouses.md`: the dataset needs a **published release** before any config names it, and the entry lands in Rpkg, Python-pkg, then here.

`red_up` runs the conjoint checks (`irw_validate.conjoint`) for this target instead of the core validator. To check files before staging them:

```
python3 -m irw_validate.conjoint *.csv
```

## Scope

A table belongs here when respondents evaluate profiles whose attributes were randomized: at least two attributes, each with varying levels. That includes paired and single-profile conjoints, and factorial surveys or vignette experiments that randomize the attributes of a text vignette (`presentation = text` in the design record). A fixed set of vignettes shown identically to everyone, such as anchoring vignettes, is a set of ordinary items and belongs in the core warehouse.

## Layout

One row per respondent × task × profile.

| column | |
|---|---|
| `id` | respondent; never a platform worker ID |
| `task` | task index within respondent, in the order shown |
| `profile` | position within the task (1 = left or first) |
| `choice` | 1 if this profile was chosen, else 0. With an opt-out, both profiles can be 0. |
| `rating` | a numeric judgement of this profile, stored as in the source, without rescaling or reversal. What it measures, its range and its direction are in `design_outcomes.csv`. |
| `choice_<name>`, `rating_<name>` | further outcomes asked about the same tasks (e.g. "which would you vote for" and "which would reduce corruption most"); same coding as `choice`/`rating` |
| `attr_<name>` | the level **as displayed**, as text (never a numeric code). An attribute the design left off this profile is the exact text `(not shown)`; never blank (below) |
| `attrpos_<name>` | row position of the attribute, when attribute order was randomized |
| `cov_<name>` | respondent covariates; a survey weight is `cov_survey_weight` |
| `trial_<name>` | other task-level details, such as experiment arm. `trial_repeat_of` is reserved: on the rows of a task that repeats an earlier one (often task 1 shown again at the end, perhaps with the profiles swapped), the number of the task it repeats; NA elsewhere. The script header says whether the profiles were swapped. |

Choice or rating:
- `choice` (or `choice_<name>`) is a pick among the profiles of a task: 0/1, at most one 1 per task. A single-profile accept/reject (or vote/don't vote) question is also a `choice`, with `opt_out = yes`, since rejecting is the outside option.
- Everything else asked about a profile is a `rating`, including 0/1 judgements that do not pick among profiles (for example, "is this candidate a Democrat?" asked of each profile). The question wording in `design_outcomes.csv` says what it means.

Respondent covariates. Most `cov_` columns keep the name and coding of the source. These names are reserved and mean the same in every table:

| column | values |
|---|---|
| `cov_gender` | `female`, `male` or `other` (non-binary, self-described); NA when missing or refused |
| `cov_age` | age in years at the survey, as the deposit records it (including an age the authors computed from year of birth; the header says so) |
| `cov_birth_year` | year of birth, as recorded (age is not computed from it) |
| `cov_age_group` | an age band, as the text of the band ("18-29") |
| `cov_education` | the main education question, as the text of the answer option in the source's own categories and language |
| `cov_party_id` | party identification (the party a respondent identifies with or feels closest to), as answer text. A US 7-point scale is `cov_party_id7`, as text. Vote choice is not party identification. |
| `cov_attention_pass`, `cov_attention_pass_<k>` | 1 = passed an attention check, 0 = failed, NA = not asked |
| `cov_duration_sec` | survey or module duration in seconds; the header says which |
| `cov_survey_weight` | the per-respondent survey weight |

In the text covariates, a refusal ("prefer not to say", "no answer") is NA, while "don't know" stays as answer text. Codes are mapped to text only from the deposit's own codebook, value labels or recode code, and the script header names the source of each mapping. When no source maps a covariate's codes, the column keeps the codes and takes a `_code` suffix (`cov_gender_code`), so a reserved name never holds codes. `irw_validate.conjoint` checks the reserved codings (J8).

Other rules:
- One experiment per table: one attribute set, one population, one fielding.
- Drop derived variables (dummy codings, "co-partisan" flags).
- Rows with no outcome are omitted.
- A choice column is present on every profile of a task or on none of them.
- Where `design_outcomes.csv` says `opt_out` is `no`, every task has exactly one chosen profile.
- **`(not shown)`** is the one reserved `attr_` value: the design left this attribute off this profile (hidden attributes, arms that show a subset, clauses omitted by design). It is the same string in every table and language, so one equality test finds it across tables. Text respondents actually saw stays as displayed, even when it reads like an absence ("No information", "None"). A blank `attr_` cell would mean only that the level is missing in the source (not saved, unknown); such tasks are dropped or the table is held, so a blank cell is an error (J4).

## Intake rules

- **Licence.** CC0, CC BY, CC BY-SA or CC BY-NC (non-commercial is accepted, as elsewhere in IRW; a no-derivatives licence is not), confirmed from the Dataverse API, with no restricted files. The table's licence fields carry the deposit's licence. For a compilation that re-hosts other studies, the original study's licence governs.
- **At least 100 respondents** per table.
- **Strip identifying columns:** MTurk, Prolific or panel worker IDs, IP addresses, GPS coordinates, and free-text personal information. Re-key respondent IDs to integers when the source ID is a platform ID.
- **Labels are required.** Attribute levels must be the text respondents saw. If a deposit ships only numeric codes and no codebook maps them, hold it.
- **Table names** follow `author_year_topic`: lowercase, at most 40 characters. `red_up` refuses a name already used in another IRW source.

## Records kept for every table

- **The script** here. Its header gives the citation, the deposit DOI and licence, the files read, the outcome wording, opt-out, randomization restrictions, what was dropped, and any count discrepancy with the paper.
- **A dictionary row,** staged with `automated_finding/stage_dict_row.py --source conj`, which writes to `dictionary_auto_conj.csv`. To change a staged row, restage it with `--replace`. `--force` adds a second row.
- **A processing note** in `metadata/data_notes.csv`.
- **A row in `candidates.csv`,** the ledger of every deposit considered. Its status is `todo`, `built`, `uploaded`, or `held: <reason>`.
- **A design record:** one row in `design_tables.csv` and one row per outcome column in `design_outcomes.csv` (below). `metadata/tests/test_conj_design.py` fails if a built or uploaded table has none. `red_up` refuses to upload a conjoint table with no `design_tables.csv` row, or with an outcome column that has no `design_outcomes.csv` row. It warns when a gender attribute has no rows in `crosswalk.csv`.

## Design records

The tables share one layout but not one meaning: `choice` is "vote for" in one table and "admit" in another, and ratings run 1–7, 0–10 or 0–100. These two files make what the header says machine-readable, so that tables can be pooled. `metadata/16_conjoint.R` joins `design_tables.csv` into `conj_metadata.csv` and publishes `design_outcomes.csv` as `conj_outcomes.csv`, both without the `evidence` column. When no source states a fact, the value is `unknown`. Never guess one.

`design_tables.csv`, one row per table:

| column | |
|---|---|
| `country` | where it was fielded: ISO 3166 alpha-2, `;`-joined if the table pools countries |
| `display_language` | the language respondents saw: ISO 639-1, or ISO 639-3 for a language without a two-letter code (Lusoga is `xog`), `;`-joined |
| `label_language` | the language of the `attr_` text as stored. This can differ from `display_language` when only an English instrument survives. |
| `restrictions` | rules about **combinations** of levels: prohibited pairs, conditional levels, levels drawn without repetition. `none` when a source says attributes were randomized independently; `yes` when a source states such a rule; `observed` when no source documents one but the table shows combinations that never occur; otherwise `unknown`. With `yes` or `observed`, an AMCE has to be estimated within the allowed combinations (for example, by conditioning on the restricting attribute); a plain difference in means across levels can mislead. |
| `level_weights` | the probabilities of the levels within an attribute: `uniform` when a source says levels were equally likely; `nonuniform` when a source gives unequal probabilities; `observed` when no source does but the table's level shares are clearly unequal; otherwise `unknown`. Unequal but independent weights leave the AMCE identified (Hainmueller, Hopkins & Yamamoto 2014), but they change what it averages over, and marginal means depend on them. |
| `restrictions_note` | the rule or the probabilities; required when `restrictions` is `yes` or `observed` or `level_weights` is `nonuniform`, and may also explain another value |
| `attr_order` | the order attributes were listed in: `fixed`, randomized once per `respondent`, randomized per `task`, or `unknown`. With `respondent` or `task`, the table has `attrpos_` columns when the deposit recorded the order. |
| `survey_weight` | `kept` (the table has `cov_survey_weight`), `none` (the deposit documents no weight), `not_kept` (the deposit has a weight the table lacks; the evidence says why), or `unknown` |
| `presentation` | `grid` (profiles shown as an attribute table), `text` (a vignette or prose), `image` (a picture, photo or mock-up such as a social-media profile), or `unknown` |
| `task_source`, `profile_source` | `recorded` (the deposit has the column), `inferred` (rebuilt from row order), or `unknown`. Position and task-order analyses should drop `inferred`. |
| `evidence` | where each value came from: header lines, codebook pages |

`metadata/16_conjoint.R` also checks each table against its record: it computes the level shares and the pairs of levels that never occur together, and warns when `restrictions` is `none` but pairs are missing, or `level_weights` is `uniform` but shares are clearly unequal.

`design_outcomes.csv`, one row per table × outcome column:

| column | |
|---|---|
| `outcome`, `type` | the column name, and `choice` or `rating` |
| `question` | the wording, verbatim. If the source gives only a translation or a paraphrase, it ends with "(translated)" or "(paraphrase)". |
| `opt_out` | choice rows only: `yes` if respondents could choose neither profile, otherwise `no` |
| `scale_min`, `scale_max`, `low_anchor`, `high_anchor` | rating rows only: the stored range and the labels of its two ends |

## Attribute crosswalk

Attribute columns keep the text respondents saw, so the same idea arrives under different names and in different languages: `attr_gender` = Female/Male, `attr_sex` = Femmina/Maschio, `attr_gender` = Mujer/Hombre. `crosswalk.csv` maps those levels to one shared coding, one concept at a time, so that an effect can be compared across tables. It adds nothing to the tables themselves.

| column | |
|---|---|
| `concept` | the shared idea. So far only `profile_gender`: the gender of the person a profile describes. |
| `table`, `attribute`, `level` | the stored level text, exactly as in the table |
| `value` | the harmonized value. For `profile_gender` this is `female` or `male`. |
| `signal` | `explicit` when the attribute states the concept; `name` when it is carried by a gendered first name and the authors' own coding says which names are which; `photo` when it is shown only in a photograph and the authors' own coding of the photo says which |
| `evidence` | where the mapping comes from |

Every displayed level of a mapped attribute has a row (`(not shown)` has none, since nothing was shown), and each concept maps to at most one attribute per table. A `name` signal carries other things too: Pedersen's names also mark ethnicity (majority versus Turkish), so a gender contrast there is within the names the authors chose. A new concept is added with its allowed values in `metadata/tests/test_conj_design.py` (`CONCEPTS`) and a line here.

## Using the tables

- Attribute levels are text, even when they are numbers (price, age, number of children); parse them for a numeric analysis.
- No baseline level is recorded. AMCEs need one and the user chooses it; marginal means do not (Leeper, Hobolt & Tilley 2020).
- `irw_conj_long()` / `irw.conj_long()` give one row per respondent × profile × outcome (`item` = outcome column, `resp` = its value, `task`/`profile`/`attr_` as `trial_` columns): a view for explanatory IRT models (response ~ attributes + respondent), not a person × item matrix. It does not keep which profiles shared a task or what each outcome means; join `conj_outcomes` for that.
- For a conditional logit with an outside option (`mlogit`, Apollo), add a row with `profile = 0` to each task of an `opt_out = yes` outcome, with `choice = 1` when no profile was chosen.

## Scripts

Each script takes `<raw dir> <output dir>` and reads only the files named in its header. Downloads are untrusted: no code shipped with a deposit is ever run.
