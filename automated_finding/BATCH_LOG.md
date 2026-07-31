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

That said, real signal exists anecdotally from the alt-format (`.sav`/`.dta`/`.sas7bdat`/`.RData`) re-discovery and batch-11 work this session: of the datasets actually processed or seriously evaluated, Chinese-language sources dominate overwhelmingly — chen2022 (cls/ses/sasc), wu2021 (6 tables), chen2026 (mpa/sa/sc), shi2024 (ysq + 2 more), ma2026 (bsmas/sabas/igds), chen2025 (body_image, 4 tables), gao2025 (family_support, 5 tables), and now dou2025 (3 tables) — 8 of roughly 9-10 non-English-sourced datasets this session. The only other non-English instance was a single Malaysian/Malay dataset (skipped — aggregate data only). This is not a controlled measurement — it's biased by whatever the English search terms happened to surface as alt-format Chinese deposits — but it's a real, consistent pattern across ~16 independent triage decisions, not noise.

## Non-English per-language discovery pilot (2026-07-15)

Ran the bounded pilot proposed above: 11 general constructs (anxiety, depression, self-esteem, resilience, burnout, life satisfaction, emotion regulation, perfectionism, mindfulness, impulsivity, grit) translated into each of the 8 non-English languages, run **separately per language** (not combined) through `irw_discover_updated.py`, to get an actual per-language candidate count for the first time.

**Discovery-stage candidate counts:**

| Language | Candidates |
|---|---|
| German | 522 |
| French | 191 |
| Dutch | 174 |
| Spanish | 130 |
| Chinese | 114 |
| Japanese | 48 |
| Arabic | 6 |
| Korean | 0 |

German came out far ahead of Chinese despite Chinese being the anecdotal favorite from the alt-format work — the two questions (raw discovery volume vs. downstream alt-format triage yield) turned out to measure different things.

**Arabic and Korean investigated separately and confirmed not a pipeline bug**: live re-queries straight against Zenodo/OSF/Dataverse (bypassing our script) reproduced the same near-zero results for multiple different Korean terms across multiple sources, with correctly percent-encoded requests — these repositories' search indices just don't have meaningful Korean-language metadata to match against. Arabic technically returned 6 hits but all were false positives (Zenodo manuscript/grammar-text titles matching an Arabic-script substring, not datasets). Conclusion: not worth pursuing either language through these particular sources — this is a real property of the source repositories, not something fixable in our pipeline.

**Triaged the top 3 languages by yield (German, French, Dutch — 887 candidates total)**:
- `good`: 2 total, both low-value — one (`osf.io/ctnaq`) is already a known duplicate sitting in `license_blocked_candidates.csv`; the other (DVN/M7AFDM) is CC0 but only N=28/2 items.
- `human_assistance`: 72 total (45 de + 11 fr + 16 nl) — retriaged.
- Retriage `worth_retrying`: 4 unique candidates after dedup (a 5th, `osf.io/mqud7`, was already known). All 4 investigated:
  - figshare 32899694 (sports facilities/well-being) — skip, `aggregate_continuous`: a pre-computed CES-D score + covariates only, not items.
  - DVN/MTTFJR ("European Quality of Life" indicators) — skip, `not_item_response`: country-year macro indicators (GDP/governance/health indices), not person-level data.
  - DVN/HWMJAE (SWAN Depression/Lifestyle) — **human review**, logged to `automated_finding/human_review_lang_pilot.csv`: real longitudinal ordinal item data (N=2803, CC0, major cohort study), but its 4 depression items split into two different response-format groups, suggesting two different SWAN questionnaire modules bundled together — can't confirm the split from public metadata alone.
  - osf.io/dcqa6 (mindfulness dose-response RCT) — skip, `aggregate_continuous`: all 37 "items" are pre-computed subscale totals (BFI-2, PROMIS, K10, WEMWBS, FFMQ-15, DERS-SF, etc.), not raw items.
- Retriage `human_review` (31 rows: 18 de + 7 fr + 6 nl) — not yet worked; would need a person, same as every other `human_review` bucket in this pipeline.

**Bottom line**: triaging the 3 highest-yield non-English languages (887 discovery-stage candidates, the top end of what the other 7 languages combined would offer) produced **zero new processed tables** — one human-review candidate of uncertain final value, everything else duplicate/aggregate/macro/not-item-data. High discovery-stage volume (especially German's 522) did not translate into IRW-usable yield. Combined with Arabic/Korea's near-zero real yield, this doesn't support extending the alt-format-style re-discovery effort to the full ~1500 non-English historical terms — the marginal cost (per-language discovery + triage + retriage, each language behaving like its own mini-batch) doesn't look justified by what a bounded, honest pilot actually found. Chinese and Japanese (114 and 48 candidates, not yet triaged in this pilot) remain the most promising unexplored piece if there's appetite to check further, given Chinese's strong track record earlier in this session — but that's a smaller, more targeted follow-up than a full non-English re-discovery, not the original all-languages plan.

## User-directed fix: Portella 2022 racial norms dataset (2026-07-16)

User pointed directly at Harvard Dataverse `doi:10.7910/DVN/ZHCTCK` ("Racial
Social Norms among Brazilian Students...", PNAS 2022) and asked to pull/convert
it — bypassing discovery since the target was already named. Investigation found
it was **not actually new**: `racialsocialnormsbrazilianstudents_portella_2022`
already had rows in the live dictionary and tags Google Sheets (added
2025-12-15 by contributor Rubina Shrestha), plus a script at
`data/racialsocialnormsbrazilianstudents_portella_2022.R` — but no matching
table in `metadata.csv` (i.e. never actually uploaded to Redivis).

**Why it was never live**: the existing `.R` script was broken —
- read from a hardcoded personal path (`/Users/rubinashrestha/Downloads/data_11.csv`),
  not reproducible/self-contained;
- melted *every* non-id column into `item`/`resp`, including the paper's EFA
  composite scores (`score_racism`, `score_homophobia`, `score_self_esteem`,
  `scores_sdo_*`, etc. — aggregates, not raw items), demographic covariates,
  and even Portuguese text labels (`"Masculino"`) as if they were response
  values;
- recoded missing responses to a sentinel `"0"` string instead of dropping them.

**What's actually usable**: checked `CODEBOOK.pdf` — the release's composite
scores are EFA-derived from underlying survey items that were **not included**
in the release, only the derived scores were. The only genuine raw item-level
data is `q9`/`q12`/`q57`/`q60`: four statements about race relations sharing
one preamble and one 4-point agreement scale, answered by 3,431 of the 4,409
students. License confirmed CC0 1.0 via the Dataverse API.

**Fix applied**:
- Deleted the broken `data/racialsocialnormsbrazilianstudents_portella_2022.R`.
- Wrote `data/portella_2022_racial_attitudes.py` (self-contained, downloads
  `data_11.tab` directly from the Dataverse API, keeps only the 4 raw items +
  demographic covariates, drops missing rather than sentinel-coding) →
  `irw_output/portella_2022_racial_attitudes.csv` (rows=13724, ids=3431,
  items=4, resp=1-4).
- Renamed the table (old name was 50 chars, over the 40-char limit) and staged
  corrected dictionary/tags rows for the user to paste in, since this pipeline
  can't write to the Sheets directly: `dictionary_fix_portella_2022.csv`,
  `tags_fix_portella_2022.csv`. Also fixes two unrelated errors spotted in the
  live sheet row: the paper DOI had lost its leading digit
  (`0.1073/pnas.2117956119` — spreadsheet auto-number-formatting artifact) and
  "URL (for data)" pointed at the PNAS paper instead of the actual Dataverse
  dataset.

## Peters 2025 COVID-19 Risk Tool: DCT belief-item mapping (2026-07-16)

User pointed at GitHub issue #1093 (Peters et al. 2025, "Collecting
behavioural data across countries during pandemics: Development of the
COVID-19 Risk Assessment Tool", PNAS... Behav Res 57, 223) and asked for the
same treatment as the Portella fix earlier this session. Turned out to be a
much bigger undertaking than Portella, matching why ben-domingue had told the
collaborator on the issue to shelve it as "complicated" (2026-07-08 comment).

**License**: the issue thread recorded "CC-BY-NC-SA" from the GitLab repo
(`gitlab.com/a-bc/your-covid-19-risk`), which would normally be disqualifying
(NC blocks redistribution). Read the actual README directly: it states
standard copyright applies project-wide *except* R scripts (CC0) and
"`.csv` data sets... are anonymized, and as such, defined as facts and
existing in the public domain by definition." The NC-SA framing is the
aspirational license for the site/branding generally, not the actual data
files — recorded as "Public Domain" in the new dictionary rows rather than
the NC-SA the old placeholder rows used.

**Structure**: the raw data is 50 CSV exports across 21 LimeSurvey survey IDs
(sids) on `gitlab.com/a-bc/your-covid-19-risk-data`. Confirmed empirically
(diffing columns across sid-100101/100106/100121) that all 21 sids share
essentially the same ~577-585 column schema — one instrument fielded across
~21 countries/languages, not 21 different item sets, matching the source
repo's own bulk-loader script (`read--your-covid-19-risk--data.R`) which
`rbind`s all 50 files together. Also confirmed the raw `id` column resets to
1 within each sid (not globally unique) — built a composite id as
`f"{sid}-{orig_id}"` and verified uniqueness (102,917 rows, 102,917 unique
ids) before using it in any merge.

**Item mapping**: found the project's own LimeSurvey-generation build script
rendered at `your-risk.com/v1-translation-results-limesurvey` (their R
Markdown source, hosted as a GitLab Pages HTML dump). It documents the
answer-scale mechanism for the Reasoned Action Approach (RAA) belief items
that make up the bulk of the survey: each belief statement is `<Item>Seq`
(randomization-order slot — empirically confirmed non-response, holds
arbitrary integers 10-155, not a scale value), plus two scored sub-questions
(`Ex...`/`Ev...` or family-specific equivalents), each on a "uni" (1-5) or
"bi" (1-7) scale with code `0` = "don't know/NA" sentinel. Confirmed the
sentinel empirically too (`NrmDeIdFamily`, a "bi" item, has real `0.0` values
in the raw data). Extracted a validated polarity mapping for 276 of ~585
columns this way, covering seven belief-item families (`AttEx`, `AttIn`,
`Gen`, `NrmDe`, `NrmIn`, `PbcSk`, `PbcCn`) plus two small single-item scales
(`CIBERlite`, `gnrc`).

**Design decision confirmed with user**: for each family, the two components
(e.g. "Ex"=belief strength vs "Ev"=belief evaluation) measure different
psychological dimensions of the same statement, not the same scale twice —
split into separate output tables rather than combined. User confirmed:
"yeah keep them separate. ex and ev are different."

**Output**: `data/peters_2025_covid19_risk_dcts.py` downloads all 50 raw
files, builds the combined+deduplicated dataset, and produces 16 separate
IRW tables (`peters_2025_att_exp_strength`/`_eval`,
`peters_2025_att_instr_strength`/`_eval`, `peters_2025_gen_risk_strength`/
`_eval`, `peters_2025_nrm_desc_behavior`/`_ident`,
`peters_2025_nrm_inj_approval`/`_motivation`,
`peters_2025_pbc_skill_prob`/`_import`, `peters_2025_pbc_cond_power`/
`_presence`, `peters_2025_ciberlite`, `peters_2025_gnrc_beliefs`) — N ranges
from ~2,100 to ~40,000 depending on table (survey uses heavy randomization,
so most respondents only see a subset of items). One real bug caught during
QC: an initial date conversion (`datestamp` -> Unix seconds) was off by
1000x because pandas returned microsecond- not nanosecond-resolution
datetimes here — fixed with a unit-agnostic `Timedelta` division rather than
assuming a fixed divisor.

**Not done**: the remaining ~300 raw columns (demographic/intake covariates
are handled as `cov_*`, but a separate "risk estimate" family —
`siCurrent*`/`siIntention*`/`hwFrequency*`/`work*`/`DMQslider*` and their
paired `*Est` follow-ups — use a different checkbox-array + numeric-estimate
mechanism not yet reverse-engineered). Logged as a follow-up in `TODO.md`.

**Dictionary/tags**: the live sheets had 50 existing placeholder rows (one
per raw file chunk, e.g. `covid19risktool_peters_2025_100121-16198-16374`)
added 2026-07-01 by Rubina Shrestha — none of these match a real output
table and all need deleting. Staged 16 replacement rows in
`dictionary_fix_peters_2025.csv` and `tags_fix_peters_2025.csv` for the user
to paste in (per the standing rule that this pipeline can't write to the
Sheets directly).

**Resolution (2026-07-16)**: dug further on the license per user request — checked
`your-covid-19-risk-data`'s own README (has no license statement at all, purely
a pipeline description) and OSF's structured license field via API
(`node_license: null`). Re-read the site README's exact wording with the user:
the "public domain by definition" statement for `.csv` files is structurally an
explicit *exception* carved out from the repo's otherwise-unsettled copyright
state, not part of the hedge — more deliberate than a first read suggested, but
still a legal argument in a README rather than a formal license grant/badge.
**Decision: paused.** ben-domingue is emailing the authors directly for
explicit confirmation rather than relying on this reasoning alone. Dictionary/
tags rows are staged but not pasted; nothing uploaded to Redivis. Logged in
`license_blocked_candidates.csv` so this doesn't get lost. Resume once
permission or an explicit license comes back.

## Peters 2025 COVID-19 Risk Tool: license approved, walked through upload steps (2026-07-17)

Author permission came back. User asked to go through the remaining steps
slowly and separately rather than all at once.

**Step 1 (reproduce data)**: re-ran `data/peters_2025_covid19_risk_dcts.py` —
same 16 tables as the 2026-07-16 run (`peters_2025_att_exp_strength/_eval`,
`att_instr_strength/_eval`, `gen_risk_strength/_eval`, `nrm_desc_behavior/
_ident`, `nrm_inj_approval/_motivation`, `pbc_skill_prob/_import`,
`pbc_cond_power/_presence`, `ciberlite`, `gnrc_beliefs`), landed in
`irw_output/` for the user to inspect and upload to Redivis themselves.

**Step 2 (source)**: confirmed with the user this just meant the processing
script already sitting in `data/` — nothing further needed, already done in
the 2026-07-16 session.

**Step 3 (tags)**: caught a real error in the 50 stale placeholder rows while
drafting replacements — they tagged `primary language(s)` as `eng` only, but
pulling `startlanguage` from all 50 raw files directly showed the tool is
actually deployed in 20 distinct languages (eng, dut, ger, rum, tur, por, fra,
gre, ind, spa, ita, pol, heb, hun, jpn, kor, urd, amh, ara, chi) across its 21
country arms. Also switched `sample` from the placeholders' `Targeted/specific`
to `"Internet-based (Mturkers, etc)", General/non-specific` — the GitLab
README describes this as an open, self-selected public web tool, not a
recruited/targeted sample. Per the convention used for other multi-scale
datasets (`promis1wave1_*`, `pemaiw_qiu_2020_*`), gave each table its own
`construct name` (e.g. "Experiential Attitude — belief strength (RAA)")
rather than repeating the instrument name 16 times. User reviewed and
approved the draft. Wrote the 16 rows directly into `metadata/tags.csv` and
deleted the 50 stale `covid19risktool_peters_2025_*` rows in the same pass
(no separate `tags_fix_peters_2025.csv` staging file needed since this file
is repo-tracked, not a Sheet).

**Step 4 (dictionary)**: user gave three specific instructions — (1) verify
the live dictionary sheet's column format first, (2) reference the paper via
its shortDOI `doi.org/p3gf` in column E (APA reference) and F (raw DOI), (3)
use `ODbL 1.0` for both Original and Derived License. Confirmed the sheet's
column order via its CSV export (`table, table.lower, Description, URL (for
data), Reference, DOI (for paper), Original License, Custom License, Public
Reshare?, Derived License, Custom License, Notes, Contributor, Date`) and
that `"ODbL 1.0"` is the exact string already used for the `geography` table.
The shortDOI resolves to the same paper already on file
(`10.3758/s13428-025-02743-x`) — pulled the full author list from Crossref
(76 authors) to build a proper APA-7 reference (first 19 authors, ellipsis,
then final author, per the 21+-author rule). Staged 16 rows in
`automated_finding/dictionary_fix_peters_2025.csv` (Contributor=`automated`,
Public Reshare=`Public`, per-table Description mirroring the tags construct
names, URL (for data) = `https://gitlab.com/a-bc/your-covid-19-risk-data`)
for the user to paste in, replacing the same 50 stale placeholder rows in
the dictionary sheet.

**Closed out (2026-07-17)**: ben-domingue confirmed the dictionary rows are
pasted in, the 50 stale placeholder rows are deleted from both Sheets, and
the 16 `irw_output/peters_2025_*.csv` tables are uploaded to Redivis. Deleted
the now-redundant `dictionary_fix_peters_2025.csv` staging file. Only open
item left is the ~300-column risk-estimate follow-up, moved to `TODO.md`.

## Batch 18 — Conflict-task paradigm search (2026-07-17)

User is building an IRW vignette replicating Hedge, Powell & Sumner (2018)'s
"reliability paradox" (large, reliable group-level congruency effects but
weak individual-differences reliability for the incongruent-minus-congruent
difference score), currently using Hearts & Flowers, an alcohol-cue Stroop
(`alcoholstroop_jones2024.R`), and OSARI. Asked for a targeted search across
the conflict/interference-task paradigm family (Stroop variants, Flanker,
Simon, go/no-go, stop-signal, MSIT, dot-probe/attentional bias, Navon/
global-local, AX-CPT/CPT, task-switching, spatial S-R compatibility,
congruency effect/conflict adaptation, response inhibition).

**Discovery**: checked `search_terms_log.csv` first — Stroop, flanker task,
stop signal (task), inhibition, task switching, and go no-go task already
had partial entries from batches 5/8 (English + a handful of languages).
Simon task/effect, MSIT, dot-probe/attentional bias, Navon/global-local,
AX-CPT/continuous performance task, spatial stimulus-response compatibility,
congruency effect, conflict adaptation, and response inhibition task had
never been searched at all, in any language — 16 new English terms,
translated into the standard 8-language set (es/de/fr/zh/ja/ar/nl/ko) =
144 queries total, all logged in `search_terms_log.csv`. English run →
`candidates_conflict_en.csv` (729 candidates after auto-exclusion of the
861 IRW-dictionary DOIs); multilingual run → `candidates_conflict_intl.csv`
(499). Merged + deduped by doi/title → 946 unique; checked against
`irw_extract_evaluated_dois.py`'s BATCH_LOG-mined exclusion set (2 matches,
both irrelevant to conflict tasks — false-positive DOI collisions).

**Triage**: `irw_batch_updated.py` OOM-killed twice on the same candidate
(`10.7910/DVN/BRCRS5`, "Effects of Air Pollution on Students' Cognitive
Performance" — a large, unrelated Brazilian exam-records dataset that
spiked memory to ~19GB, presumably via a huge `.dta`/`.xlsx`; a false-
positive relevance match, not a conflict task) — dropped that one row from
the candidate pool and resumed from the checkpoint both times rather than
restarting. Final result on 945 candidates: 4 `good`, 51 `human_assistance`,
13 `not_item_response`, 6 `license_restricted`, 90 `download_failed`, 781
`no_usable_file`.

**The 4 `good` rows were all relevance-filter false positives** (soldier
ISR decision-making, Parkinson's gait kinematics, racism/BPD perceptions,
a Colombia household survey) — none are conflict tasks, none processed.

**Retriaged the 51 `human_assistance` rows** (`irw_retriage_ha.py` →
`irw_retriage_conflict.csv`): 8 not_item_response, 19 aggregate_continuous,
6 worth_retrying, 18 human_review. Investigated all 6 `worth_retrying` plus
every conflict-task-titled `human_review` row by hand:
- **osf.io/7vbtr** (Gyurkovics, Stafford & Levita, 2020, *JEP:General*,
  10.1037/xge0000698) — by far the strongest find. Bundles trial-level
  Flanker, Simon (both with `cong` 0/1 already coded), and SART/go-no-go
  data for N=118 adolescents/adults, fully documented via the node's
  `readme.txt`. Blocked purely on license — the OSF node has no license
  relationship set at all (checked via API) and the published paper doesn't
  itself grant a data license. Logged to `license_blocked_candidates.csv`
  (batch 18) with full contributor/ORCID detail — strong candidate for an
  author-permission email per `processing_notes/Licensing.txt`.
- figshare 32725962 ("Specific cognitive-balance interference... 2D Spatial
  Stroop tasks") — same dataset already documented as aggregate-only in
  batch 4's notes (dozens of files, all pre-aggregated per-condition
  error-rate/RT summaries); confirmed still true, not reprocessed.
- figshare 21708593 ("Emotional Stroop Task - English Version", CC BY 4.0)
  — downloaded and inspected: `EST in English.xlsx` is just the 128-word
  stimulus list (word/translation/valence), not participant data. Skip.
