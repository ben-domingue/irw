# IRW Automated Finding — TODO

Currently open action items only. For the full batch-by-batch history and
context behind these (and everything already resolved), see `BATCH_LOG.md`.

- [x] **PLOS ONE batch 10 — `biblio_plos_batch10.csv` (19 rows) closed out**
  (confirmed 2026-07-30, ben-domingue): 4 papers (`baudin_2024_static99r`,
  `liu_2022_mice_skills`, `alsyouf_2024_*` ×12, `ozkurt_2026_*` ×5, all
  CC BY 4.0) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch10.csv` and all 19 `irw_output/*.csv` files gone from
  disk as expected. `baudin_2024_static99r` was corrected before upload
  (ben-domingue catch): item 1 ("Age at release") is a polytomous
  person-level attribute, not a repeated behavioral response — moved from
  the item block to `cov_age_at_release`, leaving 9 items. See
  `BATCH_LOG.md`'s "PLOS ONE batch 10" entry for full per-dataset detail.

- [x] **`automated_finding/human_review_plos_batch10.csv`** (53 rows,
  batch 10's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-07-30, ben-domingue); file deleted
  from the repo.

- [x] **PLOS ONE batch 10 — `biblio_plos_batch10_worthretrying.csv` (13
  rows) closed out** (confirmed 2026-07-30, ben-domingue): 5 papers from
  the batch 10 `worth_retrying` pass (`mavromoustakos_2016_*` ×3,
  `burns_2018_*` ×4, `bilotta_2018_*` ×2, `petrowski_2019_sclk9`,
  `schalet_2016_*` ×3, all CC BY 4.0) uploaded to Redivis and pasted into
  the dictionary sheet; `biblio_plos_batch10_worthretrying.csv` and all 13
  `irw_output/*.csv` files gone from disk as expected. See `BATCH_LOG.md`'s
  "PLOS ONE batch 10 worth_retrying pass" entry for full per-dataset
  detail, including the 15 skipped (confirmed aggregate-only/not-item-
  response) and 5 deferred (real items, needs codebook time) candidates
  from the same 26-row pool.

- [ ] **PLOS ONE batch 10 — 5 deferred `worth_retrying` datasets need
  codebook-driven follow-up** (2026-07-30): French school-subject
  self-concept study (`10.1371/journal.pone.0230103`, 249 cols, 5 parallel
  ~33-item domain scales, has a DOB/PII column to strip first); Dutch
  self/other/meta-personality study (`10.1371/journal.pone.0272095`, 1086
  cols, multi-rater HEXACO facets); chronic fatigue neuromuscular-strain
  study (`10.1371/journal.pone.0159386`, 187 cols, 5 symptom items across
  many timepoints, a genuine but unmapped wave structure); "Lab meets real
  life" thought-sampling study (`10.1371/journal.pone.0184488`, N=43,
  ambiguous `t0`/`t6`/`DoM`/`ToM` labels not yet explained by the paper
  text); psychosomatic rehabilitation gender-effects study
  (`10.1371/journal.pone.0256916`, 494 cols, cryptic suffixed variable
  names). `plos_batch10_retriage.csv` still holds these rows if picked up
  later.

- [ ] **PLOS ONE batch 9 — 25 `worth_retrying`/`recoverable_format` rows
  still unreviewed** in `plos_batch9_retriage.csv` (see below for detail)
  — older backlog, still open when batch 10 finishes.

- [x] **PLOS ONE pilot — human_review_plos_batch1.csv (184 rows)** pasted
  into the "Human eye" sheet (confirmed 2026-07-26, ben-domingue); file
  deleted from the repo.

- [x] **PLOS ONE pilot — `good` list fully closed out** (2026-07-26,
  ben-domingue): all 32 originally-flagged candidates hand-reviewed, 21
  processed → 46 tables, all uploaded to Redivis and pasted into the
  dictionary sheet (34 in `biblio_plos_batch1.csv`, 12 in
  `biblio_plos_batch2.csv` — both files deleted, content captured in
  `BATCH_LOG.md`). 11 skipped as confirmed aggregate-only/not-item-
  response/too-small (surgical resident QI and couples synchrony
  explicitly deemed too small by ben-domingue at N=14/N=10). See
  `BATCH_LOG.md` for the full list.

- [x] **PLOS ONE pilot — `biblio_plos_batch3.csv` (82 rows) closed out**
  (confirmed 2026-07-27, ben-domingue): pasted into the dictionary sheet,
  82 tables moved for Redivis upload (includes 4 QC-corrected ones, see
  `BATCH_LOG.md`'s "QC spot-check pass"). See `BATCH_LOG.md`'s
  "worth_retrying pass" entries for the full list of what's in this batch.

- [x] **PLOS ONE pilot — `biblio_plos_batch4.csv` (62 rows) closed out**
  (confirmed 2026-07-27, ben-domingue): pasted into the dictionary sheet,
  62 tables uploaded to Redivis.

- [x] **PLOS ONE pilot — `biblio_plos_batch5.csv` (11 rows) closed out**
  (confirmed 2026-07-27, ben-domingue): pasted into the dictionary sheet,
  11 tables uploaded to Redivis. This closes out the entire N≥100
  `worth_retrying` pool end-to-end.

- [x] **PLOS Mental Health + PLOS Global Public Health discovery run
  completed and retriaged (2026-07-28)** — 168 candidates (100
  `mentalhealth` + 68 `globalpublichealth`), same 22 terms as the PLOS
  ONE pilot. 1 `good`, 17 `human_assistance` → retriaged to 4
  `worth_retrying` + 7 `human_review` (rest dropped). Full run/retriage
  details, the network hiccups hit along the way, and the yield
  comparison to PLOS ONE are in `BATCH_LOG.md`'s "PLOS Mental Health +
  PLOS Global Public Health run" entry (2026-07-28).

- [x] **`automated_finding/human_review_plos_mh_gph.csv`** (7 rows)
  pasted into the "Human eye" sheet (confirmed 2026-07-28, ben-domingue);
  file deleted from the repo.

- [ ] **Decision (ben-domingue, 2026-07-28): backburner PLOS Mental
  Health/Global Public Health, refocus on PLOS ONE.** 1 `good` + 4
  `worth_retrying` candidates from the run above are parked, not
  processed, in favor of returning to the PLOS ONE sub-100
  `worth_retrying` tail below. `plos_mh_gph_triage.csv` (the full
  168-row file) disappeared from disk mid-session (2026-07-28) — same
  Dropbox-sync file-loss pattern as the 2026-07-26 incident noted below,
  not a script bug. DOI/URL/n/items for the 5 parked candidates below are
  preserved here; `plos_mh_gph_retriage_ha.csv` (17 rows, full columns
  incl. license/data_availability) survived and still exists. If the
  full triage file is needed again, DOIs are known and re-running
  `process_one` on them directly is cheap. Parked candidates:
  - **`good`**: "The impact of parkrun on life satisfaction and its
    cost-effectiveness" (`globalpublichealth`, 10.1371/journal.pgph.0003580)
  - **`worth_retrying`**: "Depressive symptoms and its associated
    factors among secondary school..." (271p/5i,
    10.1371/journal.pgph.0002826); "Child maltreatment mediates the
    relationship between HIV/AIDS family..." (285p/228i,
    10.1371/journal.pgph.0001599); "Health care needs survey to improve
    preparedness of community outreach..." (187p/146i,
    10.1371/journal.pgph.0005204); "The effect of biomass smoke exposure
    on quality-of-life among Ugandan..." (1626p/2i,
    10.1371/journal.pgph.0002892)

- [x] **PLOS ONE pilot — entire `worth_retrying` N≥100 pool (81 candidates)
  fully reviewed** (2026-07-27) — every candidate processed or explicitly
  skipped with reasons in `BATCH_LOG.md`. Filtered from 107 to 81 at
  N≥100 per ben-domingue's direction (2026-07-26).

- [x] **PLOS ONE pilot — sub-100 `worth_retrying` tail (26 candidates)
  dropped, not pursued** (ben-domingue, 2026-07-28): too small (N<100
  each) to be worth the review time. `plos_full_triage.csv` /
  `plos_full_retriage.csv` still hold these rows if reconsidered later,
  but no longer block anything. The fresh PLOS ONE discovery pass with
  new search terms this note called for has since run — see batch 6
  below.

- [x] **PLOS ONE batch 6 — `biblio_plos_batch6.csv` (24 rows) closed out**
  (confirmed 2026-07-28, ben-domingue): all 24 tables from the
  15-candidate `good` review — 8 papers (bled_2021 ×2, ruiz_parra_2023
  ×9, najari_2024_bpqsf ×3, odachi_2022 ×3, zhao_2024_erq ×1, li_2021 ×4,
  kang_2015 ×1, ly_2021 ×1) — uploaded to Redivis and pasted into the
  dictionary sheet; `biblio_plos_batch6.csv` and all 24 `irw_output/*.csv`
  files gone from disk as expected.

- [x] **`automated_finding/human_review_plos_batch6.csv`** (89 rows,
  batch 6's `human_review` rows) pasted into the "Human eye" sheet
  (confirmed 2026-07-29, ben-domingue); file deleted from the repo.

- [x] **PLOS ONE batch 6 — `biblio_plos_batch7.csv` (12 rows) closed out**
  (confirmed 2026-07-28, ben-domingue): 12 tables from 8 of the 48
  `worth_retrying` rows (baumgaertner_2018, huang_2016 ×3, grant_2018,
  laksmita_2020, rosharudin_2023 ×2, turner_2022 ×2, gomez_2022,
  yang_2015) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch7.csv` and the 12 `irw_output/*.csv` files gone from
  disk as expected. Before upload, two issues were caught and fixed in
  review (see `BATCH_LOG.md`'s "Retracted after initial processing" and
  the `yang_2015` isolated-data-entry-error fix): a 13th table
  (`stenson_2021_sleep_emotion`) was retracted entirely — its "Rating"
  column was a derived mean/contrast score across trials, not a raw
  per-trial response, per the paper's own Methods text — and
  `yang_2015_ethnic_essentialism` had one isolated non-integer value
  (3.75 on a single item/respondent) dropped as a data-entry error. Both
  findings prompted new standing checks added to `datastandard.md`
  ("Verifying a continuous-looking column is actually a raw response"
  and "Checking for imputed values" — the latter checks the source
  paper's text for imputation language, since non-integer screening alone
  doesn't catch every imputation method).

- [ ] **PLOS ONE batch 6 — 2 datasets need codebook-driven follow-up work
  (deferred from the worth_retrying pass, 2026-07-28)**: the coping-self-
  efficacy/sex-trafficking study and the full-body-mirror-exposure
  eating-pathology study both have genuine multi-wave raw items (MSPSS,
  CopSE, EDE-Q, PANAS) but need careful per-scale wave-column work beyond
  what this pass had time for. DOIs and column details in `BATCH_LOG.md`.

- [ ] **PLOS ONE batch 6 — 3 datasets have real items but ambiguous
  subscale identity** (deferred, 2026-07-28): insight-in-schizophrenia
  study (bare "C1-5"/"S1-10"/"M1-12"/VAGUS blocks, no codebook to name
  them), Brazilian smoking/FFMQ study (huge multi-scale file, needs
  filtering out extensive derived-transform columns and identifying
  ambiguous A/B/C blocks), and 1 `recoverable_format` row in
  `plos_batch6_retriage.csv` (a semicolon-delimited PsyCap file) not yet
  re-triaged with `sep=';'`.

- [ ] **PLOS ONE batch 6 — remaining `worth_retrying` rows not
  individually reviewed** (`plos_batch6_retriage.csv`, 2026-07-28): rows
  where duplicate ids are near-clean (a handful of likely-exact-duplicate
  rows needing a dedup decision) and rows where the first column is
  confirmed not to be a real person id (true id column, if any, not yet
  located). ~26 rows total; see `BATCH_LOG.md` for the full accounting of
  what was and wasn't looked at.

- [ ] **Carver 2017 PUGGS genetics-belief questionnaire
  (`10.1371/journal.pone.0169808`) needs a codebook-driven processing
  script** — flagged `good` in batch 6 but not processed: two pilot
  samples (N=207, N=78), each spanning a belief-in-determinism subscale
  (1-6/1-5 Likert with a "don't know" sentinel) and a true/false
  genetics-knowledge subscale (needs a per-item answer-key recode to
  correct/incorrect per the codebook). Both DOCX codebooks are already
  downloaded and read (see `BATCH_LOG.md`); the recode logic is
  understood, just not yet implemented as a script.

- [ ] **Meloni 2015 disability-representations study
  (`10.1371/journal.pone.0128876`) needs a codebook-driven processing
  script** — flagged `good` in batch 6 but not processed: 244-column SI
  file with ~8 distinct item families (open-ended disability-attribution
  codes, 5×12 fictional-character rating blocks, a knowledge scale,
  interest/attitude scales with paired response-time columns,
  extracurricular-activity items). Tractable but needs more per-block
  codebook time than the batch 6 pass had.

- [x] **PLOS ONE pilot — all 34 tables from the first pass uploaded and
  biblio-entered** (confirmed 2026-07-26, ben-domingue): first 7
  (muslih_2024_rses, jiang_2021_resilience, kinyanjui_2023_substance_use,
  wilson_2022_kelpie_personality, rashid_2022_mbi, yin_2022_gad7,
  yin_2022_values_importance) plus the remaining 27 (kraft_todd_2017 ×4,
  song_2023 ×3, di_riso_2025 ×2, iwasa_2016 ×4, hui_2024 ×3, liu_2018 ×5,
  uffler_2017 ×2, nabwera_2021 ×1, lu_2017 ×3) all uploaded to Redivis and
  pasted into the dictionary sheet. `biblio_plos_batch1.csv`,
  `biblio_plos_batch1_remaining27.csv`, and all 34 `irw_output/*.csv`
  files deleted from the repo — content fully captured in the sheets and
  in `BATCH_LOG.md`. This first pass of the PLOS ONE pilot is closed out
  end-to-end.

- [ ] **Note on this working directory**: `automated_finding/` lives inside
  a Dropbox-synced folder. Twice during the 2026-07-26 PLOS session, files
  written here (a `biblio_*.csv` append, and 7 `irw_output/*.csv` tables)
  disappeared from disk with no git record — most likely a Dropbox sync
  event from another device overwriting/reverting local changes mid-edit,
  not a bug in the processing scripts themselves (all source `.py` scripts
  in `data/` were untouched and the CSVs regenerated cleanly). If output
  files or biblio rows look incomplete partway through a session, check
  whether they simply need regenerating from the `data/*.py` script before
  assuming the underlying data/logic was wrong.

- [ ] **Gyurkovics/Stafford/Levita conflict-task dataset (osf.io/7vbtr)** —
  by far the strongest find from the batch-18 conflict-task search: trial-
  level Flanker + Simon + SART(go/no-go) data, N=118, fully documented,
  directly relevant to the user's Hedge/Powell/Sumner reliability-paradox
  vignette. Blocked purely on a missing OSF license (no license set on the
  node at all). **ben-domingue emailed the authors 2026-07-17 requesting
  permission — awaiting response.** See `license_blocked_candidates.csv`
  (batch 18 row) for contributor OSF profiles/ORCID. Ready to process the
  moment permission or a license appears.

- [x] **`automated_finding/human_review_conflict.csv`** (1 row: "Stroop test
  dataset", DVN/GINKMU) pasted into the "Human eye" sheet (confirmed
  2026-07-28, ben-domingue); file no longer on disk. CC0, real trial-level
  Stroop latency/accuracy columns appear to be present but buried in a
  ~700-column undocumented Russian-language child-development survey with
  no codebook found — still needs a person to decode the column scheme
  (or locate the source paper) before it can be extracted. See
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

- [x] **`automated_finding/human_review_lang_pilot.csv`** (1 row: SWAN
  depression/lifestyle data, DVN/HWMJAE) pasted into the "Human eye" sheet
  (confirmed 2026-07-28, ben-domingue); file no longer on disk. See
  `BATCH_LOG.md`'s "Non-English per-language discovery pilot" entry for
  why it couldn't be resolved automatically (real longitudinal item data,
  but the 4 items may span two different SWAN questionnaire modules —
  needs SWAN-codebook access to confirm).

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

- [x] **`automated_finding/human_review_cognitive_tasks.csv`** (17 rows,
  from batch 19's cognitive/decision-making-task search) pasted into the
  "Human eye" sheet (confirmed 2026-07-28, ben-domingue); file no longer
  on disk. Included 2 notable cases worth a second look:
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

- [x] **Pipeline improvement: `coerce_to_irw()`/`load_table()` gave up too
  early on two specific, recurring, recoverable patterns — fixed
  2026-07-30.** Found auditing the "Human eye" queue sheet: every row a
  human has ever marked eligible from it (13/13, including issues
  #1559–#1565) failed triage with the exact same reason, "Could not
  confidently identify item columns," and in every case the file was real,
  usable item-response data defeated by (a) a header row that isn't row 0
  (Qualtrics/journal-supplement exports — also hit repeatedly in past PLOS
  batches, see `cormier_2024_*`/`jordan_2020_*` in `BATCH_LOG.md`) or (b)
  item columns whose headers are the literal (often non-English) question
  text with Likert responses stored as text labels rather than numeric
  codes, which `_ordinalish()` doesn't recognize. Full writeup in
  `README.md`'s Step 1b note. Fixed:
  - `load_table()` now detects a header-offset read (>50% `Unnamed:`
    columns) and retries `header=1..4` before accepting a broken table —
    see `_looks_header_offset()`. Only fires when the default read already
    looks broken, so it can't change a working read.
  - `coerce_to_irw()`'s Case C now checks excluded columns for text-coded
    Likert categories (`_textish_likert()`) before giving up, and notes it
    explicitly rather than folding it into the generic "could not identify
    item columns" message. Detection only, deliberately not auto-recoded —
    category set/direction still needs a human, same as datastandard.md
    already requires for numeric `resp` columns.
  - `irw_retriage_ha.py` gained a rule (before RULE 7) that routes this new
    note to `worth_retrying` instead of the `human_review` catch-all, so
    it surfaces ahead of genuinely ambiguous rows next retriage run.
  Not yet re-run against a live batch to confirm real-world recovery rate —
  worth checking next time `human_assistance` rows come through.

- [ ] **Trusz 2025 NFI dataset (`DVN/DWCBOE`) has unprocessed CFA (N=437)
  and test-retest-stability (N=54) subsamples** beyond the EFA sample
  already processed as `trusz_2025_nfi`. Not picked up because the
  combined N=1097 file mixing all sub-studies has an unreliable id column;
  would need per-file (not per-combined-file) processing. Low priority —
  noted for whoever wants the extra ~500 respondents.

- [x] **`knight_2026_crt`** (2026-07-29, one-off user-supplied lead, not
  from batch discovery) pasted into the dictionary sheet and uploaded to
  Redivis (confirmed 2026-07-29, ben-domingue). Processed from Knight et
  al. (2026, *Psychological Science*) — double-blind RCT of intranasal
  testosterone vs. placebo on the 7-item Cognitive Reflection Test, OSF
  node `37ycj` (`TED_CRT_longdata.csv`), CC0. Script:
  `data/knight_2026_crt.py`. Output was `irw_output/knight_2026_crt.csv`
  (6,993 rows, 999 ids, 7 items, resp 0/1, treat 0/1, rt in seconds —
  back-transformed from the source's natural-log RT via `exp()`, verified
  against Qualtrics `Page Submit` timing elsewhere in the same raw dataset,
  which is natively in seconds). `biblio_knight_2026_crt.csv` deleted from
  the repo.

- [x] **PLOS ONE batch 8 discovered and processed** (confirmed 2026-07-29,
  ben-domingue): fresh discovery run (`irw_discover_plos.py`, 30 new
  instrument/task terms not previously searched, e.g. HEXACO, Cognitive
  Reflection Test, Ultimatum Game; logged in `search_terms_log.csv`).
  1,500 candidates -> 7 `good` + 261 `human_assistance`. Retriage
  (`irw_retriage_ha.py`) on the `human_assistance` bucket gave 42
  `worth_retrying` + 1 `recoverable_format` + 80 `human_review` + 91
  `aggregate_continuous` + 47 `not_item_response`. All 43
  `worth_retrying`/`recoverable_format` rows and all 7 `good` rows were
  downloaded and hand-inspected (see "Batch 8 worth_retrying triage" and
  "Batch 8 good-candidate review" in `BATCH_LOG.md` for the per-row
  calls). 11 papers processed -> 40 tables — `lorenz_2016` (PsyCap
  CPC-12, 7 tables), `sleboda_2021_risk_benefit`, `tiemensma_2018_iesr`,
  `alsuhibani_2022` (conspiracy/paranoia, 3 studies, 10 tables —
  LOC/SERS/GCBS merged across studies confirmed identical by the paper's
  own Methods text, ids offset per study; see `datastandard.md`'s new
  "same instrument administered to multiple sub-studies" edge case, added
  this session), `niazi_2020_moral_foundations` (2 tables),
  `kim_2025_presleep_arousal` (4 tables), `luo_2021_acculturation` (5
  tables), `reinecke_2018_online_vigilance`, `queiros_2018_qcae`,
  `esiason_2024_nmosd` (patients+caregivers merged same way as
  `alsuhibani_2022`, 7 tables), `addy_2021_sdq_ghana`. All 40 output
  files passed the per-item rare-value data-entry-error scan and
  ben-domingue's review; `biblio_plos_batch8.csv` and all 40
  `irw_output/*.csv` files are being removed from disk as expected
  (pasted into the dictionary sheet / uploaded to Redivis).

- [x] **`automated_finding/human_review_plos_batch8.csv`** (80 rows,
  batch 8's `human_review` rows) pasted into the "Human eye" sheet
  (confirmed 2026-07-29, ben-domingue); file deleted from the repo.

- [ ] **PLOS ONE batch 8 — 3 datasets still deferred** (need more
  codebook/wave-column time than any pass so far): Clinton-voter activism
  longitudinal study (`10.1371/journal.pone.0221754`, real CESD +
  Activist items across waves, T1a/T1b/Wave coding needs care); Chinese
  EFL learning study (`10.1371/journal.pone.0280919`, real items but
  Chinese-text Likert labels need recoding + a 481-vs-942-row mismatch to
  resolve); emotional-eating chain-mediation study
  (`10.1371/journal.pone.0280701`, real EES-R/CES-D/DERS bundle but item
  blocks are cryptically labeled `@10.`/`@11.` etc., needs matching to
  instruments).

- [x] **PLOS ONE batch 8 — VR-empathy and phonological-loop deferred
  datasets resolved** (confirmed 2026-07-29, ben-domingue) — the "second
  closer look" both turned out to be quick once checked against the
  papers' Methods text. `herrera_2018_vr_empathy.py`
  (`10.1371/journal.pone.0204494`) -> 4 tables:
  `herrera_2018_iri`/`_beliefs_about_empathy` (merged across the paper's
  2 studies, confirmed identically administered, ids offset per study),
  `_attitudes_homeless`/`_se_d_items` (Study 2 only). Two more candidate
  tables (`_ios`, `_dehumanization`) were caught in review as single-item
  measures and dropped — IRW does not accept single-item scales
  regardless of data quality (new standing rule, see memory
  `feedback_no_single_item_scales`). `meng_2017_referent_assignment.py`
  (`10.1371/journal.pone.0187368`) -> 1 table: the triage-flagged
  `Base-Assignment`/`Shift`/`Re-Assignment`/`Follow-RA` columns turned
  out to be derived composites (each an AND of two raw scores, per the
  paper's own coding description) rather than raw items — the actual
  5 raw per-trial correctness scores (`EQ`/`AQ`/`EQ2`/`AQ2`/`AQ3`) were
  used instead, with a `wave` column encoding the block/trial order (74
  children x 4 trials). All 5 output files uploaded to Redivis;
  `biblio_plos_batch8_deferred.csv` pasted into the dictionary sheet and
  being removed from disk as expected.

- [x] **PLOS ONE batch 9 discovered, triaged, and 5 of 7 `good` candidates
  processed** (confirmed 2026-07-29): 28 new terms, 1,261 candidates -> 7
  `good` + 184 `human_assistance`. 5 papers processed -> 9 tables
  (`xiong_2025_dass21`, `su_2025_health_behaviors`, `wakui_2023_who5`,
  `liu_2025_mlq`/`_positive_cognition`/`_learning_motivation`,
  `zamzuri_2021_rpap_risk_perception`/`_attitude`/`_practice`); 1 skipped
  (SoroTouch, N=10 derived engagement metrics, not raw items); 1 deferred
  (situational-motivation EMA, ambiguous item structure -- see below). Full
  per-dataset reasoning in `BATCH_LOG.md`'s "PLOS ONE batch 9" entry. All 9
  `irw_output/*.csv` files uploaded to Redivis and removed from disk
  (confirmed 2026-07-29, ben-domingue).

- [x] **`automated_finding/biblio_plos_batch9.csv`** (9 rows) pasted into
  the dictionary sheet (confirmed 2026-07-29, ben-domingue); file deleted
  from the repo. Re-staged as plain comma-delimited CSV after a same-day
  tab-delimited/xlsx detour was tried and reverted -- see `BATCH_LOG.md`
  and memory `feedback_dict_format` for why.

- [x] **`automated_finding/human_review_plos_batch9.csv`** (63 rows,
  batch 9's `human_review` rows from `irw_retriage_ha.py`) pasted into the
  "Human eye" sheet (confirmed 2026-07-29, ben-domingue); file deleted
  from the repo.

- [ ] **PLOS ONE batch 9 — 25 `worth_retrying`/`recoverable_format` rows
  not yet hand-reviewed** (2026-07-29), still in `plos_batch9_retriage.csv`:
  `10.1371/journal.pone.0199480` (body image/eating behavior/QoL, N=2096,
  65 items), `10.1371/journal.pone.0206800` (Multidimensional Social
  Competence Scale validation, N=734, 40 items), `10.1371/journal.pone.0169375`
  (exercise behavior in Chinese cancer patients, N=350, 138 items),
  `10.1371/journal.pone.0202818` (trust/psychological distress, urban poor
  Accra, N=788, 5 items), `10.1371/journal.pone.0322635` (exercise/
  emotional eating/body dissatisfaction SEM, N=903, 8 items), plus 19 more
  smaller-N rows and 1 `recoverable_format` (semicolon-delimited body-
  esteem/diabetes file, `10.1371/journal.pone.0263766`). See
  `BATCH_LOG.md` for the full list with n/items.

- [ ] **PLOS ONE batch 9 — situational-motivation EMA study deferred**
  (`10.1371/journal.pone.0307369`, 2026-07-29): genuine event-contingent
  repeated-measures design (22 people, 519 sessions over 10 weeks,
  pre-/post-activity self-reports), but the triage-flagged "2 items" are
  actually two multi-rating report *modules*, not two Likert items --
  needs the raw S1 Data file opened and the per-session item structure
  mapped out before it can be shipped.

