# amatus_cipora_2024_fsmas_se (slot 21, agent d)

**State.** Live in item_response_warehouse_2; item text live (`irw_text`, 45 rows, 9 items, no language/_translated columns). Not in withdrawals / table_changes / data_notes / validator results.

**Data (full read, 2,322 rows).** Matches metadata.csv (2,322; 258 ids; 9 items). Upload profile: conforms, passes; `imputed_values` concentration warning only. resp 1-5, no dup id+item.

Source re-checked independently: OSF gszpb, `AMATUS_codebook.xlsx` (sha256 a131e418...) and `AMATUS_dataset.csv` (sha256 d4f8a6b5...). The codebook lists every FSMAS_SE item as "1: yes ... 5: no", with **Reversed = yes for SE1-SE4** (the positively worded, egalitarian items) and no for SE5-SE9. In the data, SE1-SE4 are clearly stored reverse-keyed: SE2 "Studying mathematics is just as appropriate for women as for men" has 223/258 at 5, and all 36 inter-item correlations are positive (0.08-0.58). Summing the stored items reproduces `score_FSMAS_SE` exactly. So in the stored data, 5 is the *least* stereotyped answer on every item.

**Finding 1 (item text, fix, high).** The live `__items` table maps resp 1=yes ... 5=no for all nine items, including SE1-SE4. For those four items the mapping is backwards (stored 5 = "yes"). A user reading option_text would invert four of the nine items. The response data are faithful to the source; the item text needs the SE1-SE4 option rows reversed (or a note that resp is reverse-keyed).

**Finding 2 (source caveat, data_note, medium).** The AMATUS codebook says higher score_FSMAS_SE means *more* stereotype endorsement, but with the items as stored, higher means less (mean 41.7 of 45 among teachers). A user should know that resp for SE1-SE4 is reverse-keyed at source and that all nine items run toward non-endorsement. This caveat can go in the item-text fix instead, so it's medium.

**Finding 3 (covariate, needs_ruling).** `cov_age` is NA for all 258 ids (teachers in the source have no numeric age), and the script drops `age_range`, which the source has for all 258 (`cols_to_drop` in `data/amatus_cipora_2024.py`). So the table has no usable age even though the source provides it. `cov_math_load` is also all NA (the source has none for teachers), which is harmless. Group `amatus_family_covariates` (probably affects the sibling amatus_* tables too).

**Finding 4 (covariate, needs_ruling).** `cov_ease_teaching_*` and `cov_preference_teaching_*` (1-5 Likert) carry -1 = "not yet taught" (per the codebook) for 41 of 258 ids. That is a sentinel inside a numeric covariate: it biases any numeric use, but recoding it to NA would discard real information. Group `cov_sentinel_in_likert`.

**Rights.** FSMAS (Fennema-Sherman) has no register row; `check_item_text` (register passed explicitly) and `check_item_codes` hit nothing.

No script_drift: live reproduces the script.
