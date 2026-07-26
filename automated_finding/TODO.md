# IRW Automated Finding — TODO

Currently open action items only. For the full batch-by-batch history and
context behind these (and everything already resolved), see `BATCH_LOG.md`.

- [ ] **Gyurkovics/Stafford/Levita conflict-task dataset (osf.io/7vbtr)** —
  by far the strongest find from the batch-18 conflict-task search: trial-
  level Flanker + Simon + SART(go/no-go) data, N=118, fully documented,
  directly relevant to the user's Hedge/Powell/Sumner reliability-paradox
  vignette. Blocked purely on a missing OSF license (no license set on the
  node at all). **ben-domingue emailed the authors 2026-07-17 requesting
  permission — awaiting response.** See `license_blocked_candidates.csv`
  (batch 18 row) for contributor OSF profiles/ORCID. Ready to process the
  moment permission or a license appears.

- [ ] **`automated_finding/human_review_conflict.csv`** (1 row: "Stroop test
  dataset", DVN/GINKMU) — needs pasting into the "Human eye" sheet. CC0,
  real trial-level Stroop latency/accuracy columns appear to be present but
  buried in a ~700-column undocumented Russian-language child-development
  survey with no codebook found — needs a person to decode the column
  scheme (or locate the source paper) before it can be extracted. See
  `BATCH_LOG.md`'s "Batch 18" entry.

- [ ] **Political Preference China** (`10_7910_dvn_dwplbc.csv`, DVN/dwplbc) — on
  hold: 0-response ambiguity, anchor labels not documented in the source.
  Needs the anchor-label question resolved before it can be processed.

- [ ] **SAPA 7 annual releases** (2017–2024, DOIs DVN/PNGUT5 through
  DVN/3BTT82, all CC0, none in IRW yet) — decision needed on scope: process
  all 7 years separately, most recent only, or pool with `cov_year`. File
  IDs and format details are in `BATCH_LOG.md`'s "Pipeline improvements"
  section.

- [ ] **`human_review` backlog** — several hundred rows accumulated across
  all batches, tracked in the "Automated queue - Human eye" Google Sheet
  (not in this repo). Needs a person to periodically review and either
  process or dismiss entries.

- [ ] **17 OSF candidates blocked only on missing license** (not a content
  problem — see `automated_finding/license_blocked_candidates.csv` for full
  detail: URL, N/items, contributors. Worth an author-permission email per
  `processing_notes/Licensing.txt` if someone wants to pursue them). Three
  are structurally confirmed and ready to process the moment a license
  appears: "The Role of Attentional Bias in Anxiety and Depression"
  (osf.io/ctnaq, N=831, 82 items), "Assessing Creative Self-Efficacy in the
  Spanish Workplace" (osf.io/mksw2, N=405, 4 scales), "Rosenberg Self-Esteem
  Scale in Uruguay" (osf.io/h5g36, N=322, 11 items). The other 14 are
  logged with title/URL/contributors but not yet structurally inspected —
  see the CSV for the full list.

- [ ] **6 items sitting in the "Human eye" sheet from the English-terms
  backlog**, needing a person (not another automated attempt): `DVN/HIT56P`
  (no id column, needs cross-file linkage across baseline/followup waves),
  `DVN/S0HEZI` (unredacted PII in every row — real name/email/IP/GPS),
  `figshare 32953286` (mixed item types — usage flags + vignettes +
  derived scores), the Caring Efficacy Scale's unidentified second 13-item
  block (figshare 8177303, alongside the already-processed
  avilesgonzalez2019_ces), `osf.io/zc3pf` (Academic Free License 3.0 — not
  a standard accepted type, needs a call on whether it's acceptable), and
  PIRLS 2023 (University of Pretoria's Figshare instance, bot-blocked,
  needs manual browser access). Full story of how these were found in
  `BATCH_LOG.md`'s "Finishing the 32-candidate backlog" entry.

- [ ] **`automated_finding/human_review_lang_pilot.csv`** (1 row: SWAN
  depression/lifestyle data, DVN/HWMJAE) — needs pasting into the "Human
  eye" sheet; see `BATCH_LOG.md`'s "Non-English per-language discovery
  pilot" entry for why it couldn't be resolved automatically (real
  longitudinal item data, but the 4 items may span two different SWAN
  questionnaire modules — needs SWAN-codebook access to confirm).

- [ ] **Portella 2022 racial-attitudes dictionary/tags fix needs pasting in**
  (`automated_finding/dictionary_fix_portella_2022.csv`,
  `automated_finding/tags_fix_portella_2022.csv`) — replaces the existing
  `racialsocialnormsbrazilianstudents_portella_2022` row (broken processing
  script, never actually live; see `BATCH_LOG.md`'s "User-directed fix"
  entry, 2026-07-16) with a `portella_2022_racial_attitudes` row. Once
  pasted, `irw_output/portella_2022_racial_attitudes.csv` is ready to upload
  to Redivis.

- [ ] **Peters 2025 COVID-19 Risk Tool (issue #1093) — follow-up pass on the
  remaining ~300 raw columns.** Main 16 DCT belief-item tables are fully
  processed, tagged, dictionary-entered, and uploaded to Redivis
  (ben-domingue confirmed 2026-07-17; see `BATCH_LOG.md`). Not yet covered:
  the risk-estimate/checkbox-array family — `siCurrent*`/`siIntention*`/
  `hwFrequency*`/`work*`/`DMQslider*` and their paired `*Est` columns — uses
  a different, not-yet-decoded response mechanism.

- [ ] **`automated_finding/human_review_cognitive_tasks.csv`** (17 rows,
  from batch 19's cognitive/decision-making-task search) — needs pasting
  into the "Human eye" sheet. Includes 2 notable cases worth a second look:
  the Nosek & Smyth (2011) math-IAT dataset (DVN/Z3MV4J, N=11,819 — real
  data, needs the paper's PDF codebook to decode 186 cryptic columns safely)
  and the LGBTQ-judges conjoint experiment (DVN/CDLVDH, N=1,249 — a genuine
  conjoint design where the judge-profile attributes are randomized per
  response, conflicting with datastandard.md's itemcov invariance rule; a
  person needs to decide whether to ship a bare id/item/resp file without
  the attribute detail, or treat conjoint designs as out of scope). See
  `BATCH_LOG.md`'s "Batch 19" entry for the full reasoning on all 17 rows.

- [ ] **Pipeline improvement: no file-size guard in `irw_batch_updated.py`.**
  Batch 19 hit a Dataverse candidate (`DVN/BRCRS5`) whose files were six
  `.dta` files up to 1.4GB each — loading it OOM-killed the triage process
  twice (~21GB RSS on a 30GB machine) before it was manually excluded and
  the run resumed. Batch 20 hit the identical failure mode again
  (`DVN/EHBGOW`, six `.dta` files up to 1.58GB each) — now two batches in a
  row. Worth adding a size check (e.g. via each repo API's reported file
  size, skip/flag anything over some threshold without a full download) so
  this fails gracefully instead of silently killing the process. Not done —
  no one has picked this up yet.

- [ ] **Trusz 2025 NFI dataset (`DVN/DWCBOE`) has unprocessed CFA (N=437)
  and test-retest-stability (N=54) subsamples** beyond the EFA sample
  already processed as `trusz_2025_nfi`. Not picked up because the
  combined N=1097 file mixing all sub-studies has an unreliable id column;
  would need per-file (not per-combined-file) processing. Low priority —
  noted for whoever wants the extra ~500 respondents.

