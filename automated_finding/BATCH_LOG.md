# IRW Automated Finding — Batch Log

Running, append-only log of every discovery run, batch, and decision made in
this pipeline — kept for context so a future batch doesn't repeat work or
re-investigate something already resolved. It is a history, not a task list;
checkboxes here just mean "this line item is settled," not "actionable."

**For currently open action items, see `TODO.md`.**

## Cleaning scripts (irw_output/queue/ → irw_output/cleaned/)

**Priority queue (new good candidates, not yet processed):**
- [x] `10_7910_dvn_ireejj.csv` — AI Awareness & Attitudes in Bosnia (386p / 51i) — already on Redivis (karajko2025_ai_benefit/risk/governance/trust from batch 4); skip
- [x] `10_7910_dvn_atlxc5.csv` — Non-compliance task replication data (414p / 32i) — already on Redivis (xu2024_noncompliance/self_efficacy/emotional_exhaust/turnover_intent/unethical_behav from batch 4); skip
- [x] `osf_h6gqf.csv` — Resting state fMRI / Dark Triad DDDT (129p / 3 subscale sums) — skipped; only subscale sum scores, not individual item responses

- [x] `10_6084_m9_figshare_30903575_v2.csv` — Conspiracy Belief / AQ-10 / Schizotypy — 5 scale files
- [x] `10_7910_dvn_nfrees.csv` — Burnout Assessment Tool
- [x] `10_7910_dvn_2iblrk.csv` — Personality + Financial + Handwriting — 2 scale files
- [ ] `10_7910_dvn_dwplbc.csv` — Political Preference China — on hold (0-response ambiguity; anchor labels not documented) — tracked as an open item in `TODO.md`
- [x] `10_7910_dvn_iek9pw.csv` — Personality + Entrepreneurship (Brazil) — 5 scale files
- [x] `10_6084_m9_figshare_26130403_v1.csv` — Quarter-Life Crisis — 3 scale files
- [x] `10_7910_dvn_y75cp2.csv` — DPT Non-Cognitive Traits — 6 scale files
- [x] Redivis upload — all cleaned datasets uploaded (batch 1 + batch 2: 15 new tables)
- [x] Biblio sheet entries — all entries added
- [x] `10_7910_dvn_zdnsfj.csv` — Sports robot adoption (batch 3 good candidates)
- [x] `10_7910_dvn_3ckjv1.csv` — Instructor–student interaction medicine
- [x] `10_6084_m9_figshare_26789680_v3.csv` — Creactability Football
- [x] `10_6084_m9_figshare_26631202_v1.csv` — HoNOS 13-item
- [x] `10_7910_dvn_shwnk1.csv` — Physiotherapy clinical environment
- [x] `10_7910_dvn_ntvw8t.csv` — Questionnaire and Interview Results
- [x] `10_7910_dvn_ue55jt.csv` — Character qualities med students Korea (already in IRW)
- [x] `10_7910_dvn_k0srs8.csv` — English Relative Clause Rasch
- [x] `wu2026_ceramic_vases.py` — Ceramic vases aesthetics — 3 scale files (typical, novel, liking)
- [x] `arora2025_blueq.py` — BLUE-Q blended learning — 3 scale files (pedagogical, synchronous, asynchronous)
- [x] `yandun2026_cognitive.py` — Cognitive development pre/post — 4 scale files (attention, memory, language, logical_thinking)
- [x] `10_7910_dvn_tlkxaz.csv` — LLM Moral Identity — skipped (only subscale means, LLM respondents, not individual human responses)
- [x] Redivis upload — batch 3 cleaned datasets (10 new tables): wu2026_typical/novel/liking, arora2025_blueq_pedagogical/synchronous/asynchronous, yandun2026_attention/memory/language/logical_thinking
- [x] Biblio sheet entries — batch 3 (entries ready in /tmp/refs.csv)

## Queue sheet audit (2026-06-08)

- [x] DVN/TAISB2 — already in biblio sheet (dass21_depression_anxiety_stress, 2026-06-07)
- [x] DVN/NZ7VFL — already in biblio sheet (dass21_medical_graduates_bangladesh, 2026-06-07)
- [x] DVN/5YF5XJ — already in biblio sheet (pcss_adolescent_athletes + mfq_adolescent_athletes, 2026-06-07)
- [x] DVN/25583 — excluded; N=10 (Bakdash ISR, omitted in batch 4)
- [x] OSF pvb2j — excluded; repo contains IRT model diagnostics only, no raw response matrix

## Pending discovery runs

- [x] Run discovery with "patient reported outcomes" search term — 25 candidates, 0 good, 3 human_assistance (small N), 20 no_usable_file; results in irw_triage_pro.csv

## Pipeline improvements

- [x] Re-run discovery with Zenodo fixed — 539 candidates in irw_discovered.csv (135 from Zenodo)
- [x] Triage new candidates — 539 scored; 12 good, 60 human_assistance, remainder no_usable_file/download_failed
- [x] Expand search terms — executive function tasks, reaction time paradigms, educational tests not yet covered
- [x] Re-run discovery with new terms — 714 candidates in irw_discovered_new.csv (queries: executive function, reaction time task, reading fluency, phonological awareness, mathematics achievement, stroop, flanker task, n-back)
- [x] Triage new candidates — 714 scored; 13 net-new good (after dedup against queue sheet)
- [x] Cleaning scripts (batch 4) — moten2023_bpd (1 file), xu2024_conscientiousness (5 files), karajko2025_ai_attitudes (4 files); bakdash2014_isr omitted (N=10); 9 of 13 skipped as not IRW-eligible
- [x] Redivis upload — batch 4 cleaned datasets (10 new tables)
- [x] Biblio sheet entries — batch 4 (entries in /tmp/biblio_batch4.csv)
- [x] Retriage `human_assistance` rows — `irw_retriage_ha.py` applied to `irw_triage_new.csv` (376 rows). Results in `irw_retriage_ha.csv`:
  - 133 `not_item_response` — scraped HTML tables, data dictionaries, implausible n_responses ratios → drop
  - 86 `aggregate_continuous` — >50 unique resp values or extreme dup ratio → likely continuous/scale-score data → drop
  - 7 `wrong_file_selected` — all SAPA-Project entries; codebook file grabbed instead of response data
  - 4 `recoverable_format` — semicolon-delimited files read as CSV; just needs `sep=';'` then re-triage:
    - HEXACO Personality Traits on Teamwork (osf.io/jb94w/) — F01r–F54 items ✓
    - Soccer Supporters / Dark Triad (su.figshare.com) — HH/CN/VI personality items ✓
    - Visual Context Cognitive Load (DVN/AAJSJ7) — B1–G11 item blocks ✓
    - Sleep Quality mediator (figshare 30195541) — EET_01–EET_29 + PSQI items (multi-scale, needs split)
  - 29 `worth_retrying` — dup_id_item fail but plausible longitudinal structure (ratio 1–8×, n_participants ≥ 50); look for wave/timepoint columns
  - 117 `human_review` — genuinely ambiguous; requires eyes on raw file (also covers unresolved human_assistance rows from original triage.csv)

- [x] Redivis upload — batch 5 cleaned datasets (16 new tables): lindstrom2021 (4), zaehl2023 (7), merlo2025 (5)
- [x] Biblio sheet entries — batch 5 (entries in /tmp/biblio_batch5.csv)
- [x] Run personality-focused discovery (14 terms) — 1,196 candidates → irw_discovered_personality.csv
- [x] Triage personality candidates — irw_triage_personality.csv: 8 good, 282 human_assistance, 775 no_usable_file
- [x] Retriage personality human_assistance — irw_retriage_personality.csv: 190 not_item_response, 38 aggregate_continuous, 7 wrong_file_selected (SAPA, duplicate of existing TODO), 2 recoverable_format (already processed), 8 worth_retrying, 37 human_review
- [x] Batch 6 — ilic2019_cddq (1 file): Cervical Dysplasia Distress Questionnaire N=154/23i/1-4
  - script: data/ilic2019_cddq.py; CSV in irw_output/cleaned/; biblio in /tmp/biblio_batch6.csv
- [x] Redivis upload + biblio sheet — batch 6 (1 table: ilic2019_cddq)
- [x] Process `recoverable_format` cases — results:
  - DVN/AAJSJ7: skipped — fixation count data from psycholinguistics experiment, not Likert responses
  - Soccer/Lindström 2021 (osf.io/14980251): 4 files (lindstrom2021_honesty_humility/team_identification/conscientiousness/violent_intentions); N=212-231; 1-7 Likert
  - HEXACO Teamwork/Zähl 2023 (osf.io/jb94w): 7 files (zaehl2023_hexaco + 6 TWQ subscales); N=54; 1-5 Likert
  - Sleep Quality/Merlo 2025 (figshare 30195541): 5 files (merlo2025_eet + 4 eng subscales); N=1065; PSQI+TECH excluded
  - Biblio entries in /tmp/biblio_batch5.csv (16 rows)
- [ ] Process 7 SAPA annual releases (2017–2024) — all CC0, none in IRW yet (existing entries are DVN/AD9RVY and DVN/SD7SVE, different releases) — tracked as an open item in `TODO.md`
  - DOIs: DVN/PNGUT5 (2017), DVN/7A9YMV (2018), DVN/FUUB2Q (2019), DVN/YOEEDQ (2020), DVN/JOGYUD (2021), DVN/BVF52I (2022), DVN/3BTT82 (2023-24)
  - Batch script grabbed ItemInfo.csv (codebook); actual data is SAPAdata{dates}.csv (35–193MB each)
  - File IDs: 10988792, 10988863, 10988866, 10988879, 10988881, 10988884, 10988887
  - Format: wide sparse (person × q_number items), 1-6 Likert + NA, ~135 items; covariates: sex, age, english
  - Decision needed: process all 7 years separately, most recent only, or pool with cov_year
