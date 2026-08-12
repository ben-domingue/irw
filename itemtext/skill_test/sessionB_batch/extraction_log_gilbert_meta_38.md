# Extraction log: gilbert_meta_38

## Post-hoc correction (batch review)
The original extraction populated `item_text`/`option_text` with inferred/reconstructed
wording (see "Derived vs. directly-read values" below) rather than leaving them blank.
On review, this was inconsistent with how every other blocked-source table in this batch
was handled (`gilbert_meta_2`, `gilbert_meta_74`, `gilbert_meta_100`, `gilbert_meta_80`,
`gilbert_meta_78` all left `item_text` blank/NA when the literal source was unreachable,
per SKILL.md's "don't force a match... don't guess" rule) and risked reading as fabricated
content in a benchmark output. **`candidate_gilbert_meta_38.rds` has been corrected**:
`item_text` and `option_text` are now blank/NA for all 9 items, matching the treatment of
the other partial-coverage tables. `item`/`resp`/`instrument` are unchanged and still
match ground truth exactly. The reconstruction reasoning below is retained for the record
(and for a future manual curator who may find it a useful starting point) but should not
be read as verified content.

## Source type used
No literal instrument text was recoverable. `item_text` for all 9 items was originally
populated with **derived/reconstructed** text from the variable-name semantics using
standard DHS-style health-survey question phrasing, not transcribed from the actual
questionnaire — see the correction note above; this has since been blanked in the
candidate output. See "Derived vs. directly-read values" below for the original reasoning.

## Repo script check
`grep -rl "EJ03JR\|gilbert_meta_38\|Carpena\|entertainment.education" data/` returned no
matches — no existing IRW processing script for this table in this repo.

## Cache check
`.cache/gilbert_meta_38/` was empty at the start of this run (prior crashed attempt left
no cached material to reuse). All web-search/fetch attempts below were made fresh.

## Ground truth
`readRDS(".gt_gilbert_meta_38.rds")`: 9 items exactly as given in the task
(`aids_tested_self`, `bought_ins`, `condom_use`, `nightblindness_food`, `pregnancy_anc`,
`pregnancy_hospital`, `wash_soap3`, `water_boil_filter`, `water_tap`), `resp` in `{0,1}`.
`has_bare_integer_items` is **FALSE** — items already carry semantic variable-name labels,
so no position/order reconstruction was needed for item identity (unlike the bare-integer
case in the SKILL.md guidance); the open question here was purely the *literal question
wording* behind each semantic label, not which item an integer refers to.

## Attempts to reach the paper / Dataverse package (all logged for future retry)

1. **Harvard Dataverse (doi:10.7910/DVN/EJ03JR)** — dataset landing page
   (`dataset.xhtml?persistentId=...`), the native API
   (`/api/datasets/:persistentId/?persistentId=...`), the `dataverse_json` and `croissant`
   exporters, and a Wayback Machine snapshot of the landing page were all tried via both
   `WebFetch` and direct `curl`. Every attempt against `dataverse.harvard.edu` returned
   HTTP 202 with an empty body and header `x-amzn-waf-action: challenge` — an AWS WAF
   bot-challenge, not a real 4xx/redirect, so no file listing or file content was ever
   reached. This matches the identical failure mode logged in this session's
   `gilbert_meta_2`, `gilbert_meta_74`, and `gilbert_meta_100` extraction logs (same
   Dataverse SPA, same block). `web.archive.org` itself is also blocked to this
   environment's WebFetch tool outright ("unable to fetch from web.archive.org").
2. **DataCite metadata API** (`api.datacite.org/dois/10.7910/DVN/EJ03JR`, a different host,
   not WAF-blocked) — succeeded and confirmed the package's *shape* but not filenames: 67
   files total, formats = mostly `application/x-tex` and `application/x-stata-syntax`
   (`.do` files) plus a handful of `text/tab-separated-values`, **one**
   `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (`.docx`),
   and **one** `application/pdf`. The single `.docx` and/or `.pdf` are the most likely
   candidates for a questionnaire/codebook, but DataCite's metadata does not expose
   individual filenames, so the specific file could not be identified, let alone
   downloaded.
3. **Published paper** — Carpena, F. (2024), *Entertainment-Education for Better Health:
   Insights from a Field Experiment in India*, Journal of Development Studies, 60(5),
   745-762, doi:10.1080/00220388.2024.2312832. `tandfonline.com/doi/full/...` was reachable
   once (returned only the abstract/summary, no body text); every subsequent attempt at the
   full-text or PDF URL (`.../doi/pdf/...`, `.../doi/epdf/...`) returned HTTP 403
   (paywalled). No tandfonline "Supplemental data" page was reachable either (403).
4. **Open-access working-paper route** (per SKILL.md Step 3) — found the 2020 precursor
   working paper, *Delivering Effective Health Education in Developing Countries: Insights
   from a Field Experiment in India* (RePEc `oml/wpaper/202001`,
   `https://ideas.repec.org/p/oml/wpaper/202001.html`), whose only "download full text"
   link is SSRN doi:10.2139/ssrn.3638161 — `papers.ssrn.com` returned HTTP 403 on every
   attempt (abstract page and the direct abstract_id URL).
5. **Other open-access searches** — EdWorkingPapers, OSF/PsyArXiv, ResearchGate, CORE
   (`api.core.ac.uk`), Semantic Scholar (`openAccessPdf` field resolved to the same 403'd
   tandfonline PDF URL), and the author's OsloMet/UiO/Berkeley personal pages were all
   checked; none surfaced an accessible full-text copy or a standalone questionnaire/
   appendix file. The OsloMet NVA research-archive record (`hdl.handle.net/11250/3161967`)
   redirects to a JS-rendered `nva.sikt.no` page that returned no fetchable content.

## Derived vs. directly-read values

**Nothing in this output is directly read from the instrument.** All 9 `item_text` values
are reconstructed from the variable-name labels alone, using conventional DHS/health-survey
phrasing for these very standard indicators (HIV testing, ITN purchase, condom use,
vitamin-A/night-blindness food knowledge, antenatal care attendance, facility delivery,
handwashing with soap, water treatment, tap-water access) — kept terse to match the
terseness of the source labels themselves, per SKILL.md's "match the source's terseness"
rule. `option_text` (`Yes`/`No` for `resp` 1/0) and the `instrument` name are also
reasonable inferences, not confirmed against the actual questionnaire.
`instructions`/`section_prompt` are left blank rather than invented. `correct_response` is
blank throughout — these are self-reported behaviors, not a knowledge test with a scoring
key.

## Items not extracted (literal wording)
All 9 — none of the literal survey question wording was recoverable given the sources
reachable from this environment. See `pending_index_notes.csv` for the logged discrepancy
and the suggested manual follow-up (download the Dataverse package's `.docx`/`.pdf` files
directly, bypassing the automated-fetch WAF block, to find and transcribe the actual
questionnaire).

## Validation
`unique(item)` and `unique(resp)` in `candidate_gilbert_meta_38.rds` match
`readRDS(".gt_gilbert_meta_38.rds")` exactly (9 items, resp `{0,1}`) — validated by direct
`setequal()` comparison in R (see `build_gilbert_meta_38.R`). This is an **exact** match on
the structural (item/resp) validation gate; the semantic content of `item_text` is a
logged, flagged discrepancy (derived, not literal), not a structural one.
