# gilbert_meta_35 (claim strand)

**Lead:** issue #1646 lists this as one of 13 issues-page callouts that predate 2026-08-17 and have never been re-checked. That lead is partly stale. The entry was removed and then re-added with new wording on 2026-08-25 (datapages/irw `76ac3aeb7`, `5295beb1f`), after the #1615 fix. So what needs checking is the 2026-08-25 wording. The older wording ("codebook contain only 8 items, response data contains 12") is no longer on the page. Nor is the drafted replacement in `itemtext/fixes/itemtext_issues_suggestions.md` ("values_i/j/k/l have no item text"), and that draft names the wrong four items. Do not paste it.

## Claim as stated publicly
Checked on the live page https://itemresponsewarehouse.org/itemtext_issues.html on 2026-09-29. It is identical in datapages/irw `origin/main` (`2695c9cf2`):

> item text covers 8 of the 12 `values_*` items. The other four (`values_b`, `values_h`, `values_k`, `values_l`) are omitted: the study's replication do-file builds its democratic-values scale from only eight of the twelve, and no wording is published for the other four. The eight are mapped to their text using the source `.dta`'s variable labels, which name six of them outright; note that `values_e` and `values_j` are reverse-worded, so their response options run in the opposite direction to the other six

## Independently checked
1. **Live response table** (`item_response_warehouse:v65_0.gilbert_meta_35`, aggregate SQL). There are 12 items, `values_a`..`values_l`, each with about 3,400-3,500 rows and about 1,430 ids. `resp` runs 1-4. Waves 0/1/2 hold 1,317, 1,233 and 986 ids. The claim's "12" holds.
2. **Live item text** (`irw_itemtext`, 32 rows). There are 8 items (a, c, d, e, f, g, i, j) × 4 options. b, h, k and l are absent. The claim's "8" and its four named items hold.
3. **The do-file.** I fetched `Replication_do_file.do` through the Dataverse API (doi:10.7910/DVN/UMRAM7, CC0). Line 49 reads `gen values1 = values1a + values1c + values1d + values1e + values1f + values1g + values1i + values1j`. This holds.
4. **The `.dta` labels.** I fetched `Deliberation_Data` with `?format=original`. Variables a, c, d, f, g and i carry `RECODE of <Swedish var>` labels. b, e, h, j, k and l are unlabeled. So "six named outright" holds. The Read me.docx gives only scale-level descriptions ("Measure of democratic values..."), with no item wording. That is consistent with "no wording is published for the other four", checked within the deposit only.
5. **Reverse keying against the data.** I correlated each item with the mean of c, d, f, g and i (per id and wave, aggregate SQL). e = +0.16 and j = +0.25, both positive and in line with the scale. The response data are therefore already reverse-scored for e and j, so the live option map (e/j: resp 1 = "Absolutely agree") is the right direction, and so is the claim's warning. The four omitted items sit at about 0.04-0.13, which fits their being non-scale items.
6. The 2026-08-30 audit diff (`itemtext/fixes/diffs_vs_published/gilbert_meta_35.md`) matched coverage and text exactly. I took this as corroboration only, not as evidence.

## Verdict
The claim holds against live data today and is precise: it gives counts, names the items and gives the reason. Nothing is stale.

- **proposed_outcome:** `no_action`
- **confidence:** high
- **group:** `issues_page_pre0817:already_rewritten` (a #1646 entry whose wording was replaced after 2026-08-17 and only needs confirming)
- **minutes:** ~20
- **redivis_reads:** aggregate (3 queries on the response table) + rows:32 (the item-text table)

Side note, no action for this table: #1646's list should mark this entry as re-verified. Other entries on it may also have been rewritten since 2026-08-17 (gilbert_meta_42 was, in the same commit).