- [x] Spot-check `worth_retrying` cases from irw_retriage_ha.csv (4 original + 8 from personality triage = 12 total):
  - **AI Literacy** (figshare 29488523, 1205×58) — eligible. user_id resets each year (2022/2023/2024); use year+user_id composite as id. 54 items in 9 subscales (L,RE,R,SG,CM,A,IM,S,C,BI). cov_year, cov_grade, cov_age, cov_gender, cov_country.
  - **Cognitive Dissonance** (DVN/XPURU1, 1203×45) — skip. `time` is response duration, not wave. Columns are pre/post political policy positions with change-score composites — not item-response data.
  - **Body Checking** (osf.io/58xb9, 224×181) — eligible for questionnaire scales. German study; EDEQ(28i), WI(14i), FKG(20i), FKS(~17i) answered once per person. Also S1/C1-C3/S2/NC1-NC3 condition×emotion blocks (could be treated as items). ~8 duplicate rows need dropping. cov_condition, cov_sample, cov_sex, cov_age.
  - **Conspiracy Belief** (figshare 30903575) — already processed in batch 2 (5 scale files). Qualtrics export has unnamed cols; prior cleaning used queue CSV. Skip.
  - **Smoking Cessation** (DVN/8LBLYS, 319×170) — eligible. BFI(44i), FTND(6i), TSRQ(15i), ANRT(12i). Login datetime unique per person; dup is only 2 rows. Split by scale.
  - **Language Learning** (DVN/CRSBHT, 90×16) — skip. Only subscale totals (Memory/Cognitive/Compensatory/Metacognitive/Affective/Social strategy sums), not individual item responses.
  - **Self-esteem/Loneliness** (figshare 21515877, 303×51) — eligible. Items A1–A48 (Chinese adolescent scales: loneliness, self-esteem, social anxiety). `number` resets per class; use row index as id. cov_age, cov_grade, cov_sex, cov_left_behind_type.
  - **Aging Male Symptom** (DVN/9V2I0P, 1335×18) — eligible. Q01–Q17 are AMS questionnaire items. Dup was triage artifact (Testo continuous covariate had ~620 unique float values, used as id). Each row = one patient; use row index. cov_testosterone=Testo.
  - **Empathy Medical Students** (figshare 16683931, 588×136) — eligible but complex. Chinese headers; scales B(21i)+C(25i)+D(16i)+E(5i)+F(14i)+G(20i). Trailing cols are subscale aggregates (drop). Some missing 学号 (student ID); 年级 (grade/cohort) explains dup. Use row index as id.
  - Skipped: Joy of Destruction (game data, ratio=7.4×), HEXACO-100 (domain scores, ratio=7.8×)
- [x] Batch 7 — 6 datasets, 19 new tables:
  - skalka2025_ai_literacy (1): 1205p/50i/0-5; figshare 29488523
  - opladen2025_edeq/wi/fkg/fks (4): German BN/BDD/IAD N≈211; osf.io/58xb9
  - kushnir2017_bfi/tsrq/anrt/ftnd (4): smoking cessation N=316-319; DVN/8LBLYS; FTND uses standard ordinal scoring (0-3)
  - chen2022_cls/ses/sasc (3): Chinese adolescents N=303; CLS(16i/1-5), SES(10i/1-4), SASC(14i/1-3); boundaries confirmed from per-item max distributions; figshare 21515877
  - kim2020_ams (1): Korean men N=1335/17i/1-5; DVN/9V2I0P; .5 values dropped (imputed)
  - wu2021_empathy/resilience/burnout/swls/career_expectation/panas (6): Chinese med students N=588; figshare 16683931
  - scripts in data/; CSVs in irw_output/cleaned/; biblio in /tmp/biblio_batch7.csv (19 rows)
  - [x] Redivis upload — batch 7 (19 new tables)
  - [x] Biblio sheet entries — batch 7 (/tmp/biblio_batch7.csv)

- [x] Queue sheet unresolved 'good' triage candidates:
  - DVN/0ADT0D — ma2021_sme_covid (234p/28i/1-7); COVID-19 impact on Chinese SMEs; paper: 10.1371/journal.pone.0257036; script: data/ma2021_sme_covid.py
  - DVN/WV1YJ1 — skipped; identical data to DVN/0ADT0D (same 234×28 values, abbreviated column names only)
  - DVN/SNLKUE — balmas2018_leader_personality (2171p/14i/1-5) + balmas2018_leader_attitudes (2166p/3i/1-5); 5 studies pooled; paper: 10.1111/ajps.12354; script: data/balmas2018_leader_personality.py
  - [x] Redivis upload — batch 8 (3 new tables: ma2021_sme_covid, balmas2018_leader_personality, balmas2018_leader_attitudes)
  - [x] Biblio sheet entries — batch 8 (/tmp/biblio_batch8.csv)

- [ ] ~566 `human_review` rows — tracked in "Automated queue - Human eye" Google Sheet (600 rows total after dedup, 2026-06-22); the 181 figure in earlier notes undercounted; sheet has accumulated entries across all batches/runs — tracked as an open item in `TODO.md`

- [x] Batch 7 discovery complete (2026-06-12) — 1,317 candidates, 9 good (all already on Redivis), 27 human_review (added to Human eye sheet), batch files cleaned up

## Batch 9 (2026-06-24)

- [x] Discovery — 2,029 candidates (267 multilingual terms, 9 languages × 30 topics); irw_discovered_batch9.csv
- [x] Triage — irw_triage_batch9.csv
- [x] Retriage human_assistance — irw_retriage_batch9.csv: 10 worth_retrying, 59 human_review, 1 recoverable_format
- [x] human_review_batch9.csv (59 rows) — added to "Automated queue - Human eye" Google Sheet
- [x] germann_2026_terrorism.py — 5 tables (immigration/redistribution/state_intervention/environment/national_identity); DVN/ALYGQS; N≈53k; CC0
- [x] frikha_2023_motivation.py — 2 tables (pe_acrs/pe_ms); DVN/UOBDRV; N=308; CC0
- [x] Dictionary entries added for all 7 tables (/tmp/biblio_batch9.csv)
- [x] Redivis upload — 7 new tables

## Workflow notes (2026-06-24)

- `cleaned_index.csv` eliminated — was a holding tank but processing pace made it unnecessary
- `irw_output/queue/` eliminated — auto-processed CSVs went here; replaced by scripts that write directly to `irw_output/`
- `irw_output/` now contains only upload-ready CSVs; nothing else
- Dedup check = against the dictionary Google Sheet (https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s)

## Batch 10 (2026-07-12) — skill test run

- [x] Added `automated_finding/.claude/skills/irw-automated-finding/SKILL.md` — orchestration layer for this pipeline; flags that `irw_process_queue.py`/`irw_output/queue/`/`cleaned_index.csv` in README.md are stale per the 2026-06-24 workflow notes above
- [x] Discovery — 4 new terms (impostor syndrome, financial literacy, grit scale, math anxiety); 550 candidates → `candidates_test10.csv`; terms logged in `search_terms_log.csv`
- [x] Triage — irw_triage_test10.csv: 0 good, 46 human_assistance, 2 not_item_response, 2 license_restricted, 56 download_failed, 444 no_usable_file
- [x] Retriage human_assistance — irw_retriage_test10.csv: 6 not_item_response, 22 aggregate_continuous, 2 recoverable_format, 2 worth_retrying, 14 human_review
- [x] human_review_test10.csv (14 rows) — added to "Automated queue - Human eye" Google Sheet
- [x] 2 `recoverable_format` cases — re-read with `sep=';'`, both eligible and processed:
  - kurach2026_financial_literacy (data/kurach2026_financial_literacy.py): DVN/8XGUZI, N=778/3i, resp 0-1 (incorrect/correct), CC0. cov_gender, cov_treatment (4 arms: T0/Teasy/Thard/Treward), cov_total_time. Source also had a 3rd raw code (2="don't know") — not ordinal (not "more correct" than a right answer), so those responses are excluded rather than scored; 36 people who answered DK on all 3 items dropped entirely. Caught after initial review incorrectly treated 0/1/2 as a valid ordinal resp column — see workflow note below.
  - schoepp2022_test_anxiety (data/schoepp2022_test_anxiety.py): osf.io/r67wb/, N=130/18i, 0-3 Likert. License field showed as raw OSF UUID (563c1cf88c5e4a3877f9e96a) in triage — resolved via OSF's `/v2/licenses/{id}/` endpoint to CC BY 4.0 (verified, not "unknown"). Source `id` column had one collision (id=10078 x2, timestamps 1 min apart — data-entry coincidence, not a real retest pair); used row position as id instead. One respondent with all-18-items-blank correctly dropped (130 of 131 raw rows retained).
  - CSVs in `irw_output/`; biblio entries added to dictionary sheet (2026-07-13); temp files deleted
- [x] 2 `worth_retrying` cases — re-download, look for wave/timepoint column:
  - Mobile phone addiction / social anxiety (168p/55i, DVN/QS5D8C)
  - Listening text repetition / metacognition (306p/9i, DVN/WWN1TS)
  - Resolved in batch 13: DVN/QS5D8C → `data/chen2026_mpa.py` (processed); DVN/WWN1TS → flagged for human review (opaque item-code mapping, not processed). Checkbox was left unchecked here at the time — caught during the 2026-07-14 TODO/log split.
