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

- [ ] **Batch 17 wrap-up** — biblio sheet entries confirmed live in the
  dictionary (2026-07-14). `human_review_batch17.csv` (5 rows,
  `automated_finding/human_review_batch17.csv`) is still sitting locally,
  unlike batches 15/16's — not deleted yet, so not assuming it's been
  pasted into the "Human eye" sheet. Paste it and delete the file when done.

- [ ] **Re-discover past `no_usable_file` candidates now that `.sav`/`.dta`/
  `.sas7bdat`/`.RData` support is fixed** (2026-07-14 — `TABULAR_EXT` in
  `irw_batch_updated.py` extended, `load_table()` in `irw_triage_updated.py`
  now parses all four via `pd.read_spss`/`pd.read_stata`/`pd.read_sas`/
  `pyreadr`, verified end-to-end against figshare 19713625 which now
  correctly triages as `human_assistance` — N=896, 6 named scales — instead
  of silently vanishing as `no_usable_file`). The fix only helps *future*
  discovery runs; every candidate flagged `no_usable_file` in batches 1-17
  needs re-checking, since some unknown fraction of those 200-900-per-batch
  rows were SPSS/Stata/SAS/R files rejected before this fix, not genuinely
  unusable. No mechanism exists yet to re-run triage against old candidate
  lists (they were deleted per the temp-file cleanup convention) — would
  need either saved candidate URLs or a fresh discovery pass per past search
  term to recover them.
