# Extraction log: florida_twins_hwk

## Source used
Dictionary URL (`https://ldbase.org/datasets/3f7033dd-47a5-4ef8-aeab-08a559dce0d1`) is
the Wave 1 Child Survey Measures dataset page on LDbase. Ground truth `item` values
(`hwk1t`-`hwk4t`) and `wave == 3` in the data point to the **Wave 3** Child Survey
Measures dataset/codebook instead — same situation already resolved for the sibling
table `florida_twins_dbi` in this same batch. Reused the already-cached codebook rather
than re-fetching:

- Cached file: `.cache/florida_twins_dbi/W3_Child_Codebook_LDBase.docx` (downloaded for
  `florida_twins_dbi`; not re-downloaded here)
- Cached plain-text dump: `.cache/florida_twins_dbi/codebook_text.txt`
- This codebook does cover HWK items — confirmed via `grep -i hwk` on the cached text
  and by parsing the underlying `word/document.xml` table structure directly for the
  `hwk[#]t` block (see below).

No new file was fetched for this table; the existing cache from `florida_twins_dbi` was
reused per the task instructions.

## Source type used
Instrument codebook (.docx), scraped from the LDbase Wave 3 Child Survey Measures
dataset repository page — not the published paper itself. Native Word document; no
PDF/OCR involved.

## OCR / image-based extraction
None. The codebook is a native .docx (Word 2007+, valid zip/XML container). For this
table, rather than relying on the flattened `codebook_text.txt` (whose plain-text
Word-table extraction is order-ambiguous for adjacent numeric table cells — visible in
other sections of that file, e.g. the `nes`/`friends` blocks show scrambled digit
sequences), I re-parsed `word/document.xml` directly with Python (`zipfile` +
`re.sub("<[^>]+>","|",...)` per table row) to read the `hwk[#]t` table row-by-row and
confirm each cell's content unambiguously. No scanned pages or images were involved.

## Structure discovered
Item block (codebook p. 3, "Homework and Free Time" section, item 9): "During the
2016/17 school year, when you did homework how often did you…" followed by a table
`hwk[#]t` with column headers **Never / Hardly Ever / Sometimes / Often**, scored
**0 / 1 / 2 / 3** in the codebook, and 4 numbered rows:

1. Have the TV on at the same time?
2. Do social networking at the same time (Facebook, Twitter, Instagram etc.)?
3. Listen to music at the same time?
4. Text or use instant messaging (IM) at the same time?

Row-by-row XML parse of the table (`<w:tr>` blocks) confirmed each item text is
immediately followed by the literal digit sequence `0123` in its own table row — no
ambiguity in item order or the codebook's raw 0-3 scoring, unlike the scrambled digit
sequences seen elsewhere in this same file.

## Derived vs. directly-read values
`item_text`, `instructions`, and `option_text` (Never/Hardly Ever/Sometimes/Often) are
all literal transcriptions from the codebook.

**One derived value: `resp`.** The codebook's own scoring key for `hwk[#]t` is 0-3
(Never=0 ... Often=3), but the ground-truth `resp` values in the live IRW data are 1-4.
Checked the processing script `data/florida_twins.R` (line 257):
```r
mutate(across(contains('hwk'), ~ . + 1), ...)
```
This confirms the IRW processing pipeline adds 1 to all raw `hwk*` values before
upload — i.e. codebook 0/1/2/3 -> stored `resp` 1/2/3/4. `option_text` was mapped onto
the *stored* `resp` values (1=Never, 2=Hardly Ever, 3=Sometimes, 4=Often), not the raw
codebook numbers, to stay consistent with what's actually in `irw::irw_fetch()`. This
is a directly-verified transformation (read from the processing script, not guessed).

## has_bare_integer_items
FALSE, as given in the dictionary row — `item` values are semantic codes
(`hwk1t`..`hwk4t`), not bare integers. The codebook's own item numbering (1-4 within
the `hwk[#]t` block) maps directly and unambiguously onto `hwk1t`..`hwk4t` by position;
no order-reconstruction-from-integer-codes step was needed.

## Structure of output
Single section (`florida_twins_hwk_1`, blank `section_prompt` — no testlet/passage
grouping), one `instrument`/`instructions` pair applying to all 4 items,
`correct_response` blank throughout (frequency-of-behavior item, no scoring key). 16
rows total (4 items x 4 resp levels each).

## Validation
`unique(item)` and `unique(resp)` in `candidate_florida_twins_hwk.rds` match
`unique(item)`/`unique(resp)` in `.gt_florida_twins_hwk.rds` exactly: 4 items
(`hwk1t`..`hwk4t`), resp {1,2,3,4}. No items skipped, no discrepancies to log in
`pending_index_notes.csv`.
