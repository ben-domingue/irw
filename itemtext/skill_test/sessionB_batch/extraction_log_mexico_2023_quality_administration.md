# Extraction log: mexico_2023_quality_administration

## Source used
Same INEGI source as the sibling tables `mexico_2023_quality_problems` and
`mexico_2023_quality_corruptionperception` (all drawn from the ENCIG 2023 "Cuestionario
general" and its companion data dictionary). Reused the already-cached PDFs at
`.cache/mexico_2023_quality_problems/` rather than re-fetching:
- `encig23_cuestionario.pdf` (paper questionnaire instrument), text-extracted to
  `cuestionario.txt`
- `encig23_estructura_base_datos.pdf` (data dictionary describing every output
  variable), text-extracted to `estructura.txt`

Both were read as plain PDF-extracted text (not images/OCR).

## Structure discovered
Question **A.1**, at the very start of the questionnaire's **SECCIÓN A. CONFIANZA EN LA
ADMINISTRACIÓN PÚBLICA** ("Section A. Confidence in Public Administration") —
`cuestionario.txt` lines 280-300:

> "A.1 En una escala de cero a diez, como en la escuela, donde cero es nada y diez es
> completamente, en general ¿cuánto confía en…" ("On a scale of zero to ten, like in
> school, where zero is nothing and ten is completely, in general how much do you trust
> in...")

administered with "REGISTRA EL CÓDIGO CORRESPONDIENTE A CADA OPCIÓN" ("Register the
code for each option"), followed by 7 sub-items, each a target of trust rather than a
government administrative procedure/service as the pre-task hypothesis had guessed:

1. la mayoría de las personas? ("most people?")
2. la mayoría de las personas que conoce personalmente? ("most people you know
   personally?")
3. los(las) servidores(as) públicos(as) o empleados(as) del gobierno? ("public
   servants/government employees?")
4. el gobierno de su municipio o alcaldía? ("the government of your municipality?")
5. el gobierno federal? ("the federal government?")
6. la cámara de diputados y la cámara de senadores? ("the chamber of deputies and the
   senate?")
7. la policía? ("the police?")

The response card shown once for all 7 sub-items is a 0-10 "school grade"-style scale
with only the two endpoints labeled: `00 Nada` ("Nothing") ... `10 Completamente`
("Completely"), plus a `99 No sabe/no responde` ("Don't know / no answer") catch-all
code.

`estructura.txt` (the data dictionary, lines 504-610) cross-confirms the output
variables `A1_1`..`A1_7` (Numérico, valid codes `00`-`10` plus `99`), in the same order
and with the same item wording as the questionnaire — lower-cased directly to the IRW
`item` codes `a1_1`..`a1_7`. No item-to-position reconstruction was needed
(`has_bare_integer_items` is FALSE, confirmed).

## Structure of output
Single section (`mexico_2023_quality_administration_a1`) — all 7 items are sub-items of
one question sharing the same stem/scale, matching the format used for the `p3_3`
section of the sibling `mexico_2023_quality_corruptionperception` table.

- `instrument` = "INEGI Encuesta Nacional de Calidad e Impacto Gubernamental (ENCIG)
  2023 -- Cuestionario General, Sección A. Confianza en la Administración Pública,
  pregunta A.1"
- `instructions` = "REGISTRA EL CÓDIGO CORRESPONDIENTE A CADA OPCIÓN" (the
  administration instruction, table-wide since there is only one section/question in
  this table) — same placement convention as the sibling `mexico_2023_quality_problems`
  table (single-section table -> admin instruction in `instructions`, question stem in
  `section_prompt`).
- `section_prompt` = the literal A.1 stem, "A.1 En una escala de cero a diez, como en la
  escuela, donde cero es nada y diez es completamente, en general ¿cuánto confía en…"
- `item_text` = the literal 7 sub-item phrases transcribed above (numbering prefix
  stripped, matching the sibling table's `p3_3` convention of dropping the leading
  enumeration digit and keeping the phrase itself).
- `option_text`: only the two labeled endpoints of the 0-10 scale carry literal text —
  `resp = 0` -> "Nada", `resp = 10` -> "Completamente". `resp` 1-9 have no printed label
  in the source (the card shows only the two end-anchors with the intervening numbers
  unlabeled), so `option_text` is left blank for those rows rather than inventing
  descriptive labels — this matches the source's own terseness (an anchored 0-10 scale,
  not an 11-point fully-labeled Likert scale).
- The 5th/catch-all card option `99 No sabe/no responde` was **not emitted** — the live
  ground-truth `resp` set is exactly `{0,1,...,10}` with no `99`, consistent with the
  same NA-recoding pattern already observed and logged in the two sibling tables (99
  presumably recoded to `NA` rather than kept as a resp level).
- `correct_response` left blank — a trust/perception item, no scoring key.

## Ambiguities
None requiring a `pending_index_notes.csv` entry. Item set (`a1_1`..`a1_7`) and `resp`
set (`0`-`10`) both matched the cached ground truth exactly on the first pass — no
partial coverage, no undocumented missingness pattern of the kind seen in
`mexico_2023_quality_problems`.

One point worth flagging for anyone reading the table name later: despite the table
name `mexico_2023_quality_administration` and the pre-task hypothesis (0-10
satisfaction rating of specific government procedures/services), the actual source
question is a **general confidence/trust battery** ("¿cuánto confía en…", how much do
you trust in...), not a satisfaction-with-procedures item. The 0-10 "school grade"
response format is genuinely the same INEGI convention as satisfaction items elsewhere
in ENCIG, which likely drove the naming guess, but the substantive content here is
trust in institutions/people (public administration writ large, most people, personal
acquaintances, municipal/federal government, congress, police), matching the section
title "CONFIANZA EN LA ADMINISTRACIÓN PÚBLICA" (Confidence in Public Administration).
Not logged as a discrepancy since it doesn't affect item/resp validation, but noted here
since it corrects the task's working hypothesis about item content.

## Items not extracted
None — all 7 ground-truth items (`a1_1`..`a1_7`) and all 11 `resp` values (`0`-`10`)
matched and were extracted.

## OCR / image-based extraction
None. Both source PDFs (`encig23_cuestionario.pdf`, `encig23_estructura_base_datos.pdf`)
are text-layer PDFs with an extractable text layer — read via ordinary PDF text
extraction (`cuestionario.txt` / `estructura.txt`, reused from the sibling table's
cache), not images or scanned pages, so no OCR was involved.

## Derived vs. directly-read values
- `item_text` (the 7 trust-target labels) is directly read/transcribed verbatim from
  the numbered list in `cuestionario.txt` (numbering prefix stripped, per sibling-table
  convention).
- `section_prompt` (the A.1 stem) and `instructions` (the "REGISTRA..." administration
  instruction) are directly read/transcribed verbatim from `cuestionario.txt`.
- `item` codes (`a1_1`..`a1_7`) are directly read from the data-dictionary variable
  names (`estructura.txt`), lower-cased to IRW convention, not invented.
- `option_text` for `resp` 0 ("Nada") and `resp` 10 ("Completamente") is directly read
  from the response card. `option_text` for `resp` 1-9 is deliberately left blank — a
  directly-read absence (the source genuinely provides no label for these intermediate
  codes), not a derived/invented gloss.
- The exclusion of code 99 ("No sabe/no responde") is a **derived** decision (drop code
  99), consistent with its absence from the live `resp` value set, not a literal-text
  issue.
- `resp` coding (0-10) is directly read from `estructura.txt`'s declaration of each
  `A1_*` field's valid codes, cross-checked against the questionnaire's card layout.
- `correct_response` is blank by design (not applicable), not omitted due to missing
  source information.

## Source type used
**Official primary-source materials**: the same INEGI paper questionnaire instrument
(`encig23_cuestionario.pdf`) and official data dictionary
(`encig23_estructura_base_datos.pdf`) used for the sibling tables, both downloaded
directly from INEGI's public ENCIG 2023 microdata page. Strongest available source tier
(literal instrument text plus an authoritative variable-level codebook).

## has_bare_integer_items
FALSE, as stated in the dictionary row — items already carry semantic codes
(`a1_1`..`a1_7`) that map directly and unambiguously to the 7 named trust-target
variables documented in INEGI's data dictionary and to the numbered list in the
questionnaire, so no item-to-position reconstruction was needed.

## Validation result
Exact match. `unique(item)` and `unique(resp)` in the candidate exactly match the
cached ground truth (`.gt_mexico_2023_quality_administration.rds`): 7 items
(`a1_1`-`a1_7`), 11 resp values (`0`-`10`).
