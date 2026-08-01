# IRW Automated Finding — TODO

Currently open action items only. For the full batch-by-batch history and
context behind these (and everything already resolved), see `BATCH_LOG.md`.

- [x] **"Human eye" batch — 5 new tables pasted into the dictionary sheet**
  (confirmed 2026-08-01, ben-domingue): `iandolo_2021_asq`,
  `dasilva_2019_hexaco24`, `mendes_2019_snycq`, `tutrin_2020_meq30`,
  `lee_2025_nursing_exam` (combined with the batch 14 rows below into
  `biblio_batch_20260801.csv`, then pasted); `biblio_humaneye_batch1.csv`,
  `biblio_plos_batch14.csv`, `biblio_batch_20260801.csv`, and all
  `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "'Human eye' sheet review follow-through" entry for how
  each was found and what was checked.

- [ ] **Bug found in already-shipped `yandun2026_language`/
  `yandun2026_logical_thinking` tables (batch 3) — need reprocessing**
  (found 2026-08-01, while checking a "human eye" Yes-row candidate that
  turned out to be a duplicate of this same dataset): `data/
  yandun2026_cognitive.py`'s column boundaries are off by one — the
  `language` subscale wrongly includes "Relates numbers with clues" (a
  Logical Thinking item per the source header's own group-boundary row),
  and `logical_thinking` is missing it (3 items instead of the true 4).
  Fix the `SUBSCALES` column ranges in that script (language should be
  cols 14-17, logical_thinking cols 18-21, 0-indexed after header-strip),
  regenerate both CSVs, and re-upload to Redivis. See `BATCH_LOG.md` for
  the exact column-header evidence.

- [ ] **Nominal/competitions experimental-standard candidates — shortlisted,
  license/structure-screened, and deduped against the existing
  nominal/competitions table sheets — not yet downloaded or converted**
  (2026-08-01, one-off search, not a standing priority — see
  `BATCH_LOG.md`'s "Nominal / competitions experimental-standard search"
  entry, including its dedup-check addendum, for full detail and memory
  `project_alt_data_standards` for the schema criteria).
  `candidates_nominal_shortlist.csv` (57 rows) and
  `candidates_competitions_shortlist.csv` (53 rows) are keyword-filtered
  from the full 6911/6078-row discovery files. **The dedup check caught
  one exact duplicate already live in IRW (`zucco2019_portfoliosalience`,
  DVN/HJZSIM) and several already-covered domains (chess via `lichess`,
  League of Legends via `league_of_legends`, football via
  `eufootball_2010-2020`, ASAP-lineage essay corpora via `asap20train`) —
  those candidates are downgraded, not dropped from the shortlist files.**
  Strongest surviving next candidates to actually download and convert:
  nominal — Self-Coding open-ended survey data (Dataverse DVN/E4AJZF,
  **CC0**, best-confirmed fit, non-overlapping domain) and COS101
  open-ended exam responses (Figshare, CC BY 4.0, also non-overlapping);
  competitions — World Padel Tour match history (Zenodo 7860242, CC BY
  4.0, padel is not an already-covered sport). One dataverse candidate
  (`DVN/J9KSHU`) is license-blocked (CC BY-NC-SA). Needs someone to
  actually open the files, confirm id/item/text or agent_a/agent_b/score
  structure, and write bespoke processing scripts (normal
  `irw_batch_updated.py` triage does not apply to either standard).

- [x] **PLOS ONE batch 14 — `dejesus_2017_{lequesne,sf36,womac,gpm}` pasted
  into the dictionary sheet** (confirmed 2026-08-01, ben-domingue, from the
  continuous/bounded response-scale search): Lopes de Jesus et al. (2017)
  intra-articular ozone knee-OA RCT (10.1371/journal.pone.0179185), CC BY
  4.0, N=98 x up to 4 waves — see the "Human eye" batch entry above for the
  combined biblio file used. See `BATCH_LOG.md`'s "PLOS ONE batch 14" entry
  for full detail.

- [ ] **`automated_finding/human_review_plos_batch14.csv`** (12 rows, batch
  14's `human_review` rows from `irw_retriage_ha.py`) — needs pasting into
  the "Human eye" sheet.

- [ ] **PLOS ONE batch 14 — dairy tie-stall housing survey deferred**
  (10.1371/journal.pone.0216544, 2026-08-01): two clean between-subjects
  samples (S1 N=430, S2 N=372), each with 6 genuine 1-7 Likert belief items
  (`b1_morerisky/lowerquality/harmenviro`, `b2_borganic/bfamfarm/
  bsmallfarm`) plus 3 more (`has1-3`) of unclear relationship to the rest —
  needs the paper's item wording to confirm whether this is one 9-item
  battery or 2-3 separate subscales before it can be split into file(s)
  correctly. `plos_batch14_retriage.csv` still holds this row.

- [ ] **PLOS ONE batch 14 — Auricular Acupuncture exam-anxiety study
  deferred, low priority** (10.1371/journal.pone.0168338, 2026-08-01):
  N=44, mostly physiological/composite STAI-subscale readings across 3
  conditions plus a few `vas_*` items — small sample, needs more untangling
  than this pass had time for. `plos_batch14_retriage.csv` still holds this
  row.

- [ ] **Continuous/bounded-response repo-based discovery (Batch 21) in
  progress** (started 2026-08-01): same 32-term list as PLOS batch 14 (see
  above), translated into 8 languages (256 additional queries), run against
  `irw_discover_updated.py`'s repository connectors (Dataverse/Zenodo/OSF/
  Dryad/Figshare/DataCite/Scholars Portal/SURF). English run
  (`candidates_continuous_en.csv`) and multilingual run
  (`candidates_continuous_intl.csv`) still need merging, triaging, and
  reviewing. Check `BATCH_LOG.md` for whether this finished in the same
  session it was started or needs picking up.

- [ ] **Large pool of recyclable PLOS search terms still unused** (found
  2026-07-30): batches 1–11 always invented fresh instrument names for
  PLOS ONE discovery without checking whether a term had already proven
  itself against a *different* source (Dataverse/Zenodo/OSF/etc.) in
  `search_terms_log.csv` — those are a different search surface from PLOS,
  so reusing them isn't a duplicate query, and they're already-validated
  real instrument/construct/task names rather than guesses. Filtering
  `search_terms_log.csv` to non-PLOS, English-only rows not yet tried
  against PLOS turned up ~1,200 candidates in one pass; batch 12
  (2026-07-30) used 30, batch 13 (2026-07-31) used 30 more, leaving
  ~1,140 unused. See `SKILL.md`'s "Alternate discovery source:
  single-journal search (PLOS ONE)" section (term-selection bullet) for
  the exact filtering method. Expect several more batches' worth of
  higher-quality-than-average terms before this pool runs dry — pull from
  it before brainstorming new terms in future PLOS batches.

- [x] **PLOS ONE batch 13 — `biblio_plos_batch13.csv` (7 rows) closed
  out** (confirmed 2026-08-01, ben-domingue): `nelson_2019_ipqrde`,
  `hermans_2015_dm1_rods`, `liu_2025_classroom_interaction`,
  `_willingness_communicate`, `_speaking_selfefficacy`,
  `_foreign_lang_enjoyment`, `wang_2015_donation_decision` (all CC BY
  4.0) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch13.csv` and all 7 `irw_output/*.csv` files gone from
  disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 13" entry for
  full per-dataset detail.

