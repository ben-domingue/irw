# Extraction log: mexico_2023_quality_corruptionperception

## Source used
Same INEGI source as the sibling table `mexico_2023_quality_problems` (both drawn from
the ENCIG 2023 "Cuestionario general", Section III "PERCEPCIÓN DE CORRUPCIÓN"). Reused
the already-cached PDFs at `.cache/mexico_2023_quality_problems/` rather than
re-fetching — they cover the whole general questionnaire, including questions 3.2 and
3.3:
- `encig23_cuestionario.pdf` (paper questionnaire instrument), text-extracted to
  `cuestionario.txt`
- `encig23_estructura_base_datos.pdf` (data dictionary describing every output
  variable), text-extracted to `estructura.txt`

Both were read as plain PDF-extracted text (not images/OCR).

## Structure discovered
Two questions, immediately following 3.1 (already extracted for the sibling table) in
`cuestionario.txt` (~lines 322-352):

- **Question 3.2** (`p3_2`, single item): "La corrupción es una práctica que sucede
  cuando un(a) servidor(a) público(a) o empleado(a) del gobierno abusa de sus funciones
  para obtener beneficios personales como dinero, regalos o favores por parte de
  los(las) ciudadanos(as). Por lo que usted sabe, en (ESTADO) estas prácticas son:",
  administered with "CIRCULA UN SOLO CÓDIGO" (circle a single code), 5-point response
  card: Muy frecuentes=1, Frecuentes=2, Poco frecuentes=3, Nunca se dan=4, No sabe/no
  responde=9.
- **Question 3.3** (`p3_3_01`..`p3_3_24`, one item per institution): shared stem "En su
  opinión, ¿con qué frecuencia cree que ocurren prácticas de corrupción en...",
  administered with "REGISTRA EL CÓDIGO CORRESPONDIENTE A CADA OPCIÓN" (register the
  code for each option), same 5-point scale but singular wording: Muy frecuente=1,
  Frecuente=2, Poco frecuente=3, Nunca=4, No sabe/no responde=9. The 24 sub-items list
  institutions/authorities (e.g. "01 Universidades públicas?", "02 Policías?", ...,
  "24 Organismos Públicos Autónomos/Descentralizados (CONAPRED, INE, CNDH, INEGI,
  etcétera)?") — confirming the pre-task hypothesis of an institution-corruption
  checklist.

`estructura.txt` (the data dictionary) cross-confirms `P3_2` and `P3_3_01`..`P3_3_24` as
the output variable names (lines 682-839), each documented "Numérico", with option 1 =
"Muy frecuente(s)" — matching order/coding to the questionnaire, and confirming item
01-24 order matches the questionnaire's institution list 1:1. Variable names lower-cased
directly to the IRW `item` codes (`p3_2`, `p3_3_01`...`p3_3_24`), no reconstruction
needed.

## Structure of output
Two `section_id`s:
- `mexico_2023_quality_corruptionperception_p3_2` — the single item `p3_2`.
  `section_prompt` holds question 3.2's full stem plus its "CIRCULA UN SOLO CÓDIGO"
  administration instruction (see Ambiguities re: why this instruction lives in
  `section_prompt` rather than `instructions`). `item_text` left blank since nothing
  beyond the stem in `section_prompt` distinguishes this single item.
- `mexico_2023_quality_corruptionperception_p3_3` — the 24 items `p3_3_01`..`p3_3_24`.
  `section_prompt` holds question 3.3's shared stem plus its "REGISTRA EL CÓDIGO
  CORRESPONDIENTE A CADA OPCIÓN" administration instruction. `item_text` is the literal
  institution/authority label for each sub-item (e.g. "Policías?", "Jueces(ezas) y
  Magistrados(as)?").

Table-wide `instrument` = "INEGI Encuesta Nacional de Calidad e Impacto Gubernamental
(ENCIG) 2023 -- Cuestionario General, Sección III. Percepción de corrupción, preguntas
3.2 y 3.3". Table-wide `instructions` left blank (see Ambiguities).

Four `resp` rows per item (1-4), `option_text` transcribed literally from each
question's own response card (note: 3.2 uses plural wording "Muy frecuentes" etc.; 3.3
uses singular "Muy frecuente" etc. — these are genuinely different literal strings in
the source, not a transcription inconsistency, so were kept as-is per item's own
section). The questionnaire also lists a 5th option, "No sabe / no responde" = 9, for
both questions — **not emitted** because the live ground-truth `resp` set is exactly
{1,2,3,4} (verified via the cached ground truth), consistent with "no sabe/no responde"
responses being recoded to `NA` rather than kept as code 9 (same NA-recoding pattern
observed in the sibling `mexico_2023_quality_problems` table, though the cause there
was also undocumented).

