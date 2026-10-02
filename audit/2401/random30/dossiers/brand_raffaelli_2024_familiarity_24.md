# brand_raffaelli_2024_familiarity_24 (slot 1, agent a)

**Current state.** Live in `item_response_warehouse` (v65_0), 48,262 rows = 818 ids x 59 items, matching `metadata.csv`. Item text live in `irw_text` (`__items`, 413 rows = 59 items x 7 options). Not in withdrawals, table_changes (a sibling, `liking_20`, has a 08-31 entry) or data_notes. It appears in the 09-06/07 string-NA and 09-08/09 NA-concentration sweeps: resp is now numeric (float) on live, so the string-NA part is already remedied. 660 NA resp, 295 of them in 5 ids with no answers at all.

**Data (full read, 48,262 rows).** Every item is 1-7 with all 7 categories used, no sentinels. No dup id+item. `cov_age` 18-83. `cov_gender` 1-4 (codes not labelled). `cov_condition` List_1..List_10, about 81 ids each. The id prefixes `bl_`/`bp_` line up one-to-one with `item_family` logo/name. Upload profile: conforms, passes. The only warning is resp_na.

**Rights.** The item text is the researchers' own generic stem ("Please rate to what extent you are familiar with this brand."). There are no register hits on `item_text` or on item codes, and there are no `_translated` columns.

**Source caveat.** Script `data/brand_brand_raffaelli_2024.r`, plus #1656 (closed). The item code is a *loop position*, and each position carries a different brand in each of the 10 lists. #1656 was fixed by carrying `cov_condition` through, and live has it. But a user who treats `item` as a brand is fitting a mixture of 10 brands per item, and the brand names aren't anywhere in IRW (they need `Brands 2024.xlsx` + the .qsf from ResearchBox 1892). The table can't state this itself, it's true of the source design, and nothing on the landing page says it. This meets #2529's test. Proposed `data_note` for the four `brand_raffaelli_2024_*` tables, medium confidence: the defect is already fixed, so the only question is whether the note is wanted.

**Outcomes.** 1 finding: `data_note` (medium). Everything else is clean.
