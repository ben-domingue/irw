# meloni_2015_deq_oe_parent (slot 15, agent c)

**Current state.** Live in `item_response_warehouse_3`; item text live as `irw_text_2/meloni_2015_deq_oe_parent__items` (216 rows, 36 items). Not in withdrawals, table_changes, data_notes or validator results.

**Data (live, full read, 2,736 rows).** Rows = metadata.csv. **76 unique ids (parents), under the 100 floor.** 36 items (4 stimuli x 9 explanation categories). resp is 0-5, a count of coded mentions. That matches the script's note. Nonzero values per id x stimulus look like counts (mostly single 1s), not a mention order. 10 items are constant 0 (every Aesthetic and "I don't know" category, plus two Other). This is faithful to the source, so not recorded. No dup id+item. The covariates are unlabelled numeric codes (country 0-23, job 0-10). A few 0s where the scale is 1/2 (cov_disability_family/friend, cov_job_father, cov_country_*) look like missing codes. They affect 2-3 people each; below the bar. Upload profile: conforms, passes; warnings are imputed_values (count data), nested ranges and sample_floor.

**Rights.** Register run on item_text, section_prompt, instructions, option_text and the `_translated` columns: no hits. The instrument is authored by the study (PLOS ONE, CC BY). Aside, below the bar: `language` says Italian, but item_text holds English and `_translated` is empty.

**Source caveat.** Script header: raw counts shipped rather than the paper's presence/absence collapse. That is documented in the script and meets no #2529 need beyond what the resp values show.

**Outcome.** One recorded finding: sample under 100 (76 ids). needs_ruling on floor policy for already-published tables; not investigated further.