- No `good` candidates this run — expected given the broad, unrelated-construct term mix chosen to exercise the pipeline rather than target one instrument

## Batch 11 (2026-07-13)

- [x] Discovery — 12 new terms (workplace burnout, creativity scale, leadership style, screen time, climate anxiety, prosocial behavior, aggression scale, empathy scale, resilience scale, social comparison, narcissism scale, gratitude scale); 668 candidates → `candidates_batch11.csv`; terms logged in `search_terms_log.csv`
- [x] Triage — irw_triage_batch11.csv: 3 good, 32 human_assistance, 1 not_item_response, 3 license_restricted, 68 download_failed, 560 no_usable_file, 1 error
- [x] Retriage human_assistance — irw_retriage_batch11.csv: 9 not_item_response, 12 aggregate_continuous, 0 recoverable_format, 4 worth_retrying, 7 human_review
- [x] Reviewed the 3 `good` flags — 1 was a false positive:
  - **Skip** — "Personality predicts dispersal and settlement" mesocosm dataset (figshare 32605179): animal behavioral ecology data (RFID-tagged individuals, territories, ponds), not human item responses. Triage matched on shape alone (small numeric table), not content — worth remembering the `good` flag is not a content check.
  - **Processed** — rosetti2023_gad7 / rosetti2023_climate_anxiety / rosetti2023_climate_knowledge (data/rosetti2023_climate_anxiety.py): Climate Anxiety Data Base (figshare 16900393), N=468, CC BY 4.0. GAD-7 (7i, 0-3), CAS (22i, 0-4), CCKQ (10i, correct/incorrect recoded to 1/0). cov_age, cov_gender, cov_social_net_time, cov_news_time. Dropped: all `*_sum` aggregate columns, `EconGame_q*`/`ChoseToDonate` (ambiguous economic-game choices, not clearly Likert — left for a future look). CSVs in `irw_output/`; biblio in `biblio_batch11.csv`.
  - **Flagged for human review, not processed** — "Raw data from the questionnaire" (PLOS/Podgórniak-Krzykacz 2021, mayors/leadership style, Poland): `P1.1`-`P1.6` blocks (4 sub-items + "suma" each) match the OCAI (Organizational Culture Assessment Instrument) — an *ipsative* scale (4 culture-type scores forced to sum to 100 per block), not independent Likert items. `P2.1`-`P2.5` is a separate, unidentified instrument. Needs the paper to confirm structure before deciding how (or whether) to represent ipsative data in IRW format.
- [x] `human_review_batch11.csv` (8 rows: 7 from retriage + the OCAI/leadership dataset above) — added to "Automated queue - Human eye" Google Sheet; biblio entries added to dictionary sheet
- [ ] 4 `worth_retrying` cases — re-download, investigate (tracked as an open item in `TODO.md`):
  - Questionnaire scores/descriptive stats (748p/62i, figshare 30033097)
  - Personality predicts prosocial behavior (801p/66i, osf.io/zcdk8/)
  - Coaching leadership styles / athlete engagement (197p/15i, figshare 29856026) — only issue flagged is low-confidence id column
  - Affect spin and prosocial behavior (400p/16i, figshare 29486192)

## Batch 12 (2026-07-13)

- [x] Discovery — 12 new terms (trust in science, eco-anxiety, workaholism, mindfulness scale, loneliness scale, job insecurity, work-life balance, moral disengagement, cyberbullying, sexual harassment, religiosity scale, grief scale); 637 candidates → `candidates_batch12.csv`; terms logged in `search_terms_log.csv`
- [x] Triage — irw_triage_batch12.csv: 2 good, 44 human_assistance, 3 not_item_response, 3 license_restricted, 74 download_failed, 510 no_usable_file, 1 error
- [x] Retriage human_assistance — irw_retriage_batch12.csv: 8 not_item_response, 19 aggregate_continuous, 1 recoverable_format, 2 worth_retrying, 14 human_review
- [x] `recoverable_format` case checked — not usable: cyberbullying intervention data_sheet (frontiersin figshare 7256891, 10.3389/fpsyg.2018.02050.s001) is aggregate composite scale scores per subscale/wave (values include 999 as a missing-data sentinel), not individual items — no raw item-level data in this file. Dropped.
- [x] Reviewed the 2 `good` flags — both need a human before processing, not clean auto-processes like batch 11's Climate Anxiety:
  - AI-induced job insecurity, Indian IT professionals (figshare 32235024): 10 named 5-item subscales, only 3 identifiable from metadata (AIJI, PD, QoL); 7 undefined abbreviations (TF, OF, IF, ELM, SPF, TSPC, PE) need the source paper.
  - Personality/Family/Interpersonal Behaviour dissertation (figshare 22679644): triage undercounted n_items=14, actual raw file has 92 columns incl. **PII** (name/email/phone — must strip). Item wording suggests 5 bundled instruments (empathy, PID-5-BF-like, FAD general functioning, moral disengagement, Marlowe-Crowne SDS) but none confirmed against source.
- [x] `human_review_batch12.csv` (16 rows: 14 from retriage + the 2 good-but-complex cases above) — added to "Automated queue - Human eye" Google Sheet
- Nothing processed this batch — first batch since the skill existed where every candidate needed a human call rather than a clean auto-process

## Batch 13 (2026-07-13)

