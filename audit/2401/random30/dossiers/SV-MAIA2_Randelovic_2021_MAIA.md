# SV-MAIA2_Randelovic_2021_MAIA (slot 26, agent e)

**State.** Live in `item_response_warehouse` (25,086 rows = metadata.csv). Item text live as `sv-maia2_randelovic_2021_maia__items` in `irw_text` (lower-case name; 222 rows, language Serbian, with `_translated`). Not in withdrawals/table_changes/data_notes. Present in the string-NA sweeps (`resp_string_na_2026-09-0{6,7}`: 5,846 `"NA"`, 23.3%) and `resp_na_shape_2026-09-09` (bucket `E_scattered`); legacy sweep flagged dup id+item as "likely ok".

**Data (full live read; upload profile: blocked by `resp_numeric`, 5,846 literal `"NA"`).** 449 ids x 37 items, resp 0-5 (MAIA-2 scale) on every item. Three groups: students T1 (`wave=0`, 229 ids), students T2 (`wave=1`, 229 ids), practitioners (`wave` NA, 220 ids, disjoint ids). dup id+item is fully explained by `wave`.

**Finding 1 - 5,846 placeholder rows for students with no T2 (fix, high).** All 5,846 `"NA"` rows are `wave=1`, all have `date` = `"NA"` too, and they are exactly 158 students x 37 items; only 71 students actually have T2 data. So they are not scattered missingness (the 09-09 bucket `E_scattered` is wrong: the concentration is by id x wave, which that sweep cannot see). Root cause in `data/SV-MAIA2_Randelovic_2021.R`: `remove_na()` excludes `id` and `date` and expects `ncol-2` NAs, but it is called on the T2 frame before `MAIA2_final` is renamed to `date`, so the date column is counted and an all-empty row has `ncol-1` NAs and is never dropped. Fix: drop the 5,846 rows (resp becomes numeric). Group: the #2029 string-NA cleanup; the sibling SV-MAIA2 tables (SHS/DASS/ERQ/MAAS/DELTA) share the helper and are worth one look in the same fix.

**Rights.** Register on `item_text`: no hits. On `item_text_translated`: one hit, STAI row via stem "I am tense" in MAIA2_1 ("When I am tense, I notice where in my body the tension is located"). False alarm: this is MAIA-2 wording, not STAI. MAIA-2 has no register row and no stated restriction (distributed free by Mehling/UCSF). no_action; note for tuning the STAI stems (bare "I am tense" is too loose).

**Source caveat.** Script header: no stated defect. Name is mixed-case (`name_charset` warn); below the bar.
