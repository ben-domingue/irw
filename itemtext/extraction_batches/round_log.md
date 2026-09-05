# Itemtext batch-extraction round log

## batch_001 — 2026-08-16 (manual pilot run, cron not yet active)
- 12 tables claimed, 11 PASS, 1 BLOCKED (agarwal_2023_dreem — copyrighted DREEM instrument, source inaccessible)
- audit_batch.R: 11/11 written tables PASS, 0 anomalies
- One subagent hit the account's monthly spend limit mid-round; relaunched to finish the remaining table successfully.

## batch_002 — 2026-08-16 (first cron-fired round, job b126d949)
- 12 tables claimed, 12/12 PASS (extraction)
- audit_batch.R: 11 PASS, 1 WARN (algner2022_oss — only 4/6 items recoverable, logged as a legitimate partial-coverage case per SKILL.md, not a failure)
- 0 FAIL/ERROR — well under 30% circuit-breaker threshold, no flag tripped
- Notable: algner2022_cse/mimi16/oss are 3 tables from the same paper (Algner & Lorenz 2022) processed in one subagent group, which reused cached source material across them
- Notable: alexander_2017_dsi table name is generic ("dsi") but live data is only the DSI's Emotional Reactivity + Emotional Cutoff subscales (23/43 items) — Step 3b mismatch caught and logged; item-to-original-appendix-order mapping is a reconstruction, flagged for spot-check in notes.csv
- Cap check: batch_011 not yet reached, queue not exhausted, no circuit breaker flag — cron continues to next scheduled firing

