# Journal yield summary

Full methodology, scope boundaries, and per-step detail: see the docstrings
in `resolve_journals.py`, `step2_yearly_counts.py`, `step3_supp_sample.py`,
`step4_license.py`, `step6_build_outputs.py`. This file is the ranked
shortlist + what couldn't be measured.

**Seed**: `20260811` (recorded in `step3_supp_sample.py`, reused by
`step4_license.py` via the Step 3 sample) — reruns reproduce the same
100-record sample per journal.

**Sample window**: most recent 3 years with data as of this run: 2023-2025.

**Positive control (validation gate 1)**: PLOS ONE scored 24% on
`pct_with_data_like_supp`, landing 4th of 26 measured journals -- comfortably
in the top tier (most journals sit at or under 15%), though not #1. PeerJ
scored higher (79%) with only 9% ambiguous-extension-only hits, checked
against its raw file-extension breakdown and found genuine (dominated by
`.xlsx`/`.csv`/`.xls`/`.zip`, not `.zip`/`.txt` noise) rather than a
measurement artifact. Per discussion with Ben (2026-08-11), this was
treated as satisfying the gate: PLOS ONE's strong-tier placement plus a
known-good real-world pipeline track record is enough to trust the
measurement, with PeerJ's higher score noted as a genuine finding rather
than a red flag. **Decision rule going forward**: if a "sample manually
first" journal below doesn't pan out in an early manual batch, prune it
rather than re-litigating the ranking.

**Hand verification (validation gate 2)**: the Europe PMC website
(europepmc.org) is a client-rendered SPA -- WebFetch could not read its
result count off the raw HTML. Substituted a fresh, uncached direct API
call (bypassing the local cache entirely) for 3 journal-years, which
verifies there's no caching bug more directly than eyeballing a rendered
page would: PLOS ONE 2023 (15,030), Behavioral Sciences 2023 (1,010),
Psychometrika 2023 (45) -- all matched the cached CSV values exactly.

**Reproducibility (validation gate 4)**: seed recorded above; every raw API
response is cached under `cache/` with skip-if-exists, so a rerun against
the same cache reproduces byte-identical output, and a rerun with a cleared
cache reproduces the same *sample* (same seed) even if new articles have
since appeared.

## Ranked shortlist

Ranked by `pct_with_data_like_supp` (Step 3 sample), with recent-year OA
volume (`n_oa` summed 2023-2025) as the secondary signal used to break ties
between "worth the engineering cost" and "not worth it despite a high rate."

| journal | data-like % | ambiguous-only % | recent OA vol (23-25) | %CC-BY | PMC deposit proxy | recommendation |
|---|---:|---:|---:|---:|---:|---|
| PeerJ | 79.0 | 9.0 | 5,815 | 97.0 | 0.988 | **harvest now** |
| PLOS Global Public Health | 31.0 | 0.0 | 3,274 | 97.0 | 0.992 | **harvest now** |
| PLOS ONE | 24.0 | 7.0 | 52,046 | 98.0 | 0.993 | **harvest now** (positive control) |
| PLOS Mental Health | 24.0 | 1.0 | 413 | 97.0 | n/a (new journal, see note) | **harvest now** |
| Scientific Reports | 20.0 | 3.0 | 103,516 | 29.0 | 0.997 | **harvest now** -- huge volume offsets a moderate rate; note low %CC-BY, most articles are CC BY-NC-ND/other, flag for license triage |
| PLOS Medicine | 19.0 | 3.0 | 526 | 94.0 | 0.994 | **harvest now** |
| PLOS Digital Health | 15.0 | 1.0 | 766 | 93.0 | 0.995 | **harvest now** |
| Journal of Intelligence | 15.0 | 15.0 | 516 | 100.0 | 1.0 | **harvest now** -- contradicts the prior "MDPI PMC presence uncertain" label; it's well-indexed and PMC-reachable |
| Multivariate Behavioral Research | 22.2 | 22.2 | 9 | 66.7 | 0.21 | **sample manually first** -- rate looks strong but sample_n=9, too small to trust |
| Behavioral Sciences | 12.0 | 12.0 | 4,031 | 100.0 | 0.998 | **sample manually first** |
| Applied Psychological Measurement | 13.0 | 13.0 | 23 | 65.2 | 1.0 | **sample manually first** -- sample_n=23, low volume, moderate rate |
| BMC Medical Research Methodology | 9.0 | 4.0 | 924 | 71.0 | 1.0 | **sample manually first** |
| Journal of Open Psychology Data | 8.1 | 5.4 | 37 | 100.0 | 1.0 | **sample manually first** -- thematically on-target despite modest rate, worth a manual look given the whole journal exists to host this kind of data |
| BMC Public Health | 6.0 | 2.0 | 10,997 | 58.0 | 0.998 | **sample manually first** -- low rate but very high volume, could still yield in absolute terms |
| Heliyon | 4.0 | 1.0 | 29,050 | 30.0 | 0.993 | **sample manually first** -- same logic as BMC Public Health |
| Psychometrika | 11.0 | 10.0 | 135 | 88.0 | 0.467 | **sample manually first** -- hybrid, partial deposit, modest volume |
| Frontiers in Psychology | 3.0 | 1.0 | 12,760 | 100.0 | 0.996 | skip -- high volume doesn't offset a very low rate |
| BMC Psychology | 2.0 | 0.0 | 2,801 | 50.0 | 0.996 | skip |
| Behavior Research Methods | 1.0 | 0.0 | 516 | 99.0 | 0.614 | skip |
| Cognitive Research: Principles and Implications | 1.0 | 0.0 | 239 | 99.0 | 0.986 | skip |
| Royal Society Open Science | 0.0 | 0.0 | 1,873 | 100.0 | 1.0 | skip |
| Memory & Cognition | 0.0 | 0.0 | 194 | 100.0 | 0.425 | skip |
| Attention, Perception & Psychophysics | 0.0 | 0.0 | 265 | 99.0 | 0.49 | skip |
| Assessment | 0.0 | 0.0 | 86 | 73.3 | 0.412 | skip |
| Educational and Psychological Measurement | 0.0 | 0.0 | 43 | 53.5 | 1.0 | skip |
| European Journal of Psychological Assessment | n/a | n/a | 0 | n/a | 1.0 (n=1, unreliable) | **not reachable this way** -- zero OA full-text records in Europe PMC for 2023-2025 |
| Journal of Educational Measurement | n/a | n/a | 0 | n/a | 1.0 (n=1, unreliable) | **not reachable this way** -- zero OA full-text records in Europe PMC for 2023-2025 |

