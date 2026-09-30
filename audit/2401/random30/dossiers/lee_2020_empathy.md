# lee_2020_empathy (slot 14, agent c)

**Current state.** Live in `item_response_warehouse_4`; no item text. Not in withdrawals, table_changes, data_notes or validator results.

**Data (live, full read, 13,532 rows).** Rows = metadata.csv. 687 ids = the deposit's 746 rows minus the 59 with every JPSE item missing (checked on the source .sav). 20 items, all within 1-7; no sentinels, no dup id+item. cov_age 17-31, cov_study_year 1-6, categoricals labelled. Upload profile: conforms, passes (only the nested-range warning).

**Finding: keying.** The script header (`data/lee_2020_medical_students.py`) says items 11-20 "are already reversed (higher = more empathic)". That is false. On live data, items 1-10 average about 5.6 and items 11-20 about 2.8; within-block inter-item r is .51 and .52, between-block r is -.25 (97 negative pairs). The source .sav labels confirm that items 11-20 are the negatively worded JSPE stems (e.g. JPSE_12 "Attentiveness to my patients' personal experiences is irrelevant to treatment effectiveness"; JPSE_20 "...almost impossible for me to see things from my patients' perspective"). So resp is raw agreement on every item. That is correct for IRW, but a user must reverse 11-20 before any unidimensional model. The table has no item text, so nothing public tells them this. The script also says `JPSE_sum_total` equals the plain sum of the stored items, which would make the source's own total invalid (not re-checked). Proposed: a data note (like song_2023_rses), and correct the script's docstring when it is next touched.

**Rights.** No item text; skipped.

**Outcome.** data_note (high confidence on the fact).
