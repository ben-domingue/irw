# Extraction log: rd_ppcsedsof_afable_2023

## Source type used
- Primary source: the open-access PLOS ONE paper itself — Afable SD, Cruz GT,
  Saito Y (2023), "Sex differences in the psychometric properties of the
  Center for Epidemiological Studies–Depression (CES-D) Scale in older
  Filipinos," PLOS ONE 18(6):e0286508, doi:10.1371/journal.pone.0286508
  (fetched via journals.plos.org and its PMC mirror,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10266601/). Note the dictionary
  row's "Reference" field title ("...CES-D Scale in Older Filipinos") is a
  close paraphrase of the actual published title, which specifically frames
  the paper as a **sex-differences** study — same underlying paper, confirmed
  by DOI cross-check (dictionary DOI 10.7910/DVN/UT9RVL is the Harvard
  Dataverse *replication data* record; the paper itself is
  10.1371/journal.pone.0286508).
- Dataverse landing page (`dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/UT9RVL`)
  was attempted twice (plain URL and with an explicit `&version=1.0`) via
  WebFetch to look for a codebook/questionnaire file listing the P1SD1_*
  variables. Both attempts returned an empty page body to the fetch tool (no
  error, just no extractable content) — consistent with dataverse.harvard.edu
  serving a JS-rendered file-listing UI that a plain scraping fetch can't
  execute, similar to the WAF-style blocks seen on other Dataverse-hosted
  tables in this batch (e.g. `gilbert_meta_38`). Did not retry a third time
  per the task's 1-2 attempt budget. The Harvard Dataverse API endpoint
  (`api/datasets/:persistentId/`) was also tried directly with WebFetch and
  likewise returned no content.
- Did not use `irw::irw_fetch()` myself; used the cached ground truth at
  `.gt_rd_ppcsedsof_afable_2023.rds` per instructions.

