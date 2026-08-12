# Extraction log: florida_twins_behavior_panas

## Source type used
Reused the cached "Behavior and Environment Survey Codebook" (Schatschneider, Lonigan &
Taylor, LDbase, http://ldbase.org/documents/c4669c5b-9853-45be-a33f-9dff7102de20) already
downloaded and cached by the prior-session sibling table `florida_twins_behavior_rcads`
at `itemtext/skill_test/sessionB/.cache/florida_twins_behavior_rcads/codebook.doc` (same
source document underlies `_rcads`, `_cads`, and `_panas` — all are subscales inside one
FTP-BE codebook). Did not re-fetch from LDBase.

**Important source-format note (why this required a second conversion pass):** the
existing `codebook.txt` (plain-text, produced via `libreoffice --convert-to txt`) had
lost the PANAS item table entirely — the section header, instructions, and derived-score
formulas were present, but the 20-word x 5-point response grid itself converted to blank
lines because it was a Word table object, not linear text. Re-converted the same cached
`codebook.doc` to HTML (`libreoffice --headless --convert-to html`) instead, which
preserved the table cells as literal text. This affects only the PANAS section here; the
`_rcads` and `_cads` extractions used numbered running-text items that survived the plain
-text conversion fine, so this discrepancy is specific to the tabular PANAS layout and is
being flagged in case the same table-loss issue recurs for other tabular sections in this
codebook or in codebooks converted the same way.

## OCR / image-based extraction
Not applicable — no OCR was used. The source is a native Word document (`.doc`) with a
machine-readable table structure; the fix was switching the conversion target format
(HTML instead of plain text) to a format that preserves table-cell text, not image-based
recognition.

## has_bare_integer_items
FALSE, confirmed. `item` values in the live data are named codes (`panasN` / `panas_N`),
not bare integers, so no positional reconstruction was needed for item identity — the
codebook's own `panas[#]` / `panas_[#]` numbering (1-20) in the table's leftmost column
maps directly onto the ground-truth item suffix.

## Dual naming convention: panasN vs. panas_N
Ground truth has 40 distinct items: `panas1`..`panas20` (no underscore) and
`panas_1`..`panas_20` (underscore) -- NOT a naming artifact to collapse. The codebook
documents PANAS **twice**, exactly mirroring the pattern already seen in the sibling
`florida_twins_behavior_rcads` table (which has the identical `rcadsN` self / `rcads_N`
parent split):

- **Youth Booklet, "PANAS" section** (self-report, ages 9+): derived-score formula block
  reads `panas_PA = mean of panas1 panas3 panas5 ...` (no underscore) -> this is the
  **self-report** administration, item codes `panas1`-`panas20`.
- **Parent Booklet, "PANAS - Parent" section**: derived-score formula block reads
  `P_panas_PA = mean of panas_1 panas_3 panas_5 ...` (underscore) -> this is the
  **parent-report** administration (parent rates each twin child on the same PANAS word
  list), item codes `panas_1`-`panas_20`.

Both sections present the **identical 20-word item list in the identical order**
(Interested, Distressed, Excited, Upset, Strong, Guilty, Scared, Hostile, Enthusiastic,
Proud, Irritable, Alert, Ashamed, Inspired, Nervous, Determined, Attentive, Jittery,
Active, Afraid) — this is the standard Watson, Clark & Tellegen (1988) 20-item PANAS
word list, in its standard published order (positive/negative items interleaved), with
no child-adapted wording change. Only the instructions sentence differs: the self-report
form asks "for how you feel in general," the parent form asks "for how your child feels
in general. Please fill this out for each child" (same twin T1/T2 dual-response layout
seen in the `_rcads` parent form). `correct_response` is blank for both (trait
affect-frequency scale, no scoring key).

Response scale (5-point, identical for both forms), printed as literal column headers
above the circled 1-5 numbers: 1 = "Very Slightly or Not at All", 2 = "A Little",
3 = "Moderately", 4 = "Quite a Bit", 5 = "Extremely".

## Derived vs. directly-read values
- `item_text` (the 20 PANAS words) and the 5-point response-option labels are directly
  read from the codebook's table cells (via the HTML re-conversion), not derived.
- `instructions` text is directly read (literal instruction paragraph preceding each
  PANAS table).
- The two `panas_PA` / `panas_NA` (and `P_panas_PA` / `P_panas_NA`) derived mean-score
  formulas in the codebook were NOT used for anything in this extraction — they only
  confirm which item-code set belongs to which administration and were not written to
  the candidate file.

## Structure
- Two sections (`florida_twins_behavior_panas_self`, `florida_twins_behavior_panas_parent`),
  each with its own literal `instructions` text; `section_prompt` left blank (no
  passage/testlet grouping beyond the section itself).
- `item` = `panas[1-20]` (self) / `panas_[1-20]` (parent), matched 1:1 by item number to
  the codebook's `panas[#]` / `panas_[#]` table row labels.
- `option_text`/`resp`: 1-5 mapped onto the instrument's own printed anchor labels.

## Items not extracted
None — all 40 ground-truth items (20 self + 20 parent) matched. Validated exact
item/resp match against the cached ground truth
(`.gt_florida_twins_behavior_panas.rds`): `item match: TRUE`, `resp match: TRUE`,
200 rows (40 items x 5 response options).

## Files
- Build script: `build_panas.R`
- Candidate output: `candidate_florida_twins_behavior_panas.rds`
