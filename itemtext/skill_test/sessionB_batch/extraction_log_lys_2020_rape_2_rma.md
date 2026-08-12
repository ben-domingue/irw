# Extraction log: lys_2020_rape_2_rma

## Source used
Łyś, A.E. et al. (2020/2023), "Psychometric properties of the Polish Updated
Illinois Rape Myth Acceptance Scale," *Current Psychology*,
DOI 10.1007/s12144-020-01249-3 (open access, CC BY 4.0). Reused the cached
PDF/text already fetched for the sibling table `lys_2020_rape_2_rma_pre`:
`.cache/lys_2020_rape_2_rma_pre/paper_dnb.pdf` / `paper_dnb.txt`. No new
fetch was needed or performed for this table.

## Relationship to sibling table `lys_2020_rape_2_rma_pre`
This table is the same 19-item Polish Updated IRMA scale as `rma_pre`,
administered a **second time** as part of the paper's **Study 2 (Test-Retest
Reliability)**. Confirmed from the paper text (`paper_dnb.txt` lines
333-348): "The questionnaire was administered a second time to 142
participants of Study 1, two weeks after the first measurement. The
participants filled out the paper-and-pencil version." — i.e. `rma_pre` =
first (Time 1) measurement, `rma` (no suffix) = second (Time 2 / retest)
measurement, same instrument, same 19 items, same item order, administered
to the identical 142-person sample two weeks apart.

This was cross-checked against the live ground-truth data before reusing the
item text (not just assumed from the name):
- `unique(gt$id)` for `lys_2020_rape_2_rma` has exactly **142** unique
  respondents — matching the paper's stated Study 2 retest sample size (142
  participants of Study 1) exactly.
- `cov_subsample` is uniformly `"Paper-Pencil"` for all 2698 rows — matching
  the paper's statement that Study 2 participants "filled out the
  paper-and-pencil version" (Study 1 was online + paper-pencil combined).
- `cov_field_cat` values (Human/Medical/Social/STEM) are consistent with the
  paper's reported Study 2 sample composition (human sciences, social
  sciences, medical sciences, STEM sciences students).
- Item naming is a straight `rma_pre{n}` -> `rma{n}` suffix swap with the
  same 1-19 numbering; no item was added, dropped, or reordered relative to
  `rma_pre`.

Given this, the item text was **reused directly** from the already-validated
`candidate_lys_2020_rape_2_rma_pre.rds` (built from Appendix Table 7's
verbatim Polish item wording), remapping `item` from `rma_pre{n}` to
`rma{n}` and `table`/`section_id` to this table's identifiers. No new
transcription was performed since it is literally the same instrument
instance, just a different administration wave — the paper does not present
different item wording for the retest (a test-retest design by definition
reuses identical item wording).

## has_bare_integer_items
FALSE for this table — items already carry semantic labels (`rma1` through
`rma19`) rather than bare integers, so no bare-integer reconstruction check
was applicable/needed.

## Structure discovered
19 items (`rma1`...`rma19`), single section, one 5-point Likert scale (1-5)
applied uniformly to all items, matching the paper's stated "1 = strongly
disagree" to "5 = strongly agree" anchoring (same non-reversed direction as
Debowska et al. 2015, per the paper's explicit statement — see the sibling
table's log for the full discussion of this scoring-direction check).
Ground-truth item and resp sets matched the candidate exactly (verified
below).

## Structure of output
Single section (`lys_2020_rape_2_rma_1`), `instrument` field identical to the
sibling table's (naming both the immediate Polish adaptation source
(Debowska et al. 2015) and ultimate scale origin (McMahon & Farmer 2011)),
`instructions` giving the 5-point Likert anchoring and scoring direction
(identical wording to `rma_pre` since it is the same instrument
administered a second time). `option_text` populated only at the scale
endpoints (resp=1 "zdecydowanie się nie zgadzam (strongly disagree)", resp=5
"zdecydowanie się zgadzam (strongly agree)"); resp=2-4 left blank since the
source paper does not verbally label the interior scale points.
`section_prompt` and `correct_response` left blank — no scale-level prompt
beyond the general instructions, and no correct/keyed answer for an
attitude-acceptance scale.

## Ambiguities
None beyond those already logged for the sibling `rma_pre` table (minor
typographic-quote normalization in items 17/19's item_text — see that log).
No new ambiguity was introduced by remapping to the `rma` item names, since
the item-to-text mapping is a mechanical 1:1 suffix substitution confirmed
against the ground-truth sample-size/subsample checks above, not a fresh
positional guess.

## Items not extracted
None — all 19 items (rma1-rma19) map to the ground-truth item set exactly,
reusing the sibling table's fully-extracted text.

## OCR / image-based extraction
No. Reused the sibling table's source text, which came from a clean, directly
extracted PDF text layer (not scanned/OCR'd) — Polish diacritics render
correctly and consistently, with no garbled characters or OCR-typical
artifacts. No new source material was processed for this table.

## Derived vs. directly-read values
`item_text`, `instrument`, `instructions`, and the endpoint `option_text`
values were not re-derived from scratch — they were carried over unchanged
from the already-validated `rma_pre` extraction (which itself read them
directly from the paper's Method section and Appendix Table 7). The only
values changed for this table are the identifier fields (`table`,
`section_id`, `item` suffix), which were mechanically derived from the
sibling's values plus the ground-truth item-name pattern (`rma_pre{n}` ->
`rma{n}`). This reuse is only valid because Study 2 is explicitly a
test-retest re-administration of the identical instrument, confirmed via the
sample-size and subsample cross-checks above — it would not be valid to
reuse text this way for tables that merely share a similar name.

## Source type used
Paper appendix (PDF), specifically the peer-reviewed journal article's
Appendix Table 7 (via the sibling table's cached extraction), supplemented
by the Method section's Study 2 test-retest design description
(`paper_dnb.txt` lines 333-348) used to confirm the pre/post relationship.
Not OSF raw-data files, not a website codebook, not raw-data column headers.

## Validation
Programmatically compared candidate vs. cached ground truth
(`.gt_lys_2020_rape_2_rma.rds`):
- `identical(sort(unique(candidate$item)), sort(unique(gt$item)))` -> **TRUE**
  (both are `rma1`...`rma19`, 19 items, no set difference either direction)
- `identical(sort(unique(candidate$resp)), sort(unique(gt$resp)))` -> **TRUE**
  (both are `1 2 3 4 5`)

Result: **exact match**, no discrepancies to log in `pending_index_notes.csv`.
