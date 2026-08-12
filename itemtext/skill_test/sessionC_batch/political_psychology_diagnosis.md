# political_psychology discrepancy: diagnosis (no fix applied)

## Answer to the three questions

1. **Is the ground truth stale or fresh?** Neither, precisely — it's
   **wrong for a specific 7-item subset**, and demonstrably so, independent
   of any timing/versioning question. See Step 1.
2. **What caused the false "validation passed" claim?** Nothing in the
   skill's logic — the candidate's validation was actually **correct**.
   The thing that was wrong is the ground truth used to grade it. See Step 2.
3. **Is this systemic?** No. Checked every other table in the batch that
   used script-based positional reconstruction; found no second instance of
   this pattern. See Step 3.

This means the earlier report's characterization of `political_psychology`
as a "genuine item-order mismatch, possible extraction bug" was backwards:
**the candidate's extraction is correct; the eval's ground truth is wrong.**

## Step 1: is the cached ground truth stale?

Pulled `political_psychology` fresh via `irw::irw_fetch()` just now (404,595
rows, 552 unique ids — real raw response data) and compared per-item `resp`
value sets against `../sessionA_batch/groundtruth_political_psychology.rds`.

**30 of 37 items match exactly.** The other 7 (items 7, 12, 14, 21, 27, 28,
30) differ — and these are precisely the items where the candidate's
extraction log made specific, checkable claims (item 7→`abort` 1-4, item
14→`djt` 1-4, item 27→`votereport` 1-3, item 28→`voting` 1-3) plus the
items flagged as content-mismatched in the previous report's spot check
(12, 14, 21, 30).

| item | fresh `irw_fetch()` resp set | cached "ground truth" resp set | candidate's claim |
|---|---|---|---|
| 7 (abort) | 1,2,3,4 | 1,2,3,4,5,6 | 1-4 ✓ matches fresh |
| 14 (djt) | 1,2,3,4 | 1,2,3,4,5,6,7 | 1-4 ✓ matches fresh |
| 27 (votereport) | 1,2,3 | 1,2,3,4,5,6,7 | 1-3 ✓ matches fresh |
| 28 (voting) | 1,2,3 | 1,2,3,4,5,6,7 | 1-3 ✓ matches fresh |

The candidate's claims match the live data exactly and contradict the
cached ground truth on all four. This is the opposite of what the earlier
report assumed.

**Confirmed against the actual build script**, `data/political_psychology.R`
(the script that produces the live IRW table), which explicitly:
- recodes `abort` and `djt` by setting values 5/6 to `NA` (leaving 1-4 — the
  candidate's claim, not the cached ground truth's 1-6/1-7),
- recodes `votereport`'s 6/3 to `NA` and collapses 5/4 into 3 (leaving
  1-3), and maps `voting` directly to 1/2/3 (trump/clinton/other).

This is airtight: the candidate's item mapping matches both the live raw
data and the documented recoding logic in the repo's own build script. The
**cached ground truth is the thing that's wrong**, not the extraction.

**Provenance of the wrong ground truth**: traced `groundtruth_political_
psychology.rds` back through `sessionA_batch/01_select_batch.R` →
`sessionA/02_pull_all.R`, which built it via `irw_itemtext("political_
psychology")` — i.e., this is not raw response data pulled for this eval at
all, it's the **pre-existing curated itemtext database entry already on
Redivis** for this table (built by some earlier, unrelated process, before
this eval existed). That entry appears to itself contain an item-mapping
error for these 7 items — plausibly the same class of positional/column-
order mistake this eval's bare-integer fix (Fix 1) is designed to catch,
just committed by whoever originally populated Redivis's itemtext table for
`political_psychology`, not by the skill under test.

## Step 2: the skill's validation logic itself

Since Step 1 fully explains the discrepancy, there's no separate bug to
find in the skill's validation step — it did what it claimed (re-derived
item order mechanically from `data/political_psychology.R`, cross-checked
distinctive recoded ranges item-by-item) and got the right answer. The
"false positive" was in **grading this eval against a bad ground-truth
source**, not in the skill's own extraction-time check.

## Step 3: is this systemic across other script-based-reconstruction tables?

19 tables in the batch reference a `data/<table>.R` build script in their
extraction log. Of those, only `political_psychology`'s log makes
`political_psychology`-style **per-item quantitative validation claims with
explicit checkmarks** (`item N → variable, range ✓`). None of the other 18
use that exact pattern, so I instead checked the 5 other tables that failed
the resp-alignment tripwire (the outcome-level signal a false validation
claim would actually produce), regardless of overall score:

- **`chile_2023_social-welfare-survey_h`**: log claims "matched exactly for
  all 13 items" against cached ground truth. Direct check: **12/13 exact**;
  item `h3_e` has ground truth `{1,2}` vs. candidate `{1,2,3}` — the
  candidate documented the full 3-point scale while the observed live data
  for that specific item apparently never realized the 3rd category. This
  is a minor, different, and much lower-stakes discrepancy (a superset, not
  wrong content) — not the same false-validation pattern.
- **`eammi_grahe_2018_socmedia`**, **`sv-maia2_randelovic_2021_hexaco60`**,
  **`shu_2025_translation_eib`**: logs describe partial/documented
  uncertainty (e.g. QC-flag items, unconfirmed response-scale point counts)
  rather than claiming a clean pass — consistent with their non-1.0
  resp-alignment rates; no false-confidence claim to falsify.
- **`sv-maia2_randelovic_2021_erq`**: log explicitly states the response
  scale is unconfirmed and leaves `option_text` blank rather than guessing
  — an honest admission, not a false positive.

**No other table shows political_psychology's pattern** (a confident,
specific, checkmarked validation claim that directly contradicts the
ground truth it was checked against). This looks isolated to
`political_psychology`, and the root cause is a bad ground-truth source for
that one table, not a systemic flaw in the skill's validation logic.

## Bottom line

- Not a skill bug. Not systemic.
- The actual defect is in this eval's ground-truth data for
  `political_psychology` specifically (7 of 37 items), inherited from a
  pre-existing Redivis itemtext entry that predates this eval and was never
  itself verified against the live table.
- Practical implication for the batch's reported numbers: `political_
  psychology`'s 0.39 item_text similarity score is an artifact of grading
  against bad ground truth, not a real extraction failure — similar in
  spirit to the `fad_dataset1`/`fad_dataset2` finding from the prior pass,
  though the mechanism here (wrong pre-existing itemtext entry) is
  different from that one (bilingual column-comparison bug in the grading
  script). Re-scoring this table would require either correcting the 7
  wrong items in `groundtruth_political_psychology.rds` or excluding the
  table from the aggregate with a note — not a `grade_batch.R` code change,
  since the grading logic itself is working correctly here.
- No skill fix, grading-script fix, or ground-truth correction was applied
  in this pass, per your instruction — this is diagnosis only.