- **Process fix**: batches 10-12 (and the start of this one) had silently regressed to English-only discovery terms. Batch 9 was the only prior run to translate terms into 8 additional languages (es/de/fr/zh/ja/ar/nl/ko) and it wasn't carried forward as standing practice. Fixed in `SKILL.md` Step 1 — every future batch must run each new term in all 9 languages together, not English-only.
- [x] Discovery — 12 new terms (emotional eating, psychological flexibility, religious coping, gender role attitudes, future time perspective, psychological entitlement, envy scale, body surveillance, rumination scale, work passion, anxiety sensitivity, trust in artificial intelligence) × 9 languages (108 queries total); English run → `candidates_batch13.csv` (787), multilingual run → `candidates_batch13_intl.csv` (413); merged + deduped by doi/url → 1,041 unique candidates; all 108 terms logged in `search_terms_log.csv`
- [x] Triage — irw_triage_batch13.csv: 1 good, 72 human_assistance, 5 not_item_response, 900 no_usable_file, 7 license_restricted, 54 download_failed, 2 error
- [x] Retriage human_assistance — 11 not_item_response, 24 aggregate_continuous, 0 recoverable_format, 5 worth_retrying, 32 human_review
- [x] The 1 `good` candidate — Ptáček & Jelínek (2023), Czech CompACT/DASS-21/AAQ-II/SWLS bundle (osf.io/cwjxq), N=299, CC BY 4.0 (resolved from OSF license UUID 563c1cf88c5e4a3877f9e96a). One file per scale per IRW rule. `data/ptacek2023_compact.py` → 4 tables (compact, dass21, aaq2, swls).
- [x] Reviewed 5 `worth_retrying` cases (2 were unresolved duplicates carried over from batch 10's DVN/QS5D8C and DVN/WWN1TS):
  - **Processed** — Westhoff et al. (2023) psychological-flexibility ESM daily-diary study (osf.io/ejtzs, same CC BY 4.0 license id as above), N=113 x up to 105 sessions (21 days x 5/day), PBAT (18i) + STOPD (5i), 0-100 continuous slider. `-1` sentinel = unfinished session (932 rows, exactly matches `Finished==-1`), dropped whole-row. `wave = (Day-1)*5+Session`. `data/westhoff2023_pbat.py` → 2 tables.
  - **Processed** — Chen (2026), mobile phone addiction / social anxiety / self-control, Chinese college students (DVN/QS5D8C), N=195, CC0, 1-5 Likert. Source `序号` row-number column had 27 dup values (data-entry artifact) — used row position as id instead. `data/chen2026_mpa.py` → 3 tables (mpa, sa, sc). Closes out the batch-10 pending item.
  - **Skip** — Reddit AI-emotion dataset (DVN/61S3WH): thread/post text + Plutchik emotion category labels, not survey item responses.
  - **Skip** — COVID depression/anxiety Malaysian students (figshare 14207417, CC BY 4.0): file only contains composite DASS/MSPSS subscale scores and severity categories, no item-level data.
  - **Flagged for human review, not processed** — listening-text-repetition study (DVN/WWN1TS, CC0): real binary item-level comprehension scores exist with `listentimes` (1/2/3) as a plausible wave key matching the paper's repeated-listening design, but the 6 score columns per row map to items via an opaque `task`/`items` code (e.g. `"1111-1116a"`) that isn't resolved by the deposited `items_labelling` sheet (only 4 example rows) or `questionnaire.docx` (open-ended text responses, not a codebook). Needs the source paper or author contact. Closes out the other batch-10 pending item, converting it from "worth_retrying" to a properly scoped human-review case.
- [x] `human_review_batch13.csv` (33 rows: 32 from retriage + the listening-text case) — ready to add to "Automated queue - Human eye" Google Sheet
- [x] Biblio entries for 9 new tables prepared in `/tmp/biblio_batch13.csv` (ptacek2023 x4, westhoff2023 x2, chen2026 x3) — ready to paste into dictionary sheet
- [x] Redivis upload — batch 13 (9 new tables in `automated_finding/irw_output/`)
- [x] Biblio sheet entries — batch 13 (`/tmp/biblio_batch13.csv`, 9 rows)
- [x] `human_review_batch13.csv` (33 rows) — pasted into "Automated queue - Human eye" Google Sheet

## Process note (2026-07-13)

Batches 10-12 (and the start of 13) had silently reverted to English-only discovery terms — batch 9 was the only prior run to translate into 8 additional languages (es/de/fr/zh/ja/ar/nl/ko) and it wasn't carried forward as standing practice. Fixed in `SKILL.md` Step 1: every future batch must run each new term across all 9 languages together. User flagged this mid-batch-13; batch 13 was redone to include translations once caught.

## Batch 14 (2026-07-13)

- [x] Discovery — 12 new terms (parenting stress, financial anxiety, workplace incivility, psychological capital, vaccine hesitancy, flow experience, curiosity scale, pro-environmental behavior, food insecurity, microaggressions, self-disclosure, help-seeking attitudes) × 9 languages (108 queries total); English run → `candidates_batch14.csv` (683), multilingual runs → `candidates_batch14_intl1.csv` (223) + `candidates_batch14_intl2.csv` (152); merged + deduped by doi/url → `candidates_batch14_merged.csv` (914 unique); all 108 terms logged in `search_terms_log.csv`
- [x] Triage — irw_triage_batch14.csv: 1 good, 49 human_assistance, 6 not_item_response, 742 no_usable_file, 7 license_restricted, 107 download_failed, 2 error
- [x] Retriage human_assistance — irw_retriage_batch14.csv: 10 not_item_response, 17 aggregate_continuous, 2 recoverable_format, 2 worth_retrying, 18 human_review
- [x] Reviewed the 1 `good` flag — false positive, same pattern as batch 11's mesocosm dataset (matched on shape, not content):
  - **Skip** — "Patterns and Implications of Ability Tracking: Evidence from Texas Public Schools" (DVN/5ZQHV6): `CourseNames.xlsx` (52×2) is a course-name lookup table; rest of dataset is school/district administrative, finance, election, and NAEP files — no individual item-response data anywhere in the deposit.
- [x] 2 `recoverable_format` cases (semicolon-delimited, misread as comma) — both eligible, processed:
  - **algner2022** — Algner & Lorenz (2022), "You're Prettier When You Smile" workplace gender-microaggressions (MIMI) scale validation (frontiersin figshare 19366439/19366442), CC BY 4.0. Study 1 (N=500): 68-item MIMI candidate pool + Workplace Incivility Scale (16i), Perceived Subtle Gender Bias Index (21i), Meaning-of-Work/SiA (12i). Study 2 (N=612): final MIMI-16 + UWES-9, German Core Self-Evaluation Scale (12i), Occupational Self-Efficacy-SF (6i), Turnover Intention Scale (3i). `jsat`/`jsat3-6` job-satisfaction columns excluded — mixed dichotomous/1-5/percentage-allocation format, not a clean ordinal scale. Single-item `feminism`/`equality`/`workenvironment` attitude questions kept as covariates (not treated as scales). `data/algner2022_mimi.py` → 9 tables.
- [x] 2 `worth_retrying` cases reviewed:
  - **Skip** — grain borer/maize weevil taxis data (agdatacommons.nal.usda.gov 32591979): insect behavioral-ecology data, not human item responses.
  - **Processed** — **shi2024** — Shi et al. (2024, *Behavioral Sciences* 14(10):928), parental early maladaptive schema → adolescent social adaptation, intergenerational transmission (DVN/7CYIQG), CC0, N=201 Chinese parent-adolescent dyads. Source `序号`/`身份证号` unusable as id (duplicated/missing, and the latter is an ID-card number — PII, dropped along with all name columns); used row index instead. Young Schema Questionnaire short-form (75i, 1-6 Likert) answered separately by caregiver and adolescent, plus the Adolescent Social Adaptation Scale (Chen et al. 2016, 33i, 1-5). Confirmed instrument identities and item counts against the published paper (PMC11505476) before processing. `data/shi2024_ysq.py` → 3 tables.
- [x] `human_review_batch14.csv` (18 rows) — pasted into "Automated queue - Human eye" Google Sheet
- [x] Biblio entries — batch 14 (`/tmp/biblio_batch14.csv`, 12 rows: algner2022 x9, shi2024 x3) — pasted into dictionary sheet
- [x] Redivis upload — batch 14 (12 new tables: algner2022_mimi_pool/wis/psgbi/sia/mimi16/uwes/cse/oss/tis, shi2024_ysq_parent/ysq_adolescent/sas)
- [x] Temp files cleaned up (`candidates_batch14*.csv`, `irw_triage_batch14.csv`, `irw_retriage_batch14.csv`, `human_review_batch14.csv`, checkpoint/log files)

## Batch 15 (2026-07-13)

- [x] Discovery — 12 new terms (social desirability, sense of coherence, authentic leadership, job crafting, distress tolerance, body appreciation, orthorexia, intuitive eating, insomnia severity, medical mistrust, workplace ostracism, AI literacy) × 9 languages (108 queries total); English run → `candidates_batch15.csv` (682), multilingual runs → `candidates_batch15_intl1.csv` (274, first 6 terms) + `candidates_batch15_intl2.csv` (223, last 6 terms); merged + deduped by doi/url → `candidates_batch15_merged.csv` (950 unique); all 108 terms logged in `search_terms_log.csv`
- [x] Triage — irw_triage_batch15.csv: 4 good, 65 human_assistance, 8 not_item_response, 792 no_usable_file, 13 license_restricted, 68 download_failed
- [x] Retriage human_assistance — irw_retriage_batch15.csv: 15 not_item_response, 21 aggregate_continuous, 0 recoverable_format, 3 worth_retrying, 26 human_review
- [x] Reviewed the 4 `good` flags:
  - **Skip** — "Patterns and Implications of Ability Tracking: Evidence from Texas Public Schools" (DVN/5ZQHV6) — same false positive already documented in batch 14 (`CourseNames.xlsx` lookup table, no item data); recurred here because it re-matched on the AI-literacy/social-desirability term set by shape, not content.
  - **Skip** — "Cultivating AI Literacy in the GenAI Era" academic-library study (figshare 32881049): `S3_Dataset2` sheet contains only 7 subscale mean columns (decimal composites like `AI_Ethics=2.98`), no raw item-level responses.
  - **Processed** — **chowdhury2026** — Chowdhury & Sain, "Teacher AI Literacy for ML Learner Instruction" (figshare 31427369), CC BY 4.0, N=32 teachers. AI Literacy scale (12i, 1-5 Likert), Responsible AI-Use Intentions (4i, 1-5), Vignette decision-quality (4i, binary 0/1). `prior_ai_pd_cat` covariate uses literal string `"None"` as a real category — read with `keep_default_na=False` to avoid pandas silently turning it to NaN. `data/chowdhury2026_ai_literacy.py` → 3 tables.
  - **Processed** — **nelson2019** — Nelson et al. (2019, *PLOS ONE*), "psychometric properties of a new oral health illness perception measure" (figshare 7977755), CC BY 4.0, N=198 adults 62+. IPQ-RDE (Illness Perception Questionnaire — Revised, Dental), 43 items, 1-5 Likert; `-9` sentinel (missing/not administered) filtered. A separate `pqx_*` block in the same file (participant questionnaire, mixed 1-2/1-3/1-4/1-6 ranges across sub-blocks) was left unprocessed — heterogeneous response scales suggest several bundled question batteries, not one instrument, and nothing in the deposited docs names/scopes them. `data/nelson2019_ipqrd.py` → 1 table.
- [x] Reviewed 3 `worth_retrying` cases — all dead ends:
  - KLIPS labor panel (DVN/RWPOMI, 12622p/11i): `QoL`/`IncJQ`/`HardJQ`/`SoftJQ`/`SES5` are precomputed continuous composite indices (fractional values), not raw item responses.
  - "Are ChatGPT's knowledge and interpretation ability comparable to..." (DVN/N7NKSQ): respondent is ChatGPT itself answering a parasitology quiz, not human item responses.
  - Cybersecurity literacy CTCA study (DVN/HWFCOK, 80p/4i): only pre/post aggregate achievement and attitude totals, no item-level data.
- [x] `human_review_batch15.csv` (26 rows) — ready to add to "Automated queue - Human eye" Google Sheet
- [x] Biblio entries for 4 new tables prepared in `/tmp/biblio_batch15.csv` (chowdhury2026 x3, nelson2019 x1) — ready to paste into dictionary sheet
- [ ] Redivis upload — batch 15 (4 new tables in `automated_finding/irw_output/`) — tracked as an open item in `TODO.md`
- [ ] Biblio sheet entries — batch 15 (`/tmp/biblio_batch15.csv`, 4 rows) — tracked as an open item in `TODO.md`

## Batch 16 (2026-07-14) — bare-root "safe substitute" terms

**Motivation:** investigated whether a qualified search term already in `search_terms_log.csv` (e.g. "grit scale") reliably surfaces everything its bare root ("grit") would. Empirically it doesn't — live A/B testing against Dataverse/Zenodo/Dryad/Figshare showed genuinely relevant, non-overlapping hits under the bare form that the qualified form's page-1 results missed (relevance ranking, not phrase/AND matching, governs these APIs). This batch systematically mined `search_terms_log.csv` for qualified terms (`*_scale`, `*_questionnaire`, `*_inventory`, `*_task`, etc.) whose bare root had never been run.

- [x] Identified 19 raw candidate bare-roots via suffix-stripping; filtered to 8 after checking each against the full term list for redundancy/noise: excluded fragments meaningless alone (`ecological momentary`, `flanker`, `go no-go`), pure modifiers/populations not constructs (`functional`, `large-scale`, `national`, `kindergarten`, `preschool`), overly generic terms (`symptom`), and terms already well-covered from adjacent angles (`physical activity` — 6 existing adjacent terms; `vigilance` — redundant with existing `sustained attention` + `vigilance task`).
- [x] Discovery — 8 terms (`aggression`, `creativity`, `curiosity`, `envy`, `grit`, `optimism`, `religiosity`, `rumination`) × 9 languages (72 queries total); English run → `candidates_batch16.csv` (323), multilingual runs → `candidates_batch16_intl1.csv` (109, aggression/creativity/curiosity/envy) + `candidates_batch16_intl2.csv` (110, grit/optimism/religiosity/rumination); merged + deduped by doi/url → `candidates_batch16_merged.csv` (417 unique); all 80 terms (8 English + 72 translated) logged in `search_terms_log.csv`
- [x] **New tool**: `irw_extract_evaluated_dois.py` — mines `BATCH_LOG.md` for DOI-like identifiers of every dataset already evaluated (any outcome, not just ones added to the dictionary/queue sheets) and checks new candidates against them. Built in response to the recurring DVN/5ZQHV6 false-positive (resurfaced as "good" in both batch 14 and batch 15 despite being explicitly skipped after batch 14) — the existing auto-exclusion only checks the dictionary + queue sheets, not prior skip decisions. Extracted 78 identifiers from the log; 0 of batch 16's 417 candidates matched (no repeats surfaced this batch, but the tool is now a standing pre-triage step — see `--check` usage in the script's docstring).
- [x] Triage — irw_triage_batch16.csv: 1 good, 23 human_assistance, 4 not_item_response, 338 no_usable_file, 2 license_restricted, 49 download_failed
- [x] Retriage human_assistance — irw_retriage_batch16.csv: 3 not_item_response, 4 aggregate_continuous, 1 recoverable_format, 1 worth_retrying, 14 human_review
- [x] Reviewed the 1 `good` flag — blocked on license, not a content problem:
  - **Skip (no license)** — "The Role of Attentional Bias in Anxiety and Depression" (osf.io/ctnaq): N=831, 82 items, density 1.0 — otherwise a strong candidate, but the OSF node has no license relationship at all (checked directly via the OSF API, not an unresolved UUID this time — genuinely nothing set). Worth an author-permission email if anyone wants to pursue it; not sent automatically.
