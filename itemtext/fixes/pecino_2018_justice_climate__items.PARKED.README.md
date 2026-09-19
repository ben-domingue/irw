# pecino_2018_justice_climate — PARKED, not shipped (batch_129, 2026-09-10)

`pecino_2018_justice_climate__items.PARKED.csv` holds the 36 option rows
(6 items x 6 response levels) that ARE recoverable for this table, plus the
subscale each item belongs to. **It is not an extraction and must not be
uploaded as one**: every `item_text` is blank because the item wording is not
published anywhere reachable, and this instrument *does* have stems, so the
blank-`item_text` shape would misrepresent it as stemless (SKILL Step 4).

Under the irw#1770 rule ("do not ship `option_text` alone when the row carries
no referent") the table is BLOCKED. This file exists so a later pass that
locates the FOCUS-93 item list starts from the verified half rather than from
scratch.

## What is verified in this file

- `resp` -> `option_text`: the source SPSS deposit
  (PLOS ONE 10.1371/journal.pone.0207458.s001, sha256
  7408cb35f09f4e3316b32e76159d87edf6d7c2dbf7310f8ff7375d2365b208fb) attaches the
  value labels `1 No one / 2 Few / 3 Someone / 4 Quite / 5 Considerable /
  6 Everyone` to exactly the six columns `cl1ap cl2ap cl3in cl4ap cl5in cl6me`
  and to no others (the other 34 `cl` columns carry `Never..Always`). All 36
  item x level cell counts in the live IRW table reproduce the .sav's cell
  counts exactly (e.g. cl1ap 4/11/54/79/116/178), so the stored integers are the
  label codes in the labelled direction, unpermuted.
- `subscale`: the .sav's own variable labels — Support, Support, Innovation,
  Support, Innovation, Goals. These are dimension names, not item text; three
  items share "Support".
- `language`: administered in Spanish (public university in Almeria, Spain).
  The anchors above are the deposit's English; no Spanish wording is in the
  deposit or the article.

## What is missing and why

The article never names, cites or describes this instrument — its Instruments
section covers only Colquitt interpersonal justice (`jus12int`..`jus15int`, 1-5),
MBI, UWES, Carlson WFB and Goodman & Svyantek extra-role performance. See
`itemtables/batch_129/notes_pecino_2018_justice_climate.csv` for the full
reasoning and the retry conditions.
