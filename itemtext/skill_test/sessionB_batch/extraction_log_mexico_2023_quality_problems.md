# Extraction log: mexico_2023_quality_problems

## Source used
`tables_batch.csv`'s URL points to INEGI's (Instituto Nacional de Estadística y
Geografía, Mexico's national statistics institute) public microdata page for the
Encuesta Nacional de Calidad e Impacto Gubernamental (ENCIG) 2023,
`https://www.inegi.org.mx/programas/encig/2023/#microdatos`. Two official PDFs were
downloaded from that page and cached at `.cache/mexico_2023_quality_problems/`:
- `encig23_cuestionario.pdf` (the full paper questionnaire instrument, "Cuestionario
  general"), text-extracted to `cuestionario.txt`
- `encig23_estructura_base_datos.pdf` (the data-dictionary/"estructura de base de
  datos" describing every output variable), text-extracted to `estructura.txt`

Both were read as plain PDF-extracted text (not images/OCR).

## Structure discovered
Section III of the questionnaire ("PERCEPCIÓN DE CORRUPCIÓN"), question 3.1:
"En su opinión, ¿cuáles son los tres problemas más importantes que en (ESTADO) se
enfrentan hoy en día?" ("In your opinion, what are the three most important problems
that [STATE] faces today?"), instructed "MUESTRA LA TARJETA "A" Y CIRCULA LOS CÓDIGOS
CORRESPONDIENTES" ("Show card A and circle the corresponding codes") — a
pick-up-to-three-from-a-list item, laid out in `cuestionario.txt` lines 306-317 as a
two-column list of 12 labeled problem categories, each with a two-digit code:

```
Mal desempeño del gobierno .......01     Desastres naturales .................07
Pobreza ...........................02     Baja calidad de la educación pública 08
Corrupción .........................03     Mala atención en centros de salud y
Desempleo ..........................04     hospitales públicos .................09
Inseguridad y delincuencia .........05     Falta de coordinación entre diferentes
Mala aplicación de la ley ..........06     niveles de gobierno .................10
                                            Falta de rendición de cuentas ........11
                                            Ninguno ..............................99
```

`estructura.txt` (the data-dictionary PDF) confirms the output variables are one
binary (0/1, "Numérico") field per problem category — `P3_1_01` through `P3_1_11` plus
`P3_1_99` — i.e. INEGI has already converted the "pick up to 3" multi-select question
into 12 separate mentioned/not-mentioned indicator variables (lines 626, 630, 667, 676
of `estructura.txt` confirm this for `P3_1_01`, `P3_1_02`, `P3_1_11`, `P3_1_99`
respectively; the full run of codes 01-11 and 99 was cross-checked against the
questionnaire's item list and matches 1:1). This lower-cased directly to the IRW
`item` codes `p3_1_01`...`p3_1_11`, `p3_1_99`.

## Structure of output
Single section (`mexico_2023_quality_problems_1`) — all 12 items share the same
`instrument`, `instructions`, and `section_prompt` text (question 3.1's prompt and its
"show card A" instruction), since they are the 12 response options of one multi-select
question, not 12 independently-worded items. `item_text` is the literal problem-category
label transcribed from the "Tarjeta A" list (e.g. "Mal desempeño del gobierno",
"Pobreza", "Corrupción", ..., "Ninguno" for the catch-all/none-of-the-above code 99).
Two response rows per item (`resp` 0 and 1) with `option_text`: `1` = "Sí" (respondent
named this problem as one of their top three); `0` = "No se declaró como opción
afirmativa" (a descriptive, non-literal label supplied for the indicator's negative
level, since the source materials document the variable as binary but only give a
literal label for the affirmative/"mentioned" side — see Ambiguities).

## Ambiguities
- **Undocumented missingness pattern (logged to `pending_index_notes.csv`).** Item set
  matches exactly (12/12: `p3_1_01`..`p3_1_11`, `p3_1_99`) and the candidate's
  documented 0/1 `resp` coding matches the non-missing ground-truth `resp` values
  exactly. However, live ground-truth data (`irw::irw_fetch`, cached at
  `.gt_mexico_2023_quality_problems.rds`) has `resp = NA` for items `p3_1_01`
  through `p3_1_09` in almost exactly 51% of rows (39,930 / 78,896 respondents;
  verified per-item, uniform across all nine items), while `p3_1_10`, `p3_1_11`, and
  `p3_1_99` are never `NA` (0/78,896). Neither the questionnaire PDF nor the
  data-dictionary PDF documents a skip pattern, "no aplica"/refusal code, or any other
  reason nine of the twelve indicators would have missingness and the other three
  would not. Cause unknown — not fabricated, and not something this extraction can
  resolve from the available source material; flagged as an open discrepancy rather
  than guessed at.
- The negative/`0` level's `option_text` ("No se declaró como opción afirmativa") is a
  descriptive gloss, not a literal source string — the source documents this as a
  binary indicator variable but the questionnaire card only labels the affirmative
  ("select this code") side; there is no literal "No" wording tied to each of the 12
  binary fields individually (unlike a normal yes/no item).
- `correct_response` left blank — a perception/opinion item, no scoring key.

## Items not extracted
None — all 12 ground-truth items (`p3_1_01`..`p3_1_11`, `p3_1_99`) and both `resp`
values (0, 1) matched and were extracted; validated exact item-set match and exact
match of candidate `resp` levels against the non-missing `resp` levels in the cached
ground truth (`.gt_mexico_2023_quality_problems.rds`). See Ambiguities above for the
one open, logged discrepancy (missingness pattern, not coverage).

## OCR / image-based extraction
None. Both source PDFs (`encig23_cuestionario.pdf`, `encig23_estructura_base_datos.pdf`)
were text-layer PDFs with an extractable text layer — read via ordinary PDF
text-extraction to `cuestionario.txt` / `estructura.txt`, not images or scanned pages,
so no OCR was involved.

## Derived vs. directly-read values
- `item_text` (the 12 problem-category labels) is directly read/transcribed verbatim
  from the "Tarjeta A" list in `cuestionario.txt`.
- `section_prompt` and `instructions` are directly read/transcribed verbatim from
  question 3.1's stem and its administration instruction in `cuestionario.txt`.
- `item` codes (`p3_1_01` etc.) are directly read from the data-dictionary variable
  names in `estructura.txt` (lower-cased to match IRW convention), not invented.
- `option_text` for `resp = 1` ("Sí") is directly read (the card instructs circling
  the code for each problem named, i.e. affirmatively selected). `option_text` for
  `resp = 0` is a **derived** descriptive label (see Ambiguities) since no literal
  "not selected" wording exists in the source for these indicator fields individually.
- `resp` coding (0/1) is directly read from `estructura.txt`'s declaration of each
  `P3_1_*` field as a binary "Numérico" 0/1 variable.
- `correct_response` is blank by design (not applicable), not omitted due to missing
  source information.

## Source type used
**Official primary-source materials**: the actual INEGI paper questionnaire instrument
(`encig23_cuestionario.pdf`) and the official data dictionary describing the derived
output variables (`encig23_estructura_base_datos.pdf`), both downloaded directly from
INEGI's public ENCIG 2023 microdata page. This is the strongest source tier available
(literal instrument text plus an authoritative variable-level codebook), not a
paraphrase or secondary description.

## has_bare_integer_items
FALSE, as stated in `tables_batch.csv` — items already carry semantic codes
(`p3_1_01`...`p3_1_11`, `p3_1_99`) that map directly and unambiguously to the 12 named
binary indicator variables documented in INEGI's data dictionary, so no item-to-position
reconstruction was needed.