- [x] Reviewed the 1 `recoverable_format` case — also blocked on license:
  - **Skip (no license)** — "Assessing Creative Self-Efficacy in the Spanish Workplace" (osf.io/mksw2, semicolon-delimited): confirmed structure (BFI-2-S 30 items + General Self-Efficacy 10 items + two Creative Self-Efficacy scales), but same as above — no OSF license relationship at all. Also noted for future reference: raw file has both `BFI_1` and a derived `BFI_1R` reverse-coded duplicate column (`BFI_1R = 6 - BFI_1`, verified) — a trap for melting both as separate items.
- [x] **New standing file**: `license_blocked_candidates.csv` — created to stop losing otherwise-strong candidates like the two above once their triage CSV gets cleaned up. Checked both for a recoverable contributor email (OSF's API never exposes email directly; only path is a linked *published* paper's Crossref/PMC metadata) — neither has a findable published paper, so both entries carry contributor name + OSF profile link only. Wired into `SKILL.md` Step 4 as a standing per-batch step going forward.
- [x] Reviewed the 1 `worth_retrying` case — processed:
  - **Processed** — **pellerin2020** — Pellerin & Raufaste (2020, *Frontiers in Psychology*), "Psychological Resources Protect Well-Being During the COVID-19 Pandemic: A Longitudinal Study During the French Lockdown" (osf.io/45aq3), CC BY 4.0 (same license id 563c1cf88c5e4a3877f9e96a seen in prior batches). N=674, 9 psychological-resource instruments (CPC-12 Hope/Optimism/Self-Efficacy, 3D-WS-12, ASTI self-transcendence, GQ-6, Minimalist Well-Being Scale gratitude-for-being/peaceful-disengagement, Brief Serenity Scale acceptance), all confirmed against the published paper's Materials section before processing. Items collected only at Wave 0 (baseline) and Wave 5 (final follow-up) — verified empirically (100%/0% non-null pattern) rather than assumed from the R script's comments; `wave` column preserved. `data/pellerin2020_covid_resources.py` → 9 tables.
- [x] `human_review_batch16.csv` (14 rows) — ready to add to "Automated queue - Human eye" Google Sheet
- [x] Biblio entries for 9 new tables prepared in `/tmp/biblio_batch16.csv` — ready to paste into dictionary sheet
- [ ] Redivis upload — batch 16 (9 new tables in `automated_finding/irw_output/`) — tracked as an open item in `TODO.md`
- [ ] Biblio sheet entries — batch 16 (`/tmp/biblio_batch16.csv`, 9 rows) — tracked as an open item in `TODO.md`

## Process note (2026-07-14) — "to be processed" tab confirmed bypassed

While investigating why some promising batch-16 grit candidates never reached the dictionary or the "Human eye" sheet, checked the queue sheet's "to be processed" tab directly (105 rows) against every DOI processed in batches 14-16 — none were present. Confirmed with the user: since batch 7, the automated pipeline has gone straight from a `good`/`worth_retrying` triage flag to a processing script and from there into the dictionary sheet, never staging candidates in "to be processed" first. The tab isn't dead — it's still read automatically by `irw_discover_updated.py` as a dedup-exclusion source, and other (manual, non-pipeline) contributors still add rows to it — but this pipeline doesn't write to it and shouldn't start again. `README.md` and `SKILL.md` updated to describe this accurately instead of the stale "add good rows to the to-be-processed tab" instruction.

Separately, this same investigation surfaced a real pipeline gap: `irw_batch_updated.py`'s `TABULAR_EXT = (".csv", ".tsv", ".xlsx", ".xls")` means the discovery/triage pipeline never even looks at `.sav`/`.dta`/`.sas7bdat`/`.RData` files when resolving a landing page to a data file — despite `datastandard.md` listing all of those as supported formats to *process*. Confirmed concretely: figshare 19713625 ("Psychometric properties of GS, EGO, 3D-GS grit scales in Chinese adults: A Bifactor IRT study") was silently dropped as `no_usable_file` purely because its only file is `.sav` — opened it directly (`pyreadstat`, not installed by default, needed) and it's a strong candidate: N=896, 6 named scales (12-item Grit Scale, 10-item EGO scale, 17-item TD scale, 6-item Brief Resilience Scale, 7-item Brief Self-Control Scale, 9-item SGPS) plus clean covariates. This has likely caused silent false negatives across all 16 batches, not just this one dataset — not yet fixed, tracked in `TODO.md`.

Further discussed with the user (2026-07-14): also removed the "to be processed" tab from `irw_discover_updated.py`'s automatic exclusion check entirely (not just from the staging-step docs above) — `_load_queued_from_sheet()` deleted, `_load_auto_exclusions()` now checks the IRW dictionary only. Rationale: the tab is manually maintained by other, non-pipeline contributors and this pipeline's own candidates never land in it, so treating it as a second exclusion source alongside the dictionary no longer made sense once the staging step itself was retired.

## Batch 17 (2026-07-14) — bare-root terms, part 2

- [x] Discovery — 7 terms from the Q1 bare-root follow-up (`impostor`, `alcohol use`, `drug use`, `gender role`, `internet gaming`, `economic inequality`, `social dominance`) × 9 languages (63 queries total); English run → `candidates_batch17.csv` (185), multilingual runs → `candidates_batch17_intl1.csv` (59, impostor/alcohol/drug/gender role) + `candidates_batch17_intl2.csv` (122, internet gaming/economic inequality/social dominance); merged + deduped by doi/url → `candidates_batch17_merged.csv` (294 unique); all 63 terms logged in `search_terms_log.csv`; `irw_extract_evaluated_dois.py --check` → 0 matches against BATCH_LOG.md's evaluated-DOI list
- [x] Triage — irw_triage_batch17.csv: 1 good, 12 human_assistance, 4 not_item_response, 244 no_usable_file, 33 download_failed
- [x] Retriage human_assistance — irw_retriage_batch17.csv: 2 not_item_response, 3 aggregate_continuous, 0 recoverable_format, 2 worth_retrying, 5 human_review
- [x] Reviewed the 1 `good` flag — turned out to be an exact duplicate, which led to a real bug fix:
  - **Skip (duplicate)** — "Anxiety, Depression, and Stress Are Associated With Internet Gaming Disorder During COVID-19" (figshare 19158812): already fully in the IRW dictionary since 2026-06-12 as `wang2022_iat`/`wang2022_dass_depression`/`wang2022_dass_anxiety`/`wang2022_dass_stress`/`wang2022_fomo`/`wang2022_igas` (6 tables). It slipped past the dictionary exclusion check because `_extract_doi_from_url()`'s figshare regex (`figshare\.com/articles/[^/]+/(\d+)`) only matched URLs with exactly one path segment before the numeric ID — the dictionary's stored URL happened to be a shortened `articles/dataset/19158812` form, but the URL discovery actually finds includes a title slug too (`articles/dataset/Data_Sheet_1_..._xlsx/19158812`), which the old regex never matched. **Fixed**: regex now anchors on the trailing digit run regardless of how many path segments precede it (handles title slugs, `.vN` version suffixes, and query strings) — verified against 6 real URL patterns from past batches. Ran a broader check across the whole dictionary for other duplicate-DOI fallout from this bug; found none — this was the only near-miss, and no duplicate was actually created since it was caught during review, before writing anything.
