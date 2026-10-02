# robbins_2019_farmtype_belief (slot 23, agent d)

**State.** Live in item_response_warehouse_3; no item text. Not in withdrawals / table_changes / data_notes / validator results.

**Data (full read, 2,406 rows).** Matches metadata.csv (2,406; 802 ids; 3 items). Upload profile: conforms, passes, nothing to report. Each item takes resp 1-7 using all 7 values; no dup id+item; no NA. Covariates are plausible: cov_age 18-74, cov_female 0/1, cov_region 1-4, cov_rural 1-3, cov_education 1-6, cov_liberal 1-7, cov_framing hours(430)/wtp(372). The two samples are stacked with offset ids and cov_framing, per the collapse convention.

**Source caveat.** The script header (`data/robbins_2019_dairy_tiestall.py`) says the exact item wording wasn't found, so the items ship under their column names. The table can express that, and it isn't a data problem.

**Outcome.** `no_action` (high).
