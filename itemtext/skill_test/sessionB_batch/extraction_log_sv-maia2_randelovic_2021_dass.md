# Extraction log: sv-maia2_randelovic_2021_dass

## Source used
Study's own OSF Method component (osf.io/vrhdu, `maia2_materials.txt` cached at
`itemtext/.cache/sv-maia2_randelovic_2021_maia/`, reused from the sibling
`sv-maia2_randelovic_2021_maia`/`_erq`/`_hexaco60` extractions) lists the study's
instrument battery explicitly, including:

> Negative emotional states (depression, anxiety, stress): Depression Anxiety Stress
> Scales-21 (DASS-21, Lovibond & Lovibond, 1995): **to be added**

So the study's own materials page does **not** have a linked Serbian DASS-21 file — it
is explicitly marked "to be added," unlike the sibling MAIA-2/ERQ/HEXACO-60 tables,
which had live osf.io links (tpn6u, fdpc2, edm6v) that resolved to REPOPSI records.
REPOPSI's own OSF wiki/search (osf.io/5zb8p) did not surface a specific DASS-21 Serbian
record either.

**Fallback used**: the official DASS instrument home page
(https://www2.psy.unsw.edu.au/dass/Serbian/Serbian.htm — the canonical DASS/DASS-21
site maintained by the instrument's author's group, historically also mirrored under
maic.qut.edu.au), which links a Serbian DASS-21 translation PDF
(`DASS21-SER.pdf`, by Dr. Zoran Protulipac MPsych, MAPS) as one of three official
Serbian translation files (Cyrillic full DASS, Latin full DASS, Latin DASS-21). Fetched
and cached at `itemtext/.cache/sv-maia2_randelovic_2021_dass/DASS21-SER.pdf` (plaintext
extraction at `DASS21-SER.txt` in the same directory, via `pdftotext -layout`).

## Source type used
Official-translation PDF (text-based, not scanned/image) obtained directly from the
DASS instrument's own maintainer site, not from the study's own OSF materials and not
from a REPOPSI record. This is a general/well-corroborated Serbian DASS-21 translation
rather than a document confirmed to be the literal file this specific study
administered — flagged per the task instructions. Item count (21), item order/numbering,
and response scale (0-3, 4 options) match the live IRW ground-truth data exactly, which
is strong indirect corroboration (DASS-21 is presented and scored identically across
translations by convention), but the exact wording used by Ranđelović et al. 2023 could
not be independently confirmed against their own materials.

## OCR / image-based extraction
None needed. `DASS21-SER.pdf` is a native text PDF (not a scanned image); `pdftotext
-layout` extracted clean, directly machine-readable Serbian text for the instructions,
all 21 items, and the 4-point response-scale labels. No OCR was used and no text was
manually re-typed from an image.

## Derived vs. directly-read values
- `item_text` (all 21 items), `instructions`, and `option_text` (all 4 response
  categories: "Ni malo" / "Pomalo ili ponekad" / "U priličnoj meri ili često" /
  "Uglavnom ili skoro uvek") are directly read, verbatim, from `DASS21-SER.pdf`.
- `item` values (`DASS_1`..`DASS_21`) are taken directly from ground truth
  (`.gt_sv_maia2_randelovic_2021_dass.rds`); the mapping from `DASS_N` to the PDF's item
  `N` is a direct 1:1 positional match on the instrument's own printed numbering (not
  reconstructed/inferred — the PDF is pre-numbered 1-21 in the same standard order the
  DASS-21 is always administered in), so no bare-integer reconstruction judgment call
  was needed here.
- `section_id` (`sv-maia2_randelovic_2021_dass_1`..`_21`, one per item) is derived per
  SKILL.md's rule for non-testlet instruments: DASS-21 presents its three subscales
  (Depression/Anxiety/Stress) interleaved item-by-item, not in blocks (confirmed from
  the PDF's own item order and the printed subscale-code column: S,A,D,A,D,S,A,S,A,D,
  S,S,D,S,A,D,D,S,A,A,D for items 1-21), so there is no shared passage/testlet grouping
  — one trivial section_id per item, blank `section_prompt`, matching the sibling
  `mhscdc_fried_2020_dass` (English DASS-21) table's own precedent in this batch
  (`build_mhscdc_fried_2020_dass.R`).
- `resp` values 0-3 are directly read from the PDF's printed scale and match ground
  truth's 0-3 exactly (note: this differs from the English `mhscdc_fried_2020_dass`
  sibling table, which is coded 1-4 in that dataset's live data — DASS-21's *standard*
  published scoring is 0-3, so the Serbian table here is on the instrument's canonical
  coding while the English sibling table happens to be re-coded 1-4 in that dataset).
- `correct_response` left blank (no scoring key / correct answer for a
  self-report emotional-state inventory).

## has_bare_integer_items
`FALSE`, as stated in the dictionary row — ground-truth `item` values are semantic codes
(`DASS_1`..`DASS_21`), not bare integers, so no position-based reconstruction judgment
call was required for the item mapping itself (see above).

## Ambiguities / discrepancies
- The Serbian text is confirmed to be a real, official, published DASS-21 translation,
  but not confirmed as the literal file this specific study (Ranđelović, Jokic, & Purić,
  2023) administered, since their own OSF materials list marks this instrument
  "to be added" rather than linking a file. Logged to `pending_index_notes.csv`.

## Items not extracted
None — all 21 ground-truth items and all 4 ground-truth resp values were matched
exactly (`identical(sort(unique(item)), gt_items)` == TRUE,
`identical(sort(unique(resp)), gt_resp)` == TRUE). See `build_sv-maia2_randelovic_2021_dass.R`.
