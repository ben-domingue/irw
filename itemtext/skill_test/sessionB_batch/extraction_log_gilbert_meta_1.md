# Extraction log: gilbert_meta_1

## has_bare_integer_items: FALSE (confirmed)

The dictionary row's `has_bare_integer_items: FALSE` is correct — ground-truth `item`
values are already semantic strings (`s_read_11_0` ... `s_read_7_10`), not bare integers
requiring positional reconstruction. No item-to-integer mapping problem exists here; the
problem instead is that the source paper never discloses literal item wording at all
(see below).

## Source type used

- **Working paper (open-access), no appendix with item content.** Fetched
  `https://edworkingpapers.com/sites/default/files/ai22-619.pdf` (Gilbert, Kim, &
  Miratrix, 2022, EdWorkingPaper No. 22-619 — the pre-publication version of the JEBS
  2023 article named in the dictionary row). Cached at
  `itemtext/.cache/gilbert_meta_1/ai22-619.pdf`. Read in full (all 33 pages, pages 1-10,
  11-20, 21-33).
- Confirmed this is the correct paper/dataset by matching sample sizes exactly: paper
  states "110 schools randomly assigned to treatment and control ... (N = 7797
  students)"; ground truth has `length(unique(cluster_id))==110` and
  `length(unique(id))==7797`. This is not a guess — it's an exact numeric match on two
  independent statistics.
- The paper explicitly states "The full assessment is available in the Online
  Supplemental Materials" (p.5) — referring to the *published* SAGE/JEBS article's
  supplemental materials, not the working-paper PDF. I attempted to reach the published
  article (`journals.sagepub.com/doi/10.3102/10769986231171710`) via WebFetch; the page
  rendered without a visible supplemental-materials download link (likely JS-rendered or
  paywalled — SAGE supplemental files typically require institutional/journal access I
  could not exercise from this environment). I also checked the Harvard DASH repository
  handle and the EdWorkingPapers landing page for an attached appendix; neither exposed
  one. **I did not fabricate item content to fill this gap.**
- Also checked `data/gilbert_hte/postprocessing.R` in this repo, which is the actual
  processing script that produced this IRW table. It reads from
  `"06 IL-HTE Econ/analysis/data/clean/il_hte_data.Rdata"` (a private Dropbox path, not
  in this repo) and passes `x$item` straight through unrenamed — i.e., the
  `s_read_3/7/11_<n>` item codes come directly from the authors' original raw data, not
  from any processing-script invention. No item-text codebook accompanies that script.
- Checked `manuscript_src/03_il-hte.R` (used for the IRW paper itself), which confirms
  `gilbert_meta_1` is one of several RCT tables reanalyzed there, consistent with it
  being real trial data, not a synthetic methods-demo item set.

## OCR / image-based extraction

Not applicable — the PDF is native/selectable text (extracted cleanly via the Read tool
with no visible garbling), not a scanned image. No OCR was performed or needed.

## Derived vs. directly-read values

- **Directly read from the paper (verbatim facts, not item text):** "researcher-designed
  reading comprehension assessment containing 30 multiple-choice items based on three
  reading passages designed to measure different degrees of transfer from the MORE
  intervention curriculum (i.e., Near, Mid, and Far Transfer passages...)" (p.12); dosed
  the `instrument` field with a paraphrase of this description — this is a structural
  description, not a claim about literal item wording, so it does not violate the
  "don't fabricate item text" rule.
- **Not derived / left blank:** `instructions`, `section_prompt`, `item_text`,
  `correct_response`, `option_text` are all `NA`. No literal instructions, passage text,
  item stems, answer choices, or scoring key were available in any source I could reach.
  I did not attempt to infer or paraphrase plausible reading-comprehension item wording
  — per the explicit instruction from the `gilbert_meta_38` correction, absence of
  source text means blank output, not invented output.
- **`section_id` is a structural inference, clearly flagged as such:** ground-truth
  `item` values have the form `s_read_<3|7|11>_<n>`. The paper describes exactly three
  passages (Near/Mid/Far), and the numeric prefixes 3/7/11 partition the 30 items into
  three groups of 10 — consistent with one prefix per passage. I used `section_id =
  gilbert_meta_1_3` / `_7` / `_11` (neutral labels tied to the raw numeric prefix) rather
  than guessing which prefix is "Near" vs. "Mid" vs. "Far", since nothing in the
  reachable sources ties the numeric codes 3/7/11 to the Near/Mid/Far labels the paper
  uses in its own figures (Figure 3 labels items "Near-0".."Near-9",
  "Mid-0".."Mid-9", "Far-0".."Far-9" — a different, cleaner 0-9 labeling scheme than the
  raw `s_read_<prefix>_<n>` codes in the live IRW data, so the two naming schemes cannot
  be matched item-for-item without the underlying codebook/de-identification key).

## What the item-naming structure actually turned out to mean

Ground truth was inspected directly (`sort(unique(item))`) rather than assumed from the
prompt's sample. Actual structure:

- `s_read_3_0` .. `s_read_3_9` — 10 items (suffixes 0-9, clean).
- `s_read_11_0` .. `s_read_11_9` — 10 items (suffixes 0-9, clean).
- `s_read_7_0` .. `s_read_7_8`, `s_read_7_10` — 10 items, but the suffix set is
  `{0,1,2,3,4,5,6,7,8,10}`, **skipping 9 and including 10** instead of running 0-9 like
  the other two groups. This is a genuine quirk in the live data, not a
  transcription error on my part — confirmed by printing the full sorted item vector
  twice (once for all 30 items, once filtered to just the `s_read_7_` group).

Interpretation: "s_read" = student reading-assessment item (consistent with the paper's
description of a 30-item reading comprehension test). The middle number (3/7/11) almost
certainly identifies one of the three reading passages (Near/Mid/Far Transfer) — three
groups of ~10 items matches the paper's "30 multiple-choice items based on three reading
passages" exactly — but I could not confirmwhich numeric code maps to which named
passage type, since the paper's own item labels (Near-n/Mid-n/Far-n in Figure 3) use a
different, non-overlapping numbering convention than the raw `s_read_<prefix>_<n>` codes
in the live data. The trailing digit is very likely a within-passage item index (0-9,
i.e., item order within that passage's 10-item subtest); the `s_read_7` group's
"skip 9, include 10" pattern suggests either (a) an item was dropped from that passage
during scoring/QC and the original item-bank index (10) was retained rather than
renumbered, or (b) a one-off indexing/off-by-one artifact upstream of this repo's
processing script. I did not guess further since neither the reachable paper text nor
the processing script (`data/gilbert_hte/postprocessing.R`, which merely passes through
`x$item` from a private raw file) resolves it.

## Source type used (summary line)

Open-access working-paper PDF (non-final preprint of the published JEBS article) — item
wording itself not disclosed in any source I could reach; this repo's own processing
script for this table confirmed as pass-through of an unmodified upstream item-ID
scheme.

## Items not extracted

All 30 items are present in the output with the correct `item`/`resp` values (validated:
`unique(candidate$item)` and `unique(candidate$resp)` exactly match
`unique(gt$item)`/`unique(gt$resp)` from `.gt_gilbert_meta_1.rds`). No items were
dropped. However, `item_text`, `option_text`, `instructions`, `section_prompt`, and
`correct_response` are blank/NA for all 60 rows — this is a **structure-only** candidate
file (item/resp/instrument/section grouping recoverable; no literal transcribable text
recoverable). Logged to `pending_index_notes.csv`.
