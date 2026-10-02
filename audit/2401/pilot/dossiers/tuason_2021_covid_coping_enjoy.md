# tuason_2021_covid_coping_enjoy (strand: data)

**Lead** (round_log.md L18200-18215, L18286-18287; batch_197): `data/tuason_2021_thriving_covid.py` should rebuild Enjoy_* from the `Emjoy` pick string or drop the middle well-being group; 321 all-zero rows are false.

## Independent checks

**Live** (`datapages.item_response_warehouse_3:5xaj:v10_0.tuason_2021_covid_coping_enjoy:rzws`, aggregate SQL only):
- 21,574 rows = 938 ids x 23 items, resp in {0,1}, 0 NULL.
- Per-id sum of resp: 0 for **322 ids**, 2 for 1, 4 for 2, 5 for 612, 8 for 1. This matches the round log exactly.
- I joined on id to live `tuason_2021_wellbeing` (`:b8t3`), with wb = mean(resp-17). That is the paper's Well_being_Mn, which the round log confirmed equals mean(WB-17). The 322 all-zero ids have wb in [3.75, 5.625]. There are none below 3.5 or above 5.625, and all 167 ids in the 5.0-5.5 bin are all-zero. The 616 non-zero ids span 1.125-7.0.

**Local raw** (`/home/ben/irw-queue-runner/itemtext/.cache/tuason_2021_covid_coping_enjoy/s002.sav`, sha256 c6d0daf7...3230; this is the same file the script downloads):
- `Well_being_3groups` labels: 1 = "lowest 1-4.63", 2 = "middle 4.64-5.63", 3 = "highest 5.64-7.0".
- All-zero respondents by group: 1 (low) / 321 (middle) / 0 (high). The middle group has 1 respondent who is not all-zero.
- Every one of the 938 `Emjoy` strings holds exactly 5 comma-separated picks, drawn from the 23 codes 1-3, 5-24. Those are the same numbers as the Enjoy_NN columns.
- The paper (article.txt) says: "Read through the list first and then select 5 things you enjoy". The paper compares only the low and high groups, which is presumably why only those rows were dummy-coded.
- Rebuilding Enjoy_NN = 1[NN in Emjoy] matches the shipped 0/1 on all 23 cells for 610/616 non-zero rows, with 99.9% cell agreement. The 6 rows that disagree have sums of 2, 4, 5, 5, 8 and 4. Emjoy (always 5 picks) is the consistent record.

## Verdict
**Confirmed.** 322 respondents (34% of ids) carry false zeros on all 23 items: 321 in the middle group and 1 in the low group. This changes any analysis. Item means are biased down by about a third, and the "picked nothing" pattern is spurious. This is an IRW processing defect, not a source caveat: the source's own `Emjoy` variable holds the true picks.

## proposed_outcome: `fix`
In `data/tuason_2021_thriving_covid.py`, build the Enjoy table from `Emjoy`, not from the Enjoy_* dummies:
`Enjoy_NN = int(str(int(NN)) in [p.strip() for p in Emjoy.split(",")])` for the 23 existing column names. Keep the item codes (the live item text joins on them) and keep id = row index (ids stay stable).

Expected output: 938 x 23 = 21,574 rows, every id summing to 5. That changes the 322 all-zero ids plus the 6 inconsistent rows.

After the fix:
- add a `metadata/table_changes.csv` row;
- the live item text's `public_note`, which discloses this defect, then needs a `claim_edit`;
- the other four tuason tables are regenerated unchanged (the script writes all five) and should be cmp-checked, not re-uploaded.

Rejected alternative: dropping the middle group would discard 322 valid respondents.

**Confidence:** high. **Group:** `data:rebuild-from-source-variable`.
**Minutes:** ~15. **redivis_reads:** aggregate (4 queries), plus a local raw .sav read.
