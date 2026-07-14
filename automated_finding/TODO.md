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

- [ ] **Batch 15 wrap-up** — Redivis upload for 4 new tables in
  `automated_finding/irw_output/` (chowdhury2026 x3, nelson2019 x1), and
  biblio sheet entries from `/tmp/biblio_batch15.csv` (4 rows). Also paste
  `human_review_batch15.csv` (26 rows) into the "Human eye" sheet if not
  already done.
