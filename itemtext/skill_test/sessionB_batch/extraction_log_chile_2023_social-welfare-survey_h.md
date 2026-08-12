# Extraction log: chile_2023_social-welfare-survey_h

## Source used
Dictionary URL (`https://bidat.gob.cl/details/ficha/dataset/f80237f5-9231-40d1-a1f1-ed93751dc2ac`)
identifies the dataset as **Encuesta de Bienestar Social (EBS) 2023** ("Social Welfare
Survey" -- confirms the dictionary's construct label), fielded by Chile's Ministerio de
Desarrollo Social y Familia jointly with the Instituto Nacional de Estadisticas (INE),
September-December 2023, N ~ 11,234-12,500 adults 18+. bidat.gob.cl itself only exposed
the codebook (xlsx), STATA/SPSS/RData microdata, and encrypted download links -- no
questionnaire PDF on that page directly.

Found the actual questionnaire and codebook via the Ministry's own "Observatorio Social"
site (`observatorio.ministeriodesarrollosocial.gob.cl/encuesta-bienestar-social-2023`),
which lists the full document set for EBS 2023. Downloaded and cached under
`.cache/chile_2023_social-welfare-survey_h/`:
- `Cuestionario_EBS_2023.pdf` (full applied questionnaire, "Cuestionario_EBS_2023_241001.pdf")
- `Libro_de_codigos_EBS_2023.xlsx` (codebook, sheet `H`)
- `Diseno_Cuestionario_EBS_2023.pdf` (questionnaire design/methodology report -- used only
  to orient on module structure, not for item text)
- `Ficha_Tecnica_EBS_2023.pdf` (technical fact sheet)

## Source type used
Primary: the government's own applied questionnaire PDF (literal respondent-facing
question wording, interviewer instructions, and response option lists, extracted via
`pdftotext -layout`) cross-checked against the codebook spreadsheet's `H` sheet (variable
names, item labels, value labels, and per-category response frequencies). Both are
official first-party documents from the survey's publisher, not a secondary/derived
source.

