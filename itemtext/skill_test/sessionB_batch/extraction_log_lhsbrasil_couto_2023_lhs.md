# Extraction log: lhsbrasil_couto_2023_lhs

## Source type used
Open-access journal article (SciELO-hosted, journal's own site) plus its linked OSF
materials, both freely accessible, no paywall route needed.

- Paper PDF: `https://periodicos.unb.br/index.php/revistaptp/article/download/38995/38304/166143`
  (Couto & Pilati, 2023, *Psicologia: Teoria e Pesquisa*, 39, e39513; DOI
  10.1590/0102.3772e39513.en) — cached at `.cache/lhsbrasil_couto_2023_lhs/paper.pdf`.
- OSF project `https://osf.io/pt45x/` (linked from the paper's Method section as "This
  study's pre-registration, data, materials, and syntax") — confirmed via its wiki that
  `https://osf.io/w6mqe/download/` (the dictionary's URL for data) *is* this project's
  raw dataset download link, i.e. `w6mqe` and `pt45x` are the same OSF project.
  `Codebook.pdf` (`https://osf.io/download/f46n5/`) fetched via the OSF v2 API
  (`api.osf.io/v2/nodes/pt45x/files/osfstorage/`, since `osf.io/w6mqe` itself renders as
  a JS shell to a plain fetch/WebFetch) — cached at
  `.cache/lhsbrasil_couto_2023_lhs/Codebook.pdf`.
- No separate raw-instrument/survey-export file exists in the OSF file listing (only
  `Codebook.pdf`, `Data Analysis.Rmd`/`.pdf`, `EFA-output.txt`, `efa.dat`, `lhs_br.rds`,
  `facebookad.png`, a "Wiki images" folder) — the Codebook is the closest thing to an
  instrument document, and it gives variable labels in **English**, not the literal
  Portuguese survey text.

## has_bare_integer_items
FALSE, as given — ground-truth `item` values are already named codes (`LHS_01`…`LHS_20`),
not bare integers, so no positional reconstruction was needed to assign items; the
codebook's variable names map onto the ground-truth `item` values directly (`LHS_01` ↔
`LHS_01`, etc.).

## OCR / image-based extraction
None. Both the paper PDF and Codebook.pdf are native-text PDFs (not scans); no OCR was
needed for item text (Table 1 of the paper) or the codebook's variable-label table.

## Derived vs. directly-read values
- **Directly read** (no derivation): `item` values (LHS_01–LHS_20, ground truth), the
  18 Portuguese item stems for items 1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20 —
  transcribed verbatim from paper Table 1's numbered list (the item numbers there are
  the original scale's item numbers, which line up 1:1 with the `LHS_NN` suffix in the
  live data's `item` field); the 4-point response scale and its two labeled endpoints
  ("Strongly disagree" / "Strongly agree") from the paper's Instruments section; the
  pre-scale instruction line from Codebook.pdf p.2 ("Please mark the option that most
  describes you or your feelings about yourself.").
- **Derived**: none of the `item`/`resp` mappings required inference — this instrument
  uses named item codes, and the paper's Table 1 items are explicitly numbered 1–20 (with
  4 and 19 named as excluded, not silently missing), so no order-based reconstruction was
  needed, unlike bare-integer-item tables.
- **Flagged substitution**: item 4 and item 19's `item_text`, and the `instructions`
  field, are recorded in **English**, not Portuguese, because no Portuguese wording for
  them was found in either source (see Discrepancies below). Both English strings are
  literal quotes from the source materials (paper Discussion section for items 4/19,
  Codebook.pdf p.2 for the instructions line) — not paraphrased or invented — but they are
  not the language actually administered to Brazilian participants, so each is suffixed
  with `[EN only -- Portuguese wording not found in source materials]` in the output so
  this is visible in the CSV/RDS itself, not just this log.

## Discrepancies / partial coverage
- **Items 4 and 19 — Portuguese wording not recovered.** These two items were part of the
  original 20-item scale administered to all 429 participants (and are present in the
  live IRW data as `LHS_04`/`LHS_19`), but the paper's Table 1 (which is the only place
  literal Portuguese item text appears) lists only the 18 items retained in the final EFA/
  CFA solution — items 4 and 19 were dropped for poor factor loadings (.01 and -.23) and
  are referenced only in the Discussion, in English quotation marks: "Item 4 ('I don't
  place myself in situations in which I cannot predict the outcome'; loading of .01) and
  19 ('I feel that my success reflects my ability, not chance'; loading of -.23)". The OSF
  Codebook.pdf gives the same two strings, still in English, as variable labels for
  `LHS_04`/`LHS_19`. No raw survey export, screenlogic, or instrument PDF with the
  Portuguese text of these two items was found among the OSF files. Recorded per the
  "flagged substitution" note above rather than left blank, since a literal (if
  English-language) quote was recoverable and seemed more useful than NA — but this is a
  judgment call; if the convention is to prefer NA over cross-language substitution, these
  two `item_text` values should be blanked.
- **Instructions line — Portuguese wording not recovered.** Same issue: Codebook.pdf
  states the instruction "read" a particular way but renders it in English since the
  codebook itself is written in English for an international audience; no Portuguese
  original was located.
- **`option_text` for scale points 2 and 3 left blank** — the paper only verbally anchors
  the endpoints (1 = Strongly disagree; 4 = Strongly agree) of the 4-point scale; no
  separate verbal labels for 2/3 were given in the paper or Codebook, consistent with a
  standard unlabeled-midpoint Likert item (same convention as `firstborn_personality`).
- **`correct_response` blank for all items** — LHS is an attitudinal/self-report scale
  with no correct-answer scoring key (only a reverse-scoring key for computing a sum
  score, which is a scoring transformation, not an `item_text`/`correct_response` fact,
  and isn't encoded in this output).

## Items not extracted
None missing structurally — all 20 ground-truth items received an `item_text` value (18
in Portuguese, 2 in English-only per above) and all 4 `resp` levels per item received
`option_text` for the two labeled endpoints. Validation against
`irw::irw_fetch("lhsbrasil_couto_2023_lhs")`-equivalent ground truth
(`.gt_lhsbrasil_couto_2023_lhs.rds`) is an **exact match**: `unique(item)` and
`unique(resp)` both match exactly (20 items LHS_01–LHS_20; resp 1–4).