- [x] Reviewed 2 `worth_retrying` cases:
  - **Skip** — "Table_3_The Depression Anxiety Stress Scale 8-Items..." (figshare 19589485): confirmed pure supplementary statistics table (regression coefficients, VIF, factor loadings) — same false-positive pattern as every other `Table_N_` figshare file seen in past batches, not raw item data.
  - **Processed** — **ma2026** — Ma, An, Chen & Liu (2026, Research Square preprint), "Assessing Online-Related Addiction in Chinese Primary School Students: An Item Response Theory Analysis of Three Scales" (figshare 27211839), CC BY 4.0. N=1108 Chinese primary-schoolers. BSMAS (Bergen Social Media Addiction Scale, 6i, 1-5), SABAS (Smartphone Application-Based Addiction Scale, 6i, 1-6), IGDS9-SF (Internet Gaming Disorder Scale-Short Form, 9i, 1-5 — one stray out-of-range value of 6 in a single cell filtered as a data-entry error). `birthdate` column (real dates of birth for primary-school-aged children) is PII — dropped entirely, not just deprioritized. `data/ma2026_online_addiction.py` → 3 tables.
- [x] `human_review_batch17.csv` (5 rows) — ready to add to "Automated queue - Human eye" Google Sheet
- [x] Biblio entries for 3 new tables prepared in `/tmp/biblio_batch17.csv` — confirmed live in the dictionary sheet 2026-07-14
- [x] Redivis upload — batch 17 (3 new tables in `automated_finding/irw_output/`) — user confirmed done
- [ ] `human_review_batch17.csv` (5 rows) — still sitting locally, unlike batches 15/16's; not confirmed pasted into "Human eye" sheet yet — tracked as an open item in `TODO.md`

## Pipeline fix (2026-07-14) — `.sav`/`.dta`/`.sas7bdat`/`.RData` support added

Fixed the gap noted above: `TABULAR_EXT` in `irw_batch_updated.py` now includes `.sav`, `.dta`, `.sas7bdat`, `.rdata`, `.rda`, `.rds` alongside the original `.csv`/`.tsv`/`.xlsx`/`.xls`. `load_table()` in `irw_triage_updated.py` (shared by both `irw_batch_updated.py` and the single-file `irw_triage_updated.py` tool) now dispatches to `pd.read_spss`/`pd.read_stata`/`pd.read_sas`/`pyreadr.read_r` by extension. Verified each parser accepts the actual code path used (`content = polite_get(file_url).content` → raw bytes → `load_table(content, filename=fname)`): `pd.read_spss` and `pd.read_stata`/`pd.read_sas` all accept a `BytesIO` directly; `pyreadr.read_r` requires a real filesystem path (its signature is `read_r(path, ...)`, no file-like support), so `.RData`/`.rds` bytes get spilled to a `tempfile.NamedTemporaryFile` and cleaned up in a `finally` block. `pyreadstat` and `pyreadr` added to `SKILL.md`'s documented prerequisites.

**End-to-end verification**: ran `irw_batch_updated.process_one()` directly against figshare 19713625 (the `.sav`-only grit dataset from the batch-16 investigation). Before the fix this returned `no_usable_file` without ever downloading anything; after the fix it correctly resolves the `.sav` file, downloads it, parses N=896/78 columns, and flags `human_assistance` (n_items=76, `multi_scale*`/`resp_ordinal*` warnings) — the honest, correct outcome for a file bundling 6 scales plus derived composite/grouping columns that need a human to split. Not reprocessed as an actual IRW table this session — the fix was scoped to the pipeline, not to clearing this specific backlog item.

**Not done**: no mechanism exists to re-triage `no_usable_file` candidates from past batches (their candidate lists were deleted per the temp-file cleanup convention), so whatever this bug silently hid across batches 1-17 is still hidden unless someone re-runs discovery on old search terms. Tracked in `TODO.md`.

## English-terms re-discovery (2026-07-14 – 2026-07-15)

Full execution of the `TODO.md` item above: re-ran every historical English search term now that `.sav`/`.dta`/`.sas7bdat`/`.RData` triage works, to find out how much the old bug actually hid.

