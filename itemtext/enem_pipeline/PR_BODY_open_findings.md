# ENEM item text: close the findings of the 2013–2025 review still open after #2816

After #2816, the review CSV (`enem_text_check_2013_2025.csv`, 557 findings) was re-checked
against the shipped item text: IRW v655, which is cell-for-cell identical to the batch
tables on `main`. Each finding's quote was matched contiguously (" / " = line break,
"…" = elision) against its current cell. The results:

| status at v655 | findings |
|---|---|
| fixed | 361 |
| **still present** | **172** |
| needs a reader (quote is text that is *present*) | 24 |

**14 of the 172 change what an item means.** They show that #2816's "176 of 176" was
not complete. Examples:
- 2016 MT 25723 `y = 9 − x2` (for x²);
- 2018 CN 76029 `fator de 10 5` (for 10⁵);
- 2016 CN 40112, ions with their charges on the next line;
- 2015 MT 82507 and 38852, table cells whose digits ran together.

This PR closes them all, plus every other finding that can be closed from the printed
page. The 24 manual findings turned out to be fixed already (see below).

## How

The same mechanisms as #2816:
- a defect with a shape gets a rule in the pass that owns that shape;
- a one-off gets a `58_verified_patches.py` entry, read off the page.

**Baseline.** Before any change, `42_rebuild.py` from `main` reproduced all 40
driver-built tables (2013, 2015–2022) cell for cell. The only difference is `''` vs `NA`,
which `normalize_nulls.R` then canonicalises.

### Rules

**`26_strip_page_furniture.py` (v12)**
- The area-head character class lacked `Ó`, so `LINGUAGENS, CÓDIGOS E SUAS TECNOLOGIAS`
  never matched.
- Added `Questões de 01 a 05 (opção[:] espanhol)` and `Transcreva a sua Redação para a
  Folha de Redação.`
- Added a bare page number at a field's end, removed only after a sentence end and at most
  two. Measured over all 48 tables, it matches 28 cells, all 2021.
- These are item content only. `instructions` keeps its shipped behaviour exactly: 0 cells
  change.
- **Result:**
  - 27 `page_number`, 3 `area_header` and 5 `page_furniture` findings are closed;
  - **six more LC area-head blocks on option E that the review did not list**: 2013 9614,
    2015 83482, 2016 40290, 2017 18212, 2018 85387, 2019 23564.

**`43_normalize_glyphs.py` (v5)**
- Joins the fi/fl ligature gap (`intensifi  cação`, `fl  uxo`).
- 211 occurrences in item content across 2013, 2016, 2020, 2021 and 2022. The review
  listed 31. Every joined word is a real word.
- It also fixes six words of the 2013 cover page in `instructions`.
- A single space is not joined, because that is also how words are separated. The three
  single-space cases are patches.

### Verified patches (`58_verified_patches.py` v4, 138 new entries)

Each patch has an `old` copied from the text as it stands after every other pass. The
evidence is one of:
- the booklet text layer (25 entries);
- a rendered crop of the printed page (the rest);
- the DOSVOX text for 2023;
- for tables with printed totals, the row sums (2015 MT 82507: every row adds up).

| class | entries | notes |
|---|---|---|
| `space_in_word` | 49 | + 2 found in 2016 LC 67813's poster headline; 2021 CH 88365 `ac outar` → archaic *acoutar* (ruled by Mateus) |
| `flattened` | 24 | notation and merged table cells; R17 parentheses on 2016 MT 24747 |
| `fused_words` | 15 | label dumps run together or doubled (map labels, posters) |
| `residue_option` | 12 | axis ticks and figure labels after an option's description, or after the question |
| `hyphen` | 9 | line-end syllable splits only; the 24 compound or clitic line-end hyphens are kept |
| `notation_cosmetic` | 7 | missing `^`/`_` markers |
| `shared_passage` | 5 | 2025 LC 157750/51/75/79/81: the passage stays once in `section_prompt` (R7) |
| `big_paren` | 4 | table headers rebuilt from the page (e.g. `Vazão (L/min) ΔT (°C)`) |
| ligature, single space | 3 | 2018 LC 83517, 2021 LC 85244 B, 2020 MT 111566 (new) |
| `misplaced` | 2 | 2018 CN 43554: option E carried 86222's quadro and 43554's own stimulus graph |
| `glyph` | 2 | `GARCI_A` → `GARCIA`, `CALUNGA, 0` → `CALUNGA, O` |
| `labels_dropped` | 2 | 2023 LC 140987 `TEXTO 1` / `TEXTO 2`, from the DOSVOX file |
| `figure_labels`, `order` | 2 | 2016 MT 39198 stray letter; 2020 CH 112015 TEXTO I description moved under its head |

### Two downstream guards updated

Both are needed because the rules above now run first:
- `59_strip_essay_section.py` (v3): 2021 LC 120165 `expect_removed` goes from 1815 to
  1809. The essay block carried a page number that 26 now removes, so 59 refused the cut
  and the essay material reappeared.
- `60_stimulus_descriptions.py` (v3): the 2013 CH 25217 anchor `Confl  itos` becomes
  `Conflitos`. 43 now joins the gap, so the anchor stopped matching and both of the item's
  descriptions were silently dropped.

Each was caught by a cell-level diff against the previous build, not by any gate. It is
worth keeping that diff as a habit.

## Already fixed by #2816 (verified, no change)

- **`owner_missing_description` (18).** Every owner now carries its description, every
  donor has none, and every pair is in 54's OPS.
- **`stimulus_missing`.** 42 now carry `(gerada por IA)` descriptions. The other 4 carry
  their stimulus as text (2013 LC 43715 and 49507, 2015 LC 33156 and 83482).

## Left open

- **2020 MT 49630, x-axis `5 10 15 20 25 300`.** The origin is cropped in the booklet, so
  `30`+`0` cannot be confirmed. It is tick numbers only.
- **2016 MT 24747 A.** The quote `. D^2` still occurs inside the corrected
  `(500 . 81)/(A . D^2)`. It is a false match, not an open defect.

## Checks

- `42_rebuild.py --all`: 9/9 years `rebuilt ->`. Tables are identical to an independent
  rebuild.
- Cell-level diff against `main`: 186 changed cells. **Every one is explained** by a
  patch, the ligature join or a tail cut. Item and option rows are unchanged in every
  table.
- All 138 new patches are applied (each `new` present, each `old` gone), 0 `NOT applied`.
- `normalize_nulls.R` on every batch. No table differs from `main` in formatting alone.
  2024's tables are unchanged.
- `lint_verification.R`: 48 rows, no problems. `check_provenance.R`: exit 0. Pin drift:
  none. `41_staleness.py`: STALE none.
- `validate_items.R` against the #1942-corrected response CSVs: running; PASS on every table checked so far. It cannot
  fail on this PR, because every table keeps exactly `main`'s `(item, option)` rows.
- `audit_batch.R` was **not** run (about 1 h 25 min at 96 GB). No item or response set
  changes here.

No generated text is added and no provenance changes, so no issues-page entry is owed.
