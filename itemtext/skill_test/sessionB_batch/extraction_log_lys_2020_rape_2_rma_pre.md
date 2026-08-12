# Extraction log: lys_2020_rape_2_rma_pre

## Source used
Łyś, A.E. et al. (2020/2023), "Psychometric properties of the Polish Updated
Illinois Rape Myth Acceptance Scale," *Current Psychology*,
DOI 10.1007/s12144-020-01249-3 (open access, CC BY 4.0). Cached PDF/text at
`.cache/lys_2020_rape_2_rma_pre/paper_dnb.pdf` / `paper_dnb.txt`. The full
19-item Polish item wording is given verbatim in **Appendix, Table 7** ("Items
of Polish Updated IRMA", `paper_dnb.txt` lines 641-664). The response scale
description ("19 items scored on a 5-point Likert scale ... from
1 = 'strongly disagree' to 5 = 'strongly agree'") is given in the Method
section (`paper_dnb.txt` lines 152-154). An `osf_files.json` listing was also
cached (OSF project https://osf.io/eu4qd/files/osfstorage, e.g.
`study 3 validity.sav`) but the raw SPSS data files were not needed since the
paper's own appendix already contains the full item text; the OSF listing
was left unused beyond initial reconnaissance.

## Structure discovered
19 items (`rma_pre1`...`rma_pre19`), single section, one 5-point Likert scale
(1-5) applied uniformly to all items, matching the paper's stated "1 = strongly
disagree" to "5 = strongly agree" anchoring (note: the paper mentions that
some other studies, e.g. Debowska et al. 2015 and McMahon & Farmer 2011, used
a reversed 1=agree/5=disagree scale, but the authors of this paper explicitly
state they used the same non-reversed direction as Debowska et al. — this is
the direction reflected in `instructions`). Ground-truth item and resp sets
matched the candidate exactly (verified below).

## Structure of output
Single section (`lys_2020_rape_2_rma_pre_1`), `instrument` field naming both
the immediate Polish adaptation source (Debowska et al. 2015) and ultimate
scale origin (McMahon & Farmer 2011), `instructions` giving the 5-point Likert
anchoring and scoring direction. `option_text` populated only at the scale
endpoints (resp=1 "zdecydowanie się nie zgadzam (strongly disagree)", resp=5
"zdecydowanie się zgadzam (strongly agree)"); resp=2-4 left blank since the
source paper does not verbally label the interior scale points (only the
end-anchors are given). `section_prompt` and `correct_response` left blank —
no scale-level prompt beyond the general instructions, and no correct/keyed
answer for an attitude-acceptance scale.

## Ambiguities
- Item 17 and item 19 in the source text contain internal quotation marks
  around "gwałciciel" (item 17) and "nie" (item 19) rendered with typographic
  double-quote characters (") in the PDF text extraction; these were
  transcribed faithfully as plain text without the quote marks in the
  candidate `item_text`, matching how they appear cleanly in the rest of the
  paper's prose style — this is a minor formatting normalization, not a
  content change.
- The paper reports the scale under three different CFA models (Model 1/2/4)
  with items assigned to different subfactor codes (SA/MT/JD/NR/SL) in Table
  7; this subfactor coding is not part of the item content itself and was not
  encoded in the extraction (no `item_family` column populated), consistent
  with the benchmark's focus on item/response text only.

## Items not extracted
None — all 19 items (rma_pre1-rma_pre19) were extracted from the Appendix and
match the ground-truth item set exactly.

## OCR / image-based extraction
No. The cached source text (`paper_dnb.txt`) is a clean, directly extracted
PDF text layer (not scanned/OCR'd) — Polish diacritics (ś, ł, ą, ę, ż, ć, ń)
render correctly and consistently, item text has no garbled characters or
OCR-typical artifacts (e.g., no misrecognized letter substitutions), and the
item text in the candidate `.rds` matches the cached text verbatim,
character-for-character (confirmed by direct comparison above).

## Derived vs. directly-read values
None derived. All fields (`item_text`, `instrument`, `instructions`,
`option_text` endpoint labels) were read directly from the source paper's
Method section and Appendix Table 7; no values were computed, inferred beyond
what's explicitly stated, or reconstructed from indirect evidence.

## Source type used
Paper appendix (PDF), specifically the peer-reviewed journal article's
Appendix Table 7, supplemented by the Method section's scale-description text
in the same PDF. Not OSF raw-data files, not a website codebook, not raw-data
column headers.

## has_bare_integer_items
FALSE for this table — items already carry semantic labels (`rma_pre1`
through `rma_pre19`) rather than bare integers, so no bare-integer
reconstruction check was applicable/needed.

## Validation
Programmatically compared candidate vs. cached ground truth
(`.gt_lys_2020_rape_2_rma_pre.rds`):
- `identical(sort(unique(candidate$item)), sort(unique(gt$item)))` → **TRUE**
  (both are `rma_pre1`...`rma_pre19`, 19 items, no set difference either
  direction)
- `identical(sort(unique(candidate$resp)), sort(unique(gt$resp)))` → **TRUE**
  (both are `1 2 3 4 5`)
