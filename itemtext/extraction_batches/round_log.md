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
5. **Four `himmelstein-*` tables fall through the gap between both audits.**
   `status_report_20260814.md` Thread 2 flagged them as wrongly excluded (their item
   text is in a public GitHub repo cited by the dictionary itself), and they appear
   nowhere in `availability_audit_full.csv`. Needs a Shipley-copyright judgment call
   first for two of them.
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

## What needs a human, in priority order

1. **Paste issues-page callouts for batches 002-005.** `fixes/itemtext_issues_draft.md`
   regenerated 2026-08-17 from corrected provenance: 24 callouts, of which **20 are not yet
   on the live page** and 4 already are (skip `abdullah_2024_bsq_sevgen`, `addy_2021_sdq_ghana`,
   `aguirre_camacho_2021_champion`, `aguirre_camacho_2021_shai`). Apply the usual bar --
   concrete text-vs-table mismatches only, not gaps the source never published; the generator
   flags every `canonical_instrument` source, which sweeps in unremarkable cases.
2. **The `fixes/*.csv` corrected tables are still unuploaded** (confirmed with Ben
   2026-08-17, in his todo pile). Their issues-page notes are written and HELD in
   `fixes/itemtext_issues_suggestions.md` -- three of them replace existing live callouts
   with wording that is only true once the fix is live, so they must be pasted WHEN those
   tables upload, not before. `dumas_organisciak_2022` from that set was already added to
   the live page (it describes a paper-vs-data scale discrepancy, independent of the fixes).
3. **Two data-level defects, outside itemtext, in the underlying IRW tables:**
   - `alves_2017_hamd17` -- 9 out-of-range responses (items 6/14/16 are 0-2 HDRS items
     carrying stray 3s and 4s).
   - `altahla_2024_whoqol_bref` -- strict duplicate of `altahla_2024_whoqol` (all 4,914
     id/item/resp triples identical); should be one table per the collapse convention.
4. **Decide the 7 pilot tables still marked `pending`** in queue_state.csv (ali_2021_phq9,
   conner_2017_lot, consideration_future_consequences, cordova2019_clinical_edu_environment,
   cucchi_2018_pts, iwasa_2016_padua_inventory, preussmattsson_2022_ownership). They already
   have output in `itemtables/pilot/`; left as `pending` they will be re-extracted from
   scratch by batch_006.
5. **`ALSECYPIAMH_WU_2022_PHQ`** -- unverifiable 2-item mapping, paywalled source. Needs the
   paper or an author email, or should be dropped.
6. **`alomari_2025_student_questionnaire`** -- table name/dictionary misattribution (named
   "alomari", actual source Xie et al. 2026, DOI 10.1371/journal.pone.0340806). Dictionary
   problem, deliberately not on the public issues page.
7. **`alexander_2017_dsi`** -- its provenance note claims the DSI-R's ER(11)+EC(12) split, but
   content and data both give 10/13. One item is mislabelled in the note (not in the data).
8. **AUDIT THE PRE-EXISTING ISSUES-PAGE ENTRIES** (Ben's request, 2026-08-17). The 13 callouts
   that were live on https://itemresponsewarehouse.org/itemtext_issues.html BEFORE today's work
   have never been re-checked against current data, and today's sweep showed how easily such a
   claim goes stale or turns out to be imprecise. They are:
   singh_2025_identity_pba, paampsmartsud_saba_2023_ders, namprb_siwiak_2024_ssub,
   sv-maia2_randelovic_2021_erq, fivpei_perrig_2023_attdiff, oxfordcovid_xue_2024_at,
   socialstereotype_hughes_2025_judgement, gilbert_meta_51, gilbert_meta_42, gilbert_meta_38,
   gilbert_meta_35, florida_twins_friends, addy_2021_sdq_ghana.
   For each: does the stated mismatch still hold against the live IRW table and the current
   itemtext? Several are item-count claims ("paper has 28 items, IRW contains only 21") that are
   directly checkable with irw::irw_fetch, and three already have more precise replacement wording
   drafted in fixes/itemtext_issues_suggestions.md pending the fixes/ upload. Expect some entries
   to be resolvable/removable and some to need sharpening.
9. Still not started from the older list: re-triage the 218 BLOCKED availability-audit tables
   (batches 002-005 found access tricks that postdate the triage); the four `himmelstein-*`
   tables that fall between both audits.

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