`correct_response` left blank throughout — a perception/opinion battery, no scoring key.

## Ambiguities
- **Where to put the per-question administration instructions (`CIRCULA UN SOLO
  CÓDIGO` / `REGISTRA EL CÓDIGO CORRESPONDIENTE A CADA OPCIÓN`).** The per-tab schema
  keys the `instrument` tab (which carries `instructions`) only by `table`, i.e. one
  instructions value for the whole table. But this table's two questions have two
  different, non-interchangeable administration instructions (one code vs. one code per
  option) — recording either one in the table-wide `instructions` field would
  misrepresent it as applying to both sections. Since `section_prompt` is the only
  schema field that can vary by `section_id`, both admin instructions were appended to
  their respective section's `section_prompt` (with the question stem) instead, and
  `instructions` was left blank. This departs slightly from the sibling table's
  approach (which put its one admin instruction in `instructions`, but had only one
  section so the placement was scope-equivalent either way) — flagged here rather than
  silently deviating.
- Not logged to `pending_index_notes.csv` — no coverage/count discrepancy: all 25 items
  and both fields (`item`, `resp`) matched ground truth exactly.

## Items not extracted
None — all 25 ground-truth items (`p3_2`, `p3_3_01`..`p3_3_24`) and all 4 `resp` values
(1-4) matched and were extracted.

## OCR / image-based extraction
None. Both source PDFs were text-layer PDFs read via ordinary PDF text extraction
(`cuestionario.txt` / `estructura.txt`, reused from the sibling table's cache), not
images or scanned pages.

## Derived vs. directly-read values
- `item_text` (the 24 institution labels for `p3_3`) is directly read/transcribed
  verbatim from the numbered list in `cuestionario.txt`.
- `section_prompt` for both sections is directly read/transcribed verbatim from
  questions 3.2's and 3.3's stems and their administration instructions in
  `cuestionario.txt` (see Ambiguities for why the admin instruction was folded into
  `section_prompt` rather than `instructions`).
- `item` codes (`p3_2`, `p3_3_01`..`p3_3_24`) are directly read from the data
  dictionary's variable names (`estructura.txt`), lower-cased to IRW convention, not
  invented.
- `option_text` for `resp` 1-4 is directly read from each question's own response card
  in `cuestionario.txt`. The 5th card option ("No sabe / no responde" = 9) was
  deliberately **not** emitted, since it is absent from the live `resp` value set — this
  is a derived decision (drop code 9), not a literal-text issue.
- `resp` coding (1-4) is directly read from `estructura.txt`'s declaration of `P3_2`
  and each `P3_3_*` field, cross-checked against the questionnaire's card ordering.
- `correct_response` is blank by design (not applicable), not omitted due to missing
  source information.

## Source type used
**Official primary-source materials**: the same INEGI paper questionnaire instrument
(`encig23_cuestionario.pdf`) and official data dictionary
(`encig23_estructura_base_datos.pdf`) used for the sibling table, both downloaded
directly from INEGI's public ENCIG 2023 microdata page. Strongest available source tier
(literal instrument text plus an authoritative variable-level codebook).

## has_bare_integer_items
FALSE, as stated in `tables_batch.csv` — items already carry semantic codes (`p3_2`,
`p3_3_01`...`p3_3_24`) that map directly and unambiguously to the named variables
documented in INEGI's data dictionary and to the numbered institution list in the
questionnaire, so no item-to-position reconstruction was needed.
