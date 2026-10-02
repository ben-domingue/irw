# avilesgonzalez2019_ces (slot 20, agent d)

**State.** Live in item_response_warehouse_3; item text live (`irw_text`, 180 rows, 30 items). Not in withdrawals / table_changes / data_notes / validator results.

**Data (full read, 6,448 rows).** Matches metadata.csv (6,448; 215 ids; 30 items). Upload profile: conforms, passes, nothing to report. resp 1-6 on every item, no dup id+item. Negatively-worded CES items have low means (2.3-3.2) and positive ones high (4.3-5.2), so resp is raw (not reverse-keyed), consistent with item text (1=Very disagree ... 6=Strongly agree). The script drops one resp=7 row (documented in-script); live max is 6, so the script reproduces live.

Covariates: cov_age 22-63 ok. **cov_gender has one respondent coded 6**; the source .sav (figshare file 15243404, sha256 8e913f90...) labels only 1=female, 2=MALE, so 6 is an out-of-codebook value carried through (one blank gender too). One person, so the effect on any analysis is tiny. cov_department is NA for 149/215 ids, which is how the source has it.

**Rights.** Caring Efficacy Scale (Coates 1997) has no register row; `check_item_text`/`check_item_codes` (register passed explicitly) hit nothing on any text column. Silence is not a restriction -> no rights finding.
*Below the bar, noted only:* the item text's `language` is "Italian" but `item_text` holds the English original and `item_text_translated` is empty, so the administered Italian wording is not shipped.

**Source caveat.** None in the script header beyond the dropped resp=7.

**Outcome.** One finding: gender=6 on one id -> `needs_ruling` (group `single_value_cov_typo`: is a one-person out-of-codebook covariate value worth a rebuild?). Otherwise clean.
