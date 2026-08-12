# Extraction log: gilbert_meta_58

## Source type used
Published paper only (open-access PMC version). No supplementary appendix content
was actually recoverable (see below), and the Harvard Dataverse dataset page/exporters
were not attempted directly per the batch note that dataverse.harvard.edu is
AWS-WAF-blocked for every gilbert_meta table tried so far in this series; the DataCite
metadata API (api.datacite.org, a different host, not WAF-blocked) was checked instead
and returned only a dataset-level abstract, no variable/codebook documentation.

## Source used
- Reference paper: Maselko, J., Sikander, S., Turner, E. L., Bates, L. M., Ahmad, I.,
  Atif, N., ... & Rahman, A. (2020). Effectiveness of a peer-delivered, psychosocial
  intervention on maternal depression and child development at 3 years postnatal: a
  cluster randomised trial in Pakistan. *The Lancet Psychiatry*, 7(9), 775-787.
  doi:10.1016/S2215-0366(20)30258-3. Open-access PMC copy located: PMC8015797
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC8015797/).
- Fetched/read via WebFetch (page rendered to markdown/text by the fetch tool; no local
  PDF cache created because the article HTML itself was directly readable, unlike the
  supplementary appendix — see below).
- Dataverse dataset page (doi:10.7910/DVN/IJE2PC, "Bachpan Study of Maternal Depression
  and Child Development: Data from the First Three Years") — confirmed via DataCite
  metadata API only (`api.datacite.org/dois/10.7910/DVN/IJE2PC`); the abstract text
  describes the overall cohort/trial design but contains no per-variable codebook
  content. The native dataverse.harvard.edu page/exporters were not queried directly
  (consistent with the known WAF block for this table series).
- Protocol/companion papers checked for item-level detail: the trial protocol erratum
  (PMC5314478, redirects to the actual protocol at doi:10.1186/s13063-016-1530-y, not
  independently fetched) and a related PMC paper (PMC6964000, "Maternal depression in
  rural Pakistan: the protective associations with cultural postpartum practices").

## What the paper actually discloses about the instrument
The Lancet Psychiatry paper's Methods section states only:
> "The secondary maternal outcomes were disability assessed using WHO's Disability
> Assessment Schedule, WHO-DAS, and current major depressive episode based on the
> Structured Clinical Interview for DSM-IV (SCID) Disorders." (citing SCID by reference
> to the standard First et al. SCID manual, not an in-paper appendix)

Figure 2's legend gives only "SCID – Structured Clinical Interview for Depression; MDE –
Major Depressive Episode" as a label, with no item-level breakdown. No enumerated list of
individual symptom criteria (depressed mood, anhedonia, appetite/weight change, sleep
disturbance, psychomotor change, fatigue, worthlessness/guilt, concentration, suicidal
ideation, etc.), no item numbering scheme, and no scoring rubric beyond the overall
binary MDE diagnosis are given anywhere in the accessible article text.

## Supplementary appendix — attempted, not recoverable
PMC lists a supplementary appendix (`NIHMS1672023-supplement-Appendex.pdf`) attached to
PMC8015797. Both a direct `curl` fetch and a `WebFetch` call against
`https://pmc.ncbi.nlm.nih.gov/articles/instance/8015797/bin/NIHMS1672023-supplement-Appendex.pdf`
returned only an interstitial "Preparing to download..." HTML page containing an NCBI
proof-of-work (PoW) bot-challenge script (`window.ncbi.pmc.pow.init(...)`), not the PDF
itself — this tooling environment cannot solve a JS proof-of-work challenge. Saved the
interstitial response at `.cache/gilbert_meta_58/appendix.pdf` (actually HTML) for the
record. Even if recovered, it is unclear the appendix would contain a full item-level
SCID script — SCID interview forms are semi-structured clinician-administered
instruments (copyrighted, First et al./American Psychiatric Association), not a
self-report scale with a fixed verbatim item list typically reproduced in journal
supplements.

## OCR / image-based extraction
Not applicable — no image-embedded instrument content was located or attempted for this
table (unlike e.g. `gilbert_meta_56`, where the source PDF's instrument pages were
scanned images). All source material checked here (main article text, DataCite
abstract) was native text; the one inaccessible artifact (the supplementary appendix)
was blocked by a JS proof-of-work challenge before any image content could even be
determined to exist, not an OCR failure.

## Derived vs. directly-read values
- `item` (scid1now .. scid13now) and `resp` (0/1) are read directly from the cached
  ground truth (`irw::irw_fetch("gilbert_meta_58")`), not derived or reconstructed.
- `instrument` ("Structured Clinical Interview for DSM-IV (SCID) Module for Current
  Major Depressive Episode") is transcribed near-verbatim from the paper's own
  Methods-section naming of the instrument.
- `item_text` and `option_text` are left `NA` for all 13 items / 26 rows — **not
  derived, guessed, or paraphrased**. The paper discloses only that a 13-symptom(ish)
  current-MDE SCID module was administered; it does not enumerate individual symptom
  items, wording, or per-item 0/1 anchor labels anywhere in the accessible text or
  DataCite metadata, and the one place such detail might live (the supplementary
  appendix) is blocked by a bot-challenge. Per the skill's "do not guess" instruction,
  no attempt was made to reconstruct 13 SCID-IV mood-module symptom items from generic
  knowledge of the standard SCID-IV instrument (which has 9 core DSM-IV MDE criteria,
  not 13 — the discrepancy itself is a reason not to guess a 1:1 mapping).
- `instructions`, `section_prompt`, `correct_response` left blank for all rows — not
  disclosed anywhere accessible (there is no "correct" answer for a diagnostic symptom
  checklist).

## has_bare_integer_items
FALSE, as stated in the dictionary row — item values are already semantic labels
(`scid1now`..`scid13now`), not bare integers requiring positional reconstruction. This
does not change the outcome here: even with semantic labels, the *content* behind each
label (which specific DSM-IV symptom criterion `scid1now` vs. `scid2now` etc. refers to)
is simply not disclosed in any source checked.

## Items not extracted
All 13 ground-truth items (`scid1now`..`scid13now`) are present in the output with
correct `item`/`resp` values (exact match validated against
`.gt_gilbert_meta_58.rds`), but `item_text`/`option_text` are blank/NA for all of them —
zero of 13 items have literal source text recovered. This is logged as a discrepancy in
`pending_index_notes.csv` per Step 6b.

## Validation result
`item` and `resp` sets match ground truth **exactly** (13 items, resp {0,1}).
`item_text`/`option_text` coverage: 0/13 items (genuinely undisclosed source, not a
guessing failure).
