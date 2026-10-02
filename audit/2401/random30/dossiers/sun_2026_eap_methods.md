# sun_2026_eap_methods (slot 6, agent a)

**Current state.** Live in `item_response_warehouse_3` (v10_0), 3,250 rows = 650 x 5, matching metadata. Item text live in `irw_text_2` (25 rows). Not in any ledger.

**Data (full read).** Five items, all 1-5, with no NA and no dup id+item. `cov_identity` is 1/2/3 (485/124/41). The item codes are the full English column headers from the source file, and that is by design. Upload profile: conforms, passes, nothing reported. The batch_183 notes recompute the paper's Table 7 from the deposit and match 75/75.

**Rights.** The questionnaire was written by the authors (PLOS ONE S1 File, CC BY 4.0). No register hits. There are no `_translated` columns.

**Source caveat / claim.** Two points, both below the bar or already tracked:
1. `language=Chinese` is inferred while `item_text` carries the authors' English. This is the open language-convention ruling that batch_182/183 already logged (it covers sun_2026_eap x4, sun_2024 x6 and sun_2021), so it is not a new finding.
2. Teachers and students answered one stem under different instructions (teachers rate on observation, students on preference), and `cov_identity` is unlabelled. The shipped `instructions` field states the split, so a user of the item text sees it. This does not meet #2529's test on its own.

**Outcome.** Clean, `no_action` (high).