- [x] **`automated_finding/human_review_plos_batch13.csv`** (92 rows,
  batch 13's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-08-01, ben-domingue); file deleted
  from the repo.

- [ ] **PLOS ONE batch 13 — 72 `worth_retrying` rows not yet
  hand-reviewed** (2026-07-31), still in `plos_batch13_retriage.csv` —
  same pattern as prior batches' worth_retrying passes, not yet started.

- [ ] **PLOS ONE batch 13 — 3 deferred `good`-flagged datasets need more
  time** (2026-07-31): imitation task (`10.1371/journal.pone.0235595`,
  N=124) has a genuine 3-item binary imitation scale but the raw sheet's
  exclusion-flag column has a multi-block layout issue needing manual
  inspection; illusory-body-ownership embodiment questionnaire
  (`10.1371/journal.pone.0277080`, N=30) has a genuine 7-item scale x 4
  conditions but one item shows an out-of-range value and the actual
  questionnaire statement text still needs pulling from the paper;
  situational-motivation EMA (`10.1371/journal.pone.0307369`) is the same
  unresolved candidate from batch 9 (see below), flagged `good` again.
  `plos_batch13_retriage.csv` / `plos_batch13_triage.csv` still hold
  these rows.

- [x] **PLOS ONE batch 12 — `biblio_plos_batch12.csv` (3 rows) closed out**
  (confirmed 2026-07-30, ben-domingue): `page_2025_portrait10.csv`,
  `penningroth_2019_pm_goals.csv`, `penningroth_2019_pm_concerns.csv` (all
  CC BY 4.0) uploaded to Redivis and pasted into the dictionary sheet;
  `biblio_plos_batch12.csv` and all 3 `irw_output/*.csv` files gone from
  disk as expected. See `BATCH_LOG.md`'s "PLOS ONE batch 12" entry for
  full per-dataset detail.

- [ ] **PLOS ONE batch 12 — 205 `human_assistance` rows retriaged, not yet
  hand-reviewed** (2026-07-30): `plos_batch12_retriage.csv` holds 40
  `worth_retrying` + 63 `human_review` + 76 `aggregate_continuous` + 26
  `not_item_response`. The `human_review` rows still need pasting into the
  "Human eye" sheet, and the `worth_retrying` rows still need a
  hand-review pass, same as prior batches.

- [ ] **PLOS ONE batch 12 — 2 deferred `good`-flagged datasets need more
  time** (2026-07-30): MnemoCity Task (`10.1371/journal.pone.0161858`,
  N=160) has a genuine ~8-item usability/satisfaction survey mixed in with
  derived cognitive-task-summary scores in the same file — needs the
  paper's Methods text to confirm what each survey item asks before
  writing a script; children's implicit/voluntary attention-in-time study
  (`10.1371/journal.pone.0123625`, N=62) has real trial-level RT data
  (336 trials/child) but it's spread across 62 separate per-participant
  Excel sheets that need merging — a custom multi-sheet script, not a
  simple melt.

- [x] **PLOS ONE batch 11 — `biblio_plos_batch11.csv` (21 rows) closed
  out** (confirmed 2026-07-30, ben-domingue): 8 papers (`xu_2016_pqb`,
  `fredrickson_2015_mhcsf`, `milavic_2019_psisysf`, `tanck_2021_*` ×2,
  `aguirre_camacho_2021_*` ×2, `conner_2017_*` ×7, `shi_2025_*` ×5,
  `reinwarth_2023_*` ×2, all CC BY 4.0) uploaded to Redivis and pasted
  into the dictionary sheet; `biblio_plos_batch11.csv` and all 21
  `irw_output/*.csv` files gone from disk as expected. Three QC catches
  along the way, see `BATCH_LOG.md`'s "PLOS ONE batch 11" entry:
  `teicher_2015_mace` was **retracted** (ben-domingue caught an odd
  even-number-only response pattern -- the paper confirms MACE severity
  scores are IRT-derived, not raw responses; script and output deleted),
  `aguirre_camacho_2021_*` needed a non-integer filter for EM-imputed
  cells (paper-confirmed), and `shi_2025_maas`/`shi_2025_rrs` had isolated
  single data-entry errors dropped.

- [x] **`automated_finding/human_review_plos_batch11.csv`** (28 rows,
  batch 11's `human_review` rows from `irw_retriage_ha.py`) pasted into
  the "Human eye" sheet (confirmed 2026-07-30, ben-domingue); file deleted
  from the repo.

- [x] **Teicher 2015 MACE S9_File — `biblio_teicher_2015_mace.csv` (12
  rows) closed out** (confirmed 2026-07-31, ben-domingue):
  `teicher_2015_mace_verbal/_nonverbal/_physical/_sexual/_witness_parent/
  _witness_sib/_peer_verbal/_peer_physical/_emot_neglect/_phys_neglect/
  _distress_helpless/_distress_terrified.csv` (all CC BY 4.0) uploaded to
  Redivis and pasted into the dictionary sheet; `biblio_teicher_2015_mace.csv`
  and all 12 `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "Teicher 2015 MACE S9_File raw items" entry for full
  detail, including a list of columns deliberately not shipped (an
  unmapped pilot item, ambiguous peer `Date_*` columns, several unmatched
  household-context columns) that could be revisited if the paper's actual
  survey instrument/codebook
  turns up.

- [ ] **PLOS ONE batch 11 — 4 deferred `worth_retrying` datasets need
  codebook-driven follow-up** (2026-07-30): disordered-eating-in-athletes
  prospective study (`10.1371/journal.pone.0257577`, N=802, 3 waves, ~20
  subscale prefixes incl. EDI and EDE-Q blocks in one 665-column file);
  psychological-crisis-coping/physical-activity study
  (`10.1371/journal.pone.0350928`, N=1051, clean rumination[22i,3sub]/
  PA[3i]/CC[32i,4sub]/ER[14i,2sub] block structure already identified,
  just needs subscale semantic labels from the paper's codebook);
  `10.1371/journal.pone.0279701`'s remaining q11/q12/q13 domain-
  importance/satisfaction/FLZ battery + unidentified q18 6-item block
  (the loneliness3/phq4 tables from this same file are already shipped,
  see above). `plos_batch11_retriage.csv` still holds these rows.

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

- [x] **Carver 2017 PUGGS — `biblio_carver_2017_puggs.csv` (8 rows) closed
  out** (confirmed 2026-07-31, ben-domingue): `carver_2017_puggs_pilot1_traits/
  _det_core/_genom_know/_attitudes` and `_pilot2_traits/_det_core/_genom_know/
  _attitudes.csv` (all CC BY 4.0) uploaded to Redivis and pasted into the
  dictionary sheet; `biblio_carver_2017_puggs.csv` and all 8
  `irw_output/*.csv` files gone from disk as expected. See `BATCH_LOG.md`'s
  "Carver 2017 PUGGS genetics-belief questionnaire" entry for full detail,
  including why the two pilots were kept as separate files (different raw
  response formats for the core-ideas items, confirmed from their own
  codebooks) and why pilot 2's true/false items were recoded to
  correct/incorrect while
  pilot 1's Likert items were not.

- [x] **Meloni 2015 disability-representations study —
  `biblio_meloni_2015_disability.csv` (9 rows) closed out** (confirmed
  2026-07-31, ben-domingue): `meloni_2015_deq_oe_parent/_child`,
  `meloni_2015_deq_ce_parent/_child`, `meloni_2015_parent_divers_ed`,
  `meloni_2015_parent_interests`, `meloni_2015_child_disab_knowledge`,
  `meloni_2015_child_ia_satisfaction/_frequency` (all CC BY 4.0) uploaded
  to Redivis and pasted into the dictionary sheet; `biblio_meloni_2015_disability.csv`
  and all 9 `irw_output/*.csv` files gone from disk as expected. The
  fractional (.5) values in `deq_ce_parent`/`_child`/`child_disab_knowledge`
  were checked against the paper's full text (no imputation language found
  anywhere) and confirmed genuine — restricted to exactly the two 1-4
  scales whose own codebook documents a half-point response option, absent
  everywhere else. See `BATCH_LOG.md`'s "Meloni 2015 disability-representations
  study" entry
  for full detail, including why the `DEQ_OE` blocks are raw mention
  counts (0-8) rather than the paper's own published 0/1 presence table,
  and why the misleadingly-named `_TIME` columns are actually a frequency
  scale, not response times.

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

- [x] **Peters 2025 COVID-19 Risk Tool — `biblio_peters_2025_precautions.csv`
  (6 rows) closed out** (confirmed 2026-07-31, ben-domingue):
  `peters_2025_work_precautions`, `_si_current`, `_si_trigger`,
  `_si_intention`, `_hw_frequency`, `_hw_intensity` (all ODbL 1.0) uploaded
  to Redivis and pasted into the dictionary sheet; `biblio_peters_2025_precautions.csv`
  and all 6 `irw_output/*.csv` files gone from disk as expected. See
  `BATCH_LOG.md`'s "Peters 2025 COVID-19 Risk Tool: precaution-checklist
  follow-up" entry for the `*Est`-column decoding mechanism (it's a fixed
  risk-weight/administration flag, not a per-person estimate, despite the
  name). `proximity` (single radiobutton) and `DMQslider.nr.` (single
  slider) remain unshipped — genuinely single-item, can't form their own
  scale.

- [ ] **`tags_fix_peters_2025_precautions.csv` (6 rows) still staged, not
  yet confirmed applied** (2026-07-31) — optional per-table tags entries
  for the 6 precaution tables above, matching the original 16 tables'
  convention. Not yet pasted/applied; file still on disk.

- [ ] **`metadata/tags.csv` missing rows for the existing 16 `peters_2025_*`
  tables** (found 2026-07-31, while adding tags for the 6 new precaution
  tables above): `BATCH_LOG.md`'s 2026-07-17 entry records these 16 rows
  as "written directly into metadata/tags.csv," but none are present now —
  zero case-insensitive matches for "peters" in the file. The corresponding
  `metadata/biblio.csv` rows *are* present and correct (full APA reference/
  DOI/BibTeX confirmed for `peters_2025_att_exp_eval` etc.), so this is
  tags.csv-specific — possibly a metadata-pipeline regeneration overwrote
  the direct edit, or the same Dropbox-sync file-loss pattern documented
  elsewhere in `BATCH_LOG.md`. Not investigated further — worth a look next
  time `metadata/tags.csv` is regenerated or the site-update skill runs.

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

