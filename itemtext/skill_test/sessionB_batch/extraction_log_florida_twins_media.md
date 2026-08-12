# Extraction log: florida_twins_media

## Source used
Dictionary URL (`https://ldbase.org/datasets/3f7033dd-47a5-4ef8-aeab-08a559dce0d1`) is
the **Wave 1** Child Survey Measures dataset page on LDbase. Ground truth's own `wave`
column is `3` for every row of `florida_twins_media`, and `item` values (`media1t`-
`media11t`) match the `media[#]t` variable-naming convention used in the **Wave 3**
Child Codebook — same situation already resolved for sibling tables `florida_twins_dbi`
and `florida_twins_hwk` in this batch. Reused the already-cached Wave 3 codebook rather
than re-fetching:

- Cached file: `.cache/florida_twins_dbi/W3_Child_Codebook_LDBase.docx` (downloaded for
  `florida_twins_dbi`; not re-downloaded here)
- Cached plain-text dump: `.cache/florida_twins_dbi/codebook_text.txt`
- Confirmed this codebook covers the media items via `grep -i media` on the cached text,
  and re-parsed `word/document.xml` directly (see below) to confirm structure
  unambiguously.
- Also checked `.cache/florida_twins_class/` (the Wave 1 codebook cache from
  `florida_twins_class`) — not used, since the ground truth's `wave` column points to
  Wave 3, not Wave 1.

No new file was fetched for this table; the existing `florida_twins_dbi` cache was
reused, per the task instructions. A small scratch dir
`.cache/florida_twins_media/` was created but left empty (no new source material to
store there).

## Source type used
Instrument codebook (.docx), scraped from the LDbase Wave 3 Child Survey Measures
dataset repository page — not the published paper itself. Native Word document; no
PDF/OCR involved.

## OCR / image-based extraction
None. The codebook is a native .docx (Word 2007+, valid zip/XML container). Rather than
relying solely on the flattened `codebook_text.txt` (whose plain-text rendering of
tables can be ambiguous for adjacent numeric cells, as already noted for the `hwk`
table in this batch), I re-parsed `word/document.xml` directly with Python
(`zipfile` + regex) two ways:

1. Located the `[media1t]`...`[media5t]` block directly in the XML run text (each
   `w:t` run), confirming each item's literal wording and its inline `(1) Yes ; (0) No`
   scoring key.
2. Located the `media[#]t` response table (a genuine Word table, `<w:tbl>`) covering
   items 6-11, and parsed it row-by-row via `<w:tr>`/`<w:tc>` cell extraction:

   ```
   ['media[#]t', 'I don't know (DK)', 'Nothing', 'Only a little', 'Some', 'A lot']
   ['6 What you do and see online', 'DK-98', '0', '1', '2', '3']
   ['7 The types of video or computer games you play', 'DK-98', '0', '1', '2', '3']
   ['8 Which TV shows you watch', 'DK-98', '0', '1', '2', '3']
   ['9 The songs you listen to', 'DK-98', '0', '1', '2', '3']
   ['10 What you do on social media (such as Facebook, Twitter, or Instagram)', 'DK-98', '0', '1', '2', '3']
   ['11 Which apps you use', 'DK-98', '0', '1', '2', '3']
   ```

   This row-by-row structural parse (not the flattened text) is what confirmed
   unambiguous item-to-number alignment for items 6-11. No scanned pages, images, or
   OCR were involved anywhere in this extraction.

## Structure discovered
Two distinct sub-blocks under the "Homework and Free Time" section of the Wave 3 Child
Codebook, both about parental monitoring of media use — no single named instrument
title covers both (no "PANAS"/"DBI"-style label given in the codebook), so `instrument`
records the section name plus a descriptive suffix, and each stem sentence is recorded
as a `section_prompt` scoped to its own `section_id` (not `instructions`, since neither
stem applies to the other sub-block's items):

- **`florida_twins_media_talked`** (`media1t`-`media5t`): stem "Have your parents ever
  talked to you about any of the following (Please circle Yes or No):" — 5 Yes/No
  items, scored `(1) Yes ; (0) No` per the inline key.
  1. media1t: "When you can use media (such as only on weekends, only after homework or
     chores)"
  2. media2t: "How long you can use media for (such as no more than an hour a day)"
  3. media3t: "What types of media you can use (such as no watching certain types of
     shows or playing certain games)"
  4. media4t: "Staying safe online (such as not giving out personal information)"
  5. media5t: "Being responsible, respectful, and kind online (such as not bullying or
     copying other people's work)"

- **`florida_twins_media_know`** (`media6t`-`media11t`): stem "How much do your parents
  know about..." — 6 items on a 5-point scale in the source (I don't know (DK) = -98,
  Nothing = 0, Only a little = 1, Some = 2, A lot = 3).
  6. media6t: "What you do and see online"
  7. media7t: "The types of video or computer games you play"
  8. media8t: "Which TV shows you watch"
  9. media9t: "The songs you listen to"
  10. media10t: "What you do on social media (such as Facebook, Twitter, or Instagram)"
  11. media11t: "Which apps you use"

## Derived vs. directly-read values
`item_text`, `section_prompt` (both stems), and `option_text` (No/Yes; Nothing/Only a
little/Some/A lot) are all literal transcriptions from the codebook. `item` values are
already the semantic `media[#]t` codes used verbatim in the source (`has_bare_integer_items`
is FALSE, confirmed — no order-reconstruction step was needed).

**One value intentionally dropped, not derived:** the source's "I don't know (DK)"
option (coded `-98`) for items 6-11 was **not** included as an `option_text`/`resp` row.
Ground truth `resp` for this table is exactly `{0, 1, 2, 3}` — `-98` never appears in the
live IRW data, meaning DK responses were filtered/recoded to missing upstream in
processing. Adding a `resp = -98` row would introduce a value outside the ground-truth
`resp` set and fail Step 5 validation, so it was omitted rather than forced in.
`table_level instructions` was left blank (empty string) rather than duplicating either
section's stem sentence at the table level, per the instructions/section_prompt
boundary rule — neither stem is common to both sections' items.

## has_bare_integer_items
FALSE, as given in the dictionary row — `item` values are semantic codes
(`media1t`..`media11t`), not bare integers. The item-to-text mapping was justified
directly by the codebook's own inline `[media1t]`...`[media5t]` variable tags (block 1)
and the `media[#]t` table's own row numbering 6-11 (block 2), not by positional
inference from bare integers.

## Validation
`unique(item)` and `unique(resp)` in `candidate_florida_twins_media.rds` match
`unique(item)`/`unique(resp)` in `.gt_florida_twins_media.rds` exactly:
- 11 items, `media1t`..`media11t` (verified via `identical(sort(unique(...)), sort(unique(...)))` == TRUE)
- resp `{0, 1, 2, 3}` (verified == TRUE)

No items skipped. One discrepancy logged for the record (not a validation failure): the
source's DK/-98 response option for items 6-11 has no corresponding value in the live
IRW `resp` data, so it was omitted from `option_text`/`resp` rather than forced in — see
`pending_index_notes.csv`.
