# trevisan_2018_mscs (strand: data)

**Lead** (round_log.md L18029, L18035, L18233, L18299; batch_191): the comment in `data/trevisan_2018_mscs.py` calls two mean-substitution imputations "data-entry errors". The question is whether this is a data_note, a fix, or no_action.

## Independent checks

**Live** (`datapages.item_response_warehouse_3:5xaj:v10_0.trevisan_2018_mscs:nyxs`, aggregate SQL only):
- 90,703 rows, 1,178 ids, 77 items, resp 1-5, 0 non-integer values.
- id 590 has 76 rows and lacks MSCS_54. id 885 has 76 rows and lacks MSCS_66. Their neighbours (589/591, 884/886) have 77 rows each. MSCS_54 and MSCS_66 each have 1,177 rows, against 1,178 for MSCS_1.

**Local raw** (`/home/ben/irw-queue-runner/itemtext/.cache/trevisan_2018_mscs/s002.sav`, sha256 9769a7f3...e083):
- There are 1178 x 77 = 90,706 MSCS cells. One is NaN (id 246, MSCS_12). Two are fractional: id 590 MSCS_54 = 3.88, and id 885 MSCS_66 = 3.64.
- 90,706 - 3 = 90,703, which equals the live row count.
- The mean of each respondent's other 76 items, with reverse items keyed as 6 - x (keying from the `_R` columns), is **3.882** for id 590 and **3.645** for id 885. These reproduce the fractional values to 2 dp.
- So these are person-mean substitutions (the source author's missing-data fill), not typing errors.
- The script comment's "row 589/884" is 0-based; the ids are 590/885.

## Verdict
The live table is correct. The two imputed cells are dropped, so they show as missing, which is the honest representation. The only error is the wording of the script comment ("data-entry errors" should say "person-mean imputations"). That wording changes no value and no analysis.

It fails #2529's data_note bar. The table already expresses the fact: 3 absent cells out of 90,706. There is no source value the user is being asked to trust. The ieswriting_molloy_2022 mean-fill precedent differs, because there the fill was *kept* in the data until #2514.

## proposed_outcome: `no_action`
Housekeeping, outside the outcome list: correct the comment when the script is next touched. The replacement text would read: "MSCS_54 = 3.88 (id 590) and MSCS_66 = 3.64 (id 885) are person-mean imputations in the source (each equals that respondent's keyed mean of the other 76 items); dropped as missing."

**Confidence:** high. **Group:** `data:script-comment-only`.
**Minutes:** ~10. **redivis_reads:** aggregate (3 queries), plus a local raw .sav read.
