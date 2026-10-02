# hoai_2026_teaching_presence (slot 3, agent a)

**Current state.** Live in `item_response_warehouse_5` (v6_0), 2,900 rows = 580 x 5, matching metadata. Item text live in `irw_text_2` (25 rows). Not in any ledger or results file.

**Data (full read).** TP1-TP5 are 1-5, with no NA and no dup id+item. TP1 and TP4 never use 1, which the script header already documents as floor non-use. The covariates are small integer codes (gender 1-3, age band 1-4, year 1-5, major/program/university type), with no out-of-range values. Upload profile: conforms, passes, with one nested-range warning (a false alarm).

**Rights.** A researcher-built questionnaire (Mendeley tdsspksw83, CC BY 4.0). The Vietnamese administered wording is in `item_text`, and the authors' own English is in `_translated` (their README says so). No register hits on either column.

**Source caveat.** The script header (`data/hoai_2026_blended_learning.py`) states nothing beyond floor non-use. The itemtext notes confirm the level counts against the raw workbook, 5/5.

**Outcome.** Clean, `no_action` (high).
