# IRW Automated Finding — TODO

Currently open action items only. For the full batch-by-batch history and
context behind these (and everything already resolved), see `BATCH_LOG.md`.

- [ ] **Political Preference China** (`10_7910_dvn_dwplbc.csv`, DVN/dwplbc) — on
  hold: 0-response ambiguity, anchor labels not documented in the source.
  Needs the anchor-label question resolved before it can be processed.

- [ ] **SAPA 7 annual releases** (2017–2024, DOIs DVN/PNGUT5 through
  DVN/3BTT82, all CC0, none in IRW yet) — decision needed on scope: process
  all 7 years separately, most recent only, or pool with `cov_year`. File
  IDs and format details are in `BATCH_LOG.md`'s "Pipeline improvements"
  section.

- [ ] **Batch 11 `worth_retrying` cases**, never investigated:
  - Questionnaire scores/descriptive stats (748p/62i, figshare 30033097)
  - Personality predicts prosocial behavior (801p/66i, osf.io/zcdk8/)
  - Coaching leadership styles / athlete engagement (197p/15i, figshare
    29856026) — only issue flagged is low-confidence id column
  - Affect spin and prosocial behavior (400p/16i, figshare 29486192)

- [ ] **`human_review` backlog** — several hundred rows accumulated across
  all batches, tracked in the "Automated queue - Human eye" Google Sheet
  (not in this repo). Needs a person to periodically review and either
  process or dismiss entries.

- [ ] **Two strong OSF candidates blocked only on missing license** (not a
  content problem — worth an author-permission email per
  `processing_notes/Licensing.txt` if someone wants to pursue them):
  - "The Role of Attentional Bias in Anxiety and Depression" (osf.io/ctnaq,
    N=831, 82 items)
  - "Assessing Creative Self-Efficacy in the Spanish Workplace" (osf.io/mksw2,
    N=405, BFI-2-S + General Self-Efficacy + 2 Creative Self-Efficacy scales
    — structure already confirmed, ready to process the moment a license
    exists)

- [ ] **Pipeline gap: `.sav`/`.dta`/`.sas7bdat`/`.RData` files are invisible
  to discovery/triage.** `irw_batch_updated.py`'s `TABULAR_EXT` only checks
  `.csv`/`.tsv`/`.xlsx`/`.xls` when resolving a landing page to a data file,
  so any candidate whose only file is SPSS/Stata/SAS/R format gets silently
  flagged `no_usable_file` without ever being opened — even though
  `datastandard.md` lists all of those as supported formats to process.
  Confirmed concretely via figshare 19713625 ("Psychometric properties of
  GS, EGO, 3D-GS grit scales in Chinese adults: A Bifactor IRT study," a
  `.sav`-only deposit that turned out to be a strong candidate — N=896, 6
  named scales — once opened by hand with `pyreadstat`). Likely a source of
  silent false negatives across all 16 batches, not just this one dataset.
  Needs: extend `TABULAR_EXT` handling (and the download/parse logic) to
  cover these formats, `pyreadstat` added to the documented prerequisites,
  and probably a pass at re-discovering `no_usable_file` candidates from
  past batches once fixed. Not yet fixed.