## Structure discovered
The dictionary row's guess that the `h` prefix = "section H" was correct, but the
specific content guess (a generic housing/neighborhood section) was wrong: **Modulo H in
this instrument is "Seguridad" (Security/crime-victimization and perceived safety)**, not
housing. Housing is a *different* module ("Modulo V: Vivienda") in this instrument, which
happens to reuse the same value 1-5 range but is a separate module (not present in this
table's item set). This was resolved by locating the actual questionnaire PDF and codebook
directly, not by inferring content from the letter alone.

Module H's 13 items break into four question blocks / testlets, exactly matching the
ground truth's `h1`, `h2_a`-`h2_d`, `h3_a`-`h3_e`, `h4_a`-`h4_c`:
- **h1** (standalone): "En los ultimos 12 meses, ¿cuantas veces ha sido victima de un
  delito, como asalto o robo al interior o fuera de su hogar?" -- 3-point scale
  (1=Nunca, 2=Una vez, 3=Mas de una vez).
- **h2_a-d**: shared stem "En los ultimos 12 meses, en su barrio o localidad me podria
  decir, ¿que tanta seguridad siente en las siguientes situaciones?" -- 4 sub-situations
  (plazas/parks; walking by day; walking by night; inside home/property), 5-point scale
  (1=Nada ... 5=Mucha).
- **h3_a-e**: shared stem "En los ultimos 12 meses, por temor a ser victima de algun
  delito; como robo o asalto..." -- 5 avoidance-behavior sub-items, mostly Si/No (1/2)
  except h3_d and h3_e which add a third non-applicable category (3="No hay ninos..." /
  3="No usa transporte publico").
- **h4_a-c**: shared stem "En su barrio o localidad, ¿cuentan con alguna de estas
  instancias para abordar los problemas de seguridad?" -- 3 neighborhood-security-resource
  sub-items, Si/No (1/2).

This is a textbook case of the SKILL.md instructions/section_prompt boundary rule: each
of h2/h3/h4's shared stems is framing text specific to that subset of items (a
testlet-context prompt), not whole-table framing, so it was recorded once in
`section_prompt` per `section_id` (`h2`, `h3`, `h4`) rather than in `instructions`. The
one genuinely whole-module framing line ("Ahora, le hare algunas preguntas respecto a la
seguridad publica.", printed immediately before h1 as the module's opening line) was
recorded once in `instructions` and applied to all 13 items, including h1 itself. h1 was
given its own trivial `section_id` (`h1`) with a blank `section_prompt` since it has no
shared framing beyond the module-level instructions.

Interviewer-only directives visible in the PDF (`Lea alternativas.`, `Espere respuesta
espontanea.`, `[NO LEER]` markers next to the -88/-99 sentinel codes, `Condicion
habilitante: no tiene`) were treated as interviewer script, not respondent-facing
instructions/item_text/option_text, and excluded from the transcription -- consistent
with "literal transcript, not a rewrite," since these aren't text read to the respondent.

## has_bare_integer_items
FALSE, as stated in the dictionary row -- confirmed: all 13 `item` values are the
survey's own semantic variable codes (`h1`, `h2_a`, ..., `h4_c`), not bare integers, so no
item-to-question reconstruction/ordering judgment call was needed.

## OCR / image-based extraction
None needed. `Cuestionario_EBS_2023.pdf` is a native-text (not scanned/image) PDF;
`pdftotext -layout` extracted clean text directly. No OCR was performed or required.

## Derived vs. directly-read values
All `item_text`/`section_prompt`/`instructions`/`option_text` values are directly
transcribed (copy-typed with only encoding cleanup, e.g. plain apostrophes/no accents in
this log) from the literal questionnaire PDF text, not derived/paraphrased. Where the
codebook's `Label` column gave a shorter/paraphrased version of the same question (e.g.
codebook: "h3_c. Por temor a delito: ¿Dejo de llevar dinero, joyas, documentos o celular?"
vs. questionnaire's fuller "En los ultimos 12 meses, por temor a ser victima de algun
delito...¿Dejo de llevar dinero en efectivo, joyas, documentos o celular?"), the fuller
questionnaire wording was used as `item_text`/`section_prompt` since it is the actual
instrument text the respondent heard; the codebook's shorter label was treated as a
paraphrase for spreadsheet purposes, not the source of record. `resp`/`option_text`
mappings (1=Nunca/2=Una vez/3=Mas de una vez, etc.) are directly read from both the
questionnaire's printed option lists and the codebook's `Value Labels` column, which
agreed in all 13 items.

## Validation
Built `candidate_chile_2023_social-welfare-survey_h.rds` (41 rows, one row per
(item, resp) pair actually observed) and validated directly against the cached ground
truth (`.gt_chile_2023_social_welfare_survey_h.rds`):
- `unique(item)`: exact match (13 items, all present).
- Per-item `unique(resp)` sets: exact match for all 13 items (h1: {1,2,3}; h2_*: {1..5};
  h3_a/b/c/e: {1,2}; h3_d/h3_e: {1,2,3}; h4_*: {1,2}).
- As a further, stronger check beyond the skill's required item/resp-set validation: the
  codebook's `Frecuencia` column (per-category response counts) was cross-tabulated
  against `table(gt$item, gt$resp)` on the live ground-truth data and matched exactly for
  every item/response-value cell (e.g. h1: 9693/1022/510 for Nunca/Una vez/Mas de una vez
  in both codebook and ground truth) -- strong independent confirmation that the h1-h4
  mapping and response coding are correct, not just plausible.

## Items not extracted
None -- all 13 ground-truth items were fully extracted with literal item text and
response-option text, and validated as an exact match (item set, resp set, and per-item
response-frequency cross-tab) against the cached ground truth. No entry added to
`pending_index_notes.csv` since there is no discrepancy to log.