## batch_003 — 2026-08-16 (cron round 2, job b126d949)
- 12 tables claimed, 10 PASS (extraction), 2 BLOCKED (algner2022_wis — copyrighted German incivility scale, source paywalled with no OA route; allen_2025_bis — live resp values {0,1,2} don't match any known BIS-11 variant, no reliable source for item mapping)
- audit_batch.R: 9 PASS, 1 WARN (ali_2021_isi — row-count anomaly on isi_1/2/3, but explained: those ISI severity-anchor items are legitimately skippable/inapplicable per the instrument, not conflation)
- Failure rate 2/12 = 16.7% — under 30% circuit-breaker threshold, no flag tripped
- Notable: alomari_2025_student_questionnaire has a table-naming/dictionary mismatch — table named for "alomari" but actual source paper is Xie, Zhu, Wang, Bai & Zhang 2026, no "Alomari" author anywhere; extraction itself validated cleanly, but the table name/dictionary Reference field looks wrong and should be corrected separately
- Cap check: batch_011 not yet reached, queue not exhausted, no circuit breaker flag — cron continues to next scheduled firing

## batch_004 — 2026-08-16 (cron round 3, job b126d949)
- 12 tables claimed, 9 PASS (extraction), 3 BLOCKED (all alsyouf_2024_* — facilitating_conditions, performance_expectancy, social_influence — systemic: source paper cites a companion 2022 paper for item wording, which in turn cites a 2011 paywalled journal article with no OA copy found anywhere; 3-deep citation chain, no verbatim text recoverable at any level)
- audit_batch.R: 8 PASS, 1 WARN (alsuhibani_2022_npi_s3 — 100% blank item_text, but expected/correct: forced-choice NPI-13 format has no separate question stem, only paired A/B option text)
- Failure rate 3/12 = 25% — under 30% circuit-breaker threshold, no flag tripped
- Notable: alsuhibani_2022_loc — paper's Methods text describes the LOC scale as "five-point" but the live data and the source SPSS file both show a genuine 6-point scale; went with the data/SPSS file (authoritative) over the paper's imprecise description, logged as a caveat
- Notable: PLOS ONE .sav supplementary files (SPSS variable/value labels) were the highest-efficiency source across most of the alsuhibani_2022_* cluster — same trick as batch_002/003, reinforcing that this should be a standard first check per SKILL.md's Step 3 tricks list
- Cap check: batch_011 not yet reached, queue not exhausted, no circuit breaker flag — cron continues to next scheduled firing

## batch_005 — 2026-08-16 (cron round 4, job b126d949)
- 12 tables claimed, 8 PASS (extraction), 4 BLOCKED (amorim_2025_climej_climej / _desenhonotrabalho /
  _suporteorganizacional — 3 tables, same paper, source item text not published anywhere accessible, likely
  primary source is a Harvard Dataverse dataset blocked by an AWS WAF bot-challenge; american_multiracial_face —
  unrelated, item-integer assignment depends on row order across 19 raw rater-level OSF files, only 10/19 present)
- audit_batch.R: 8/8 written tables PASS, 0 anomalies
- Failure rate 4/12 = 33.3% — EXCEEDS 30% circuit-breaker threshold
- **CIRCUIT BREAKER TRIPPED**: wrote `.cache/extraction_batches/circuit_breaker.flag`, cron job b126d949
  self-cancelled via CronList->CronDelete at this firing, 2026-08-16 ~11:52 PDT
- Not a systemic pipeline problem — audit passed cleanly on all written tables, this was a coincidental
  clustering of hard-blocked sources (one shared WAF-blocked dataset affecting 3 tables + 1 unrelated
  missing-files case) in one round
- Cumulative through batch_005: 50 done, 10 failed, 1283 pending (of 1343 total AVAILABLE)
- Human review needed before resuming: review batch_001-005 output, then either recreate the cron job
  (same round-trigger prompt) or investigate the amorim_2025_climej Dataverse WAF block first

## 2026-08-17 — review pass over batches 001-005 (no new extraction)
- Normalized on-disk null representation across all 50 files to match the published corpus
  convention (the `NA` token, per 19/20 sampled curated tables) via the new normalize_nulls.R.
  Batch output had drifted to empty strings; 49/50 files were affected.
- Fixed agogue_2020_self_perceived_creativity: an unlabeled 1-7 scale had "2".."6" padded into
  option_text, which the coverage metric was scoring as 0% missing. Middle options now blank
  (71% missing, honest). Its item text was separately verified against the live S1 .sav --
  all 6 variable labels are an exact character-for-character match, so the mapping is authoritative.
- audit_batch.R gained two checks: `canonical_nulls` (raw-byte comparison, since read.csv collapses
  all three on-disk null forms to the same value) and an `option_text == resp` padding check.
- Added provenance.csv to every batch (mapping_basis / text_source / source_ref / note /
  public_note / uploaded), backfilled for all 50 tables. Combined: 21 data_labels, 16 paper_explicit,
  10 paper_order, 1 reconstructed, 2 unknown; 18 tables carry a public_note.
- New draft_issues_qmd.R turns provenance into draft callouts for the public issues page
  (fixes/itemtext_issues_draft.md); the live .qmd is never edited automatically.
- PROMOTED TO REDIVIS: abouhashish_2025_chatgpt_attitudes, abukhalaf_2025_disaster_prep,
  addy_2021_sdq_ghana, agogue_2020_self_perceived_creativity — staged via itemtables/clean/,
  uploaded by Ben, then removed from batch_001 (marked in provenance.csv `uploaded`).
  batch_001 now holds 7 files; its provenance.csv still documents all 11.
- addy_2021_sdq_ghana also got a live entry on itemtext_issues.qmd (SDQ_7 reversed options).
- STILL OPEN: 16_personalityfactors and abdullah_2024_bsq_sev24 have `unknown` provenance
  (produced by the agent that hit the spend limit) and should not be promoted until re-sourced.

---

## OPEN ITEMS as of 2026-08-17 (session closing)

Process/how-to now lives in `itemtext/BATCH_PROCESS.md`, including the verbatim
cron round-trigger prompt needed to restart the loop. Prior to today that prompt
existed only in a chat session and would have been lost.

**To resume extraction (batches 006-011):** the cron job was deleted when the
circuit breaker tripped at batch_005, and session-scoped cron jobs die with their
session regardless. Recreate it from the prompt in BATCH_PROCESS.md. First delete
`extraction_batches/circuit_breaker.flag`, or Step 0 will immediately
self-cancel. Nothing is left `in_progress`, so the queue is clean to resume:
50 done, 10 failed, 1283 pending.

**Blocking / needs a decision before those tables move:**
1. `16_personalityfactors` and `abdullah_2024_bsq_sev24` have `mapping_basis=unknown`
   (produced by the agent that hit the account spend limit mid-round; it never
   reported its sourcing). Re-source before promoting either to clean/.
2. `alomari_2025_student_questionnaire` (batch_003) appears MISATTRIBUTED — named
   for "alomari" with a blank dictionary Reference, but the source paper is by
   Xie, Zhu, Wang, Bai & Zhang (2026), DOI 10.1371/journal.pone.0340806. The
   extraction validates cleanly; this is a dictionary/table-name problem, so it was
   deliberately NOT put on the public issues page.

**Worth doing, not started:**
3. **De-dupe the pilot tables from the queue.** 7 of the 10 tables in
   `itemtables/pilot/` are still marked `pending` in queue_state.csv (ali_2021_phq9,
   conner_2017_lot, consideration_future_consequences, cordova2019_clinical_edu_environment,
   cucchi_2018_pts, iwasa_2016_padua_inventory, preussmattsson_2022_ownership) and
   would be re-extracted from scratch by a future round. Decide whether the pilot
   output is being kept (mark them done) or discarded (leave pending) before resuming.
4. **Re-triage the 218 BLOCKED tables.** `availability_audit_full.csv` labels them
   "tooling wall, likely available", and they are never revisited by this pipeline
   (it reads only AVAILABLE rows). Batches 002-005 discovered access tricks that did
   not exist at triage time -- Europe PMC supplementaryFiles zip, python-docx table
   parsing, SPSS variable labels -- so this is plausibly high-yield.
5. **Four `himmelstein-*` tables fell through the gap between both audits** --
   resolved 2026-08-31 (issue #1692), and all four now carry a row in
   `queue_state.csv`, which they previously did not. `status_report_20260814.md`
   Thread 2 flagged them as wrongly excluded (their item text is in a public GitHub
   repo cited by the dictionary itself), and they appear nowhere in
   `availability_audit_full.csv`. Outcome: `impossible_question` extracted
   (`batch_014`, 90 items); the two Shipley tables are **excluded** -- the
   copyright judgment call is settled, WPS barred the source study itself, see the
   commercial-instrument section in `SKILL.md`; `admc_raw` is **pending** and needs
   its own round (38 items, several ADMC subtests, 0-6 scale, js text not keyed to
   the `a1_*`/`dr*` codes).
6. **Paste the drafted issues-page callouts.** `fixes/itemtext_issues_draft.md` has 25
   generated callouts across batches 001-005. `addy_2021_sdq_ghana` is ALREADY LIVE on
   the page -- skip it or you will duplicate. Some others are noise: the rule flags any
   `canonical_instrument` source, which sweeps in unremarkable cases like
   `allen_2025_delaydiscount` (Kirby MCQ) and `alsuhibani_2022_gcbs`.

**Calibration finding worth keeping:** realized yield across batches 001-005 was
**50/60 = 83.3%** -- i.e. ~17% of tables the availability audit called AVAILABLE turn
out to be blocked on contact. The audit's triage bar was deliberately liberal ("does
the text exist somewhere", no per-item-code check), so this is the first empirical
measure of how well that call holds. Extrapolated, expect ~1,120 of the 1,343 AVAILABLE
tables to actually land.

---

## 2026-08-17 (later) — review pass over the 7 unpromoted batch_001 tables

All 7 re-audited PASS and staged to `itemtables/clean/` for Ben to upload.

- **`16_personalityfactors` — blocker cleared.** Re-sourced from the dataset's own
  `codebook.html` (openpsychometrics `16PF.zip`). Rebuilt the column→item-integer mapping
  exactly as `data/16_personalityfactors.R` assigns it and diffed all 815 rows: **162 of
  163 items match character-for-character** on item_text and on all five option labels.
  `mapping_basis` unknown → `data_labels`. Exception: item 163 = column `P10`, which the
  codebook omits; its text came from the IPIP Q4/Tension scale listing, corroborated by
  P1–P9 being that scale's other nine items (Ben's call: keep, note the exception). Its
  trailing period was stripped to match the 162 siblings. The earlier "wording mismatch"
  flag is **closed as not-an-error**: the source's whole-test instructions and its own
  per-item codebook labels disagree with each other; option_text follows the codebook.
- **`abdullah_2024_bsq_sev24` — blocker cleared.** The 2024 `.sav` has no variable or value
  labels and the article quotes no item wording, but **Table 1 of the BSQ-M validation paper
  it cites as its instrument source (IJERPH 18:2487, CC BY) lists every item bilingually
  against its own code** — an exact code-to-text match. unknown → `paper_explicit`.
  Same table upgraded `bsq_sevgen` from `paper_order` → `paper_explicit`. Ordering
  corroborated independently: the papers say Sev24 item 5 is the 1–8 item, and `SEV24_5` is
  the only 8-level item in the live data. option_text stays blank — BSQ options are per-item
  multiple-choice categories that no source publishes.
- **`abdullah_2024_hpbbloat_stress` — downgraded, honestly.** `paper_order` → `reconstructed`.
  Confirmed the SM-code→final-form mapping cannot be verified: both supplementary `.sav`
  files carry `SM1`–`SM8` with no labels, and Supplemental Information 3 is the renumbered
  final 17-item form, which interleaves the five subscales round-robin (SM items at #4, #9,
  #13, #17). Consistent with the ascending-order assumption, not proof of it. Given a
  `public_note`.
- **`aguirre_camacho_2021_champion` — no change needed.** Verified correct as shipped: Table 2
  supplies the administered Spanish items, and the paper labels only the 1/5 anchors and only
  in English. The language mismatch is a property of the source.
- **`aguirre_camacho_2021_shai` — one real defect fixed.** `HAnx15`'s `item_text` had the entire
  consequences-of-illness section preamble prepended to its stem; the preamble now lives in
  `section_prompt` on a second section covering HAnx15–18. Re-validated against live data.
  Also noted: the paper's own description of the SHAI response format ("0 to 3: no symptoms,
  mild, severe, very severe") does not describe the SHAI, whose options are item-specific
  statements — transcribed per the instrument, not the paper's prose.
- **`ahmed_2019_food_consumption` — clean, no change.**

**Policy decision (Ben, 2026-08-17):** where a study administered a translation whose wording
is unpublished, **ship the original-language instrument text with a `public_note`** rather than
holding the table. This unblocks a large recurring class. Applied to `shai`; the two BSQ tables
turned out not to need it after the bilingual validation-paper table surfaced.

**Inconsistency worth settling before it propagates:** `champion` ships the *administered*
Spanish wording while the two BSQ tables ship the *English* wording even though their source
table publishes the administered Malay alongside it. Both are defensible; there is no
convention yet for which language wins when a source publishes both.
- STAGED FOR UPLOAD 2026-08-17: six tables moved out of batch_001 into `itemtables/clean/` --
  16_personalityfactors, abdullah_2024_bsq_sev24, abdullah_2024_bsq_sevgen,
  aguirre_camacho_2021_champion, aguirre_camacho_2021_shai, ahmed_2019_food_consumption.
  `uploaded` in provenance.csv is still blank for all six; stamp it once Ben confirms the push.
  batch_001 now holds only abdullah_2024_hpbbloat_stress (held: `reconstructed` mapping, three
  items, unverifiable SM-code ordering -- see above).
- SPOT-CHECK FINDING 2026-08-17 (`aguirre_camacho_2021_shai`, caught before upload): pulled back out
  of `clean/` and rebuilt. The SHAI/HAI-18 has **no item stems** -- each item is a group of four
  complete statements (same forced-choice shape as alsuhibani_2022_npi_s3) -- but the extraction had
  synthesized a stem per item and compressed the statements into short anchors, dropping wording
  (item 2 lost "(of my age)"; item 12's "I usually think that I am seriously ill" became "Usually").
  Now a literal transcript: item_text blank throughout (expected 100%-blank audit WARN), 72 verbatim
  option_texts, HAnx15-18 in their own section carrying the pre-item-15 instruction. Re-validated.
  **Generalizable lesson: for four-statement-group instruments (HAI/BDI-style), a tabular
  clinical-website rendering is a paraphrase, not the instrument.** Worth checking any other batch
  table whose source was a third-party assessment site.

---

## 2026-08-17 — mapping-verification sweep across batches 001-005 (all 50 tables)

Triggered by the `champion` spot-check, which showed that an item-to-text mapping can be an
unverified numeric correspondence even when `mapping_basis` is `paper_explicit`. Neither
`validate_items.R` nor `audit_batch.R` can catch a permuted mapping -- both only check sets.

**Now a required step:** SKILL.md Step 5b, with two new scripts --
`item_stats.R` (per-item M/SD/floor/ceiling from live data, wave-split, ties flagged) and
`mapping_structure.R` (correlation-block / keying-polarity structure). Outcomes are tracked
permanently in `itemtext/mapping_verification.csv`.

**Result over all 50 tables: 0 left unassessed.**

| Status | n |
|---|---|
| NOT_NEEDED | 29 |
| VERIFIED | 7 |
| PARTIAL | 10 |
| NO_ROUTE | 4 |

The 29 exempt: 22 `data_labels` (source variable labels are authoritative), 7 with
self-describing item codes (`TLXEffort`, `afraid`, Stroop stimulus words) where a permutation
could not hide. **All 4 already-uploaded batch_001 tables are in the exempt group**, so
nothing already on Redivis was exposed.

**Eight verification routes now documented in Step 5b**, several discovered during this sweep:
per-item statistics (`champion`), response-range fingerprint (`alves_2017_hamd17` 17/17,
both `bsq_*`), implied parameter monotonicity (`allen_2025_delaydiscount`, Spearman +0.96
between choice proportion and Kirby k), subscale block structure (`alexander_2017_dsi` 21/23,
`algner2022_mimi16` 15/16), keying polarity (`algner2022_cse`, canonical odd/even CSES
pattern), marker item (`almuqbil_2022_epds` item 10), subscale totals
(`shai`), semantic coherence (`ahmed_2019_food_consumption`).

**Findings beyond itemtext (all need action outside this pipeline):**
1. `alves_2017_hamd17` -- **9 out-of-range responses** in the underlying IRW table. Items 6,
   14 and 16 are clean 0-2 HDRS items with 2, 1 and 6 stray values at 3-4. Should be dropped
   per datastandard.md.
2. `altahla_2024_whoqol_bref` is a **strict duplicate** of `altahla_2024_whoqol`: identical
   26-item set, identical 1-5 range, all 189 ids among the other's 412, and all 4,914
   (id,item,resp) triples identical. Differs only in covariate columns. Per the
   collapse-same-instrument-samples convention this should be one table; as it stands we
   would ship the same item text twice.
3. `alsuhibani_2022_gcbs` reclassified `paper_explicit` -> `data_labels`: the study's own
   PLOS `.sav` files label every GCBS item and the extraction had missed them. Fixed GCBS_13
   from the US-spelled canonical 'rumors' to the study's own 'rumours'.
4. `alexander_2017_dsi` -- its provenance note claims the DSI-R's ER(11)+EC(12) split, but
   both the item content and the data give 10/13. One item is likely mislabelled in the note.

**Highest residual risk, unfixable with data:** `ALSECYPIAMH_WU_2022_PHQ`. Two items only
(anhedonia vs depressed mood), paywalled source, unlabeled OSF columns; a swap is a coin flip
and the items are too close semantically for any plausibility check. Needs the paper or an
author email. `algner2022_oss` is the weakest table overall -- only 4 of 6 items have text,
one of those a back-translation, and no route exists -- a candidate for dropping rather than
verifying.

## 2026-08-17 — batch_001 closed out

- STAGED IN `clean/` for Ben to upload (6): 16_personalityfactors, abdullah_2024_bsq_sev24,
  abdullah_2024_bsq_sevgen, aguirre_camacho_2021_champion, aguirre_camacho_2021_shai,
  ahmed_2019_food_consumption. Audit: 6 PASS + 1 expected WARN (shai's 100%-blank
  `item_text`, correct for a four-statement-group instrument). `uploaded` still blank in
  provenance.csv -- stamp on confirmation.
- HELD (1): abdullah_2024_hpbbloat_stress -- `reconstructed` mapping, NO_ROUTE in
  mapping_verification.csv, three items. Stays in batch_001.
- ISSUES PAGE: added 4 entries to `../irw_site/itemtext_issues.qmd` (now 17 total) --
  aguirre_camacho_2021_shai (English original for a Spanish administration; no item stems so
  all text is in option_text; within-subscale order unverified), aguirre_camacho_2021_champion
  (Spanish items, English endpoint anchors), abdullah_2024_bsq_sevgen (stated per-item scale
  ranges disagree with the data; SEVG2 published but absent), 16_personalityfactors (source
  instructions contradict its own codebook labels; item 163 absent from the codebook).
  Deliberately NOT listed, per the issues-page bar (concrete text-vs-table mismatches only,
  not gaps the source never published): bsq_sev24's unpublished option labels, and
  ahmed_2019_food_consumption (nothing to report).
- UPLOADED 2026-08-17 (6): 16_personalityfactors, abdullah_2024_bsq_sev24, abdullah_2024_bsq_sevgen,
  aguirre_camacho_2021_champion, aguirre_camacho_2021_shai, ahmed_2019_food_consumption. Stamped in
  provenance.csv and mapping_verification.csv, then removed from batch_001. **batch_001 is closed**
  except abdullah_2024_hpbbloat_stress, which stays held (NO_ROUTE mapping, 3 items); its sidecars
  still document all 12 tables the batch produced.
- STATE MOVED OUT OF `.cache/` (which is gitignored, so the whole batch history and queue were
  untracked): `round_log.md` and `queue_state.csv` now live in `itemtext/extraction_batches/` and are
  committed. `circuit_breaker.flag` moved with them but stays gitignored -- its presence is transient
  control state, not history. BATCH_PROCESS.md paths updated throughout, including inside the
  round-trigger prompt, which also now carries the Step 5b mapping-verification requirement.

---

# CONSOLIDATED STATE as of 2026-08-17 (supersedes the "OPEN ITEMS as of 2026-08-17
# (session closing)" section above, which is now partly stale)

## Where the pipeline is

- Queue: **50 done, 10 failed, 1283 pending** of 1343 AVAILABLE. Batches 001-005 complete;
  006-011 not started (the cron job is gone; recreate from BATCH_PROCESS.md, and delete
  `extraction_batches/circuit_breaker.flag` first or Step 0 self-cancels).
- Realized yield 50/60 = 83.3% of tables the availability audit called AVAILABLE.
- **batch_001 is CLOSED**: 6 tables uploaded 2026-08-17, 1 held
  (`abdullah_2024_hpbbloat_stress`), 1 blocked at extraction (`agarwal_2023_dreem`),
  4 uploaded in the earlier pass. Its sidecars still document all 12.
- Batches 002-005: extracted and verified, **not yet reviewed by Ben, nothing uploaded**.

## Health of batches 002-005 (all re-checked 2026-08-17, nothing left to re-run)

- `normalize_nulls.R`: clean. One file (`alsuhibani_2022_gcbs`, batch_004) had been left with
  Python-quoted `"NA"` by a manual spelling fix and is now normalized.
- `audit_batch.R`: 36 PASS + 3 WARN, all three explained and expected --
  `algner2022_oss` (partial coverage, 2 of 6 items unrecoverable), `ali_2021_isi`
  (row-count anomaly on isi_1/2/3, legitimately skippable severity-anchor items),
  `alsuhibani_2022_npi_s3` (100% blank item_text, correct for a forced-choice instrument).
- Mapping verification: complete for all 50 tables (`mapping_verification.csv`).
- Third-party-website sourcing (the failure mode that produced the bad first
  `aguirre_camacho_2021_shai`): swept. Only 3 tables in 002-005 were website-sourced.
  `alsuhibani_2022_gcbs` was replaced with the study's own `.sav` labels; `alves_2017_hamd17`
  and `amarilla_2020_lawton_brody` were inspected and are structurally correct (domain-name
  stems with genuine severity/descriptive anchors, not a paraphrased grid).

## What needs a human — now tracked as GitHub issues (2026-08-17)

The prose list that used to live here has been converted to issues on ben-domingue/irw,
all labelled `ITEMS`, so it stops drifting out of date in this file:

| issue | matter |
|---|---|
| #1643 | ship-or-hold `ALSECYPIAMH_WU_2022_PHQ` (unverifiable 2-item mapping) |
| #1644 | `fixes/*.csv` corrected tables unuploaded; their issues-page notes held with them |
| #1645 | verify the 4 earliest-uploaded tables, recoverable only from Redivis |
| #1646 | audit the 13 issues-page callouts predating the 2026-08-17 review |
| #1647 | coverage gaps: `ALSECYPIAMH_WU_2022_SDQ` and the four `himmelstein-*` tables |
| #1648 | re-triage the 218 BLOCKED availability-audit tables |
| #1649 | should the issues page carry explanatory entries as well as discrepancies? |
| #1650 | decide the fate of the 7 pilot tables still `pending` in the queue |
| #1651 | table-naming/dictionary mismatches: `alomari_2025_student_questionnaire`, `allen_2025_bis` |
| #1652 | `altahla_2024_whoqol_bref` duplicates `altahla_2024_whoqol`'s responses |

Plus #1642 (`data fix` label, not ITEMS): `alves_2017_hamd17`'s 9 out-of-range responses.

Still held, not filed as issues because they are extraction outcomes rather than open
questions: `agarwal_2023_dreem` (copyrighted DREEM, source inaccessible) and
`algner2022_oss` (2 of 6 items have no recoverable text, one of the rest a back-translation).

## What changed in the skill (so future rounds don't repeat this session)

- **SKILL.md Step 5b (new, REQUIRED)** -- mapping verification against the data, 8 routes +
  2 exemptions, `item_stats.R` and `mapping_structure.R`, outcomes recorded in
  `mapping_verification.csv`. Set-level checks cannot catch a permuted mapping.
- **SKILL.md Step 4** -- stemless / four-statement-group instruments: `item_text` blank is
  correct, and clinical-website grids are paraphrases, not the instrument.
- **SKILL.md Step 6d** -- re-run normalize + audit after ANY later edit, including one-line
  script fixes (Python `csv` writes `"NA"` where R writes `NA`).
- **BATCH_PROCESS.md** -- state moved out of gitignored `.cache/` into tracked
  `extraction_batches/`; round-trigger prompt now carries the Step 5b requirement.

## 2026-08-17 — batch_002 reviewed and staged

- 12 tables, 11 PASS + 1 WARN. Reviewed table by table with Ben; two spot-checked in depth.
- FIXES MADE DURING REVIEW:
  - `alasmari_2025_ai_trust_confidence` shipped `raw_resp` (label strings) because the paper never
    states its 1-4 coding direction -- but `data/alasmari_2025_ai_trust_confidence.py` defines
    RESP_MAP outright. Converted to `resp`, then confirmed empirically: label counts in the raw S1
    .xlsx match integer counts in the live table in all 16 item x level cells. Its sibling
    `_compare` had already done this correctly, so the two were inconsistent.
  - `ajaykumar_2023_nasa_tlx`: item_text was the official NASA-TLX Appendix A definitions while the
    paper says it administered an "Adapted ... modified version" it never reproduces. Reduced to
    dimension names, then RESTORED to the definitions on Ben's call -- they describe the construct
    far better than a bare label and the divergence belongs in the public note. Dimension name now
    prefixes each definition, matching the TLX document's own title+description layout.
  - `alcoholhealthwarninglabel_brennan_2022_awareness_harms_followup`: option_text shortened.
    Confirmed the dichotomisation is the STUDY's (source columns FD2_FD6_*_b; our script only casts
    to int), so "Aware"/"Not aware" are their categories.
  - `alexander_2017_dsi`: spot-check against the Skowron & Friedlander (1998) published Appendix
    verified all 23 item texts verbatim AND scored 23/23 on the block test using the published
    subscale key. This RETRACTED an error I had introduced earlier in the day: I had grouped items
    by reading their text rather than using the published key, misassigned dsi_4, scored 21/23, and
    "corrected" the provenance note's ER(11)+EC(12) to 10/13. The paper and instrument were right.
  - Three tables emitted a separate section_id per item with blank prompts, against the standard's
    "single trivial <table>_1" rule: alasmari_2025_ai_trust_confidence, albeitawi_2025_preceptor_needs,
    alcoholhealthwarninglabel_brennan_2022_awareness_harms_followup. Collapsed.
- SKILL.md gained: the PRIME COMMANDMENT section (`item` must be common between the resp and
  itemtext tables; raw_resp breaks linkage and is a last resort, not a default when the paper is
  merely silent), the rule to read `data/<table>.py|R` before falling back to raw_resp, and Step 5b
  route 9 (response-frequency matching) plus explicit naming of the two mapping axes.
- STAGED IN `clean/` (11), `uploaded` still blank pending Ben's push: ahmed_2019_wellbeing,
  ajaykumar_2023_nasa_tlx, alasmari_2025_ai_trust_compare, alasmari_2025_ai_trust_confidence,
  albeitawi_2025_preceptor_needs, both alcoholhealthwarninglabel_brennan_2022_*,
  alcoholstroop_jones2024, alexander_2017_dsi, algner2022_cse, algner2022_mimi16.
- HELD (1): `algner2022_oss` -- 2 of 6 items have no recoverable text, one of the other four is a
  back-translation from a Brazilian adaptation, NO_ROUTE on verification. Weakest of all 50 tables;
  a candidate for dropping rather than fixing. batch_002 now holds only this table plus sidecars,
  which still document all 12.

## 2026-08-17 — ALSECYPIAMH_WU_2022 family, chased on Ben's question

`data/ALSECYPIAMH_WU_2022.r` produces **10** IRW tables (CPS, SDQ, SWEMWBS, SWLS, PEI, NEI,
PHQ, Empathy, MIL, PIL). Status of each for itemtext:

- **7 already have itemtext on Redivis** (cps, empathy, nei, pei, pil, swemwbs, swls), which is
  why the availability audit lists only 2 of the family -- the audit was seeded from tables
  *without* itemtext. No coverage gap there.
- **PHQ** -- ours, batch_004.
- **MIL** -- `pending` in queue_state.csv; batch_006+ will pick it up.
- **SDQ** -- appears in NEITHER the availability audit NOR the itemtext list. **Genuine coverage
  gap**, same class as the four `himmelstein-*` tables. The SDQ is well documented and
  `addy_2021_sdq_ghana` was extracted successfully, so this is likely easy yield.

PHQ mapping: NO_ROUTE now *established*, not assumed. The OSF raw file `CPS Study 2.sav` labels
39 of its 92 columns but not PHQ1/PHQ2; the OSF supplementary docx covers only the CPS; the JORA
paper is paywalled and not in Europe PMC OA. Live means (PHQ1 0.939, PHQ2 0.816) distinguish the
two items but there is no external anchor for which canonical PHQ-2 item should be higher.

**Side finding worth using:** that same supplementary docx contains the full bilingual CPS items
AND per-item means/SDs by subgroup (Tables S1, S2). `alsecypiamh_wu_2022_cps` itemtext is already
live and has never been verified -- those per-item means make it checkable by Step 5b route 1.
Fold this into the pre-existing-issues audit (consolidated-state item 8).

## 2026-08-17 — batch_003 re-evaluated with focus on `item` mapping, then staged

Prompted by two spot-checks that turned up oddities. Every table's item-code provenance was
traced to its processing script and verified against the actual source file.

**Item-mapping findings (the point of the pass).** Four `ali_2021_*` tables and both
`alkouri_2025_*` tables assign item codes POSITIONALLY from raw column indices, so being
`data_labels` did not by itself make them inference-free -- the tie depends on header
positions. All were checked directly against the source files:
- `ali_2021_gad7` 7/7, `ali_2021_iesr` 22/22 exact against the S1 headers.
- `ali_2021_spfi` 15/16; the deviation is a corrected source typo ("emphathetic").
- `ali_2021_isi` positions confirmed, but 6/7 texts had been silently normalised to canonical
  ISI wording (source has "NOTICABLE", "Difficult falling asleep"). Kept the canonical wording;
  `text_source` corrected study_materials -> canonical_instrument, because the note had claimed
  verbatim transcription and that was false.
- `almuqbil_2022_epds` UPGRADED paper_order -> data_labels: the study's own file carries the
  item wording in its column headers. 10/10 verified.
- `alkouri_2025_coping` / `_icu_stressors`: item mapping verified against source column order;
  response mapping verified by frequency matching (95/95 and 145/145 item x level cells).

**Two real defects fixed.** Both alkouri tables had option rows for `item_01` ONLY, with every
other item carrying a single NA-resp row -- 18 of 19 and 28 of 29 items had no linkable response
options. Rebuilt as full grids (95 and 145 rows). `audit_batch.R` gained a check for exactly this
asymmetry (some items have option rows while others in the same table have none); blank
option_text alone stays a note rather than a WARN, since it is legitimate table-wide.
A source quirk surfaced and is now represented: the stressor questionnaire changes its level-2
label mid-block (items 01-14 "Barely", items 15-29 "Rarely").

**Result:** batch_003 verification is 9 VERIFIED + 1 PARTIAL (`algner2022_uwes`). All 10 moved to
`clean/`; batch_003 retains only its sidecars.

**batch_002 uploaded**: the 11 staged tables were removed from `clean/` by Ben, the documented
signal that they went to Redivis; stamped uploaded=2026-08-17. Those disk deletions were swept
into commit bcf671d by an over-broad `git add -A` -- no loss, but the commit message does not
mention them.

## 2026-08-17 — batches 004 and 005 re-evaluated under the updated process

Same discipline as batch_003: trace every table's item codes to its processing script, then verify
against the actual source file rather than trusting the `data_labels` label.

**batch_004 (9 tables) -> 7 VERIFIED, 1 NOT_NEEDED, 1 NO_ROUTE.** The whole `alsuhibani_2022_*`
cluster was checked against the study's own PLOS `.sav` variable labels: consp_s1 5/5, ecrs_s3
12/12, pads_s1 10/10, pads_s2 8/8, sers 20/20, gcbs 15/15, and loc 24/24 once the source labels'
leading "N." numbering is dropped. `loc`/`sers`/`gcbs` are cross-study renames documented in the
script, not inferences. `npi_s3` has no item text to verify (forced-choice, blank by design -- its
audit WARN is expected). `ALSECYPIAMH_WU_2022_PHQ` stays NO_ROUTE.

**batch_005 (8 tables) -> 8 VERIFIED.** Two substantive corrections:

1. **`amarilla_2020_lawton_brody` was wrongly called NO_ROUTE by me earlier today.** I had checked
   the paper and its total-index supplement and concluded no per-domain source existed. The study's
   `.sav` labels **263 of its 278 columns**, including `LYBRODYBASAL1` = "A. Ability to Use Telephone
   prior hip fracture" through `LYBRODYBASAL8`. All 8 item_texts match. paper_order -> data_labels,
   NO_ROUTE -> VERIFIED, public_note removed. Its siblings verified the same way: barthel 10/10,
   eq5d 5/5, sf12 12/12.
2. **The three `altahla_2024_*` tables had paraphrased item text.** Their source headers are not
   opaque -- they carry the full item text numbered 1-31 (1-26 WHOQOL-BREF, 27-31 SWLS) -- and the
   script replaces the header positionally. Checking shipped text against those headers gave only
   17/26 for WHOQOL and 3/5 for SWLS: 9 WHOQOL items were a paraphrase (shipped "How much do you
   feel that pain prevents you..." vs the source's and the instrument's "To what extent do you feel
   that physical pain prevents you..."). item_text rebuilt from the source headers, which for WHOQOL
   are the canonical wording. paper_explicit/translated_substitute -> data_labels/study_materials.
   Sheet1 and GP headers verified identical. option_text was already right (per-item WHOQOL anchors).

**Two notes corrected as inaccurate:**
- `altahla_2024_whoqol_bref`'s note claimed it is "a genuinely distinct sample ... not a duplicate
  upload". It is the SCI-only subsample of `altahla_2024_whoqol`, which is the combined SCI+healthy
  file (189+223=412) carrying cov_group; all 4,914 of its (id,item,resp) triples appear there
  identically. Redundant at the response-data level.
- The altahla language caveat was right in substance but vague: the paper confirms a Chinese sample,
  so participants read a Chinese version while the shipped English text is the study's own labelling.

**Cumulative verification across all 50 tables: 27 VERIFIED, 6 PARTIAL, 3 NO_ROUTE, 14 NOT_NEEDED.**
NOT started: staging 004/005 to `clean/` -- deliberately held while Ben uploads batch_003 from
there, to avoid mixing batches in the staging directory.

## 2026-08-17 — batch_003 uploaded, batch_004 staged

- batch_003's 10 tables were uploaded by Ben and cleared from `clean/`; stamped uploaded=2026-08-17
  in provenance.csv and mapping_verification.csv. batch_003 now holds only its sidecars.
- STAGED IN `clean/` (8 of batch_004's 9): alsuhibani_2022_consp_s1, _ecrs_s3, _gcbs, _loc, _npi_s3,
  _pads_s1, _pads_s2, _sers. Audit on the staging dir: 7 PASS + 1 expected WARN (npi_s3's blank
  item_text, correct for a forced-choice instrument). Every one verified item-by-item against the
  study's own .sav labels.
- HELD (1): `ALSECYPIAMH_WU_2022_PHQ`. Still the only NO_ROUTE in the batch and the decision on it
  is still open -- my recommendation is to ship it with its public note, for consistency with
  almuqbil_2022_epds and altahla_2024_swls, whose mappings rest on the same "column N = instrument
  item N" convention; the difference is only that PHQ has no marker item to corroborate it and just
  two items, so a wrong guess would affect the whole table.
- ISSUES PAGE (main, commit 5c47bbb, now 26 entries): added `alsuhibani_2022_loc` (paper says
  five-point, data and the study's SPSS file show six). The other seven need no callout -- no
  text-vs-table discrepancy survived verification.
- Deliberately NOT added: a note explaining `alsuhibani_2022_npi_s3`'s blank item_text. It is a
  correct encoding of a forced-choice instrument rather than a mismatch, so it fails the page's
  bar -- but a user seeing a 100%-empty item_text column may well wonder, so it is worth revisiting
  whether the page should carry explanatory entries as well as discrepancy ones.

## 2026-08-17 — batch_005 reviewed; new per-item resp-coverage check

- All 8 tables VERIFIED (7 data_labels verified against source labels/headers, hamd17 via the
  response-range fingerprint). Audit: 7 PASS + 1 WARN, the WARN now pointing at a real data defect
  rather than an itemtext one.
- NEW AUDIT CHECK: per-item resp coverage. validate_items.R compares the resp SET table-wide, so an
  item can lack option rows for levels its own respondents used and still pass, with the join then
  silently dropping those responses. It found `alves_2017_hamd17`'s HamD9Baixa (Agitation) covering
  0-2 while 14 respondents scored 3 and one scored 4 -- a real 0-4 range from a later HDRS variant,
  since the 0-2 anchors are Hamilton's original 1960 scoring that the rest of the table follows.
  Added rows for 3 and 4 with blank option_text rather than mixing HDRS versions within one table.
- Swept the check over every other local table AND 27 already-uploaded tables recovered from git
  history: no other table has the defect.
- `alves_2017_hamd17`'s 9 stray out-of-range values on items 6, 14 and 16 are a RESPONSE-DATA
  problem, now filed as ben-domingue/irw#1642 with the `data fix` label rather than put on the
  itemtext issues page. The agitation version mismatch did go on the page (main, 6f12f00, 27 entries).
- batch_004's 8 staged tables were uploaded and cleared from `clean/`; stamped uploaded=2026-08-17.
  `ALSECYPIAMH_WU_2022_PHQ` remains held and unstamped (open decision 9).
- STAGED IN `clean/` (batch_005, all 8): altahla_2024_swls, altahla_2024_whoqol,
  altahla_2024_whoqol_bref, alves_2017_hamd17, amarilla_2020_barthel, amarilla_2020_eq5d,
  amarilla_2020_lawton_brody, amarilla_2020_sf12. All 8 pass validate_items.R; staging-dir audit is
  7 PASS + 1 WARN, the WARN being alves_2017_hamd17 pointing at the response-data defect filed as
  ben-domingue/irw#1642, not at the item text.
- ISSUES PAGE (main, 82ba79b, now 30 entries): added the three altahla_2024 language callouts;
  whoqol_bref's also records that it duplicates altahla_2024_whoqol's responses. alves_2017_hamd17
  was added earlier (6f12f00).
- batch_005 now holds only its sidecars. With this, all five batches are through review: 50 tables
  extracted, 47 uploaded or staged, 3 held (agarwal_2023_dreem blocked at extraction,
  algner2022_oss, ALSECYPIAMH_WU_2022_PHQ).

## batch_006 — 2026-08-17 (first round under the consolidated skill)

12 claimed, **11 written, 1 blocked** (8.3% failure, well under the breaker). audit_batch.R: **11/11 PASS**,
no anomalies. Verification: 7 VERIFIED, 1 PARTIAL, 1 NO_ROUTE, 3 NOT_NEEDED.

The new Step 5b/core-model discipline visibly changed behaviour — agents classified the code
derivation before extracting, and two positional tables (`arora2025_blueq_pedagogical`,
`_synchronous`) got the required header diff rather than an assumption.

**Blocked (honest):** `arnulf_2022_conspiracy_thinking`. The shared .sav labels its CT2 columns with
bare codes and no item-text value labels (its CT1 siblings DO carry them, but those items aren't in
IRW); the paper describes a 15-item inventory while the data hold 14 columns with no record of which
was dropped. Recorded `unknown`/`NO_ROUTE` rather than aligning canonical wording by guess.

**Findings worth a human eye:**
- `APFCompact_Ptacek_2024_DASS-21` is a **complete duplicate** of `ptacek2023_dass21` -- identical item
  sets, all 6,279 (id,item,resp) triples shared, same 299 ids -- and the older table additionally has
  cov_gender/cov_age. Neither has itemtext yet. Filed as #1653 (`data fix`); the extracted item text
  should follow whichever table survives.
- `anjum_2022_gad7` ships **6 of GAD-7's 7 items**: `E20_Anxiety` exists in the source .sav but the
  processing script never ships it. Response-data question, not itemtext.
- `an_2020_efl_self_regulated` pools **three instruments** (TSELSS Q1-26, an enjoyment/environment
  block Q27-33, and a 16-item English Language Self-Efficacy Questionnaire Q34-49) while the table
  name signals only the first. Same shape as `AOMT_..._BRS`, which combines the Bullshit Receptivity
  Scale with motivational-quotation controls. Both carry public_notes.
- `AOMT_..._AOT`'s 14 codes are a 10-item scale plus 4 reverse-coded duplicates (`AOT3_rev` = 6 - AOT3,
  confirmed empirically); the duplicates ship the parent text with reversed option_text.
- `anh_2026_finbehavior`: all nine items sit within 0.04 of the scale midpoint (means 2.980-3.016,
  SDs 0.956-1.021, n=306). Unusual enough to check the S1 file against. NOTE: the extracting agent
  reported this as "exactly 3.000 for all nine", which is false -- corrected in notes.csv. Its item
  text also came from OCR of an image table, so it deserves a transcription spot-check.
- Verbatim source typos kept and disclosed rather than silently normalised, per the new rule:
  `anjum_2022_gad7` E21 "not being able to sleep or control worrying" (canonical: "stop"), E24 "hart
  to sit still"; `arnulf_2022_general_knowledge` "principle street for finance in New York".

**Follow-up 2026-08-18 (human spot-check of 5 of the 11 tables).** No extraction defects found:
`anh_2026_finbehavior`'s nine OCR'd stems are character-exact against the Table 3 image (including
its inconsistent terminal punctuation), the two `anjum_2022_gad7` typos are genuinely in the .sav
labels, all 14 `..._AOT` texts match the codebook (which itself documents the four `_rev` codes as
reverse-coded copies with no wording of their own), all 50 `art` codes match the .rda colnames, and
49/49 `an_2020` Chinese labels match after stripping source numbering. The corrected means note is
right (2.980-3.016, SD 0.956-1.021).

But the check turned up an **availability-audit error**: the PLOS Table 3 that supplied FB's text is
an *image*, and it prints wording for all six constructs in the file, not just FB. The five sibling
tables (`anh_2026_finsocialization`, `_ai_adoption`, `_finwellbeing`, `_finliteracy`,
`_digitaltrust`, 36 items) were classified UNAVAILABLE/BLOCKED on reasoning like "the paper only
names the source scale without reproducing wording" — true of the article text, false of the paper.
`grep "shop around"` over the scraped text returns 0 hits and the table's HTML endpoint 404s; only
the PNG carries it. All five reclassified AVAILABLE and inserted at the head of the pending queue
(1,228 pending). The rule is now in SKILL.md Step 3.

~100 of the 324 UNAVAILABLE/BLOCKED rows citing a PLOS/PMC-family source give reasoning of that same
"paper does not reproduce the wording" form, so some fraction is probably recoverable the same way.
**Deliberately not swept now** (Ben, 2026-08-18): defer to one big re-sweep once substantially more
of the queue is processed, rather than interrupting extraction to re-audit.

**TRIAGED 2026-08-18.** 11 written tables reviewed against the batch_001 model; gates re-run live
first (`normalize_nulls.R` clean, 0 of 11 changed; `audit_batch.R` **11/11 PASS**;
`mapping_verification.csv` complete, 12 rows).

- STAGED IN `clean/` for Ben to upload (10): an_2020_efl_self_regulated, andrich_mudfold,
  anh_2026_finbehavior, anjum_2022_gad7, AOMT_..._AOT, AOMT_..._BRS, arnulf_2022_general_knowledge,
  arora2025_blueq_pedagogical, arora2025_blueq_synchronous, art. `uploaded` still blank in
  provenance.csv -- stamp on confirmation. Verified `clean/` holds no non-`__items.csv` file.
- HELD (1): `APFCompact_Ptacek_2024_DASS-21` -- #1653 says it is a complete duplicate of
  `ptacek2023_dass21`; the item text should follow whichever table survives. Stays in batch_006.
- Still blocked at extraction (1): `arnulf_2022_conspiracy_thinking`.
- Independent re-checks of the 6 tables not covered by the 2026-08-18 spot-check, all clean:
  arora ped/sync positional claim confirmed against `data/arora2025_blueq.py` (0-based cols 3-12
  and 15-20) and the spreadsheet's row-2 header, 16/16 exact; DASS-21's 21 stems are canonical and
  its header subscale letters reproduce the published key at all 21 positions; AOMT BRS 20/20
  against the codebook; arnulf general knowledge 12/12 against the .sav labels; andrich_mudfold's
  codes are self-describing (the `mudfold` package is not installed here, so its published-means
  check was not re-run).
- ISSUES PAGE: 7 of the 10 draft callouts added to `irw_site/itemtext_issues.qmd` (now 39 total) --
  an_2020_efl_self_regulated, anjum_2022_gad7, both AOMT_... tables, arnulf_2022_general_knowledge,
  arora2025_blueq_synchronous, art. Deliberately NOT added, per the issues-page bar:
  `arora2025_blueq_pedagogical` (its only caveat is that the source never published anchors -- its
  sibling IS listed, because the canonical prompt says "face-to-face component" for sessions the
  study ran online, which is a concrete mismatch); `anh_2026_finbehavior` and `andrich_mudfold`
  (no caveat at all); `APFCompact_Ptacek_2024_DASS-21` (held, not shipping); and
  `arnulf_2022_conspiracy_thinking`, whose auto-generated callout ("the origin of the item text was
  not recorded") is an artifact of templating over a blocked table that shipped no text.
- NOTED, not acted on: `arora2025_blueq_asynchronous` is a third sibling from the same spreadsheet,
  marked BLOCKED by the availability audit ("Dataverse page returned no fetchable content"), but its
  seven item texts sit in the cached raw.xlsx at cols 23-29 exactly where `data/arora2025_blueq.py`
  reads async1-7. Left for the deferred BLOCKED re-sweep (#1648) per Ben, 2026-08-18.

- UPLOADED 2026-08-18 (12): the 10 staged above, plus the two tables that were already sitting in
  `clean/` — `american_multiracial_face` (batch_005, previously unstamped) and
  `amarilla_2020_lawton_brody` (a re-upload of the corrected version from 2589531, so its stamp moves
  2026-08-17 -> 2026-08-18). Stamped in each batch's provenance.csv and in mapping_verification.csv;
  the uploaded CSVs removed from batch_005/ and batch_006/ per the batch_001 convention, sidecars
  kept. `clean/` is empty again. **batch_006 is closed** except `APFCompact_Ptacek_2024_DASS-21`
  (held on #1653) and `arnulf_2022_conspiracy_thinking` (blocked at extraction); its sidecars still
  document all 12 tables the batch claimed.

## batch_007 — 2026-08-17

12 claimed, **11 written, 1 blocked** (8.3%). audit_batch.R: 9 PASS + 2 WARN, both explained in notes.csv
(neither is an itemtext defect). Verification: 4 VERIFIED, 1 NO_ROUTE, 7 NOT_NEEDED.

**Blocked:** `atmadjaja_2026_pos` — the figshare xlsx has bare headers (CQ1-4/POS1-4/EWE1-4/ITS1-4), no
codebook, no labels, no second sheet, empty figshare references, and no companion paper locatable by
title or by any of the three author names. Honest no-source block.

**TWO BAD SOURCE LABELS, of different kinds — the notable finding of this round.** The core model ranks
source labels first; both of these would have shipped wrong text to anyone who trusted them blindly:
1. `bakker_2020_rses` (NOT yet extracted, warned in advance): in the shared PLOS .sav, five of seven
   labelled RSES columns contradict their own column names (`satisfied301` is labelled "I feel that I'm
   a person of worth"; `goodqualities303` is labelled "...I am a failure") and three columns have no
   label at all. Filed as #1654 before extraction. Its sibling `bakker_2020_pss10` is unaffected and
   shipped.
2. `baka2023_bpnsf`: the .sav's VALUE labels state 1 = "Strongly agree" ... 7 = "Strongly disagree",
   but the data say otherwise. Verified independently by the orchestrator: the 24 items split into two
   clean blocks (within-block r 0.37/0.44, between -0.23); one block correlates +0.37 with the same
   study's work-engagement mean and the other negatively; and the Polish item content identifies the
   positive block as SATISFACTION ("poczucie wolności i swobody wyboru") and the negative as FRUSTRATION
   ("czuję się wykluczony/a"). Under the file's stated direction a satisfaction item would have to
   correlate negatively. Anchors shipped reversed, documented. NOTE the diagnostic needs both halves —
   correlation alone fits either direction until item content fixes which block is which.

Both are now in SKILL.md core model §2, along with Stata's 80-char label cap (vs SPSS's 255) and the
do-file `label variable` recovery route, found via `audretsch_2021_entrepreneurial_ecosystems`.

**Needs a human decision:** `artistic_preferences` ships 30 of 56 items with NO stem text — they are
painting-PAIR stimuli with no verbal prompt (images ship in the archive), the same no-stem case as a
forced-choice instrument. Its opaque name also hides three instruments (APS 1-30, TIPI 31-40, a
16-word vocabulary check list 41-56); the dictionary description covers only the first.
`arzamoncunill_2023_epq_clinical` ships the supplement's short CATEGORY DESCRIPTORS rather than literal
stems, because the study published full Spanish wording only for the 26 items retained in its final
questionnaire while the live table holds all 22 clinical items of the 43-item pretest pool.

**TRIAGED 2026-08-18.** Gates re-run live: `normalize_nulls.R` clean (0 of 11), `audit_batch.R`
9 PASS + 2 WARN (both already explained in notes.csv, neither an itemtext defect).

- STAGED IN `clean/` (11 -- the whole written batch): artistic_preferences,
  arzamoncunill_2023_epq_clinical, audretsch_2021_entrepreneurial_ecosystems,
  autonomysupport_mokken, avilesgonzalez2019_ces, baaziz_2023_sms2, baka2023_bpnsf,
  baka2023_jcs, baka2023_olbi, baka2023_uwes, bakker_2020_pss10. Nothing held.
- **`artistic_preferences` decided by Ben (2026-08-18): ship all 56 as-is**, blank `item_text` for
  the 30 painting-pair items with the public_note explaining the images, matching the
  `aguirre_camacho_2021_shai` / `alsuhibani_2022_npi_s3` precedent. The alternatives considered were
  shipping only items 31-56 (fails validate_items.R by design) and holding the table.
- **The `baka2023_bpnsf` anchor reversal was independently re-verified** (notes.csv asked for a human
  check before upload). Sorting the 24 items by CONTENT rather than canonical item number gives a
  clean split against the UWES mean (0-6 Never..Always, unambiguous): all 12 positively-worded items
  +0.28..+0.40 (freedom of choice +0.37, "did things that really interest me" +0.40), all 12
  negatively-worded -0.03..-0.22 ("I feel excluded" -0.11, "I feel like a failure" -0.18). The .sav's
  stated direction would require the opposite. The shipped reversal is correct.
- Other independent re-checks, all clean: all 70 `baka2023_*` item texts exact against the .sav
  labels; `audretsch` 15/15 prefix-match against the .dta, with every label at exactly 80 chars
  extended by the do-file and every label under 80 matching to the character -- textbook Stata
  truncation; `artistic_preferences`' positional map reproduced from the raw data.csv (56 columns
  ra1a..v6a, tipi1-10, vcl1-16, so item 31 = tipi1 and item 41 = vcl1); `avilesgonzalez2019_ces`
  30/30 and `bakker_2020_pss10` 10/10 against their .sav labels. Note the PSS-10 sibling's column
  names and labels AGREE at all 10 positions -- the naming defect was specific to the RSES table.
- **`baaziz_2023_sms2`: the "unexplained" items 16-18 mean gap is the study's own supplements
  disagreeing.** Concatenating the CFA and EFA halves does not reproduce the "Totale" file that IRW
  is built from (Item17 off by 0.43, Item16 by 0.30, while Item4/5/18 match exactly). The paper's
  Table 2 matches the Totale file for items 1-15. Separately the item-16 evidence is stronger than
  the note's "looks unreliable": its printed text is external-regulation content, but it correlates
  0.88-0.90 with items 17/18 and 0.02/0.04/-0.03 with the three external items, so position 16 is an
  amotivation item and Table 7 almost certainly misprinted its wording. Neither affects the item
  mapping, which is a header label match. Not filed as an issue -- both are upstream of IRW.
- ISSUES PAGE: 10 callouts added (now 49 total). Omitted: `bakker_2020_pss10` (no caveat) and
  `atmadjaja_2026_pos`, whose auto-generated callout is again templating noise over a blocked table
  that shipped no text -- the second round where `draft_issues_qmd.R` has done this.
- **#1655 commented**: `baka2023_olbi` ships 8 of the OLBI's 16 items, a third instance of that
  pattern -- though here the study's own .sav holds only 8, so it may be a short administration
  rather than a processing-script drop.
- **Post-triage follow-ups (2026-08-18).** Independent per-item `resp` coverage check across all 11
  staged tables: **0** items missing an option row for a level their own respondents used, **0**
  option rows for unused levels, **0** duplicate (item,resp) pairs. This is the check
  `validate_items.R` cannot do, since it compares the resp SET over the whole table;
  `artistic_preferences` is the good test case, spanning 8 distinct resp values because APS is 1-5,
  TIPI 1-7 and the vocabulary list 0/1, with every item's own range covered.
- `autonomysupport_mokken` was the one table nobody had independently re-read (the `mokken` package
  was not installed). Ben installed it; verified against `man/autonomySupport.Rd`: all 7 item texts
  exact against the Rd's Content column, item codes are the Rd's Short names and the package
  colnames, anchors verbatim from the Details section (1 = "not at all/never", 5 =
  "certainly/always"; 2-4 genuinely undocumented). "(inversely coded)" is correctly stripped from
  `Decide` -- it is an annotation, not item text -- and `Choose` really does have only levels 1-4 in
  the package data, so its 4 option rows are right. **All 11 staged tables are now independently
  verified.**
- Ben's call on the two remaining judgment items (2026-08-18): **disclose, don't change the data.**
  Both issues-page callouts strengthened accordingly -- `baaziz_2023_sms2` now states plainly that
  the text shown for item 16 is probably not the item respondents answered and should not be used as
  its wording, and `arzamoncunill_2023_epq_clinical` now opens by saying none of its item text is the
  wording respondents read.

- UPLOADED 2026-08-18 (11): all 11 staged tables. Stamped in `itemtables/batch_007/provenance.csv`
  and `mapping_verification.csv`; the uploaded CSVs removed from batch_007/, sidecars kept. `clean/`
  is empty again. **batch_007 is closed** except `atmadjaja_2026_pos`, which was blocked at
  extraction and never wrote a CSV.
- WORKFLOW CHANGE (Ben, 2026-08-18): the agent now **edits `irw_site/itemtext_issues.qmd` directly**
  instead of leaving drafts for a human to paste. SKILL.md Step 6c and the audit-mode yellow bullet
  updated, including the correct path (`../../irw_site/` from `itemtext/`, not `../irw_site/`), the
  requirement to apply the issues-page bar and log the drops, and the standing warning that
  `draft_issues_qmd.R` emits a nonsense callout for blocked tables. BATCH_PROCESS.md gains a
  **Triage and staging** section — the protocol had none, which is why the step had to be explained
  from scratch mid-round.

## batch_008 — 2026-08-17

12 claimed, **12 written, 0 blocked** — the first full round. audit_batch.R: **12/12 PASS**.
Verification: 11 VERIFIED, 1 NOT_NEEDED. (An initial ERROR on `boyd_prism_2024` was a transient
irw_fetch failure; the table fetches fine on retry, 606 ids / 22 items.)

**`bakker_2020_rses` RESOLVED — and it overturned my own #1654.** I had filed that issue concluding
the .sav's column NAMES looked right and the labels shuffled. The opposite is true, and the data
settle it: `goodqualities303` is labelled "...I am inclined to feel that I am a failure" and sits at
the FLOOR (mean 1.5 of 4); `nogood302` is labelled "I have a number of good qualities" and sits at
the CEILING (3.3). A positively-worded self-esteem item cannot floor in a general sample. Read in
column order the labels reproduce a standard circulated RSES administration order (items
7,3,9,4,5,10,1,8,6,2); the names were assigned by numbering columns in Rosenberg's ORIGINAL order
without noticing the form was permuted. My issue also wrongly said three columns were unlabelled --
I had mis-transcribed their names (`usefull306`, `morerespect308`, `positiveattitude310`); all ten
are labelled. #1654 corrected and closed; SKILL.md §2 now says the name is at least as likely to be
wrong as the label, and to decide with keying polarity and item means rather than tidiness. The
table ships a public_note that its item codes must not be read as item content.
Bonus: the paper's Methods states the RSES ran 1=strongly agree..4=strongly disagree; cross-checked
against the PSS-10 in the same file, the .sav's opposite direction is correct and the paper is wrong.

**#1655 filed (`data fix`):** two tables ship fewer items than their source holds --
`anjum_2022_gad7` (6 of GAD-7's 7) and `bitew_2020_self_efficacy` (9 of the GSE's 10). The latter
also has an OFFSET: `SEFFICAY` is GSE item 1 and is dropped, so `SEFFICAn` = GSE item n+1. Verified
independently against the .sav labels (SEFFICA5 "can solve most issues" = GSE 6; SEFFICA6 "get
silent" = GSE 7 "remain calm"; SEFFICA7 "find options" = GSE 8).

**Other findings:** `beck_2021_iesr` uses a 4-anchor German IES-R and IRW stores the category index
1-4, NOT that version's 0/1/3/5 scoring weights -- summing `resp` gives a different scale from the
paper's (public_note). `bang_2023_self_esteem` had no item text at any level in its source, and its
order was reconstructed from keying polarity -- landing on the same permuted administration order as
the bakker labels, which is mutual corroboration. `bitew_2020_lte` is a MODIFIED 12-item LTE (items
reordered, item 12 not an LTE-Q item), so canonical wording was deliberately not substituted.
`data/beck_2021_covid_burden.py` reads a local xlsx that is not in the repo -- a reproducibility gap.

**TRIAGED 2026-08-18.** Gates re-run live: `normalize_nulls.R` clean (0 of 12), `audit_batch.R`
**12/12 PASS**, no anomalies. Independent per-item `resp` coverage check: 0 gaps and 0 duplicate
(item,resp) pairs across all 12.

- STAGED IN `clean/` (12 -- the whole batch, nothing held or blocked).
- **11 of the 12 re-verified against source by the orchestrator**, all clean:
  `bakker_2020_rses` (see below); `bakumenko_2023_adyghe_values` positional map reproduced from the
  raw workbook (item_1..7 = columns 6..12, the seven "Оцените важность..." headers, and the block is
  cleanly bounded -- column 13 starts a different question series); `bang_2023_self_esteem` polarity
  structure recomputed from the .xlsx; `bitew_2020_self_efficacy`'s +1 GSE offset checked label by
  label against the canonical GSE-10; `bitew_2020_osss3` canonical text and per-item anchor sets;
  `bitew_2020_lte`/`_phq9` against the .sav labels (PHQ8 ships the full two-part canonical item, not
  just the "so slowly" half its label emphasises); `benitezsillero_2021_bullying` 14/14 against the
  paper's Table 1 IMAGE; `boyd_prism_2024` 22/22 against the .rds haven labels after the documented
  `${Q2}` -> `[NAME]` substitution (the two unshipped labelled columns are `Often`/`Platform`,
  covariates, correctly excluded); `beck_2021_iesr` 22/22 against the German IES-R PDF including the
  pre-1996 orthography; `beck_2021_pss10`'s subscale split confirmed by the source column names
  themselves (PSS_PH_1,2,3,6,9,10 / PSS_PSE_4,5,7,8 = the canonical assignment). Only
  `bartoli_2022_badge_notifications` was not re-derived -- its item codes are the app names.
- **`bakker_2020_rses` confirmed independently, and the evidence is stark.** Per-column means on the
  1-4 Strongly Disagree..Strongly Agree scale: `goodqualities303`, labelled "...I am inclined to feel
  that I am a failure", = **1.47**; `nogood302`, labelled "I have a number of good qualities", =
  **3.27**. Every negatively-worded LABEL floors (1.47/1.54/1.94/1.99) and every positively-worded one
  ceilings (3.16-3.43). The labels win; the names are the wrong half. All ten columns are labelled.
- **`bang_2023_self_esteem` downgraded VERIFIED -> PARTIAL** in `verification_merged.csv` and
  `mapping_verification.csv`. Its own evidence string already said the routes pin polarity class and
  the position of S8 but NOT the order within each polarity block -- the status field overstated it.
  Recomputed from the .xlsx: positives {S1,S2,S4,S6,S7} +0.31..+0.73, negatives {S3,S5,S9,S10}, S8
  near-zero against the positive block except +0.50 with S10. That leaves 5!x4! orders consistent
  with the evidence; the shipped one is the standard administration order, an assumption. Shipped
  with a strong issues-page entry saying so, consistent with Ben's ship-and-disclose calls on
  `artistic_preferences`, `baaziz_2023_sms2` and `arzamoncunill_2023_epq_clinical`.
- **Convention worth knowing: "offered but unused" response levels are handled inconsistently across
  the corpus, and the gate forces it.** `boyd_prism_2024` keeps option rows for a level three of its
  items never saw (every item offered the full 5-point scale), which passes because other items in
  the table use that level. `arora2025_blueq_pedagogical` had to DROP its unused level 1, because no
  item in that table used it and `validate_items.R` compares resp SETS table-wide, so the extra row
  would fail the gate. Same situation, opposite output, decided by the gate rather than by judgment.
- ISSUES PAGE: 9 callouts added (now 58). Omitted: `bakumenko_2023_adyghe_values`,
  `benitezsillero_2021_bullying` and `boyd_prism_2024`, which carry no caveat.

- UPLOADED 2026-08-18 (12): the whole batch. Stamped in `itemtables/batch_008/provenance.csv` and
  `mapping_verification.csv`; uploaded CSVs removed from batch_008/, sidecars kept. `clean/` is empty
  again. **batch_008 is closed** — nothing held, nothing blocked, the first batch to close complete.
- **#1661 filed** (`data fix`): `data/beck_2021_covid_burden.py` reads
  `data/journal.pone.0250590_S1_Data.xlsx`, a local file that is absent from the working tree and has
  no git history, so the four `beck_2021_*` tables cannot be regenerated from a clean clone. The
  script's own header already carries the fetchable PLOS supplement URL, and 561 of the other
  `data/*.py` scripts fetch by `requests.get` — a small fix. Does not affect the shipped tables'
  correctness, only reproducibility.
- Already-tracked items from this batch, not re-filed: `bitew_2020_self_efficacy`'s 9-of-10 GSE
  coverage and code offset are in **#1655**, and `bakker_2020_rses` closed **#1654**.

## batch_009 — 2026-08-17

12 claimed, **12 written, 0 blocked**. audit: 11 PASS + 1 WARN (explained: `51_liking` exists only in
the brand-name subsample, so ~300 rows vs a 1,197 median — not conflation). Verification: 7 VERIFIED,
3 NO_ROUTE, 2 NOT_NEEDED.

**The round's major finding: the four `brand_raffaelli_2024_*` tables' item codes do NOT identify
brands, and one of them is mis-recoded.**
- The Qualtrics `.qsf` loop table is 59 rows x 10 brand fields with a BlockRandomizer assigning each
  respondent to one of ten brand lists, so `1_liking` is a loop POSITION carrying a different brand
  per condition. `data/brand_brand_raffaelli_2024.r` drops `Condition`, making the brand
  unrecoverable. Confirmed independently on the live table: no condition column, and pooled per-item
  means span only 4.05-4.70 across 59 supposed brands. Both agents reached this separately. No brand
  names were shipped as item_text — they would be wrong for ~90% of respondents. Filed **#1656**.
- **#1657 (verified against the study's own .qsf):** the `lp` (logo-Prolific) subsample of
  `brand_raffaelli_2024_liking_20` is recoded with a rotated choice map. `Logo_Controls_Prolific.qsf`
  defines choice id 9 = "Dislike 1" and id 8 = "Like 7", but the script maps 9→7 and 2→1. Every `lp`
  response is shifted one point down and **1,028 "Dislike" answers are stored as 7**. ~25% of the
  table's rows. The corrected distribution matches the sibling logo sample's shape; the shipped one
  does not.

**Second value-label override of the day, verified:** `burkert_2019_whoqol_bref` stores LQ3/LQ4/LQ26
already reverse-coded against its own value labels — 66.2% of respondents sit at LQ4=5 ("extremely
dependent on medical treatment") and all three correlate +0.39/+0.34/+0.53 with the other 23 items.
Anchors shipped reversed. This produced the generalisable rule now in route 6: **reverse-coding
status is a property of the TABLE, not the instrument** — the corpus holds WHOQOL-BREF stored raw in
`altahla_2024_whoqol` and pre-reversed here.

**Also new in the skill:** Step 4 now covers items whose wording varies per participant by design
(`buczel_2022_inoculation_belief`, six counterbalanced scenarios) and piped `${...}` tokens.

Other results: `broadband_inventories` is the 181-item AMBI — one instrument, not a battery, despite
the plural name — verified with max per-item mean difference 0.000 against the raw file (a
one-position shift gives 4). `bukurov_2022_sf36` shipped genuinely item-specific anchor sets across
6 real sections and confirmed direction against the file's own `_highgood` recode.

**TRIAGED 2026-08-18.** Gates re-run live: `normalize_nulls.R` clean (0 of 12), `audit_batch.R`
11 PASS + 1 WARN (the `51_liking` row-count anomaly, already explained and not code conflation).

- STAGED IN `clean/` (9): brain_hemisphere, brederecke_2020_phq4, brederecke_2020_sis,
  broadband_inventories, buczel_2022_inoculation_belief, bukurov_2022_sf36, burgess_2025_soas,
  burkert_2019_whoqol_bref, busch_2022_course_alleviate.
- **HELD (3) — Ben's call, 2026-08-18: hold all three `brand_raffaelli_2024_*` tables.** Each ships
  ONE sentence repeated across all 51-59 items (the rating stem) plus two anchor labels, because the
  item code is a randomised Qualtrics loop position and the processing script drops `Condition`, so
  brand identity is unrecoverable (#1656). No per-item information is conveyed. `liking_20` has the
  additional defect in #1657 (~25% of rows recoded with a rotated choice map, 1,028 "Dislike"
  answers stored as 7). The options offered were: ship two and hold `liking_20`; ship all three with
  callouts; hold all three. Revisit if #1656 is fixed by adding `cov_condition`, which would make the
  brand recoverable via Brands 2024.xlsx + the .qsf loop tables and turn these into real item text.
- Re-verified against source by the orchestrator: `broadband_inventories` **181/181** exact against
  the AMBI codebook (including the kept typo "when Im feeling badly"); `brain_hemisphere` 20/20
  against its codebook; `brederecke_2020_sis` — the reversal is not an override at all, the .sav
  names those two columns "SIS Item 4 recoded" / "SIS Item 9 recoded" and they are exactly the two
  negatively-worded items; `burkert_2019_whoqol_bref` recomputed from live data — LQ3/LQ4/LQ26
  correlate +0.18..+0.46 with unambiguously positive items and 52.5% of respondents sit at LQ3=5,
  confirming they are stored already-reversed and the shipped reversed anchors are right.
- ISSUES PAGE: **9 callouts added (now 67)** — all nine staged tables. The three held brand tables
  get none while held, the same treatment `APFCompact_Ptacek_2024_DASS-21` got in batch_006.
  I first omitted `brederecke_2020_phq4`, `burgess_2025_soas` and `brain_hemisphere` as
  caveat-free, then re-read them and reversed that: phq4 ships terse English data-file labels for a
  German administration AND anchors that differ from the published PHQ-4 ("On single days" for
  "Several days"); burgess has non-contiguous codes (SOAS5,7,9,10,11,12) pointing into a 13-item
  administration, with no labels in the source at all; brain_hemisphere's `instructions` field
  describes the response scale rather than quoting participant-facing text, and the dataset is the
  20-item version of a scale now published with 24. **None of the three had a `public_note` in
  provenance, so `draft_issues_qmd.R` generated nothing for them** — the drafting script only sees
  `public_note`, so a caveat recorded solely in `notes.csv` is invisible to it. Worth checking
  `notes.csv` directly during triage rather than trusting the draft set to be complete.

- UPLOADED 2026-08-18 (9): the nine staged tables. Stamped in `itemtables/batch_009/provenance.csv`
  and `mapping_verification.csv`; their CSVs removed from batch_009/, sidecars kept. `clean/` is
  empty again. **batch_009 is closed except the three held `brand_raffaelli_2024_*` tables**, whose
  CSVs stay in batch_009/ with blank `uploaded` stamps pending #1656/#1657.

## batch_010 — 2026-08-17

12 claimed, **12 written, 0 blocked**. audit: 11 PASS + 1 WARN (explained: `cacciatore`'s row-count
spread is applicability-driven missingness — a matrix rating care providers respondents only rated
if they encountered them). Verification: 4 VERIFIED, 4 PARTIAL, 4 NOT_NEEDED.

**Infrastructure failure worth noting:** group 3 (gai/gds/lsita) was killed by an API content-filter
error before it read anything — three tables lost to one failure. Re-dispatched as three SEPARATE
single-table agents and all three then passed, so the filter trip was spurious rather than anything
about the data. **Lesson: grouping three tables per agent means one infrastructure failure costs
three tables. Isolation retry is the right response, and finer-grained agents would reduce the blast
radius.**

**All five `buzgova_2023_*` tables share one `.sav` with NO labels at any level** (variable, value,
or variable_to_label — checked across all ~105 columns), so none could use `data_labels`. Each
established its scale direction from the data by a different route, and all five turned out to be
stored **already reverse-scored**:
- `rses` — all 45 inter-item r positive (0.12–0.63, none negative); alpha 0.806 vs the paper's 0.81.
- `soc` — the canonical SOC-13 reverse set {1,2,3,7,10} ranks **1st of all 1,287** possible 5-item
  subsets on method-factor strength; per-item means correlate r=0.87 with an independent Czech
  SOC-13 sample.
- `gds` — all 15 corrected item-totals positive; total mean 3.44/15 with 72.9% in the published 0–4
  "normal" band (the flipped reading would put the average respondent in the severe range).
- `lsita` — the raw column sum reproduces the paper's published total exactly (36.30/8.68/12–62 vs
  36.34/8.66/12–62).
- `gai` — all 20 item-rest correlations positive with low means, consistent with uniform anxious
  keying and nothing pre-reversed.
Consequence: `option_text` is deliberately NON-UNIFORM within `rses`, `gds` and `lsita` — reverse
items carry flipped anchors because that is how the data are stored. All carry public notes.

**Skill gained** (route 3): reproducing a published total settles subscale assignment AND stored
reverse-coding direction at once, since a scale summed the wrong way misses the published mean by an
obvious margin.

**Weakest table:** `buzgova_2023_rses` (PARTIAL). Because the data are pre-reversed the keying-polarity
route is dead, and an exhaustive search over all 252 five-item subsets found no reverse-wording method
factor to substitute. Its item order rests on "RSESn = Rosenberg item n" — the exact assumption that
proved FALSE in `bakker_2020_rses`. A candidate to hold.

**Also:** `busch_2023_stigma` does not measure stigma — its items are binary self-reports of
concealable identities and the survey's actual 4-point stigma measure is absent from IRW. Added as a
third case to #1651. Both `butt_2022` agents independently derived and verified the same
"code number = position within construct block" convention on their shared file.

**TRIAGED 2026-08-18.** Gates re-run live: `normalize_nulls.R` clean (0 of 12), `audit_batch.R`
11 PASS + 1 WARN (the `cacciatore` row-count spread, already explained as applicability-driven
missingness). **STAGED all 12, nothing held.**

- **`buzgova_2023_rses` shipped on Ben's call, with new evidence.** The round flagged it as a hold
  candidate: no labels at any level, data stored pre-reversed (so the polarity route that caught
  `bakker_2020_rses` is dead), leaving "RSESn = Rosenberg item n" as an unverifiable assumption —
  the very assumption that proved FALSE in bakker. The orchestrator found positive support for one
  position: **RSES8 has both the lowest mean (1.53) and the lowest item-rest correlation (0.36, vs
  0.40-0.57 for the rest)** — the known signature of Rosenberg item 8 ("I wish I could have more
  respect for myself"), the scale's classic misfitting item. The same signature sat at position 8 in
  `bang_2023_self_esteem`, and in the permuted bakker file position 8 was one of the three columns
  whose name and label agreed. Alpha 0.805 against the paper's 0.81. Positions 1-7, 9 and 10 remain
  unconfirmed. Recorded in the evidence string and stated in the callout. Options offered were ship
  with a strong callout / hold / ship item 8 only.
- **Paper-vs-data discrepancy confirmed on `buzgova_2023_soc`**: the paper reports Cronbach's alpha
  0.92; the released data give **0.765** (n=1096, corrected item-totals 0.29-0.53). Recomputed
  independently. Not filed as an issue — it is a property of the study's own release, not an IRW
  defect — but it is now stated in that table's callout, since anyone recomputing the scale hits it.
  `rses` (0.805 vs 0.81) and `gds` (total mean 3.44) reconcile fine, so it is specific to SOC-13.
- ISSUES PAGE: 10 callouts added (now 77). Only `butt_2022_task_tech_fit` and
  `butt_2022_user_satisfaction` carry no caveat. **Candidates were read from `notes.csv` directly**
  rather than from the draft script's output, per the batch_009 lesson.
- `busch_2023_stigma`'s table-name mismatch is already tracked as the third case in **#1651**.

- UPLOADED 2026-08-18 (12): the whole batch. Stamped in `itemtables/batch_010/provenance.csv` and
  `mapping_verification.csv`; CSVs removed from batch_010/, sidecars kept. `clean/` is empty again.
  **batch_010 is closed complete** — nothing held, nothing blocked, like batch_008.

### State after batches 001 and 006-010 were triaged and closed (2026-08-18)

`mapping_verification.csv` now holds 111 rows, 102 of them stamped as uploaded:
**60 VERIFIED, 31 NOT_NEEDED, 12 PARTIAL, 8 NO_ROUTE.** Seven tables remain written but unshipped,
each for a stated reason:

| table | batch | why it is held |
|---|---|---|
| `abdullah_2024_hpbbloat_stress` | 001 | `reconstructed` mapping, NO_ROUTE, 3 items |
| `algner2022_oss` | 002 | 2 of 6 items have no recoverable text |
| `ALSECYPIAMH_WU_2022_PHQ` | 004 | unverifiable 2-item mapping (#1643) |
| `APFCompact_Ptacek_2024_DASS-21` | 006 | complete duplicate of `ptacek2023_dass21` (#1653) |
| `brand_raffaelli_2024_liking_20` | 009 | loop-position codes (#1656) + rotated choice map (#1657) |
| `brand_raffaelli_2024_liking_24` | 009 | loop-position codes (#1656) |
| `brand_raffaelli_2024_familiarity_24` | 009 | loop-position codes (#1656) |

Plus two honest extraction blocks that never wrote a CSV: `arnulf_2022_conspiracy_thinking` (007)
and `atmadjaja_2026_pos` (007), and `agarwal_2023_dreem` (001, copyrighted DREEM).

## batch_011 — 2026-08-18 — extracted and gate-verified; UNTRIAGED. Blockers cleared 2026-08-24.

### Incident: the Redivis export quota was exhausted, and it was this round that did it

**RESOLVED 2026-08-24 — see "Both blockers cleared" at the end of this section. The account
below is kept because the arithmetic that caused it still holds; the state it describes does not.**

**`irw_fetch()` is dead account-wide until the 30-day export window rolls over.** Confirmed
first-hand by calling Redivis directly, which gives the error `irw` hides:

```
[400 invalid_request] Cannot export more than 200GB within a 30 day period,
unless the dataset's owner has configured an export billing project.
You have exported 204GB in the past 30 days...
```

`tbl$get()` still works (metadata, row counts); only data export is blocked. This affects everything
that calls `irw_fetch` — the metadata pipeline, vignettes, other sessions — not just itemtext.

**Attribution, corrected 2026-08-18 after measuring rather than assuming.** My first writeup said
this round caused the exhaustion. That is overstated, and the numbers say so: the twelve round-1
tables total **10.1 GB** for one full export each (`condon_2024_sapa_personality` 4.55 GB,
`criticalperiod_syntax` 3.31 GB, `ftna_kasper_2022` 0.68 GB, the rest under 0.6 GB). Add this
session's triage — `audit_batch.R` over batches 007-010 (47 mostly-small tables), three
`resp_check.R` passes, assorted single fetches — and the session's plausible total is on the order of
**15-25 GB**, not 204 GB. The round was the straw, not the load.

What actually consumed the other ~180 GB inside the rolling window is not determinable from here
(other sessions, vignette work, the tag pipeline and the manuscript analyses all fetch tables, and
`metadata/01_metadata.R` has a `to_tibble()` fallback for any table whose server-side `resp` count
comes back NULL). **The structural fact is the one that matters: the core warehouse is 181.8 GB
across its four datasets, so any workflow that exports every table once consumes ~91% of the monthly
allowance in a single pass.** With a cap that tight relative to the corpus, exhaustion was going to
happen; this round is simply when it did.

The pipeline-side lesson stands regardless: `irw_fetch` always exports the whole table, and the hard
gate it feeds (`validate_items.R`) needs only `unique(item)` and `unique(resp)` — a few dozen values.
Egressing 68 million rows to compute 135 item codes is indefensible whoever spends the quota.

**Compounding it, the error is misreported.** `irw:::.irw_handle_datasource_error` returns
`invisible(NULL)` for any error that is not invalid/auth/not_found whenever more than one core
datasource is configured — which is always — so `fetch_single_data` falls through to
`"table does not exist in IRW"`. Four agents independently concluded their table had been removed
from the warehouse, and two wrote that into their notes before the real cause was found. Filed as
**#1663**, together with the whole-table-export design.

### BOTH PACKAGE-SIDE PROBLEMS ARE FIXED — Rpkg#121 (Ben, 2026-08-18)

Branch `fix/quota-errors-and-table-sets` on itemresponsewarehouse/Rpkg, see #1663:

- **Error classification.** `.irw_handle_datasource_error()` now classifies export-quota /
  rate-limit / `RESOURCE_EXHAUSTED` as a `"quota"` error and stops immediately, saying it is an
  account-wide export limit rather than a problem with the table. The check runs BEFORE the
  `invalid_request` check, since the quota failure arrives as `[400 invalid_request] Cannot export
  more than 200GB…`. Unclassified errors are collected across the four datasources and re-raised, so
  **"does not exist in IRW" now means all four genuinely returned not-found.** That single message
  produced three wrong conclusions in one evening (four agents deciding their table had been deleted,
  and my own repeated claim that `emidy2024_fevs` was not uploaded).
- **`irw_table_sets(name, source = "core", per_item = FALSE)`** — the server-side path, now in the
  package: row count, item set, resp set, optionally per-item n / resp min / max / level count, with
  the literal `"NA"` token dropped so it matches what `irw_fetch()` returns. Validated live:
  `condon_2024_sapa_personality` gives 135 items and resp 1-6 in **13 seconds with no export**,
  against a 4.55 GB download; `criticalperiod_syntax` (107M rows) likewise.
- Also in the PR: `irw_info()` no longer calls `to_tibble()` just to read column names.

**Consequence for this pipeline — DONE 2026-08-24.** `scripts/table_sets.R` and the inline query
helper in `audit_batch.R` were both interim copies of the shard-resolution logic. Both now call
`irw::irw_table_sets()`; `table_sets.R` is a thin CLI wrapper over it. One correction to the plan
recorded here: `per_item = TRUE` turned out NOT to be the right call for `audit_batch.R`. It returns
each item's resp min/max and level *count*, but the per-item coverage check needs the actual *set*
of levels an item's respondents used — that is the check that caught the `alkouri_2025_*` defect —
and its `n` counts only non-missing resp, where the row-count anomaly check wants each item's total
rows, missingness included. So `audit_batch.R` takes the canonical item/resp sets and the resolved
qualified reference from the package and runs one further `GROUP BY` for the per-item detail. Still
no export. Re-run over batch_011 afterwards: byte-identical to the shipped `audit_report.csv`,
7 PASS / 5 WARN.

Possible Rpkg follow-up: a `per_item` variant that returns the per-item resp *set* and total rows
would let `audit_batch.R` drop its remaining query.

**`metadata/01_metadata.R` — also done.** which lives outside the package repo and was not
touched. Its `get_statistics()` path is fine; the problem is the fallback, which drops to
`to_tibble()` on the FULL table whenever a table's `resp` count comes back NULL. Run across the whole
corpus, hitting that fallback on a handful of large tables makes a real dent in the 200 GB window and
hitting it broadly exhausts it. Replacement is a `SELECT COUNT(DISTINCT …)` / `GROUP BY` on the
table's `qualified_reference` — reuse `irw_table_sets()` once the PR lands, or inline the query if
the script shouldn't depend on the package.

**And the export billing project on the datapages datasets is still the fix that removes the cap
without every caller changing — still outstanding, and now the only part of this that is.**

### Both blockers cleared — 2026-08-24, verified live

- **Rpkg#121 landed.** Installed `irw` is 1.0.1; `irw_table_sets(name, source = "core", per_item =
  FALSE)` is exported with exactly the signature the PR described, and
  `.irw_handle_datasource_error()` carries the `"quota"` branch. Checked live:
  `irw_table_sets("machivallianism_test_main")` → 1,469,720 rows / 20 items / resp 1–5;
  `irw_table_sets("chen_2022_sasc")` → 1,698,642 rows / 22 items / resp 1–5. Seconds, no export.
- **The export quota has rolled over.** `irw_fetch("machivallianism_test_main")` returned 1,469,720
  rows with no `[400 invalid_request]`. So the round's held-over instruction to "re-run
  validate_items.R once the quota resets before uploading" (recorded in `notes.csv` for
  `close_relationships` and others) is now actionable.
- **`metadata/01_metadata.R`'s `to_tibble()` fallback is gone**, replaced by a
  `redivis$query(sql)$to_tibble()` at line 86, with the change recorded in the comment at line 60.

**batch_011 is therefore unblocked and its next step is triage** (`BATCH_PROCESS.md` §"Triage and
staging"), with two things carried in from this round: `verify_geography.R` is the only agent script
written against `irw_fetch` rather than the query path, and `geography` is flagged on the index
workbook's `xz_todo` tab, so confirm nobody is mid-work on it before it ships.

### The interim fix: `scripts/table_sets.R`

Server-side aggregates are unaffected by the export limit. `table_sets.R <table>` resolves the table
across the four core datasources and returns the item set, the resp set and per-item n/range from
`GROUP BY` queries — quota-free, seconds rather than minutes, and it works right now while
`irw_fetch` does not. Validated against two tables whose sets were known independently
(`rosenberg_selfesteem`, `bakker_2020_rses`). Two details it has to get right and does: `resp` is
stored as a STRING carrying a literal `"NA"` token, which must be excluded and cast, or the resp set
gains a phantom level and MIN/MAX come back NA.

**`validate_items.R` should be rewritten on top of this** — not done yet, deliberately, because
agents were still reading that file mid-round.

### Round status: 12 dispatched, **12 written, 0 blocked** — but NOT gate-verified

One agent per table, at the top 12 in-scope tables by volume (`neurips_2020` pulled before dispatch:
27,613 image-stimulus items, a different deliverable, still `pending`). **Round 2 of the pilot was
NOT dispatched** — with `irw_fetch` down there is no hard gate to run, and thirteen more agents
would produce unvalidated output. Those 13 tables stay `pending`.

Sidecars merged; queue reconciled (nothing left `in_progress`); `mapping_verification.csv` now holds
123 rows. Verification: **4 VERIFIED, 2 PARTIAL, 6 NOT_NEEDED**; bases: 8 `data_labels`,
2 `paper_explicit`, 2 `reconstructed`; 9 of 12 carry a public_note.

> **UPDATE 2026-08-18, later the same evening: THREE OF THE FOUR GATES NOW PASS.** The quota blocks
> *exports*, not *queries* — so the gates' substance can be run without egress after all.
> - **Item/resp sets vs live data, via server-side `SELECT DISTINCT`: 12/12 PASS.** Every table's
>   item set and resp set match the live warehouse exactly (`geography` 1458/1458, `sapa_personality`
>   696/696, `condon_2024_sapa_personality` 135/135). That is `validate_items.R`'s substance.
> - **`verify_batch.R`: 6 PASS, 1 NO VERDICT, 5 MISSING(exempt)** — and it ran for real. Six of the
>   seven agent-written scripts re-ran their own evidence live and passed. The exception is
>   `verify_geography.R`, which was written against `irw_fetch` rather than the query path and dies
>   on the quota error; its mapping is nonetheless confirmed by the SQL gate above. **This is the
>   pilot's headline measurement: evidence-as-code works.**
> - **`normalize_nulls.R`: clean, 0 of 12 changed.**
> - **`audit_batch.R` rewritten onto the query path and run: 7 PASS + 5 WARN, item and resp sets
>   TRUE for all 12.** Everything it needs from live data — the item set, the resp set, each item's
>   own resp levels, each item's row count — is a single `GROUP BY`, so it no longer downloads the
>   response tables at all. `irw_fetch` survives only as a fallback if the query route itself fails.
>   All five WARNs are the row-count-spread check firing on things the extracting agents had already
>   documented, and each is now explained in `notes.csv`: FEVS routes q82-q84 to respondent subsets;
>   `ftna_kasper_2022`'s three shared subject codes appear in both waves; `geography` is an ADAPTIVE
>   practice system so per-item n varies by design; `sapa_personality` uses planned missingness;
>   `twod_rotation_mather2023` has 70 retained items at n>10000 against 234 pilot items near 1,224,
>   plus the expected 100% blank item_text for an image-stimulus instrument. **No defects.**
>
> **All four gates have now run. batch_011 is fully verified and ready to triage.**
>
> **`emidy2024_fevs` IS live** — 49M rows, 1.76 GB, in `item_response_warehouse_3`. Its agent
> reported the table as not-yet-uploaded; that was the misleading "table does not exist in IRW"
> error again, and I repeated the claim before checking. The 761MB TODO entry is stale.
>
> Original note, still true of `audit_batch.R` only:
> Each agent satisfied the gate's *substance* by other means (the `table_context.R` fetch that
> succeeded before the quota tripped, plus server-side aggregate queries), and the CSVs pass a local
> structural check — correct columns, no `raw_resp`, no duplicate (item,resp) pairs, row counts
> reconciling against each table's scale structure. But the gates themselves have not run. Run all
> four when the export window rolls over, THEN triage. Nothing is staged in `clean/`.

**On the pilot's actual question — can agent-written evidence replace hand re-derivation? Yes, and
better than expected.** Two examples worth reading before designing the next round:

- `twod_rotation_mather2023` had no prose stems to transcribe (algorithmically generated hexomino
  figures). It took the `artistic_preferences` shape, then recovered the instruction line by reading
  it off the stimulus PNGs and pixel-hashing the headers to confirm it identical across all 304. It
  verified against the paper's Table S7 (58 published Ns match the live row counts EXACTLY, r=0.9999
  on proportion correct), then mechanically recovered each figure's target rotation from the images
  and showed the 12 items the study's own code drops as "not requiring mental rotation" all come out
  at 0° — 12/12 against a 25.7% base rate, p=8.1e-08. And it still filed PARTIAL, because the 304
  figures reuse only 111 distinct stimulus panels so panel-mates cannot be separated.
- `criticalperiod_syntax` reconstructed per-item scored accuracy from the raw per-option endorsement
  file and matched live means at r=0.9812 against a permutation null of 0.353 — then filed PARTIAL
  because 4 option pairs rest on a global convention rather than their own numbers.

Both applied the strict VERIFIED definition against their own interest in claiming a clean result,
which is exactly what that change was for. 7 `verify_<table>.R` scripts were written (the 5 missing
are `data_labels`, correctly exempt) and several default to server-side queries rather than
`irw_fetch` — the agents found that workaround independently, mid-round.

**Step 3b findings: three tables in one round pool instruments under a name signalling one, and all
three are openpsychometrics-style releases.** `riasec` is only items 1-48; 49-58 are the TIPI and
59-74 a 16-word vocabulary check. `depression_anxiety_stress` is DASS-42 + TIPI + the same
vocabulary check. `chen_2022_sasc` is worse than pooled — it is outright misnamed: not the Social
Anxiety Scale for Children but the 22-item **Smartphone Addiction Scale for College Students**,
confirmed from the source .sav's variable labels and its own `PSU` total-score column. The
dictionary Description needs correcting; this looks systematic for that source and is worth a
standing note in SKILL.md.

Other findings: `ftna_kasper_2022`'s items are whole-subject exam grades, not questions, and its
0-4 → E-D-C-B-A scale was pinned twice from the study's own do-files. `geography` ships the place
type alongside the name (`Georgia (country)` vs `Georgia (region)`) because 46 names are shared by
two places — an annotation, disclosed. `emidy2024_fevs` is not live in IRW at all (761MB upload
still open in `automated_finding/TODO.md`), and OPM has REDACTED the DEIA item text from the
technical report it currently serves, so that wording came from a Wayback capture.

`geography` shows as PRESENT on the index workbook's `xz_todo` tab — probably flagged-for-later
rather than claimed, but confirm nobody is mid-work on it before shipping.

**Process finding: the session scratchpad is shared across parallel agents.** Two agents
independently reported a sibling overwriting their `cand.csv` mid-run, one wasting a retry on the
resulting spurious failure. Now fixed in BATCH_PROCESS.md — scratch files must be namespaced under
`.cache/<table>/`. A subtler collision could ship one table's rows under another's name, and neither
`validate_items.R` nor `audit_batch.R` would catch it.

### Skill changes 2026-08-18 (the "now" phase, before scaling the pipeline)

Four changes, each pinned to something that actually went wrong in batches 006-010.

1. **`verify_<table>.R` is now required for every non-`data_labels` table** — a re-runnable version
   of the Step 5b evidence, written by the extracting agent, alongside the CSV. Prose evidence
   ("per-item means 4.80, 4.85 ... match Table 1") cannot be re-run, so triaging 006-010 meant
   re-deriving ~11 of every 12 tables by hand; that was the whole cost of triage. Contract: fetch
   your own data, print the numbers compared, last line exactly `VERDICT: PASS`/`FAIL`, verify the
   MAPPING not the plumbing. `references/verify_template.R` is a working example (the real
   `arora2025_blueq_pedagogical` check — it runs and passes against live data), and
   `scripts/verify_batch.R` runs a whole batch and reports PASS/FAIL/MISSING, with
   `MISSING(exempt)` for `data_labels` tables.
2. **`draft_issues_qmd.R` fixed on both counts.** It no longer emits a callout for tables that
   shipped no CSV (the "the origin of the item text was not recorded" nonsense that appeared for
   `arnulf_2022_conspiracy_thinking` and `atmadjaja_2026_pos`) — and it distinguishes "blocked" from
   "already uploaded" by provenance's `uploaded` stamp, so re-running it on a closed batch still
   drafts correctly. It now also prints a **REVIEW THESE TOO** section listing every shipped table
   that earned no draft, with its `notes.csv` text, which is the blind spot that cost three
   batch_009 callouts: the drafter only ever sees `public_note`.
3. **`scripts/lint_verification.R` (new)** — catches a status claiming more than its evidence
   supports. Regression-tested against the bug that motivated it: with `bang_2023_self_esteem`
   flipped back to VERIFIED it fires on that row's own words ("...not the order within each polarity
   class, so adjacent same-polarity swaps are not independently excluded"). The hedge list was
   deliberately narrowed after a first pass produced mostly false positives — words like "ambiguous"
   and "underpowered" show up in good evidence describing a rival route that failed. On the current
   111-row corpus it reports 0 ERROR and 7 WARN, and those 7 are a real historical finding: rows
   from batches 001-005 marked NOT_NEEDED while their `mapping_basis` is `paper_explicit`, which
   SKILL.md does not exempt. SKILL.md now also defines VERIFIED strictly — the route must
   distinguish every item from every other; pinning a class, block or subset is PARTIAL.
4. **One agent per table, not groups of three.** batch_010 lost three tables to one content-filter
   error and all three passed on individual retry. Twelve agents sit under the concurrency cap, so
   this costs no wall clock and makes a failure's blast radius exactly one table.

Both the triage section and the round-trigger prompt in BATCH_PROCESS.md were updated, so a
stateless cron firing picks all of this up.

### Standing exclusion added 2026-08-18: `enem*`

Ben: **do not extract ENEM item text — it is being handled separately.** The 52 `enem*` rows are
now `status=excluded` in `queue_state.csv` (a new status; only `pending` rows are claimable), and
the exclusion is written into BATCH_PROCESS.md's state table, its Standing exclusions section and
the round-trigger prompt, plus SKILL.md.

Queue is now **1,176 pending** (was 1,228), 109 done, 11 failed, 52 excluded.

This changes every volume statistic quoted for this pipeline, because the ENEM tables dominate the
corpus: they are **2.12 billion of the 2.44 billion pending responses, 87% of all pending volume**.
Restated on the remaining 1,176 tables (320M responses):

| non-enem pending tables | share of non-enem pending response volume |
|---|---|
| top 25 | 93.5% |
| top 50 | 96.0% |
| top 100 | 97.7% |

So the priority-block argument survives — it just gets cheaper. Roughly **two rounds over the top 25
non-enem tables covers 93.5%** of the volume that is actually in scope, rather than five rounds over
50. The largest in-scope tables are `criticalperiod_syntax` (107M) and `condon_2024_sapa_personality`
(68M), which between them are more than half of all remaining pending volume.

## batch_005 retry — 2026-08-18

Re-attempted the 4 tables `batch_005` left BLOCKED. **1 written, 3 still blocked** — but all
four now have a settled answer rather than a "retry later".

**`american_multiracial_face` — RESOLVED.** The original block was based on a false premise: 9 of
the 19 rater-level `.sav` files were reported missing from the paper's OSF project (osf.io/qsdrp).
All 21 are present; the earlier listing failure was transient. The table's 2,252 bare-integer items
were reconstructed by re-running `data/american_multiracial_face.R`'s own logic — alphabetical
`ls()` → `mget` → `rbind` of the 19 files it reads, drop `rating==0`, `unique(case_lbl)` →
`row_number()` — and the reconstruction is **exact**: 2,252 unique case labels and 117,880 rows,
per-item n identical for all 2,252 items, per-item means agreeing to max |diff| 5.3e-15 (cor =
1.000) against `irw_fetch()`. Each case label encodes attribute + face + expression version
(`Amb_F2`, `RaceProt_F100S_6`), and the attribute was assigned **by source file**, not by parsing
the label, so no inference entered. Wording and 1–7 anchors are verbatim from the study's own OSF
codebook. Attribute-block means independently corroborate the published norms over the smaller
released face set (ambiguity 3.662 vs 3.649; expression 3.937 vs 3.964; masculinity/femininity
4.727 vs 4.783; White prototypicality 3.745 vs 3.770; attractiveness 4.636 vs 4.641).

**Generalisable rule (new): when the IRW item code is an order-dependent integer assigned inside
the processing script, re-run the script rather than trying to infer the order.** The script is
deterministic, the raw files are usually still on the source repository, and per-item n/mean give
an exact, falsifiable check on the result — a stronger verification than any statistical route in
Step 5b. Both prior rounds treated "arbitrary integer assigned across a 19-file rbind" as
inherently unrecoverable; it is not.

Its 2 audit WARNs are both expected: 71.4% blank `option_text` because the survey labelled only
scale points 1 and 7, and the row-count flag because rating counts vary by design (raters saw
subsets; n runs 32–71 around a median of 52, and the low end is the smile-genuineness block, where
"0 = N/A this person is not smiling" is recoded to NA by the script).

**Response-data gap found (not an itemtext defect).** `data/american_multiracial_face.R` reads 19
of the 21 available `.sav` files, silently omitting `Smile_Black_prototypicality_trans.sav` (6,202
usable ratings of 119 smiling faces) and `Neutral_Smile_final_trans.sav` (4,322 ratings of 118
neutral faces). Black prototypicality is the only one of the six racial-prototypicality traits with
no smiling-photo ratings in the IRW table. Filed as ben-domingue/irw#1660.

**The three `amorim_2025_climej_*` tables — still blocked, but the reason has changed.** The AWS
WAF challenge on Harvard Dataverse `doi:10.7910/DVN/DB8K7V` has cleared (the API returns 200), so
the deposit was finally inspected — and it does not contain the item text. Its single file,
`DadosPublicizados.xlsx`, has a `Dicionário` sheet that repeats the variable NAME in the "Questão"
column for all 128 CLIMEJ, 17 WQD and 9 EPSO items (`Questão` for CLIMEJ57 is literally
"CLIMEJ57"), and gives only scale width ("1 a 5 Concordância") with no anchor labels. So these are
no longer "retry when Dataverse is reachable" — the remaining routes are author contact, the
unpublished in-press CLIMEJ pilot paper, the Portuguese WDQ item bank, and the Gomide & Siqueira
(2008) book chapter.

**Lesson for the blocked bucket generally:** two of these four blocks were about *access*, and
access-based blocks are worth retrying cheaply, but the retry's real job is to convert "couldn't
reach it" into "reached it, and here is what it does or doesn't contain". Three of the four ended
up in the second state without any new item text, which is still a better outcome than leaving them
on a retry list forever.

## batch_011 TRIAGE — 2026-08-24

All four gates re-run live, no export spent (queries only; see the blockers-cleared note above).

- `audit_batch.R` — first re-run reproduced the shipped `audit_report.csv` byte-identically
  (7 PASS / 5 WARN). After the `criticalperiod_syntax` edit below it is 6 PASS / 6 WARN.
- `normalize_nulls.R --dry-run` — 0 of 12 files would change.
- `verify_batch.R` — **7 PASS, 5 MISSING(exempt)**, up from the round's 6 PASS + 1 no-verdict.
- `lint_verification.R` — 12 rows, 0 ERROR, 1 WARN (`condon`, see A below; the WARN is expected
  and correct — the evidence does still hedge, legitimately).

### verify_geography.R — converted off irw_fetch, and it found a real comparison bug

It was the only agent script with an unconditional `irw::irw_fetch()`. It needs per-item row count
and mean resp, i.e. one `GROUP BY`, so it now takes the qualified reference from
`irw_table_sets()` and queries it (irw_fetch kept as a fallback, as `verify_riasec.R` and
`verify_twod_rotation_mather2023.R` already do).

Running it then failed 1440 of 1458 items — **not a mapping defect, a missing-value convention
mismatch.** `geography` has 281,706 rows (2.8% of 10,087,305) with a missing `resp`: the
answer.csv events where the user gave no answer. The script's own definition,
`accuracy(place) = mean(place_asked == place_answered)`, scores a no-answer as 0; the IRW
processing script maps those events to missing instead. Score them as 0 on both sides and the
two agree on **1458/1458, max |diff| 5e-07**. VERDICT: PASS. Both the count fix and the
convention fix are in the script with the reasoning written down.

Worth knowing beyond itemtext: whether a slepemapy no-answer *should* be a missing resp or an
incorrect one is a live question about the response table, not about item text. Not filed.

### Decisions (Ben, 2026-08-24)

- **A. `condon_2024_sapa_personality` stays VERIFIED.** The stale half of its hedge — that
  `validate_items.R` could not be run — was a quota artifact and is deleted from the evidence;
  the item/resp gate was reproduced server-side and re-confirmed by `audit_batch.R` today
  (135/135, resp 1-6). What remains is that the four intermediate anchors are transcribed from
  the official SPI-135 form rather than re-derived, which is provenance of wording, not an
  unproven mapping. `lint_verification.R` will keep flagging it; that is the right behaviour.
- **B. `geography` ships.** The `xz_todo` check was waived.
- **C. `chen_2022_sasc` ships.** Ben has already made the SAS-C naming correction in the metadata.
- **D. `twod_rotation_mather2023` is HELD** from this upload — 100% blank `item_text` because the
  items are images, and a row with no item text was judged not worth shipping. Extraction is not
  in doubt (audit and verify both pass); CSV and sidecars stay in the batch folder.
- **D. `criticalperiod_syntax` ships WITH machine-generated picture descriptions.** Its six
  sentence-to-picture items (q1, q2, q3, q5, q6, q7) have two picture answer choices that the
  source prints only as figures. Those twelve rows now carry a description of each panel in
  `option_text`, prefixed `[machine-generated image description] ` — the only text in the table
  not transcribed from the source. The panel-to-resp assignment is not inferred: the SI answer key
  names the correct panel (1. Bottom, 2. Bottom, 3. Top, 5. Bottom, 6. Bottom, 7. Top) and these
  are two-alternative forced choices, so accuracy 1 identifies the chosen panel. Descriptions were
  written from `mmc1.pdf` pp.45-47 rendered at 300dpi; the thumbnails are genuinely misleading at
  low resolution (in q1 both animals run *rightward*, which reverses who is chasing whom), so
  zoom before describing.

  Consequence: the file goes from a uniform 100%-blank `option_text` (which passed) to 93.7% blank
  plus a new WARN, "89 of 95 items have NO option_text rows while others do". **That asymmetry is
  by design, not the `alkouri_2025_*` defect the check exists for** — the 89 grammaticality items
  are "choose all that apply", where accuracy 1 can mean selecting *or* not selecting the sentence,
  so no single option was chosen and a label there would be exactly the padding flagged on
  `agogue_2020`. Recorded in `notes.csv`.

### Issues page

`criticalperiod_syntax` callout written by hand and applied directly to
`irw_site/itemtext_issues.qmd` (79 entries now) — the drafter only sees `public_note`, so it
produced the q10_4 duplicated-label point but nothing about the machine-generated descriptions.
The 8 other drafts from `draft_issues_qmd.R` were then triaged against the page's bar (concrete
text-vs-table mismatches, not gaps the source never published) and **6 applied, 2 dropped**. The
page is at 85 entries.

- Applied as drafted, all four being cases where the table NAME misleads about its contents:
  `chen_2022_sasc` (SAS-C smartphone addiction, not Social Anxiety Scale for Children -- the
  dictionary Description is fixed but the table name still reads the wrong way, which is why this
  still earns a callout), `depression_anxiety_stress` (pools DASS-42 + TIPI + vocabulary check),
  `riasec` (only items 1-48 are RIASEC), `ftna_kasper_2022` (items are whole-subject exam grades,
  and the three core subjects reuse one item code across two different examinations -- a real join
  hazard).
- Applied trimmed, keeping only the half that clears the bar: `geography` (kept: the "(type)"
  annotation appended to each place name is added text, not part of the source name; cut: "the task
  published no options"), `sapa_personality` (kept: 17 of 696 items ship the dictionary's
  abbreviated shorthand rather than the sentence the participant read; cut: "the instruction text
  was never published").
- Dropped: `emidy2024_fevs` -- nothing mismatches, it records that the text came from OPM's
  published FEVS instrument because the .dta labels truncate at Stata's 80 characters, i.e. it
  describes doing the right thing. And `twod_rotation_mather2023` -- held, so there is no item text
  on the site to caveat; the draft is worth keeping if it ever ships.

**Lesson on the drafter:** it turns `public_note` into a callout mechanically and does not judge, so
it drafts for every table that has a note whether or not the note clears the bar, and misses
anything recorded only in `notes.csv`. Both halves of that showed up in this batch -- 2 of 9 drafts
did not belong on the page, and the `criticalperiod_syntax` machine-generated-description caveat,
the single most important one in the round, had to be written by hand.

### CLOSED 2026-08-24 — 11 of 12 uploaded

Ben confirmed the upload. `uploaded=2026-08-24` stamped on 11 rows in
`itemtables/batch_011/provenance.csv` and 11 `batch_011` rows in `mapping_verification.csv`; the
11 `__items.csv` deleted from the batch folder, sidecars and the seven `verify_*.R` kept. The held
`twod_rotation_mather2023__items.csv` and its unstamped rows stay in place.

`queue_state.csv` needed no edit — all 12 were already `done` from extraction time. Note that
`twod_rotation_mather2023` therefore reads `done` in the queue despite not being uploaded; the
queue has no `held` status, so the hold is recorded in `notes.csv` and here instead. Anyone
reconciling queue counts against what is live on the site should expect that one-table gap.

Batch totals for the round: **11 uploaded, 1 held, 0 failed.**

### Still open

Nothing. The six `notes.csv` entries that ended with "re-run validate_items.R once the quota
resets before uploading" (`close_relationships`, `emidy2024_fevs`, `ftna_kasper_2022`, `geography`,
`machivallianism_test_main`, `sapa_personality`) each carry a `[DISCHARGED 2026-08-24: ...]`
sentence saying the window rolled over, Rpkg#121 landed, and `audit_batch.R` re-checked the gate
against live data — so no future reader re-runs a gate on account of a note that outlived its
cause.

## TODO (added 2026-08-24, from Ben) — sweep the notes/flagged rows on the index workbook

Revisit the rows in the itemtext index workbook
(https://docs.google.com/spreadsheets/d/1jvwxYJ3gjSpEDtx4km-8czvDXu7iEIHhF5V5Y9VWNG0/edit?gid=0#gid=0)
that carry a note or are otherwise flagged — typically the ones with **no link to a Google Sheet
of item text**, i.e. tables whose processing was started and abandoned for some reason. Go through
those, work out why each stalled, and add the ones that can now be finished.

Scope notes for whoever picks this up:
- **Scope is `Sheet1` (`gid=0`) only** — per Ben, that's where the valuable notes live. The other
  tabs (`queue`, `xz_todo`, `nj_todo`, `tables_excluded`) are not part of this sweep.
- Expect a mix of causes: genuinely unavailable source text, access blocks that may since have
  cleared (see the batch_005 retry above — access blocks are cheap to retry and the retry's job is
  to convert "couldn't reach it" into a settled answer), items already extracted but never linked
  back into the sheet, and rows flagged-for-later by a human that nobody returned to.
- Cross-check against `extraction_batches/queue_state.csv` and the batch sidecars before
  re-extracting — some of these may already have text sitting in `clean/` or a staging dir that was
  simply never linked on the sheet.
- Anything `enem*` stays out of scope (Ben handles those separately).

## 2026-09-03 — index-workbook Sheet1 sweep (the 2026-08-24 TODO), and the queue restart

### The sweep

Sheet1 of the itemtext index workbook has **413 rows**; **100 are flagged** (90 carry a
note, 51 have no item-text link, 41 both). Cross-checked against `queue_state.csv`,
`availability_audit_full.csv`, `mapping_verification.csv`, the batch sidecars, and live
`irw_list_tables()` / `irw_list_itemtext_tables()` before anything was re-extracted, as the
TODO asked. Full per-row result: `extraction_batches/sheet1_sweep_2026-09-03.csv`.

The 100 split three ways:

| | n | what it means |
|---|---|---|
| already published | 27 | item text is live in `irw_text`. The flag is stale — the work was finished and never linked back on the sheet. |
| not an IRW table | 11 | absent from `irw_list_tables()` (4,221 live). Nothing to attach text to. |
| **live, no item text** | **62** | the real target. |

Of the 62, **56 were absent from `queue_state.csv` entirely** and 51 were absent from the
availability audit too — so the flagged rows were never a subset of the extraction queue,
which is why running the queue was never going to reach them. 6 were already `pending`.

**49 were appended to `queue_state.csv`** (pending → 1,164 → 1,213). They sort to the end of
the file, so the cron works them after the existing backlog; nothing was reordered.

**Nothing on Sheet1 was already staged-but-unlinked.** The TODO anticipated that class and
it is empty: zero of the 100 had an `__items.csv` on disk or a row in
`mapping_verification.csv`. The 27 resolved ones went all the way to publication; the sheet
just never got updated.

**5 of the 49 were queued under a corrected name.** The sheet spells them lowercase and the
live tables are not: `fivpei_perrig_2023_attdiff` → `FIVPEI_Perrig_2023_AttDiff`,
`kfcovid_li2020` → `kfcovid_Li2020`, `namprb_siwiak_2024_ssub` → `NAMPRB_Siwiak_2024_SSUB`,
`fad_fadplus_goto2021` → `FAD_fadplus_goto2021`, `fedsp_trzcinska_2023_monknow` →
`FEDSP_Trzcinska_2023_MonKnow`. Queued as spelled on the sheet, all five would have come
back "does not exist in IRW" — which, post-Rpkg#121, is now taken at face value, so five
live tables would have been recorded as missing.

**7 held out deliberately**, recorded `blocked` in `itemtables/pending_index_notes.csv`: the
six `dwyer_2025_genomics_*` and `rd_ppsl7as_ghasemy_2024_sl`, all flagged "Permission to use
the scale need to be obtained". That is a licensing question, not an access or tooling one;
a round would either block on them repeatedly or ship text the project has no right to
redistribute. **They need a rights decision before they are queued.** The 11 non-IRW tables
are recorded `note_only` so the next sweep starts from the answer.

What the remaining flags actually are, now that they are classified: 15 "contains
graph/images" (image-only sources — queued, expected to block honestly, but a settled block
beats a two-year-old sticky note), 11 access failures worth a retry ("no access to referred
paper" ×7, "not accessible", "can't find"), and ~15 item-count / resp-clash mismatches,
which are response-data questions as much as item-text ones and may be issues-page material.

### The restart

The queue did not stop for a reason, it stopped for a mechanism, and there was a second
mechanism underneath the one in the ruling. The cron died with its session on 2026-08-18 —
but Step 0's stop condition was still `itemtables/batch_011 already exists`, and batches
011-015 exist. **Re-creating the cron unchanged would have self-cancelled on its first
fire**, and the pipeline would have read as dead a second time. Cap raised to `batch_031`
(16 rounds of 12 from batch_016, ~192 tables — a human-reviewable amount of triage rather
than an unbounded run).

Confirmed before starting: no `circuit_breaker.flag`, `itemtables/clean/` absent, queue at
1,164 pending. `irw` is 1.0.1 (Rpkg#121 landed) and `scripts/table_sets.R` was smoke-tested
live — it returned the item and resp sets for `neurips_2020` (24,076,951 rows, 27,613 items)
with no export, which is the route that has to hold for the quota not to break again.

Rounds run from a **worktree** (`/home/ben/irw-wt/1709/itemtext`, branch
`itemtext/1709-restart-queue`), not `src`, which is checked out on
`tags/construct-type-rules`. `queue_state.csv` was byte-identical between the two at fork.
`check_provenance.R`'s `../../irw_site/` argument resolves outside the worktree and was made
absolute in the round prompt. The prompt itself is now a file,
`extraction_batches/round_prompt_v1.md`, rather than a 15kB paste re-transcribed per restart.

## batch_016 — 2026-09-03 — first round of the restart. 8 written, 4 blocked. CIRCUIT BREAKER TRIPPED.

12 tables, one agent each, worked in queue order. **8 wrote a CSV, 4 blocked.** At 33.3%
`failed` the breaker fired, `circuit_breaker.flag` is written and the cron job
`ITEMTEXT_BATCH_ROUND_V1` has been deleted. Nothing uploaded.

### Gates (all run at round close, against live data)

| gate | result |
|---|---|
| `normalize_nulls.R` | 8/8 already clean, 0 normalized |
| `audit_batch.R` | **6 PASS, 2 WARN** — both WARNs explained in `notes.csv` per Step 5c |
| `verify_batch.R` | **5 PASS, 3 exempt** — no FAIL, no missing verdict |
| `lint_verification.R` | **0 ERROR, 3 WARN** (adjudicated below) |
| `irw-validate` | 8/8 ok |
| `check_provenance.R` | 232 rows / 18 files, no vocabulary error |

`mapping_verification.csv`: 139 -> 151 rows, no collisions. The 12 added are 4 VERIFIED,
1 PARTIAL, 4 NO_ROUTE, 3 NOT_NEEDED.

### The four blocks are correct outcomes, not faults

`neurips_2020` and `neurips_2022` (Eedi publishes no wording as text; the 2020 images are barred
from reuse and 2022 ships none), `icar_sapa` (ICAR pool gated behind registration; 35 of 60 items
figural — **blocked, not excluded**, since ICAR is public-domain and stays re-queueable), and
`concretewords` (the table is **transposed** — `item <- x$Participant`, so the item axis holds
anonymous rater IDs; 1831/1831 match the Qualtrics ID pattern, 0/1831 contain a space).

### Four response-data defects found by extraction

This round found more than any previous one, and none is an item-text problem:

1. **`neurips_2020` item-code collision** — the task-1/2 and task-3/4 releases are anonymised
   separately and the challenge guide forbids linking their IDs, but `data/neurlps_2020.R` rbinds
   them and sets `item = question_id + 1`. Result: 27,613 contiguous codes instead of 28,561, and
   codes 1-948 each pool two different questions (median n 2,515 vs 396). `id` is merged the same
   way, so persons collide too.
2. **`neurips_2020` `resp` conflation** — a `rename(IsCorrect = AnswerValue)` before the rbind
   mixes binary correctness with 1-4 option identity; 22,468 of 27,613 items carry all five levels.
   This is the `resp_ambiguous` class.
3. **`concretewords` transposition** — as above.
4. **`vocabulary_iq` scoring defect** — `data/vocabulary_iq.R` scores *every* column against the
   vocabulary answer key, so the 30 bundled personality-survey items' 1-5 agreement responses
   (361,632 non-missing cells) all collapse to `resp=0`. Items 46-75 are unusable as responses.

**Two dictionary/metadata defects** as well: `hypersensitive_narcissism` is the HSNS *plus* the
Dirty Dozen (22 items, not 10) and its dictionary Reference cites an unrelated study (Jorgenson
2016 OHBDS); `content_literacy_intervention_g1` is the N=5,494 grade-1-AND-2 replication
(`doi:10.7910/DVN/HQEMN6`), not the N=674 first-grade trial its dictionary cites, so the `_g1`
suffix is misleading. `vocabulary_iq` likewise bundles two instruments.

### lint WARNs — adjudicated, statuses kept

`hypersensitive_narcissism`, `machivallianism_test_tipi` and `short_dark_triad` were flagged
VERIFIED-but-hedging. Reviewed: in all three the mapping axis IS fully established (132/132 cells
and 22/22 distinct profiles; 10 mutually distinct per-item counts; 135/135 cells and 27 distinct
profiles — every item separated from every other). The hedges concern the *source's own* fidelity
and the unlabelled anchors at resp 2/4, which is a different question from item<->text mapping.
Statuses stand. The lint is a keyword heuristic that correctly prompted the review.

### Process problems this round exposed

**1. The cadence is wrong and a second round fired mid-flight.** BATCH_PROCESS.md sets
`7,22,37,52` on the assumption a round takes "well under 10 minutes with 4-way parallelism". Under
one-agent-per-table these agents ran 3.6-16.4 minutes each and the round took ~40. A second firing
arrived while batch_016 was still `in_progress`; it correctly stood down, but only because a human
was watching — **Step 0 has no in-flight stop condition**, and none of its three conditions covers
this.

**2. Step 3's cleanup destroys its own output.** The step says merge into
`verification_merged.csv`, then delete the per-table files. `rm -f verification_*.csv` matches
`verification_merged.csv`, which is the exact filename `lint_verification.R` requires. Following
the documented procedure literally deleted all 9 verification rows at round close. They were
restored verbatim by resuming each agent (every one still held its evidence string; byte sizes
matched the originals), and the merge was redone deleting by explicit name. **Fix the step**:
merge to a name outside the glob and rename, or delete by name. Two agents identified this
independently.

**3. `validate_items.R` cannot satisfy the quota rule on a live table.** Its only two data routes
are `--resp-csv` against a local file and live `irw::irw_fetch()`, which exports the whole table.
So on any live IRW table the "HARD GATE" necessarily spends export quota, contradicting the
standing "never `irw_fetch` for a gate" constraint. Each agent resolved it alone and they did not
agree: two skipped the gate and substituted server-side set checks (`hypersensitive_narcissism`
1.19M rows, `machivallianism_test_tipi` 729k), two ran it live (`psychoneurotic_inventory` 698k,
`vocabulary_iq` 913k), and `short_dark_triad` built a 135-row surrogate CSV from an aggregate
`GROUP BY` and passed it via `--resp-csv` — sound for the two set comparisons, but a deviation
that was reported as a bare PASS until asked. **Recommended fix: give `validate_items.R` a third
route that takes its item and resp sets from `irw::irw_table_sets()`.** The script's own header
says it only compares sets, so this loses nothing and makes the quota rule satisfiable.

### The breaker fired on correct behaviour — needs a ruling

Step 5 maps "wrote no CSV" to `failed` and the breaker counts `failed`, but SKILL.md and the
2026-09-03 ruling both say an honest block is a CORRECT outcome and that blank-when-uncertain is
the extractor's validated property. Eight clean extractions plus four well-documented source
blocks is a good round by the skill's own standard, and it halted the loop.

This is the second time: batch_005 tripped at 33% and `round_log` recorded it as "a coincidental
cluster of WAF-blocked and missing-file sources, not a pipeline fault". The queue is worked in
table order and the head of the queue is where the corpus's large public-dataset tables sit —
bare-integer codes, image or closed sources — so clearing the flag without changing anything will
likely trip it again within a round or two.

**Proposal for Ben:** count only genuine faults toward the breaker (gate FAIL, crash, verify FAIL,
lint ERROR) and track documented source blocks as a separate non-halting statistic. A threshold
that fires on declining-to-guess trains future rounds away from the one property the 110-table
study validated.

### Queue

1,213 pending -> 1,201 pending, 131 done, 15 failed, 54 excluded. The four blocked tables are
recorded in `itemtables/pending_index_notes.csv` with `status=blocked`.

### Circuit breaker rule changed, and batch_016 reclassified — 2026-09-03 (ruled by Ben)

The breaker counted every no-CSV table as `failed`, so a table the extractor correctly DECLINED
was indistinguishable from one where the extractor BROKE. It fired twice on correct behaviour:
batch_005 (33%, recorded at the time as "not a pipeline fault") and batch_016 (33.3%, eight clean
extractions plus four determinate source blocks).

**New rule — the retry test.** *Would an unchanged retry, right now, plausibly produce a different
result?*

- **YES -> `failed`, and it COUNTS.** Gate FAIL/ERROR, crash, verify FAIL or missing VERDICT, lint
  ERROR, HTTP 403/timeout, exhausted quota, source never located. A cluster of these is what a
  systemic breakage looks like, which is the thing the breaker exists to catch — so "ignore all
  blocks" was explicitly rejected: a network or quota outage surfaces as twelve agents reporting
  "couldn't reach the source".
- **NO -> `blocked`, and it does NOT count.** The source publishes no wording, the licence bars
  reuse, the wording is images only, the pool is gated behind a human action, or a data defect
  makes item text unattachable. An unchanged retry fails identically; only a human action or a
  data change moves it.

`blocked` is a new `queue_state.csv` status. It is NOT `excluded` — excluded means never extract,
blocked means not until something changes, so these are the pool to revisit when it does. When in
doubt the rule is to choose `failed`: that costs one retry, whereas a wrong `blocked` quietly
removes a table from the queue forever.

Per-table agents must now answer the retry test explicitly in their notes and report, and say what
would have to change. The orchestrator classifies at Step 5 from that answer.

**batch_016 reclassified.** All four blocks fail the retry test: `neurips_2020` and `neurips_2022`
(Eedi publishes no wording as text; the 2022 kit ships no question content at all), `icar_sapa`
(pool gated behind registration — a human action, not a retry), `concretewords` (transposed table;
needs a data change). So the round is **8 done, 4 blocked, 0 failed — 0% against the 30% threshold,
does not trip.** `circuit_breaker.flag` deleted; it was raised by the rule that has now been
replaced.

Rounds must from now on log written / blocked / failed separately plus the yield. A high blocked
rate is a fact about which tables the queue served up — table order puts the corpus's large
closed-source datasets at the head — not about pipeline health.

The cron job has NOT been re-created. Restarting the queue is a separate decision.

### batch_016 triage — orchestrator re-verification of the round's claims (2026-09-03)

Step 5b requires the orchestrator to independently re-check any claim that overrides a source,
reports a response-data defect, or is headed for a public artifact. All nine were checked. **None
was overturned**; two came out stronger than reported.

| claim | verdict | how it was checked |
|---|---|---|
| `hypersensitive_narcissism` dictionary wrong | CONFIRMED, **worse than reported** | `irw_info()`: *both* `Construct` and `Reference` cite Jorgenson (2016) Open Hemispheric Brain Dominance Scale. The agent reported only the Reference. |
| `content_literacy_intervention_g1` cites the wrong deposit | CONFIRMED | per-item n is 4,826-4,843; the cited `RVJIMX` trial had N=674. Arithmetically impossible. Resp ranges also match the claimed block boundaries (items 1-20 on 1-3, items 100+ on 0-1). |
| `mgkt` instructions say -1.25, table penalises 1 | CONFIRMED, **by a cleaner route** | the cached test page does say "-1.25 points for each wrong answer", but with 5 correct and 5 wrong alternatives a 1.25 penalty lands on quarter-integers. Observed `resp` is exactly the integers -5..5, in both live data and the shipped CSV. Integrality alone settles it; the agent's least-squares fit was not needed. |
| `psychoneurotic_inventory` three source overrides | CONFIRMED | the codebook really does read `"sexual dreams ?"`, `"crushed m a crowd"`, `"St Vitus'dance"`; `page.html`/`p1.html` (the administered form) read exactly what shipped. The codebook is the defective transcription -- OCR artifacts -- so the override is right. |
| `psychoneurotic_inventory` 112 vs 116 | CONFIRMED | `intro.html`: "The test has 112 yes/no questions". The form carries **116** `YES NO` items and the data has 116. |
| `concretewords` transposed | CONFIRMED | `verify_concretewords.R`: 1831/1831 item values match `^R_[A-Za-z0-9]{15,17}$`, 0/1831 contain a space, first values are literal Qualtrics IDs (`R_036k0LpyK0SQ68p`). |
| `neurips_2020` item-code collision | CONFIRMED | `verify_neurips_2020.R`: codes contiguous 1..27,613, not 28,561; codes 1-948 median n 2,515 vs 396 (6.35x), 1,890,744 excess responses. |
| `neurips_2020` resp conflation | CONFIRMED | 22,468 of 27,613 items carry all five resp levels. |
| `vocabulary_iq` scoring collapse | CONFIRMED, to the row | server-side `GROUP BY item, resp`: items 1-45 carry `{0,1}`; all 30 of items 46-75 carry only `0`, across **361,632** non-missing responses -- the agent's figure exactly. |

Note for future rounds: `verify_batch.R` only runs the verify scripts of tables that shipped a
CSV, so the three blocked tables' scripts were never executed by the gate chain. They were run by
hand here and all reproduce. If blocked-table evidence is meant to be re-runnable -- and it is,
that is why the scripts are written -- `verify_batch.R` should pick them up too.

Also note `resp` is stored as a STRING in at least some tables, so `NA` is a literal and
`WHERE resp IS NOT NULL` does not filter it, and `MIN`/`MAX` on it return NA. Worth knowing before
writing an aggregate query against a live table.

### batch_016 staged — 2026-09-03 (Ben's call)

**Staged into `itemtables/clean/` (5 tables, 584 rows):** `short_dark_triad` (135),
`psychoneurotic_inventory` (232), `hypersensitive_narcissism` (110), `machivallianism_test_tipi`
(70), `machivallianism_test_vcl` (32). All byte-identical to their batch copies. Awaiting the
human `red_up` step; nothing has been uploaded.

**Held in the batch folder (3):**

- `mgkt` — clean on every gate, but `correct_response` holds a *reconstructed* answer key: the
  codebook never states which alternatives are correct, so it was solved from the raw data
  (weights exactly +1 on A0-A4, -1 on A5-A9, max residual 5e-14). That is project-generated content
  in a content field, the same shape as `machine_translation`, and no `provenance_vocab.csv` value
  or `check_provenance.R` check covers it. Held pending a disclosure ruling.
- `vocabulary_iq` — item text VERIFIED, but 30 of its 75 items are degenerate response data
  (`resp=0` only, 361,632 responses). If that defect is fixed by re-deriving the table, its
  positional item codes could shift and the text would need remapping. Held so the work is not
  done twice.
- `content_literacy_intervention_g1` — Step 5b `PARTIAL`, 76.2% of rows blank, and the dictionary
  cites the wrong deposit. The protocol names this combination a hold candidate.

**Owed on the public issues page once uploaded:** `psychoneurotic_inventory` (instructions say 112
questions, the form and data have 116) and, if it ships, `mgkt` (instructions state a -1.25 penalty
per wrong answer; the stored score penalises 1).

### Derived answer keys are disclosed content — ruled 2026-09-03, and `mgkt` staged

`mgkt` shipped a `correct_response` its source never published. The MGKT codebook prints each
question's ten alternatives but never states which five are correct, so the key was solved from
the response data by least squares: weights came back exactly +1 on A0-A4 and -1 on A5-A9,
reproducing every stored score to a max residual of 5e-14.

**Ruled: ship it, with disclosure.** The evidence being strong was never the issue. It is
IRW-generated content sitting in a content field, indistinguishable to a reader from a key the
study itself published — the same shape as the machine-translated English addressed on 2026-09-02,
so it gets the same remedy rather than a special case.

Implemented:

- **`provenance_vocab.csv` gains a `key_source` field** — `source_published`,
  `derived_from_responses`, or empty (no `correct_response`, or an instrument with no correct
  answer).
- **`check_provenance.R` now checks any number of vocabulary fields**, not just
  `translation_source`, and reports the disclosure debt for each. It groups the output by reason,
  so translations and derived keys are listed separately rather than merged into one count. A
  field with no vocabulary rows is reported as an error rather than passing silently — otherwise a
  typo in the vocabulary file would quietly disable the check for that column.
- Its error message was field-agnostic-ified: it used to print "UNKNOWN translation_source values"
  and list only `translation_source`'s allowed set, which for a `key_source` error sent the reader
  looking for the wrong thing. It now names the offending field and prints the allowed set for
  every checked field.
- **`SKILL.md` Step 6c documents `key_source`** and points at the vocabulary file rather than
  restating it.
- `mgkt`'s provenance row carries `key_source=derived_from_responses` and a `public_note` that
  opens by saying the key was not published with the dataset.

Verified both ways: the gate accepts `derived_from_responses` and exits 0, and an injected
`key_source=guessed` is caught, named, and exits 1. `mgkt` is now reported as owing an
issues-page entry alongside the 64 outstanding machine-translation tables.

**`mgkt` staged** into `itemtables/clean/` — 6 tables now staged, 897 rows. It owes two lines on
the issues page when uploaded: the derived key, and the -1.25-vs-1 scoring penalty.

### batch_016 defects filed as issues — 2026-09-03

All five carry the `data fix` label and the verified evidence, and each names the processing script
at fault. Filed only after the orchestrator re-check, per Step 5b — an agent's finding is a lead
until confirmed, and one of these (`mgkt`'s penalty) changed shape under re-checking.

| # | table | defect |
|---|---|---|
| [#1875](https://github.com/ben-domingue/irw/issues/1875) | `neurips_2020` | item codes 1-948 pool two questions each (the task-1/2 and task-3/4 ID spaces are merged against the challenge guide's explicit instruction), and `resp` conflates `IsCorrect` with `AnswerValue` |
| [#1876](https://github.com/ben-domingue/irw/issues/1876) | `concretewords` | `item` and `id` transposed; the item axis holds anonymous Qualtrics respondent IDs |
| [#1877](https://github.com/ben-domingue/irw/issues/1877) | `vocabulary_iq` | 30 bundled survey items scored against the vocabulary key, collapsing 361,632 responses to `resp=0` |
| [#1878](https://github.com/ben-domingue/irw/issues/1878) | `hypersensitive_narcissism` | dictionary `Construct` AND `Reference` cite the Open Hemispheric Brain Dominance Scale, an unrelated study |
| [#1879](https://github.com/ben-domingue/irw/issues/1879) | `content_literacy_intervention_g1` | dictionary cites the N=674 first-grade trial; the data are the N=5,494 grade-1-and-2 replication |

`neurips_2020`'s two defects were filed as ONE issue rather than two: they live in the same script
and would be fixed in the same edit, so splitting them would have created duplicate work.

Two of the held tables are now blocked on an issue rather than on a judgment call: `vocabulary_iq`
waits on #1877 (a re-derivation could shift its positional item codes, so staging the text first
risks doing the mapping twice) and `content_literacy_intervention_g1` waits on #1879 plus its own
`PARTIAL`/76%-blank status.

**Five of eight tables in this round produced a defect report against already-published data.** The
round log's standing observation that "the extraction pass is, in practice, also an audit of the
response data" is holding at a much higher rate here than in batches 001-011 — which is a property
of working the head of the queue, where the corpus's large aggregated public datasets sit.

### Both protocol defects fixed, and batch_016's public disclosures shipped — 2026-09-03

**1. `validate_items.R` gains `--table-sets`.** The gate had only two data routes: `--resp-csv`
against a local file, or live `irw::irw_fetch()`, which exports the whole table. So on any
published table the "HARD GATE" necessarily spent export quota, and the standing "never
`irw_fetch()` for a gate" rule was literally unsatisfiable. batch_016 is the evidence that this
matters: five agents hit the conflict and resolved it five different ways — two skipped the gate
(`hypersensitive_narcissism` 1.19M rows, `machivallianism_test_tipi` 729k), two exported
(`psychoneurotic_inventory` 698k, `vocabulary_iq` 913k), and `short_dark_triad` hand-built a
135-row surrogate CSV from an aggregate `GROUP BY` and passed it via `--resp-csv`, reporting a
bare PASS until asked. That divergence, not any one agent's judgment, was the bug.

The new route takes `unique(item)` and `unique(resp)` from `irw::irw_table_sets()` — the same
server-side route `audit_batch.R` already uses — and builds a surrogate frame carrying only enough
distinct values to reproduce the two sets. That is all this script ever compares, so nothing is
lost, and the banner now says which route produced the verdict. `--table-sets` and `--resp-csv`
are mutually exclusive.

Tested three ways: it reproduces the live route's verdict on `vocabulary_iq` (75 items PASS, resp
PASS) with no export; it still **FAILs** on a real mismatch, naming the missing items (dropped
items 1 and 2 from the CSV and it caught both); and passing both flags errors instead of silently
preferring one. Documented in SKILL.md Step 5 and in the per-table agent brief in both
BATCH_PROCESS.md and round_prompt_v1.md.

**2. Step 3's cleanup no longer destroys its own output.** The step said merge into
`verification_merged.csv`, then delete the per-table files — and `rm -f verification_*.csv` matches
the merged file, which is the exact name `lint_verification.R` requires. Following the documented
procedure literally deleted all nine of batch_016's verification rows at round close. Both copies
now say to delete BY NAME, and say why. Recovery was only possible because each agent still held
its evidence string and could be resumed; nothing on disk could have rebuilt them.

**3. batch_016's public disclosures shipped.** Two entries added to `itemtext_issues.qmd`
(datapages/irw PR #116, merged): `mgkt`'s derived answer key plus its -1.25-vs-1 scoring mismatch,
and `psychoneurotic_inventory`'s 112-vs-116 item count. The drafter generated seven entries; five
were dropped as below the page's bar — they describe wording the source never published, which the
standard explicitly says not to publish. `check_provenance.R` against the merged page reports 69
IRW-generated tables, 0 undisclosed.

An earlier reading of that check was wrong and is corrected here: it reported 64 undisclosed
machine-translation tables, but the `irw_site` checkout was on a stale feature branch holding 89
entries while `main` already carried those disclosures. The script's own branch warning — which
withholds a verdict when the page's state is unknown — was right to refuse one.

**The six uploaded tables are still in `irw_text`'s DRAFT, not released.** `red_up` writes a draft
only, so `irw_list_itemtext_tables()` still reports 578. Verified before stamping that no table
doubled: all six present, marked `added`, every row count matching its source CSV exactly
(135/32/70/232/110/313 = 892 rows).

### Step 3.5 verification gap closed — ruled and backfilled 2026-09-03

**Ruled: yes, forward + backfill.** `automated_finding` Step 3.5 had shipped 30 tables with no row
in `itemtext/mapping_verification.csv` — the permanent "one row per table, ever" record of how a
mapping was checked. It ran the three gates that compare a table against its SOURCE and none of the
four that check the mapping's own claim, the data standard, or the public disclosure record. Its
SKILL.md did not mention the verification layer at all, so this was a wiring gap rather than an
argued exemption.

**Forward.** Step 3.5 now requires a `mapping_verification.csv` row for every table it ships —
`NOT_NEEDED` for `data_labels`, real Step 5b evidence plus `verify_<table>.R` for anything else —
and runs `irw-validate` and `check_provenance.R`. The requirement is stated where it is because
Step 3.5 is *better placed than anyone* to satisfy it: it wrote `data/<table>.py`, so the item-code
derivation is known rather than reconstructed. A later pass has to re-find the paper from a
dictionary DOI and reverse-engineer a script that is frequently not named after the table
(`neurips_2020` is built by `data/neurlps_2020.R`; one script often writes a dozen tables).

**Backfill: all 30 now have a row.** Tracker 151 -> 181.

- **25 `data_labels`** got `NOT_NEEDED` rows naming the file and label level that tied code to text.
- **5 non-`data_labels`** got real evidence, one agent each. **Every one came back `PARTIAL`, and
  every one found the recorded `mapping_basis` overstated.**

**The finding: `paper_explicit` was wrong on all five.** The provenance note argued that because the
script renames the deposit's columns onto the codes the paper prints, the mapping is "explicit
rather than order-inferred". That is invalid — renaming onto explicit codes does not make the
correspondence explicit. Five independent checks reached it separately:

- The three `xue_2025_*` tables: the paper labels stems `(AS1)`..`(AS20)` but the deposit columns
  are `Q9_1..Q9_20`, and the script renames positionally. The paper's codes are not the data's codes.
- The two `wang_2024_*` tables: the appendices print items numbered 1-15 (or 1-13) continuously
  under block headers, so the block PREFIX is a label match but the numeric SUFFIX is print order.
  The string `LSE` occurs exactly once in the S2 appendix — in the header.

Corrected to `paper_order` in both `itemtext_provenance.csv` and the tracker, with the reasoning
recorded. Step 5b's "explicit code labels in the paper" exemption never applied, so verification was
genuinely owed on all five.

**No mapping defect was found.** Item wording is verbatim against source on every table, and the
cross-construct risk — three `xue` tables sharing one S3 "Constructs and items" file, where a
block-boundary slip would put one construct's wording on another's codes — was ruled out from both
ends. `xue_2025_academic_stress`: live alpha 0.9169 / KMO 0.9324 against published 0.917/0.932, with
off-by-one windows giving 0.9134 and 0.9105, neither of which rounds to 0.917.
`xue_2025_coping_style`: subscale totals 34.851/6.070 and 18.216/4.755 against published
34.852/6.070 and 18.216/4.755, largest deviation 0.001, neighbouring boundaries nowhere close.
`xue_2025_academic_procrastination`: alpha 0.871 vs published 0.871 and Table 3 subgroup totals
reproducing exactly.

**What none of them could establish: within-block order.** Every route available is invariant to
permuting items inside a subscale — 5,184 orderings survive on `wang_2024_self_efficacy_sources`.
The papers publish only scale-level statistics, so no route closes it. `PARTIAL` is the honest
status, and three agents explicitly reported failed routes as failures rather than as support.

`lint_verification.R` over the whole tracker: **181 rows, 0 ERROR.**

One correction to my own dispatch: I told all five agents `text_source=study_materials`. That is
true of the two `wang_2024_*` rows only; the three `xue_2025_*` are `translated_substitute`. An
agent caught it and worked from the file rather than the brief.

## batch_017 — 2026-09-03 — 12 written, 0 blocked, 0 failed. First round from the stable worktree.

**A clean sweep, and a sharp contrast with batch_016 (8/4).** The difference is the queue's own
order: batch_016 drew the corpus's large aggregated public datasets — Eedi/NeurIPS, ICAR, a
transposed word-norms table — while batch_017 drew established published instruments with reachable
open-access deposits. Yield is a property of what the queue serves up, not of pipeline health, which
is exactly why the circuit breaker was changed on 2026-09-03 to stop counting determinate blocks.

### Gates (all run at round close, after every agent finished)

| gate | result |
|---|---|
| `normalize_nulls.R` | 12/12 already clean, 0 changed |
| `audit_batch.R` | **12 PASS, 0 WARN** |
| `verify_batch.R` | **10 PASS, 2 exempt**, no FAIL |
| `lint_verification.R` | **0 ERROR**, 3 WARN (adjudicated below) |
| `irw-validate` | 12/12 ok |
| `check_provenance.R` | 244 rows / 19 files, no vocabulary error, 0 undisclosed |

`mapping_verification.csv`: 181 -> 193 rows (7 VERIFIED, 3 PARTIAL, 2 NOT_NEEDED). Queue 1,201 ->
1,189 pending, 131 -> 143 done.

### lint WARNs — adjudicated, statuses stand

`anh_2026_ai_adoption`, `anh_2026_digitaltrust` and `rosenberg_selfesteem` were flagged
VERIFIED-but-hedging. In each the mapping axis IS fully established — 40/40 item x resp cells with
eight distinct 5-tuples; per-item VIFs reproducing the published values to 4e-4; ten distinct
(n, mean) pairs matching to 1.7e-14. The hedges concern language provenance (whether the shipped
English is what Vietnamese respondents read), anchors the source never labels, and instruction
wording the deposit does not record — none of which is the item<->text mapping. Same adjudication,
on the same reasoning, as batch_016's three.

### Findings worth carrying forward

**1. The `anh_2026_*` deposit sits on the scale midpoint across every construct.** Five agents
independently computed per-item statistics from PLOS ONE 10.1371/journal.pone.0340002's S1 File:

| construct | items | item means | SDs |
|---|---|---|---|
| AI adoption | 8 | 2.974-3.105 | ~1.0 |
| Digital trust | 6 | 2.971-3.016 | ~1.0 |
| Family financial socialisation | 7 | 2.974-3.026 | 0.990-1.030 |
| Financial literacy | 8 | 2.971-3.013 | 0.973-1.024 |
| Financial well-being | 7 | 2.961-3.026 | 0.971-1.016 |
| Financial behaviour (already published) | 9 | 2.980-3.016 | — |

That is ~45 items across six unrelated constructs, every mean within ~0.04 of 3.00 and every SD
within ~0.06 of 1.0, on n=306. **This is an observation, not an accusation**: the paper's own
published statistics reproduce exactly from the same file (alpha 0.891 and 0.904, VIFs to three
decimals, AVE 0.630, loadings), so the data are internally consistent with what was published, and
each table's mapping verified independently. But six independent constructs do not normally share
that distributional shape, and it is a property of the DEPOSITED data rather than of IRW processing.
Worth a look at the S1 file as a whole before more of this deposit ships.

**2. The `anh` deposit was administered in Vietnamese, and that answers an open audit row.** All
five agents reached the same conclusion from Methods 3.3 (translation + back-translation) and the
same evidence (the sole supplement is a pure-ASCII CSV with zero non-ASCII bytes). All five shipped
the documented fallback: English base fields, `language=Vietnamese`, empty `_translated` columns,
`text_source=translated_substitute`, `public_note` owed at upload. **This closes the `NEEDS_REVIEW`
row for the already-published sibling `anh_2026_finbehavior` in
`language_backfill/audit_2026-09-01.csv`** — the answer is Vietnamese, fallback, and it applies to
all six tables from the deposit. `anh_2026_finbehavior` shipped in batch_006 with no `language`
column and should be backfilled.

**3. A table can pool two administered languages, and the schema has no way to say so.** Both
`campos_2023_*` tables pool Finnish (n=3,614) and Brazilian Portuguese (n=3,979) respondents, so no
single administered string exists per row. Two agents independently invented the same workaround —
`language="Finnish; Portuguese"` — and both flagged it as their own convention rather than a
documented one. **This needs a ruling.** The honest fix may be splitting these tables by country,
which is a data change, not an item-text change. Both administered wordings are recoverable if it is
ever split: Portuguese in Campos 2020 Table 1 and Campos 2021 (PeerJ 8:e8814), Finnish in the
authors' Acta Odontol Scand 2021 supplemental file.

**4. A fourth dictionary defect.** `rosenberg_selfesteem`'s Description reads "Experinces in Close
Relationships Scale" (typo in the original) and its Reference appends a Brennan/Clark/Shaver 1998
ECR citation; the RSE half of the Reference is correct, the rest is copy-paste from another Open
Psychometrics table. With `hypersensitive_narcissism` and `content_literacy_intervention_g1` from
batch_016, that is three dictionary defects found in 24 tables — dictionary metadata looks like a
systematic weak spot rather than a run of coincidences.

**5. `carney_2023_substance_use` ships derived indicators, not administered items.** `resp=1` means
any use in the past three months (ASSIST) for every substance EXCEPT `alcohol`, where it means an
AUDIT score above 8 — hazardous or harmful use, not any drinking. A reader taking `alcohol`/`1` at
face value would be wrong about all 414 respondents. Pinned by the paper's own 147/35.5% count.
Genuine issues-page material.

### Process notes

**`normalize_nulls.R` is batch-scoped and the per-table brief tells every agent to run it.** One
agent ran it across the whole batch directory and rewrote a sibling's in-flight CSV; two others
explicitly declined, reasoning that it writes across a shared directory; a fourth found it has a
**single-CSV mode** and used that. The change is idempotent so nothing was corrupted — batch-close
`normalize_nulls.R` reported 0 of 12 files needing normalization — but the instruction is ambiguous
and three agents resolved it three ways. **Fix: tell the per-table agent to run it on its own file
only, or move it to the orchestrator's Step 4 exclusively.** Same shape as the `verification_*.csv`
glob trap: a batch-scoped tool invoked from a per-table context.

**Today's two fixes both held.** Every agent used `validate_items.R --table-sets`, so not one of the
twelve faced the gate-versus-quota conflict that produced five different improvisations in
batch_016, and no agent called `irw_fetch()` for a gate. Sidecar merging deleted BY NAME rather than
by glob, so `verification_merged.csv` survived its own cleanup this time.

**One brief steered an agent wrong and it checked anyway.** I warned the `anh_2026_finliteracy`
agent that a financial-literacy measure is often a knowledge test and told it not to solve for a key
silently. The items are all "I am aware..." / "I feel confident..." — a subjective self-assessment
with no correct answers. It tested the premise instead of inheriting it, which is the behaviour that
prevents an invented answer key.

## batch_018 — 2026-09-03 — 11 written, 1 blocked, 0 failed. CAP REACHED, job self-cancelled.

Second and final round of the two-round trial. Gates: audit **6 PASS / 5 WARN** (all five explained in
notes.csv per Step 5c), verify_batch **10 PASS + 1 exempt**, lint **0 ERROR / 5 WARN** (adjudicated —
statuses stand), irw-validate **11/11 ok**, check_provenance clean. `mapping_verification.csv`
193 -> 205. Queue 1,189 -> 1,177 pending, 143 -> 154 done.

### The round was interrupted by an account-wide spend limit, and the wreckage was the danger

**8 of 12 agents were killed mid-run by HTTP 429** (monthly spend limit; session reset 19:50 PT).
Four had completed; a fifth was complete by exemption. **Three died AFTER writing an `__items.csv`
but BEFORE writing provenance or verification.** At merge time an ungated, unrecorded items CSV is
indistinguishable from a finished one — so they were moved to
`extraction_batches/quarantine_batch018_ratelimit/` with a README, not left in the batch. One of them
was `cdm_timss03`, a table expected to BLOCK; its agent's last words were "Now I'll build the CSV",
so the file may even be a partial write.

**The seven unfinished tables were NOT marked `failed`.** Nothing was determined about them: this was
our own budget, not a verdict about any source. Marking them failed would have tripped the circuit
breaker at 67% AND written a false statement about seven sources into the queue. They stayed claimed
to batch_018 and were re-dispatched after the reset.

**The retry briefs were much stronger than the originals**, because the four survivors had mapped the
terrain — which supplement is which pilot, the block ranges, that the pilots genuinely differ, the
Portuguese finding, and the renumbering trap. The `genom_know` retry was told explicitly NOT to
re-extract: its predecessor's complete output had survived, so its job was to verify that work. It
did, kept the content, and repaired one real defect.

### The pilot-1 renumbering trap — found by a sibling, relayed mid-flight

`carver_2017_puggs_pilot1_attitudes` finished early and found that **the S4 Code Book and the S3
questionnaire number Sections 2-3 DIFFERENTLY**. Its own block (32-51) is numbered identically in
both, so it was unaffected — but `det_core` (Q1-Q13) and `genom_know` (Q14-Q31) sit inside the
disagreeing range, where the wrong choice ships wrong wording on every item while passing every
set-based gate silently. The orchestrator relayed the warning to both agents mid-run.

Both proved the data follow **Code Book** numbering, independently and decisively:

- `det_core`: the permutation would mis-word **10 of 13** items. Three checks — polarity inverts at
  the two positions the documents key oppositely (Q2 +0.063 vs -0.135; Q4 +0.126 vs -0.142); the
  near-consensus lifestyle/diabetes marker sits at Q3 (mean 3.78, 161/205 strongly agree) where the
  Code Book puts it, versus Q7 (mean 2.16, 55 don't-knows) under S3; and the technical amino-acid
  statement draws 39 don't-knows at Q9 versus 2 at Q11, which S3 numbering reverses.
- `genom_know`: exactly five stems contain "epigenetic", and since don't-know is dropped, per-item n
  is a non-response measure. The five lowest-n items are **exactly** the Code Book's epigenetic set
  (86, 104, 105, 110, 114, then a gap to 128); the S3 set would be 149, 110, 177, 185, 152. **1 in
  8,568 by chance.**

**S1/S2 Text AGREE for pilot 2** — confirmed independently by three agents. The trap is pilot-1 only.

### S3 is the PRE-REVISION English, which affects a table already marked complete

The paper's back-translation review PRECEDED the pilots and forced wording changes in both languages,
naming "diet" -> "eating habits". The Code Book reads "Eating habits and physical exercise"; S3 still
reads "Diet and exercise". So S3, despite being titled "used in the first pilot study", is one
revision behind the administered form. **`pilot1_attitudes` ships S3 wording.** Its numbering is
unaffected (32-51 agree), so the mapping is sound, but the wording is stale — it keeps the
ungrammatical "used for modify or enhance" that the Code Book fixes. **A human should decide whether
to switch that table's wording base to the Code Book.** Two agents reached this independently.

### Both TIMSS tables shipped, against expectation — and the reason is a methodological lesson

`cdm_timss03` (23 items) and `cdm_timss07` (25 items) were both expected to block on TIMSS secure
items. Both shipped, because the codes are IEA's own item IDs carried through `data/cdm.R` unchanged,
and **every released-item page prints that ID in its header** — an explicit label match, not booklet
position. `cdm_timss11` shipped partial: 73 of 174 items, the other 101 being secure by design.

**The trap all three hit: the released-item PDFs are RASTERISED.** `pdftotext` returns only header
metadata and the copyright watermark, so a text-only pass reads as "wording not extractable" and
blocks incorrectly. Every stem was transcribed from rendered page images. Three agents found this
independently. Any future round touching image-distributed assessments should know it.

`cdm_timss03` also found that 6 items secure in 2003 were released in the **2007** cycle under IEA's
release-cycling policy, and used the 2007 pages for them. That runs against a warning the orchestrator
gave (do not accept other cycles' material) and the agent was right to reason past it: TIMSS trend
items are the SAME item reused under the SAME ID, so a 2007 page headed `Item ID M022234B` documents
the identical item. Substituting a different cycle's items would be the error; this is not that. The
orchestrator's blanket instruction was too strict.

Corroboration was strong: `cdm_timss07` reproduced the booklet design 25/25 (block M04 n=344, M05
n=698) at zero export; `cdm_timss11` matched IEA's published Austria percent-correct across all 73
released items at **r = 0.9991**, mean |diff| 0.82 pp.

### Cross-sibling reconciliations applied by the orchestrator

Three agents independently flagged that the batch disagreed with itself. Fixed at round close:

1. **`pilot2_attitudes` and `pilot2_traits` shipped no `language` column** and `text_source=study_materials`,
   while their six siblings from the same study shipped the Portuguese fallback. Four agents established
   Brazilian Portuguese administration and confirmed zero Portuguese-accented characters across every
   supplement. Both tables now carry `language=Portuguese` with the four `_translated` columns present
   and empty — the standard's documented signal. Left alone, the corpus query
   `language != '' AND item_text_translated == ''` would have silently missed them.
2. **`pilot2_attitudes` cited the wrong supplement labels** ("S1 File", "S6 Text", "S3 File"). Per the
   paper's own SI list the pilot-2 Code Book is **S2 Text (.s008)**; S6 Table is the pilot-2 raw data.
   Right files, wrong names — and the orchestrator propagated the error into two retry briefs before
   two agents independently caught it.
3. **`cdm_timss03` recorded `mapping_basis=data_labels`** where its two TIMSS siblings recorded
   `paper_explicit` for the identical situation. `data_labels` means the source DATA FILE ties code to
   text; here the data file supplies only the CODE and the tie to WORDING comes from the PDF printing
   that ID. Corrected to `paper_explicit`.

### Still open for a human

- **`cdm_timss07` licence.** IEA's 2007 notice reads "Commercial exploitation, distribution,
  redistribution, reproduction ... are prohibited unless written permission has been provided by IEA."
  If "Commercial" distributes across the list — supported by the per-item watermark and the preceding
  non-commercial-use sentence — IRW is clear. If it attaches only to "exploitation", ALL redistribution
  needs written permission. The agent shipped on the first reading and flagged it. **Note the 2003
  notice is materially clearer**: "Although the items are in the public domain, please print an
  acknowledgement of the source." The cycles differ, so a ruling on 2007 does not transfer to 2003.
- **TIMSS `resp` encoding differs between siblings**: `cdm_timss03` puts `resp=1` on the keyed option
  row and 0 on distractors; `cdm_timss07` records the two score levels. Same kind of table, two
  conventions, and the agent flagged its choice as a choice.
- **`cdm_timss03` has no administered language established**, while 07 and 11 are Austria/German. Not
  guessed — flagged.
- **Image-read transcription** on all three TIMSS tables warrants a spot-check before upload, and
  bracketed figure descriptions in them are IRW's own words, not IEA's.
- **`instrument` string differs between carver siblings** — one uses the paper's actual expansion
  ("Public Understanding and Attitudes towards Genetics and Genomics"), another a phrasing the paper
  never uses ("Public Understanding of Genetics and Genomics Survey").
- **`chanal_2020_anglais` Description is wrong**: the table reads as self-concept but ships the
  academic MOTIVATION questionnaire; the self-concept block CS1..CS6 is dropped by the script. Four
  sibling tables share the problem.
- **An unreproduced published figure**: the paper's only pilot-2 per-item number, "78.8% correct" for
  the single-gene item, does not reproduce (Q2 is 82.1% under the convention that reproduces the
  pilot-1 figures exactly). Not evidence against the mapping; possibly worth an author query.

### Trial verdict

Two rounds, 24 tables: **23 written, 1 blocked, 0 failed.** Both of the day's tooling fixes held —
every agent used `--table-sets`, no agent called `irw_fetch()` for a gate (one used a 583-row fetch
inside a verify script for per-item number-correct, which `irw_table_sets()` does not expose, and said
so), and sidecar merging deleted by name. The `normalize_nulls.R` single-CSV instruction added after
batch_017 was followed by every agent in batch_018.

### batch_018 TRIAGE — 2026-09-03. 7 staged, 4 held.

**Staged into `itemtables/clean/` (7 tables, 439 records):** `carver_2017_puggs_pilot1_det_core` (52),
`_pilot1_genom_know` (72), `_pilot1_traits` (100), `_pilot2_attitudes` (80), `_pilot2_det_core` (18),
`_pilot2_genom_know` (32), `_pilot2_traits` (85). All byte-identical to their batch copies, item counts
matching each agent's report, zero duplicate `(item, resp)` pairs. Awaiting the human `red_up` step.

**The orchestrator's Step 5b re-check.** The load-bearing claim across the pilot-1 tables is that the
data follow the S4 Code Book numbering rather than the S3 questionnaire's. If that is wrong, every item
in two tables is mis-worded and every set-based gate still passes. Both proofs were reproduced
independently, from the shipped CSVs plus live server-side aggregates, not from the agents' scripts:

- **`pilot1_genom_know`**: the five stems containing "epigenetic" are `Q19, Q21, Q23, Q24, Q27`, and the
  five lowest-n items are Q19 (86), Q24 (104), Q23 (105), Q27 (110), Q21 (114) — ranks 1-5, with a clear
  gap to rank 6 (Q22, 128). Exact match. Since "don't know" is dropped by the processing script, n is a
  non-response measure and jargon items draw the most don't-knows.
- **`pilot1_det_core`**: Q3 is "Eating habits and physical exercise can play an important role in
  preventing and controlling diabetes", mean **3.8**, the highest of the 13 — where the Code Book places
  the near-consensus marker. Q7 is "Traits and diseases caused by a single gene are not very common",
  which is S3's item 2, matching the permutation the agent described. Q3's wording is also the
  POST-revision "Eating habits" rather than S3's "Diet", independently corroborating that the Code Book
  carries the administered form.

**Held (4), none for a defect in the extraction:**

- `cdm_timss07`, `cdm_timss03`, `cdm_timss11` — [#1891](https://github.com/ben-domingue/irw/issues/1891).
  2007's IEA notice is ambiguous about whether non-commercial redistribution is permitted; 2003 and 2011
  read as public domain on their own terms but are covered by the same issue's second question, which is
  that all three record `License: GPL-3.0` (the CDM R package's licence, covering the RESPONSE data)
  while their item text is IEA-licensed. That is a table with two rights regimes and the dictionary field
  describes only one. All three also want a transcription spot-check, being image reads.
- `carver_2017_puggs_pilot1_attitudes` — ships S3 questionnaire wording, which two agents established is
  the PRE-revision English. Its mapping is sound and its gates are green; the hold is purely about
  whether to ship wording one revision behind what respondents read. Needs a ruling, not a fix.

**A measurement error worth recording.** The first staging pass reported `pilot1_det_core` at 104 rows
against the agent's stated 52, which looked exactly like the doubling failure `red_up` guards against.
It was not: `wc -l` counts PHYSICAL lines, and these CSVs carry embedded newlines inside quoted
`item_text`/`instructions` fields, so it over-counted by the number of wrapped lines. Parsed as CSV the
file has exactly 52 records, 13 items, resp 1-4, no duplicates. **Count records with a CSV parser, never
`wc -l`** — the failure mode is a false doubling alarm, and on a different day it could as easily mask a
real one.

## batch_019 — 2026-09-04

**12 tables claimed. Written 7 / blocked 4 / failed 1. Yield 58% (7/12).**
Circuit breaker **not tripped**: 1/12 = 8.3% failed, well under the 30% threshold.

**Written (7), all gates green:** `chatton2024_honos13`, `chen_2021_acculturation`,
`chen_2021_enculturation`, `chen2022b_selfesteem`, `chen2022b_socsupport`, `chen2022_cls`,
`chen2022_ses`. `audit_batch.R` reports **7 PASS with no anomalies — zero WARNs**, so Step 5c
had nothing to explain. `verify_batch.R`: 3 PASS + 4 MISSING(exempt, `data_labels`).
`irw-validate`: ok on all 7, nothing to report. `check_provenance.R`: 267 rows over 21 files,
69 IRW-generated tables, 0 without a public issues-page entry. `lint_verification.R` initially
raised 3 ERRORs — all three were the `data_labels` tables awaiting their Step 3 `NOT_NEEDED`
rows; after adding those, clean at 11 rows. 11 rows merged into `mapping_verification.csv`
(205 → 216), one per claimed table.

**Blocked (4), all determinate (retry test NO), none counting toward the breaker:**
`chanal_2020_francais` (text recoverable, mapping not — and the published subscale order is
positively *refuted* by the data; same block the batch_018 agent reached independently on the
sibling `chanal_2020_anglais`), `che_2026_regulatory_self_efficacy` (CC BY, but no companion
paper exists and the RESE's ordered wording is not openly published),
`chen2025_self_esteem` (deposit publishes no wording and no instrument name; items statistically
exchangeable), `chinvararak_2021_ecr` (rights: two independent NC clauses).

**Failed (1):** `CHEXI_Lin_2019` — killed by an API rate limit (monthly spend cap) before it read
anything. No files on disk. Retry test YES; a re-dispatch after the limit resets is all it needs.

### The rate limit nearly cost two completed tables
Three agents were reported `failed` by the harness with a 429 monthly-spend-cap error, their
result text showing only "I'll start by reading the skill documentation." **Two of the three had
in fact finished their entire job** and were killed on the final message: `chatton2024_honos13`
had written a complete 65-row items CSV plus all four sidecars, and `chanal_2020_francais` had
written a full determinate block record including its `verify_*.R`. Only `CHEXI_Lin_2019` was
genuinely killed early, and the tell was that it had left no files at all.
**Lesson for future rounds: a harness "failed" status reports how the agent's process ended, not
how much work it completed. The notification's `<result>` excerpt is the FIRST assistant text, not
the last — it is not evidence of how far the agent got. Always `ls` the batch directory before
classifying a killed agent.** Trusting the status here would have discarded a clean table and a
fully-argued block, and marked both for a pointless retry.

### Step 5b orchestrator re-checks (3 agent claims, all independently re-derived)
- **`chatton2024_honos13` entry/exit duplication — CONFIRMED EXACTLY.** In the source deposit
  (n=609) `HonosE1` and `HonosS1` are identical for **all 609** participants (differ = 0), while
  every other entry/exit pair differs for between **103** (item 6) and **379** (item 3). Item 1's
  admission and discharge waves therefore carry the same values by construction. A **response-data**
  defect, not an item-text one — the itemtext gates are green and the wording is unaffected.
  Worth its own GitHub issue.
- **`chen2025_self_esteem` flat battery — CONFIRMED and sharpened.** Across all 53 item columns of
  the four sibling scales, **52 have means in 3.101–3.195** (spread 0.094) and SDs in 0.943–1.034;
  the sole exception is `BI1` at mean 3.772 / SD 1.299. **All 1378 inter-item correlations are
  positive** (0.017–0.649, mean 0.245) — not one negative, across a battery spanning body image,
  motivation, peer support and self-esteem. Spans `chen2025_body_image` / `_activity_motivation` /
  `_peer_support` / `_self_esteem` as a group.
- **`chen2022b_selfesteem` polarity — CONFIRMED in direction, constants differ.** As stored,
  alpha = **0.691** with **36/45** inter-item correlations positive; re-reversing the five
  negatively worded items gives alpha = **0.510** with only **21/45** positive. (The agent reported
  0.731 vs 0.563 — same conclusion, different NA handling.) The deposit is already
  direction-aligned, so the paper's uniform anchors do not apply per item and blank `option_text`
  is right. The item block was also re-checked and is correct: the 10 shipped codes are exactly
  source columns 31–40, properly excluding the adjacent MSPSS item at column 30.
  **New, missed by the agent:** the raw deposit carries a single out-of-range value **22** on
  "I feel I have no strengths"; all nine other RSES columns are clean 1–4 and that column's only
  outlier is this one cell, so it is an isolated data-entry error (a typo for 2), not a sentinel.
  It does not reach the shipped item text — the live table's resp set is exactly {1,2,3,4} and the
  gates pass — but it is recorded as a raw-source observation.

### Escalation raised by the `chinvararak_2021_ecr` agent, endorsed
The ECR rights reasoning is **not table-specific**: it applies to every IRW table whose wording is
the ECR / ECR-R / ECR-R-18 / ECR-S. Better ruled once at corpus level than rediscovered per table.

### Also notable
- **Every table this round used the server-side query route.** No agent performed a full
  `irw_fetch` export; ground truth came from `irw_table_sets()` / `table_sets.R` throughout.
- Sibling isolation held. Four same-source pairs ran concurrently (`chen_2021_*`, `chen2022b_*`,
  `chen2022_*`, plus `chinvararak_2021_ecr` whose out-of-batch sibling `_phq15` was explicitly
  fenced off) with no cross-writes and no scratch collisions, the per-table `.cache/<table>/`
  namespacing having done its job.
- The `chen2022_ses` and `chen2022_cls` agents independently found the same structural signature in
  the same deposit: the 8 A-numbers absent from A1–A24 are exactly Asher (1984)'s 8 LSDQ filler
  positions (1/735471 by chance). Corroboration from two directions, not one agent's inference.
- Sidecar merge used exact-filename deletion, per the batch_016 incident; `verification_merged.csv`
  survived.

### Triage — 2026-09-04

Done in the runner worktree the same morning the round ran, which is a first: every
previous batch was triaged days later. Ben cancelled the 06:13 round before this
(deliberate pause via `circuit_breaker.flag`, not a tripped breaker) — the unattended
hourly cadence is being replaced, partly because an API monthly spend cap makes firing
into an empty budget wasteful.

**Gates re-run live, all clean.** `normalize_nulls.R` 0 of 7 needing changes;
`audit_batch.R` 7 PASS / 0 WARN against current live data; `verify_batch.R` 3 PASS +
4 MISSING(exempt), the four exempt being exactly the four `data_labels` tables;
`lint_verification.R` 11 rows, no problems. Nothing the round claimed failed to
reproduce.

**Staged (6, 509 rows / 99 items)** into `itemtables/clean/`: `chatton2024_honos13`,
`chen_2021_acculturation`, `chen_2021_enculturation`, `chen2022b_selfesteem`,
`chen2022b_socsupport`, `chen2022_cls`.

**Held (1): `chen2022_ses`** — Ben's call, see its `notes.csv` row. Not a gate failure:
all four gates passed. The mapping is `reconstructed` and PARTIAL, laying the canonical
RSES onto A25..A34 in published order with no source naming an individual item — the
`gilbert_meta_35` shape. The `chen2022_cls` filler-gap signature pins the A-numbering to
instrument positions, but nothing establishes that the source used canonical RSES order,
and A34's lone negative item-rest (-0.16, in an already positively-keyed block) is
evidence the other way. Unblocking needs a source that NAMES items — the Ji and Yu (1999)
Chinese adaptation with numbered items, or the authors' codebook.

**Worth noting for future triage:** `draft_issues_qmd.R`, run independently of the
verify scripts, reached the same conclusion about `chen2022_ses` from the provenance
alone — "MAPPING IS RECONSTRUCTED, not sourced ... Nothing distinguishes A27 from A28",
and it reads A34 as "one item left unreversed when the others were scored". Two
independent routes to the same hold.

**Issues page not yet applied.** Draft for all 7 is in
`fixes/itemtext_issues_draft_batch019.md`. It is blocked on the upload by design — a
table gets no entry until it ships — and `chen2022_ses`'s entry must be dropped unless
that table ships. Applying it edits `../../irw_site/itemtext_issues.qmd`, a different
repo, so it wants its own branch there.

**Not stamped.** `uploaded=` stays blank in `provenance.csv` and `mapping_verification.csv`
until Ben confirms the upload actually happened.

---

## 2026-09-04 — the deliberate pause ended; rounds are now run by hand

`circuit_breaker.flag` was set at 05:38 as a DELIBERATE PAUSE (not a trip) to stop the
06:13 cron round while the scheduling question was reopened. That question is settled
(#1913, HANDOFF decision (c)): **there is no scheduler.** `extraction_batches/run_round.sh`
is started by a human, one round per triage session.

Three things had to happen before the queue could resume, and all three are done:

1. The `13 * * * *` crontab line is removed (Ben, 2026-09-04).
2. The runner worktree `/home/ben/irw-queue-runner` was found parked on
   `itemtext/handoff-scheduling-state`, not `itemtext/queue-rounds` — the branch guard
   would have refused every round. It is back on `itemtext/queue-rounds`, fast-forwarded
   to `main` at f6556f7.
3. `origin/itemtext/queue-rounds` was deleted when #1904 was merged with `--delete-branch`.
   It has been recreated, which restores both the runner's push check and the standing PR.
   **Do not delete it again on merge.**

The flag is deleted. Nothing fires on its own; the next round happens when someone runs
`run_round.sh`. The cap is `batch_020`, so that is one round, then it stops.

## batch_020 — 11 written / 1 blocked / 0 failed (92% yield)

Fired 07:19 by hand (`run_round.sh`, the first round under the no-scheduler regime). **The round
agent abandoned the protocol at Step 4 and the closing steps were completed by a human at 08:0x —
read "How this round ended" below before trusting anything about its provenance.**

**Written, all gates green:** `chinvararak_2021_phq15`, `choy_2022_extraneous_events`,
`chuemchit_2024_nonpartner_violence`, `chuemchit_2024_partner_violence`, `cinar_tanriverdi_2023_gad7`,
`COACH_Chen_2022_ADL`, `COACH_Chen_2022_CSQ`, `COACH_Chen_2022_IADL`, `COACH_Chen_2022_MOS_SSS_C`,
`COACH_Chen_2022_WHOQOL_BREF`, `cogcontrol_gyurkovics_2019_flanker`.

Gates, all run after the fact: `normalize_nulls.R` 0 of 11 needed normalising; `audit_batch.R`
**9 PASS / 2 WARN**, both explained below; `verify_batch.R` 8 PASS + 3 MISSING(exempt, all
`data_labels`); `lint_verification.R` 0 ERROR / 3 WARN; `irw-validate` no ERRORs (five
`name_charset` WARNs, all on pre-existing capitalised COACH table names, not on anything this round
produced); `check_provenance.R` clean, 69 IRW-generated tables all disclosed.

**Blocked (1), determinate:** `choy_2022_intent_career` — CC BY and the codes are the source column
names, but the paper publishes one sample item with no item number and CFA loadings without wording;
2 of 3 items have no published referent. Retry test NO. Recorded in `pending_index_notes.csv`.

**Failed: none.** 0/12 = 0%, breaker not approached.

### The two audit WARNs, both explained, neither an itemtext defect

- `COACH_Chen_2022_IADL` — 6 items carry live resp values above their own option ceiling. This is a
  **response-data defect, not a mapping error**, and the round's own note had already quantified it:
  65 of 54,653 responses (0.12%) sit above their item's defined maximum, all at the 6- and 12-month
  waves. Checked independently at close-out with `item_stats.R`: at **wave 1** every item's max
  equals its canonical Lawton ceiling exactly (q5 max 2, q8 max 2, q1/q3/q6/q7 max 3, q2/q4 max 4);
  the out-of-range values appear only in waves 2 and 3 at 0.0–0.4% per item. The unequal option
  counts are correct Lawton IADL, and the option_text mapping stands. **Worth its own `data fix`
  issue** — the stray values are in the published table.
- `cogcontrol_gyurkovics_2019_flanker` — the four high-count codes (`targ_19`, `targ_25`, `targ_30`,
  `targ_32`) are exactly the four **congruent** displays (↓↓↓↓↓, ↑↑↑↑↑, →→→→→, ←←←←←). Every
  participant saw all four; the paper's random direction-pairing design gives each participant only
  4 of the 12 incongruent codes, so a congruent code carries ~3x the trials. Design property, not
  item-code conflation.

### The three lint WARNs are correct as VERIFIED

`lint_verification.R` flags `chinvararak_2021_phq15`, `chuemchit_2024_nonpartner_violence` and
`chuemchit_2024_partner_violence` as "VERIFIED but its evidence hedges". Read against the rule —
VERIFIED means the route distinguishes every item from every other item — all three are right: each
evidence string says in terms that the mapping is fully pinned (15/15 distinct source labels; five
published prevalences mutually distinct at 30x the residual; 494/494 row-by-row reconstruction with
every off-diagonal breaking). Their "does not establish" clauses are about **wording provenance**
(translated substitutes, unpublished composite keys), not about the item↔code mapping under test.
The lint fires on the phrase, which Step 5b actually *requires* the evidence to contain. No change.

### How this round ended — a new failure mode

The agent finished extraction and Step 3 cleanly, then **launched the Step 4 gates as a background
command and ended its turn to wait for a notification**. A `claude -p` run has no next turn: ending
the turn ended the session. The log records it verbatim — "The background command will notify me
when the audit finishes — no need to poll. Waiting." — and the process exited **0** at 07:35 with
Steps 4, 5 and 6 never run, nothing committed, and all 12 rows left `in_progress`.

Two things worked exactly as designed and one did not:

- The **guards worked.** 12 `in_progress` rows plus a dirty tree meant the next round would have
  refused twice over, which is the whole point of them.
- The **standing PR worked** — first successful run of that path since #1904 deleted the branch. It
  pushed and opened #1922.
- **Exit code 0 is now worthless as a completion signal, for the second distinct reason.** It was
  already known that a 429 kill exits 0; now an abandoned protocol does too. The fix is a
  post-condition check rather than an exit code: after the agent returns, a round has completed only
  if zero rows are left `in_progress` and the batch has an `audit_report.csv`. Added to
  `run_round.sh`, along with a Step 2 instruction never to background a command or wait on a
  notification.

Close-out was done by hand rather than by re-running: every gate passes, the 12 notes all carry
their retry tests, and `mapping_verification.csv` already held all 12 tracker rows — the work was
sound and complete, only unrecorded. The three `NOT_NEEDED` rows for the `data_labels` COACH tables
were missing from the batch-local `verification_merged.csv` (they were in the permanent tracker) and
were added; that was the only substantive gap, and it cleared the 3 lint ERRORs.

**Note for whoever edits these files next:** `notes.csv` has **mixed line endings** — the flanker row
is CRLF while the rest are LF — and no quoting convention round-trips it. Edit lines in place,
byte-wise, and preserve each line's own terminator. A `csv.writer` rewrite silently reformats the
whole file.

### batch_020 triage — 11 of 11 staged, 0 held

Gates were re-run live at close-out (above), so triage did not re-run them a third time; what it
added was the per-table go/no-go, a read of the two source overrides, and the issues.

**Staged into `itemtables/clean/`: all 11.** Every non-`data_labels` table has its
`mapping_verification.csv` row, which SKILL.md Step 6c requires before promotion — six of them
(`MOS_SSS_C`, `choy_2022_extraneous_events`, both `chuemchit_2024_*`, `cinar_tanriverdi_2023_gad7`,
`cogcontrol_gyurkovics_2019_flanker`).

**The two source overrides were read, not taken on trust.** Both verify scripts test the decision
that was actually made rather than the plumbing, which is what triage is for:

- `verify_COACH_Chen_2022_MOS_SSS_C.R` states the codebook grouping and the shipped grouping as two
  named permutations and lets the data choose, with a 2000-draw permutation null. It also says in
  terms what it does not establish (within-subscale order), which is why the status is PARTIAL and
  not VERIFIED. Good script.
- `verify_COACH_Chen_2022_WHOQOL_BREF.R` tests the one axis that carried a decision (q26's option
  direction) with a falsifiable predicate, and deliberately reads the study's own Dataverse raw file
  instead of `irw_fetch()` to avoid the export quota. Also good.

**Two judgment calls, both settled by precedent rather than by inventing a rule:**

- `cogcontrol_gyurkovics_2019_flanker` ships `item_text` that IRW *reconstructed* — the arrow display
  ("↓↓←↓↓") decoded from trial data, since the OSF deposit ships no stimulus images. That is not a new
  category: `reconstructed` + `study_materials` covers 8 tables in the corpus and four of them are
  already uploaded (`depression_anxiety_stress`, `riasec`, `hypersensitive_narcissism`,
  `short_dark_triad`). Staged, with the reconstruction disclosed in the public note.
- `COACH_Chen_2022_WHOQOL_BREF` raised a WHOQOL **rights** question. Applying #1891 as ruled — it
  fires on a quotable restriction, never on an inference — no NC clause could be retrieved, and the
  wording came from a CC0 deposit, so the rule does not fire and the table is staged. Holding it
  alone would have been incoherent anyway: **the same instrument's wording is already published for
  three other IRW tables** (`altahla_2024_whoqol`, `altahla_2024_whoqol_bref` 2026-08-17,
  `burkert_2019_whoqol_bref` 2026-08-18). Filed corpus-wide as #1927 instead; it covers 7 tables.

**Issues filed:** #1924 (`IADL`, 65 out-of-range responses — data defect, not a mapping error),
#1925 (`CSQ`, dictionary names Larsen's CSQ-8 but the items are Baker's CSQ-9 short form — the fifth
dictionary defect the extraction pass has found), #1927 (WHOQOL rights, corpus-wide decision).
Commented on #1831 with the COACH cluster result, since that issue had specifically asked for the
WHOQOL direction to be checked against its own data — it was, and the codebook lost.

**Issues page: drafted, NOT applied.** `fixes/itemtext_issues_draft.md` has all 11 entries. They go
into `irw_site/itemtext_issues.qmd` when the tables actually ship — the drafter's rule is that a
table with a blank `uploaded` stamp gets no entry until then, and `check_issues_page.R` re-reports it
once it does. Putting them up now would describe issues in tables nobody can see. No REVIEW THESE TOO
section this time: all 11 shipped tables carry a `public_note`, so the drafter had no blind spot.

**Structural spot-checks passed:** `chinvararak_2021_phq15` ships genuine administered Thai in
`option_text` with English in `option_text_translated`, and `item_text_translated` is the canonical
`NA` token throughout — the documented signal that the base fields are a substitute.
`cinar_tanriverdi_2023_gad7` carries real Turkish beside real English. The `chuemchit_2024_*` pair
carries English with `_translated` = `NA`, the #1777 fallback shape. `choy_2022_extraneous_events`
and the flanker have no `language` column at all, which is correct for them.

**Next:** upload is Ben's step. On his confirmation — stamp `uploaded=<date>` in `provenance.csv` and
`mapping_verification.csv`, apply the 11 draft entries to the issues page, and delete the uploaded
`__items.csv` from `batch_020/` (sidecars stay). `clean/` is cleared by Ben, not by the pipeline.

---

## batch_021 — 2026-09-04

**12 tables claimed. Written 10 / blocked 2 / failed 0. Yield 83.3%.** Circuit breaker not tripped
(0% failed against the 30% threshold). **This round completes the round cap: `batch_021` exists, so
Step 0's first stop condition now fires and no further round should start** — the runner will decline
on its own, and 1,141 rows remain `pending` for whenever the cap is lifted.

**One agent per table, 12 in parallel.** No infrastructure failure, no rate limit, no content filter,
no export-quota trip. Every agent reported, so no agent needed the batch_019 "reported-failed but the
files are on disk" rescue.

**Export discipline held.** Every agent used `irw_table_sets()` / `table_sets.R` for ground truth and
ran `validate_items.R --table-sets`. Exactly one `irw_fetch` export was taken all round, by the `pwi`
agent on a 1,360-row table, to establish respondent-level CONTROL/EXP disjointness — which
server-side aggregates genuinely cannot show. That is the export-as-a-decision rule working as
intended.

**Gates.** `normalize_nulls` 0 of 10 needed normalizing (agents wrote clean `NA` tokens).
`audit_batch` **10/10 PASS with no anomalies — no WARNs at all**, so Step 5c had nothing to explain,
a first for a full round. `verify_batch` 6 PASS / 4 MISSING(exempt), no FAIL and no missing VERDICT.
`irw-validate` ok on all 10 (2 checks each; no `dup_item_resp`, no `resp_ambiguous` — notable for
`conner_2017_bfi` and `conner_2017_cesd`, which deliberately ship two anchor directions in one table
and correctly do not trip the per-item-direction-is-legitimate carve-out). `check_provenance` clean:
291 provenance rows over 23 files, 69 IRW-generated tables, 0 with no issues-page entry.

**`lint_verification`: 4 ERROR → 0 ERROR, 1 WARN (adjudicated, kept).** The ERRORs were mine, not the
agents': I had added the four `NOT_NEEDED` rows for the `data_labels` tables to the permanent
`mapping_verification.csv` but not to the batch's own `verification_merged.csv`, which is what lint
reads. Fixed. The surviving WARN is on `conspiracy_asd__asd_aq10` ("VERIFIED but its evidence
hedges"), and I kept VERIFIED: the hedge is scoped to route B (option direction), while route A
carries the item axis and does separate every item from every other — source columns 53-62 reproduce
the live per-item means to 0.00e+00 with all 10 means distinct at 2 d.p. Reasoning recorded in
`notes.csv` rather than left for the next reviewer.

**Near-miss worth recording — the `rm` trap has a second mouth.** The protocol's warning is about
`rm -f verification_*.csv` eating `verification_merged.csv`; I avoided that by merging to `_m_*.csv`
names and deleting the 32 source files by name from a list. But the list was written with
`"\n".join(...)` — no trailing newline — and `while read -r f` silently drops an unterminated final
line, so `verification_conspiracy_asd__asd_aq10.csv` survived. Harmless here (its row was already in
the merge, and I removed it explicitly after checking), but the same slip in a delete-then-rename
sequence is exactly how a file gets orphaned. Terminate the list, or count what you deleted.

**Step 5b orchestrator re-check — one claim verified, one stale artifact found.** The agent claims
that override a source or report a data defect (`bfi` 16 reverse-keyed items, `cesd` 4 flipped
anchors, `soc13`'s unique {1,2,3,7,10} subset reproducing `SOCTOTAL` 921/921, `mlq`'s override of its
own pre-registration's stated scale direction) all carry `verify_*.R` scripts that re-ran and PASSED
under `verify_batch`, so they are independently re-executed by construction. The one load-bearing
claim with no verify script — `conner_2017_vitality`, `data_labels`-exempt — I checked by hand and
**CONFIRMED**: `metadata/biblio.csv` reads verbatim "Subjective Vitality Scale (4 items, 0-100
continuous), baseline/follow-up, N=171", which is internally inconsistent — it names the SVS (Ryan &
Frederick 1997: 6- or 7-item, 1-7 Likert) while describing SF-36 Vitality's structure.
`metadata/metadata.csv` independently gives n_items=4, n_categories=6, n_participants=171: four items
over six discrete levels (0/20/40/60/80/100 per SF-36 guidance), which the SVS cannot produce, and
which also makes "0-100 continuous" wrong — it is 6-category ordinal. A third, independent hit:
`tags/tags_auto.csv` line 930 flagged the identical contradiction in an earlier unrelated pass.
**Stale counter-claim to fix:** `itemtext/availability_audit_full.csv` line 851 still asserts this
table is "the well-known Subjective Vitality Scale" — that row is wrong and should be corrected with
the biblio Description. Dictionary/metadata defect, not an itemtext defect; the shipped table is
correct.

**Step 3b instrument mismatches found (3).** (1) `conner_2017_vitality` — above; the dictionary
correction is owed. (2) `conner_2017_curiosity` — the paper's Measures section describes only a
*single* daily smartphone curiosity item, so the 10-item table reads as a mismatch until you find the
CEI-II (Kashdan et al. 2009) living only in the deposited SPSS file as `cei1..cei10`; easy to
misread, worth flagging to anyone auditing this study. (3) `cognitive_load_klimova_2023_stomp` — the
deposit's own DataCite metadata lists the study's scales as "PWI, BZGS, MAS-R, MLQ" and never mentions
STOMP, so the "Short Test of Musical Preferences" reading rests on the column prefix alone and could
not be confirmed. Contributed to that table's block.

**Other findings worth keeping.** `cognitive_load_klimova_2023_mlq` holds 9 of the MLQ's 10 items
(item 10 absent from the response data, not padded) and its shipped scale direction **contradicts the
study's own AsPredicted #134579 pre-registration**, which states "1 (Absolutely True) to 7 (Absolutely
Untrue)"; the data say the opposite (Presence 4.42/4.44, Search 4.89/4.68, reverse item 9 at
3.41/3.15, matching Steger's student norms only under the canonical direction). Canonical direction
shipped, override documented — the pre-registration is wrong, and this is the second round running in
which a study's own metadata lost to its own data. `conspiracy_asd__asd_aq10` ships
`wording_rights=NC` on every row: the wording came from a CC BY 4.0 Figshare deposit so under irw#1891
it ships, but the ARC rights page carries a quotable non-commercial clause; an issues-page entry is
owed when it goes live. Its coded workbook header row is also corrupted by a find/replace artifact
(`2tice`/`do 2t`/`k2w` for notice/do not/know) — the survey docx was used instead.

**The two blocks are one deposit, and one human action clears both.**
`cognitive_load_klimova_2023_pwi` and `_stomp` are both blocked on openICPSR E194063V2, which is
Cloudflare-403 to every automated route and requires an account before any download, with the only
publication (Field Methods 38(1):46-61) closed access and zero OA locations. Both are `blocked`, not
`failed`: the wall is a registration gate plus a paywall, and both agents additionally reached a
determinate finding independent of access — the item codes are contentless letters (`a..h`, `a..i`)
that no canonical instrument can be keyed to without fabrication. The third sibling, `_mlq`, shipped.
**A single authenticated openICPSR download of `Final_data.csv`'s headers/labels would likely resolve
both blocks at once** — that is the highest-value human action this round surfaced. Full retry tests
and the structural facts already established (between-subjects arms, letter-identity across arms, the
suspected off-scale `resp=6` "don't know" code) are in `pending_index_notes.csv`.

**Provenance shape:** 7 `data_labels`, 3 `reconstructed`, 2 `unknown` (the two blocks).
Verification: 2 VERIFIED, 4 PARTIAL, 2 NO_ROUTE, 4 NOT_NEEDED — 12 tracker rows, one per claimed
table, and every written table has exactly one.

**Next:** upload is Ben's step, and nothing here has been uploaded. On his confirmation — stamp
`uploaded=<date>` in `provenance.csv` and `mapping_verification.csv`, add the `conspiracy_asd__asd_aq10`
NC-rights entry to the issues page, and delete the uploaded `__items.csv` from `batch_021/` (sidecars
and `verify_*.R` stay). Separately owed regardless of upload: correct the `conner_2017_vitality`
description in `metadata/biblio.csv` and the stale row in `availability_audit_full.csv`.

**CAP REACHED — 2026-09-04T08:23-07:00.** `itemtables/batch_021` now exists, so Step 0's first stop
condition fires from here on and no further round should start. No self-cancel action was possible or
needed: there is no scheduler — `extraction_batches/run_round.sh` is human-triggered and checks the
same condition in bash before launching, so it will decline on its own. 1,141 rows remain `pending`
(plus 52 permanently `excluded` enem* tables) for whenever a human decides to raise the cap.

### batch_021 triage — 10 of 10 staged, 0 held

Gates re-run live at triage (not the round's own report). **Everything clean:** `normalize_nulls`
0 of 10 needed changes; `audit_batch` **10/10 PASS with no WARNs at all**, so Step 5c had nothing to
explain; `verify_batch` 6 PASS / 4 exempt; `lint_verification` 0 ERROR / 1 WARN; `irw-validate` ok on
all ten with no WARNs either (unlike batch_020, none of these table names are capitalised);
`check_provenance` clean.

**Staged into `clean/`: all 10.** Every non-`data_labels` table has its tracker row — `simon`, `mlq`
and `soc13` are `reconstructed`, and all three carry one. Note `clean/` now holds **21 files from two
batches**, batch_020's 11 and batch_021's 10, because batch_020 has not been uploaded yet. One upload
covers both; the hazard to avoid is uploading twice, since Redivis appends and the only check that
catches a doubled table is `COUNT(*)` against the source.

**The rights call on `conspiracy_asd__asd_aq10` is correct and worth restating.** The AQ-10 wording
was copied from a **CC BY 4.0** Figshare deposit, and `itemtext_standard.md` § Rights is explicit that
the licence of the source IRW copied from governs, not the instrument's own terms. The Autism
Research Centre's clause ("used for research purposes and not for commercial use") is an
instrument-level restriction, so it is **recorded rather than obeyed**: `wording_rights=NC` on every
row — and only on that table, per the omit-the-column-otherwise rule — plus an issues-page entry when
it ships. This is the ECR-R shape, not the TIMSS shape.

**The three verify scripts for the reconstructed tables are all substantive:**

- `verify_cognitive_load_klimova_2023_mlq.R` — the round overrode the study's **own pre-registration**
  (AsPredicted #134579 states 1 = "Absolutely True" … 7 = "Absolutely Untrue"); the data say the
  canonical direction. Two falsifiable predictions, tested on the two disjoint subsamples (Control
  n=83, Exp n=87). Presence 4.42/4.44 and Search 4.89/4.68 above the midpoint with reverse item 9 at
  3.41/3.15 matches Steger's student norms and mirrors them under the pre-registration's reading.
  Second round running where a study's own metadata lost to its own data.
- `verify_colomer_perez_2021_soc13.R` — the strongest test in the batch: reversing exactly items
  1,2,3,7,10 must reproduce the authors' own `SOCTOTAL` for every respondent, and no other subset of
  the 8192 possible should. Uses `irw_table_sets` for the code check rather than exporting.
- `verify_cogcontrol_gyurkovics_2019_simon.R` — decodes the display from two independent columns,
  same shape as the flanker in batch_020.

All three say plainly that they do not fix within-class order, which is why two are PARTIAL.

**The one lint WARN was already adjudicated by the round, correctly.** `conspiracy_asd__asd_aq10` is
kept VERIFIED: the hedge sentence is scoped to route B (option direction), while route A carries the
item axis and does separate every item from every other — source columns reproduce the live per-item
means exactly and all ten means are distinct at 2 d.p. The WARN catches the phrase, not the status.

**Triage caught one blind spot.** `conner_2017_curiosity` shipped with no `public_note`, and the
drafter's REVIEW THESE TOO section flagged it. Its `notes.csv` records that item wording is
transcribed verbatim from the study's SPSS file including a grammatical slip — item 1 reads "I
actively seeks as much information as I can in a new situation" where the published CEI-II reads "I
actively seek … in new situations". A user comparing against the published instrument would read that
as an IRW transcription error. Public note written by hand; the batch now has 21 draft entries and no
REVIEW section.

**Corrected an overstatement in the round's own summary.** It reported that "one authenticated
download of `Final_data.csv`'s headers would likely resolve both" blocked tables. Its own per-table
notes say otherwise: the openICPSR deposit contains **exactly two data files and no codebook,
README or questionnaire**, and the IRW item codes already ARE those column headers. So the download
returns strings we have. The real routes are author contact for the questionnaire, or SAGE access to
*Field Methods* 38(1):46–61 **and** that article reproducing the scales keyed to the letters. Filed
accurately as #1930.

**Issues filed:** #1929 (`conner_2017_vitality` is SF-36 Vitality, not the Subjective Vitality Scale
— biblio Description and `availability_audit_full.csv:851` both wrong; the sixth dictionary defect
this pass has found), #1930 (the two openICPSR blocks and what would actually clear them).

**Issues page: drafted, NOT applied** — 21 entries covering both staged batches, going up when the
tables ship.

### batches 020 and 021 — uploaded 2026-09-04

Ben ran `red_up` on the 21 staged tables. Verified before stamping, because a stamp that runs ahead
of the upload is worse than none and the read token cannot see drafts: `python3 -m red_up.drafts
--dataset irw_text --verbose` lists all 21 as `added` in the `irw_text` draft (34 pending in total —
the other 13 are batch_019's and the carver pilots, still unreleased, 1.6d since v15.1 and inside the
one-week window).

**Stamped `uploaded=2026-09-04`** on the 21 shipped tables in `batch_020/provenance.csv`,
`batch_021/provenance.csv` and `mapping_verification.csv`. The three blocked tables
(`choy_2022_intent_career`, `cognitive_load_klimova_2023_pwi`, `_stomp`) were left alone.

**Watch the unset value — the two trackers disagree.** `provenance.csv` leaves `uploaded` empty when
a table has not shipped, but batch_020's rows in `mapping_verification.csv` use the literal string
`no` (batch_019's use empty). A stamping pass that tests `if not uploaded.strip()` silently skips
every `no` row and then reports success, because the same test says they are already stamped. That
happened here and was caught only by counting rows changed against rows expected — 10 changed where
21 were due. Treat `''` and `no` as unset.

**Deleted the 21 uploaded `__items.csv`** from both batch directories. The sidecars stay, so each
folder still documents every table the batch claimed: `notes.csv`, `provenance.csv`,
`verification_merged.csv`, `audit_report.csv` and the re-runnable `verify_<table>.R` scripts —
including for the blocked tables, whose scripts record the structure a future attempt needs.

**Still not released.** `red_up` only ever writes the draft; publishing is a human action, and until
the version is released nothing uploaded is visible to `irw_fetch()`, `irw_itemtext()` or the site.
The 21 issues-page entries are already merged to `datapages/irw` main (PR #127) and describe tables
the corpus cannot yet serve — and `quarto_publish.yaml` is `workflow_dispatch` only, so the live page
has not rebuilt either. Three things are now waiting on a human: release the `irw_text` draft version,
trigger the publish workflow, and clear `itemtables/clean/`, which is Ben's to empty, not the
pipeline's.

## batch_023 — 10 written / 2 blocked / 0 failed (83.3% yield)

**Originally numbered batch_022, and renumbered.** The round was fired at 10:03 and **killed by Ben
at 10:20**, mid-Step-3, on a well-founded worry that it might be duplicating xingyi-zhang's work in
[#1935](https://github.com/ben-domingue/irw/pull/1935). It was not — that PR covers
`promis1wave1_*` and `ecps_sahm_2024_*`, this round claimed the next 12 alphabetically
(`conspiracy_asd__*` through `cormier_2024_*`), and the two sets are disjoint. But **both were
numbered `batch_022`**, which would have fused two unrelated batches into one directory with
conflicting `notes.csv`, `provenance.csv`, `verification_merged.csv` and `audit_report.csv`. This one
renumbered to `batch_023` because #1935 was already open and complete while this was local and
unfinished. Second collision of this kind; the COACH tables hit it from the other side.

**The kill cost nothing.** Extraction and the Step 3 merge had completed; only Steps 4-6 were
missing, so the round was closed out by hand rather than re-run.

**Written:** `conspiracy_asd__{cognitive_flexibility,conspiracy_gcbs,schizotypy,thinking_styles}`,
`cooper_2018_{funny_topics,offensive_topics}`,
`cormier_2024_{cognitive_decline,personality,phq4,pss4}`.

**Gates, all run at close-out:** `normalize_nulls` 0 of 10 needed changes; `audit_batch`
**10/10 PASS with no anomalies**; `verify_batch` 3 PASS + 7 exempt (`data_labels`);
`lint_verification` **0 ERROR** / 2 WARN; `irw-validate` ok on all ten; `check_provenance` clean.

The 0 ERROR is worth noting: the Step 3 fix from batch_021 — write `NOT_NEEDED` rows into the
batch's own `verification_merged.csv` as well as the permanent tracker — held. Two consecutive
rounds had thrown 3 and 4 spurious lint ERRORs before it.

**Blocked (2), both determinate and both on rights, not access.**
`contreras_valdez_2022_bsq` and `_rses` are the Mexican Spanish BSQ-16 and RSES. The wording was
**located in both cases** — Amaya Hernández A (2013), UNAM doctoral thesis TESIUNAM 0704071,
Apéndices A and B — and cannot be shipped: the thesis front matter states *"DERECHOS RESERVADOS …
PROHIBIDA SU REPRODUCCIÓN TOTAL O PARCIAL"* with use restricted to educational and informational
purposes. That is a quoted, source-level non-commercial restriction plus an explicit bar on partial
reproduction, and under the 2026-09-04 ruling the licence of the source actually copied from
governs. Same shape as TIMSS 2003 and `chinvararak_2021_ecr`. Retry test NO for both.

**A finding worth keeping even though its table is blocked.** `contreras_valdez_2022_rses`: the
deposit's stated anchor direction is almost certainly **reversed** relative to the stored data. The
Keys sheet and the paper both say 1 = *totalmente de acuerdo*, but the file's own `rses_pse` /
`rses_nse` factor scores are raw sums of exactly the positively- and negatively-worded item sets and
only reconcile the other way round (−0.395 and +0.287 against `edeq14_overall`, matching the paper's
own convergent-validity result). Read with the printed anchors, a general-population sample would be
agreeing they are useless (means 1.43–1.54) and disagreeing that they have good qualities (means
3.28–3.58). An extraction that trusted the Keys sheet would have shipped the anchors backwards.
Recorded in `pending_index_notes.csv` and re-runnable as `verify_contreras_valdez_2022_rses.R`.

**Both lint WARNs adjudicated, both kept VERIFIED** — same pattern as batch_021, the lint fires on
the phrase "does not establish" rather than on the status. `conspiracy_asd__thinking_styles` says in
terms that all ten (mean, floor%, ceiling%) signatures are distinct with closest-pair distance
0.8349, so every item is separated; its hedge is about unlabelled scale midpoints, not the item axis.
`cooper_2018_funny_topics` is the stronger of the two: the Hungarian optimum over all 34!
text-onto-code assignments lands on the shipped identity assignment with 0 items reassigned, where
nearest-neighbour alone would have left 8 ambiguous. Its hedge is about `option_text` describing the
0/1 check-all-that-apply coding rather than transcribed wording.

**Circuit breaker:** 0 of 12 failed (0%), threshold 30%. Not tripped.

Not yet triaged, not staged, not uploaded.

### batch_022 triage (xingyi-zhang, #1935) — 20 of 20 staged, 0 held

Not one of my rounds: extracted by @xingyi-zhang against #1831 and merged as #1935. Triaged here on
Ben's ask. **This is the cleanest batch the pipeline has produced.**

Gates re-run live at triage: `normalize_nulls` 0 of 20 needed changes; `audit_batch` 16 PASS / 4
WARN, all four explained below; **`verify_batch` 20/20 PASS**; `lint_verification` *no problems
found*; `irw-validate` no ERRORs **and no WARNs**; `check_provenance` clean. Verification mix is 9
VERIFIED / 11 PARTIAL, and lint agrees each status matches its evidence.

**The verification design is better than ours and worth copying.** Rather than testing the mapping
statistically after the fact, `rederive_promis.py` and `rederive_ecps.py` rebuild the shipped text
from the source — the PROMIS Wave 1 codebook, and the administered COVIDiSTRESS Qualtrics form plus
two registration workbooks — and the verify scripts diff the CSV against that rebuild rather than
against a prose claim. The re-derivation output is committed as JSON, so the scripts re-run
elsewhere without the source cache.

**One limit of re-running them here**, worth stating so nobody over-reads a green result: without
`.cache/ecps_sahm_2024/` and the PROMIS cache — both gitignored and local to the extractor's machine
— the scripts diff against the *committed* re-derivation, not a fresh rebuild from the PDF. Here
that tests internal consistency; on the extractor's machine it tested source fidelity.

**Four audit WARNs, none an itemtext defect.** All are applicability-driven missingness, which is
what a branching survey produces:
- `promis1wave1_physicalfunction` — PFC1-PFC5 are missing their top option 'Very easy'; n runs
  1069-2145 against a 2535 median, and the deficit tracks item easiness (Spearman ≈ -0.8), which is
  what dropping the easiest response looks like and what a category collapse does not.
- `ecps_sahm_2024_distrust` — the form randomises the misperception blocks one-of-three.
- `ecps_sahm_2024_stress` — the secondary-stressor block is conditional; per-index n follows the
  branch that gates it (student ≈1,140, children ≈3,200, occupation ≈9,900).
- `ecps_sahm_2024_sscd` — compliance shown to all (n≈15,300), the two norm blocks to a subset
  (n≈3,800); and its '47.6% blank option_text' is 80 unlabelled midpoints on the two
  `socialinfluence_nor*` ladders, which label only their endpoints.

**Two gaps triage closed rather than reported:**

1. **The batch shipped no `notes.csv`.** Per-table detail is in `provenance.csv`'s `note` column
   instead (838-4,158 chars, median 2,765) so nothing was lost, but Step 5c's "append the reason to
   that table's `notes.csv` row" had nowhere to go. Created one carrying the four WARN explanations.
2. **The misattribution was disclosed in only 1 of 11 public notes.** Amended the other 9 affected
   (all `ecps_sahm_2024_*` except `_emotion`, which genuinely is the ERQ short form). Without it a
   reader of the issues page sees a dictionary that says Emotion Regulation Questionnaire and no
   indication it is wrong — the same gap `COACH_Chen_2022_CSQ` and `conner_2017_vitality` had.

**Issue filed: #1936**, the largest dictionary defect this pass has found. Ten of eleven
`ecps_sahm_2024_*` tables are attributed to the wrong *study* — Sahm et al.'s German ERQ-S
validation rather than COVIDiSTRESS Global Survey Round II, whose data file is hosted inside that
OSF project. Re-verified three ways independently of the extraction: the ERQ has two subscales and
there are eleven tables; every table carries `cov_covid_self` and `cov_residing_country`; and they
hold 12,988-15,736 participants rather than a German validation sample. `biblio.csv` also keys these
as `ECPS_Sahm_2024_*` against `metadata.csv`'s lowercase, so any case-sensitive join drops all
eleven.

**Staged all 20 into `clean/`.** Every non-`data_labels` table has its `mapping_verification.csv`
row. The 11 `paper_order` + PARTIAL tables were the ones to look hardest at, and they hold up: the
mapping rests on the administered form's order, the re-derivation checks every shipped string
against that form, and PARTIAL is the honest status because order is what ties text to code.

### batch_023 triage — 10 of 10 staged, 0 held

Gates were run live at close-out earlier today and were clean throughout —
`normalize_nulls` 0 of 10, `audit_batch` **10/10 PASS with no anomalies**, `verify_batch` 3 PASS +
7 exempt, `lint_verification` 0 ERROR / 2 WARN, `irw-validate` ok, `check_provenance` clean — so
triage did not re-run them a third time. What it added was the per-table go/no-go and the public
notes.

**All 10 are `mapping_basis=data_labels`**, the strongest basis: the source file's own labels tie
code to text, with no positional inference for a statistic to check. Both lint WARNs were
adjudicated at close-out and both stay VERIFIED — `conspiracy_asd__thinking_styles` (all 10
mean/floor%/ceiling% signatures distinct, closest pair 0.8349) and `cooper_2018_funny_topics` (the
Hungarian optimum over all 34! text-onto-code assignments lands on the shipped identity, 0 items
reassigned, where nearest-neighbour alone leaves 8 ambiguous).

**The drafter's REVIEW THESE TOO section earned its place again.** Six shipped tables carried no
`public_note`, and five of the six turned out to have a caveat a data user would otherwise
misread. Written by hand:

- `conspiracy_asd__cognitive_flexibility` — **the deposit's coded workbook is corrupted** by a
  global find/replace of 'no' to '2' ("I feel I have 2 power", "I just don't k2w what to do"), so
  the wording was taken from the plain-text survey document instead. Anyone comparing this table
  against those workbook labels finds differences and would have no way to know which is right.
- `conspiracy_asd__thinking_styles` — REI-10; only the two extreme scale points are labelled, so
  `option_text` is blank at responses 2-4 by design rather than missing. Same corruption caveat.
- `cooper_2018_funny_topics` and `_offensive_topics` — select-all-that-apply checklists, so `resp`
  is a checkbox state and 'Selected' / 'Not selected' describe that 0/1 coding rather than
  transcribing anything the survey printed.
- `cormier_2024_phq4` — the Qualtrics header concatenates a shared block stem with each item stem;
  the stem ships once in `instructions`, so an item here is shorter than its source column header.

`cormier_2024_cognitive_decline` is the one left without a note, correctly: it has no `notes.csv`
entry either, i.e. a clean pass with nothing to disclose.

**Staged all 10.** `clean/` now holds **30 files** — batch_022's 20 and batch_023's 10 — for one
upload.

**One judgment left to a human rather than taken here.** `cooper_2018_offensive_topics` ships item
text that is a list of demographic and identity categories, because the study (Cooper 2018) was
about which topics people find offensive. That is inherent to the research and the transcription is
faithful, so nothing about it is a data defect and no note was written. Whether IRW wants any
content signposting on tables of this kind is an editorial policy question, not an extraction one.

### batches 022 and 023 — uploaded 2026-09-04

30 tables uploaded by Ben and verified in the `irw_text` draft with `red_up.drafts --verbose` before
anything was stamped. Stamped `uploaded=2026-09-04` in both batches' `provenance.csv` and in
`mapping_verification.csv`; deleted the 30 uploaded `__items.csv`, sidecars kept. `clean/` was
emptied by Ben. Issues-page entries applied as datapages/irw#128 (201 → 230).

**A THIRD convention for "not uploaded", and the audit that missed it.** This morning's note said to
treat `''` and `no` as unset. batch_022 uses neither: its `uploaded` column holds the literal
**`NA`**, which is the project's canonical null token and therefore the likeliest form of all. The
stamping pass skipped all 20 rows, and the audit — sharing the same `UNSET` predicate — reported
them as already stamped. The rule that actually works is the inverse one:

> **A row is stamped only if it holds a real date (`^\d{4}-\d{2}-\d{2}$`). Everything else is
> unstamped, whatever it says.**

That needs no list of null spellings and cannot be defeated by a fourth one appearing.

**And the audit must not share a code path with the thing it audits.** Rewritten with the date rule,
the stamp function reported 20 rows changed while the audit read 20 still unstamped — because the
rewrite had dropped its `open(path,'wb').write(...)` line. It counted without persisting. Only an
audit that re-read the files from disk caught it; one built on the same helper would have agreed
with the bug twice.


### WHOQOL item text withdrawn — 2026-09-04

Ben ruled that **IRW does not offer WHOQOL item text**, closing #1927. Six tables are now `blocked`;
four of them had already shipped and are being withdrawn.

**The clause that decided it is not the one #1927 went looking for.** That issue asked whether the
WHOQOL carries a *non-commercial* restriction, and the answer is essentially no — commercially
funded use attracts a royalty (NZ$500 for a single study), which is a fee, not a prohibition. The
terms found today state something narrower and more directly fatal:

> "You agree that you will not reproduce copies of the WHOQOL instruments except for the limited
> purpose of generating sufficient copies for use in investigations stated hereunder and shall in no
> event distribute them to third parties by sale, rental, lease, lending or any other means."
> — AUT / NZ WHOQOL, *Terms and Conditions of Use of the WHOQOL Tools*

Shipping item text **is** distributing the instrument to third parties. An NC clause restricts who
may use it; this restricts the act IRW performs.

**It took a text proxy to read it, which is the reusable lesson.** `cpcr.aut.ac.nz` returns 403 to a
direct fetch and Manchester's user-information PDF fails on a TLS certificate mismatch
(`research.bmh.manchester.ac.uk` presents a certificate for `apps.mhs.manchester.ac.uk`), so the
batch_020 extraction concluded no clause could be quoted and shipped the table under the
source-licence rule. That conclusion was reasonable on the evidence it had and still wrong.
**Absence of a retrievable clause is not absence of a clause** — when a rights page is unreachable
rather than silent, say so as a distinct finding instead of treating it as permission.

**This is a deliberate exception to the source-licence rule, recorded as such** in
`itemtext_standard.md` § Rights. IRW's WHOQOL copies came from openly licensed deposits — CC0 in the
COACH case — so under the ECR-R ruling they would ship. The ruling honours the rights holder's
no-redistribution term anyway. It is scoped to the WHOQOL and does **not** generalise itself: whether
any quotable no-redistribution clause should override the source licence is left as an open question
for a later, deliberate ruling, because settling it the other way would reverse ECR-R for a whole
class of instruments.

**Done here:** all six tables `blocked` in `queue_state.csv` (done 206 → 202, blocked 17 → 23,
pending 1,112 → 1,110); the four shipped rows carry a withdrawal note in `provenance.csv` with their
`uploaded` date kept as history rather than falsified; six rows added to `pending_index_notes.csv`;
the rule written into the standard; and the four issues-page entries rewritten to record the
withdrawal rather than describe wording that no longer exists (datapages/irw#129). **Ben removes the
tables from the `irw_text` draft** — that is the part that makes it true in the warehouse.

## batch_024 — 2026-09-04

**12 tables claimed · 12 written / 0 blocked / 0 failed · yield 100%.** Best round of the
series so far, and the first with no block at all. 1,370 item-text rows.

| table | rows | mapping_basis | audit | verification |
|---|---|---|---|---|
| corti_2023_academic_adaptation | 35 | data_labels | PASS | VERIFIED |
| cox_2024_feedback_perceptions | 15 | data_labels | PASS | VERIFIED |
| CPDMMC_Kunnari_2020_HCD | 84 | paper_explicit | PASS | VERIFIED |
| CPDMMC_Kunnari_2020_PDP | 36 | paper_explicit | PASS | VERIFIED |
| CQTMS_Hur_2023 | 800 | paper_order | WARN | PARTIAL |
| cucchi_2018_kims | 90 | data_labels | PASS | NOT_NEEDED |
| cucchi_2018_rfq | 56 | data_labels | PASS | NOT_NEEDED |
| cucchi_2018_scoff | 10 | data_labels | PASS | VERIFIED |
| cucchi_2018_tas20 | 100 | data_labels | PASS | PARTIAL |
| cugmas_2021_elderly_social_support | 64 | data_labels | PASS | VERIFIED |
| CV_OASIS_ODSIS_PPE_Novak_2020_BFI | 40 | reconstructed | PASS | PARTIAL |
| CV_OASIS_ODSIS_PPE_Novak_2020_DSES | 40 | reconstructed | PASS | PARTIAL |

**Gates.** normalize_nulls 0/12 needed changes. audit_batch 11 PASS / 1 WARN.
verify_batch 10 PASS + 2 MISSING(exempt) — no FAIL, no missing VERDICT.
lint_verification 12 rows, **0 ERROR**, 6 WARN. irw-validate: no ERROR.
check_provenance clean (69 IRW-generated tables, 0 without an issues-page entry).

**Why the yield was this high.** Nine of the twelve reached a level-1 source that ties code
to text directly — six SPSS `.sav` deposits with self-prefixed variable labels, an OSF
codebook keyed by column name, an `.xlsx` whose headers are the questions. The head of the
queue happened to serve up depositing studies rather than the large closed-source datasets
that produced the block clusters in batch_016 and batch_019. This is a fact about which
tables came up, not a pipeline improvement — do not read it as a new baseline.

**The one audit WARN is a source property, not a defect.** CQTMS_Hur_2023 ships blank
`item_text` for 81 of its 160 items: Hur & Seo published wording only for the 79 items that
survived screening, and the 81 dropped preliminary items appear in neither the article, its
five supplements, nor the CC0 Dataverse deposit. Blank beats invented. Explained in notes.csv;
it will recur on every re-run and is not actionable.

**Orchestrator re-check (Step 5b).** The `CPDMMC_Kunnari_2020_HCD` agent recorded VERIFIED
while its own evidence said the VT/V code pair "cannot be separated statistically" — the exact
shape lint_verification flags. Re-checked rather than downgraded: the codes are content-coherent
with the shipped dilemmas (VT = vaccine test, V = vitamin-deficiency kidney), and the ordering is
predictable independently of the codebook, since VT kills one to save millions while V takes a
kidney from a man who survives to save six. Observed means run VT 4.780 > V 3.493, as that
predicts. Route 8 separates the pair the mean-identity check could not; VERIFIED stands and the
evidence string now carries the re-check. The other five lint WARNs were adjudicated and left
alone — each hedges about the `option_text` axis, transcription fidelity, or source identity,
none of which bears on whether the route distinguishes every item from every other item.

**TWO LICENCE DECISIONS FOR BEN — both shipped under the current rule, both withdrawable.**
`itemtext_standard.md` says the WHOQOL no-redistribution ruling must not be extended to another
instrument without asking, so both tables shipped by default and are flagged rather than blocked:

1. **`cucchi_2018_tas20`.** The TAS-20 holders charge a US$40 copyright fee and have enforced it
   (a 2021 *Molecular Autism* paper was retracted for using the scale without permission). But a
   fee is not a non-commercial clause and not a redistribution bar, and IRW's copy came from a
   CC BY 4.0 PeerJ deposit that published all 20 items itself — so the ECR-R source-licence rule
   governs and `wording_rights` was left unset. If fee-licensed instruments should be treated like
   WHOQOL, this withdraws `cucchi_2018_tas20`, the already-live `rmet_higgins_2022_tas`, and the
   pending `ruiz_parra_2023_tas20`.
2. **`CV_OASIS_ODSIS_PPE_Novak_2020_DSES`.** Underwood requires registration, states the scale is
   free for non-profit use, and the Fetzer compendium copy reads "Permission of author required to
   distribute or copy" — a redistribution bar of the same shape as WHOQOL's. Shipped because the
   wording was transcribed from Underwood's own CC BY 3.0 article, but every row carries
   `wording_rights=NC`. This is the one table an `NC` query finds.

**Other things worth knowing.**
- Five `name_charset` WARNs from irw-validate (CPDMMC_*, CQTMS_*, CV_*) are properties of existing
  capitalised corpus table names, not of these extractions. Upstream; nothing to fix here.
- `CQTMS_Hur_2023`: Supplement 1's row for item I21 is byte-identical to I133's — a duplicated row
  in the published supplement. It cost one item its distribution check; the other 78 pinned the
  `itm<n>` = `I<n>` mapping regardless.
- `cucchi_2018_tas20` and `cucchi_2018_kims` both use subscale-grouped SPSS numbering that is NOT
  canonical instrument numbering. Recorded as public_notes so the codes are not misread.
- `CV_OASIS_ODSIS_PPE_Novak_2020_BFI` and `_DSES` were both administered in Czech with no Czech
  wording published anywhere in the deposit; both ship canonical English with `language=Czech` and
  empty `_translated` columns — the documented backfill signal, and two more rows for that queue.
- Three agents independently noted they declined to run the batch-wide `normalize_nulls.R` /
  `audit_batch.R` because 11 siblings were live in the directory. One ran normalize_nulls anyway
  and reported normalising a file that may have been a sibling's. Harmless here (idempotent, and
  the orchestrator's own run found 0 of 12 needing changes), but the per-table subagent prompt
  should say explicitly that batch-wide scripts belong to the orchestrator.
- Merge-cleanup near-miss: the per-table sidecar list was deleted by name, as required. The last
  entry had no trailing newline, so `while read` skipped it and one `verification_*.csv` survived;
  removed by name afterwards. Whoever scripts this next should write the list newline-terminated.

**CAP REACHED.** batch_024 is the cap raised in 4dcd2ee. The next firing will hit the
"batch_024 already exists" stop condition in Step 0 and stand down. 1,098 tables remain
pending; raise the cap to continue.

---

## batch_025 — 2026-09-04T12:17:38 → ~12:35

**12 tables claimed. 8 written / 4 blocked / 0 failed.** Yield 8/12 = 67%. Circuit breaker NOT
tripped: 0% failed against the 30% threshold. Every block is a determinate verdict with retry
test = NO; none is an access failure, and no round-level rate limit or spend cap was hit.

Written: `CV_OASIS_ODSIS_PPE_Novak_2020_RSES` (40), `dahlstrom_2022_scoare` (80),
`daiku_2021_dirty_dozen` (60), `dalky_2020_sf36` (146), `dasilva_2019_hexaco24` (120),
`dass_Thiyagarajan2022` (84), `dd_rotation` (20), `debacker_2018_decisionjustification` (24).

Blocked: `daiku_2021_lie_scale` (wording never published — the paper gives one unkeyed English
exemplar of a 3-item subset drawn from Yanai et al. 1987), `DART_Brysbaert_2020_1` and
`DART_Brysbaert_2020_3_4_5` (both CC BY-NC-SA on the test material; two agents reached this
independently), `debacker_2018_justice_appraisal` (wording fully published and CC BY, but nothing
ties an item to a code below subscale level, and the data *refutes* the S2 presentation order).

**Gates.** normalize_nulls 0 of 8 changed. audit_batch 7 PASS / 1 WARN. verify_batch 6 PASS,
2 MISSING(exempt). lint_verification 0 ERROR / 2 WARN. irw-validate clean (2 `name_charset`
WARNs on pre-existing capitalised corpus names). check_provenance clean — 347 rows, 69
IRW-generated tables, 0 without a public issues-page entry.

The Step 3 NOT_NEEDED rows for the two `data_labels` tables were written into BOTH
`verification_merged.csv` and the permanent tracker, so lint came back with 0 ERROR — the
batch_020/021 false alarm did not recur.

**Audit WARN explained (Step 5c).** `dahlstrom_2022_scoare`: KB and KR carry 316 rows against a
median of 182. Not conflation and not an itemtext defect — those two knowledge items were asked in
both program years while every other item ran in one year only, which the processing script already
documents. A property of the response data.

**The two residual lint WARNs are expected.** Both DART rows are `NOT_NEEDED` with
`mapping_basis=unknown`, which the lint flags because only `data_labels` is exempt. Both ship no
CSV: there is no mapping to verify because the table was blocked on rights. Not a gate failure.

**Orchestrator re-checks (Step 5b) — one agent finding corrected, one confirmed.**

1. **CORRECTED — the `debacker` resp=0 claim.** The agent reported resp=0 as an unstripped
   not-applicable code, evidenced by "four person-game rows have all 12 items = 0 with
   playing_match = 3 (niet spelen)". Re-reading the PLOS S3 `.sav` directly: **two** rows have all
   12 justice items = 0, and five have all 4 decisionjustification items = 0 (only 2 of those are
   playing_match=3). The zeros are overwhelmingly *partial* — 19 of the 21 justice-block rows with
   any zero have some-but-not-all zeros, 74 zero cells in all — and those rows split across
   playing_match 1/2/3 as 9/4/8, tracking the overall 387/161/113 distribution. Carrying a zero is
   therefore **not** associated with not having played, and the person-level explanation does not
   survive. What does survive: resp=0 is outside the paper's stated 1–5 scale, is rare (5–8 per
   item), and sits scattered singly inside otherwise-normal response vectors — a per-item skip code,
   not a scale point. Still worth an issue against `data/debacker_2018_coaching_justice.py` (drops
   only NaN), but filed as "out-of-range 0 of unknown meaning". Both debacker notes rows amended.
2. **CONFIRMED exactly — the DART `ja`→`1` corruption.** `raw_data_study1.xlsx` has 138 headers, of
   which four carry the global find/replace damage: `Is de volgende persoon een auteur- [1ne
   Austen]`, `[1mes Patterson]`, `[1ne Jessup]`, plus the covariate `Aantal boeken gelezen in het
   afgelopen 1ar-`. All three name codes are live in IRW verbatim. A real defect in a published
   table, independent of the rights block.
3. **Status downgraded on evidence.** `dasilva_2019_hexaco24` was filed VERIFIED while its own
   evidence said the range signature pins only 3 of 24 positions. Changed to `NOT_NEEDED`, which is
   the right label for `data_labels` and matches what the sibling `dalky_2020_sf36` did in this same
   batch. Full evidence string retained.

**Other things worth knowing.**
- **The DART rights block is a policy question, not a research one.** IRW already publishes the
  132 DART names — they *are* the live `item` codes, ingested from the same CC BY-NC-SA deposit. So
  the block bars an itemtext table while the wording sits in the response table's join keys. Worth
  a ruling.
- **Wrong DOI in a PLOS reference list.** Daiku et al. 2021 cites Tamura et al. 2015 as
  `10.2132/personality.26.1.2`, which resolves to the SD3-J paper. Correct: `10.2132/personality.24.26`.
  The availability audit and any retry would follow the printed DOI into the wrong article.
- `daiku_2021_dirty_dozen`'s wording came out of a **stencil image** (DTDD-J Appendix 2), invisible
  to `pdftotext` and recovered with `pdfimages -f 11`. Hand-transcribed — worth a spot-check.
- `dalky_2020_sf36` is the second SF-36 to ship (after `bukurov_2022_sf36`, batch_009) on the
  source-licence rule: the wording came from the CC BY 4.0 PeerJ deposit's own SPSS labels, and no
  NC or no-redistribution sentence is quotable for Optum/QualityMetric.
- `CV_OASIS_ODSIS_PPE_Novak_2020_RSES` does **not** use Rosenberg's 1965 item order — the study's
  own script reverse-scores 2/5/6/8/9 (the Morris Rosenberg Foundation form), and the live data
  reproduces that split exactly, 1 of 252 possible subsets. Anyone assuming canonical numbering here
  ships five items wrong.
- `dd_rotation` is a figure-stimulus task with no administered prose, but unlike
  `twod_rotation_mather2023` (held from upload for 100% blank `item_text`) every row carries a real
  referent — the per-item rotation angle published in diffIRT's `rotation.Rd`.
- Three tables ship with `language` set and empty `_translated` columns — the documented backfill
  signal: RSES (Czech), `dalky_2020_sf36` (Arabic), `dass_Thiyagarajan2022` (Malay).
- No Redivis export quota was spent on ground truth; agents used `irw_table_sets()` throughout, with
  two deliberate single-table exports (`dahlstrom_2022_scoare` for `item_stats.R`, and its verify
  script).
- Merge cleanup was done in Python, deleting the exact 33 filenames just merged and writing the
  merge output to a dotfile renamed afterwards — so the `verification_*.csv` glob trap could not
  fire. Recommended over the shell loop that near-missed in batch_024.

**CAP REACHED.** batch_025 is the cap raised in 484725d. The next firing will hit the
"batch_025 already exists" stop condition in Step 0 and stand down. 1,086 tables remain
pending; raise the cap to continue.

### TAS-20 item text withdrawn — fee-licensed instruments — 2026-09-04

Ben ruled that **an enforced licence fee disqualifies an instrument's wording**, extending the
WHOQOL ruling from no-redistribution clauses to fee-licensed instruments. The TAS-20's holders
charge a per-study fee and have enforced it (a 2021 *Molecular Autism* retraction).

**This goes further than the WHOQOL ruling, deliberately.** WHOQOL turned on a clause forbidding the
act of distribution. This does not: `cucchi_2018_tas20`'s wording came from a **CC BY 4.0** PeerJ
article that reproduced all 20 items itself, so IRW is declining to redistribute text an open
licensor already published. That argument was put before the decision and the ruling stands. Unlike
the WHOQOL ruling, this one **does** generalise — it is a rule about fee-licensed instruments.

**Done:** `cucchi_2018_tas20` deleted from the `irw_text` next draft (100 rows, verified absent
afterwards) and `ruiz_parra_2023_tas20` blocked before extraction — both `blocked` in
`queue_state.csv` (done 222 → 221, blocked 27 → 29, pending 1,086 → 1,085), both with a
`pending_index_notes.csv` row saying what would have to change. Ben removed the already-live
`rmet_higgins_2022_tas` from the draft himself; it remains in the released version until the next
release drops it. `cucchi_2018_tas20`'s provenance keeps its `uploaded=2026-09-04` as history and
carries the withdrawal in `public_note`; its `__items.csv` is deleted but
`verify_cucchi_2018_tas20.R` stays, so the mapping is still reproducible if the ruling is ever
reversed. Rule written into `itemtext_standard.md` § Rights.

**Still outstanding:** the issues-page entries for all three tables (datapages/irw), and
`wording_rights` is not set on these rows — the WHOQOL precedent sets `wording_rights=NC`, which is
the wrong flag for a fee rather than a non-commercial clause, so that column needs a decision.

### DSES item text withdrawn — no-redistribution clauses override the source licence — 2026-09-04

Ben ruled that **a quotable no-redistribution clause outranks the licence of the deposit the wording
came from**, withdrawing `CV_OASIS_ODSIS_PPE_Novak_2020_DSES`. The DSES requires registration with
Underwood and the Fetzer copy states "Permission of author required to distribute or copy"; IRW's
wording came from Underwood's own CC BY 3.0 article, which was ruled not to rescue it.

This settles the question the WHOQOL ruling explicitly left open, in the strict direction, and it is
the second ruling the same day narrowing ECR-R — the first being the fee-licence rule on the TAS-20.
Taken together, **a source deposit's open licence is no longer sufficient on its own.**

**Done:** deleted from the `irw_text` next draft (40 rows, verified absent), `blocked` in
`queue_state.csv` (done 221 → 220, blocked 29 → 30), `pending_index_notes.csv` row recording that
the author's permission is the one thing that would make it shippable on its own terms, provenance
keeping `uploaded=2026-09-04` as history with the withdrawal in `public_note`, `__items.csv`
deleted, `verify_*.R` retained. Rule written into `itemtext_standard.md` § Rights.

**Outstanding, and worth naming plainly:** no re-audit of already-shipped tables has been run
against either of the day's two rulings. Tables shipped before 2026-09-04 under "the source licence
governs" have never been checked for a rights-holder restriction, and some will not survive. This
table was the only one in the corpus carrying `wording_rights=NC`, so that column cannot be used to
find the others — the sweep has to read provenance and sources.

### DART: itemtext block stands, response data untouched — 2026-09-04

Ben ruled on the tension batch_025 surfaced. **The block stays and the response data is left alone**,
accepting an inconsistency rather than resolving it: the DART's items are author names, and IRW
already publishes all 132 of them as the live `item` codes in the response table, ingested from the
same CC BY-NC-SA deposit that caused the block. So the NC-restricted wording is public either way,
and the block prevents only an `__items` table.

Two alternatives were put and declined — ruling that a bare item identifier is not "item text"
(which would have made the two positions consistent on the record) and reviewing the DART response
tables themselves. Recording that here so this is not later mistaken for an oversight: it is a known
gap, left open deliberately.

**Still outstanding and independent of rights:** the `ja`→`1` find/replace corruption in
`raw_data_study1.xlsx` is live in IRW — `1ne Austen`, `1mes Patterson`, `1ne Jessup`, and a mangled
`...afgelopen 1ar-` covariate. No issue has been filed for it yet.

### Data defects from batches 024/025 filed — 2026-09-04

Three defects confirmed against primary sources during these rounds are now public issues:

- **irw#1950** — `DART_Brysbaert_2020_*`: a `ja`→`1` find/replace in the deposited
  `raw_data_study1.xlsx` put `1ne Austen`, `1mes Patterson` and `1ne Jessup` into IRW as live item
  codes, plus a mangled `...afgelopen 1ar-` covariate. `1ne Jessup` is one of the test's foils, so
  its exact string is what a reuser matches on. Damage is in the deposit, carried through unchanged.
- **irw#1951** — `cordova2019_clinical_edu_environment`: `biblio.csv` says "DREEM-based"; the
  instrument is PHEEM per the companion paper's own Methods and its 40-item Table 1. IRW holds real
  DREEM tables (`agarwal_2023_dreem`), so the mislabel makes this look like their sibling.
- **irw#1952** — `debacker_2018_*`: `resp=0` sits outside the paper's stated 1–5 scale.
  Filed as "out-of-range 0 of unknown meaning" and the issue states explicitly that the earlier
  "did not play" reading was **disproved** on re-reading the `.sav`, so it is not revived.

Worth noting what produced all three: none came from a gate. They came from reading a source against
its processing script, which is what the extraction step does anyway — the gates compare a table to
itself and cannot see any of these.

### Outstanding work filed as issues — 2026-09-04 (end of session)

Everything left open at the end of the day is now tracked, so nothing depends on this log being read:

- **irw#1954** — re-audit already-shipped item text against the day's two rights rulings. The
  important part: `wording_rights` cannot find the affected tables (it is set on zero tables now),
  so the sweep has to read provenance and re-check each instrument's rights holder. `canonical_instrument`
  tables are the highest-risk group.
- **irw#1955** — `wording_rights` cannot express a fee, and is currently set on no tables at all.
  Extend the vocabulary or drop the column; a one-value flag nothing carries is the worst option.
- **irw#1956** — clear the 45 uploaded `__items.csv` from batch folders. Must NOT be a directory
  glob: the two byte-identical `ALSECYPIAMH_WU_2022_PHQ` files were never uploaded, and deleting
  them loses the only copies.
- **datapages/irw#132** — issues-page entries for the three withdrawn tables. `rmet_higgins_2022_tas`
  is the one that matters: live now, and it disappears at the next release.

Also filed earlier today: irw#1950 (DART `ja`→`1`), irw#1951 (DREEM/PHEEM), irw#1952 (debacker `resp=0`).

**State at close.** queue_state: 220 done / 30 blocked / 12 failed / 54 excluded / 1,085 pending.
The `irw_text` next draft holds 111 tables, every one row-count verified against its source. Round
cap is `batch_025`, so the runner stands down until someone raises it. `delete_branch_on_merge` is
now **false** on `ben-domingue/irw`, which should stop the branch-deletion failure that hit twice
(#1904, #1944).

## batch_026 — 2026-09-04

**12 tables · 9 written / 3 blocked / 0 failed · yield 75%.** One agent per table, all 12 dispatched in
parallel; all 12 returned a report and none was killed by a rate limit or spend cap. Circuit breaker NOT
tripped (0% failed — the three no-CSV tables are determinate rights verdicts, retry test NO).

Tables: decamp_2022_online_discussion, deilkas_2019_patient_safety_climate, dejesus_2017_lequesne,
dejesus_2017_sf36, derubeis_2017_arsq, de_vries_2022_bat_burnout_core, de_vries_2022_bat_secondary,
de_vries_2022_hexaco_meta, de_vries_2022_hexaco_other, de_vries_2022_hexaco_self,
dinic_2025_shortdarktriad, direkvand_2022_mjsi.

**Gates.** normalize_nulls 3 of 9 normalized. audit_batch **9/9 PASS, zero WARN** (so Step 5c had nothing
to explain — notable given direkvand ships blank option_text on all 125 rows by design). verify_batch
6 PASS + 3 MISSING(exempt, data_labels). lint_verification 12 rows, **0 ERROR**, 2 WARN. irw-validate ok
on all 9. check_provenance: vocabulary clean.

**The round's story is a licence wall, not a pipeline problem.** Three of the five de_vries_2022 tables are
the Dutch HEXACO-PI-R (self / observer / meta-perception, 96 items each) and all three blocked on the same
non-commercial clause. The other two de_vries tables (BAT burnout core + secondary) passed cleanly — the BAT
is explicitly non-proprietary — so the split inside one source file is instrument rights, not access.

**Step 5b orchestrator re-checks (both changed or firmed up an artifact):**
- *HEXACO clause — CONFIRMED.* Three agents quoted it independently; re-fetched hexaco.org/hexaco-inventory
  directly and it is verbatim: "You can download any of these forms free of charge, but only for the purpose
  of non-profit academic research." The page also confirms the 200-item form is gated behind author contact
  and bars publicly searchable administration. The three blocks stand on a verified quote.
- *deilkas duplicate label — CONFIRMED but the claim was overstated, and the public note was corrected.*
  The agent reported Q34 and Q59 as carrying "byte-identical variable labels". They do not: the .sav has
  '31. Fatigue impairs my performance during emergency situations…' and '56. <same sentence>'. The numbering
  prefix is stripped on the way in, so what is byte-identical is the **shipped item_text** (verified on the
  written CSV). The substantive finding — a duplicated fatigue item in the deposit, Q34 the likely error,
  Q60 the routine-care twin — holds. public_note rewritten to say exactly that.
- direkvand's claim that the paper's published alphas of 0.96 (2 items) and 0.98 (4 items) are unreproducible
  is confirmed by its own verify script running live: observed 0.161 and 0.354, while communications (0.733 vs
  0.73) and whole-tool (0.705 vs 0.71) reproduce to within 0.005. Paper-side error, not a mapping error.

**ESCALATION — the NC ruling reaches already-live tables.** irw#1891 (2026-09-04) postdates several HEXACO-PI-R
uploads. `sv-maia2_randelovic_2021_hexaco60` and `sv-maia2_randelovic_2021_hexaco100` are **live** and shipped
HEXACO-PI-R wording that has never been audited against this rule; `zaehl2023_hexaco` and `lindstrom2021_*` are
queued behind the same clause; and `availability_audit_full.csv` classes the whole family AVAILABLE on the
reasoning that hexaco.org publishes the items freely — reasoning that does not survive the rule. Worth handling
as a class rather than table by table. `dasilva_2019_hexaco24` is unaffected (Brief HEXACO Inventory, CC BY).

**Upload-time obligation.** check_provenance flags `derubeis_2017_arsq` as the corpus's one IRW-generated-content
table with no issues-page entry (German ARSQ, English supplied by this project). It needs a line on
itemtext_issues.qmd at upload. Reported-but-not-enforced here: the irw_site checkout is on branch 'agent-brief',
not main.

**Two lint WARNs, both cosmetic and both explained in notes.csv.** hexaco_meta and hexaco_self recorded
status=NOT_NEEDED with mapping_basis=unknown; the linter only exempts data_labels. Both ship no CSV, so no
mapping reaches the corpus — the agents meant "nothing shipped, nothing to verify", where the third sibling
(hexaco_other) recorded the same situation as NO_ROUTE. Left as written rather than rewriting an agent's own
evidence string. Worth a linter tweak: a no-CSV table deserves its own status rather than borrowing one.

**Other findings worth a look.** dinic_2025_shortdarktriad: the paper's Table 3 and the deposited .sav variable
labels disagree on the wording at 4 of 27 items (the .sav quotes statements that are not SD3 items at all);
Table 3 was shipped and the labels treated as the erroneous side. dejesus_2017_sf36: the questionnaire prints
1=Sim/2=Não but the deposited data stores 0/1 — fixed against the data, disclosed. dejesus_2017_lequesne: the
study's own English annex is not a literal translation of its own Portuguese annex in three places.

**Quota.** No full-table export except one deliberate small fetch (hexaco_self, 41,664 rows); every other agent
used irw_table_sets()/table_sets.R server-side aggregates.

Cap check: Step 0's cap is batch_027, so the cap is NOT reached — the next firing picks up batch_027.

### batch_026 triage — 9 of 9 staged, 0 held — 2026-09-04

Triaged unattended, at Ben's instruction to keep the queue moving while he was away.

**All four gates re-run live rather than read off the round's report**, per BATCH_PROCESS
step 1, and they reproduce it: `normalize_nulls` 0 of 9 files would change (the round had
already normalized 3); `audit_batch` **9/9 PASS, zero WARN** against current live data;
`verify_batch` 6 PASS + 3 MISSING(exempt, `data_labels`); `lint_verification` 0 ERROR.
The blank-`option_text` percentages the audit reports — 4.8% dejesus_2017_lequesne, 66.7%
derubeis_2017_arsq, 60% dinic_2025_shortdarktriad, 100% direkvand_2022_mjsi — are each
explained by a `notes.csv` entry and are by design.

**Three of the round's substantive claims were re-checked independently, not read.**

- *HEXACO non-commercial clause — CONFIRMED a third time.* Re-fetched
  hexaco.org/hexaco-inventory independently of both the agent and the orchestrator. The
  clause is verbatim as quoted ("free of charge, but only for the purpose of non-profit
  academic research"), and the 200-item form is contact-gated. All three
  `de_vries_2022_hexaco_*` blocks stand. This was worth a third look because a wrong
  `blocked` is permanent — it removes the table from the queue for good.
- *deilkas Q34/Q59 — CONFIRMED on the shipped file.* The written CSV's `item_text` for
  Q34 and Q59 is byte-identical, and that pair is the **only** duplicated wording among the
  62 items. Q60 is the routine-care twin, as the corrected public note says.
- *dinic reverse-coded anchors — CONFIRMED on the shipped file.* sd3_11/15/17/20/25 ship
  resp 1 = 'Agree strongly', and the other 22 items ship resp 1 = 'Disagree strongly'.

**Two changes made at triage.**

1. `verify_direkvand_2022_mjsi.R` header corrected. It named **two** of the published
   subscale alphas as unreproducible; in fact **four** of five are (professional 0.85 vs
   0.580, responsibility 0.96 vs 0.161, physical-mental 0.98 vs 0.354, social 0.88 vs
   0.464), and the verdict silently rested on communications, the whole tool, and the
   item-block correlations. The script's PASS is still right and the status is still
   PARTIAL — the dimension assignment is what those three support — but the comment
   overstated how much of the stated test was met. The residual is a source-side problem,
   as the round said: alpha 0.96 on a 2-item block implies inter-item r near 0.92 against
   the ~0.09 the deposited data give.
2. `de_vries_2022_hexaco_meta` and `_self` moved `NOT_NEEDED` → `NO_ROUTE` in both
   `verification_merged.csv` and `mapping_verification.csv`. All three blocked HEXACO rows
   describe the same situation and the third sibling (`_other`) already read `NO_ROUTE`;
   `NOT_NEEDED` is what `lint_verification.R` tests as the `data_labels` exemption, so those
   two rows were the batch's only WARNs and both were false. Evidence strings untouched.
   Batch lint is now 0 ERROR / 0 WARN. The round's own better suggestion — give a no-CSV
   table its own status instead of borrowing one — is left to the standard; the same false
   WARN sits on `DART_Brysbaert_2020_1` and `_3_4_5` from an earlier round, so it recurs.
   Corpus-wide lint is 315 rows, 0 ERROR, 35 WARN, all pre-existing.

**Staged: all 9.** `itemtables/clean/` now holds exactly those 9 `__items.csv` and nothing
else. **Held: none** — no table's fate depends on an open decision, since the three tables
that did (the HEXACO family) were blocked at extraction rather than shipped.

**Issues page: drafted and rewritten, deliberately NOT applied.** 8 entries for the 9 shipped
tables, in `fixes/itemtext_issues_draft_batch026.md`, rewritten from each table's full `note`
rather than pasted from `draft_issues_qmd.R`. `decamp_2022_online_discussion` earns none and
that is correct — `data_labels`, no `notes.csv` entry, nothing to disclose. They are held
because the page's own rule is that a table earns an entry once it ships and batch_026 is 0 of
12 stamped `uploaded`, and because the local `irw_site` checkout is on branch `agent-brief`.
The rewrite mattered most for `derubeis_2017_arsq`: the drafter's version, templated from
`public_note`, never mentions that the English in the `_translated` columns was generated by
this project — which is the single fact check_provenance flags that table for.

**Found while drafting: the page is two batches behind.** `batch_024` (12 of 12 stamped
`uploaded`) and `batch_025` (8 of 12) have shipped and have **no** entries on
`itemtext_issues.qmd` — the last application was `1491d4c`, batches 022 and 023. Verified by
table name against the live file. 024, 025 and 026 should be drafted in one pass.

**Not decided here, left for Ben.** `dinic_2025_shortdarktriad` omits `language` and the
`_translated` columns because it pools 14 samples in 12 languages, following the
`ecps_sahm_2024_*` precedent (irw#1831). That is a consistent, documented choice, but it
contradicts `itemtext_standard.md`'s own instruction not to blank `language`, and the other
precedent — `campos_2023_*`, two languages — writes a semicolon-joined `Finnish; Portuguese`
instead. The standard does not cover a pooled multi-language table; one of the two precedents
should win. Not changed here, because picking a value for 12 languages is a policy call.

### batch_026 — uploaded 2026-09-04

Ben ran the upload and reported 9 of 9 uploaded and row-count verified. Confirmed
independently before stamping, because the read token is blind to drafts and a green
upload is not a visible one: `red_up.drafts --dataset irw_text --verbose` lists all nine
`__items` tables as **added** to the `irw_text` draft.

Stamped `uploaded=2026-09-04` on the nine in `itemtables/batch_026/provenance.csv` and in
`mapping_verification.csv` — 9 rows changed in each, git confirms exactly 9 lines touched
per file, and an audit re-reading both from disk agrees: 12 rows each, 9 stamped, and the 3
unstamped are exactly the blocked `de_vries_2022_hexaco_*` tables. Corpus-wide the tracker
now reads 276 of 315 stamped. `verification_merged.csv` is left unstamped, as in every prior
batch. Fields were addressed by header name, and a row counts as stamped only if it holds a
real date — the two rules that have each already broken a stamping pass.

Removed the nine uploaded `__items.csv` from the batch folder and from `itemtables/clean/`,
**by explicit table name rather than a directory glob** (irw#1956: a glob deletes files that
were never uploaded). Every sidecar stays, including the three `verify_de_vries_2022_hexaco_*.R`
scripts for the blocked tables, which record what a future attempt would need.

Still owed on this batch: the issues-page entries, drafted and rewritten in
`fixes/itemtext_issues_draft_batch026.md`, now unblocked by the upload. They should go up
together with batches 024 and 025, which shipped earlier today and have no entries at all.

---

## batch_027 — 2026-09-04 (CAP REACHED)

**12 tables claimed. Yield 10 written / 2 blocked / 0 failed (83%).** Circuit breaker not
tripped: it counts `failed`, and there were none. Both blocks are determinate rights verdicts
with retry test NO. No rate limit or spend cap was hit, so these counts mean what they say.

Tables: `di_riso_2025_mask_emotion`, `DMCT_Addis_2020_PSIQ`, `dominguez_2018_jcs`,
`donati_2021_cfq7`, `dong_2025_teacher_leadership`, `dopmeijer_2022_loneliness`,
`dou2025_area`, `doustmohammadian_2017_fnlit`, `dpt_noncog__emotional_intelligence`,
`dpt_noncog__interpersonal_reactivity` (written); `dominguez_2018_uwes`, `dpt_noncog__grit`
(blocked).

**Gates.** `normalize_nulls.R` fixed 2 of 10 files. `audit_batch.R` 8 PASS / 2 WARN, both WARNs
explained in `notes.csv` per Step 5c. `verify_batch.R` 7 PASS + 3 MISSING(exempt) — no FAIL and
no missing VERDICT. `lint_verification.R` **0 ERROR**, 3 WARN. `irw-validate` clean on 9 of 10;
the tenth is a `name_charset` WARN on `DMCT_Addis_2020_PSIQ`, a property of the existing IRW
table name, not of this extraction. `check_provenance.R` clean on vocabulary.

The three lint WARNs ("VERIFIED but its evidence hedges") were reviewed and left as VERIFIED:
in each the hedge is about what the route does *not* cover — the option anchors, or the words of
a translation — not about item separation, and each route does distinguish every item from every
other item by cell-for-cell response-frequency identity with mutually distinct profiles.

**Step 5b — three agent findings re-checked by the orchestrator against the live data. All three
confirmed; one needed a correction.**

1. **`donati_2021_cfq7`: `cov_population` is inverted.** Confirmed. The group labelled `clinical`
   holds 258 distinct ids and `non_clinical` holds 107, against the paper's 258 non-clinical /
   105 clinical — and the "clinical" group scores *lower* on cognitive fusion at all 7 items
   (CFQ2 3.0 vs 4.4), which is backwards. `data/donati_2021_cfq7.py` maps `Population 1.0 ->
   clinical, 2.0 -> non_clinical` the wrong way round. Needs a script fix and a re-upload of the
   response table; the item-text join is unaffected. **Worth its own issue.** The agent said the
   second group was n=107 against the paper's 105 — that 2-person discrepancy is real and
   reproduces, and should be looked at alongside the fix.
2. **`dominguez_2018_jcs`: `item_17` is not an item.** Confirmed. On the live table `item_17`
   equals `FLOOR(mean(item_18..item_21))` for **200 of 202** ids, r = 0.93, mean |diff| = 0.35.
   The S1 column headed "Item 17" is the block Subtotal `=AVERAGE(Z:AD)`. It ships with blank
   `item_text`/`option_text` rather than a false wording — which is exactly the audit WARN.
   **Recommend dropping `item_17` from the response table.**
3. **`doustmohammadian_2017_fnlit`: the 16 option-less items.** Confirmed as source coverage, not
   a defect. The 16 items with no `option_text` are *exactly* the 16 with no
   `item_text_translated` (16/16 overlap) — the validation-form items dropped before publication,
   which appear in neither questionnaire PDF, so their anchors were never published anywhere.

Also verified: the `DMCT_Addis_2020_*` naming problem is real — `table_context.R` gives
Reference = **Suggate, S.P. (2024)**, doi 10.3758/s13428-024-02496-z, and there is no "Addis 2020"
anywhere in the record. Affects all three siblings (`_PSIQ`, `_MCT`, `_SUIS`). Renaming a live
table is a human call.

**Rights — the dominant theme of this round, and it cuts both ways in the same paper.** Both
blocks are NC/redistribution verdicts where the *text was in hand* and the *mapping was already
proven*, so an unblock is cheap if the rule is read differently:

- `dominguez_2018_uwes` — the Spanish UWES-17 exists only in Schaufeli & Bakker's own manual,
  which carries the NC clause (irw#1891). The CC BY deposit publishes zero wording, so the ECR-R
  source-licence carve-out has nothing to attach to.
- `dpt_noncog__grit` — Grit-S. angeladuckworth.com/measures carries an NC clause **and** an
  explicit "cannot be published or used for … wide public distribution" bar, which under the
  2026-09-04 DSES ruling overrides the CC0 deposit that does print the items.

Against which `dominguez_2018_jcs`, from the *same paper* as the blocked UWES table, **shipped**
with `wording_rights=NC`: its wording came from a CC BY 4.0 article rather than from Bakker's
restricted download, which is the ECR-R shape. Likewise `dpt_noncog__interpersonal_reactivity`
shipped with `wording_rights=NC` (Davis's IRI permissions page has an NC clause but no
redistribution bar and no fee). The line that decided all four is *whether the only source of the
administered wording is itself restricted* — not whether the instrument is NC.

**Three escalations for Ben, none actioned here:**
- **Two already-uploaded tables have never been audited against irw#1891.** `algner2022_uwes`
  (batch_003) took its wording from the German UWES-9 PDF on wilmarschaufeli.nl — the same
  NC-clause source, so it likely does *not* survive. `baka2023_uwes` (batch_007) took Polish
  wording from the study's own CC BY figshare `.sav` labels — ECR-R shape, likely *does*.
- The Grit ruling is **instrument-level**, so the pending `grit_BrummerHoffman_2021` is blocked by
  the same clause, as is any future Grit-S/Grit-O table.
- `dominguez_2018_mbi`, from the same paper again, is MBI-HSS — Mind Garden fee-licensed, a strong
  candidate for the TAS-20 fee rule.

**Two availability-audit verdicts are now wrong** (`availability_audit_full.csv`, checked on
disk, not actioned): `dpt_noncog__grit` is recorded AVAILABLE on the reasoning that Grit-S is a
"freely published public-domain instrument" — that verdict predates the rights rules. And
`di_riso_2025_contact_behavior` is recorded UNAVAILABLE on the reasoning that its 3 items are
"not reproduced in text, tables, or the data-only supplement" — but the `di_riso_2025_mask_emotion`
agent, working the same paper, reports all three named verbatim in the same Table 2 image, with
means 3.27/3.77/4.00. That table is probably extractable and the audit row should be corrected.

**Owed at upload:** `dou2025_area` ships IRW-generated English (`machine_translation`) and needs a
public issues-page line. `check_provenance.R` flags it, correctly, as the only table in that state
besides `derubeis_2017_arsq`, which predates this round. This is due at upload, not now.

**Minor.** Di Riso et al. (2025)'s Supporting Information cites three deposit DOIs
(`10.5061/dryad.fbg79cp3g`, `10.5281/zenodo.14056914`, `10.5281/zenodo.14056916`) that all fail to
resolve; the PLOS `.s005` ZIP still carries the data, which is what IRW used, so nothing is lost.
No Step 3b instrument mismatch was found on any of the 12 tables.

**Cap — the prompt and the repo disagree, and the repo is newer.** Step 0 of the round prompt this
round ran under names `batch_027` as the stop condition, so by the prompt the cap is now reached.
But `e51f1ef itemtext: raise the round cap to batch_030 (#1709)` is on this branch, so
`run_round.sh` will start `batch_028` on the next hand-launch and be right to. Nothing to
self-cancel either way — there is no scheduler — but the next round's prompt should carry
`batch_030` in Step 0, or it will stand down for a cap that no longer applies. The queue holds
1,061 pending rows.

**Housekeeping: a concurrent session committed this round's in-flight files.** `2e30c03 itemtext:
batch_026 uploaded — stamp, clear, log` swept partially-written `batch_027` sidecars and
`__items.csv` files into a batch_026 commit — the known whole-tree staging behaviour of parallel
sessions on this repo. No content was lost (the round-close commit supersedes it), but batch_027's
history is split across two commits and `git log -- itemtables/batch_027` names the wrong one
first.

### batch_027 triage — 10 of 10 staged, 0 held — 2026-09-04

Triaged unattended, in parallel with the batch_028 round.

**Gates re-run live.** `audit_batch` 8 PASS / 2 WARN, `verify_batch` 7 PASS + 3
MISSING(exempt, `data_labels`), `lint_verification` 0 ERROR / 3 WARN. Both audit WARNs
were already explained by the round's notes: `dominguez_2018_jcs`'s blank rows are the
`item_17` Subtotal column, and `doustmohammadian_2017_fnlit`'s 16 option-less items are
exactly its 16 untranslated ones.

**A transient gate ERROR that is not a defect.** The re-audit returned
`[ERROR] di_riso_2025_mask_emotion: could not read live data: An error occurred while
querying IRW: missing value where TRUE/FALSE needed`, where the round's own audit had it
PASS. It does **not** reproduce — audited alone immediately afterwards it PASSes. Recorded
in `notes.csv` because the message reads like an R bug in the gate rather than a network
blip, and the next person to see it should not go hunting for a defect that is not there.

**Three lint WARNs adjudicated, all kept VERIFIED.** `dopmeijer_2022_loneliness`,
`doustmohammadian_2017_fnlit` and `dpt_noncog__interpersonal_reactivity` are each flagged
"VERIFIED but its evidence hedges (does not establish)". The hedge is real but concerns
something Step 5b does not claim: in all three the evidence says the numeric route pins the
code-to-item **mapping** completely and does not establish the **words**, which is the
translation question. The routes themselves are decisive — 0 of 34,551 observations
discrepant with the reversed reading off by 41,586; all 49 published alpha-if-item-deleted
values reproduced to 0.0005; 74 of 74 item×resp cells matching with mutually distinct
frequency profiles. Same false positive as `CPDMMC_Kunnari_2020_HCD` in batch_024: the
linter keyword-matches "does not establish" without regard to what the sentence is about.
That is now four instances, so the linter's hedge test is worth narrowing.

**Staged: all 10. Held: none.** `dominguez_2018_jcs` was the one candidate for a hold — its
`item_17` is not an item but the block Subtotal column, equal to `FLOOR(mean(item_18..21))`
for 200 of 202 ids — and it is staged anyway. The item table is correct with respect to the
live response table as it stands today; holding it would park nine good tables' worth of
schedule behind one row whose fix is a response-table change. If that change lands, the item
table is re-uploaded.

**File format, per batch, undocumented.** batch_027's CSVs are MINIMAL-quoted with **LF**
endings; batch_026's are MINIMAL with **CRLF**. Neither BATCH_PROCESS's claim (CRLF, every
field quoted) nor any single convention holds across batches. Round-trip the file and check
byte-identity before writing, every time.

**Two response-data defects the round found, filed rather than fixed here** —
`donati_2021_cfq7`'s inverted `cov_population` and `dominguez_2018_jcs`'s `item_17`.
Both need a change to a processing script and a response-table re-upload, which is not
something a triage pass should do.

---

## batch_028 — 2026-09-04

**12 tables claimed. Written 10 / blocked 2 / failed 0.** Yield 10/12 = 83.3%. Circuit
breaker not tripped: 0% failed (the breaker counts `failed`, not `blocked`).

`dpt_noncog__intolerance_of_uncertainty`, `duboz_2021_pss10`, `dudasova_2021_cpc12`,
`dudasova_2021_cpc12_study3`, `dudasova_2021_gratitude`, `dudasova_2021_swls`,
`dulger2024_wordcompletion`, `dussel_2022_pcl17`,
`dvivdtws_ppmial_marcatto_2023_cwb`, `dvivdtws_ppmial_marcatto_2023_dtw` written.
`duboz_2021_swls` and `dudasova_2021_engagement` blocked — both determinate (retry test NO),
both with rows in `itemtables/pending_index_notes.csv`.

**All six gates clean.** `normalize_nulls.R` fixed 1 of 10 files. `audit_batch.R`: 10 PASS,
**no WARNs at all**, so Step 5c had nothing to explain. `verify_batch.R`: PASS=10, no
FAIL and no missing VERDICT. `lint_verification.R`: 12 rows, **0 ERROR**, 2 WARN.
`irw-validate`: all 10 ok. `check_provenance.R`: no vocabulary errors.

**No NOT_NEEDED rows were needed** — both `data_labels` tables wrote real verification rows
of their own, so all 12 tables already had exactly one row each. The batch-020/021 lint
false alarm did not recur.

### The thing that needs Ben: two agents in ONE batch reached OPPOSITE rights verdicts on the SWLS

`duboz_2021_swls` was **blocked** on the SWLS's licence; `dudasova_2021_swls` **shipped**
SWLS wording. Same instrument, same rights holder, same batch. They read different pages of
that rights holder, and the orchestrator re-fetched both:

- `eddiener.com/scales` (maintained successor site, © 2025) — "These scales are copyrighted
  by Ed Diener and his co-authors." / "The use of these scales is permitted for
  non-commercial purposes only." **Confirmed verbatim.** This is the irw#1891 NC clause.
- `labs.psychology.illinois.edu/~ediener/scales.html` — "The scale is in the public domain
  and therefore you are free to use it without permission or charge by all professionals
  (researchers and practitioners) as long as you give credit to the authors of the scale."

**Correction to both agents' accounts of the older page**, and it matters: each described it
as saying the scale is *copyrighted but free to use*. It does not. It says **public domain**,
and on that page the word "copyrighted" is scoped to SPANE and the Flourishing Scale, **not**
the SWLS. So this is not "one page has an NC clause and the other is silent" — it is a direct
contradiction on the SWLS specifically, and the older statement is a stronger basis for
shipping than either agent claimed.

Scope of the ruling: ~14 SWLS tables sit in the queue; `altahla_2024_swls` (batch_005) and
`campos_2023_swls` (batch_017) have already shipped; the same eddiener.com clause also covers
the Flourishing Scale and SPANE. **Do not upload `dudasova_2021_swls` while
`duboz_2021_swls` stands blocked** — ship both or block both.

### Duplicate live tables — confirmed independently, decide before uploading

`dvivdtws_ppmial_marcatto_2023_cwb` and `dvivdtws_ppmial_marcatto_2023_dtw` are the **same
data under two names**. The agent flagged it; the orchestrator confirmed it without taking
the agent's word: both report `rows=12,166`, the identical 22-item set `dtw1..dtw22` and the
identical resp set 1–5, and `item_stats.R` returns byte-identical per-item blocks on every
item (dtw1 n=552 M=2.86 SD=1.09 floor 11.4% ceil 6.2%; dtw11 n=551 1.44/0.79 69.3/0.7;
dtw16 n=553 1.26/0.63 81.7/0.5; dtw21 n=553 1.14/0.55 92.0/0.4).

The `_cwb` one is the **misnamed** member: its dictionary Description says "Counterproductive
Work Behavior items(CWB)" but the data are the 22-item Dark Tetrad at Work scale — the OSF
deposit `osf.io/8mj73` keeps the blocks separate and CWB has 45 items, Italian half only.
Both CSVs are staged; **upload at most one.** If `_cwb` is deleted as a duplicate, drop its
CSV and keep `_dtw`.

### Step 5b orchestrator re-checks — three agent findings verified, one corrected

- **`dudasova_2021_gratitude`, both data findings reproduce exactly.** The authors' own
  `Grat` total sums `Grat6` un-reversed: corr(total, raw sum) = **1.000000**, means identical
  (28.163 vs 28.163); reversing `Grat6` gives corr 0.8956 / mean 31.702. Polarity evidence
  also reproduces (mean off-diagonal r: +0.382 / +0.386 / +0.334 / +0.327 / +0.259 /
  **−0.451**; r(Grat1,Grat2) = 0.808). Source-file defect, harmless to the IRW table, which
  ships per-item responses and not the total.
- **`dpt_noncog__intolerance_of_uncertainty`'s public_note holds against live data.** The
  live item set really does contain both `iu_21a` and `iu_21b`, carrying the deposit's single
  `IU_Scale_21` label across two distinct items.
- **The SWLS rights account was corrected** (above) — an agent finding taken as a lead and
  changed by the check, which is exactly what Step 5b is for.
- Agent prediction that did **not** come true: `dudasova_2021_gratitude` expected
  `irw-validate` to flag `resp_ambiguous` for its deliberate two-direction `option_text`.
  It did not. Per-item direction differences are legitimately not flagged, as with
  `aip_vangsness_2019`. No defect.

### Both lint WARNs adjudicated — kept VERIFIED, and the same false positive as batch_027

`dpt_noncog__intolerance_of_uncertainty` and `dulger2024_wordcompletion` are flagged
"VERIFIED but its evidence hedges". In both the hedge is about an axis Step 5b does not
claim: the IUS table's hedge is about the 2–4 anchor labels, not the item axis (route 9
matched all 16 response-count vectors cell-for-cell, all 16 mutually distinct); the
word-completion table's hedge is about scenario wording that is **not shipped**, plus
`acc_d_nt` vs `ac_id_nt`, a pair carrying the *same* `correct_response` so no swap is
possible (all 60 claimed target words are the unique maximum, every other word scoring
exactly 0.000). This is now the **fifth and sixth** instance of the linter keyword-matching
"does not establish" without regard to what the sentence is about — batch_024 had one,
batch_027 had three. The hedge test is overdue for narrowing.

### Other findings worth carrying forward

- **`dudasova_2021_cpc12_study3` is misleadingly named.** `_study3` refers to the article's
  **S3 supporting-information file**, not the paper's Study 3. The data are the second German
  sample (N=202) from *Study 2*, on the original German CPC-12 — not Study 3's Czech CPC-12R,
  which swaps in three different resilience items. The dictionary Description is already
  correct; only the table name misleads.
- **`dudasova_2021_cpc12` nearly shipped a 9-of-12 permutation.** The paper's own appendix
  prints the *revised* CPC-12R, which re-orders the facets relative to the CPC-12 that Study 1
  actually administered. Transcribing the appendix in appendix order would have permuted 9 of
  12 items and every existing set-based gate would still have passed. Verified out by
  reproducing the paper's twelve distinct CFA loadings item by item.
- **`dudasova_2021_engagement`'s instrument identity is a dictionary conjecture.** The
  Description "Work engagement scale (UWES-9-style, 9 items)" is not a source claim — the
  paper never mentions engagement at all, and the team's other paper on this cohort describes
  the 17-item UWES. Worth a dictionary fix independent of the rights question.
- **`dulger2024_wordcompletion` pools two tasks, not one** (40 scenario-completion fragments
  + 20 memory-recognition fragments = the 60 live items), and 36 of its 60 target words are
  IRW-derived from the modal correct completion rather than stated by the authors — the
  `public_note` discloses this per the 2026-09-03 derived-answer-key ruling.
- **`duboz_2021_pss10` introduces `wording_rights=NC` for the PSS**, which the two live
  PSS-10 tables (`bakker_2020_pss10`, `beck_2021_pss10`, both uploaded 2026-08-18) do not
  carry. Backfilling that column on live tables is an upload-side decision, flagged not done.
- **Provenance header drift, again**: 10 of 12 agents wrote the 7-column header and the two
  `marcatto` agents wrote the 8-column one with `translation_source`. The merge normalised to
  8 columns, matching batch_027. The subagent prompt still specifies 7 — worth fixing there.
- **Issues-page debt is upload-side.** None of this batch's tables have an
  `itemtext_issues.qmd` line yet; `check_provenance.R` does not flag them because they are
  not uploaded. Five will need one at upload (`duboz_2021_pss10`, `dudasova_2021_swls`,
  `dudasova_2021_gratitude`, `dussel_2022_pcl17`, `dulger2024_wordcompletion`). Separately,
  its two standing complaints (`derubeis_2017_arsq`, `dou2025_area`) are pre-existing debt
  from earlier batches, untouched by this round.

**No systemic access issues.** No quota exhaustion, no rate limit, no killed agents; every
agent reported a determinate outcome and all 12 sidecar sets were written. Queue: 1,049
pending remain. Cap is batch_030 — **not reached**, two rounds left.

### batch_027 — uploaded 2026-09-04

Ben ran the upload and reported 10 of 10 uploaded and row-count verified, including
`dominguez_2018_jcs` (staged with its Subtotal `item_17`, see #1965). Confirmed before
stamping: `red_up.drafts --dataset irw_text --verbose` lists all ten as **added**.

Stamped `uploaded=2026-09-04` in `itemtables/batch_027/provenance.csv` and
`mapping_verification.csv` — 10 rows each, git confirms exactly 10 lines touched per file,
and an independent re-read agrees: 12 rows each, 10 stamped, the 2 unstamped being exactly
the blocked `dominguez_2018_uwes` and `dpt_noncog__grit`. Removed the ten uploaded
`__items.csv` from the batch folder and `clean/`, by name.

**`mapping_verification.csv` is now MIXED line endings and a `csv.writer` pass would have
silently reformatted the whole file.** It was uniformly CRLF when batch_026 was stamped a
few hours earlier; the batch_027 round left it at 12 CRLF lines and 328 LF, so no single
convention round-trips it any more. The stamp was therefore done as a byte-level edit — each
record starts at a line start and its first four fields (`table`, `batch`, `mapping_basis`,
`uploaded`) are simple, so the prefix is unambiguous — and the file came out 100 bytes
larger, exactly 10 × the date, with the CRLF/LF counts unchanged. `batch_027/provenance.csv`
does still round-trip (MINIMAL + LF) and was stamped the ordinary way.

Whoever writes to `mapping_verification.csv` next should check this first. The file is
rewritten by rounds, so its convention can change under you between one batch and the next.

### batch_028 triage — 8 of 10 staged, 2 held — 2026-09-04

**Gates re-run live.** `audit_batch` 10/10 PASS with no anomalies; `verify_batch` PASS=10
with no exempt rows, every table carrying its own verify script; `lint_verification` 0
ERROR / 2 WARN. Both WARNs are the translation-caveat false positive on the hedge check,
now diagnosed and filed as **irw#1966**: `(does not|do not|did not) (establish|settle|pin)`
matches without regard to its object, so an evidence string that correctly says a numeric
route cannot check a *translation* is read as hedging about the *mapping*. **31 of the
corpus's 40 WARNs are that one pattern.** Statuses left VERIFIED — the mapping evidence is
decisive in both (all 80 item×resp cells matched for the IUS table; `correct_response`
pinned per item for `dulger2024_wordcompletion`).

**Ben's SWLS ruling — the source you copied from governs, applied one level in.** Put to him
with both pages quoted; written up in `itemtext_standard.md` under "Two pages, two terms, one
rights holder". Wording from a study's own open deposit ships; wording from
`SWLS_English.doc` on the Illinois page ships, because that page distributes the document and
states no non-commercial restriction; wording from eddiener.com does not, because that page
states one. So `dudasova_2021_swls` **ships and is staged**, and `duboz_2021_swls`'s block is
**retryable, not determinate** — the same words are reachable under permitting terms.

**A correction to the round's own report, which mattered to the ruling.** The orchestrator
said both agents had misquoted the Illinois page and that it declares the SWLS *public
domain*. It does not — the phrase does not appear on that page at all, checked directly at
triage. The agents' quotes were accurate and the re-check was not. That is what took the case
out of the TIMSS 2003 precedent (one page stating a public-domain claim beside an NC clause,
where the restriction governs) and into the ECR-R source-licence rule.

**`duboz_2021_swls` is owed a queue flip, blocked → pending, and it has NOT been made yet.**
The batch_029 round is live and a round rewrites `queue_state.csv`; editing it concurrently
would either lose the change or corrupt the file. Do it once 029 finishes.

**Held: the marcatto duplicate pair.** `dvivdtws_ppmial_marcatto_2023_cwb` and `_dtw` hold the
same 12,166 rows, the same 22 items and byte-identical per-item statistics, and `_cwb` is the
misnamed one — its Description says Counterproductive Work Behavior while the data are the
Dark Tetrad at Work scale, whose real CWB block is a separate 45 items. Filed as **irw#1967**.
Per the #1653 ruling the item text is held and re-pointed at whichever table survives rather
than uploaded against a table that may be deleted. Both CSVs stay in the batch folder; neither
is in `clean/`; nothing needs re-extracting either way, since the two files differ only in the
`table` column.

**Staged: 8.** `clean/` holds `dpt_noncog__intolerance_of_uncertainty`, `duboz_2021_pss10`,
`dudasova_2021_cpc12`, `dudasova_2021_cpc12_study3`, `dudasova_2021_gratitude`,
`dudasova_2021_swls`, `dulger2024_wordcompletion`, `dussel_2022_pcl17`.

## batch_029 — 2026-09-04

12 tables claimed, one agent per table. **8 written / 4 blocked / 0 failed** — yield 66.7%.
Circuit breaker: **not tripped** (0% failed; all four no-CSV outcomes are determinate blocks,
retry test NO). No rate limit or spend cap was hit; every agent returned a real verdict.

**Written (8):** `dwyer_2019_clinton_cesd` (80 rows), `EEN_Lacey_2024_Children` (41),
`EEN_Lacey_2024_Parent` (77), `ellis_2016_calc_instrprac` (48), `ellis_2016_calc_instrqual` (48),
`emobank_buechel_2017` (30), `enkavi_2019_ant_flanker` (96), `enkavi_2019_navon` (24).

**Gates all clean.** `audit_batch.R` 8/8 PASS **with zero WARNs** (so Step 5c has nothing to
explain this round). `verify_batch.R` PASS=2, MISSING(exempt)=6. `lint_verification.R` 0 ERROR.
`irw-validate` 0 ERROR. `check_provenance.R` clean for this batch. All 12 tables have exactly one
tracker row in `mapping_verification.csv`; the 6 data_labels NOT_NEEDED rows were written into
**both** `verification_merged.csv` and the permanent tracker, so the lint came back with no
"ships a CSV but has no verification row" ERRORs.

### Orchestrator corrections (Step 5b)

1. **`EEN_Lacey_2024_Children` — language claim removed.** The extraction shipped
   `language=Nepali` on all 41 rows with the source's **English** Stata labels in `item_text` and
   every `*_translated` cell NA — i.e. IRW-supplied English sitting in the administered-wording
   slot. I re-checked the deposit, the IZA WP (dp17166) and the AEA PAP (AEARCTR-0007778)
   directly: **none states the administered language**, and the agent's own note conceded the
   inference. Dropped `language` and the four `*_translated` columns. This removes an assertion no
   source makes and matches the sibling `EEN_Lacey_2024_Parent` — worked from the same replication
   package by a different agent, which omitted the claim. Two agents on one study reaching
   opposite language decisions is the cluster-consistency check earning its keep.
   **Gap worth closing:** `check_provenance.R` did *not* flag this, because
   `text_source=translated_substitute` with `translation_source` empty is not counted as
   IRW-generated content.
2. **`enkavi_2019_dpx_axcpt`, `enkavi_2019_stopsignal`** — verification status `NOT_NEEDED`
   corrected to `NO_ROUTE` (only `data_labels` is exempt from Step 5b; these are `unknown`).
3. **`enkavi_2019_navon`** — lint WARN "VERIFIED but its evidence hedges" reviewed, status
   **kept VERIFIED**. The hedge is about the transcribed instructions and the resp 0/1 accuracy
   labels, neither of which is the item mapping; the route itself distinguishes every item from
   every other (12/12 distinct per-item n, reproduce exactly, max diff 0).

### Verified upstream finding — response data, not item text

The stopsignal agent reported that the shared processing script mislabels a covariate. **I
re-checked it against the raw deposit and it is correct.** `data/enkavi_2019_conflict_tasks.py:148`
maps `{"itemcov_delay": "condition"}`, but `condition` is stop-signal **frequency**, not delay:
in the raw `stop_signal.csv.gz` test stage, `condition=high` gives 62,640/156,600 stop trials
(40.0%) and `condition=low` gives 31,320/156,600 (20.0%), while `SS_delay` is a separate column
carrying 18 distinct values under **both** conditions. `itemcov_ss_frequency` would be correct.
This lives in the **shared** script for the whole `enkavi_2019_*` conflict family, so it affects
those response tables, not just this one. Worth its own GitHub issue.

### The blocked four — one decision, not four

`enkavi_2019_dpx_axcpt`, `enkavi_2019_gonogo`, `enkavi_2019_simon`, `enkavi_2019_stopsignal`.
Rights are **not** the issue (authors' explicit CC BY confirmation is in the processing script
header) and every source was read in full. The wording does not exist: `item` is a stimulus
condition and `resp` is trial accuracy, so neither join axis has text. Each has a
`pending_index_notes.csv` row recording what was recovered (instructions, colour bindings, correct
keys) so a later pass need not re-derive it.

**Note the cluster split, which needs ratifying:** `ant_flanker` and `navon` *shipped* from the
same battery, because their stimuli are letter/arrow displays the task's own source code writes
out in text (arrow notation; `<global>_of_<local>.png` naming) — a transcription of the source's
own representation. The four blocked tables have wordless stimuli (coloured boxes and squares,
abstract PNGs) where any `item_text` would be invented. That line is defensible, and both the
simon and gonogo agents flagged it independently, but it is **one policy call from Ben covering
the whole family**: are IRW-authored stimulus descriptions for cognitive-task conditions in scope?

Also surfaced: `availability_audit_full.csv` marks `enkavi_2019_simon` AVAILABLE because "the
stimulus/design is fully reconstructable from the well-known paradigm description" — that is
reconstruction from general knowledge, which `itemtext_standard.md` explicitly rules out.

### Other notes

- `irw-validate` WARN `name_charset` on both `EEN_Lacey_2024_*` tables (capitalised table name)
  is inherited from the live IRW table name; not fixable from the itemtext side.
- `check_provenance.R` reports `derubeis_2017_arsq` and `dou2025_area` as IRW-generated content
  with no issues-page entry. **Both are pre-existing, not from this batch** — still outstanding.
- Cap not reached (cap is batch_030); next round proceeds normally.

### batch_028 — uploaded 2026-09-04 (partially stamped; see the deferred half)

Ben ran the upload of the 8 staged tables and reported 8 of 8 uploaded and row-count
verified. Confirmed before stamping: `red_up.drafts --dataset irw_text --verbose` lists all
eight as **added**.

Stamped `uploaded=2026-09-04` in `itemtables/batch_028/provenance.csv` — 8 rows, and an
independent re-read agrees: 12 rows, 8 stamped, and the 4 unstamped are exactly the two
blocked tables (`duboz_2021_swls`, `dudasova_2021_engagement`) and the two held ones
(`dvivdtws_ppmial_marcatto_2023_cwb`, `_dtw`). Removed the eight uploaded `__items.csv` from
the batch folder and `clean/`; the two held CSVs correctly remain in the batch folder.

**Two writes are deliberately DEFERRED because the batch_029 round is still live**, and a
round rewrites both of these files — a concurrent edit either loses the change or corrupts
the file:

1. `mapping_verification.csv` — the 8 `uploaded=2026-09-04` stamps.
2. `queue_state.csv` — `duboz_2021_swls` from `blocked` to `pending`, per Ben's SWLS ruling.

Neither is optional and both are owed the moment 029 finishes. Note the failure mode if they
are forgotten: an unstamped row in `mapping_verification.csv` reads as "never uploaded", which
is what the stamp exists to distinguish from a table that went missing.

### batch_029 triage — 8 of 8 staged, 0 held — 2026-09-04

**Gates re-run live.** `audit_batch` 8/8 PASS with no anomalies; `verify_batch` PASS=2 + 6
MISSING(exempt, `data_labels`); `lint_verification` 0 ERROR / 1 WARN — `enkavi_2019_navon`,
the same translation-caveat false positive now filed as irw#1966, kept VERIFIED. Its mapping
evidence is decisive: all 12 per-item counts reproduce the live table exactly and are mutually
distinct, so no permutation of two item codes survives, and the raw `correct_response` key is
unanimous within each item and matches the shipped attended level.

**Verified the round's own pre-ship correction.** It dropped a `language=Nepali` claim from
`EEN_Lacey_2024_Children`, which had asserted Nepali on all 41 rows while putting the source's
English in the administered-wording slot, with no source stating the language. Checked at
triage: neither that table nor its Parent sibling now carries a `language` column or any
`_translated` columns. Correct — under the standard, `language` is a fact about the study, and
here nothing establishes it.

**Two findings filed rather than fixed.**

- **irw#1969** — `data/enkavi_2019_conflict_tasks.py:148` populates `itemcov_delay` from the
  deposit's `condition` column, which is the stop-signal *frequency* manipulation (40.0% stop
  trials under `high` against 20.0% under `low`), while `SS_delay` is a separate column with 18
  distinct values. The covariate is both misnamed and missing, and it is the shared script, so
  the whole `enkavi_2019_*` family is affected. No item text depends on it.
- **irw#1970** — the round noticed `check_provenance.R` did not catch the Nepali claim, because
  `translated_substitute` with an empty `translation_source` is not counted as IRW-generated
  content. Measured at triage: **58 tables carry `text_source=translated_substitute` and all 58
  have `translation_source` empty**, so the check has no signal for that shape at all. Most are
  probably fine; the defect is that nothing distinguishes a study's own English from English
  this project wrote, and the gate passes either way.

**A scope question for Ben, not a defect.** Four tables blocked — the wordless-stimulus tasks
from the Enkavi 2019 battery — while `ant_flanker` and `navon` shipped from the same battery,
because their stimuli are letter and arrow displays the task's own source code writes out in
text. The blocked four are coloured boxes and abstract PNGs, where any `item_text` would be
invented. Two agents drew that line independently and it is defensible, but the real question
is whether IRW-authored stimulus descriptions for cognitive-task conditions are in scope at
all, and that answer covers the whole `enkavi_2019_*` family at once. Everything recoverable —
instructions, colour bindings, correct keys — is banked in `pending_index_notes.csv`, so an
unblock is cheap if Ben rules them in.

**Staged: all 8.**

---

## batch_030 — 2026-09-04

**12 tables claimed · 10 written / 2 blocked / 0 failed · yield 83.3%.** Circuit breaker not
tripped (0% failed against a 30% threshold). Cap is `batch_034`; not reached.

Written: `duboz_2021_swls`, `enkavi_2019_stroop`, `environment_ltm`, `esiason_2024_aaqii`,
`esiason_2024_ace`, `esiason_2024_cfq`, `estevezlopez_2016_panas`, `evans_2023_vaccination_norms`,
`evans_2023_vaccine_hesitancy`, `evpromisi_stone_2021_cdiag`.

**Gates.** `audit_batch.R` 9 PASS / 1 WARN, `verify_batch.R` 10/10 PASS, `lint_verification.R`
0 ERROR / 5 WARN, `irw-validate` ok on all 10, `check_provenance.R` clean for this batch.

The audit's *first* run returned 2 ERRORs — `environment_ltm` and `evpromisi_stone_2021_cdiag`,
both "could not read live data: " with an empty message. Both re-ran clean immediately
afterwards: `irw_table_sets()` and the per-item `GROUP BY` both succeed for both tables when
issued on their own. Transient Redivis query failures under the load of twelve concurrent
agents, not content defects, and **not** the export quota. Worth knowing that this is the shape
that failure takes — an empty `conditionMessage`, arriving as a hard ERROR, indistinguishable at
a glance from a real gate failure. Classifying on the first run would have marked two clean
tables `failed`.

**The one audit WARN is task design, not a defect.** `enkavi_2019_stroop`, "row-count anomaly
... median=5384: blue_blue, green_green, red_red". Re-checked server-side: the 3 congruent
conditions have n=10768 each, the 6 incongruent n=5384 each — exactly 2× — so congruent trials
total 32,304 against incongruent 32,304, the standard 50/50 Stroop congruency split spread over
an unequal number of cells. All 9 items have exactly 523 distinct ids. Explained in `notes.csv`.

**The 5 lint WARNs were adjudicated, not waved through.** All five are "VERIFIED but its
evidence hedges". In every case the hedge is about *text fidelity* — a single-source stem, a
package descriptor standing in for a survey question — and not about mapping discrimination,
which is what VERIFIED means. Each route does separate every item from every other; the
reasoning is written into `notes.csv` per table so the next reviewer does not re-derive it. One
lint WARN *was* substantive and was fixed: `esiason_2024_vlq_importance` had recorded
`NOT_NEEDED` with `mapping_basis=unknown`, where only `data_labels` is exempt. Changed to
`NO_ROUTE`, matching what its identical sibling recorded, in both the batch file and the tracker.

### Both blocks are one rights question, and it is worth a single ruling

`esiason_2024_vlq_importance` and `esiason_2024_vlq_consistency` are the two halves of the
Valued Living Questionnaire. Two agents, working independently, reached the same block on the
same clause — the Wilson (2002) form footer, printed on both its pages: *"You may reproduce and
use this form at will for the purpose of treatment and research. You may not distribute it
without the express written consent of the author."* That is a quotable redistribution bar and
fires the 2026-09-04 no-redistribution ruling, which overrides the CC BY source deposit. The
deposit itself publishes no VLQ wording at all, so there is no second route.

**Retry test: NO for both** — determinate, every source was retrieved successfully. These do not
count toward the breaker. The class is larger than these two tables: the same footer governs any
future VLQ table, so this wants one decision rather than per-table calls. Ground truth is banked
in `pending_index_notes.csv` (codes are the source column names verbatim, one-to-one with VLQ
domains 1–10), so an unblock costs no rework.

### Three defects found in *other* people's artifacts — all re-verified by the orchestrator

Per Step 5b these were re-checked independently before being written down; all three confirmed,
and none of them affects the item text shipped this round.

- **`data/esiason_2024_nmosd.py` truncates the AAQ-II.** Line 83 passes `valid_range=(1,5)` for a
  1–7 instrument (siblings correctly use `(1,7)`). Verified against the PLOS supplements: S2
  contains 19 sixes and 18 sevens, S1 none; 389 non-missing raw responses minus those 37 equals
  the 352 rows now live. **9.5% of the data is silently dropped and the scale truncated.** Item
  text was consequently shipped for resp 1–5 only. Wants a script fix and a reupload.

- **`cov_group` is transposed across all seven `esiason_2024_*` tables** — the five here plus
  `_bai` and `_bdi`. The script maps S1→`patient`, S2→`caregiver`; three lines say the reverse.
  (1) The paper: *"Descriptive statistics for all psychological variables among caregivers are
  summarized in Table 3. See S1 Data."* (2) S1 has 21 rows, matching *"Twenty-one out of 22
  caregiver participants completed a demographics survey."* (3) BDI-II totals give S1≈6.3 against
  a published caregiver 7.2, and S2≈16.2 against a published patient 14 — the current assignment
  puts patients at 6.3 against a published 14. Two agents flagged it independently. No item text
  depends on it; it mislabels a covariate on seven live tables.

- **`biblio.csv` describes `evpromisi_stone_2021_cdiag` as "PROMIS fatigue".** It is the study's
  own 12-item chronic-diagnosis checklist (1=No never / 2=No but in the past / 3=Yes currently).
  Corroborated independently of the codebook: the live table has 3 response levels where PROMIS
  fatigue short forms are 5-point. The *deposit* is "Ecological Validity of PROMIS Instruments" —
  the PROMIS content sits in the sibling tables. Note also that `collection_members.csv` files
  this table under the `promis` collection via `rule:cname:promis`, a name-matching rule that is
  wrong for its content. Both want correcting.

One further finding was checked and **downgraded**: an agent reported two misprinted means in the
Evans 2023 article's Supplemental Table 2b. It is real and self-corroborating (the table's own
crude-difference row reads −0.08 = 3.50 − 3.58), but it is a defect in the *publication*, not a
text-vs-table mismatch, so it stays in the verification evidence and off the issues page.

**`duboz_2021_swls` reopened and shipped.** Blocked in batch_028; the SWLS ruling of 2026-09-04
settles it — wording from `SWLS_English.doc` on the Illinois page ships, the eddiener.com NC
clause does not reach it. Confirmed the agent sourced the Illinois page and never opened
eddiener.com. Its stale batch_028 `NO_ROUTE` row in `mapping_verification.csv` was **replaced**,
not duplicated, and its `pending_index_notes.csv` row is now `resolved` with the original block
note preserved inline.

**Export discipline held.** No round-wide full-table exports; ground truth came from
`irw_table_sets()` and server-side `GROUP BY`. Two deliberate `irw_fetch` calls were spent by
agents whose `verify_*.R` scripts must fetch their own data.

**Verification mix:** 5 VERIFIED, 4 PARTIAL, 1 VERIFIED via the data_labels exemption (run
anyway), 2 NO_ROUTE for the blocked pair. Every written table has exactly one tracker row.

### batch_030 triage — 10 of 10 staged, 0 held — 2026-09-04

**Gates re-run live and they reproduce the round.** `audit_batch` 9 PASS / 1 WARN;
`verify_batch` PASS=10 with no exempt rows; `lint_verification` 0 ERROR / 5 WARN.

The audit WARN is `enkavi_2019_stroop`'s row-count anomaly on the three congruent
conditions, and the round's explanation checks out exactly: 3 congruent cells at n=10,768
and 6 incongruent at n=5,384 give 32,304 trials on each side — the standard 50/50 Stroop
congruency split across an unequal number of cells — with all 9 items on 523 distinct ids.
Task design, not conflation.

All 5 lint WARNs are the text-fidelity false positive (irw#1966), each already adjudicated
per table by the round. **That check has now fired in five consecutive batches**, which is
the case for narrowing it, not for continuing to hand-wave it.

**`duboz_2021_swls` shipped.** The SWLS ruling worked end to end: blocked in batch_028 on the
eddiener.com clause, reopened to `pending` at triage, picked up by this round, and extracted
from the Illinois document under terms that permit shipping. The round replaced its stale
tracker row rather than duplicating it, and marked its index note `resolved` with the original
block text preserved inline.

**The round independently reproduced the transient-audit-failure shape logged under batch_027.**
Its first audit run returned 2 ERRORs (`environment_ltm`, `evpromisi_stone_2021_cdiag`) reading
`could not read live data:` with an *empty* message; both re-ran clean immediately. Two
independent sightings now, in different batches, under concurrent agents. Classifying on a
first run would have marked clean tables `failed` — always re-run before believing that error.

**Three defects filed, none of them item-text defects.**

- **irw#1971** — `data/esiason_2024_nmosd.py:83` passes `valid_range=(1,5)` for the 1–7 AAQ-II,
  dropping 37 of 389 raw responses (19 sixes, 18 sevens, 9.5%); the sibling `cfq` call one line
  down correctly uses `(1,7)`. Same script transposes `cov_group` across **all seven**
  `esiason_2024_*` tables — the paper's "twenty-one out of 22 caregiver participants" matches
  S1's 21 rows, and BDI-II totals give S1≈6.3 against a published caregiver 7.2 while S2≈16.2
  against a published patient 14.
- **irw#1972** — `evpromisi_stone_2021_cdiag` is not PROMIS fatigue but the study's own 12-item
  chronic-diagnosis checklist; corroborated independently of the codebook by the live table
  having 3 response levels where PROMIS fatigue short forms are 5-point. `collection_members.csv`
  also files it under `promis` on a name-matching rule that is wrong for its content.
- The two blocks are **one rights question**, not two: both VLQ halves rest on the same Wilson
  (2002) form footer, *"You may not distribute it without the express written consent of the
  author."* That is a quotable no-redistribution clause, so it blocks under the DSES ruling, and
  the same footer governs any future VLQ table. Ground truth is banked, so an unblock costs no
  rework if Ben reads it differently.

**`esiason_2024_aaqii` is staged deliberately despite irw#1971.** Its `option_text` stops at 5
because the live data does, and the item set and resp set must match exactly; its public note
names IRW's own script as the cause. When the script is fixed and the response table re-uploaded,
this item table needs re-uploading with the upper two anchors restored.

## batch_031 — 2026-09-04

12 tables claimed, 12 resolved. **written 6 / blocked 6 / failed 0.** Yield 50%.
Circuit breaker: NOT tripped (0% failed, threshold >30% failed; blocked does not count).
No rate limit or spend cap hit; all 12 agents returned reports.

**Written (done):** EWAS_Sanford_2024_Flourish, extremera_2016_ei, extremera_2016_sbq,
extremera_2016_shs, extremera_2016_swls, falih_2026_dass21.

**Blocked (all retry test NO — determinate):** evpromisi_stone_2021_{ddedanx, ddeddep,
ddpainin, global} (PROMIS redistribution bar), experimental_iq (image-only items),
face_memory_test (image-only face half + HEXACO NC clause on the only source publishing
the wording).

### The round's one real decision: PROMIS

Three agents independently blocked their evpromisi tables on the HealthMeasures Terms of
Use no-redistribution clause; a fourth (`_ddeddep`) shipped a CSV from the same CC0 deposit,
having weighed the same question and dismissed it on the precedent of the batch_022
`promis1wave1_*` uploads.

The orchestrator verified the clause directly rather than taking three concurring reports at
face value: the two agents' fetched PDFs are byte-identical (md5
`fe672ca0c092d6b324a8098ac049c7e3`), and the text carries both "shall not reproduce
HealthMeasures Instruments except as needed to conduct the authorized single use" and
"shall not distribute, publish, sell, license, or provide HealthMeasures products, by any
means whatsoever, to third parties". `itemtext_standard.md`'s 2026-09-04 ruling is general,
not instrument-specific: a quotable redistribution bar governs even where IRW's wording came
from an openly licensed deposit.

So `_ddeddep` was **withdrawn by the orchestrator**, not by its agent — its `__items.csv`
moved to `itemtext/quarantine/batch_031/` with a README, its provenance reset to
`unknown`/`unknown` with the override recorded, and the round's four PROMIS tables now
resolve consistently. The extraction was good work (route 9, 40/40 cells) and restores
unchanged if the ruling goes the other way.

**FOR BEN — one decision, not four.** Is PROMIS wording an exception to the 2026-09-04
redistribution rule? It reaches beyond this batch: the seven `promis1wave1_*` tables shipped
in batch_022 and stamped `uploaded=2026-09-04` carry PROMIS item-bank wording (including the
EDANX bank) with no rights analysis in their provenance, and the standard itself records that
sweep as outstanding — "a table shipped before 2026-09-04 under 'the source licence governs'
may not survive this rule". Either PROMIS is barred (withdraw those seven, keep these four
blocked) or it is an exception (restore `_ddeddep` from quarantine and requeue the other
three). `evpromisi_stone_2021_cdiag` (batch_030) is unaffected either way — investigators'
own comorbidity checklist, not PROMIS wording.

### Gates

- `normalize_nulls.R`: 0 of 6 normalized (agents already in convention).
- `audit_batch.R`: PASS 5, WARN 1, no FAIL.
- `verify_batch.R`: PASS 5, MISSING(exempt) 1 (EWAS is `data_labels`).
- `lint_verification.R`: 12 rows, **0 ERROR**, 2 WARN — both on the blocked PROMIS tables
  (`_ddeddep`, `_ddpainin`), flagging VERIFIED-with-a-hedge. The hedge is about the *wording*
  resting on a codebook document, not about the mapping axis the route verifies, and neither
  table ships anything, so the status was left alone. The NOT_NEEDED row for EWAS was written
  into BOTH `verification_merged.csv` and the permanent tracker, which is why the lint is clean.
- `irw-validate`: 5 ok, 1 WARN — `name_charset` on `EWAS_Sanford_2024_Flourish` (mixed-case
  LIVE table name; not an itemtext defect and not fixable here).
- `check_provenance.R`: no vocabulary errors. Three IRW-generated-content tables still owe a
  public issues-page line: `extremera_2016_shs` (this batch, owed at upload) plus the
  pre-existing `derubeis_2017_arsq` and `dou2025_area`.

### Step 5b — orchestrator re-checks of agent claims

- **PROMIS clause: CONFIRMED**, see above. Changed the round's outcome.
- **`extremera_2016_sbq` data defect: CONFIRMED exactly** against the source `.sav`. sbq3 =
  {0:2, 1:833, 2:79, 3:19, 4:17, 5:11}, so 2 of 961 responses carry a code outside the item's
  five printed options — this is the audit WARN, and it is a defect in the response data, not
  in the item text. Also confirmed: the deposit's `SuicideBehaviours_Scores` equals the raw
  four-item sum on 960/960 complete rows and reaches **19**, above the SBQ-R's published 3–18
  range; `resp` is the raw printed option index, not SBQ-R scoring. Worth a data-side issue.

### Other findings worth a human's eye

- **Flourishing Scale rights inconsistency.** `EWAS_Sanford_2024_Flourish` ships with
  `wording_rights=NC` (eddiener.com names the FS under a non-commercial clause);
  `conner_2017_flourishing` shipped the same instrument in batch_030 **without** the flag. One
  of the two is wrong. The flag is the safer state, so nothing was changed retroactively.
- **`extremera_2016_ei` — two rival published numberings.** The same authors publish the
  WLEIS-S interleaved (administration form) and blocked (Psicothema Table 1). Route 5 over
  1117 cases chose interleaved decisively (within/between r gap +0.125 and 33/48 top-3
  correlates in-subscale, vs +0.007 and 9/48 for blocked). Taking the paper table at face
  value would have mislabelled all 16 items. `translation_source=mixed` (authors' English
  glosses for stems, IRW's for the five intermediate anchors) — owes an issues-page line.
- **`evpromisi_stone_2021_ddpainin` metadata defect:** dictionary Description says "PROMIS
  Pain Intensity"; the items are PROMIS Pain **Interference**.
- **`face_memory_test` schema problem:** one 175-code space stacks two instruments with two
  different response scales (1–2 face recognition, 1–5 HEXACO agreement) in one `resp`
  column — the `resp_ambiguous` shape, on a live table.
- **Blocked rate is about the queue, not the pipeline.** The queue is worked in table order
  and this stretch served four tables from one PROMIS deposit plus two openpsychometrics
  image-based tests. Six determinate source/rights verdicts is correct behaviour, not
  breakage.

Provenance merged in the 8-column form (`translation_source` present); `extremera_2016_ei`
recorded as `mixed`. Sidecars deleted by exact filename, never by glob.

Cap is batch_034 — not reached, three rounds remain.

### batch_031 triage — 6 of 6 staged; the PROMIS question held for Ben — 2026-09-04

**Gates re-run live.** `audit_batch` 5 PASS / 1 WARN; `lint_verification` 0 ERROR / 2 WARN,
both on blocked PROMIS rows that shipped nothing and both the irw#1966 false positive. The
audit WARN reaches the round's own finding independently: `extremera_2016_sbq`'s `sbq3` carries
a live `resp=0` with no `option_text` row — a response code outside the item's own printed
options. With the deposit's own score reaching 19 against the SBQ-R's published 3–18 range,
that is a response-data defect, filed as **irw#1973**.

**The HealthMeasures clause verified a third time, because this ruling reaches the draft.**
Three agents blocked on it, a fourth shipped against it, and the orchestrator verified it and
withdrew the shipped file to quarantine. At triage the Terms of Use PDF was fetched
independently — **md5 `fe672ca0c092d6b324a8098ac049c7e3`, matching the agents' copies** — and
the text extracted rather than summarised:

> "User shall not reproduce HealthMeasures Instruments except as needed to conduct the
> authorized single use … User shall not distribute, publish, sell, license, or provide
> HealthMeasures products, by any means whatsoever, to third parties not involved with the
> authorized single use as stated above, without the prior written agreement of the Provider."
> — *Terms of Use, Approved Version 1.12-2017*, "Single Use, Reproducibility, and Distribution"

That is a quotable redistribution bar, which the DSES ruling already says governs even where
IRW's copy came from an openly licensed deposit — and the Stone deposit is CC0, exactly the
DSES shape. The same section reads "publicly available for use without licensing or royalty
fees for individual research", the free-but-restricted pattern of TIMSS and HEXACO.

**Scope, checked table by table.** Four blocked this round (`evpromisi_stone_2021_ddedanx`,
`_ddeddep`, `_ddpainin`, `_global`), with `_ddeddep` in `itemtext/quarantine/batch_031/` with
its extraction intact. Seven already in the `irw_text` **draft** and stamped `uploaded=2026-09-04`
from batch_022: `promis1wave1_{anger,anxiety,depression,fatigue,pain,physicalfunction,social}`,
carrying PROMIS bank wording from the CC0 Wave 1 codebook with no rights analysis recorded.
They are unreleased, so withdrawal is a deletion before release rather than a public withdrawal.
**`promis1wave1_cesd` and `promis1wave1_haq` are NOT affected** — their provenance places them
in the codebook's legacy-items tables rather than the PROMIS bank sections, so CES-D and HAQ
carry their own separate rights.

**The SWLS ruling propagated correctly.** `extremera_2016_swls` records that its wording came
from `SWLS_English.doc` on the Illinois page and that eddiener.com "was NOT opened as a source"
— exactly the record the ruling asks for, written by a round that had only the standard to go on.

**Flourishing Scale flag inconsistency, left as found.** `EWAS_Sanford_2024_Flourish` ships
`wording_rights=NC`; `conner_2017_flourishing` (batch_021, uploaded 2026-09-04) shipped the same
Diener instrument without it. Under the field's own definition — the instrument's rights holder
states an NC restriction even though IRW copied from an open source — **EWAS is right and conner
is the one missing a flag.** Not fixed here: it is a disclosure flag on an already-uploaded
table, it belongs to the outstanding rights re-audit (irw#1954), and irw#1955 has the column's
future open anyway.

**Staged: all 6 written.** `clean/` now holds 24 tables from batches 029, 030 and 031.

### batch_032 — ROUND KILLED, out of memory — 2026-09-04 21:10 → ~21:2x

**The queue is stopped and needs a human.** The batch_032 round was killed by the OS while
its 12 agents were running — the machine ran out of memory, not a rate limit and not an agent
failure. It left **12 rows `in_progress`**, which the runner's own guard treats as "a round is
running or died mid-round", so **every subsequent round will stand down until these rows are
reconciled**. Reconciling them is deliberately a human decision, per Step 0 and BATCH_PROCESS:
a dead round can leave half-written files, and this one did.

**Machine state.** Memory recovered on its own once the agents died — 19 GiB available at
inspection, no orphaned `run_round.sh` or agent processes. The spike was 12 concurrent agents
on top of Chrome, Slack and Dropbox. Nothing needs cleaning up at the OS level, but a round
fired while this desktop is loaded can evidently lose the race, which is a new failure mode
for this runner: previous kills were rate limits, which exit 0 and look like completion.
**This one exits non-zero and leaves the queue blocked, which is the safer failure.**

**Per-table inventory, so the reconciliation is a decision and not an investigation.**

| state | tables | what is on disk |
|---|---|---|
| complete-ish (2) | `fisher_2019_belonging`, `fisher_2019_structure` | `__items.csv` + provenance + notes + verification + `verify_*.R` |
| orphan CSV (2) | `falih_2026_mds16`, `fisher_2019_preparedness` | `__items.csv` and a `verify_*.R`, but **no provenance and no notes** |
| script only (1) | `FIVPEI_Perrig_2023_PENS` | a `verify_*.R` and nothing else |
| nothing written (7) | `fatima_2025_mslq`, `fredrickson_2015_mhcsf`, `frikha_2023_pe_acrs`, `frikha_2023_pe_ms`, `fukuda_2021_health_literacy`, `fukuda_2021_info_reliability`, `fukuda_2021_withholding_behavior` | nothing |

The seven that wrote nothing are clean to return to `pending`. The two complete-ish ones could
be closed out by hand rather than re-extracted. The two orphan CSVs are the ones that need a
judgement: an `__items.csv` with no provenance row is exactly what the tracker was built to
catch, and per BATCH_PROCESS orphaned CSVs are quarantined, not promoted.

**Nothing was reconciled here.** `queue_state.csv` is committed as the dead round left it, so
the record shows what actually happened rather than a tidied version of it.

### batches 029, 030 and 031 — uploaded 2026-09-05

Ben ran one upload of the 24 staged tables and reported 24 of 24 uploaded and row-count
verified. Confirmed before stamping: `red_up.drafts --dataset irw_text --verbose` lists all
24 as **added**.

**Note the date.** These stamp `uploaded=2026-09-05`, a day after the batches were extracted,
because the upload happened after midnight. That is correct and not a bookkeeping slip; anyone
reading provenance later should not expect the stamp to match the batch's own date.

Stamped 24 rows across `batch_029/provenance.csv` (8), `batch_030/provenance.csv` (10),
`batch_031/provenance.csv` (6) and `mapping_verification.csv` (24) — git confirms exactly 24
lines changed in each file, and an independent re-read agrees. The 12 rows left unstamped are
exactly the blocked tables, and they account for themselves:

- batch_029 — `enkavi_2019_{dpx_axcpt,gonogo,simon,stopsignal}`, the wordless-stimulus tasks
  awaiting Ben's scope call
- batch_030 — `esiason_2024_vlq_{consistency,importance}`, the Wilson (2002) no-redistribution
  footer
- batch_031 — the four `evpromisi_stone_2021_*` PROMIS tables awaiting Ben's ruling, plus
  `experimental_iq` and `face_memory_test`, image-only items

Removed the 24 uploaded `__items.csv` from their batch folders and from `clean/`, by name.
`clean/` is empty. The `dvivdtws_ppmial_marcatto_2023_{cwb,dtw}` pair stays held in batch_028
and the quarantined `evpromisi_stone_2021_ddeddep` stays in `itemtext/quarantine/batch_031/`.

`mapping_verification.csv` reads as uniform CRLF again (375 of 375 lines), where it was mixed
at the batch_028 stamp — a later round rewrote it. The byte-level stamp preserves whatever is
there, which is why it keeps working across the change. Check the convention every time.

**Corpus position after this upload:** 59 tables of item text uploaded across batches 026–031
in this session, all resident in the `irw_text` **draft** and none of it visible until the
version is released.

### batch_032 reconciled by hand — 4 done, 1 blocked, 7 requeued — 2026-09-05

Ben ruled: salvage the five tables that produced work, requeue the seven that produced none.
**The queue is unblocked — zero `in_progress` rows remain.**

**Nothing was re-extracted.** Every field in the three reconstructed provenance rows is read off
the verify scripts and the shipped CSVs that survived the kill; nothing was re-derived from the
sources, and no wording was touched.

**The verify scripts are what made the salvage bigger than the file inventory suggested.** Two
tables looked like orphaned CSVs and were not: each carries a full `verify_*.R` naming its source
and mapping basis. A third, `FIVPEI_Perrig_2023_PENS`, looked like an incomplete extraction and is
actually a *finished block* — its script records that the study's deposit publishes every
instrument it administered except the PENS, whose 21 items appear only as bracketed placeholders,
and that the 21 live IRW codes are byte-identical to the redacted `PENS_*` columns. Determinate,
so `blocked` rather than `failed`, and it does not count toward the circuit breaker.

**Gates run at reconciliation, not assumed.** `normalize_nulls` fixed 2 of the 4 files — the step
the round died before reaching. `audit_batch` passes all four on item and resp sets.
`verify_batch` **PASS=4**, each script re-run live rather than trusted:

- `fisher_2019_belonging`, `fisher_2019_structure` — VERIFIED, sidecars already complete
- `fisher_2019_preparedness` — VERIFIED on two independent discriminators: the source columns
  carry different non-missing counts (460 and 454) matching the live per-item n, and the paper's
  Fig 2 asymmetry reproduces, with perceived success carried by `prepared1` (0.311, p=0.00 against
  0.048, p=0.37) and feeling accepted by `prepared2` (0.2, p=0.001 against 0.1, p=0.105)
- `falih_2026_mds16` — PARTIAL. The Q1/Q16 music pair are mutual maxima, the published two-factor
  blocks separate, and Q15, the only positively-valenced item, has the highest mean of the sixteen
  — but nothing distinguishes the order of items *within* a block

**One gap the round left had to be closed rather than assumed.** `falih_2026_mds16` takes its
wording from the instrument's own distribution PDF, which is exactly where a fee or NC clause
would sit, and the round was killed before recording any rights check. The PDF was fetched at
reconciliation and its full text extracted: **no copyright notice, no permission statement, no
licence, no restriction — zero matches for copyright/permission/licen/reproduc/distribut across
the document.** Silence is permission under the standard, so no rule fires and `wording_rights`
is omitted. Had that come back differently, the table would have been blocked instead of staged.

`lint_verification` reports 0 ERROR and 1 WARN, the irw#1966 false positive again, on a row the
round wrote itself. `check_provenance` reads 424 rows across 34 files with no vocabulary errors.

**Staged: the 4.** The 7 requeued rows are back to `pending` with their batch and timestamp
cleared, in the shape every other pending row has.

### batch_032 — uploaded 2026-09-05

Ben ran the upload of the four salvaged tables and reported 4 of 4 uploaded and row-count
verified; `red_up.drafts` lists all four as **added** before stamping. Stamped
`uploaded=2026-09-05` in `itemtables/batch_032/provenance.csv` and `mapping_verification.csv`,
4 rows each, exactly 4 lines changed per file. The single unstamped row is
`FIVPEI_Perrig_2023_PENS`, which is blocked and shipped nothing. Cleared the four CSVs from the
batch folder and `clean/`.

So the killed round cost seven tables' worth of extraction work, not twelve — and the five that
had produced anything all reached the warehouse or a determinate verdict.

### Issues page — datapages/irw#134 merged, and what it does and does not cover

Merged 2026-09-05: 29 entries for batches 024, 025 and 026, taking the page from 230 to 259, and
closing datapages/irw#132 (the three withdrawn tables, `rmet_higgins_2022_tas` included).

**Batches 027 through 032 are now the backlog** — 47 tables uploaded across them with no entries
on the page. They are all stamped, so they are all due; the drafter will template them from
`public_note`, and per the standing lesson the drafts must be rewritten from each table's full
`note` and its REVIEW THESE TOO section read, not pasted. Known callouts already waiting in that
set: `dpt_noncog__interpersonal_reactivity` carries `wording_rights=NC`, `esiason_2024_aaqii`
must disclose that IRW's own script truncated the 1-7 AAQ-II and dropped 9.5% of responses
(irw#1971), and `falih_2026_mds16` owes the within-block ordering caveat.

Note also that merging that PR did **not** rebuild the live page: `quarto_publish.yaml` in
`datapages/irw` is `workflow_dispatch` only.

### batch_033 — round stopped by hand, all 12 rows requeued — 2026-09-05

Ben stopped the round about four minutes in, then halved the agent count. Nothing was lost:
the round had claimed its 12 tables and dispatched, but `itemtables/batch_033/` held **zero
files** when it was stopped, so there was nothing to salvage and nothing to weigh. All 12 rows
went back to `pending` with batch and timestamp cleared, on Ben's go-ahead. Zero `in_progress`
rows remain and the queue is 1,009 pending, exactly where it stood before the round started.

The empty `batch_033/` directory was removed, so the next round is batch_033 rather than
batch_034 — which is also the cap, and would have left no room after it.

**Rounds are now 6 agents, not 12** (Ben, 2026-09-05, after two consecutive OOM kills). The
reason is written into Step 2 of `round_prompt_v1.md` beside the number, because the note that
was there justified twelve on the wrong constraint: "Twelve agents sits under the concurrency
cap, so this costs no wall clock." True of the API, irrelevant to the machine. **The binding
limit is RAM on the laptop the runner shares with a desktop session.** batch_032 died after
writing four of twelve tables and cost seven tables of extraction work; batch_033 died partway
through dispatch and cost nothing only because it was stopped before it wrote.

The round-size arithmetic stated as current fact was corrected in `BATCH_PROCESS.md` and
`run_round.sh` — both said "8 of the 12 tables in a round" and "~98 rounds" against a
1,165-table queue. At 6 a round and 1,009 pending it is **~168 rounds**, with per-round token
cost roughly halved and the round count roughly doubled. Historical accounts of batches 010,
018, 019 and 020 keep their original numbers, since those describe what happened.

### PROMIS ruled and withdrawn — 2026-09-05

Ben ruled three questions after batch_031. **(1)** The HealthMeasures redistribution clause bars
IRW from shipping verbatim PROMIS bank wording; the DSES rule applies unchanged, CC0 deposit or
not. **(2)** The bar reaches the study's own *modified* daily-diary adaptations too — a
derivative of a barred instrument stays barred, which avoids drawing a line about how much
rewriting is enough. **(3)** The seven already-shipped tables come out.

**A correction that changed the third answer, and had to be made before it was final.** Ben was
first told the seven `promis1wave1_*` tables were sitting in an unreleased draft, so removing
them would be a quiet deletion no user had seen. **That was wrong: `irw_text` v16.0 is released
and all seven were live in it.** So was almost everything else from this session — 51 of the 55
tables uploaded across batches 026–032 are in v16.0; only batch_032's four are draft-only.

The mistake was reading `red_up.drafts --verbose`'s `added` label as "added relative to the
released version". It is not that — it reports what the draft session added, and says nothing
about whether the table is public. **To tell whether something is live, compare `version="current"`
against `version="next"` directly.** That is now written into the standard.

**Done, in this order, safest first.** The issues-page edit (reversible) before the Redivis
deletion (not). Seven tables deleted from the `irw_text` draft — 746 tables before, 739 after,
and the removed set asserted equal to the seven targets, so nothing else moved.
`promis1wave1_cesd` and `promis1wave1_haq` were explicitly checked present before and after:
they are the CES-D and the HAQ, legacy instruments in the same deposit, and are **not** in scope.
Until the next release the withdrawn wording still exists in v16.0, so this is recoverable up to
that point and not after it.

`queue_state.csv`: the seven go `done` → `blocked`. `batch_022/provenance.csv`: the withdrawal is
recorded in each `note`, `public_note` is **cleared**, and the `uploaded` stamp is kept as
history so the record still shows these tables shipped.

**Withdrawal entries are no longer published at all.** Ben ruled the same day that the fact of a
withdrawal is not useful to a data user and tacitly advertises that IRW published material it
should not have. The seven existing entries — four WHOQOL, the DSES, and both TAS-20 tables —
were removed from `itemtext_issues.qmd`, taking it from 259 entries to 252, and no PROMIS entries
were written. Withdrawals now live in `provenance.csv` and this log only. Noted at the time, and
overruled: `rmet_higgins_2022_tas` is live and disappears at the next release, so with its entry
gone that disappearance is unexplained to anyone who used it.

### Picture-stimulus tasks ruled — 2026-09-05

Ben ruled the Enkavi scope question, and it turned out to be about a corpus inconsistency rather
than about four tables. IRW had already answered "what does a picture-stimulus task ship?" three
different ways: `twod_rotation_mather2023` shipped 304 picture items with `item_text` **blank by
design**; `enkavi_2019_{stroop,navon,ant_flanker}` and `dd_rotation` shipped **IRW-authored
stimulus descriptions**; `gilbert_meta_39` shipped **nothing**.

**The rule is now the blank one.** Ship the table, leave `item_text` empty, and let it carry what
the source really publishes — instructions, section structure, and the accuracy labels. The
stimulus identity already lives in the item code. Ask whether the source publishes wording, not
whether the task is verbal.

**The four live tables carrying authored descriptions stand.** They are correct, disclosed and in
v16.0, and re-uploading live tables to *remove* usable information is not worth it. So the corpus
is knowingly mixed, which is recorded in the standard along with the instruction not to cite them
as precedent.

**Reopened: `enkavi_2019_simon`, `_gonogo`, `_stopsignal`** — `blocked` → `pending`, index notes
marked `resolved` with the original block text preserved inline, the `duboz_2021_swls` pattern.
Their recovered material is already banked, so nothing needs re-deriving: for `gonogo` that
includes the binding that `style.css` fixes `#stim1=orange` and `#stim2=DodgerBlue`, with only the
go/no-go role counterbalanced. Whoever extracts `stopsignal` should know it has no shippable
`correct_response` — the shape-to-key mapping is shuffled per session.

**`enkavi_2019_dpx_axcpt` stays blocked, on a different ground.** Its probe labels are randomised
**per participant**, so `AX_probe3` is a different image for different people. The item code does
not denote a stable stimulus, and blank `item_text` would not fix that, because the problem is the
code rather than the text. That is a fact about the dataset, not a policy about pictures.

Queue after both rulings: **1,012 pending / 270 done / 53 blocked / 12 failed / 54 excluded.**

---

## batch_033 — 2026-09-05

**6 tables claimed, 6 shipped. Written 6 / blocked 0 / failed 0. Yield 100%.** Six agents (the
new post-2026-09-05 count, halved from twelve after the OOM kills); all six returned, none hit a
rate limit or spend cap.

`enkavi_2019_gonogo` (8 rows), `enkavi_2019_simon` (16), `enkavi_2019_stopsignal` (32),
`fatima_2025_mslq` (567), `fredrickson_2015_mhcsf` (84), `frikha_2023_pe_acrs` (60).
Every table returned RETRY TEST: NO — six determinate passes, nothing pending on access.

**The three reopened `enkavi_2019_*` tables all shipped**, which is what the 2026-09-05
picture-stimulus ruling was for. All three carry blank `item_text` by design over wordless
stimuli, following `twod_rotation_mather2023`; the ruling's own prediction held that
`stopsignal` has no shippable `correct_response` (per-session key shuffle) while `simon` does
(congruency fixes the arrow from the item code). None of them copied the live siblings'
IRW-authored stimulus descriptions.

**Gates.** `normalize_nulls.R` fixed 1 of 6 (`frikha`, 60 lines). `audit_batch.R` 3 PASS / 3 WARN,
0 FAIL. `verify_batch.R` **PASS=6**, no FAIL and no missing VERDICT. `lint_verification.R` 0 ERROR
(2 WARN, resolved below). `irw-validate` ok on all six. `check_provenance.R` reports nothing
against this batch — its output is the standing backlog (`translation_source` gaps on 61 older
tables; `dou2025_area`, `extremera_2016_shs` undisclosed), and note it could not enforce the
disclosure check because that checkout sits on `agent-brief-python-parity`, not main.

**Two VERIFIED claims downgraded to PARTIAL at round close** — the lint's hedging WARNs were
right in both cases, and the status now matches the evidence's own sentence.
`enkavi_2019_gonogo`: no route separates `go_stim1` from `go_stim2`. The agent's argument that
the swap is harmless (every shipped field is identical within each pair) is accepted and is why
this is not a defect — but it is an argument about consequences, not a route.
`fatima_2025_mslq`: the subscale-block route pins subscale membership, not within-subscale order,
across 73 items. Neither downgrade disputes the shipped mapping.

**Two agent findings re-checked independently (Step 5b), both CONFIRMED.** Both are response-table
/ metadata defects, not item-text problems, and both are written into `notes.csv`:

1. `enkavi_2019_stopsignal` — the item code's `high`/`low` component is stop-signal **frequency**,
   not delay, but `data/enkavi_2019_conflict_tasks.py:148` maps it to `itemcov_delay`. Re-checked
   against the task source: `experiment.js:670` draws `ss_freq = randomDraw(['high','low'])`,
   `:690` assigns it to `condition`, and `:678-683` make high = 40% stop trials
   (`['stop','stop','go','go','go']`) vs low = 20% (`['stop','go','go','go','go']`). The real
   delay is a separate staircase (`SSD`, init 250, ±50, stored in its own column at `:568`).
   `itemcov_ss_frequency` is the correct name. **Affects the sibling `enkavi_2019_*` tables too —
   worth its own issue.**
2. `frikha_2023_pe_acrs` — `metadata/biblio.csv:6454` describes it as "Perceived E-learning
   Acceptance and Course Rating Scale (PE-ACRS)". It is not an e-learning scale: the shipped
   wording is a physical-education basic-needs scale under the stem "When I am in PE...", with
   relatedness q1/4/7/10, competence q2/5/8/11, autonomy q3/6/9/12 — an allocation corroborated
   independently of the wording by the source workbook's own stored subscale sums, which
   `verify_batch.R` reproduced 308/308, 306/308, 308/308. The Dataverse title agrees ("motivation
   PNS"). Should read PE autonomy relatedness competence scale (PE-ARCS), Sulz, Temple & Gibbons
   (2016). The sibling `frikha_2023_pe_ms` (biblio:6462) is suspect on the same grounds but was
   **not** in this round and was **not** checked.

**Step 5c — both row-count-anomaly WARNs are properties of the response data, not defects.**
`gonogo`: per-item n 107415 / 104580 / 11620 / 11935, which sums to exactly the 235550 that
`irw_table_sets()` reports live and reproduces the audit's own median of 58257.5 — a 211995:23555
split, the standard 9:1 go/no-go ratio. `stopsignal`: the eight flagged `low_*` items are rare-vs-
common by the same frequency design just described; `irw_table_sets()` n_rows 403800 matches the
agent's rebuild exactly. Both checks used server-side aggregates — **no full export was taken
anywhere in this round.** The three blank-`item_text` WARNs are the ruling working as intended.

**Sidecar merge:** deleted by explicit name, not by glob — `verification_merged.csv` survived.
All six tables carried their own verification row, so no NOT_NEEDED rows were needed. The three
`enkavi_2019_*` tables had stale `batch_029` NO_ROUTE rows in `mapping_verification.csv` from when
they were blocked; those were **replaced**, not appended, so every table still has exactly one
tracker row (382 rows, no duplicates).

Queue after this round: **1,006 pending / 276 done / 53 blocked / 12 failed / 54 excluded.**
Circuit breaker not tripped (0% failed). Cap is `batch_034`; not reached, so the next round proceeds.
