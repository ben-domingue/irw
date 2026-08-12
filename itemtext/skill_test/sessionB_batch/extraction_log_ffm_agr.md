# Extraction log: ffm_agr

## Source type used
Primary source (not OCR/PDF): the openpsychometrics.org raw-data zip
`IPIP-FFM-data-8Nov2018.zip` (http://openpsychometrics.org/_rawdata/IPIP-FFM-data-8Nov2018.zip),
cached at `.cache/ffm_agr/IPIP-FFM-data-8Nov2018/` (`data-final.csv` +
`codebook.txt`). The dictionary's "URL (for data)" field is the general
`openpsychometrics.org/_rawdata/` listing, not a specific file, so I fetched
that directory listing (via WebFetch) and identified the correct zip by
matching sample size: ground truth has 1,015,341 unique `id`; the directory
listing's "IPIP-FFM" entry states N=1,015,342 (off by one from unique-id
count, consistent with a header/footer-row rounding difference, not a
mismatch) — no other FFM/Big-Five entry on the page (`BIG5.zip`, HEXACO,
16PF) had a matching N. `codebook.txt` is plain text, directly readable, no
OCR involved.

## Cross-reference: IPIP public item pool
Cross-checked the item wording and construct assignment against the official
IPIP Big-Five Factor Markers Agreeableness scale (ipip.ori.org,
`newBigFive5broadKey.htm`, fetched via WebFetch). That page lists a 20-item
Agreeableness scale (Goldberg's original 100-item Big-Five markers); all 10
`codebook.txt` AGR items are a subset of that 20-item list, just reworded
from IPIP's third-person "Am/Have..." phrasing to first-person "I am/have..."
phrasing — the same phrasing convention already documented for the IPIP-50
survey items in `firstborn_personality`'s extraction (see
`sessionB/extraction_log_firstborn_personality.md`). This confirms `ffm_agr`
is the 10-item Agreeableness subscale of the IPIP-50 (not the 20-item/IPIP-100
version), consistent with N items = 10 in the ground truth.

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE`, and I confirmed this
directly: ground-truth `item` values are `"item_1"`..`"item_10"` — named,
non-bare-integer codes, not `"1"`..`"10"`. However the codes are still
generic (`item_N`, not `AGR1`..`AGR10`), so which paper item each `item_N`
refers to still had to be reconstructed positionally, the same reasoning the
skill requires for bare-integer items:
- `data-final.csv`'s header confirms column block order: `EXT1..EXT10,
  EST1..EST10, AGR1..AGR10, CSN1..CSN10, OPN1..OPN10` (checked directly via
  `head -1 data-final.csv`, not assumed).
- `codebook.txt`'s item list is given in that same block order (AGR block
  listed as AGR1 through AGR10 in sequence, after EXT and EST).
- I mapped `item_1`..`item_10` to `AGR1`..`AGR10` in that stated order —
  position within the Agreeableness block, not an assumption from
  response-range matching (all 50 IPIP-50 items share the same 1-5 range, so
  range alone would not have been sufficient, per the skill's warning).

## Derived vs. directly-read values
- Directly read from `codebook.txt`: `instrument` framing text, `instructions`
  (transcribed verbatim: "The following items were presented on one page and
  each was rated on a five point scale using radio buttons. The order on page
  was EXT1, AGR1, CSN1, EST1, OPN1, EXT2, etc. The scale was labeled
  1=Disagree, 3=Neutral, 5=Agree."), all 10 `item_text` values (verbatim,
  AGR1-AGR10).
- Derived: `option_text` for `resp` 2 and 4 left blank (`""`) because the
  codebook only gives verbal anchors for 1/3/5 ("Disagree"/"Neutral"/"Agree")
  — same pattern as `firstborn_personality`; did not invent labels for the
  unlabeled scale points.
- Derived: `section_id` = `ffm_agr_1` (single shared section, no real
  testlet/passage grouping in this instrument — a plain single-page Likert
  battery), per the skill's rule to still emit a section_id column even
  absent real grouping.
- `correct_response` left blank throughout: this is a personality inventory
  with no scoring key answer (reverse-keyed vs. straight-keyed direction is a
  documented IPIP property but is a scoring-time transformation, not
  something disclosed as "correct_response" in either source, consistent
  with the `firstborn_personality` precedent).

## OCR / image-based extraction
None used. Both sources (`codebook.txt` and the ipip.ori.org page) are plain
text/HTML, fetched and read directly — no PDF or image OCR was needed for
this table.

## Validation result
Exact match. `Rscript build_ffm_agr.R` confirms:
- `unique(candidate$item)` == `unique(gt$item)` (10 items, `item_1`..`item_10`)
- `unique(candidate$resp)` == `unique(gt$resp)` (1-5)
- 50 rows total (10 items x 5 resp levels), no missing/extra items.

## Items not extracted
None — all 10 ground-truth items matched and were extracted with literal
item text from the codebook.