- figshare 1609723 ("The impact of induced anxiety on affective response
  inhibition", CC BY 4.0) — downloaded `OpenAccessDataset.sav`: per-subject
  aggregated RT/accuracy means by condition (N=114), not trial-level. Skip.
- figshare 13042430 ("Hypervigilance to dynamic and static facial
  expressions in social anxiety", CC BY 4.0) — downloaded
  `CompleteData_2021.xlsx`: per-subject, per-condition aggregate eye-tracking
  summary measures (%correct, fixation count/time by emotion×intensity),
  N=56-58, not trial-level. Skip.
- `10.7910/DVN/VOBQPR` ("Behavioral data of a combined flanker/stop signal
  task") — CC0, has a real `.tab` file that the triage script missed
  (filename `Online data available.tab` didn't match its file-type
  heuristics). Downloaded and inspected: per-subject condition-aggregate
  columns (CGoRT, ICSSRT, etc.), not trial-level. Skip.
- `10.7910/DVN/GINKMU` ("Stroop test dataset") — CC0, also missed by triage
  on the same filename heuristic. Downloaded `StrooptestQ.tab`: a ~700-column
  Russian-language multi-purpose child-development survey with what look
  like genuine trial-level Stroop latency/accuracy columns
  (`v1_NS_BELL_1_lat`...`_5_lat` etc., 2 waves) buried inside it, but no
  codebook or linked paper found to decode the abbreviation scheme safely.
  Logged to `human_review_conflict.csv` — needs a person with the source
  codebook, not another automated pass.

**Broader landscape note**: of the ~130 candidates whose titles matched a
conflict-task keyword, the overwhelming majority (91 `no_usable_file`, 90
`download_failed`) are PLOS ONE-style "S1 Table"/"Figure data" supplementary
files (pre-aggregated means/SDs/ANOVA tables, not raw responses) or landing
pages on access-controlled cohort platforms (`data.individualdevelopment.nl`
requires registration). This mirrors the pre-existing "IAT/reaction-time
data" dead-end pattern already noted in earlier batches — open, trial-level
conflict-task data is scarce in these repositories regardless of search
term; the Gyurkovics dataset is the one clear exception.

**Filename-heuristic gap found**: the triage script's `no_usable_file`
classifier missed at least 2 confirmed-real `.tab` files this batch because
their filenames didn't match its recognized-extension/naming heuristics
(`Online data available.tab`, and presumably others with generic names).
Not fixed here — flagging as a real, if minor, false-negative source for
whoever next tunes `irw_batch_updated.py`'s file-detection logic.

Temp files from this batch (`candidates_conflict_*.csv`, `discover_*.log`,
`triage_conflict*.log`, `irw_triage_conflict.csv`, `irw_retriage_conflict.csv`,
`downloads/*`) can be deleted once the license-blocked and human-review rows
above are confirmed captured — `human_review_conflict.csv` still needs
pasting into the "Human eye" sheet (see `TODO.md`).

**Follow-up (2026-07-17)**: ben-domingue confirmed they emailed the
Gyurkovics/Stafford/Levita authors requesting permission — noted in `TODO.md`
as awaiting response, nothing else changes until they reply.

## User-directed lead: Self Regulation Ontology project data (2026-07-17)

User pointed directly at the PNAS paper Enkavi, Eisenberg, Bissett, Mazza,
MacKinnon, Marsch & Poldrack (2019), "Large-scale analysis of test-retest
reliabilities of self-regulation measures" (10.1073/pnas.1818430116) and its
data-availability link — bypassing discovery, same pattern as the Portella
2026-07-16 fix. Confirmed via the paper's PMC record (PMC6431228) that the
canonical data source is
https://github.com/IanEisenberg/Self_Regulation_Ontology/tree/master/Data.

This is the single strongest candidate found so far for the conflict-task/
reliability-paradox vignette — the paper itself is a test-retest reliability
study of self-regulation tasks. `Data/Complete_02-16-2019/Individual_Measures/`
and the parallel `Data/Retest_02-16-2019/Individual_Measures/` each contain
trial-level long-format CSVs covering nearly the entire target paradigm
family: `stroop.csv.gz`, `simon.csv.gz`, `attention_network_task.csv.gz`
(flanker component), `go_nogo.csv.gz`, `stop_signal.csv.gz`,
`motor_selective_stop_signal.csv.gz`, `stim_selective_stop_signal.csv.gz`,
`local_global_letter.csv.gz` (Navon/global-local), `dot_pattern_expectancy.csv.gz`
(an AX-CPT variant), `threebytwo.csv.gz` + `shift_task.csv.gz` (task-
switching) — each with a matching Retest-sample counterpart, meaning this
dataset could support a genuine test-retest reliability analysis directly,
not just the group-effect side that Hearts & Flowers/alcohol-Stroop/OSARI
cover. Downloaded and inspected `stroop.csv.gz`, `simon.csv.gz`, and
`attention_network_task.csv.gz` directly to confirm structure: `worker_id`
(person id), `trial_id`/`trial_num`, `condition` (congruent/incongruent),
`correct`, `rt`, `exp_stage` (test/practice — filter to `test`) — e.g.
`stroop.csv.gz` has 50,112 test-stage trial rows across 522 workers, evenly
split congruent/incongruent. Would map cleanly to IRW's id/item/resp/
cov_condition schema per `datastandard.md`.

**Blocked on license**: no `LICENSE`/`LICENSE.md`/`LICENSE.txt` file on the
GitHub repo (checked via the GitHub API and direct raw-file probes, all
404), no license field on the repo itself, and no OSF companion project
found. The project is NIH-funded (Science of Behavior Change Common Fund,
NIDA UH2DA041713) and clearly intended for reuse given how thoroughly the
data release is organized and documented, but per this pipeline's standing
rule, intent to share isn't the same as an explicit open license — GitHub's
own policy treats a repo with no LICENSE file as all-rights-reserved by
default. Logged to `license_blocked_candidates.csv` (`user-directed` batch
row) with full structural detail. Found a real, non-guessed contact —
`zenkavi@stanford.edu` (A. Zeynep Enkavi, first author) — directly in the
PMC article page's HTML (PMC6431228), so an author-permission email per
`processing_notes/Licensing.txt` is very much worth sending; flagged in
`TODO.md` as the top-priority open item.

**Follow-up (2026-07-17)**: ben-domingue confirmed they emailed
zenkavi@stanford.edu requesting permission — `TODO.md` updated to "awaiting
response," nothing else changes until she replies.

## SRO conflict-task battery: license approved, processed (2026-07-17)

Author permission came back: the SRO dataset is released under CC BY.
Wrote `data/enkavi_2019_conflict_tasks.py` to process the 8
conflict/interference tasks relevant to the vignette (deferred the other
~50 SRO measures — surveys, n-back, discounting tasks, etc. — as out of
scope for this request).

**Design decisions**:
- Each task's `Individual_Measures/<task>.csv.gz` is fetched directly from
  GitHub raw for both `Complete_02-16-2019` (wave=1) and `Retest_02-16-2019`
  (wave=2) samples — `worker_id` is stable across both (confirmed 150/151
  retest workers also appear in the complete sample), giving a genuine
  test-retest structure per datastandard.md's wave convention.
- Filtered to `exp_stage=="test"` only (drops practice trials).
- **Item construction**: raw trial order/stimuli are randomized per
  participant, so there's no shared item bank to key items on directly.
  Built `item` as `"<condition-label>_<NNN>"` (e.g. `congruent_001`,
  `congruent_002`, ... `incongruent_001`, ...) where NNN counts occurrences
  of that condition-label within person+wave. This keeps id+item unique per
  wave and makes each task's `itemcov_*` column(s) exactly invariant within
  item, by construction — necessary since congruency/condition varies trial
  to trial, not by a fixed item identity.
- `resp` = trial accuracy (`correct`, 0/1 in the source; `go_nogo` and
  `threebytwo` stored it as bool — coerced explicitly, `pd.to_numeric`
  alone leaves bool untouched and later breaks on NaN assignment).
- **Sentinel caught in QC**: `dot_pattern_expectancy`'s `correct` column has
  a third value, `-1` (1787 of 66,816 test rows), paired with
  `key_press==-1` and `rt==-1` — a non-response/timeout, not "incorrect."
  The script's own summary-line QC step (`resp={min}-{max}`) caught this
  immediately (`resp=-1-1` on the first run) before it shipped — fixed by
  filtering `resp` to strictly `{0,1}`, dropping non-response rows entirely
  (both accuracy and rt are genuinely missing on those trials, matching how
  `go_nogo`/`stop_signal` non-response trials on nogo/stop trials already
  behave: rt<=0 with a real 0/1 accuracy value, which is different and
  correctly kept).
- `rt`: milliseconds → seconds; `<=0` (the same non-response sentinel
  pattern, e.g. `stop_signal`'s successfully-stopped trials, `go_nogo`'s
  correctly-withheld no-go trials) mapped to missing, row kept (accuracy is
  still meaningful with no RT).

**Output** (all in `irw_output/`, verified via a QC pass — unique
id+item+wave, no PII, `resp` clean 0/1, `rt` in seconds):

| table | rows | ids | items | source task |
|---|---|---|---|---|
| enkavi_2019_stroop | 64,608 | 523 | 96 | Stroop |
| enkavi_2019_simon | 67,300 | 523 | 100 | Simon |
| enkavi_2019_ant_flanker | 96,912 | 523 | 144 | ANT (flanker component) |
| enkavi_2019_gonogo | 235,550 | 523 | 350 | go/no-go |
| enkavi_2019_dpx_axcpt | 83,967 | 522 | 128 | dot-pattern-expectancy (AX-CPT) |
| enkavi_2019_navon | 64,608 | 523 | 167 | local/global letter (Navon) |
| enkavi_2019_stopsignal | 403,800 | 523 | 600 | stop-signal |
| enkavi_2019_taskswitch | 296,120 | 523 | 615 | three-by-two (task-switching) |

**Not yet done**: tags.csv rows, dictionary rows, and the Redivis upload
itself — same remaining steps as the Peters 2025 case above, deferred until
the user says how they want to proceed (that case was walked through "slowly
and separately" by request rather than all at once).

## SRO conflict-task battery: item redefinition + dictionary staging (2026-07-17)

**Item redefinition**: user reviewed the initial item-construction choice
(`"<condition>_<NNN>"`, a positional label) and asked for `item` to instead
be the actual stimulus combination, with a separate `position` column
holding the repetition index. Rewrote `data/enkavi_2019_conflict_tasks.py`
per-task:

- `stroop`: item = word × color (9 combos)
- `simon`: item = color × side × condition — condition has to stay in the
  key because the color-to-response-key mapping is **counterbalanced across
  participants** (confirmed empirically: the same stim_color+stim_side
  combination is "congruent" for about half the sample and "incongruent"
  for the other half, always consistent *within* a person). Every other
  task's congruency label is fully derivable from its stimulus columns.
- `attention_network_task`: item = cue × flanker_type × flanker direction ×
  flanker location (48 combos)
- `go_nogo`: item = condition × stimulus id (extracted via regex from a
  malformed-whitespace HTML stimulus string — `id = stim1` vs `id  =
  stim1` were spuriously producing 4 "distinct" strings for 2 real stimuli)
- `dot_pattern_expectancy`: item = condition × probe image id (24 combos;
  each row's `trial_id` is always `"probe"` — cue-phase rows aren't in this
  file at all)
- `local_global_letter`: item = attended level × global shape × local shape
  (12 combos; `conflict_condition` confirmed fully derivable from
  global_shape==local_shape)
- `stop_signal`: item = delay condition × trial type × shape id (16 combos)
- `threebytwo`: item = cue × digit × color × task_switch (288 combos) —
  used `cue` rather than `task` since 2 cues map to each task (confirmed
  1:1) and cue-vs-task-switch is the actual manipulation in this cued
  task-switching design

Added an explicit runtime assertion checking every `itemcov_*` column is
genuinely invariant within `item` (not merely assumed) — this is what would
have caught the Simon counterbalancing issue if it had been missed. All 8
tables pass. Row counts unchanged from the first version; only the
`item`/`position` keying changed.

**Dictionary rows staged**: `automated_finding/dictionary_fix_enkavi_2019.csv`
(8 rows, one per table) — matches the live dictionary sheet's column order
(verified via its CSV export) and follows the exact precedent already set
by the existing `alcoholstroop_jones2024` row for "source has no formal
license, author granted permission by email": `Original License` = "Missing
(NA)", `Derived License` = "CC BY 4.0", `Notes` = "email permission",
`Contributor` = "automated". Reference is the full 7-author APA citation
(PNAS 116(12):5472-5477).

**Closed out (2026-07-17)**: ben-domingue confirmed the dictionary rows
were pasted in and the 8 `irw_output/enkavi_2019_*.csv` tables are uploaded
to Redivis. Explicitly deprioritized tags.csv entries for now ("don't worry
about tags") — not done, and not currently tracked as an open TODO item;
revisit if/when the user wants it. This closes out the SRO conflict-task
battery lead end-to-end: discovered as a user-directed pointer, license-
blocked, permission granted, processed (8 tables), dictionary staged and
pasted, uploaded.

## Batch 19 — Cognitive/decision-making task discovery (2026-07-26)

**New search terms**: 10 topics not previously in `search_terms_log.csv`
(confirmed absent by grep before running), each in English + the standard
8-language set (Spanish, German, French, Chinese Simplified, Japanese,
Arabic, Dutch, Korean) = 90 queries, run together via
`candidates_cognitive_tasks_intl.csv`: Implicit Association Test, Raven's
Progressive Matrices, Posner cueing task, visual search task, digit span
task, reading span task, Iowa Gambling Task, Balloon Analogue Risk Task,
dictator game, Corsi block-tapping task. All 90 terms logged to
`search_terms_log.csv`. 649 candidates found.

**Pipeline hazard hit and worked around**: candidate #8 (Dataverse
`DVN/BRCRS5`, "Air Pollution and Students' Cognitive Performance") OOM-killed
`irw_batch_updated.py` twice in a row (confirmed via `journalctl -k`: both
attempts hit ~21GB RSS before the kernel OOM-killer stepped in on a 30GB
machine). The dataset's files are six `.dta` files up to 1.4GB each plus a
183MB `.tab` — `pandas.read_stata`/read on a file this size expands well
beyond the on-disk size in memory. Worked around by excluding that one row
(`candidates_cognitive_tasks_intl_safe.csv`, 648 rows) and resuming from the
existing checkpoint; the rest of the batch completed cleanly with no further
OOM. **Pipeline improvement worth considering** (not done, added to
`TODO.md`): `irw_batch_updated.py` has no file-size guard before attempting
to load a candidate file — a size check (e.g. skip/flag anything over ~200MB
per file without downloading fully first) would prevent this class of
failure automatically instead of requiring a human to notice the process
died silently.

**Triage summary** (`irw_triage_cognitive.csv`, 648 rows): good 2,
human_assistance 39, not_item_response 5, no_usable_file 511,
license_restricted 7, download_failed 84.

**Retriage summary** (`irw_retriage_ha_cognitive.csv`, 39 human_assistance
rows): not_item_response 9, aggregate_continuous 9, worth_retrying 6,
human_review 15 (0 wrong_file_selected, 0 recoverable_format).

**Both `good` rows turned out to be false positives on inspection** — the
triage tool's item-count heuristic doesn't distinguish real item batteries
from columns that happen to look like a small numeric grid:
- "Pre-test and post-test dataset of working memory in students with
  learning disabilities" (figshare 27141603, CC BY, N=40): the 9 "item"
  columns are all pre/post *composite test totals* (Visual/Verbal Memory
  Total Score, WMS Score, WM-PTF Score, Raven score) — aggregate, not
  item-level. Not processed.
- "Time as a medium of reward in three social preference experiments"
  (figshare/eur 14636322, CC BY, N=62): 9 Excel sheets, one per behavioral-
  economics game variant (Dictator/Ultimatum/Trust Game at two endowment
  levels, plus money-only controls) — each subject makes a single game
  decision per sheet with demographic covariates alongside it, not a battery
  of comparable items. Not processed.

**Of the 6 `worth_retrying` cases, 4 were dropped and 2 reclassified to
human_review** (details in `human_review_cognitive_tasks.csv`, appended to
the 15 rows the automated retriage couldn't resolve — 17 rows total):
- Dropped (all aggregate/composite scores or not item-response data, same
  pattern as the two "good" false positives above): "Working Memory
  Training in Healthy Adults" (figshare 3121582, N=81 — pre/post digit-span/
  RAPM/CCFT/coding *totals*, no items); "The explicit-implicit personality
  relationship study" (UCL RDR 22202371, CC0, N=1458 — IAT D-scores and
  TEIQue subscale totals, no items); "Mapping indicators of food security...
  Senegal" (DVN/YYJJHN, N=296 "participants") — turned out to be a pure GIS/
  remote-sensing agroforestry dataset (rasters, land-cover, InVEST ecosystem-
  service model outputs); the triage tool's participant/item counts came
  from an incidental small `.tab`/`.csv` file with no survey data at all;
  "Do Gender-Related Stereotypes Affect Spatial Performance? ... Mental
  Rotation Task" (Frontiers/figshare 6854201, CC BY, N=76) — per-condition
  (Neutral/Male-optimized/Female-optimized) summary stats (%%correct, mean
  latency, confidence), not trial-level responses.
- Reclassified to `human_review` (real data, but doesn't safely fit the
  automated schema): "Nosek and Smyth (2011): Implicit social cognitions
  predict math engagement and achievement" (DVN/Z3MV4J, CC0, N=11,819) — a
  186-column `.sas7bdat` mixing IAT block key-assignment metadata (e.g.
  `PanxB3` values are strings like `"MATH/Anxious,FURNITURE/Confident"`, not
  responses) with raw latencies and self-report items across 5 sub-IATs;
  needs the paper's PDF codebook to safely separate real Likert columns from
  task metadata. "Ideological Cues, Partisanship, and Prejudice Against
  LGBTQ Judges" (DVN/CDLVDH, CC0, N=1,249) — a genuine conjoint experiment
  (2 randomized judge-nominee profiles per respondent, 5-point support
  rating each) that maps cleanly to `id`/`item`(profile_1/profile_2)/`resp`,
  but its natural `itemcov_*` candidates (the 9 randomized judge attributes:
  age/race/law school/job/politics/gender/transgender status/sexuality/
  rhetoric) are randomized **per response**, violating datastandard.md's
  itemcov invariance rule (itemcov must be constant within an item across
  all rows). A draft processing script was written and then deliberately
  discarded rather than shipped with a schema violation — flagged for a
  person to decide whether to ship a bare `id`/`item`/`resp`/`cov_*` file
  (losing the conjoint attribute detail) or treat conjoint designs as out of
  scope for IRW's shared-item psychometric paradigm.

**Net result this batch**: 0 new tables in `irw_output/` — every `good` and
`worth_retrying` lead turned out to be aggregate/composite data, non-survey
data, or a genuine schema mismatch on closer inspection. This is a real
(if unexciting) outcome, not a missed opportunity: the search successfully
surfaced candidates worth checking, and checking them thoroughly (rather
than trusting the triage tool's flag) is what caught the false positives.

**Cleanup**: `candidates_cognitive_tasks_intl.csv`,
`candidates_cognitive_tasks_intl_safe.csv`, `irw_triage_cognitive.csv`,
`irw_retriage_ha_cognitive.csv`, `irw_batch_checkpoint.jsonl`,
`triage_cognitive_run.log` deleted — content captured above.
`human_review_cognitive_tasks.csv` (17 rows) kept pending user paste into
the "Human eye" sheet; tracked in `TODO.md`.

## Batch 20 — Well-being/clinical-screening instrument discovery (2026-07-26)

**New search terms**: 10 named instruments not previously in
`search_terms_log.csv` (confirmed by grep before running, since several
adjacent-sounding terms like "life satisfaction" or "PTSD" already existed
but these exact instrument names did not): Perceived Stress Scale, UCLA
Loneliness Scale, Multidimensional Scale of Perceived Social Support,
Buss-Perry Aggression Questionnaire, Domain-Specific Risk-Taking Scale,
Problem Gambling Severity Index, Barratt Impulsiveness Scale, Maslach
Burnout Inventory, Satisfaction with Life Scale, Alcohol Use Disorders
Identification Test — each in English + the standard 8-language set
(Spanish, German, French, Chinese Simplified, Japanese, Arabic, Dutch,
Korean) = 90 queries, run together via `candidates_batch20.csv`. All 90
terms logged to `search_terms_log.csv`. 1,023 candidates found.

**Pipeline hazard hit again, same class as batch 19**: candidate
`DVN/EHBGOW` ("Taking Teacher Evaluation to Scale...") OOM-killed
`irw_batch_updated.py` at row 652/1023 (confirmed via `journalctl -k`: 21GB
RSS on a 30GB machine). Checked the Dataverse file listing directly this
time before resuming: six `.dta` files up to 1.58GB each. Excluded that one
row (`candidates_batch20_safe.csv`) and resumed from the checkpoint; the
rest completed cleanly. This is now the second batch in a row hitting this
exact failure mode — reinforces the open `TODO.md` item for a file-size
guard in `irw_batch_updated.py` (still not implemented).

**Triage summary** (`irw_triage_batch20.csv`, 1023 rows): good 2,
human_assistance 67, not_item_response 7, no_usable_file 835,
license_restricted 7, download_failed 102, error 3.

**Both `good` rows were false positives on inspection**, same pattern as
batch 19 — the triage heuristic counts columns without checking they form a
shared item bank:
- Marathi translation-equivalence pilot for MSPSS/PSS (figshare 25888477,
  CC BY 4.0, N=10) — 12 items rated twice (self vs. interview method) by only
  10 raters, plus aggregate total/mean/difference columns. Too small and a
  translation-validation pilot, not a substantive response dataset. Not
  processed.
- "Questionnaire and Interview Results" (DVN/NTVW8T, CC0, N=150, 181
  nominal "items") — a Philippine/Chinese secondary-school language-program
  survey: open-text policy questions, per-grade checklists, administrative
  headcounts. No shared Likert item battery. Not processed. (Note: this DOI
  was listed with a bare, unannotated checkmark in this file's original
  batch-3 audit section — re-confirmed here from scratch since the dictionary
  itself was checked live via `irw_discover_updated.py`'s auto-exclusion and
  this DOI was not excluded, meaning it was never actually uploaded.)

**3 of 3 `worth_retrying` cases panned out this time** (unlike batch 19,
where all 6 were dead ends) — all inspected directly rather than trusting
the retriage tool's guess:
- `DVN/DWCBOE` ("Need Fulfillment Inventory for Older Adults... University
  of the Third Age", Trusz 2025, CC0) is a multi-file scale-development
  deposit (EFA N=660, CFA N=437, retest N=54, combined N=1097). The
  retriage tool flagged the combined N=1097 file's dup_id_item ratio as
  possibly longitudinal; direct inspection showed that file mixes 3
  incompatible sub-studies with an unreliable `KOD` id (constant/blank for
  660 of 1097 rows) and duplicate-valued "retest" columns that turned out to
  be mean-imputed copies (`PO_IMPUTACJI` = "after imputation"), not a second
  wave — not usable as-is. The EFA-only file (`EFA_NFI72_N660.sav`) is clean
  though: `lp` is a genuine unique id (660/660), `i1`-`i72` are the real
  NFI-72 items (1-5 Likert, ignore the `i*_1` imputed-duplicate columns and
  the `@`-prefixed raw-text columns and the `*_SUM`/`*_SR` subscale
  aggregates). Processed as `trusz_2025_nfi.py` → `trusz_2025_nfi.csv`
  (659 ids after dropping one all-missing row, 72 items, resp 1-5). CFA and
  retest subsamples not processed — left as a note in the dictionary row for
  anyone who wants to pick them up later.
- Gan et al. (2015), "Rumination and Loneliness... Chinese Elderly in
  Nursing Homes" (figshare 1535084, CC BY 4.0, N=71) — the retriage tool
  flagged a low-confidence id mapping; `num` is in fact a clean unique id.
  Real CES-D (20 items, 0-3), UCLA Loneliness short form (8 items, 1-4), and
  RRS (10 items, 1-3, numbered 1,2,4-11 — the source already excludes item 3)
  all present. Processed as `gan_2015_nursing_home.py` → 3 tables
  (`gan_2015_cesd`, `gan_2015_ucla_loneliness`, `gan_2015_rrs`).
- Chen, Ji & Jiang (2022), "Psychological Abuse and Social Support in
  Chinese Adolescents" (figshare 19410062, CC BY 4.0) — retriage flagged a
  4.1x dup_id_item ratio as possibly longitudinal; direct inspection showed
  `number` instead resets across respondents (same participant number maps
  to different ages/genders across rows — same false-longitudinal pattern as
  earlier batches' "number resets per class" cases), so used row index as
  `id` instead per datastandard.md, giving 417 real respondents. Three
  scales: parental psychological abuse (14 items, 1-5), MSPSS-style social
  support (12 items, 1-7), Rosenberg-style self-esteem (10 items, 1-4).
  Caught one data-entry sentinel (a single `22` in an otherwise 1-4 item)
  via the `resp` range filter before shipping. Processed as
  `chen_2022b_adolescents.py` → 3 tables (`chen2022b_psychabuse`,
  `chen2022b_socsupport`, `chen2022b_selfesteem`). Named with a `b` suffix
  because the first author's surname ("Chen Chen") collides with the
  unrelated existing `chen2022_cls/ses/sasc` batch-7 entry (different paper,
  different figshare DOI, same author name) — flagging here so the
  collision doesn't look like a duplicate-processing mistake later.

**Net result this batch**: 7 new tables in `irw_output/` across 3 datasets
(`trusz_2025_nfi`, `gan_2015_cesd`/`ucla_loneliness`/`rrs`,
`chen2022b_psychabuse`/`socsupport`/`selfesteem`) — all CC0/CC BY, verified
id uniqueness, no PII, no dup id+item, resp ranges matched documented
scales. Dictionary rows staged in
`automated_finding/dictionary_fix_batch20.csv` (7 rows), not yet pasted.

**7 `license_restricted` rows** (all explicit NC/ND-family licenses —
cc-by-nc, cc-by-nc-nd, cc-by-nc-sa — not a missing/unresolvable-license
case, so not added to `license_blocked_candidates.csv`; that file is
reserved for missing/unverifiable licenses, not deliberately-restrictive
ones): Kenya Diet Quality Questionnaire ×2, Social Capital Integrated
Household Questionnaire, air pollution/cognition Kenya replication data,
stress/trauma/family-resilience child outcomes, VR height-perception
self-esteem study, mindfulness/self-compassion/perfectionism Hong Kong
gifted-adolescents study — all skipped outright, no email-permission attempt
(NC/ND is a deliberate restriction stated by the depositor, not an
oversight worth appealing).

**18 `human_review` rows** — generic "no clear automated classification"
cases the retriage tool couldn't sub-classify further; saved to
`human_review_batch20.csv`, needs pasting into the "Human eye" sheet.

**Cleanup**: `candidates_batch20.csv`, `candidates_batch20_safe.csv`,
`irw_triage_batch20.csv`, `irw_retriage_batch20.csv`,
`irw_batch_checkpoint.jsonl`, `discover_batch20.log`, `triage_batch20.log`,
`triage_batch20_resume.log`, `triage_test20.csv` deleted — content captured
above. `human_review_batch20.csv` and `dictionary_fix_batch20.csv` kept
pending user paste into the sheets.

**Closed out (2026-07-26)**: ben-domingue confirmed both
`human_review_batch20.csv` (18 rows) and `dictionary_fix_batch20.csv` (7
rows) were pasted into their respective sheets; both files deleted from the
repo. ben-domingue also confirmed the 7 `irw_output/*.csv` tables
(`trusz_2025_nfi`, `gan_2015_cesd`/`ucla_loneliness`/`rrs`,
`chen2022b_psychabuse`/`socsupport`/`selfesteem`) are uploaded to Redivis.
This closes out batch 20 end-to-end.

## PLOS ONE pilot (2026-07-26) — new source: single-journal search via Supporting Information files

**What this is**: a different discovery mode, not a numbered batch of
`irw_discover_updated.py`. All of that script's connectors query data
*repositories* (Dataverse/Zenodo/OSF/Dryad/Figshare/DataCite/...) for
dataset-shaped records. PLOS ONE papers instead attach their raw data
directly to the article as "Supporting Information" files — those are
structurally invisible to every repo-based connector, since the data was
never deposited in any of those systems. New script: `irw_discover_plos.py`.
It queries PLOS's own Solr search API (`api.plos.org`, filtered to PLOS
ONE's eissn `1932-6203` so it's robust to the "PLoS ONE"/"PLOS ONE" naming
drift in their own metadata), then for each candidate DOI fetches the
article page, reads the Data Availability statement, and pulls any
Supporting Information file with a tabular-looking declared format
(CSV/XLSX/XLS/SAV/DTA) — same `triage_dataset()`/`load_table()` content and
format gate the regular pipeline uses, no separate scoring logic. It also
captures any external-repo DOI mentioned in the Data Availability statement
(even bare, unlinked DOIs like `doi: 10.5061/dryad.xxxx`) so a lead pointing
back into Dryad/OSF/etc. isn't lost.

**Pipeline fix found during this pilot**: `pyreadstat`'s native `.sav`
parser can segfault outright on a corrupt file — a C-level crash, not a
catchable Python exception, so a bare try/except around the per-candidate
processing step doesn't protect a long unattended run (confirmed: the first
full-batch attempt died at 168/~3000 candidates, taking the whole run down
with it). Fixed by isolating each candidate in its own worker process
(`ProcessPoolExecutor(max_workers=1)`, respawned on crash/timeout) — a
crashed worker is now recorded as a `crashed` row and the batch continues.
Also added `--resume` (skip DOIs already in `--out`). Same segfault risk
likely exists in `irw_batch_updated.py`'s `.sav` path for the regular
pipeline; not yet ported there.

**Also fixed**: `xlrd` wasn't installed, so every old-style `.xls`
Supporting Information file failed with `download_failed` instead of being
read. Installed (`pip3 install --user --break-system-packages xlrd`) —
recovered 5 of 7 affected candidates in a spot-check. Worth adding to
`SKILL.md`'s prerequisite-check list alongside pandas/openpyxl/pyreadstat/pyreadr.

**Run**: 22 terms (named instruments + constructs spanning depression,
anxiety, personality, stress, burnout, cognitive/executive-function tasks),
restricted to PLOS ONE — `search_terms_log.csv` updated (logged separately
from `irw_discover_updated.py`'s terms since a term's coverage doesn't
transfer between sources). 2,996 unique candidates after dedup against the
IRW dictionary (pulled fresh at run start).

**Triage result**: 2,325 `no_usable_file` (77.6%), 546 `human_assistance`
(18.2%), 57 `not_item_response`, **32 `good`**, 26 `download_failed`, 8
`error`, 1 `crashed`, 1 `timeout`. License: 2,527 `cc-by`, 60 `cc0`, 407
`unknown` (parse misses on the copyright-notice extraction, not actual
non-open licenses — 0 `license_restricted` rows; PLOS ONE's license is
uniformly open), 2 blank. Nothing added to `license_blocked_candidates.csv`
— no candidate was dropped purely for license reasons.

**Retriage on the 546 `human_assistance` rows** (`irw_retriage_ha.py`, no
changes needed — same column shape as the regular pipeline's output):
**107 `worth_retrying`**, 184 `human_review`, 159 `aggregate_continuous`
(drop), 94 `not_item_response` (drop), 2 `recoverable_format`.

**Duplicate check**: re-pulled the IRW dictionary fresh and checked all 32
`good` DOIs against `DOI (for paper)` — 0 exact matches. Re-checked again
after the first 6 were written to `irw_output/` — still 0.

**License verification for Supporting Information files specifically**
(distinct question from the article's own license): PLOS's Licenses and
Copyright policy states CC BY 4.0 applies to "articles and other works we
publish" (not narrowly "the PDF/HTML body"), and Crossref registers each SI
file's own DOI as `is-component-of` the parent article DOI — i.e. PLOS
structurally treats SI files as part of the same published work, not an
independent third-party deposit with its own separate terms (which is the
case for data availability statements pointing to an *external* repo
instead — those still need their own per-repo license check, same as the
regular pipeline already does). No single sentence found stating literally
"Supporting Information files are CC BY" — this is inferred from the two
points above, not a first-party stamped label the way an external repo's
API returns an explicit license field. Judged sufficient to satisfy the
"explicitly and verifiably open, confirmed on the source page" bar, but
flagging the inference so it's not confused with a repo API's direct
license field.

**First pass of the 32 `good` candidates** — 6 processed by hand rather
than blindly trusting the triage flag (see `datastandard.md`'s "still needs
a human glance" note):
- `muslih_2024_rses` (260p×10i), `jiang_2021_resilience` (952p×17i, itemcov_dimension
  for the 4 subscale groupings; 4 stray `0` values dropped as data-entry
  errors — 1-2 occurrences per item vs. hundreds at 1-5, and the other 14
  items never take 0), `kinyanjui_2023_substance_use` (400p×12i binary
  checklist; dropped 5 Big Five subscale SUM columns also in the raw file
  — aggregates, not items), `wilson_2022_kelpie_personality` (228p×18i,
  owner recorded as `rater` since the dog, not the owner, is the focal
  unit), `rashid_2022_mbi` (168p×22i — **caught a wrong-file selection**:
  the article has 4 SI files; S1/S4 hold only derived MBI subscale totals,
  which is what the automated triage grabbed; S2/S3 hold the real 22 raw
  items, used instead), `yin_2022_gad7` + `yin_2022_values_importance`
  (153p×7i / 153p×13i — one raw file held two distinct scales, split per
  the one-scale-per-file rule).
- **Skipped** 2 candidates despite a `good` triage flag: the PANAS/social-
  functioning paper (SI's only affect column was a Positive Affect
  composite sum, not raw items) and the dietician intention-to-quit paper
  (heterogeneous single-question professional survey, not a coherent
  multi-item instrument).
- Biblio entries for the 6 processed → `biblio_plos_batch1.csv` (7 rows;
  Yin split into 2 tables). `human_review_plos_batch1.csv` (184 rows)
  ready to paste into the "Human eye" sheet.
- Remaining: 26 more `good` candidates + 107 `worth_retrying` still to
  review by hand.

**Continued same day**: 6 more `good` candidates processed by hand (12
total now):
- `kraft_todd_2017_*` (4 tables: competence, warmth, care_measure, panas —
  physician nonverbal-empathy experiment, 1377p, 4 sub-studies pooled, two
  crossed binary conditions kept as covariates not `treat`).
- `song_2023_*` (3 tables: rses, slwai, mpats — Chinese medical students,
  1238p).
- `di_riso_2025_*` (2 tables: mask_emotion, contact_behavior — large
  Italian sample, 1151p; dropped several single-item questions and PID-5-BF
  aggregate sums from the same raw file).
- `iwasa_2016_*` (4 tables: dpssr, padua_inventory, asi, stai_trait —
  Japanese sample, 481p, 112 items total across 4 validated instruments).
- `hui_2024_*` (3 tables: gbfs, who5, pss10 — Chinese college students,
  309p).
- `liu_2018_*` (5 tables: swls, shyness, panas, gse, lot_r — Chinese
  working adults, 208p; raw file also had a second set of SEM item-parcel
  columns, confirmed as averaged composites via fractional values and
  excluded).
- Also reviewed and **skipped** the "Network study of responses to
  unusualness" candidate (pone.0246894, 1500p×6i) — all 6 columns in the SI
  file are subscale SUM scores (ranges like 9-45), no raw items available
  at all.
- `biblio_plos_batch1.csv` now has 28 rows total. Duplicate-checked all new
  DOIs against a freshly-pulled dictionary (2273 rows) — 0 matches.
- **Redivis/dictionary status, confirmed by ben-domingue (2026-07-26)**:
  the first 7 tables (muslih/jiang/kinyanjui/wilson/rashid/yin×2) are
  uploaded to Redivis and their biblio rows are pasted into the dictionary
  sheet. The other 21 tables (rows 8-28) are not yet uploaded/pasted.
- **File-loss incident**: mid-session, an in-place append to
  `biblio_plos_batch1.csv` silently reverted to just the appended content
  (lost the original 7 rows — caught and fixed by reconstructing the full
  file), and separately the 7 already-uploaded `irw_output/*.csv` tables
  disappeared from disk with no git record. `automated_finding/` lives in a
  Dropbox-synced folder — most likely explanation is a sync event from
  another device, not a bug in the processing scripts (all `data/*.py`
  scripts were untouched and regenerated their output cleanly on rerun).
  Noted in `TODO.md` as a standing caution for this working directory.
- Remaining: ~20 more `good` candidates + all 107 `worth_retrying` still to
  review by hand.

**Continued same day**: 3 more `good` candidates processed (15 total, 34
tables):
- `uffler_2017_*` (2 tables: lecture_seating 26-item 1-7 Likert, seat_reasons
  7-item binary multi-select checklist — health sciences students, 593p).
- `nabwera_2021_bdi` (1 table, 20 items — BDI-II embedded inside a ~90-column
  menstrual-hygiene-management survey in rural Gambia; only the BDI-II block
  is a coherent scale, rest excluded as heterogeneous single-question items).
- `lu_2017_*` (3 tables: phq9, gad7, pss10 — Chinese university students).
  **Notable recovery**: the article has 2 SI files; automated triage only
  found S1 (retest subsample, N=129) and flagged it `good` on that basis.
  Manual review found S2 (main sample, N=1296) and confirmed via exact-set
  overlap that all 129 S1 ids are a subset of S2's — a genuine 2-wave
  design, not a duplicate/separate dataset. Combined into `wave` 1
  (main)/2 (retest), recovering 10x the participants the triage flag alone
  would have suggested. One data-entry error (-1 on a 0-4 scale item)
  caught and dropped.
- `biblio_plos_batch1.csv` now 34 rows; `irw_output/` now 34 files — counts
  cross-checked and match. All new DOIs re-checked against a freshly-pulled
  dictionary (2273 rows), 0 duplicates.
- Two of the 5 items rechecked against source data mid-session, as a spot
  QC pass at the user's request: `hui_2024_who5`'s `resp=0` values (1-12
  occurrences per item, all 5 items) confirmed genuine — WHO-5's own scale
  is 0-5, unlike the earlier jiang/lu cases where a lone out-of-range value
  was a data-entry error.
- Remaining: ~17 more `good` candidates + all 107 `worth_retrying` still to
  review by hand.

**Closed out (2026-07-26)**: ben-domingue confirmed all 34 tables from this
first pass (the initial 7 + the following 27) are uploaded to Redivis and
their biblio rows pasted into the dictionary sheet. `biblio_plos_batch1.csv`,
`biblio_plos_batch1_remaining27.csv` (the 27-row split-off prepared for this
paste), and all 34 `irw_output/*.csv` files deleted from the repo — the 27
files had already vanished from disk by the time of cleanup, consistent with
this being a Dropbox-synced folder (see `TODO.md`'s standing note) rather
than anything left to actually delete. The 9 `data/*.py` scripts remain in
place and are re-run to regenerate any of these tables if ever needed. This
closes out the first pass of the PLOS ONE pilot end-to-end — 15 `good`
candidates processed, 34 tables. ~17 more `good` candidates and all 107
`worth_retrying` candidates remain open (tracked in `TODO.md`), along with
`human_review_plos_batch1.csv` (184 rows, not yet pasted).

**human_review_plos_batch1.csv closed out (2026-07-26)**: the file had
disappeared from disk (same Dropbox-sync pattern noted above) by the time
it was needed for a DOI spot-check; regenerated deterministically from
`plos_full_retriage.csv` (same 184 rows, same order — verified the
regenerated last row's DOI, `10.1371/journal.pone.0273327`, against what
ben-domingue had on hand before it was pasted). ben-domingue confirmed all
184 rows pasted into the "Human eye" sheet; file deleted from the repo.

**Second pass on `good` candidates (2026-07-26)**: 5 more processed (9
tables) → `biblio_plos_batch2.csv`:
- `zhu_2024_pyd` — **largest single table in the pilot**: 41-item Positive
  Youth Development Scale, 2 waves, N=4060 (284,194 rows). Raw file also
  had B1-B3/SB1-B3 columns confirmed to be IRT theta-scores rather than
  raw items (each takes exactly 7 values evenly spaced by 5/6 -- the
  signature of a theta-transform on a 3-item raw-score table), excluded.
- `boni_2018_mbi_ss` — MBI-Student Survey, 15 items, N=270 (of 281; 99 used
  as a consistent missing sentinel).
- `bang_2023_*` (5 tables: health, depression, anxiety, self_esteem,
  parenting_stress) — quasi-experimental wellness program, N=37, confirmed
  scale groupings via the raw file's own "Data dictionary" sheet.
- `luu_2024_stai6` — STAI-6, N=359, text-coded responses parsed.

Also reviewed and **skipped** 4 more `good`-flagged candidates, all
confirmed to have no raw item-level data at all despite passing the
automated triage:
- pone.0246894 ("Network study... unusualness") — 6 columns, all subscale
  SUMS (already logged in the first pass).
- pone.0258752 (cognition-targeted exercise) — entirely composite outcome
  scores at 3 timepoints × 2 groups × 4 scales; no item columns anywhere.
- pone.0199118 (mobile depression self-rating) — single sheet of algorithm
  scores/cutoffs/PHQ9 total; other 2 sheets in the workbook are empty.
- pone.0253779 (altered states) — Tellegen Absorption + NEO-FFI-2 factor
  TOTALS only, no raw items.
- pone.0238022 (spatial working memory) — S1 has real per-condition
  performance data but only 14 unique subjects (112 = 14 subj × 8
  conditions, not 112 participants as the triage's `n_participants`
  implied); S2 is fMRI ROI activation data, out of scope. Judged too small
  (N=14) to be worth the schema-fit work, deferred rather than processed.

**Good list closed out (2026-07-26)**: reviewed all 6 remaining small
candidates.
- `makowska_2023_*` (2 tables: pss4, pdts) — Digital Transformation Stress
  Scale paper. Article has 2 SI files (S1 N=229, S2 N=558); used S2, the
  larger sample. Polish text-coded responses parsed.
- `alkouri_2025_*` (2 tables: icu_stressors 29 items, coping 19 items) —
  **another triage miscount**: flagged `n_items=1`, actually has 2 real
  multi-item scales the automated melt entirely missed. Raw file also had
  `Name`/`Email` columns (real PII — Email 127/127 non-null) dropped
  entirely; item column names were full sentences, mapped to
  `item_01..item_NN` with the mapping preserved as ordered lists in the
  script. "Barely"/"Rarely" used interchangeably as the 2nd-lowest
  frequency category across different items (verified never both within
  one item) and mapped to the same value.
- pone.0279255 (school value-added scores) — **skipped**: confirmed
  school-level aggregate rankings, `id` would be a school not a person,
  not item-response data at all.
- pone.0275045 (patient feedback) — **skipped**: confirmed a systematic-
  review study-coding table (methodological metadata about other papers),
  not survey responses from participants.
- pone.0254922 (surgical resident QI, N=14 after removing an embedded
  Qualtrics question-text row that the automated read had counted as a
  data row) and pone.0147008 (couples synchrony, N=10) — inspected (both
  structurally valid: 0254922 has real Q7/Q1 11+10-item scales with
  standard 4-point response formats) but **not processed**, per
  ben-domingue: too small to be worth it.

All 32 originally-flagged `good` candidates have now been reviewed by
hand. Final count: **21 candidates processed → 46 tables**, **11 skipped**
(confirmed aggregate-only, not item-response data, or too small: PANAS/
social-functioning composite, dietician heterogeneous survey, "network
study" unusualness composites, cognition-targeted-exercise composites,
mobile-depression algorithm scores, altered-states composites, spatial-WM
N=14 fMRI companion, school value-added rankings, patient-feedback
systematic-review coding table, surgical-resident QI N=14, couples
synchrony N=10).

**`good` list closed out end-to-end (2026-07-26)**: ben-domingue confirmed
the remaining 12 tables (`biblio_plos_batch2.csv`: zhu_2024_pyd,
boni_2018_mbi_ss, bang_2023 ×5, luu_2024_stai6, makowska_2023 ×2,
alkouri_2025 ×2) uploaded to Redivis and pasted into the dictionary sheet,
joining the first 34 closed out earlier. `biblio_plos_batch2.csv` and all
12 `irw_output/*.csv` files had already disappeared from disk by the time
of cleanup (same Dropbox-sync pattern noted in `TODO.md` — nothing left to
actually delete). The full `good` list — all 32 candidates, 46 tables from
21 of them — is now fully processed and closed out. Remaining open item:
all 107 `worth_retrying` candidates.

## `worth_retrying` pass, first batch (2026-07-26)

At ben-domingue's direction, filtered the 107 `worth_retrying` candidates
to N≥100 (81 remain) before starting hand review — the sub-100 tail is
deprioritized, not abandoned (still in `plos_full_retriage.csv`).

7 candidates reviewed, 5 processed → 14 tables (`biblio_plos_batch3.csv`):
- `wurm_2016_*` (hbi 40 items, mdi 10 items) — German physicians, N=5897.
  Retriage flag was a low-confidence id mapping; id was actually fine.
- `ye_2025_*` (3 tables, 9/10/13 items) — Chinese university students,
  N=4513. Retriage flag was dup_id_item; confirmed the 124 duplicated
  `index` rows were exact full-row duplicates (double-submitted survey),
  deduplicated. Instrument identity for each Q-block not confirmed against
  the full paper text — labeled by source question number.
- `dopmeijer_2022_*` (4 tables: sense_belonging, ubos, loneliness,
  performance_pressure) — Dutch students, N=3141. No id column exists in
  the raw file at all; retriage's dup_id_item flag came from a heuristic
  guess on the wrong column. Row index used, no actual duplication.
- `leon_guereno_2020_*` (breq 23 items, resilience 10 items) — recreational
  runners, N=1850.
- `roelen_2020_*` (k6 6 items, rses 10 items, dietary_diversity 17 items)
  — rural Haiti, N=1381. Item text (household survey has ~240 opaquely-
  coded columns) resolved via Stata variable labels (pyreadstat), not
  guessed — found the paper's actual focal instrument (RSES) this way.

2 skipped: pone.0202750 (equine ethogram/behavioral-coding data, doesn't
fit the item-response schema — the "7357 participants" the retriage
reported was a red herring from a repeated-observation coding file, not
real N); pone.0150312 (all columns are DASS/wellbeing/social-support
composite TOTALS, no raw items).

Remaining: 74 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued (2026-07-27)

10 more candidates reviewed, 7 processed → 21 more tables (35 total in
`biblio_plos_batch3.csv`):
- `pranckeviciene_2022_*` (phq9, gad7) — Lithuanian students, N=1358.
  `phone` column (real PII, 1358/1358 non-null) dropped.
- `contreras_valdez_2022_*` (edeq, bsq, rses) — Mexican general
  population, 2 studies pooled (id unique only within-study, composite
  key used). Two different EDE-Q missing-sentinel codes (9 vs 99)
  resolved via the raw file's own "Keys" codebook sheet, not guessed.
- `buzgova_2023_*` (qol, rses, soc, lsita, gds, gai — 6 scales, 83 items)
  — Czech elders, largest multi-scale find in this pass. Raw id column
  fails uniqueness with no wave/date column to explain it; row index used
  per the standard's non-unique-id guidance rather than assuming a
  longitudinal structure without evidence.
- `duboz_2021_*` (swls, pss10) — Senegal, 2 locations pooled; 7 exact
  full-row duplicate pairs within Dakar deduplicated.
- `cormier_2024_*` (personality, pss4, phq4, cognitive_decline) — hearing
  loss study; Qualtrics export with 2 extra header rows (question text +
  ImportId JSON) that the automated triage's plain read didn't skip.
  SC1-12 columns are per-instrument TOTALS (row-1 label is literally the
  instrument name), excluded.
- `jutte_2024_*` (loneliness ×2 waves, personality) — COVID-era panel;
  wave already explicit in the raw file's own `_w1`/`_w2` suffixes.
- `safiye_2023_*` (mbi, rfq) — teachers; RFQc/RFQu per-item transformed
  columns (used to derive 2 subscale totals) correctly recognized as
  redundant with the raw RFQ items, not double-counted.

3 skipped: pone.0233831 (SCL-90/resilience/social-support -- all subscale
SUM/mean columns, no raw items); pone.0304549 (PHQ9 column is a binary
clinical-cutoff flag, not items or even a total); pone.0307744 (all
columns are single summary/behavioral measures, e.g. minutes of physical
activity per week -- no raw items).

Remaining: 64 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued further (2026-07-27)

4 more candidates reviewed, 3 processed → 10 more tables (45 total in
`biblio_plos_batch3.csv`):
- `teshome_2021_pss10` — Ethiopian healthcare workers, N=798.
- `bitew_2020_*` (anxiety, self_efficacy, osss3, phq9, lte — 5 scales, 39
  items) — Ethiopian students. Two text-coded scales use abbreviated/
  nonstandard category labels; ordinal direction inferred from semantics,
  flagged as such rather than asserted with false confidence.
- `hellstrom_2019_*` (psqi, isi, sci, pss14 — 4 scales, 43 items) —
  Swedish students. The source paper is itself a psychometric methods
  paper about the Sleep Condition Indicator's item-response properties.
  Each PSQI/ISI/SCI item had genuinely different response-category
  wording (verified per-column, not assumed uniform) -- built item-
  specific value maps rather than one shared map. Excluded 4 Pittsburgh
  single items that turned out to be clock-time values, not ordinal
  responses.

1 skipped: pone.0140621 (Brazilian birth-cohort growth study; only
derived depression classification/sum columns present, no raw items, and
`id` unresolvable -- no per-person identifier at all, cryptic Portuguese
column names throughout).

Remaining: 60 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued further still (2026-07-27)

6 more candidates reviewed, 3 processed → 8 more tables (53 total in
`biblio_plos_batch3.csv`):
- `cinar_tanriverdi_2023_*` (pmss 13 items, gad7 7 items) — Turkish
  medical students. Main sample (S1, N=572) had SPSS multiple-imputation
  artifacts (28 rows with near-integer jittered floats identically across
  every item, e.g. 1.988282041) -- dropped per "remove imputed values",
  not rounded to the nearest integer. S2 (N=70) confirmed a genuine
  retest subsample via 69/70 id overlap, combined as wave 1/2.
- `van_der_donk_2019_bdi` — full 21-item BDI, depressed diabetes patients,
  Netherlands, N=566.
- `hoorani_2022_*` (child_help, ps, sp, epreas, nps — 5 scales) — Young
  Lives India adolescent panel, 2 waves. The Excel SI file (S1) had these
  same items with source-level string truncation (values like "Strongly"
  with no agree/disagree indication -- genuinely ambiguous, not a display
  artifact); the Stata companion (S2) had the full untruncated strings
  and was used instead.

3 skipped: pone.0212914 (SF-36/PSQI/HADS -- all domain-level and total
scores, no raw items); pone.0292302 (K6/FCV19/STAI -- all totals, no raw
items; S2 turned out to be an unrelated COVID case-count time series);
pone.0271374's item structure recovered via S2 as noted above (not a
skip, listed for context).

Remaining: 55 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued yet further (2026-07-27)

5 more candidates reviewed, 2 processed → 4 more tables (57 total in
`biblio_plos_batch3.csv`):
- `jeon_2019_*` (cbi 19 items, cesd10 10 items) — Korean homecare
  workers, N=464.
- `bakker_2020_*` (pss10, rses) — Ethiopian midwifery students, N=403. A
  third 10-item block about the paper's actual focal topic (mistreatment
  during childbirth) takes values 1-10 with a categorical-looking
  distribution (likely provider/location type) rather than ordinal
  severity -- not included, flagged as uncertain rather than guessed.

3 skipped: pone.0200609 (each column is a different construct/rater-type
score -- cognitive/math-pretest/math-interest/etc as judged by student
vs. teacher -- not repeated items of one scale, doesn't fit the
id×item×resp schema); pone.0321373 (all Big-5/anxiety/depression totals,
no raw items); pone.0239002 (aHSCS/BRS/RSES/GSES/DSRS all present only as
aggregate a/b/c score variants, no raw items).

Remaining: 50 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued (2026-07-27, cont'd)

3 more candidates reviewed, 2 processed → 4 more tables (61 total in
`biblio_plos_batch3.csv`):
- `tran_2023_*` (gad7, phq9, gi_symptoms) — Vietnamese medical students,
  N=400. One duplicate id (data-entry error, not a real wave) disambiguated
  rather than dropping either respondent's data.
- `weida_2020_financial_security` — 10-item scale, N=371. Confirmed f1-f4
  are continuous IRT factor scores (not raw items) via their hundreds of
  distinct non-integer values, not assumed.

1 skipped: pone.0302350 (heterogeneous demographic/clinical survey, no
multi-item scale present at all -- "Personality traits(high)" and
"Adherence score" are each single columns, not scales).

Remaining: 47 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued (2026-07-27, cont'd further)

2 more candidates reviewed, 2 processed → 3 more tables (64 total in
`biblio_plos_batch3.csv`):
- `rahman_2022_phq9` — Bangladeshi students, no reliable id column at all
  (Timestamp only covers half the rows); row index recovers the full
  N=677 instead of the 333 the triage's partial id guess implied.
- `park_2024_*` (ageism 18 items, mbi 22 items) — Korean nurses, N=331.
  Same reverse-coded-twin-column pattern as wurm_2016 earlier in this
  pass (Korean "역산" suffix instead of German "umgepo").

1 skipped: pone.0255392 -- retracted paper (title literally begins
"RETRACTED:"), skipped outright regardless of content.

Remaining: 45 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued (2026-07-27, cont'd yet more)

5 more candidates reviewed, 2 processed → 4 more tables (68 total in
`biblio_plos_batch3.csv`):
- `koirala_2024_*` (pss10, brief_cope 28 items) — Nepali nursing students,
  N=317. AQ/BQ/CQ blocks turned out to be demographics (age/income/
  institution), not items, once actually inspected.
- `menaldi_2023_*` (mbi 22 items, brief_cope 28 items) — Indonesian
  resident physicians, N=388. Raw sheet interleaves a raw-text response
  column with a numerically-coded column per item; selected the coded
  columns via regex on column name rather than position.

3 skipped: pone.0171186 (all single aggregate scores -- FIQ/BFI/PCS/MCS/
BDI/STAI/etc totals, no id column, no raw items); pone.0224322 (PHQ9_T1/
T2, Stress, Support are totals; GH/PF/RF/... are MOS-HIV domain-level
scores, not raw items); pone.0262638 (PHQ items split across
inconsistent multi-part gating/frequency sub-questions -- e.g. PHQ3 has
PHQ31/PHQ311/PHQ322 -- that would need nontrivial reconstruction logic,
and no reliable person-ID column exists either; too complex/risky for
the likely payoff, deferred rather than guessed at).

Remaining: 41 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass — dudasova_2021 (2026-07-27)

1 candidate, 10 tables (78 total in `biblio_plos_batch3.csv`) —
**largest single multi-scale find in the worth_retrying pass**:
`dudasova_2021_*` (cpc12, engagement, job_satisfaction, swls, hope,
social_support, gratitude, positive_affect, performance — 9 scales, 88
items, N=282; plus cpc12_study3, a second independent N=202 sample of
just the focal CPC-12 instrument under a different naming convention).
Article has 4 SI files, one per validation sub-study with independent
samples; only S1 (richest) and S3 (CPC-12 alone) were used -- S2 (sparse
mixed single-item subset) and S4 (CPC-12's 4 subfacets as separate
blocks, needing nontrivial remapping to align with S1's combined naming)
were not reconciled for this pass, noted as a possible future addition
rather than silently dropped.

Remaining: 40 more `worth_retrying` candidates with N≥100.

## `worth_retrying` pass, continued (2026-07-27, cont'd further still)

2 more candidates reviewed, 1 processed → 4 more tables (82 total in
`biblio_plos_batch3.csv`):
- `jordan_2020_*` (burnout, pss10, resilience, mindfulness — 4 scales, 38
  items) — first-year medical students, N=539. Retriage flag was only
  n_items=2; real content is a Qualtrics export with 3 header rows above
  the data (ImportId JSON, question text, short code) -- header=2
  recovers the real scales and the full N=539, not the 282 the triage's
  partial read implied.

1 skipped: pone.0280338 (depression/GAD present only as single derived
binary flags, no raw items).

Remaining: 39 more `worth_retrying` candidates with N≥100.

**QC spot-check pass (2026-07-27)**, at ben-domingue's request, on 9
specific `resp` values across already-processed tables. 5 confirmed
legitimate (bakker_2020_pss10 resp=0; buzgova_2023_lsita resp=6;
buzgova_2023_rses resp=0, a known alternate RSES 0-3 coding;
contreras_valdez_2022_edeq's 0-50 range, expected from its two item
types; jeon_2019_cesd10 resp=3). **4 real data-entry errors caught and
fixed**, all isolated to one item (or absent everywhere else in the same
scale) rather than recurring proportionally across items — the diagnostic
that told real values from errors here:
- `bitew_2020_lte`: stray resp=2 (1 of 7908; scale is otherwise strictly
  binary) — dropped, now 0-1.
- `bitew_2020_osss3`: resp=0 (2-4 per item vs. 87-287 for genuine
  categories; standard OSSS-3 scoring has no 0) — dropped, now 1-5.
- `leon_guereno_2020_resilience`: resp=0 isolated to RS7 only, absent
  from the other 9 items — dropped, now 1-5.
- `park_2024_ageism`: stray resp=5 on item a18 only (every other item
  caps at 4) — dropped, now 1-4.

This "isolated-to-one-item vs. consistent-across-items" diagnostic was
formalized into `datastandard.md`'s "Data entry errors at known values"
section and its QC checklist item 4, so future scripts (in this pipeline
or `data/`) apply it up front rather than needing a manual spot-check
after the fact.

**Upload note**: `biblio_plos_batch3.csv` (82 rows through this point)
was pasted into the dictionary sheet by ben-domingue and the file deleted
before this note-annotation update could be applied to the 4 corrected
rows -- the actual dictionary entries (DOI/N/description) are unaffected
by these fixes, only the underlying `irw_output/*.csv` content changed,
so nothing needs re-pasting. The 4 corrected CSVs (and the other 78) were
still present in `irw_output/` as of this fix, ahead of the Redivis
upload -- confirm the corrected versions (not any earlier download) are
what gets uploaded.

**Closed out (2026-07-27)**: ben-domingue confirmed all 82 tables from
this batch (`biblio_plos_batch3.csv`, including the 4 QC-corrected ones)
moved for Redivis upload; `irw_output/` and the biblio CSV both empty/gone
on confirmation, consistent with upload having happened. 42 of 81
`worth_retrying` candidates now fully closed out end-to-end (24 processed
→ 82 tables, 18 skipped). Remaining: 39 more `worth_retrying` candidates
with N≥100.

## `worth_retrying` pass, batch 4 (2026-07-27)

1 candidate, 5 tables → `biblio_plos_batch4.csv`: `rahm_2017_*` (spane,
panas, swls, hswbs, shs) — German SPANE validation, N=498, 47 items
total. `VP` isn't a person id (records collection mode); SPANE's 1-month
follow-up columns exist wide on the same row and were melted into a wave
column. SHS's mixed numeric-string/text-endpoint export handled with
per-item maps, verified via per-item resp distribution per the newly
formalized diagnostic (datastandard.md) before finalizing.

2 more candidates, 2 tables (7 total in `biblio_plos_batch4.csv`):
- `moore_2016_bdi` (20 of 21 BDI-II items) — N=282, no id column, row
  index used.
- `rinaldi_2021_mas` (61-item Mentalized Affectivity Scale, the paper's
  focal instrument) — N=258. The per-item distribution check (freshly
  formalized) caught 3 corrupted recoded-item columns (values up to 124
  on an otherwise clean 1-7 scale) before they went into the output;
  fixed by using the raw un-recoded items instead of patching around the
  corruption, since the standard only requires within-item direction
  consistency, not across items.

3 more candidates reviewed, 2 processed → 4 more tables (11 total in
`biblio_plos_batch4.csv`):
- `donati_2021_cfq7` — Cognitive Fusion Questionnaire-7, clinical +
  non-clinical Italian samples, N=365. One duplicate-code collision
  within the clinical group disambiguated.
- `zautra_2015_*` (caug, iri, tmms24 — 3 scales, 47 items) — pre/post
  social-intelligence intervention, Spanish sample. Id unique only within
  experimental/control group, composite used. A 35-item CIS block with
  item-specific full-phrase response categories (not a uniform scale)
  deferred rather than force-mapped.

2 skipped: pone.0229591 (ASL receptive-skills deaf-education longitudinal
growth-curve study, mostly derived scores with opaque item codes);
pone.0174367 (real name/email PII columns present; a 9-item anxiety/
depression screener + 8-item ESS each administered twice, but
distinguishable only by column position with unnamed offset headers
throughout -- too fragile for reliable extraction, deferred).

1 more candidate, 1 table (12 total in `biblio_plos_batch4.csv`):
- `gomez_2020_mpq` (114 items) — Multidimensional Personality
  Questionnaire brief-form item pool, N=213. Retriage dup_id_item flag
  was because the raw file has every respondent's row duplicated
  exactly (a plain export artifact, not real repeated measures) --
  full-row drop_duplicates fixed it. Separately, 18 of 132 M-item
  columns had corrupted SPSS value-label metadata (nonsense labels like
  "Company"/"Plane" instead of True/False) and were dropped rather than
  guessed at.

3 more candidates reviewed, 2 processed → 5 more tables (17 total in
`biblio_plos_batch4.csv`): `park_2021_*` (pss10, swls, N=208) and
`kim_2023_*` (pss10, phq9, gad7, N=202) — both clean multi-scale
extractions, only the raw items kept out of files with many _sum/_aver/_T
aggregate columns. 1 skipped: pone.0182845 (Pubertal Development Scale +
Family Affluence Scale, only 7 items total, but item-specific German
category text mixed with float/string corruption -- poor effort/value
tradeoff for the item count).

1 more candidate, 6 tables (23 total in `biblio_plos_batch4.csv`):
- `rzeszutek_2020_wwii_*` (matgrandmother/matgrandfather/patgrandmother/
  patgrandfather, 29 items each) + `rzeszutek_2020_swls`/`ghq28` —
  grandchild-reported WWII trauma-history checklist (loss of parent,
  combat, concentration/Soviet camp, ghetto, rape, hiding Jews, etc. —
  confirmed real distinct items via SPSS variable labels), Polish young
  adults, N=500. `lp` is a family/sibling-group id shared by 2-4
  respondents of differing age/sex (not a per-respondent id) — row index
  used, `lp` kept as cov_family. Each trauma item is yes/no/don't know;
  "don't know" isn't an ordinal point between no/yes for a factual
  historical question, so treated as missing and dropped (no=0/yes=1).
  Per-item resp distribution checked clean across all 6 tables (per the
  standing diagnostic) before finalizing.

5 more candidates reviewed, 1 processed → 11 more tables (34 total in
`biblio_plos_batch4.csv`):
- Skipped 4 as aggregate-only, no raw items: pone.0195239 (autistic
  traits/social anxiety — both SI files are per-condition accuracy
  composites and SPAI/AQ totals, no trial- or item-level data);
  pone.0156939 (systematic review — SI is a study-characteristics results
  database, not respondent data); pone.0206555 (video game expertise —
  SI has only derived task scores: MMR, Grit total, span-task totals);
  pone.0256983 (sleep deprivation/emotion regulation — 8 SI files are all
  pre-aggregated by condition/bout, e.g. Subject×Valence×Session means,
  not raw trials or items despite trial-based task design).
- Processed — `wolf_2017_*` (posaff/vitality/anxiety × Study 1, plus
  Study 2's pre/post + video_liking + nature_connect — 11 tables, 76
  items total) — biodiversity-exposure well-being study, N=140 (Study 1)
  / N=264 (Study 2). Every item across both studies uses one uniform
  5-point format (bare numeric string or "LABEL (N)" endpoint text) —
  a single regex handled all 11 tables. Study 2's pre/post scales use
  different, mostly non-overlapping item wording per the SPSS labels
  (confirmed before assuming a wave structure applied), so kept as
  separate tables rather than melted into a shared wave column.

1 more candidate, 1 table (35 total in `biblio_plos_batch4.csv`):
- `garciabatista_2021_erq` — Emotional Regulation Questionnaire (10
  items), COVID-19 health workers, N=187. The PSS-14 columns the paper's
  title implies (perceived stress) are entirely empty in the export (0
  non-null across all 14, confirmed not a read/parse issue) — only ERQ
  usable. No reliable id column (`TimeStamp` had only 9 unique values
  across 187 rows); row index used. Real PII (`Email` column) dropped
  entirely, not kept even as a covariate.

2 more candidates reviewed, 1 processed → 3 more tables (38 total in
`biblio_plos_batch4.csv`):
- Skipped: pone.0271719 (BDNF/CRH vitiligo genetics — PHQ-15/GAD-7/PHQ-9
  present only as single total-score columns, no raw items).
- Processed — `nteveros_2021_*` (mbi, who5, psqi_disturbance) — Greek
  medical-student burnout study, N=182, 30 items total. MBI (15i) and
  PSQI component-5 (10i) both exported as Greek-text frequency
  categories, mapped to ordinal codes after confirming each scale's full
  item set shares one identical category string set. WHO-5 (5i) already
  numeric. Left out: PSQI's other single-item components (heterogeneous
  time-of-day/duration/differently-worded formats) and an unlabeled
  c1-c7 block whose construct isn't identified anywhere in the source or
  paper.

1 more candidate, 3 tables (41 total in `biblio_plos_batch4.csv`):
- `makransky_2016_*` (motivation, self_efficacy, mcq_correct) — virtual
  lab-simulation training study, N=189. Genuine pre/post design with the
  *same* items asked twice (unlike wolf_2017 above) — used wave=1/2
  rather than separate tables. MCQ items scored correct(1)/incorrect(0);
  raw MCQ answer-option letters not processed (would need the item key).

4 more candidates reviewed, 1 processed → 1 more table (42 total in
`biblio_plos_batch4.csv`):
- Skipped 3 as aggregate-only, no raw items: pone.0200129 (perimenopausal
  quality-of-life prediction — every column is a subscale/domain score);
  pone.0212482 (children's executive-function physical-activity breaks —
  all columns are derived t-values/conflict-scores/indices);
  pone.0200609 (already logged as skipped earlier in this pass).
- Processed — `kolcu_2025_mmas` — medication-adherence questionnaire (6
  items), pre/post LNG-IUD insertion, N=143. `Case` had one duplicate
  value; row index used as id. SF-36 (subscale scores only) and Beck
  Depression (total only) present in the same file but have no raw items,
  excluded.

2 more candidates reviewed, 1 processed → 4 more tables (46 total in
`biblio_plos_batch4.csv`):
- Skipped: pone.0199605 (retirement time-use study — every column is a
  DASS/Rosenberg/SWEMWBS/time-use total, no raw items).
- Processed — `extremera_2016_*` (shs, swls, sbq, ei) — unemployment/
  emotional-intelligence/suicide-risk study, N≈1123, 29 items total.
  Important correction to the original triage: `cuestionario` (what the
  retriage treated as the id, giving a "150 participants, ~7.5x
  duplication ratio" worth_retrying flag) is NOT a person identifier —
  spot-checking rows sharing a `cuestionario` value showed different
  ages and sexes, i.e. different people. It's a batch/version code, not
  a repeated-measures key, and there's no real wave/longitudinal
  structure at all — this is a cross-sectional sample of ~1123
  respondents, not ~150. Row index used as id. Per-item resp-distribution
  QC caught 2 isolated resp=0 values in SWLS (dropped) but confirmed
  SBQ item 4's legitimate 0-6 range (703/961 at 0 — the standard SBQ-R
  format for that item, not an error) before keeping it.

2 more candidates reviewed, 1 processed → 5 more tables (51 total in
`biblio_plos_batch4.csv`):
- Skipped: pone.0338126 (asthma/depression predictors — ACT/AQLQ/PHQ-9
  present only as total-score columns, no raw items).
- Processed — `chinvararak_2021_*` (bdi, phq15, ylseq, ssq, ecr) — Thai
  depressed-patient attachment/depression study, N=180, 113 items total.
  Three scales exported as Thai text categories (PHQ-15 3-point severity,
  YLSEQ binary yes/no, SSQ 5-point) each mapped to ordinal codes after
  confirming the full category set was identical across every item in
  that scale; BDI and ECR already numeric.

2 more candidates reviewed, 1 processed → 1 more table (52 total in
`biblio_plos_batch4.csv`):
- Skipped: pone.0223482 (MS social-cognitive treatment — every column
  across 4 timepoints is an MSSES/UCL/MSQOL54/anxiety/depression/IPA
  subscale total, no raw items).
- Processed — `ojelabi_2019_sf36` — SF-36 raw items (36 items), sickle
  cell disease patients in Nigeria, N=200. No id column at all; row
  index used. A companion covariate file (PHQ9/GAD7/SGH totals, same 200
  row count) was deliberately not merged in — no confirmed shared key or
  row-order alignment between the two files, and guessing risked
  silently pairing the wrong patients' records.

1 more candidate, 10 tables (62 total in `biblio_plos_batch4.csv`):
- `wang_2016_*` (study1_power/authliving/authalien/authexternal/se/
  relationship + study3_se/power/auth/social_desirability) —
  authenticity/power/self-esteem/relationship-satisfaction study, 2 of 3
  sub-studies processed (Study 1 N=104 English, Study 3 N=210 Chinese;
  Study 2's ambiguous Q3_1-21/po item blocks with no codebook match
  skipped). Study 3 exported as 5-point Chinese agree/disagree text,
  mapped after confirming se/power/auth share one identical category
  set; its 5-item social-desirability scale had per-item SPSS
  value-label corruption (only {0.0, one Chinese label} per item instead
  of a clean binary pair) — treated as 0/1 by relative state, same
  pattern as gomez_2020_mpq's corrupted labels earlier in this batch.

Remaining: ~13 more `worth_retrying` candidates with N≥100 (pool
recounted 2026-07-27 against actual BATCH_LOG skip decisions, not just
processed scripts — several earlier skips weren't being excluded from
the "remaining" count).

## `worth_retrying` pass, batch 5 (2026-07-27)

`biblio_plos_batch4.csv` (62 rows) confirmed uploaded/pasted by
ben-domingue; recounted the actual remaining pool precisely (not the
rough estimate above) — 5 true unreviewed candidates left, not ~13 (most
of the gap was already-skipped rows the estimate hadn't excluded). New
staging file `biblio_plos_batch5.csv` started.

1 candidate, 2 tables → `biblio_plos_batch5.csv`:
- `ibrahim_2015_*` (sf36, bfi) — chronic kidney disease patients, N=200,
  80 items total. SF-36 exported as 8 different section-specific text
  formats (expected for this instrument); enumerated each section's full
  category set before mapping. Two isolated stray numeric values dropped
  as out-of-range errors (Q3 one 4.0 against 3 categories, Q4 one 3.0
  against binary); Q10's stray 6.0 kept as a legitimate response
  (matches that section's real 6th category). SS1-5/SE1-8 (13 items) and
  SF9-19 (11 items) also present but left unprocessed — no variable
  labels, no identifiable instrument name in the paper's available text.

1 more candidate, 1 table (3 total in `biblio_plos_batch5.csv`):
- `marcussonclavertz_2019_velten` — Velten Mood Induction Procedure
  statements (80 items), online validation study, N=106. LimeSurvey's
  opaque `vNN_SQ001` codes only resolve to the real mood-statement text
  via SPSS variable labels, not the column names — checked before
  assuming these were uninterpretable, unlike the batch-10/13
  listening-text-repetition case where no such labels existed. Study 2
  (a separate file with a structurally different, already-named PANAS-
  style item set) not processed here.

1 more candidate, 2 tables (5 total in `biblio_plos_batch5.csv`):
- `chen_2019_*` (cdrsc, csq) — cold-pressor pain-appraisal study, N=235.
  Confirmed instrument identities directly against the paper's Measures
  section text (CDRS-C 0-4, task-specific CSQ 0-6) rather than guessing
  from column names. 37 columns (pse01-08/appraisal01,a02-06/nrs01-03/
  hs01-06) left unprocessed — no labels and no matching description
  found in the paper text for any of them.

1 more candidate, 3 tables (8 total in `biblio_plos_batch5.csv`):
- `romadlon_2022_*` (mfi20, facit, bdi) — Indonesian type 2 diabetes
  fatigue study, N=200, 54 items total. `Sample` (1-3 letter codes,
  likely patient initials) reused across different respondents —
  neither a reliable id nor safe to keep as a covariate; dropped
  entirely, row index used as id. PSQI1-7 (the 7 standard PSQI component
  scores, not raw sub-questions — treated as derived, like SF-36 domain
  totals elsewhere) and Q1-5 (heterogeneous binary/continuous/ordinal
  formats, unidentified) excluded.

Final candidate, 3 tables (11 total in `biblio_plos_batch5.csv`):
- `dolzdelcastellar_2021_*` (faces, stai, eds) — family functioning/
  differentiation-of-self/anxiety study, Spanish young adults, N=185,
  114 items total. Two raw column-naming inconsistencies fixed (`EDCS_34`
  and `EDS65`, both missing/wrong naming relative to the rest of the
  74-item EDS scale).

**This closes out the entire `worth_retrying` (N≥100) pool** — every
candidate from the 81-row filtered list (2026-07-26) has now been
reviewed: processed or explicitly skipped with reasons logged above.
Only the deprioritized sub-100 tail (26 candidates, filtered out
2026-07-26 per ben-domingue's direction) remains unreviewed in the
`worth_retrying` category.

`biblio_plos_batch5.csv` (11 rows) confirmed uploaded/pasted by
ben-domingue (2026-07-27).

## Decision: expand beyond PLOS ONE (2026-07-27)

ben-domingue's direction for the next session: run a fresh discovery
pass with new search terms rather than working the sub-100
`worth_retrying` tail, and evaluate expanding the PLOS discovery script
beyond PLOS ONE.

Discussed and agreed: target PLOS Mental Health and PLOS Global Public
Health specifically, not the full PLOS journal family. Both share PLOS
ONE's CC-BY licensing and site template, so `irw_discover_plos.py`
(currently filtered to PLOS ONE's eissn 1932-6203) likely only needs an
eissn swap or an additional eissn in the filter, not a rewrite of the
SI-extraction/license/data-availability logic. Both journals also
publish survey/psychometric data as a core part of their scope, similar
to the psych/health subset of PLOS ONE that's produced most of this
pipeline's hits so far. Explicitly decided against expanding to PLOS
Biology/Genetics/Pathogens/Computational Biology/etc. — those mostly
publish lab/genomic data, not item responses, so the discovery/triage
time would have low yield. Not yet implemented — this is the plan for
the next session, starting narrow with these two journals before
considering further expansion.

## PLOS Mental Health + PLOS Global Public Health run, and decision to backburner (2026-07-28)

Implemented the plan above: `irw_discover_plos.py` generalized from a
single hardcoded PLOS ONE eissn/URL to a `JOURNALS` dict keyed by slug
(`plosone`, `mentalhealth` [eissn 2837-8156], `globalpublichealth`
[eissn 2767-3375]) plus a `--journals` CLI flag; slugs confirmed against
live `journals.plos.org` article URLs, not guessed. Journal slug threaded
through `Hit.source` (`"plos:<slug>"`) so it survives being pickled to the
`ProcessPoolExecutor` worker. Reused the same 22 terms as the PLOS ONE
pilot (logged in `search_terms_log.csv`, 2026-07-27) rather than writing
new ones — same topics, new journals.

**Run hit two network problems mid-flight, both since resolved, neither a
code bug**: (1) a transient DNS resolution outage on this machine killed
every `globalpublichealth` query from `GAD-7` onward the first time
through (21/22 terms got zero results, `PHQ-9` was cut mid-pagination) —
re-ran just `globalpublichealth` with `--resume` once DNS recovered
(dedupes by DOI already in the output, so it only filled the gap). (2)
35 of the resulting `globalpublichealth` rows landed as `download_failed`
— an abnormal 51% rate vs. `mentalhealth`'s 0% — traced to the same
network instability (connection-refused fetching the *article page*, not
a real 404/broken SI link). `--resume`'s DOI dedupe would have skipped
these too (it doesn't distinguish flag), so instead pulled those 35 rows
out of the CSV and fed their DOI/URL straight into `process_one_isolated`
via a throwaway script, bypassing the Solr search since the URLs were
already known. Of the 35, 34 resolved cleanly on retry (confirming the
network-flakiness diagnosis) and 1 was a genuine persistent
`download_failed`.

**Final triage** (168 total candidates — `mentalhealth` 100,
`globalpublichealth` 68): 134 `no_usable_file`, 12 `timeout`, 17
`human_assistance`, 3 `not_item_response`, 1 `good`, 1 `download_failed`.

**Retriage on the 17 `human_assistance` rows** (`irw_retriage_ha.py`):
4 `worth_retrying`, 7 `human_review`, 3 `aggregate_continuous` (drop), 3
`not_item_response` (drop). `human_review_plos_mh_gph.csv` (7 rows) ready
to paste into the "Human eye" tab.

**Comparison to the PLOS ONE pilot** (same 22 terms): PLOS ONE produced
2,996 candidates → 32 `good` (1.1%) + 107 `worth_retrying` after
retriage. This run produced 168 candidates → 1 `good` (0.6%) + 4
`worth_retrying`. Per-candidate yield rate is comparable; the shortfall
is pool size — these are much smaller/newer journals (Mental Health
launched 2024, Global Public Health 2021), not a worse hit rate. At this
volume, further investment here (e.g. an 8-language translation pass,
standard practice for the repo-based pipeline) isn't worth it relative to
other queued work.

**Decision (ben-domingue, 2026-07-28): backburner PLOS Mental
Health/Global Public Health, refocus on PLOS ONE.** The 1 `good` + 4
`worth_retrying` candidates from this run are parked, not processed, for
the same reason: not urgent enough to justify diverting from PLOS ONE's
existing backlog. See `TODO.md` for the parked candidate list and their
DOIs/URLs/n/items, and for the still-open sub-100 `worth_retrying` PLOS
ONE tail this session is refocusing on.

## PLOS ONE batch 6 — new search terms, discovery + full good-candidate pass (2026-07-28)

Per the decision above, ran a fresh PLOS ONE discovery pass with 22 new
instrument/construct terms not previously tried against any PLOS journal
(Need for Cognition Scale, Short Dark Triad, Autism Spectrum Quotient,
Toronto Alexithymia Scale, Fear of COVID-19 Scale, Insomnia Severity
Index, Eating Disorder Examination Questionnaire, Barratt Impulsiveness
Scale, Emotion Regulation Questionnaire, Raven's Progressive Matrices,
Implicit Association Test, n-back task, go/no-go task, Five Facet
Mindfulness Questionnaire, Multidimensional Scale of Perceived Social
Support, WHOQOL quality of life, Social Dominance Orientation, Balloon
Analogue Risk Task, Body Shape Questionnaire, Gratitude Questionnaire,
trust game, vocabulary test) — logged in `search_terms_log.csv`.
`python3 irw_discover_plos.py <22 terms> --out plos_batch6_triage.csv`,
run in the background (~2.5 hours wall clock for 1841 candidates).

**Triage**: 1841 candidates → 15 `good` (0.8%, comparable to the original
22-term pilot's 1.1%), 274 `human_assistance`, 1491 `no_usable_file`, 42
`not_item_response`, 12 `download_failed`, 6 `error`, 1 `timeout`.

**Retriage on the 274 `human_assistance` rows** (`irw_retriage_ha.py` →
`plos_batch6_retriage.csv`): 92 `aggregate_continuous` (drop), 89
`human_review`, 48 `worth_retrying`, 44 `not_item_response` (drop), 1
`recoverable_format` (a semicolon-delimited PsyCap file, not yet
re-triaged). The 89 `human_review` + 48 `worth_retrying` are not yet acted
on — next open item.

**All 15 `good` candidates hand-reviewed** (per this skill's standing
caution that a `good` flag needs a human glance — the triage script only
inspects the first tabular SI file, and several turned out to be
subscale-total/aggregate files rather than raw items once actually
opened):

Processed (8 papers → 24 output tables, all CC-BY, in
`biblio_plos_batch6.csv`, ready to paste into the dictionary sheet):
- `bled_2021_imagery_phenomenology` / `bled_2021_imagery_use` (autism
  mental-imagery use, N=119) — 2 short scales bundled in one file.
- `ruiz_parra_2023_rfq8` / `_ipo83` / `_maas` / `_iri_pt` / `_tas20` /
  `_scl90r` / `_bdi2` / `_pid5bf` / `_iip32` (Spanish RFQ validation
  study, N=605 non-clinical sample) — 9 validated instruments bundled in
  one SI file, each administered to a different overlapping subsample
  (confirmed via per-scale missingness being uniform across every item
  within a scale, i.e. real administration pattern, not random
  non-response). IRI items were letter-coded (A-E), recoded to 1-5. RFQ-8
  had one isolated -9 data-entry error (single value, single respondent),
  dropped. The "Retest" and "clinical" sheets in the same workbook (113
  and 41 rows) were not processed — left for a future pass if wanted.
- `najari_2024_bpqsf_awareness` / `_autonomic` / `_stress` (BPQ-SF
  Persian validation, N=751) — one stray Persian free-text value in
  column `s1`, coerced to NaN by the standard numeric cleaning step.
- `odachi_2022_fear_covid19` / `_hads` / `_bfs` (Japanese nurses, N=417).
- `zhao_2024_erq` (ERQ-8 validation, Chinese students, N=1534).
- `li_2021_sustainable_innov_behav` / `_cultural_intelligence` /
  `_knowledge_sharing` / `_org_cultural_diversity` (N=336).
- `kang_2015_facial_preference` (N=16 subjects x 24 faces) — the raw file
  is transposed (rows=faces, columns=subjects); reshaped so id=subject,
  item=face, resp=continuous facial-preference proportion (0-1). Small
  sample but genuine continuous item-level data, kept.
- `ly_2021_animal_empathy` (N=30, farm-animal empathy videos) — each
  participant rated a different subset of 20 videos on 7 emotions;
  item defined as video_id+emotion (verified participant x video unique)
  rather than emotion alone, since a bare emotion-only item would create
  spurious duplicate id+item pairs across different video content.

Skipped as **not actually item-level data** despite the `good` flag —
all four turned out to be aggregate/composite scores or non-Likert
ranking data once the raw file was opened, not raw item responses:
- `10.1371/journal.pone.0249033` (Ngai 2021, animal-assisted humane
  education) — SI file has only subscale-total scores at 3 timepoints
  (Prosocial/Cognitive/Empathy/etc. T0/T1/T2), no raw items.
- `10.1371/journal.pone.0186581` (Kumazaki 2017, robot appearance
  preferences in autism) — N=16, only a 3-category ranking task plus
  aggregate AQ/IQ totals; too small and not real Likert items.
- `10.1371/journal.pone.0230258` (Lasagna 2020, eye contact perception) —
  the picked SI file (`S1_Data.csv`) is an aggregated psychophysical
  count-correct matrix (participants x trials, cell = count out of ~12
  correct at a given signal-strength level), not raw per-trial responses;
  the other two SI Data files are similarly aggregated fitted-parameter
  and subscale-total data.
- `10.1371/journal.pone.0243209` (Megreya 2020, emotion regulation +
  face recognition) — all three experiment sheets contain only
  summary-statistic columns (hit/miss rates, accuracy %, CERQ subscale
  sums), no raw trial or item data anywhere in the file.
- `10.1371/journal.pone.0279360` (van Heyst 2022, attentional bias for
  weapons) — SI file has per-category accuracy proportions (aggregated
  across trials), not raw per-trial responses.

**Not yet processed — flagged for a follow-up session, not abandoned**
(both need real codebook-decoding time rather than a quick pass):
- `10.1371/journal.pone.0169808` (Carver 2017, PUGGS genetics-belief
  questionnaire) — two pilot-study raw-data files (N=207, N=78) each
  spanning 2-3 distinct subscales (belief-in-determinism, 1-6/1-5 with a
  "don't know" sentinel; true/false genetics-knowledge items needing an
  answer-key-based correct/incorrect recode per the codebook). Full DOCX
  codebooks already downloaded and read; the recoding logic is understood
  but not yet implemented as a script.
- `10.1371/journal.pone.0128876` (Meloni 2015, disability representations
  in parents and children) — 244-column SI file with ~8 distinct item
  families (open-ended disability-attribution codes, 5x12 fictional-
  character rating blocks, knowledge scale, interest/attitude scales with
  paired response-time columns, extracurricular-activity items); tractable
  but needs more per-block codebook time than this pass had.

## Human-eye backlog cleared; batch 6 human_review split out (2026-07-28)

ben-domingue confirmed three long-open "Human eye" pastes are done:
`human_review_conflict.csv` (Stroop/DVN-GINKMU), `human_review_lang_pilot.csv`
(SWAN/DVN-HWMJAE), and `human_review_cognitive_tasks.csv` (17 rows, batch
19) — all three files were already missing from disk (Dropbox-sync loss,
same pattern as elsewhere in this log) but content was preserved in
`TODO.md`'s descriptions, so closing them out is just a TODO update, no
regeneration needed.

Split batch 6's 89 `human_review` rows out of `plos_batch6_retriage.csv`
into `human_review_plos_batch6.csv` (columns: title, doi, url, license,
data_availability, data_file, n_participants, n_items, density,
refined_reason) — ready to paste into the "Human eye" sheet. The 48
`worth_retrying` rows remain in `plos_batch6_retriage.csv`, not yet
reviewed.

ben-domingue is now uploading batch 6's 24 `irw_output/*.csv` files to
Redivis and pasting `biblio_plos_batch6.csv` into the dictionary sheet —
those files are expected to disappear from disk shortly as a result, not
a sync-loss incident.

## PLOS ONE batch 6's 48 `worth_retrying` rows reviewed (2026-07-28)

Worked through all 48 `worth_retrying` rows from batch 6's retriage
(`plos_batch6_retriage.csv`). Most had been flagged only because
`irw_batch_updated.py`'s id-detection heuristic wasn't confident, or
because a dup_id_item failure looked longitudinal — neither of those
triage signals turned out to reliably predict whether a file actually
contained raw item responses. Downloaded and hand-inspected every file's
real column structure (id uniqueness, item vs. aggregate columns, text-
vs-numeric encoding) via a bulk inspection pass before deciding.

**Processed → 13 tables from 9 papers** (all CC-BY, in
`biblio_plos_batch7.csv`):
- `baumgaertner_2018_vaccine_trust` — 2 batteries of 3 vaccination-
  likelihood items, text-coded ("Very unlikely"..."Very likely") recoded
  1-5, N=997.
- `huang_2016_neo_neuroticism` / `_neo_conscientious` / `_cesd` — NEO-FFI
  N/C subscales (12 items each) + CES-D (20 items), N=113-114. The
  file's PSQI sleep-quality section was left unprocessed (item-level
  components are text-coded and mixed in among already-computed PSQI
  component scores; would need a separate pass).
- `grant_2018_ersq` — Emotion Regulation Skills Questionnaire (27 items),
  pre/post intervention as `wave` 1/2, N=36; text Likert labels ("Not at
  all"..."Almost always") recoded 0-4.
- `laksmita_2020_mspss` — MSPSS, Indonesian adolescent disaster
  survivors, N=299.
- `rosharudin_2023_dass21` / `_ders18` — one SI file bundling DASS-21 (21
  items, obfuscated `@N_LETTER` column names where the letter denotes
  Stress/Anxiety/Depression) and DERS-18 (18 items, letters denote the
  six DERS subscales) — identified by matching subscale-letter counts
  against the two named instruments in the title. Malay, N=689.
- `turner_2022_sr_belief_change` / `_cognitive_mediation` — two item sets
  in one file (stimulus-response belief-change, 9 items; cognitive-
  mediation beliefs, 15 items), N=250.
- `gomez_2022_qcae` — QCAE (31 items; some text-coded "Strongly
  Disagree"..."Strongly Agree", some already-numeric reverse-scored
  columns kept as-is), N=203. Every other instrument in this file (TOSCA,
  SIAS-6, SPS-6, BIS/BAS, ERQ, ATQ) was present only as subscale
  totals/means, not raw items — excluded.
- `yang_2015_ethnic_essentialism` — 104-item combined essentialism/
  multicultural-ideology/cultural-anxiety battery, Chinese university
  students, N=113. Every respondent was duplicated as a byte-identical
  row pair (export artifact, confirmed by direct row comparison) —
  deduplicated before melting. No codebook exists to split the 104 items
  by construct, so they're kept as one file.
**Retracted after initial processing (2026-07-28, caught by ben-domingue
in review)**: `stenson_2021_sleep_emotion` (10.1371/journal.pone.0256983)
was initially shipped as a 13th table (continuous "Rating" per session x
valence, item = session×valence, N=59) but the paper's Methods text
states the real per-trial response is a 5-point Likert rating (1-5, "how
negatively you felt about the image"), 15 trials per condition, and
explicitly says "Mean ratings for the attend/negative and decrease/
negative conditions were used" — i.e. the SI file's "Rating" column is a
derived mean/contrast score across trials (further transformed somehow,
since it goes negative, which a raw 1-5 mean can't), not a raw response.
Continuous-looking values were wrongly assumed legitimate by analogy to
`kang_2015_facial_preference`'s genuine FPV proportions, without
independently checking this file against the source paper's description
of what's actually being measured. Pulled the table, its `data/` script,
and its biblio row; `biblio_plos_batch7.csv` now has 12 rows.
**Process gap this exposed**: continuous/fractional values in a "worth_
retrying" SI file need to be checked against the paper's Methods text for
what the raw per-observation unit actually is (single Likert response?
average over N trials? a computed index?) before being accepted as
`resp` — matching values in-range for the *stated* raw scale isn't
enough on its own; out-of-range or oddly-fractional values are a strong
signal the column is already a composite, and should be looked into
before use rather than after.

**Skipped as aggregate/composite/derived data, not raw items** (despite
a clean, unique id column) — the recurring failure mode in this batch:
files whose only "items" were already-computed subscale totals,
standardized T-scores, IAT D-scores, or (in one case) values that were
fractional/imputed throughout every column, none of which are raw
responses per datastandard.md:
- ADHD/ERP twins study, videogame-virtue-behavior study (all SDQ/AQ/BIS/
  STAXI totals + game telemetry), undergrad romantic-attachment study
  (all subscale-mean composites), workplace social-support study (every
  scale's values were fractional/imputed throughout, not raw Likert
  codes), COVID hospital-staff longitudinal study (K6/FCV19/STAI stored
  only as wave-level totals despite a genuine `time` wave column),
  complementary chronic-pain-treatment study (T1_* columns are all
  scale-total names), error-related-negativity video-game study (EEG/
  behavioral aggregates only), drunk-driving IAT study (D-scores only,
  4 genuine explicit-attitude items too thin on their own), police-cadet
  heart-rate-stress study (behavioral/physio aggregates, 3 genuine
  single-item mood ratings too thin alone), abacus-training and ADHD-
  executive-function-training studies (T-scores/standardized composites
  throughout).

**Deferred, not abandoned** (flagged for a follow-up session, same as
PUGGS/disability-representations from the `good` pass): coping-self-
efficacy/sex-trafficking study and full-body-mirror-exposure eating-
pathology study (both have genuine multi-wave raw items — MSPSS,
CopSE, EDE-Q, PANAS — but need careful per-scale wave-column work);
insight-in-schizophrenia study (many real item blocks with ambiguous
subscale identity, e.g. bare "C1-5"/"S1-10"/"M1-12" prefixes with no
codebook); Brazilian smoking/FFMQ study (huge multi-scale file with
extensive derived-transform columns to filter out and ambiguous A/B/C
block identities). The remaining rows in `plos_batch6_retriage.csv`
(near-clean duplicate-id cases needing a dedup decision, and rows where
the first column is confirmed not to be a real id) were not individually
worked through this pass — see `TODO.md`.

## PLOS ONE batch 8 discovery + worth_retrying triage (2026-07-29)

Fresh PLOS ONE discovery run following the 2026-07-28 decision to keep
mining PLOS ONE with new instrument/task terms. 30 terms not previously in
`search_terms_log.csv` (HEXACO Personality Inventory, Difficulties in
Emotion Regulation Scale, Interpersonal Reactivity Index, Pittsburgh Sleep
Quality Index, Adult ADHD Self-Report Scale, Self-Compassion Scale, Trait
Emotional Intelligence Questionnaire, Need for Closure Scale, Right-Wing
Authoritarianism Scale, Moral Foundations Questionnaire, Cognitive
Reflection Test, Delay Discounting Task, Ultimatum Game, Wisconsin Card
Sorting Task, Digit Span Task, Dot Probe Task, Fear of Negative Evaluation
Scale, Social Interaction Anxiety Scale, Body Appreciation Scale, Eating
Attitudes Test, Alcohol Use Disorders Identification Test, Internet
Addiction Test, Adverse Childhood Experiences Questionnaire, Impact of
Event Scale, Brief COPE, Utrecht Work Engagement Scale, Psychological
Capital Questionnaire, Experiences in Close Relationships Scale,
Strengths and Difficulties Questionnaire, Fear of Missing Out Scale).

`api.plos.org` DNS dropped mid-run after ~24 terms (transient network
hiccup, not a script bug) — the last 6 terms were re-run with `--resume`
once DNS recovered, which correctly skipped the ~1281 already-processed
DOIs and only fetched the gap. Final tally: 1,500 candidates -> 1,153
`no_usable_file`, 261 `human_assistance`, 35 `download_failed`, 23
`not_item_response`, 7 `good`, 4 `error`, 1 `timeout`.

Retriage (`irw_retriage_ha.py`) on the 261 `human_assistance` rows gave:
91 `aggregate_continuous`, 80 `human_review`, 47 `not_item_response`, 42
`worth_retrying`, 1 `recoverable_format` (a semicolon-delimited PsyCap
file misread with the comma default).

### worth_retrying / recoverable_format triage (43 rows, all hand-inspected)

Downloaded and hand-inspected every flagged file's real column structure
via a throwaway bulk-inspection script (`inspect_batch8_wr.py`, deleted
after use; full per-row structural dump captured in
`batch8_wr_inspection.txt` before deletion). Same recurring failure mode
as prior batches: many `dup_id_item`-flagged rows turned out to be files
of already-computed subscale totals/z-scores/composite indices, not raw
items, despite having a clean unique-looking first column.

**Processed -> 8 papers, 31 tables** (all CC-BY, `biblio_plos_batch8.csv`):
- `lorenz_2016_hope`/`_optimism1`/`_optimism2`/`_resilience`/`_efficacy1`/
  `_efficacy2`/`_psycap` (PsyCap CPC-12 validation, Study 1, N=321) — the
  `recoverable_format` row; confirmed the semicolon re-read produces 76
  clean 1-6 item columns across 7 distinct batteries (hope, two optimism
  batteries, CD-RISC-13 resilience, two self-efficacy batteries, and the
  24-item PsyCap item pool). No id/covariate columns in source; row index
  used as id.
- `sleboda_2021_risk_benefit` (N=3228) — 80-item risk/benefit-perception
  battery, 5 hazard domains x 16 semantic-differential dimensions.
  `pd.read_spss`'s default value-label handling mixed numeric and
  labeled-endpoint Swedish text inconsistently across columns (labels
  exist only at the scale's 1/11 endpoints) — `convert_categoricals=False`
  was required to get clean 1-11 codes throughout; a real gotcha worth
  remembering for other Nordic-language SPSS files.
- `tiemensma_2018_iesr` (N=549) — 22-item IES-R. Source `id` collided on 2
  of 552 rows with genuinely different response patterns (not a retest) —
  failed the uniqueness check, so row index was used instead per
  datastandard.md's fallback rule.
- `alsuhibani_2022_*` (conspiracy/paranoia across 3 independent samples,
  combined N=2644) — 10 tables. Per ben-domingue's direction this session,
  checked the paper's own Methods text before assuming any cross-study
  item correspondence, rather than merging on column-name similarity
  alone: confirmed the 24-item Multidimensional Locus of Control Scale
  was "identical" across all 3 studies, the 20-item Self-Esteem Rating
  Scale was used in "Studies 2 and 3", and Study 3's 15-item GCBS was
  explicitly "the same ... employed in Study 2 ... the two additional
  items ... were not included" — so those three instruments were merged
  into single cross-study files (`alsuhibani_2022_loc`, `_sers`, `_gcbs`)
  with each study's `id` offset by `100000*study_number` to keep the
  combined id space collision-free; Study 2's 2 extra GCBS items with no
  Study-3 counterpart were kept as their own small file
  (`alsuhibani_2022_gcbs_extra_s2`) rather than discarded. PADS differed
  in both item count (10 vs 8) and scale range (0-4 vs 1-5) between
  Study 1 and Study 2 with no textual confirmation of correspondence, so
  those stayed separate, as did the single-study Consp (S1), Revised
  Paranoia scale (S3), NPI (S3), and ECRS (S3) batteries. This merge-vs-
  separate distinction is now documented in `datastandard.md`'s new "same
  instrument administered to multiple sub-studies/samples" edge case.
- `niazi_2020_mfq` / `_mfq_stereotype` (N=300) — MFQ-32 rated twice per
  respondent: once as the respondent's own judgment, once as their
  prediction of the average person's rating on the same 32 statements.
- `kim_2025_psas` / `_isi` / `_psqi` / `_hads` (Korean sleep-arousal
  validation, N=286) — 4 instruments bundled in one file, text-coded
  responses ("1=not at all", etc.) with leading-integer extraction; PSQI's
  4 clock-time/duration items (bedtime, wake time, minutes-to-sleep,
  hours-slept) are not ordinal Likert responses and were excluded, keeping
  only its 14 ordinal items (item 5's 10 disturbance sub-items + items
  6-9).
- `luo_2021_ecr` / `_conational_ties` / `_host_ties` / `_intl_ties` /
  `_acculturation_index` (international students in China, N=229) — 5
  instruments in one file with a Excel-merge header artifact (only the
  first item in each block carries real question text, later items are
  bare "@2."/"@3." placeholders with non-ASCII apostrophes) — columns were
  selected by position rather than by retyping the header text, and
  output items renamed to generic `item_NN` labels. A 2-item QCL block was
  excluded: values were fractional with a min near 0.01, indicating an
  already-computed proportion rather than a raw response.
- `reinecke_2018_online_vigilance` (N=229) — 12-item Online Vigilance
  Scale (salience/reactibility/monitoring subscales).

All 31 output files passed an automated per-item rare-value scan (looking
for values isolated to a single item and appearing nowhere else in that
item's scale, the data-entry-error signature from prior batches) with
nothing flagged.

**Skipped as aggregate/composite/derived or otherwise out of scope**
(~25 rows) — same recurring pattern as prior batches: files whose columns
were already-computed subscale totals, z-scored/standardized composites,
or clinical/biomarker measures, despite a clean unique id column. Notable
cases: a tourism choice-experiment (`10.1371/journal.pone.0270531`) and a
preference-reversal betting experiment (`10.1371/journal.pone.0292011`)
were skipped as conjoint/trial-level economic-game designs, the same open
scope question as the LGBTQ-judges conjoint case from batch 19 (see
TODO.md); a full-body-mirror-exposure eating-pathology study
(`10.1371/journal.pone.0257303`) turned out to be the identical paper
already deferred from batch 6's worth_retrying pass, just resurfaced via
a different search term; a small (N=26) JIA/SDQ study and a small (N=41)
racially-targeted-food-marketing study were skipped as too small per the
established N<100(ish) threshold; a HEXACO-100 test-retest study
(`10.1371/journal.pone.0262465`) only exposed domain-level facet means
(O/C/A/X/E/H) in the parsed sheet despite its SI caption promising
"items, facets, and domains" — flagged for a follow-up look at whether
another sheet in the same Excel file holds the raw 100 items.

**Deferred, not abandoned** (5 datasets, need more codebook/wave-column
time): a Clinton-voter activism longitudinal study
(`10.1371/journal.pone.0221754`, real CESD + Activist items across waves
but T1a/T1b/Wave coding needs care), a Chinese EFL learning study
(`10.1371/journal.pone.0280919`, real items with Chinese-text Likert
labels needing recoding plus a 481-vs-942-row mismatch to resolve), an
emotional-eating chain-mediation study (`10.1371/journal.pone.0280701`,
real EES-R/CES-D/DERS bundle but item blocks are cryptically labeled
`@10.`/`@11.` etc. and need matching to instruments), and a VR-empathy
perspective-taking study (`10.1371/journal.pone.0204494`) plus a
phonological-loop children study (`10.1371/journal.pone.0187368`) that
both look like real per-item/per-trial data but want a second look before
committing. See `TODO.md`.

The 7 originally-`good`-flagged candidates from the discovery run have
not yet been reviewed — next step, per plan agreed with ben-domingue.

## PLOS ONE batch 8 good-candidate review (2026-07-29)

Hand-reviewed all 7 originally-`good`-flagged candidates from the batch 8
discovery run before writing scripts, per the skill's standing caution
that the triage script only inspects the first tabular SI file.

**Processed -> 3 papers, 9 tables** (added to `biblio_plos_batch8.csv`):
- `queiros_2018_qcae` (N=562) — 31-item QCAE, Portuguese sample. The file
  extension in the SI listing (`.xls`) was misleading twice over: the
  triage-selected suffix guessed from caption order didn't match the
  actual live URL (fixed by re-running `extract_si_files` fresh rather
  than assuming a `.sNNN` numbering pattern), and even the correct URL's
  content is OOXML-zip-based despite the `.xls` name, needing
  `engine="xlrd"` — actually failed until traced through: don't guess
  SI suffixes from caption order, always re-derive the live URL.
- `esiason_2024_aaqii`/`_cfq`/`_bai`/`_bdi`/`_vlq_importance`/
  `_vlq_consistency`/`_ace` (NMOSD patients N=21 + caregivers N=37,
  combined into single cross-group files per the same identical-
  instrument-across-samples logic as `alsuhibani_2022`, caregiver ids
  offset by 1000) — REDCap export with a title row above the real header
  (`header=1` needed). AAQ-II, a 13-item CFQ item pool, BAI, BDI (items
  16/18 use a 1-7 code capturing both increase/decrease directions, a
  known BDI-II digitization quirk rather than a data error, confirmed via
  per-item `value_counts()`), the Valued Living Questionnaire (importance
  + consistency ratings on 10 life domains, written as two files), and a
  10-item ACE screen. REDCap `*_complete` status columns and 94
  `acoping___N`/`bcoping___N` checkbox fields (a coping word-pair
  checklist with no accompanying codebook) were excluded.
- `addy_2021_sdq_ghana` (N=405) — first 10 raw SDQ items (0-2 scale).
  `SDQ_TOTAL` and subscale sums, `TOTAL_DF_old`, and 25 `SDQ*_CAT`
  columns (banded/categorized recodes of the full 25-item SDQ, not raw
  responses to `SDQ_1`-`SDQ_10`) were excluded.

**Skipped, 4 candidates:**
- `10.1371/journal.pone.0243209` (Megreya, emotion regulation + face
  recognition) — same DOI already skipped in batch 6 as aggregate-only
  (hit/miss/accuracy face-memory stats, ERQ subscale means); resurfaced
  via a different search term (Emotion Regulation Questionnaire) but not
  new information.
- `10.1371/journal.pone.0220622` (ultimatum game neural correlate) —
  the "3 items" the triage flag saw were per-subject acceptance-rate
  proportions (Fair/Mid-value/Unfair conditions, values like 0.14/0.86/
  0.92 with a malformed multi-row Excel header) — an aggregate over
  trials, not raw per-trial responses, per datastandard.md's
  "continuous-looking column" check.
- `10.1371/journal.pone.0275045` (health-service positive-feedback
  systematic scoping review) — the "data" is a literature-review study-
  characteristics abstraction table (one row per reviewed paper), not
  survey response data at all.
- `10.1371/journal.pone.0233025` (monetary-incentive RCT for vulnerable
  children survey response) — the 5 "items" the triage flag saw
  (EMOSYM/CONPRO/HYPACT/PEEPRO/PROBEH) are already-computed SDQ subscale
  scores, not raw items; `response`/`allocation` are the RCT's own
  outcome/treatment fields with no accompanying item-level data.

This closes out PLOS ONE batch 8's discovery/triage/processing pass.
Still open: splitting the 80 `human_review` rows into
`human_review_plos_batch8.csv` for the "Human eye" sheet, and the 5
deferred datasets noted in the previous entry. ben-domingue is reviewing
all of batch 8's output CSVs before pasting `biblio_plos_batch8.csv` into
the dictionary sheet.

## PLOS ONE batch 8 — VR-empathy and phonological-loop deferred datasets resolved (2026-07-29)

Took the "second, closer look" promised in the previous entry for the 2
datasets that looked plausible but weren't committed to. Both resolved
cleanly once checked against the source papers' own Methods text, rather
than needing new codebook time — reclassified from "needs a closer look"
to "just needed the paper read more carefully."

**`herrera_2018_vr_empathy`** (`10.1371/journal.pone.0204494`, Herrera
et al., building long-term empathy via traditional vs. VR perspective-
taking about homelessness) -> 4 tables:
- `herrera_2018_iri` (21 items — Empathic Concern/Perspective
  Taking/Personal Distress subscales of the IRI) and
  `herrera_2018_beliefs_about_empathy` (12 items) — both merged across
  Study 1 (N=117) and Study 2 (N=439) since the Methods text confirms
  both were administered "pre-intervention" identically in both studies
  as sample checks; Study 2's id offset by 1000. Source `PID` strings
  collide across unrelated respondents in both studies (confirmed via
  mismatched ages on the same PID string, e.g. `26c2` appearing twice
  with ages 15 and 28) — row index was used as id instead.
  `cov_condition`/`cov_study` carry the group assignment rather than
  `treat`, since Study 1 is a 2-arm comparison (traditional vs. VR) but
  Study 2 is 4-arm (traditional/desktop/VR/control), so a single binary
  `treat` column wouldn't fit both.
- `herrera_2018_attitudes_homeless` (8 items, Study 2 only) — matched to
  the paper's "Attitudes toward the Homeless" scale on Likert range
  (1-9) and topic (the paper describes it as 7 items; the file has 8,
  likely an off-by-one in the paper's own count, not independently
  re-verified against the raw item text).
  `herrera_2018_se_d_items` (8 items, Study 2 only, `SE1-4`/`D1-4`) could
  not be matched to a named instrument in the text and were kept under
  their original source labels rather than guessed at.

**Caught and corrected in review (2026-07-29, ben-domingue)**: initially
also shipped `herrera_2018_ios` (Inclusion of Other in the Self, single
item) and `herrera_2018_dehumanization` (Ascent-of-Man Dehumanization
Scale, single continuous 0-100 item), both explicitly named single-item
measures in the paper's Methods text. Pulled both — **IRW does not
accept single-item scales regardless of data quality**, since there's no
within-person item pattern to model; this is now a standing rule (see
memory `feedback_no_single_item_scales`). Removed from `irw_output/`,
`biblio_plos_batch8_deferred.csv`, and the processing script.

**`meng_2017_referent_assignment`** (`10.1371/journal.pone.0187368`,
Meng, Murakami & Hashiya — phonological loop and children's referent
assignment) -> 1 table. The original triage flagged
`Base-Assignment`/`Shift`/`Re-Assignment`/`Follow-RA` as the item
columns, which is what made this look ambiguous at first pass, but the
paper's Methods text spells out that each of those four is a derived
composite: "The Base-Assignment Score ... coded as 1 when both the EQ
and AQ were correct," and likewise Shift = f(EQ, EQ2), Re-Assignment =
f(EQ2, AQ2), Follow-RA = f(AQ2, AQ3). The actual raw responses are the 5
binary correctness scores those composites are built from — `EQ`
(explicit question), `AQ` (ambiguous question, same trial), `EQ2`/`AQ2`
(same pair after a topic shift), and `AQ3` (repeated ambiguous question,
a consistency check). Each of 74 children contributed 2 blocks x 2
trials = 4 observations of this 5-item set, encoded as a `wave` column
(1-4) rather than needing all 4 as separate items, since datastandard.md
allows duplicate id+item pairs when `wave` is present. `LPS` (0-8 range,
consistent with the paper's forward digit-span phonological-loop
measure) and `CES` (abbreviation not spelled out in the text) are
constant per child across all 4 rows and carried as covariates.

Both datasets' biblio rows are in `biblio_plos_batch8_deferred.csv` (5
rows, after removing the 2 single-item tables above), separate from the
already-pasted `biblio_plos_batch8.csv`. All output files passed the
per-item rare-value data-entry-error scan.

Still deferred: the Clinton-voter activism longitudinal study, the
Chinese EFL learning study, and the emotional-eating chain-mediation
study — all three still need real per-scale codebook/wave-column work,
not just a closer read of the paper text. See `TODO.md`.

## One-off: santos_2018 (GH issue #1557, 2026-07-29)

User-directed pointer, not from the discovery pipeline:
[issue #1557](https://github.com/ben-domingue/irw/issues/1557) linked
`https://osf.io/e9r5s/` (raw file `Santos_PlosOne.txt`) and the paper
Santos, Kossakowski, Schwartz, Beeber & Fried (2018), "Longitudinal
network structure of depression symptoms and self-efficacy in low-income
mothers," PLOS ONE 13(1):e0191675 (`10.1371/journal.pone.0191675`),
noting "permission from author." The OSF node itself has no license set
(`node_license` empty via the OSF API) — same "no formal license, author
granted permission" situation as `alcoholstroop_jones2024`/
`enkavi_2019`, so `Original License` = "Missing (NA)", `Derived License`
= "CC BY 4.0" (per ben-domingue instruction and the standard permission-
email template's default terms), `Notes` = "email permission (issue
#1557)".

N=306 low-income mothers, two combined RCTs (2003-2010), up to 4 waves
(baseline/14wk/22wk/26wk, not all retained at every wave; 957 person-wave
rows total). `data/santos_2018_maternal_depression.py` writes 2 tables:
- `santos_2018_gse.csv` — 10-item Generalized Self-Efficacy scale
  (columns `gse2`/`gse4`/`gse5`/.../`gse18`, kept as-is since they're the
  item numbers from the source instrument's larger bank, not positions),
  1-4 range. `GSEcomponent` (a PCA composite of these 10 items, per the
  paper's own network-analysis Methods) is a derived score, not a raw
  item — excluded.
- `santos_2018_cesd.csv` — 20-item CES-D depression scale, 0-3 range.
  `CESDtot` (aggregate sum) excluded.

Both files carry `wave` (`time`, 1-4, already ascending) and `treat`
(`RX`, mapped from the paper's "2=intervention, 1=control" coding to the
standard 1/0, confirmed constant per id across waves). The sentinel
value `9` appears 1-2 times on literally every item in both scales,
consistent with a missing-data code sitting outside each scale's
documented range — filtered out per the per-item rare-value check,
along with two isolated `4`s on `cesd12`/`cesd13` (otherwise 0-3). No
imputation involved — the paper's own text ("we estimated GGMs ... using
pairwise complete observations") confirms the shared raw file is
pre-imputation.

**Closed out (2026-07-29, ben-domingue)**: both tables uploaded to
Redivis and the tab-delimited dictionary rows confirmed pasted into the
dictionary sheet; `dictionary_fix_santos_2018.csv` deleted.

**Paste format fix (2026-07-29)**: ben-domingue reported the dictionary
rows didn't paste cleanly into the Google Sheet — comma-CSV quoting
around `Description`/`Reference` (both routinely contain commas: author
lists, "13(1), e0191675" style citations) isn't honored by Google
Sheets' plain clipboard paste, which splits on every literal comma and
shifts `License`/`Contributor`/`Date` out of alignment. Rewrote
`dictionary_fix_santos_2018.csv` tab-delimited (real `\t`, no quoting
needed since no field contains a literal tab) and documented this as the
standard going forward in `SKILL.md`. Use tab-delimited for all future
`dictionary_fix_*`/`biblio_*` staging files, not comma-CSV.

## PLOS ONE batch 9 (2026-07-29)

Fresh discovery run following the same pattern as batches 6/8: 28 new
instrument/construct/task terms not previously searched against PLOS ONE
(General Health Questionnaire, Life Orientation Test, Attention Network
Test, Trail Making Test, Tower of London Task, Narcissistic Personality
Inventory, Machiavellianism Scale, Empathy Quotient, Marlowe-Crowne Social
Desirability Scale, Rejection Sensitivity Questionnaire, Behavioral
Inhibition/Activation Scale, Operation Span Task, Mental Rotation Task,
Epworth Sleepiness Scale, Kessler Psychological Distress Scale, WHO-5
Well-Being Index, Meaning in Life Questionnaire, Three-Factor Eating
Questionnaire, Dutch Eating Behavior Questionnaire, Dyadic Adjustment
Scale, Parental Bonding Instrument, Child Behavior Checklist, Test
Anxiety Inventory, Job Satisfaction Survey, Perceived Organizational
Support Scale, Prisoner's Dilemma Game, Social Value Orientation Scale,
System Justification Scale; logged in `search_terms_log.csv`). A few
terms initially considered (Iowa Gambling Task, Corsi Block-Tapping Task,
Reading Span Task, Dictator Game, Public Goods Game, Continuous
Performance Task) were swapped out because they'd already been searched
via `irw_discover_updated.py` in an earlier batch (different source/
mechanism, but kept the term list maximally novel for this pass anyway).

1,261 candidates -> 7 `good` + 184 `human_assistance` + 25
`not_item_response` + 7 `download_failed`/`error`. Retriage
(`irw_retriage_ha.py`) on the `human_assistance` bucket gave 24
`worth_retrying` + 1 `recoverable_format` + 63 `human_review` + 68
`aggregate_continuous` + 28 `not_item_response`.

**Good-candidate review** (all 7 hand-checked against the full article
text and Supporting Information file list, per SKILL.md's "needs a human
glance more than usual" note): 5 processed -> 9 tables, 1 skipped, 1
deferred.
- `xiong_2025_dass21` (`10.1371/journal.pone.0316703`, DASS-21 TMD
  study): DASS-21 (21 items, 0-3) merged across two independently-
  recruited samples (Wave 1 N=519, Wave 2 N=455) since Methods text
  confirms identical wording/scale in both; id offset per sample,
  `cov_sample` added rather than a `wave` column (different people, not
  repeat measures). The paper's "5Ts" TMD-symptom items were dropped: the
  text describes them as binary yes/no in both waves, but the raw Wave 2
  columns actually contain values 0-3 -- inconsistent with the paper's
  own description, so left out rather than guessed at.
- `su_2025_health_behaviors` (`10.1371/journal.pone.0333086`): 19-item
  ad hoc student health-behaviour-influence inventory (1-5 Likert), N=150.
  Not a named standardized instrument, but the paper reports Cronbach's
  alpha=0.889 across the full set, confirming it's treated as one
  coherent measure rather than 19 unrelated single-item ratings. An
  unexplained extra "Age" column (values 1-5, inconsistent with the
  actual "What is your age?" item) was dropped rather than guessed at.
- `wakui_2023_who5` (`10.1371/journal.pone.0294357`, aroma-seal-mask RCT):
  WHO-5 (5 items, 0-5) at baseline and 2-week follow-up, N=61, `wave`
  column for the two timepoints. Caught in review: the article's other SI
  file, ostensibly DASS-21 data, actually contains only pre-computed
  subscale totals (Total/Anxiety/Depression/Stress), not raw items -- not
  shipped, per datastandard.md's "verifying a continuous-looking column
  is actually a raw response" check. `Group` (aroma vs. placebo, coded
  1/2) kept as `cov_group` rather than `treat` since the article text
  never states which numeric code is which arm.
- `liu_2025_mlq` / `liu_2025_positive_cognition` /
  `liu_2025_learning_motivation` (`10.1371/journal.pone.0330447`, N=345
  Chinese college students): three scales in one Chinese-language raw
  file -- Meaning in Life Questionnaire (9 items, 1-7), Positive
  Cognition (12 items, 1-5), Learning Motivation (16 items, 1-5). Item
  columns relabeled `item_1..` with original Chinese text kept in
  `item_text`, per datastandard.md's non-Latin-column-names edge case.
  `来自IP` (source IP address) dropped as PII, not carried as a covariate.
- `zamzuri_2021_rpap_risk_perception` / `_attitude` / `_practice`
  (`10.1371/journal.pone.0256636`, dengue RPAP questionnaire validation,
  N=253 Malaysian respondents, main Sheet1 sample only): three domain
  blocks on an 8-point scale -- Risk Perception (D, 12 items), Attitude
  (E, 10 items), Practice (F, 13 items). Ships all raw items as
  collected rather than the paper's post-hoc reduced 29-item scoring
  subset. A separate N=67 test-retest subsample (Sheet3) was left
  unprocessed.
- Skipped: `10.1371/journal.pone.0299201` (SoroTouch abacus-training
  cognitive study) -- the flagged "4 items" are derived per-participant
  engagement metrics (usage time, questions attempted, correct answers,
  proficiency level), not raw item responses; N=10 in the SoroTouch arm
  is also too small on its own.
- Deferred (not processed this pass): `10.1371/journal.pone.0307369`
  (situational-motivation/physical-activity EMA study) -- genuine
  event-contingent repeated-measures design (22 people, 519 sessions over
  10 weeks) but the triage-flagged "2 items" turned out to be pre-/post-
  activity report *modules* each containing several sub-ratings, not two
  comparable Likert items; needs the raw file opened and the actual
  per-session item structure mapped before it can be shipped correctly.

All 9 output tables passed the per-item rare-value data-entry-error scan
(clean, plausible-skew distributions, no isolated-to-one-item outliers).
All 9 `irw_output/*.csv` files uploaded to Redivis and removed from disk
(confirmed 2026-07-29, ben-domingue).

**Biblio staging format detour and revert (2026-07-29)**: `biblio_plos_batch9.csv`
was first staged tab-delimited per the standing convention (see the
`santos_2018` entry above), but ben-domingue reported columns shifting on
import. Root cause turned out to be Google Sheets' delimiter
auto-detection guessing comma over tab because of the many literal commas
still present in `Description`/`Reference` text -- the file itself was
confirmed correctly tab-delimited (10/10 rows, 14 fields each). Re-staged
as `.xlsx` to remove delimiter guessing entirely, which fixed the paste --
but ben-domingue then asked to revert entirely to the plain comma-CSV
system used before that morning's tab-delimited change, treating the
santos_2018/batch-9 issues as isolated rather than grounds to change the
standing format. `SKILL.md`'s tab-delimited paragraph (added earlier this
session) was reverted via `git checkout`, and `biblio_plos_batch9.csv` /
`human_review_plos_batch9.csv` were rebuilt as standard comma-delimited
CSV. Both pasted successfully and confirmed by ben-domingue; both files
deleted from the repo. Standing convention going forward: plain
comma-delimited CSV, no special-casing -- see memory
`feedback_dict_format` for the reasoning.

**Not yet reviewed**: 24 `worth_retrying` + 1 `recoverable_format` rows
remain in `plos_batch9_retriage.csv`, not individually hand-checked this
pass (titles/DOIs/n/items preserved in `TODO.md`). Notable ones by size:
`10.1371/journal.pone.0199480` (body image/eating behavior/QoL, N=2096,
65 items), `10.1371/journal.pone.0206800` (Multidimensional Social
Competence Scale psychometric validation, N=734, 40 items),
`10.1371/journal.pone.0169375` (exercise behavior in Chinese cancer
patients, N=350, 138 items), `10.1371/journal.pone.0202818` (trust/
psychological distress, urban poor Accra, N=788).

## PLOS ONE batch 10 (2026-07-30)

Fresh discovery run following the same pattern as batches 6/8/9: 30 new
instrument/construct terms not previously searched against PLOS ONE
(Center for Epidemiologic Studies Depression Scale, Brief Symptom
Inventory, Symptom Checklist-90, Rotter Locus of Control Scale, Ten Item
Personality Inventory, NEO Five-Factor Inventory, Buss-Perry Aggression
Questionnaire, State-Trait Anger Expression Inventory, Snaith-Hamilton
Pleasure Scale, Multigroup Ethnic Identity Measure, Social Provisions
Scale, Cognitive Failures Questionnaire, UPPS Impulsive Behavior Scale,
Sensation Seeking Scale, Toronto Empathy Questionnaire, Frost
Multidimensional Perfectionism Scale, Sport Anxiety Scale, Physical
Activity Enjoyment Scale, Illness Perception Questionnaire, Medical
Outcomes Study Social Support Survey, Basic Psychological Need
Satisfaction Scale, Academic Motivation Scale, Schutte Self-Report
Emotional Intelligence Test, Multidimensional Anxiety Scale for Children,
Positive Mental Health Scale, Cognitive Emotion Regulation Questionnaire,
Zimbardo Time Perspective Inventory, Cyberbullying Victimization Scale,
Compassion Scale, Interpersonal Support Evaluation List; logged in
`search_terms_log.csv`).

907 candidates -> 7 `good` + 162 `human_assistance` + 21 `not_item_response`
+ 4 `download_failed` + 1 each `crashed`/`timeout`/`error`. Retriage
(`irw_retriage_ha.py`) on the `human_assistance` bucket gave 25
`worth_retrying` + 1 `recoverable_format` + 53 `human_review` + 49
`aggregate_continuous` + 34 `not_item_response`.

**Good-candidate review** (all 7 hand-checked against the full article's SI
file list and Methods text, per SKILL.md's "needs a human glance more than
usual" note): 4 processed -> 19 tables, 3 skipped as aggregate-only.
- `baudin_2024_static99r` (`10.1371/journal.pone.0307216`): Static-99R
  actuarial sexual-recidivism risk tool, 9 behavioral items (items 2-10,
  binary/ordinal 0-1 or 0-3 risk factors), N=146 Swedish forensic-psychiatric
  cohort. Item 1 ("Age at release") is a polytomous person-level attribute
  scored from an age-at-release table (18-34.9=1, 35-39.9=0, 40-59.9=-1,
  60+=-3), not a repeated behavioral response like the other 9 -- moved to
  `cov_age_at_release` rather than the item block (ben-domingue catch,
  2026-07-30). 6 binary DIF covariates (psychotic disorder, intellectual
  disability, etc.) also kept as `cov_*`.
- `liu_2022_mice_skills` (`10.1371/journal.pone.0271430`): 16-item
  employability-skills importance rating (1-5 Likert) for MICE
  (meetings/incentives/conferences/exhibitions) management
  students/professionals, N=95. Paper text confirms 120 questionnaires
  distributed, 95 valid (incomplete ones excluded, not imputed) -- ships
  all 16 raw items rather than the paper's post-hoc EFA-reduced subset.
- `alsyouf_2024_*` (`10.1371/journal.pone.0300657`, Jordan/Saudi Arabia
  nurses EHR continuance-intention study, N=472): 12 tables from one rich
  raw file -- 7 UTAUT-based tech-acceptance scales (continuance_intention
  6i, performance_expectancy 5i, effort_expectancy 5i, social_influence 8i,
  facilitating_conditions 6i, management_support 4i, end_user_support 4i,
  all 1-5) plus the full NEO-FFI-3 personality inventory split into its 5
  factor subscales (neuroticism/extraversion/openness/agreeableness/
  conscientiousness, 12 items each, 1-5). Column-prefix legend (CI/PE/EE/
  SI/FC/MS/EUS/N/E/O/A/C) confirmed directly from the paper's Sec. 2.3
  text, not guessed from column names alone.
- `ozkurt_2026_*` (`10.1371/journal.pone.0353067`, elite Turkish wrestlers,
  N=374): 5 tables -- ego_orientation (10i, 1-5), basic_psych_needs (14i,
  1-5, matches the BPNS search term), sport_motivation (16i, 1-7),
  paces_enjoyment (8i, 1-7, matches the PACES/Physical Activity Enjoyment
  search term), continuance_intention (6i, 1-7). Used the article's
  `S2_File.sav` (clean EGOQ/BPNS/SMS/PACES/INT column labels via SPSS
  variable labels) rather than the triage-flagged `S1_File.xlsx`, whose
  headers were ambiguous/incomplete for the same underlying data (missing
  item 1, per-column "Ego Orientation"/"Task Orientation" captions instead
  of a clean prefix) -- caught exactly the "needs a human glance more than
  usual" scenario SKILL.md warns about. A 3rd SI file (qualitative
  interview excerpts) was not used.
- Skipped (aggregate-only, not raw items -- all 3 confirmed by opening the
  actual SI file, not just the triage flag): `10.1371/journal.pone.0199118`
  (mobile depression-screening app) -- columns are 3 different algorithm
  total scores plus a single PHQ-9 total, no item-level PHQ-9 responses;
  `10.1371/journal.pone.0253779` (flicker-light altered-states study) --
  file has only a Tellegen Absorption Scale total and 5 NEO-FFI-2 factor
  scores, N=24, no raw items; `10.1371/journal.pone.0243209` (emotion
  regulation/face recognition) -- Face Memory columns are aggregated
  signal-detection outcome counts (Hit/Miss/Misid/CR/FPS/Acc) and the ERQ
  columns are subscale means (Reappraisal/Suppression), not per-trial or
  per-item raw responses.

All 19 output tables passed the per-item rare-value data-entry-error scan
-- several scales show low counts of "1"/"2" spread across most items in
the same scale (the expected tail of a skewed Likert distribution, not an
isolated-to-one-item anomaly). `biblio_plos_batch10.csv` (19 rows) staged
for the dictionary sheet; `human_review_plos_batch10.csv` (53 rows) staged
for the "human eye" sheet. All CC BY 4.0.

**Not yet reviewed**: 25 `worth_retrying` + 1 `recoverable_format` rows
remain in `plos_batch10_retriage.csv` (not individually hand-checked this
pass) -- same deferred-backlog pattern as batch 9's tail.

## PLOS ONE batch 10 worth_retrying pass (2026-07-30)

Hand-reviewed all 25 `worth_retrying` + 1 `recoverable_format` rows left
over from batch 10 (`plos_batch10_retriage.csv`). Downloaded and opened
every candidate's actual SI file rather than trusting the triage row's
`n_items` count, which repeatedly turned out to be counting composite/
total-score columns as if they were raw items.

**5 processed -> 13 tables:**
- `mavromoustakos_2016_*` (`10.1371/journal.pone.0161272`, flying phobia,
  N=115): FASQ (Flight Anxiety Situations Questionnaire, 32 items, 1-5),
  `probability_scale` (perceived probability of flying/general negative
  and positive events, 20 items, 0-100 continuous -- confirmed as "the
  Probability Scale" from the paper's own Methods text, not a "Panic
  Symptoms Questionnaire" despite the `PSQ` column prefix), ZTPI (Zimbardo
  Time Perspective Inventory, 56 items incl. reverse-scored, 1-5).
  `VAR00001` (phobic vs. non-phobic group) kept as `cov_flying_phobic_group`.
- `burns_2018_*` (`10.1371/journal.pone.0203435`, PETALE study, couples
  whose child was treated for leukemia, N=103): DAS-4 and BSI-18 each
  split into father-report and mother-report tables (4 tables total) --
  father and mother are different respondents reporting on their own
  relationship/symptoms, linked by the shared family ID (`PT`).
- `bilotta_2018_*` (`10.1371/journal.pone.0201216`, mindreading in
  narcissistic PD, N=1362): TAS-20 (20 items, 1-5) and SCL-90-R (90 items,
  0-4 -- the paper's text paraphrases the anchors as "1=not at all to
  4=very much" but 0 recurs proportionally on every item, so the raw 0-4
  convention was kept as genuine data, not a sentinel). Two other raw item
  blocks in the file (`IVAMIt1-16`, `xNAR1-9`) are not described anywhere
  in this paper's Measures section (only SCID, SCL-90-R, TAS-20, and the
  MAI clinical interview are) -- left unshipped rather than guessed at.
- `petrowski_2019_sclk9` (`10.1371/journal.pone.0213490`, German norming
  study, N=2502): SCL-K-9 (9 items, 0-4). This was the `recoverable_format`
  row -- file is semicolon-delimited. `-1` filtered as a missing-data
  sentinel (recurs at ~0.2-0.4% on every item, outside the 0-4 range).
- `schalet_2016_*` (`10.1371/journal.pone.0159647`, paroxetine-vs-placebo
  depression RCT, N=180): HRSD, HRSA, and BAI (raw file labels the BAI
  columns `si*`/`s08i*`, identified from the 21-item count and the paper's
  extensive discussion of BAI results), each with `wave` (0=intake,
  1=week-8) and `treat` (1=paroxetine, 0=placebo per `TAF1`). HRSD's
  week-8 assessment included 7 extra items (18-24) not scored at intake --
  kept as wave=1-only item rows, valid per datastandard.md's longitudinal
  rules. Per-item value ranges vary within each scale (e.g. some HRSD
  items 0-2, others 0-4) -- the instruments' own known item-specific
  scoring, not a data-entry issue.

All 13 tables passed the per-item rare-value scan -- flagged low counts
were each item's own natural distribution tail (recurring across most
items in the same scale), not isolated one-item anomalies.
`biblio_plos_batch10_worthretrying.csv` (13 rows) staged for the
dictionary sheet, all CC BY 4.0.

**15 skipped** (aggregate-only or not item-response data, confirmed by
opening the actual file): `10.1371/journal.pone.0150312` (Social Rhythm
cross-cultural, all composite scores), `10.1371/journal.pone.0161840`
(Type A/D personality hypertension, all composite scores),
`10.1371/journal.pone.0181209` (videogame/SDQ study, all subscale
totals), `10.1371/journal.pone.0245113` (ADHD narrative-discourse network
analysis, all composite scores), `10.1371/journal.pone.0272987`
(irrational beliefs/motivation regulation, 6 composite scores only),
`10.1371/journal.pone.0275995` (HIV transmission Vietnam modeling, CES-D
totals + epi covariates, no raw items), `10.1371/journal.pone.0277516`
(passive-sensor personality-network study, derived network metrics
only), `10.1371/journal.pone.0282406` (hyperbaric oxygen fibromyalgia
RCT, SF-36/BSI-18/MOS all subscale totals despite a banner-row layout
that looked promising), `10.1371/journal.pone.0302350` (psychotropic
non-adherence Uganda, categorical/derived vars only, also had a PII phone
number column), `10.1371/journal.pone.0307744` (leisure physical
activity/happiness, composite scores only), `10.1371/journal.pone.0311889`
(dance and wellbeing -- turned out to be a systematic-review table of
included studies, not participant-level survey data at all),
`10.1371/journal.pone.0124364` (temperament/autistic traits, AQ/EAS/FCB
all composite totals), `10.1371/journal.pone.0262465` (HEXACO-100
test-retest, only the 6 factor totals present, not the 100 raw items),
`10.1371/journal.pone.0234997` (longitudinal mental health Germany/
Russia/China, all composite BL/FU scores despite the 2-wave structure),
`10.1371/journal.pone.0203336` (spirituality in pain medicine, BSI/FSB
subscale totals + physiology measures only).

**5 deferred** (real item-level data present but needs dedicated codebook
time beyond this pass): `10.1371/journal.pone.0230103` (French
school-subject self-concept study, 249 cols, 5 parallel ~33-item domain
scales -- Ecole/Maths/Francais/Anglais/EducPhy -- plus Big Five-like and
other blocks; has a `Date de naissance` DOB/PII column to strip first);
`10.1371/journal.pone.0272095` (Dutch self/other/meta-perceptions of
personality, 1086 cols, multi-rater HEXACO facet items with `_1`/`_2`/...
rater suffixes); `10.1371/journal.pone.0159386` (chronic fatigue
neuromuscular-strain study, 187 cols, 5 symptom items x many timepoints
from baseline through 24hrs post-maneuver -- a genuine wave-structured
design but needs the full timepoint list mapped); `10.1371/journal.pone.0184488`
("Lab meets real life" thought-sampling study, N=43, `t0`/`t6` and
`DoM`/`ToM`/etc. column labels not explained anywhere in the paper text
found so far); `10.1371/journal.pone.0256916` (psychosomatic
rehabilitation gender-effects study, 494 cols with cryptic `N7`/`N1`-
suffixed variable names, no clear raw-item naming pattern found).

## PLOS ONE batch 11 (2026-07-30)

Fresh discovery run following the same pattern as batches 6/8/9/10: 30 new
instrument/construct terms not previously searched against PLOS ONE (Penn
State Worry Questionnaire, Social Phobia Inventory, Liebowitz Social
Anxiety Scale, Yale-Brown Obsessive Compulsive Scale, Padua Inventory,
Hewitt Multidimensional Perfectionism Scale, Multidimensional Body-Self
Relations Questionnaire, Eating Disorder Inventory, Yale Food Addiction
Scale, Multidimensional Health Locus of Control Scale, Illness Attitude
Scales, Whiteley Index, Short Health Anxiety Inventory, PHQ-15, Beck
Hopelessness Scale, Columbia Suicide Severity Rating Scale, Social
Support Questionnaire, De Jong Gierveld Loneliness Scale, Need to Belong
Scale, Social Connectedness Scale, Conflict Tactics Scale, Dysfunctional
Attitudes Scale, Automatic Thoughts Questionnaire, Ruminative Response
Scale, Anxiety Sensitivity Index, Flourishing Scale, Subjective Happiness
Scale, Oxford Happiness Questionnaire, Coping Self-Efficacy Scale,
Copenhagen Burnout Inventory; logged in `search_terms_log.csv`).

634 candidates -> 4 `good` + 107 `human_assistance` + 7 `not_item_response`
+ 13 `download_failed` + 2 `error` + 1 `timeout`. Retriage
(`irw_retriage_ha.py`) on the `human_assistance` bucket gave 19
`worth_retrying` + 28 `human_review` + 41 `aggregate_continuous` + 19
`not_item_response`.

**Good-candidate review**: all 4 hand-checked; 3 processed, 1 retracted.
- `teicher_2015_mace` (`10.1371/journal.pone.0117423`) -- **retracted
  2026-07-30** (ben-domingue catch): the triage-flagged S4/S5/S6 files are
  blank Excel *scoring templates* for the MACE instrument (hence tiny
  N=9/12/24), not participant data -- caught exactly the "needs a human
  glance more than usual" scenario, and the real dataset (S11_File,
  N=1051) was initially shipped as 10 items (maltreatment type) x 18
  waves (age). But the paper's own text states MACE severity scores were
  "developed... using item response theory to gauge severity of
  exposure" -- these are IRT-calibrated severity weights, not raw
  responses to a single question, which is why per-type values cluster
  on even numbers (0,2,4,6,8,10) rather than spanning the full integer
  range. Same category of problem as the `stenson_2021_sleep_emotion`
  retraction (batch 6/7): a derived index shipped as if it were `resp`.
  `data/teicher_2015_mace.py` deleted, `irw_output/teicher_2015_mace.csv`
  removed, dropped from `biblio_plos_batch11.csv`. S9_File in the same
  article *does* contain genuine raw binary (0/1) lifetime-endorsement
  items behind MACE's scoring (`Swore`, `Hit`, `Fondled`, `Pushed`, ~70
  candidate columns total, plus paired `_Helpless`/`_Terrified` distress
  ratings and `_sib`/peer/adult variants) -- a promising raw dataset, but
  properly separating item vs. covariate columns across ~70 candidates is
  new work for a future session, not done here.
- `xu_2016_pqb` (`10.1371/journal.pone.0148935`, N=505): Prodromal
  Questionnaire-Brief Version, 21 items, 0-5 (Chinese adaptation uses a
  0-5 severity scale rather than the original's binary format). `NUM`
  used as id since `DATE` (the first column) was not unique.
- `fredrickson_2015_mhcsf` (`10.1371/journal.pone.0121839`, N=122):
  Mental Health Continuum-Short Form, 14 items, 0-5. One cell held a
  literal `'.'` missing-value placeholder, handled by the standard
  `to_numeric(errors="coerce")` + dropna path.
- `milavic_2019_psisysf` (`10.1371/journal.pone.0220930`, N=304):
  Psychological Skills Inventory for Sports Youth-SF, 18 items, 1-5. A
  trailing all-NaN column literally named `#########` (Excel
  column-width overflow artifact) dropped.

**worth_retrying pass**: hand-reviewed all 19 rows plus re-confirmed
`10.1371/journal.pone.0234997` was already skipped in batch 10 (same
paper, different search term). 5 papers processed -> 18 tables.
- `tanck_2021_edeq` / `tanck_2021_bcq` (`10.1371/journal.pone.0257303`,
  N=73): pre/post full-body mirror exposure. BCQ (23 items) is
  straightforward; EDE-Q (28 raw columns) needed a closer look after
  ben-domingue asked about item 13-15 values up to 20 (not 0-6) --
  confirmed against the paper's own text: "the EDE-Q consists of 22 items
  which are rated on a Likert scale from 0 to 6," and 12+10=22 of the 28
  raw columns (items 1-12, 19-28) are indeed bounded 0-6 in the data.
  Items 13-18 are the instrument's separate frequency-count questions
  (e.g. number of binge/vomiting/exercise episodes out of the past 28
  days) -- real EDE-Q items, just not part of the 4 subscale totals this
  paper computed, so genuinely legitimate at values up to 20-28 rather
  than a data error. Kept in the same file per the "ship all raw items
  from the instrument" precedent (`liu_2022_mice_skills`, batch 10) since
  they're still real responses on the same questionnaire form, just a
  different response format than the 0-6 items. Source column numbering
  is zero-padded at `_pre` but not `_post` -- normalized to a shared item
  label.
- `aguirre_camacho_2021_shai` / `aguirre_camacho_2021_champion`
  (`10.1371/journal.pone.0249562`, N=244/442): Short Health Anxiety
  Inventory (18 items, 0-3) and Champion Breast Cancer Fear Scale (8
  items, 1-5, with a wave=1 retest subsample n=78). **Caught in QC**: the
  per-item rare-value scan surfaced fractional values (e.g. 2.71, 3.39)
  on both scales -- the paper's own Methods text confirms EM-algorithm
  imputation was applied to missing values (~1.3% of cells) in this same
  file before analysis. Filtered to integer-only `resp` (imputed cells
  are the non-integer ones); ~0.2-0.4% of cells dropped per scale.
- `conner_2017_*` (`10.1371/journal.pone.0171206`, N=171, fruit/vegetable
  RCT, 3 arms kept as `cov_condition`): 7 tables -- CES-D, HADS-Anxiety,
  Flourishing Scale, Vitality (0-100 continuous VAS), Curiosity and
  Exploration Inventory, Life Orientation Test (all baseline+follow-up),
  and Big Five Inventory (baseline only). A handful of isolated
  non-integer cells (5 total across ~24,000, no imputation language in
  this paper) filtered as data-entry errors on the non-VAS scales. The
  daily-diary mood items (6 adjectives x ~13 days) not shipped -- needs
  day-by-adjective mapping.
- `shi_2025_*` (`10.1371/journal.pone.0331084`, N=196, mindfulness-vs-
  control RCT, 3 waves pre/post/3-month): 5 tables -- MAAS, BRUMS,
  DASS-21, RRS, Resilience (27 items). `组别`/Group kept as `cov_group`,
  not `treat` -- paper confirms a 98/98 split but never states which
  numeric code is which arm (same ambiguity as `wakui_2023_who5` in batch
  9). **Caught in QC**: MAAS item 9 had one `42` and item 8 one `8`
  (valid range 1-6); RRS items 9 and 16 each had one `5` (valid range
  1-4) -- isolated single data-entry errors against hundreds of
  legitimate responses on those same items, filtered out.
- `reinwarth_2023_loneliness3` / `reinwarth_2023_phq4`
  (`10.1371/journal.pone.0279701`, N=2465/2464, German representative
  population sample): 3-item brief loneliness scale and PHQ-4, both
  confirmed via the file's own German variable labels
  (`meta.column_names_to_labels`). An 8-domain importance/satisfaction
  battery, the validated FLZ life-satisfaction questionnaire, and an
  unidentified 6-item block in the same file were not shipped -- would
  need per-domain label translation or instrument identification beyond
  this pass.

All 18 tables passed the per-item rare-value/imputation scan after the
two fixes above. `biblio_plos_batch11.csv` (21 rows: 3 good + 18
worth_retrying, after the `teicher_2015_mace` retraction above) staged
for the dictionary sheet, all CC BY 4.0. `human_review_plos_batch11.csv`
(28 rows) staged for the "human eye" sheet.

**10 skipped** (aggregate-only or not item-response shaped, confirmed by
opening the file): `10.1371/journal.pone.0307349` (German caregiver
trait-anxiety study, all composite totals), `10.1371/journal.pone.0171186`
(fibromyalgia QoL SEM, all composite totals), `10.1371/journal.pone.0189808`
(gastric cancer/caregiver social support, all composite totals),
`10.1371/journal.pone.0190292` (Floatation-REST, mostly composite/VAS
totals; a small ambiguous ~43-item `sec_*` block with only 51/151 rows
complete not pursued), `10.1371/journal.pone.0284769` (chocolate/muscle
pain, repeated VAS pain-intensity readings over time under 3 chocolate
conditions -- a psychophysics time-series, not item-response-shaped data),
`10.1371/journal.pone.0350293` (DBS-for-OCD QoL, only 4 columns, YBOCS/QLES
totals despite a longitudinal structure), `10.1371/journal.pone.0256001`
(chronic pain RCT, all T1_/T2_ composite subscale totals),
`10.1371/journal.pone.0122311` (facial disgust/estradiol, Hits/FA/Pr are
signal-detection summaries across trials, not raw per-trial responses),
`10.1371/journal.pone.0304132` (international-students mental health, ad
hoc mixed-type items with no shared validated scale, N=87; the paper's
secondary N=201 dataset also composite-only), `10.1371/journal.pone.0270464`
(role-stress/burnout Hong Kong, Int/Ext/Total are per-wave composite
behavior scores plus latent-growth-curve model parameters, not raw
items).

**4 deferred** (real item-level data present, needs more codebook time):
`10.1371/journal.pone.0257577` (disordered-eating-in-athletes prospective
study, N=802, 3 waves, ~20 subscale prefixes incl. EDI Drive-for-
Thinness/Body-Dissatisfaction and EDE-Q C/R/S/W/X blocks in one 665-column
file); `10.1371/journal.pone.0350928` (psychological-crisis-coping/
physical-activity study, N=1051, clean 2-row header revealed rumination
[22 items, 3 subscales], PA [3 items], CC [32 items, 4 subscales], ER [14
items, 2 subscales] blocks, but subscale semantic identity needs the
paper's codebook); `10.1371/journal.pone.0279701`'s remaining q11/q12/q13
domain-importance/satisfaction/FLZ battery and unidentified q18 6-item
block (loneliness3/phq4 already shipped from this same file, see above);
`10.1371/journal.pone.0291207` (coping-self-efficacy/sex-trafficking
study) -- confirmed to be the same dataset already flagged deferred in
batch 6's `TODO.md`, not re-investigated.

## PLOS ONE batch 12 (2026-07-30)

**Term selection change**: for the first time, terms were pulled from
`search_terms_log.csv` rows already run against *other* discovery sources
(Dataverse/Zenodo/OSF/etc.) but never against PLOS -- a different search
surface, so reuse isn't a duplicate query, and these terms are
already-validated real instrument/construct/task names rather than fresh
guesses. Filtering the log to non-PLOS, English-only, not-yet-tried-on-PLOS
rows turned up ~1,200 candidates in one pass; 30 were used this batch (see
`TODO.md` for the remaining pool). New rule documented in `SKILL.md`'s PLOS
section.

30 terms (Iowa Gambling Task, Corsi block-tapping task, dot-probe task,
global-local task, Navon task, Posner cueing task, prospective memory
task, reading span task, Simon task, stop signal task, task switching,
visual search task, attentional bias task, continuous performance task,
Multi-Source Interference Task, dual-task performance, emotional Stroop
task, spatial Stroop task, numerical Stroop task, dictator game, public
goods game, Domain-Specific Risk-Taking Scale, Problem Gambling Severity
Index, Job Crafting, envy scale, curiosity scale, grief scale, Fagerstrom
Test for Nicotine Dependence, Multidimensional Assessment of Interoceptive
Awareness, Pain Catastrophizing Scale; logged in `search_terms_log.csv`).

1,556 candidates -> 6 `good` + 205 `human_assistance` + 54
`not_item_response` + 10 `error` + 5 `download_failed` + 1 `timeout`.
Retriage (`irw_retriage_ha.py`) on the `human_assistance` bucket gave 40
`worth_retrying` + 63 `human_review` + 76 `aggregate_continuous` + 26
`not_item_response`.

**Good-candidate review**: all 6 hand-checked by opening the actual SI
file(s) -- 2 of the 6 were false positives, matching the standing "good
needs a human glance more than usual" caution.
- `page_2025_portrait10` (`10.1371/journal.pone.0335734`, N=245):
  PORTRAIT-10 complex-health-care-needs tool, 10 items scored 0-4
  ("Answers to questions are scored from 0 to 4 (Likert type)" per the
  paper's own text), administered at baseline and follow-up (`wave`
  1/2). Follow-up missing for 86/245 (35.1%) matches the paper's own
  reported attrition rate exactly -- genuine dropout, not imputation.
  Source file has a 2-row header (banner row + real column names) and
  inconsistent capitalization between baseline/follow-up column names
  (`Alcohol/drug use` vs `Alcohol/Drug use_2`), handled via case-
  insensitive column lookup. Script: `data/page_2025_portrait10.py`.
- `penningroth_2019_pm_goals` / `penningroth_2019_pm_concerns`
  (`10.1371/journal.pone.0216888`, N=89): real-life prospective memory
  task recall study. Each participant free-recalled up to 5 real-life PM
  tasks, each content-coded into 15 goal categories and 15 concern
  categories (binary 1/0 per category). Coding scheme and column meanings
  came directly from the raw file's own "META-DATA" sheet, not inferred.
  `percPMgr`/`percPMcr` (derived % goal-/concern-related) excluded as
  composites; `grpYvsO` (2-group young/older split used in this study)
  kept as a covariate alongside `AgeGroup` (original 3-subgroup coding).
  Shipped as two files (goal vs. concern are conceptually distinct
  motivational categories, matching the paper's own separate
  `percPMgr`/`percPMcr` composites) per `datastandard.md`'s one-scale-
  per-file rule. Script: `data/penningroth_2019_pm_goals_concerns.py`.
- `attnbias_0279360` (video-games/weapons attentional-bias study,
  `10.1371/journal.pone.0279360`) -- **not processed, false positive**:
  all 4 sheets (Accuracy/RT/Caution Scores/Gaming Data) hold per-
  condition aggregated proportions/scores per participant, not raw
  per-trial responses anywhere in the file. Same category of problem as
  `10.1371/journal.pone.0122311` (batch 11) -- a signal-detection-style
  summary, not item-response-shaped data.
- `10.1371/journal.pone.0220622` (ultimatum game neural correlate) --
  **not processed, false positive**: the flagged SI file is
  figure-source-data (one sheet per published figure, e.g. "Figure 1A"
  holding aggregated acceptance rates per fairness condition), not
  participant-level responses. The paper's own Data Availability
  statement points to the real dataset on Figshare
  (`10.6084/m9.figshare.9037808`) -- a lead for the regular repo-based
  pipeline, not re-downloaded here.

**2 deferred** (real item-level data present, needs more time):
- `10.1371/journal.pone.0161858` (MnemoCity Task): file mixes a genuine
  ~8-item usability/satisfaction survey (`US1/US2`, `SA1-4`, `Q3D`,
  `Q2_US1`, `Q2_SA1`, `PRE1`, `PRE2`) with derived cognitive-task-summary
  scores (`Direct/Inverse CBTT Score`, `MnemoCity Score`, `Satisfaction`,
  `Usability` composites) that aren't raw items. Only the survey portion
  looks shippable; needs the paper's Methods text to confirm exactly what
  each survey item asks before writing a script.
- `10.1371/journal.pone.0123625` (children's implicit/voluntary attention
  in time): triage only read the "Demographics" sheet (just ID/Group/Age/
  Sex/Hand covariates, n_items=3 was a mis-read). The real raw data is
  trial-level (336 trials x 62 children: `Trial`, `Delay`, `ISI_value`,
  `Target.RT`, `Validity`) but spread across 62 separate per-participant
  sheets (named `"1"`-`"62"`) that need merging into one long file --
  genuine data, just needs a custom multi-sheet-merge script.

Both ready datasets processed, QC'd (per-item value_counts, id
uniqueness, no PII, correct column order), and staged:
`biblio_plos_batch12.csv` (3 rows, all CC BY 4.0) for the dictionary
sheet; `irw_output/page_2025_portrait10.csv`,
`irw_output/penningroth_2019_pm_goals.csv`,
`irw_output/penningroth_2019_pm_concerns.csv` ready for Redivis upload.

## Teicher 2015 MACE S9_File raw items (2026-07-31)

Follow-up to the batch 11 retraction of `teicher_2015_mace` (which shipped
IRT-derived severity scores as if they were raw responses). The TODO note
left after that retraction flagged S9_File (`10.1371/journal.pone.0117423`,
same article, CC BY 4.0, N=1051) as a genuine raw-item dataset worth a
closer look -- picked up now as the highest-value item in the open
codebook-driven-follow-up list.

While investigating, also opened the S5_File Excel scoring template
(a companion Supporting Information file on the same article, previously
dismissed in batch 11 as a "blank scoring template" -- true for its
Entry/correction/Scored sheets, but its `Reference_sheet` turned out to
hold the full item-to-subscale legend for the instrument: 10 named
subscales (Familial and Non-Familial Sexual Abuse, Parental Verbal Abuse,
Parental Non-Verbal Abuse, Parental Physical Maltreatment, Witnessing
Physical Abuse between parents, Witnessing Abuse toward sibling, Peer
Verbal Abuse+Ostracism, Peer Physical bullying, Emotional Neglect,
Physical Neglect) each listing their plain-English item names. This
confirmed S9's checklist columns are genuine per-event yes/no items
feeding the instrument's IRT scoring (not composites themselves), and
gave a validated basis for grouping S9's ~75 raw item-pool columns into
per-subscale files rather than guessing at groupings from column-name
similarity alone.

S9 is more granular than the reference's collapsed subscale counts (it
keeps parent- vs. other-adult- vs. sibling-directed versions of the same
event separate, where the reference collapses them for final scoring) --
S9's own column names were used as item labels since they're already
meaningful, with the reference used only to confirm construct membership.

**10 checklist tables + 2 distress-rating tables shipped** (all binary
0/1, verified clean per-item via `value_counts()`, no unexpected values):
`teicher_2015_mace_verbal` (4i), `_nonverbal` (5i), `_physical` (6i),
`_sexual` (12i, familial+non-familial+peer combined), `_witness_parent`
(8i), `_witness_sib` (8i), `_peer_verbal` (5i), `_peer_physical` (5i),
`_emot_neglect` (5i), `_phys_neglect` (5i). Plus `_distress_helpless` and
`_distress_terrified` (35 items each) -- subjective distress ratings
asked as a follow-up to 35 of the checklist events; shipped as their own
two files since this is a different response dimension (how it felt) from
the checklist (did it happen), not a new instrument. Source values for
these were a messy mix of `'0'/'No'/'1'/'Yes'/'yes'` -- recoded to 0/1.
Covariates: gender, age, number of siblings, race, ethnicity, own/father's/
mother's/parents' education years, financial sufficiency, and an
interviewed-in-person flag.

**Not shipped, left for a future pass** (noted in `TODO.md`): `Yelled`
(parental verbal item with no match in any of the reference's 10
subscales -- likely a dropped pilot item); the peer items' `Date_*`
columns (binary, paired to each peer item, meaning not confirmed from the
paper text); several household-structure/context columns not clearly
matched to a named subscale (`Separated`, `Divorced`, `P_died`,
`Two_households`, `Foster_care`, `Adult_resposibility`, `Unsuper`,
`P_homework`, `M_unavail_good`, `F_unavail_good`, `Felt_close`); and all
derived/composite columns (`SQ_*`, `DES_SCORE`, `LSCL33`, `ASIQ_tot`,
`*vas` severity scores, `CTQ_*`, `ACE_*`, `MACE_*_EVER`, `MACE_SUM_EVER`,
`emotional_negl_01`...`w_sib_ab_01`, `ATQ_*`) -- excluded on the same
grounds that got the original `teicher_2015_mace` table retracted.

Script: `data/teicher_2015_mace_items.py`. `biblio_teicher_2015_mace.csv`
(12 rows, CC BY 4.0) staged for the dictionary sheet; all 12
`irw_output/*.csv` files ready for Redivis upload.

## Carver 2017 PUGGS genetics-belief questionnaire (2026-07-31)

Second item picked up from the open codebook-driven-follow-up list
(`10.1371/journal.pone.0169808`, CC BY 4.0). Re-downloaded and re-read the
SI files fresh this session (the DOCX codebooks referenced as "already
downloaded" in the prior note were in a session-scoped scratchpath from
an earlier session, no longer on disk).

Two pilot studies (S5/S6 Tables, N=207 and N=78), each with its own Code
Book (S4/S2 Text). **Key finding: the two pilots use genuinely different
response formats for the "core ideas" items** (confirmed from their own
codebooks, not assumed from matching item content) -- pilot 1 uses a
4-point Likert agreement scale per true/false-keyed statement; pilot 2
uses a direct True/False/Don't-know choice. Per `datastandard.md`'s
same-instrument-multiple-sub-studies rule (identical administration must
be confirmed before merging), these were kept as separate per-pilot
files, not merged.

**8 tables shipped**:
- `carver_2017_puggs_pilot1_traits` / `_pilot2_traits`: "Table of Traits"
  items (rate genetic vs. environmental influence on a named trait, 1-5,
  higher=more genetic). Pilot 1's codebook also gives a scientifically
  "expected" answer per trait -- kept as `itemcov_expected_answer` (an
  item attribute, not a derived score). Pilot 2 has no such key and one
  fewer trait (17 vs. 20).
- `carver_2017_puggs_pilot1_det_core` / `_genom_know` (13i/18i, 1-4
  Likert): raw agreement ratings shipped as-is, NOT recoded to the
  codebook's own "determinism"/"understanding" direction -- that would be
  exactly the kind of reverse-scoring flip `datastandard.md` says not to
  apply ourselves (direction is allowed to vary across items).
- `carver_2017_puggs_pilot2_det_core` / `_genom_know` (9i/16i): pilot 2's
  raw True(1)/False(2) codes have no inherent ordinal direction, so
  (matching `datastandard.md`'s own worked example for a true/false/
  don't-know financial-literacy quiz) these were recoded to
  correct(1)/incorrect(0) using the paper's own answer key; don't-know(3)
  and missing(99) were filtered as genuine non-response, not scored as
  incorrect (the paper's own codebook conflates the two for its own
  analysis -- overridden here per `datastandard.md`'s explicit guidance).
- `carver_2017_puggs_pilot1_attitudes` / `_pilot2_attitudes` (20i each,
  1-4 Likert): raw agreement, unmodified.

Sentinel handling confirmed against the actual data, not just the
codebook: pilot 1 uses `99` as an additional true-missing code on top of
each item's own built-in "don't know" option (6 for the TT block, 5 for
Q-items); pilot 2 uses `99` throughout. A single out-of-range pilot-1 Age
value (`5`, codebook only defines 1-4) was set to missing as a covariate-
cleaning step (doesn't affect any item data). All 8 files QC'd (per-item
value_counts, correct ranges, no covariate leakage into items).

Script: `data/carver_2017_puggs_items.py`. `biblio_carver_2017_puggs.csv`
(8 rows, CC BY 4.0) staged for the dictionary sheet; all 8
`irw_output/*.csv` files ready for Redivis upload.

## Meloni 2015 disability-representations study (2026-07-31)

Third item from the open codebook-driven-follow-up list
(`10.1371/journal.pone.0128876`, CC BY 4.0, N=152: 76 parent-child dyads).
Re-downloaded both SI files fresh (S1 File data, S2 File codebook -- a
legacy `.doc`, converted to text via `soffice --headless --convert-to txt`
since `python-docx` only reads `.docx`).

**9 tables shipped**, split parent-population (`id` 101-181) vs.
child-population (`id` 201-281) throughout, since the two groups answer
via different response modalities (parents: numeric scale; children: a
smiley-face card) even where item content is shared -- not assumed
equivalent, kept separate:
- `meloni_2015_deq_oe_parent` / `_child` (36 items: 9 coded disability-
  model categories x 4 stimuli). **Not a 0/1 presence flag** despite the
  codebook's description of the paper's own *published* scoring table --
  raw values in this file range 0-8, a count of coded mentions per
  model/stimulus before the paper's own presence/absence collapse.
  Shipped as raw counts; the paper's own binary collapse was not
  re-derived.
- `meloni_2015_deq_ce_parent` / `_child` (44 items: 11 statements x 4
  stimuli, 1-4 with half-points allowed per the codebook, confirmed
  genuine in the data).
- `meloni_2015_parent_divers_ed` (60 items: 12 statements x 5 image
  stimuli, 1-5) and `meloni_2015_parent_interests` (25 items, 1-5),
  parent-only.
- `meloni_2015_child_disab_knowledge` (16 items, 1-4 w/ half-points) --
  `itemcov_keyed_true` marks whether the statement is true-keyed
  ("knowledge") or false-keyed ("stereotype") per the codebook; raw
  agreement shipped either way, no correct/incorrect recode (unlike
  Carver 2017 pilot 2 -- these are attitude/endorsement items by the
  paper's own design, not a scored quiz).
- `meloni_2015_child_ia_satisfaction` / `_ia_frequency` (20 items each,
  1-5): the same 20 activities have two response dimensions in the raw
  file -- a preference ranking and, despite the confusing `_TIME` column
  suffix, the codebook's own "how often" frequency scale (not a response
  time). Shipped as two files.

A `0` value appears at a low, consistent rate (~0.3-1.5%) across every
1-4/1-5 rating block, below each scale's documented floor -- a missing-
response sentinel used throughout the file (not isolated to one item),
filtered out. All 9 files QC'd (per-item value_counts, correct ranges,
`id` correctly partitioned by population).

Script: `data/meloni_2015_disability.py`. `biblio_meloni_2015_disability.csv`
(9 rows, CC BY 4.0) staged for the dictionary sheet; all 9
`irw_output/*.csv` files ready for Redivis upload.

## Peters 2025 COVID-19 Risk Tool: precaution-checklist follow-up (2026-07-31)

Fourth item from the open codebook-driven-follow-up list -- the ~300-column
"risk-estimate/checkbox-array" remainder left undone by the original
2026-07-16/17 session (`work*`/`siCurrent*`/`siTrigger*`/`siIntention*`/
`hwFrequency*`/`hwIntensity*` + paired `*Est` columns, "a different,
not-yet-decoded response mechanism").

**Mechanism, reverse-engineered from the raw data** (not documented in the
project's own build script the way the RAA belief items were): each family
is a LimeSurvey "checkboxes" question, one column per option, holding `Y`
if selected and blank otherwise. The paired `*Est` column is **not a
per-person numeric estimate** despite the name -- confirmed across two
different sids/countries, each `*Est` column takes only 1-2 distinct
values, identical across sids, and those values are the tool's own fixed
internal risk-scoring coefficients for that option (e.g. `hwFrequencyCntctEst`
is always exactly `0` when the respondent washes hands after contact and a
constant `2.7` when they don't -- a risk weight, not a response). Its real
use here is different: `*Est` is non-null exactly when that option was
actually administered to that respondent (this survey uses per-item skip
logic -- e.g. `siIntention`'s own LimeSurvey definition has
`array_filter = "siCurrent"`), and null when never shown. Exhaustively
verified (two sids, ~600 checkbox-cell comparisons): zero rows where the
checkbox is "Y" but Est is null. Decoding rule: Est null -> not
administered (excluded); Est not null & checkbox=="Y" -> resp=1; Est not
null & checkbox blank -> resp=0.

`siTrigger.other.` and `siIntention.other.` are "Other, please specify"
free-text boxes (values are open-ended sentences, e.g. participants' own
written reasons in Dutch/etc, not "Y") -- detected programmatically (not
assumed from naming) by checking each checkbox column's non-null values
are a subset of `{"Y"}`, and excluded as open-text.

**6 tables shipped** (id/date/covariates identical scheme to the sibling
`peters_2025_covid19_risk_dcts.py` script -- `id` = `{sid}-{orig_id}`,
`date` = Unix seconds from `datestamp`): `peters_2025_work_precautions`
(4 items: who you work in contact with), `peters_2025_si_current` (6
items: activities currently done despite self-isolation guidance),
`peters_2025_si_trigger` (4 items, after excluding the free-text option:
what would trigger starting self-isolation), `peters_2025_si_intention`
(5 items, after excluding the free-text option: which activities you'd
resume), `peters_2025_hw_frequency` (7 items: situations prompting hand-
washing), `peters_2025_hw_intensity` (4 items: hand-washing thoroughness).
N ranges ~70,000-75,000 depending on table (matches the DCT tables' scale
-- same underlying ~76-102k-respondent dataset, survey randomization/skip
logic limits how many see each specific item family). All resp values
strictly 0/1, verified per-item with sensible non-degenerate distributions
(no all-0/all-1 items; rare "none"/"never" options behave as expected).

**Not covered** (single-item, can't be shipped as their own scale per
IRW's no-single-item-scale rule): `proximity` (single radiobutton) and
`DMQslider.nr.` (single slider item).

**Aside, not part of this task**: while building the tags/dictionary
entries for these 6 new tables, found that the *existing* 16
`peters_2025_*` tables (from the 2026-07-16/17 session) have zero rows in
`metadata/tags.csv` despite BATCH_LOG recording them as "written directly"
into that file -- the correct rows *do* exist in `metadata/biblio.csv`
(confirmed `peters_2025_att_exp_eval` etc. present with full APA
reference/DOI/BibTeX), just not in tags.csv. Not investigated further
here (likely a metadata-pipeline regeneration or the same Dropbox-sync
loss pattern documented elsewhere in this log) -- flagged in `TODO.md` for
whoever next touches `metadata/tags.csv` or runs the site-update skill.

Script: `data/peters_2025_covid19_risk_precautions.py`.
`biblio_peters_2025_precautions.csv` (6 rows, ODbL 1.0, matching the
license/reference convention the user specified for this paper's earlier
tables) staged for the dictionary sheet; `tags_fix_peters_2025_precautions.csv`
(6 rows) staged in case tags entries are wanted per-table like the
original 16; all 6 `irw_output/*.csv` files ready for Redivis upload.