- [x] Classified all 2080 unique logged terms by language. First attempt (file-provenance-based) was wrong — several files assumed English-only actually mixed languages. Second attempt used an offline English-dictionary word-list check (`/usr/share/dict/words` + a small technical/acronym allowlist, ≥90% of a term's words must match) — spot-checked both directions (30 included, 20 excluded) with no errors found. **575 terms classified as English.**
- [x] Discovery split into two phases after Harvard's Dataverse API was found severely degraded mid-run (timing out completely on some calls, 30-58s on others — confirmed by direct timing, not assumed): **phase 1** ran the other 6 sources (zenodo/osf/dryad/figshare/datacite/surf) first; **phase 2** ran dataverse + scholars_portal (also slow, ~20-24s/query, but not failing) once Dataverse's health check passed. Rationale for not dropping dataverse entirely: an earlier 11-term pilot (see below) found all 4 of its best alt-format hits *on* Dataverse — it's disproportionately where `.dta`/`.RData` political-science/economics replication archives live, so cutting it would have undermined the whole exercise.
  - Phase 1: 575 queries, ~4.2 hours, 8195 hits.
  - Phase 2: 575 queries, ~5.7 hours (Dataverse recovered to healthy but scholars_portal stayed slow throughout), added more hits.
  - Merged + deduped by doi/url: **10198 unique candidates**.
- [x] **Pilot first** (11 terms: 10 random pre-fix English terms + `grit`, before committing to the full 575): 483 candidates, 13 (2.7%) alt-format, 8 of those `human_assistance`-worthy — established the exercise was worth doing at scale before spending hours on it.
- [x] Built `_scan_file_formats.py`: a lightweight metadata-only scan (`resolve_data_files()` — lists filenames via each repo's API, no download) run on all 10198 candidates instead of full triage, specifically to avoid the ~1-2 day cost full triage would have taken on a set this size for a question ("is the file alt-format?") that doesn't need it. Scan took ~82 minutes. **186 of 10198 (1.8%) resolved to an alt-format file** — the actual size of what the pre-fix bug was hiding across 17 batches' worth of English search terms.
- [x] Full triage on just those 186: 1 `good`, 128 `human_assistance`, 17 `not_item_response`, 37 `download_failed`, 3 `license_restricted`.
- [x] Retriaged the 128 `human_assistance` rows: 42 `worth_retrying`, 33 `not_item_response`, 30 `human_review`, 23 `aggregate_continuous`.
- [x] The 1 `good` — **Skip (no license)**: Rosenberg Self-Esteem Scale in Uruguay (osf.io/h5g36, N=322, 11 items). No license relationship on the node at all; no findable paper. Logged to `license_blocked_candidates.csv`.
- [x] Spot-checked the highest-value `worth_retrying` rows (by N × construct fit, not exhaustively — 42 is far more than any prior batch's count) rather than reviewing all 42:
  - **Processed** — **chen2025** (Chen, 2025, figshare 30093970): "Body Image, Self-Esteem, Peer Support, and Physical Activities Motivation in Adolescents," CC BY 4.0, N=1100 Chinese adolescents, 4 clean scales (Body Image 23i, Activity Motivation 15i, Peer Support 5i, Self-Esteem 10i), all 1-5 Likert, no missing data, exactly balanced gender quota. No linked published paper. `data/chen2025_body_image.py` → 4 tables.
  - **Processed** — **villarrealzegarra2026** (Villarreal-Zegarra, 2026, figshare 32514540): "Telemedicine Readiness Inventory for Facilities (TRI-F)," CC BY 4.0, N=993 Peruvian primary-care health workers, 85 items (p1-p85), 1-4 Likert. Paper found via Crossref (10.64898/2026.07.01.26356790). Source R analysis script fits per-dimension factor models on subsets of the 85 items but doesn't map specific item numbers to named dimensions in an easily-extractable way — kept as one item pool rather than guessing a split. `data/villarrealzegarra2026_trif.py` → 1 table.
  - **Flagged for human review, not processed** — "Sexual cognitive schemas" (figshare 31288357, N=256): 318 columns — 200 unlabeled `z`-prefixed items plus multiple unclear abbreviation blocks (`scs`/`df`/`dn`/`AG`/`SS`/`AC`/`EX`/`NE`) mixed with aggregate composite scores (`IIEF`/`FSFI`/`NEG`/`POS`) — too ambiguous to safely auto-process without the source paper.
  - **Blocked on license, not processed** — two more no-license OSF nodes found the same way as Rosenberg above: "Self-esteem Importance - Lost Email" (osf.io/zg3f8, N=1489, 79 items) and "Cognitive Emotion Regulation and Bystander Behavior in School Bullying" (osf.io/gdbq2, N=1122, 226 items, large enough it likely bundles multiple scales). Both logged to `license_blocked_candidates.csv`, neither structurally inspected yet (no point until a license exists).
  - **Inaccessible** — PIRLS 2023 English/isiZulu achievement data (University of Pretoria's institutional Figshare instance, 12342p/42i): a major international reading-literacy assessment, would be a strong candidate, but the instance's API is behind an AWS WAF bot challenge that blocked every automated request. Needs manual browser access.
  - **37 remaining `worth_retrying` rows never investigated** — saved to `automated_finding/worth_retrying_backlog_english_redisc.csv` (title/url/n_participants/n_items preserved) rather than TODO.md, to keep TODO.md's own "currently open" list lean; TODO.md just points to the file.
- [x] `human_review_english_redisc.csv` (31 rows: 30 from retriage + the sexual-schemas case) — ready to add to "Automated queue - Human eye" Google Sheet.
- [x] Biblio entries for 5 new tables prepared in `/tmp/biblio_english_redisc.csv` — ready to paste into dictionary sheet.
- [x] Redivis upload — 5 new tables (chen2025_body_image/activity_motivation/peer_support/self_esteem, villarrealzegarra2026_trif) in `automated_finding/irw_output/` — user confirmed done
- [x] Biblio sheet entries — confirmed live in the dictionary sheet 2026-07-15
- [x] `human_review_english_redisc.csv` (31 rows) — confirmed pasted into "Human eye" sheet (file deleted locally)

**Bottom line on the original cost/benefit question**: re-running all 575 historical English terms cost roughly 10 hours of background compute (~4.2h phase 1 + ~5.7h phase 2, overlapping somewhat with the ~1.5h scan+triage) and surfaced 186 previously-invisible candidates (1.8% of 10198) — of which, after triage, 5 tables were processed, 3 more strong candidates are sitting in `license_blocked_candidates.csv` ready the moment a license appears, 1 was too ambiguous to process, and 37 remain to be looked at. Multilingual terms (the other ~1500 logged terms) were explicitly out of scope for this run — whether to extend this exercise to them is a separate, larger cost/benefit decision.

## Working the 37-candidate backlog (2026-07-15)

- [x] **Processed** — **emidy2024** (Emidy, Lewis & Pizarro-Bore, 2024, *Public Personnel Management*), "U.S. Federal Employees With Disabilities..." (DVN/UXRFPV), CC0 1.0 — the 2022 Federal Employee Viewpoint Survey (FEVS) microdata. **The largest table this pipeline has ever produced**: N=557,778, 93 items, 761MB. Notable along the way:
  - Item set confirmed via the `.dta` file's own embedded Stata value-label metadata (not guessed from value ranges): 93 items use one of 5 genuine ordinal label sets (`fscale`/`rscale` = agree-disagree in each direction, `gscale` = poor-good, `sscale` = dissatisfied-satisfied, `ascale` = never-always); excluded `q15_1`-`q15_6` (unlabeled binary multi-select checklist) and `q90`-`q93`/`q95` (labeled with nominal telework-arrangement value sets, not ordinal attitude scales).
  - Several items had out-of-label values (0 or 6 on an otherwise-labeled 1-5 scale) — an unlabeled "Do Not Know"/"Does Not Apply" sentinel per FEVS methodology, filtered before it contaminated `resp`.
  - **Caught a real data-integrity bug before it shipped**: first processing attempt used the source `randomid` column as `id` and produced 320 million rows (vs. an expected ~52M) with `ids=99615` instead of the true 557,778 respondents. Root cause: `randomid` is not a unique person key despite the name (confirmed empirically — up to 18 rows share one value), so joining item columns to covariates on it produced a cartesian-product blowup, silently generating wrong data (each response incorrectly duplicated and cross-joined with unrelated people's covariates). Fixed by using row position as `id` instead — this pipeline's standard fallback whenever a source ID column turns out unreliable, but the failure mode here was unusually dangerous: the corrupted version still "ran successfully" and produced a plausible-looking file, just wrong. Caught only because the final `ids=` count didn't match the known respondent count — a reminder to always sanity-check `ids=` in the summary line against an independently-known N, not just check that the script didn't crash.
  - Also caught before committing to it: with all 7 originally-planned covariates, the correctly-joined output would have been ~9-20GB (confirmed by killing a 9GB partial write after 10 minutes) — asked the user, who chose to trim to just `cov_disability` (the paper's actual focus) rather than process at full covariate width or skip the dataset entirely.
  - `data/emidy2024_fevs.py` → 1 table.
- [x] Biblio entry prepared in `/tmp/biblio_english_redisc2.csv` — ready to paste into dictionary sheet.
- [ ] Redivis upload — emidy2024_fevs (761MB — may need to confirm Redivis' upload size handling before treating this as routine) — tracked as an open item in `TODO.md`.
- [ ] Biblio sheet entry — `/tmp/biblio_english_redisc2.csv` (1 row) — tracked as an open item in `TODO.md`.
- [x] Reviewed 4 more backlog candidates, all skipped:
  - DVN/LYAOHZ ("Leaders Always Mattered"): only 6 binary researcher-derived leader-evaluation variables pooled across 10 Canadian Election Study waves (1984-2015), not raw survey items.
  - figshare 28075277 (Financial Literacy Migration): entirely derived econometric variables (entropy scores, factor loadings, logged sums), no raw item battery.
  - DVN/Z3MV4J (Nosek & Smyth 2011 IAT data): 186 columns of IAT block-level reaction-time/error statistics across 5 implicit-association tasks — needs specialized IAT-scoring expertise to convert correctly, not a simple Likert-item file. Triage's "6 items" estimate was a clear mis-parse of this complex structure.
  - DVN/LFQCOO ("Why Anxious People Lean Left"): a 14-file replication package assembling several *already-existing* large public surveys (ANES 2012/2016, multiple CCES modules, TAPS panel) rather than one self-contained new dataset — too multi-source to evaluate as a unit.
  - 32 of the original 37 backlog candidates remain unreviewed; `worth_retrying_backlog_english_redisc.csv` updated to drop all resolved rows (both processed and skipped) so it always reflects only what's left.

## Finishing the 32-candidate backlog (2026-07-15)

User asked to work through all 32 remaining and consolidate every biblio entry (including `emidy2024_fevs`) into one file to paste at once: `/tmp/biblio_english_redisc_all.csv`, 16 new tables across 7 datasets. `worth_retrying_backlog_english_redisc.csv` deleted — every one of the 32 (plus the 4 from the prior session) has now been individually reviewed.

- [x] **Processed** — **dulger2024_wordcompletion** (Dülger, Van Bockstaele, Majdandžić & de Vente, 2024, *Cognitive Therapy and Research*, osf.io/384h5), CC BY 4.0. Word-fragment completion task (implicit interpretation-bias measure), N=179, 60 items, binary correct/incorrect. Source file was already trial-level long format — no melt needed. `data/dulger2024_wordcompletion.py` → 1 table.
- [x] **Processed** — **baka2023** (Baka & Prusik, 2023, figshare 21988799), CC BY 4.0. Three-wave Polish employee study: OLBI (Oldenburg Burnout Inventory, 8i, 1-4), BPNSF (Basic Psychological Need Satisfaction/Frustration, 24i, 1-7), UWES (Utrecht Work Engagement Scale, 17i, 0-6), JCS (Job Crafting Scale, 21i, 0-5), N=839, `wave` column (1/2/3) preserved for all four. `data/baka2023_jobcrafting.py` → 4 tables.
- [x] **Processed** — **avilesgonzalez2019_ces** (Aviles Gonzalez et al., 2019, *PLOS ONE*, figshare 8177303), CC BY 4.0. Caring Efficacy Scale (Coates, 1997), N=215, 30 items, 1-7 Likert — English-gloss column names in the source file matched the standard 30-item CES exactly. A second 13-item block in the same file has an unconfirmed identity, flagged separately for human review. `data/avilesgonzalez2019_ces.py` → 1 table.
- [x] **Processed** — **poza2026_hlseu** (Poza Méndez et al., 2026, figshare 31078552), CC BY 4.0. Health-literacy screening items, N=101, 16 items, binary correct/incorrect, migrant population in Southern Spain. `data/poza2026_hlseu.py` → 1 table.
- [x] **Processed** — **moe2025** (Moè, 2025, figshare 30385261), CC BY 4.0. Italian teachers, N=95: SIS (Situations in Schools, 15 scenarios × 4 motivating-style sub-items = 60i, 1-7), SCS (Self-Compassion Scale, 26i, 1-5, standard range confirmed), ERQ (Emotion Regulation Questionnaire, 10i, 1-7, standard range confirmed). `id` = row position (source `Codice` column had 1 duplicate). `data/moe2025_selfcompassion.py` → 3 tables.
- [x] **Processed** — **gao2025** (Gao, 2025, figshare 28737626), CC BY 4.0. Chinese older adults, N=459: attachment avoidance (6i, 1-7), attachment anxiety (3i, 1-7), spiritual well-being (12i, 1-5), perceived family support (4i, 1-7), and an "SSE" scale (6i, 1-5, abbreviation not confirmed against a paper — none found). A second figshare deposit (30048610) shares this exact title and is byte-identical (`df.equals()` confirmed) — not separately processed. `data/gao2025_family_support.py` → 5 tables.
- [x] Reviewed and skipped 8 more:
  - `hty9u` (Umbrella Review): confirmed via the actual data file — a systematic-review metadata extraction table (author names, titles, abstracts of reviewed papers), not human responses.
  - `yg7qk` (Action Schemas Deaf Adults, N=24): all 17 columns are derived composite scores (VFB_difference, AR_score_stringent, etc.) from an underlying video task — no raw items.
  - `figshare 11286935` (oral health literacy): only 4 summary columns (tooth-cavity count, a literacy score, social class) — no items.
  - `sr7zw` (Intolerance of uncertainty): trial-level fear-conditioning data with only pre-aggregated/demeaned personality covariates, not raw survey items — too experimental/multi-file to fit cleanly.
  - `figshare 32725962` (Spatial Stroop): dozens of files, all pre-aggregated per-condition error-rate/RT summaries, no individual-level data.
  - `figshare 29338256` (Vocabulary Learning): N=20, messy multi-file structure with real participant names in filenames (PII concern) plus interview audio/video.
  - `figshare 21341232` (cognitive load/deception): only aggregate accuracy/RT summary columns per subject, no trial-level items.
  - `figshare 20227446` (risky decision-making): only aggregate Iowa Gambling Task summary scores (premed/sSeek/PosMood/payoff/MeanIGT), no items.
- [x] Flagged 4 more for human review (`human_review_backlog2.csv`, 6 rows total including the CES second block and PIRLS carried over):
  - `DVN/HIT56P` (Peers Affect Personality Development): the raw item file has no id column at all and needs cross-referencing with several other files (baseline/followup waves) by row order — too risky to guess without documentation.
  - `DVN/S0HEZI` (AI Integration, N=3416): confirmed `.RData` support works correctly (`pyreadr` read it fine) — but every single row has real, unredacted name/email/IP/GPS data. A data-sharing concern beyond a simple strip-and-process call, left for a person to decide.
  - `figshare 32953286` (Digital Professionalism Tanzania): mixed structure — binary platform-usage flags, vignette-judgment items, and derived scores all together, no single consistent item type.
  - `osf.io/zc3pf` (anxiety/perspective-taking): license is "Academic Free License 3.0," not one of this pipeline's standard accepted categories — plausibly fine (OSI-approved, permits redistribution) but needs a person to confirm before processing.
- [x] Added 12 more no-license OSF candidates to `license_blocked_candidates.csv` (title/URL/N/items/contributors only, not structurally inspected beyond the license check, given the volume): `osf.io/syw4p`, `uh2av`, `xmfb3`, `mqud7`, `7u8ty`, `39qs5`, `ehtdv`, `yfpt5`, `3k7sh`, `xsbta`, `p23dw`, `w4gnq`.
- [x] **Caught and fixed a real CSV-formatting bug while writing these up**: wrote several `license_blocked_candidates.csv` rows with unescaped commas in title fields (e.g., "The Role of Relational Self-Discrepancy, Negative Affect, and Commitment...") via raw string concatenation instead of the `csv` module, which silently shifted all subsequent columns out of alignment. Caught by checking field counts per row before moving on, not by visual inspection — rewrote every affected row using `csv.writer` and verified all 17 rows have exactly 13 fields matching the header.
- [x] Biblio entries for 16 new tables consolidated into `/tmp/biblio_english_redisc_all.csv` (includes `emidy2024_fevs` from the prior session) — ready to paste into dictionary sheet in one pass. Verified zero table-name collisions against a fresh pull of the live dictionary.
- [x] Redivis upload — 16 new tables in `automated_finding/irw_output/` — user confirmed done
- [x] Biblio sheet entries — confirmed live in the dictionary sheet 2026-07-15 (16/16 found)
- [x] `human_review_backlog2.csv` (6 rows) — confirmed pasted into "Human eye" sheet (file deleted locally)

**Final tally for the whole English-terms re-discovery + backlog effort**: from 575 re-run search terms, 21 new tables processed across 9 datasets (chen2025 + villarrealzegarra2026 from the initial pass, plus emidy2024/dulger2024/baka2023/avilesgonzalez2019/poza2026/moe2025/gao2025 from the backlog session). 17 candidates total sitting in `license_blocked_candidates.csv` awaiting a license. 6 flagged for human review in this session's `human_review_backlog2.csv` (on top of the 31 from the initial pass, already pasted). Roughly 25 confirmed genuinely ineligible along the way (aggregate/derived data, PII concerns, or too complex/multi-file to safely automate) — most of that learning is now captured as reusable patterns (large-N Dataverse "Replication Data" political-science deposits, IAT/reaction-time data, "Table_N_"/summary-statistics figshare files) rather than one-off dead ends.

## Post-processing data-quality fixes (2026-07-15)

User caught two single-row out-of-range values by spot-checking the shipped tables, both the same underlying pattern:
- `baka2023_jcs`: `resp=0` on 1 of 52,761 rows — the Job Crafting Scale is documented 1-5, not 0-5 as the script had assumed from the raw value range alone; the single 0 was a data-entry artifact.
- `avilesgonzalez2019_ces`: `resp=7` on 1 of 6,449 rows — the Caring Efficacy Scale is actually 1-6, not 1-7; the script's original range check (which happened to also match the *separate* 13-item CAPS block's genuine 1-7 range in the same source file) was checking the wrong thing.

Both scripts fixed to filter to their real documented range (`baka2023_jobcrafting.py` now takes explicit `(valid_min, valid_max)` per scale instead of trusting the observed min/max; `avilesgonzalez2019_ces.py` filters to 1-6) and re-run — `baka2023_jcs.csv` and `avilesgonzalez2019_ces.csv` regenerated (1 row fewer each) and re-uploaded to `irw_output/`. `/tmp/biblio_english_redisc_all.csv` updated to match (corrected Likert range in the description, added a note on the filtered artifact).

**Lesson for future scripts in this pipeline**: "the observed min/max in the raw data" is not the same as "the documented valid range for the instrument" — a single stray value at the boundary is easy to miss when eyeballing `.min()`/`.max()` on a large table, especially when (as with the CES case) a *different* scale in the same source file coincidentally has the same wrong-looking range and creates false confidence. Checking `value_counts()` for values with suspiciously low frequency at the extremes — not just the min/max themselves — would have caught both before shipping.

## Batch 11 `worth_retrying` cases resolved (2026-07-15)

Four cases sat un-investigated in `TODO.md` since batch 11. All 4 now resolved:

- **Processed** — **dou2025** (Dou, Zhang, Wang, Zhang & Hou, 2025, *PLOS ONE*, DOI 10.1371/journal.pone.0331067), CC BY 4.0, figshare 30033097. "The way aesthetic needs affects the relationship between aesthetic responsiveness and creativity," N=748 Chinese university students. Source workbook (64 cols) bundles 3 named instruments back-to-back with blank "Unnamed" gap columns marking the boundaries — confirmed against the paper's abstract rather than guessed: Aesthetic Needs Scale (ANS, 18i, 1-6), Aesthetic Responsiveness Assessment (AReA, 12i, 1-5, includes a few creative-behaviour items like "sculpt/paint/write poetry/took an art class"), Williams Creative Tendency Scale (WCTS, 23i, 1-5). Source `序号` id column had 14 rows with NaN id holding garbage decimal junk values (9.6-87.1, clearly formula/summary artifacts from the bottom of the sheet) in one AReA item column — dropping NaN-id rows removes them cleanly and leaves exactly 748 unique ids, matching the paper's reported N exactly. `data/dou2025_aesthetics.py` → 3 tables (`dou2025_ans`, `dou2025_area`, `dou2025_wcts`).
- **Skip** — osf.io/zcdk8 ("How much can personality predict prosocial behavior?"), CC BY 4.0 (confirmed via UUID `563c1cf88c5e4a3877f9e96a` resolution). `data_ppp_benchmarking.csv` (N=2707, 82 cols) contains only precomputed composite scale scores (decimals/means across ~80 named personality/moral constructs — HEXACO, PID-5, narcissism, Machiavellianism, etc.), no id column, and no raw item responses — a benchmarking-analysis dataset by design, not item-response data. The 1.4GB `Analysis.zip` was not opened (near-certainly scripts/output given the file naming, and the codebook.html is a client-side-rendered R `codebook` package page with no greppable raw-item mentions).
- **Skip** (already resolved earlier this session, confirming here for the record) — figshare 29856026 ("Coaching leadership styles and athlete engagement..."), CC BY 4.0. Despite deceptively item-like column shape, file contains aggregate subscale means, not individual item responses.
- **Human review** — figshare 29486192 ("affect spin and prosocail behavior"), CC BY 4.0, anonymous authorship. 8-sheet Excel workbook (全部数据汇总.xlsx, N=400) — no findable paper (title has a typo, not indexed on Crossref) to confirm what the 8 sheets represent (separate measures? waves? mixed?), and subject ids only partially overlap between sheets ② and ③, not a clean join. Needs a person to open the file and `Appendix.doc` (may document the design) rather than another automated pass.

**Closed out 2026-07-15**: `dou2025_ans`/`dou2025_area`/`dou2025_wcts` uploaded to Redivis and biblio rows confirmed live in the dictionary sheet; the figshare 29486192 human-review row confirmed pasted into the "Human eye" sheet.

## Non-English source yield — anecdotal signal, no rigorous breakdown exists

Checked whether any per-language candidate counts exist in this log to answer "which non-English languages are producing the most results" — they don't. Every multilingual discovery run (batches 9, 13-17) only recorded a combined total across all 8 non-English languages per batch (e.g. "multilingual runs → candidates_batch15_intl1.csv (274, first 6 terms)") — the discovery script itself doesn't tag which language matched, so no reconstruction is possible from existing files without re-running queries language-by-language.

That said, real signal exists anecdotally from the alt-format (`.sav`/`.dta`/`.sas7bdat`/`.RData`) re-discovery and batch-11 work this session: of the datasets actually processed or seriously evaluated, Chinese-language sources dominate overwhelmingly — chen2022 (cls/ses/sasc), wu2021 (6 tables), chen2026 (mpa/sa/sc), shi2024 (ysq + 2 more), ma2026 (bsmas/sabas/igds), chen2025 (body_image, 4 tables), gao2025 (family_support, 5 tables), and now dou2025 (3 tables) — 8 of roughly 9-10 non-English-sourced datasets this session. The only other non-English instance was a single Malaysian/Malay dataset (skipped — aggregate data only). This is not a controlled measurement — it's biased by whatever the English search terms happened to surface as alt-format Chinese deposits — but it's a real, consistent pattern across ~16 independent triage decisions, not noise. If a genuine per-language yield estimate is wanted before committing to the full multilingual re-discovery, the clean way to get one is a small bounded pilot: run the same ~10-term sample already used for the alt-format pilot across each of the 8 non-English languages separately (not combined), and count candidates per language before triaging.