## OCR / image-based extraction
Not applicable — both the PLOS ONE HTML article and its PMC mirror were
fetched as machine-readable text/HTML (WebFetch's markdown conversion), not
as scanned images or PDF requiring OCR. No image-based extraction was
performed or needed.

## Derived vs. directly-read values
- **`instrument` name** — DERIVED. The paper never gives the scale a single
  formal name distinct from "the 11-item CES-D Scale" / "the 11-item
  3-response category CES-D Scale." I constructed `"CES-D Scale (11-item,
  3-response version)"` to disambiguate from the standard 20-item CES-D and
  the more common 4-point Kohout-derived short forms (see "P1SD1 /
  instrument-variant" section below) — this label is my synthesis, not a
  verbatim title from the paper.
- **`instructions`** — DIRECTLY READ (near-verbatim). Quoted from the paper:
  "Respondents were asked to rate how often they felt these symptoms in the
  past seven days based on a three-response scale." This is table-wide
  framing text, so it belongs in `instructions` per the boundary rule, not
  `section_prompt` (there is no testlet/passage grouping here — all 11 items
  share one flat CES-D block, so a single `section_id`
  (`rd_ppcsedsof_afable_2023_cesd`) was used with a blank `section_prompt`,
  per the "still emit one section_id, blank prompt" rule when there's no real
  grouping).
- **`item_text`** — DIRECTLY READ, but note these are the paper's own SHORT
  LABELS, not the full literal item stems as administered to respondents.
  The paper's Figure 3 legend gives, verbatim: "1 –poor appetite; 2 –feeling
  depressed; 3 –feeling that everything was an effort; 4 –restless sleep;
  5 –feeling happy; 6 –feeling lonely; 7 –feeling that people are unfriendly;
  8 –enjoyed life; 9 –feeling sad; 10 –feeling that people dislike you;
  11 –could not get going." These labels were used as `item_text` (with only
  capitalization normalized), in item order 1–11 matching P1SD1_01–P1SD1_11
  exactly. The paper does NOT reproduce the full CES-D item sentences (e.g.
  the canonical "I did not feel like eating; my appetite was poor" form) or
  the Filipino-language wording actually read to respondents, and no
  appendix/supplementary questionnaire file was found (see Dataverse access
  issue above). I deliberately did **not** substitute the well-known
  "textbook" Kohout/HRS-family 11-item CES-D full-sentence wording (which I
  did locate via web search for cross-reference) because that wording comes
  from a different survey family (HRS/AHEAD/ELSA/SHARE) using a different
  4-point response scale, and I have no confirmation the LSAHP instrument
  used identical phrasing or was even administered in English — using it
  would risk fabricating text not actually shown to belong to this specific
  instrument. `item_text` should therefore be read as short descriptive
  labels, not literal respondent-facing item stems.
- **`option_text` / `resp` mapping** — PARTIALLY DERIVED. The paper states the
  response scale directly: "0 –Rarely/Not at all, 1 –Sometimes, and 2
  –Often." The live ground-truth `resp` values are `1, 2, 3`, not `0, 1, 2`.
  I mapped resp=1→"Rarely/Not at all", resp=2→"Sometimes", resp=3→"Often",
  assuming a uniform +1 shift between the paper's reported (post-recode)
  scoring and the raw IRW/Dataverse response coding. **This shift is an
  assumption, not independently confirmed** by a codebook (which I could not
  access — see above). It is the simplest and most standard explanation
  (raw survey responses are very commonly 1-based, then recoded 0-based for
  analysis/scoring), and the ordinal direction (higher = more frequent
  symptom) is unambiguous either way, but flagging this explicitly as a
  discrepancy per Step 6b.
- **`correct_response`** — left blank for all items; this is a symptom
  self-report inventory with no scoring key/correct answer.

## has_bare_integer_items
FALSE, as given in the dictionary row — and confirmed against the ground
truth: `item` values are semantic codes (`P1SD1_01`...`P1SD1_11`), not bare
integers, so no position/order reconstruction from bare integers was needed.
The mapping challenge here was different: matching the paper's own 1–11
item-label numbering to the P1SD1_01–P1SD1_11 suffixes, which line up
one-to-one in the same order (both start at 1/01 and run to 11).

## What "P1SD1" turned out to mean
Not explicitly glossed anywhere in the accessible sources (paper text or
Dataverse), so this is inference, flagged as such. The source data are from
the **Longitudinal Study of Ageing and Health in the Philippines (LSAHP)**
baseline survey (2018–2019 face-to-face interviews, nationally representative
sample of community-dwelling Filipinos 60+, N=5,209 — matches this table's
N exactly). LSAHP-style panel surveys of this kind typically organize their
questionnaire into lettered/numbered "Panel"/"Person"/"Section" blocks (e.g.
Panel 1 = respondent-level questionnaire, Section D = a specific health/
well-being module); "P1SD1" most plausibly parses as **Panel 1, Section D,
sub-block 1** (i.e., the first item-block within the depressive-symptoms
section of the main respondent questionnaire), with `_01`.._11` as the
sequential item numbers within that block. This reading is consistent with
the paper's own framing (CES-D is one of several health instruments — "self-
assessed health, diagnosed illnesses, oral health, sleep, pain, falls,
incontinence, depressive symptoms..." per LSAHP documentation) but I could
not confirm the literal section lettering/numbering scheme against an actual
LSAHP codebook or questionnaire PDF (not found in the accessible sources).

## Which CES-D variant this is
Confirmed via the paper itself: this is the **11-item, 3-response-category
CES-D short form** (not the standard 20-item CES-D, and not the more common
8-item or 10-item short forms used in HRS/SHARE/ELSA-family surveys, which
typically use binary yes/no or a different 4-point scale). The paper reports
four subscales: Positive Affect (items 5, 8 — happy, enjoyed life — reverse
scored), Depressed Affect (items 2, 9 — depressed, sad), Somatic Retardation
(items 1, 3, 4, 11 — appetite, effort, sleep, could-not-get-going), and
Interpersonal (items 6, 7, 10 — lonely, unfriendly, disliked). This 11-item/
3-point combination does not match the well-known Kohout et al. (1993)
11-item short form (which uses a 4-point "Never/Hardly ever/Some of the
time/Most of the time" scale in HRS-family surveys) — it appears to be a
variant specific to this Philippine survey instrument (or a locally adapted
translation), not a direct reuse of the Kohout form, despite having the same
11 underlying CES-D symptom items.

## Ambiguities / discrepancies (see pending_index_notes.csv)
1. `item_text` values are the paper's short descriptive labels (from a figure
   legend), not the literal full item stems/sentences as administered to
   respondents — the actual questionnaire wording (possibly in Filipino) was
   not recoverable; the Dataverse dataset page could not be scraped (returned
   empty content to WebFetch on two attempts, consistent with a JS-rendered
   file listing).
2. `resp`/`option_text` mapping (1/2/3 → Rarely/Sometimes/Often) assumes a
   +1 shift relative to the paper's stated 0/1/2 coding; not independently
   confirmed by a codebook.
3. `instrument` name is my own synthesized label, not a verbatim title quoted
   from the paper.
4. "P1SD1" section-naming interpretation (Panel 1 / Section D / block 1) is
   inference from general LSAHP survey structure, not confirmed by an actual
   codebook.

## Validation result
EXACT MATCH. `unique(item)` == the 11 ground-truth `P1SD1_01`..`P1SD1_11`
values exactly (33 rows total: 11 items × 3 resp levels). `unique(resp)` ==
`{1, 2, 3}` exactly, matching `irw::irw_fetch("rd_ppcsedsof_afable_2023")`
via the cached ground truth. The item-count and resp-cardinality match is
structural (11 items, 3-point scale, confirmed directly from the paper's own
description of its instrument) — it is the underlying item *wording* and the
0/1/2→1/2/3 *coding direction* that carry the residual uncertainty logged
above, not the item/resp value sets themselves.