Note on Scientific Reports and Heliyon/BMC Public Health's low %CC-BY: this
is the license-mix column doing its job, not a data-quality problem --
these journals mix CC BY with other Springer Nature/Elsevier license terms
even among OA articles. Reported, not filtered, per spec; a human makes
the license call per table at processing time as usual.

## What could not be measured, and why

- **PMC deposit scope ("all articles" vs funder-only)**: the official PMC
  Journal List (pmc.ncbi.nlm.nih.gov/journals/) is a client-rendered page
  with no stable scrape target or API found. Substituted a proxy --
  `IN_PMC:y` hitCount over total hitCount for 2023 -- computed from Europe
  PMC itself (already in scope). This is in the `pmc_deposit_scope_proxy`
  column throughout. Caveat: at low total-hitcount volumes (roughly <50)
  this ratio isn't statistically meaningful -- several Tier E journals show
  `1.0` on a base of 1-45 records, which just means Europe PMC's index for
  that ISSN is thin, not that deposit is complete.

- **Springer OA supplemental counts (Step 5)**: `SPRINGER_API_KEY` is not
  set in this environment. Per spec, left as NA (`springer_oa_n` column)
  rather than fetched, and no key was registered or hardcoded. This mainly
  affects Springer-hybrid Tier E titles (Behavior Research Methods,
  Psychometrika, Multivariate Behavioral Research, Memory & Cognition,
  Attention Perception & Psychophysics) -- their true OA volume may be
  understated here since Europe PMC/PMC coverage of hybrid journals is only
  the funder-eligible slice.

- **Five journals dropped before Step 2** (thin all-time Europe PMC
  volume, confirmed by an unfiltered all-time ISSN query, not just a bad
  reference year): Meta-Psychology (0 hits ever), Psychological Test
  Adaptation and Development (1), Psych/MDPI (2), Measurement Instruments
  for the Social Sciences (7), Judgment and Decision Making (17). These
  aren't necessarily bad IRW targets -- they may just not be indexed in
  Europe PMC/PubMed at all, which this pipeline can't see past.

- **Five journals dropped after Step 2** for a different, more serious
  reason: their real publication volume, cross-checked against Crossref,
  turned out to be 6x-600x higher than what Europe PMC's ISSN search
  reported, meaning they're essentially invisible to Europe PMC rather than
  genuinely low-volume: Journal of Statistical Software (32 Crossref vs 5
  Europe PMC, 2023), Frontiers in Education (1,029 vs 5), Large-scale
  Assessments in Education (39 vs 5), Collabra: Psychology (110 vs 2),
  Education Sciences/MDPI (1,256 vs 2). **A PMC-based connector cannot
  reach these journals at all**, regardless of their true supplementary-file
  yield -- they would need a Crossref-driven or publisher-direct access
  route, which is a different, unbuilt mechanism and out of scope for this
  study's positive-control-validated methodology. Worth a separate look if
  their real yield turns out to matter (Education Sciences in particular
  publishes at PLOS ONE-scale volume).

- **European Journal of Psychological Assessment / Journal of Educational
  Measurement**: real journals, resolved cleanly in Step 1, but zero OA
  full-text records in Europe PMC for the entire 2023-2025 sample window
  (pool=0) -- flagged `not reachable this way` per the spec rather than
  reported as a fabricated 0% yield. Both are hybrid journals with very low
  overall volume in Europe PMC's index even outside the OA filter (1
  record each in 2023), so this is likely a genuine near-total absence of
  OA content from these titles in the relevant window, not a search bug.

## Environment

- Europe PMC REST API, no authentication
- Crossref REST API (`api.crossref.org`), no authentication, contact email
  in User-Agent
- OpenAlex REST API (`api.openalex.org`), `mailto` param set
- DOAJ REST API (`doaj.org/api`), no authentication
- Python 3, `requests`
- Contact email used throughout: ben.domingue@gmail.com
- All raw API responses cached under `cache/{resolve,step2,step3,step4}/`
