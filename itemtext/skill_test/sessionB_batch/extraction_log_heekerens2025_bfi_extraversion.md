# Extraction log: heekerens2025_bfi_extraversion

## Source used
Dictionary URL (https://zenodo.org/records/14984624) points to a Zenodo record for
Heekerens et al. (2025), "The Dissociative Symptoms Scale (DSS): Psychometric properties
of scores on a German version in clinical samples" (*Psychological Assessment*,
10.1037/pas0001432). The Zenodo record contains a single data file, `dss_2.xlsx`
(cached at `.cache/heekerens2025_bfi_extraversion/dss2.xlsx`), whose page description
explicitly lists the measures included: "PDS-5, PHQ-8, **BFI-10**, FDS (44-item), and
SDQ-20." The xlsx column headers (`extraversion_1_r`, `agreeableness_1`,
`conscientiousness_1_r`, `neuroticism_1_r`, `openness_1_r`, `extraversion_2`,
`agreeableness_2_r`, `conscientiousness_2`, `neuroticism_2`, `openness_2`) confirm this
is the standard 10-item BFI-10 (2 items per Big-Five dimension), and the case-insensitive
match of `extraversion_1_r`/`extraversion_2` to the ground truth's
`EXTRAVERSION_1_r`/`EXTRAVERSION_2` confirms item identity and order directly from the
primary data source — this is not an inference from the paper text alone.

The paper itself (Psychological Assessment, published Nov 2025) is paywalled; no PMC or
author-repository open-access full text was found (checked PubMed, the corresponding
author's personal site, which hosts only the DSS German-version PDF, and general web
search). The abstract (via PubMed) mentions convergent/discriminant validity against
"personality facets" without naming BFI-10 explicitly, so the Methods section's exact
phrasing for which BFI-10 version/translation was administered could not be confirmed
directly from the paper. The BFI-10 item text and response-scale anchors used in this
output are instead drawn from the instrument's own original source: Rammstedt, B., &
John, O. P. (2007), "Measuring personality in one minute or less: A 10-item short version
of the Big Five Inventory in English and German," *Journal of Research in Personality*,
41, 203-212 (open PDF cached at
`.cache/heekerens2025_bfi_extraversion/bfi10_rammstedt.pdf` /
`bfi10_rammstedt.txt`), Appendix A, "German version."

## Source type used
Primary data source (Zenodo xlsx column headers) for item identity/order/reverse-coding;
secondary/standard-instrument source (Rammstedt & John, 2007 original BFI-10 publication)
for literal item wording and response-scale anchors, since the Heekerens et al. paper
itself was inaccessible (paywalled, no OA copy located) and did not reproduce the item
text or response labels in any available cached/abstract material.

## OCR / image-based extraction
The Rammstedt & John (2007) PDF's Appendix A German BFI-10 table was extracted with
`pdftotext -layout` (not a live web page). The extracted text has ligature-decoding
artifacts typical of PDF text layers (e.g. "triVt" for "trifft", "W" substituting for the
"ffi"/"fi" ligature glyph, "ƒ" as a bullet/ellipsis placeholder for the repeated stem
"Ich..."). These were corrected by hand against the well-known/standard form of the scale
(e.g. "triVt" -> "trifft") before use; no wording was invented, only ligature glyphs were
normalized. The five response-scale anchors were reconstructed from a 3-line,
column-wrapped table header in the extracted text
("triVt/triVt/weder eher/triVt", "überhaupt/eher/noch zutreVend/voll und",
"nicht zu/nicht zu//ganz zu") by reading down each column: "trifft überhaupt nicht zu",
"trifft eher nicht zu", "weder noch", "eher zutreffend", "trifft voll und ganz zu".

## Derived vs. directly-read values
- `item` values: directly read from the Zenodo `dss_2.xlsx` column headers (case-adjusted
  to match ground truth's uppercase convention, no other change).
- `item_text`: directly read (post-ligature-cleanup) from Rammstedt & John (2007)
  Appendix A, German version, items 1 ("...bin eher zurückhaltend, reserviert.") and 6
  ("...gehe aus mir heraus, bin gesellig."), each prefixed with the instrument's stem
  "Ich" per the source table's "Ich..." header.
- Which item is reverse-scored: directly read from the same appendix's scoring key line
  ("Extraversion: 1R, 6 ... R = item is reversed-scored") — item 1 reverse, item 6
  (mapped to `EXTRAVERSION_2`) not reversed. This matches the ground truth's `_r` suffix
  on `EXTRAVERSION_1_r` only, which is a strong independent confirmation.
- `instructions`: directly read (German version instruction line, "Inwieweit treffen die
  folgenden Aussagen auf Sie zu?").
- `option_text`/`resp` mapping: directly read column order from the source table (1 =
  leftmost anchor ... 5 = rightmost anchor); not derived/inferred, since the BFI-10's
  1-5 coding is unambiguous and ascending in the source table itself.
- No value in this table was derived by calculation or inference beyond the ligature
  cleanup described above.

## has_bare_integer_items
FALSE, as given in the dictionary row — the ground-truth `item` values are already
semantic/named codes (`EXTRAVERSION_1_r`, `EXTRAVERSION_2`), not bare integers, so no
position/order reconstruction was needed to map items.

## Structure of output
Single section (`heekerens2025_bfi_extraversion_1`, blank `section_prompt` — no
testlet/passage grouping applies; the instrument-level instruction line covers the whole
2-item subscale, so it lives in `instructions`, not `section_prompt`). `instrument` is
labeled "Big Five Inventory-10 (BFI-10), German version (Rammstedt & John, 2007) --
Extraversion subscale" to reflect that this table carries only the extraversion pair out
of the full 10-item BFI-10 administered in the study. `correct_response` left blank for
both items (personality-trait Likert items have no scoring key).

## Ambiguities / discrepancies
- The Heekerens et al. (2025) paper's own Methods text could not be directly read (no
  open-access full text found), so it is inferred rather than confirmed verbatim from the
  paper itself that the standard, unmodified Rammstedt & John (2007) German BFI-10
  item/response wording was used as administered. This inference rests on: (a) the
  Zenodo dataset's own description explicitly naming "BFI-10" as one of the measures,
  (b) the data column names and reverse-coding suffix matching the standard instrument's
  known item/scoring structure exactly (item 1 reverse, item 6/here `_2` not reverse),
  and (c) the BFI-10 being administered in its standard, unmodified German form is the
  overwhelmingly common practice in German-language psychology studies citing this
  instrument. No sign of a modified/adapted item wording was found anywhere in the
  available sources. Flagging this per Step 6b as a should-paste note rather than a full
  validation failure, since the item/resp sets validate exactly.
- No supplementary/appendix file with a study-specific codebook was found in the Zenodo
  record itself (only the raw response `dss_2.xlsx`); nothing to cache beyond that file.

## Items not extracted
None — both ground-truth items (`EXTRAVERSION_1_r`, `EXTRAVERSION_2`) and all 5 resp
values (1-5) were extracted and validated as an exact match against
`readRDS(".gt_heekerens2025_bfi_extraversion.rds")`.

## Validation result
EXACT match: `unique(item)` and `unique(resp)` in the candidate table are identical to
the cached ground truth. See pending_index_notes.csv for the logged discrepancy note
about item-wording provenance (BFI-10 item text sourced from the original Rammstedt &
John 2007 publication rather than a directly-read excerpt of the Heekerens et al. paper
itself, which was inaccessible).
