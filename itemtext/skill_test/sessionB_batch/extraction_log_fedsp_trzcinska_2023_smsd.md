# Extraction log: fedsp_trzcinska_2023_smsd

## Source used
Dictionary URL (for data) `https://osf.io/sa87b/` resolves to an OSF project with three
files: `Online Supplement.docx`, `metadata-2.docx`, and `data-3.sav` (all cached at
`.cache/fedsp_trzcinska_2023_smsd/`). The source paper (Podsiadłowski, Trzcińska, Golus,
& Wieleszczyk, 2024, *Journal of Experimental Child Psychology*, 246, 106013, DOI
10.1016/j.jecp.2024.106013) is paywalled on ScienceDirect (HTTP 403 on fetch) with no
open-access copy found (Unpaywall lookup on the DOI: `is_oa: false`, no OA location). No
author preprint, institutional-repository copy, or PMC mirror was located.

## What "SMSD" turned out to mean
Not a self-esteem measure, despite the paper's title. `metadata-2.docx` (the OSF
dataset's formal metadata record) states explicitly under its variable description
section: "p_SMSD_total - calculated score of **the objective economic deprivation among
parents**." Cross-referencing "SMSD" independently turned up "Severe Material and Social
Deprivation" — a standard EU-SILC (EU Statistics on Income and Living Conditions)
poverty indicator, defined as an enforced lack of at least 7 of 13 deprivation items (6
individual-level, 7 household-level; see Eurostat's SMSD glossary entry). The item count
(13) matches this paper's ground-truth item set (`p_SMSD_1`..`p_SMSD_13`) exactly, and
the "p_" prefix denotes parent-report, consistent with a parent-completed household
economic-deprivation instrument rather than a child self-esteem scale. The paper's two
actual self-esteem measures are separate variables not in this table
(`c_PSPCSA` = overt/explicit self-esteem, `c_PSIAT` = implicit self-esteem, both
child-level, per `metadata-2.docx`).

## Source type used
- **Directly read (literal)**: the 4-point response-scale wording. `data-3.sav`
  (downloaded from OSF: `https://osf.io/download/ruxzn/`), opened with `pyreadstat` in
  Python, carries SPSS value labels on every `p_SMSD_1`..`p_SMSD_13` column, identical
  across all 13: `1 = "definitely does not allow", 2 = "rather does not allow",
  3 = "rather allow", 4 = "definitely allow"`. This is literal text embedded in the data
  file the authors themselves distributed, not a paraphrase — used directly as
  `option_text`, keyed to `resp` 1–4.
- **Derived (not directly read)**: the `instrument` field's description ("Severe Material
  and Social Deprivation (SMSD) index...") is a descriptive label built from the
  `metadata-2.docx` variable description plus the EU-SILC SMSD concept match — not a
  literal instrument title quoted from the paper, since the paper text itself wasn't
  accessible to confirm what name/citation it uses for this instrument.
- **Not recoverable**: literal per-item stems (what each of `p_SMSD_1`..`p_SMSD_13`
  specifically asks — e.g. which EU-SILC deprivation domain, such as "afford a week's
  holiday away from home" or "keep the home adequately warm," each item number
  corresponds to) and the literal instructions/preamble sentence given to parents. Both
  would need the paper's Method/Measures section or an item-level appendix, and neither
  is in the two OSF Word documents (`Online Supplement.docx` covers only an exploratory
  moderated-mediation model with no item text; `metadata-2.docx` is a DDI-style dataset
  metadata record with variable-level, not item-level, descriptions) or in the .sav
  column labels (all `None`/unset for the `p_SMSD_*` variables — only the value labels
  were populated). Left as `NA` rather than assigning the generic EU-SILC 13-item list
  order, since this paper's specific administration order/wording was not confirmed.

## OCR / image-based extraction
None used. All source material (OSF `.docx` files converted via `pandoc`; `.sav` file
read via `pyreadstat`) was machine-readable text/structured data — no scanned images or
PDF OCR was needed or attempted.

## Derived vs. directly-read values
- Directly read: `item` and `resp` value sets (from ground-truth `irw::irw_fetch`
  equivalent, per the cached `.gt_*.rds`); `option_text` (from `data-3.sav` SPSS value
  labels, verbatim).
- Derived: `instrument` label (synthesized from OSF metadata + external SMSD/EU-SILC
  identification, not a literal paper quote); `section_id` (single trivial group
  `fedsp_trzcinska_2023_smsd_1` for all 13 items — no testlet/passage structure evident,
  so one shared section per the skill's fallback rule).
- Left blank/NA (not directly read, not derived — genuinely unrecoverable from
  accessible sources): `instructions`, `item_text`, `correct_response` (correct_response
  is also conceptually blank since this is a deprivation-report scale with no scoring
  key).

## has_bare_integer_items
FALSE, as given in the dictionary row — confirmed correct. Ground-truth items are
`p_SMSD_1`..`p_SMSD_13`, i.e. already-named/semantic-suffix codes (not bare integers
like `1`,`2`,`3`), so no positional reconstruction of which paper item maps to which
`item` code was needed; the mapping ambiguity here is instead about recovering literal
stem text per known item code (see above), not about which item code an integer refers
to.

## Structure of output
Single section (`fedsp_trzcinska_2023_smsd_1`) covering all 13 items, one shared
`instrument` description, `instructions` and `item_text` left `NA` for every row,
`correct_response` blank (no scoring key), `option_text` populated for all 4 `resp`
levels (1-4) per item from the literal `data-3.sav` value labels. 13 items x 4 resp
levels = 52 rows.

## Validation result
Exact match: `unique(item)` and `unique(resp)` in the candidate output equal the
ground-truth sets exactly (13 items `p_SMSD_1`..`p_SMSD_13`; resp `1,2,3,4` — a
numeric/integer type difference only, values identical). Logged as a **partial**
extraction in `pending_index_notes.csv` despite the exact item/resp match, because
`item_text` and `instructions` — normally expected fields — could not be recovered from
any accessible source (paywalled paper, no OA copy, OSF materials lack item-level
detail).

## Items not extracted
Item-level text (`item_text`) for all 13 items, and the overall `instructions` text —
not accessible without the paywalled paper's Method/Measures section or an
item-level appendix/instrument reproduction, neither of which was found on OSF or
elsewhere. `option_text`/`resp` mapping, by contrast, was fully and literally recovered
from the raw SPSS data file's value labels.
