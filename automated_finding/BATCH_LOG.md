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

## PLOS ONE batch 13 (2026-07-31)

Continued the term-pool drawdown started in batch 12 (see `TODO.md`'s
"Large pool of recyclable PLOS search terms" item): 30 more terms pulled
from `search_terms_log.csv` rows already run against other discovery
sources but never against PLOS, favoring named instruments/methodology
terms not yet tried (PCL-5, BDI, STAI, SF-36, PROM, PISA, TIMSS, NAEP,
PIRLS, computerized adaptive testing, differential item functioning,
ecological momentary assessment, experience sampling, trolley problem,
distributive justice, moral judgment, economic games, AX-CPT, congruency
effect, conflict adaptation, response inhibition task, acquiescence bias,
careless responding, social desirability, sense of coherence, distress
tolerance, body appreciation, orthorexia, intuitive eating, insomnia
severity; logged in `search_terms_log.csv`). ~1,140 unused terms remain in
the pool after this batch.

1,878 candidates (some terms hit PLOS's per-query cap) -> 17 `good` + 280
`human_assistance` + 1,435 `no_usable_file` + 65 `download_failed` + 37
`timeout` + 28 `not_item_response` + 16 `error`. Note: the background
monitor watching this run undercounted `good`/`human_assistance` in its
live progress notifications (naive `cut -d',' -f7` on a CSV with commas
inside quoted title fields shifts field positions for some rows) -- the
true counts, from `csv.DictReader`, are as stated above. Retriage
(`irw_retriage_ha.py`) on the `human_assistance` bucket gave 72
`worth_retrying` + 92 `human_review` + 72 `aggregate_continuous` + 44
`not_item_response`.

**Good-candidate review**: all 17 hand-checked (fetched full SI file list
per candidate, not just the triage-flagged file, per the standing "good
needs a human glance more than usual" caution). 7 were already resolved
before any download was needed:
- `10.1371/journal.pone.0220622` (ultimatum game neural correlate) --
  same confirmed false positive as batch 12 (figure-source-data, not
  participant-level responses).
- `10.1371/journal.pone.0279360` (video-games weapons attentional bias)
  -- same confirmed false positive as batch 12 (per-condition aggregated
  proportions, not raw per-trial responses).
- `10.1371/journal.pone.0117423` (MACE) -- already fully processed as
  `teicher_2015_mace_*` (see "Teicher 2015 MACE S9_File raw items" above).
- `10.1371/journal.pone.0307216` (Static-99R) -- already fully processed
  as `baudin_2024_static99r` (batch 10).
- `10.1371/journal.pone.0255039` (thinking in pictures, autistic adults)
  -- already fully processed as `bled_2021_imagery_phenomenology`/
  `bled_2021_imagery_use` (batch 6).
- `10.1371/journal.pone.0193861` ("All metrics are equal...") -- not
  item-response data: a systematic-review dataset of included studies
  (papers), not people.
- `10.1371/journal.pone.0174044` (archerfish symbol-value discrimination)
  -- non-human subjects (fish), out of IRW's scope.

**4 papers processed -> 7 tables** (all CC BY 4.0, in
`biblio_plos_batch13.csv`, ready to paste into the dictionary sheet):
- `nelson_2019_ipqrde` (`10.1371/journal.pone.0214082`, N=198): the
  43-item Illness Perception Questionnaire - Revised, Dental Edition
  (IPQ-RDE), a new CSM-framework instrument for older adults' perception
  of dental conditions. 1-5 Likert. A sparse `-9` sentinel (27/8514
  cells, spread across 17 of 43 items) filtered as missing. The file's
  other blocks (`pqx_*`: bundled depression/social-support/OHQOL
  sub-instruments; `ohs_*`: clinician-administered screening findings,
  not self-report) not shipped -- would need separate instrument
  identification.
- `hermans_2015_dm1_rods` (`10.1371/journal.pone.0139944`, N=312): the
  raw Myotonic Dystrophy Type 1 (DM1) activity/participation item bank
  (105 items, `r_ods001`-`r_ods144` naming from the same group's R-ODS
  methodology) used to Rasch-reconstruct the final 25-item DM1-Activ C
  scale -- shipped the full raw item bank rather than only the paper's
  post-selection 25 items, since IRW wants raw responses. 0/1/2 scale, no
  missing values.
- `liu_2025_classroom_interaction` / `_willingness_communicate` /
  `_speaking_selfefficacy` / `_foreign_lang_enjoyment`
  (`10.1371/journal.pone.0328226`, N=623, Chinese EFL students, 1-5
  Likert, no missing): four validated instruments administered in one
  44-item block, each with its own paper-reported Cronbach's alpha --
  Classroom Interaction Scale (Wu & Gao, 11 items: learner-instructor +
  learner-learner dimensions), Willingness to Communicate in English
  Scale (Peng & Woodrow, 10 items), Speaking Self-Efficacy Scale (Wang &
  Sun, 14 items: linguistic/self-regulatory/delivery/performance
  dimensions), Foreign Language Enjoyment Scale short form (Botes et al.,
  9 items: personal/teacher/social sub-scales -- grouped by actual item
  content since the raw column order didn't match the paper's prose
  order). Shipped at one-file-per-named-instrument granularity to match
  the paper's own reliability reporting, not split further by internal
  sub-dimension.
- `wang_2015_donation_decision` (`10.1371/journal.pone.0138219`, N=371,
  China/US cross-cultural donation experiment): 3 raw items (distress,
  sympathy, both 0-7; `Q4WTC` donation amount out of 100, kept as
  collected). Excluded `WTC` (a log-transformed version of `Q4WTC`, the
  paper's own normality-driven transform) and `count` (a derived
  donated-something binary) as composites/transforms.

**3 deferred** (real item-level data present, needs more time):
- `10.1371/journal.pone.0235595` (social evaluation/imitation of
  prosocial/antisocial agents, infants/children, N=124): genuine 3-item
  binary imitation task (`Imitation_pulling mitten off/shaking the
  mitten/putting mitten back on`), but the raw sheet's "Analyzability
  imitation" exclusion column contains stray non-binary values (`21`,
  `23`, `'Age'`, etc.) suggesting a multi-block sheet layout that a
  simple `header=3` read doesn't fully resolve -- needs manual sheet
  inspection before trusting the analyzable-subset filter.
- `10.1371/journal.pone.0277080` (visuo-tactile/visuo-vestibular illusory
  body ownership, N=30): genuine 7-item (`S1`-`S7`) embodiment
  questionnaire administered across 4 conditions, across 3 sheets in the
  same file (a main Questionnaire Experiment + 2 SCR-experiment sheets)
  -- but `S7` shows an out-of-range value (8) against an otherwise
  -3..+3-looking scale, and the actual questionnaire statement text
  (needed for item labels/direction) wasn't yet pulled from the paper.
- `10.1371/journal.pone.0307369` (situational-motivation EMA) -- same
  candidate flagged `good` again (previously deferred in batch 9); still
  unresolved, see batch 9's entry below for the known complexity
  (session-level report modules, not simple Likert items).

**3 not shipped, reviewed and skipped**:
- `10.1371/journal.pone.0201698` (PANAS-C/CASAFS, Spanish children,
  N=390): the SI file only contains subscale-level composite totals (PA,
  and CASAFS's SP/PR/FR/HD), not the underlying 10+24 raw items -- those
  aren't in the file at all.
- `10.1371/journal.pone.0199118` (mobile depression screening app,
  N=20-23): algorithm-validation summary data (cutoffs, a single PHQ-9
  total score), not raw item responses.
- `10.1371/journal.pone.0344731` (selfish intentions, 5-year-olds, N=48):
  the "Liking" ratings are 3 single-item measures of unrelated constructs
  (partner liking vs. an unrelated ice-cream-preference manipulation
  check) -- doesn't form a coherent multi-item scale, and IRW doesn't
  ship single-item measures (`feedback_no_single_item_scales`).

Scripts: `data/nelson_2019_ipqrde.py`, `data/hermans_2015_dm1_rods.py`,
`data/liu_2025_classroom_wtc.py`, `data/wang_2015_donation_decision.py`.
`biblio_plos_batch13.csv` (7 rows) staged for the dictionary sheet;
`human_review_plos_batch13.csv` (92 rows) staged for the "Human eye"
sheet; all 7 `irw_output/*.csv` files ready for Redivis upload.
`plos_batch13_retriage.csv` still holds 72 unreviewed `worth_retrying`
rows (see `TODO.md`).

## PLOS ONE batch 14 — continuous/bounded response-scale search (2026-08-01)

User-supplied term list (direct terminology, method names, research/
methodological angles, combined and emerging terms — 32 terms after merging
near-duplicates) targeting continuous and bounded response measures (VAS,
sliders, thermometers, NRS, graphic rating scales, etc.), run against both
PLOS ONE (this entry) and the repository-connector pipeline (see the
following entry). All 32 terms confirmed unused against every prior
`search_terms_log.csv` row (repo or PLOS) before running — genuinely new.

- Discovery — 32 English terms (no translation; PLOS ONE is English-only) →
  `plos_batch14_triage.csv`: 281 candidates → 2 `good`, 44 `human_assistance`,
  2 `not_item_response`, 2 `error`, 1 `download_failed`. Terms logged in
  `search_terms_log.csv`.
- Both `good` flags were false positives (shape-only match, not content):
  - "Effects of mindfulness-based stress reduction..." (HCC/TACE,
    10.1371/journal.pone.0352434): triage's 22 "items" mix a single
    repeated 0-10 NRS pain score (one item across 4 timepoints — would
    violate the no-single-item-scale rule on its own) with aggregate
    HADS-Anxiety/HADS-Depression/SUPPH-* subscale *totals* (values in the
    20s-30s land in the same resp column as the 0-10 NRS scores, confirming
    they're not comparable items of one scale).
  - "Effects of speculum lubrication on cervical smears..."
    (10.1371/journal.pone.0292207): the 13 "items" are demographic/clinical
    trial variables (age, parity, religion, marital status, etc.), not a
    psychometric instrument.
- Retriage (`irw_retriage_ha.py`) on the 44 `human_assistance` rows →
  `plos_batch14_retriage.csv`: 16 `aggregate_continuous`, 12
  `worth_retrying`, 12 `human_review`, 4 `not_item_response`.
- `human_review_plos_batch14.csv` (12 rows) — ready to paste into the
  "Human eye" sheet.
- All 12 `worth_retrying` rows hand-reviewed (downloaded and inspected each
  SI file):
  - **Processed** — Lopes de Jesus et al. (2017) intra-articular ozone vs.
    placebo knee-OA RCT (10.1371/journal.pone.0179185), CC BY 4.0, N=98
    patients x up to 4 visits (baseline/4/8/16 weeks). One raw file held
    **four** separate instruments, unpacked into 4 tables
    (`data/dejesus_2017_ozone_knee.py`): Lequesne Algofunctional Index (10
    items, mixed 0-2/0-8 per-item ranges incl. half-points), SF-36 (22 raw
    items), **WOMAC (24 items, genuine 0/25/50/75/100 bounded response —
    directly on-topic for this batch's continuous/bounded search)**, and
    the Geriatric Pain Measure (24 items, mostly binary + two 0-10
    intensity items, confirmed via the paper's Methods text as a named
    instrument, not a triage artifact). `id`=patient number, `wave`=week,
    `treat`=1 ozone/0 placebo, `cov_age/sex/schooling/marital_status/
    race/knee` (confirmed baseline-only, constant per patient). Dropped:
    `TUG (seconds)` (single continuous performance test) and a standalone
    `VAS` pain column — both single-item measures, excluded per the
    no-single-item-scale rule.
  - **Skipped — confirmed non-recoverable imputation contamination**:
    "Abdominal symptoms in cystic fibrosis..." (JenAbdomen-CF Score,
    10.1371/journal.pone.0174463, CC BY 4.0, N=131, a genuine new 17-item
    pilot GI-symptom questionnaire with plausible per-item 0-5/0-8/half-point
    ranges). Looked structurally clean, but the paper's Methods explicitly
    states missing values were replaced with zero ("the percentage of
    missing data was only 4.8%"). Since 0 is also the legitimate bottom
    anchor for nearly every item ("never"/"not at all"), genuine-zero and
    imputed-zero responses are indistinguishable in the raw file with no
    separate missingness flag available — not recoverable. Per
    `datastandard.md`'s "Checking for imputed values", this disqualifies
    the file as-is.
  - **Skipped — not item-response data**: "Psychosocial and demographic
    factors influencing pain scores..." (10.1371/journal.pone.0195075,
    mostly-NaN demographics + one single "Pain score" column); "Feasibility,
    acceptability and appropriateness of a reproductive PROM..."
    (10.1371/journal.pone.0256497, open-ended qualitative feedback text
    about survey design, not itemized responses).
  - **Skipped — aggregate/composite scores only**: "Patient reported
    outcomes... osteopathic care" (10.1371/journal.pone.0249719, S1/S2:
    `BQ baseline sum score` is an aggregate sum; GRoC/satisfaction/
    experience are single-item categorical measures at 2 timepoints, no
    multi-item raw block); "Effects and predictors of intravenous
    lidocaine..." (10.1371/journal.pone.0320463: WPI/SSS/rFIQ/DSIS are all
    aggregate composite/subscale-total scores, Worst/Least/Ave NRS are
    single-item pain scores); "Complementary treatment comparison for
    chronic pain..." (10.1371/journal.pone.0256001: T1-T4 columns are
    subscale *totals* — HADS-A, ISI, PDI, PCS/MCS, SOPA subscales — not raw
    items); "Associations between the injustice experience questionnaire
    and treatment termination..." (10.1371/journal.pone.0231077: NRS, NDI,
    HADS-A/D, IEQ, EQ-5D are all single aggregate scores per person, one row
    each, no raw items).
  - **Skipped — too small**: "Development and validation of the facial
    scale (FaceSed)..." (10.1371/journal.pone.0251909) is a genuine 4-item
    observational rating scale (Ears/Eyes/Lower lip/Upper lip, 0-2 each,
    scored by 4 evaluators from photos) but the rated unit is the **horse**,
    not a person, and there are only **7 unique horses** — far below any
    reasonable N threshold (cf. the N=10/N=14 minimums ben-domingue already
    rejected in the PLOS ONE pilot).
  - **Deferred — needs paper's item wording/scale-structure confirmation**:
    "Factors influencing public support for dairy tie stall housing..."
    (10.1371/journal.pone.0216544, CC BY 4.0): two clean between-subjects
    survey samples (S1 N=430 "hours" framing, S2 N=372 "willingness-to-pay"
    framing), each with 6 genuine 1-7 Likert belief items (`b1_morerisky`,
    `b1_lowerquality`, `b1_harmenviro`, `b2_borganic`, `b2_bfamfarm`,
    `b2_bsmallfarm`) plus 3 more (`has1-3`) of unclear relationship — not
    processed because it's ambiguous from column names alone whether `b1_*`/
    `b2_*`/`has*` are one 9-item battery or 2-3 separate subscales (the
    "one file per scale" rule needs this resolved first). See `TODO.md`.
  - **Deferred — low priority**: "Auricular Acupuncture for Exam Anxiety..."
    (10.1371/journal.pone.0168338, N=44, mostly physiological/composite
    STAI-subscale readings across 3 conditions plus a few `vas_*` items —
    small N, needs more untangling than this pass had time for).
- `biblio_plos_batch14.csv` (4 rows, all `dejesus_2017_*`) — ready to paste
  into the dictionary sheet; `irw_output/dejesus_2017_{lequesne,sf36,
  womac,gpm}.csv` ready for Redivis upload.

## Nominal / competitions experimental-standard search (2026-08-01, one-off, ben-domingue-requested)

Ben asked for a one-off search against IRW's two experimental data standards
("nominal" — id/item structure with unordered-category or free-text `text`
responses instead of `resp`; "competitions" — no id/item structure, instead
`agent_a`/`agent_b`/`date`/`homefield`/`score_a`/`score_b`/`winner` head-to-
head event data). Full criteria preserved in memory
`project_alt_data_standards`. **Standing rule going forward: do not
default to searching for this flavor again** — this was explicitly a
one-off, not a new pipeline priority.

Discovery (already run before this session, `irw_discover_updated.py --all`
with the relevance filter disabled since it doesn't recognize sports/MCQ/
essay-scoring language): `candidates_nominal.csv` (6911 data rows, 10 terms:
"multiple choice item distractor", "selected response option data", "essay
scoring corpus", "constructed response scoring", "short answer response
dataset", "automated essay scoring", "open-ended response coding", "free
text response categorization", "choice option dataset survey", "categorical
response coding scheme") and `candidates_competitions.csv` (6078 data rows,
12 terms: "pairwise comparison judgment dataset", "paired comparison
experiment", "head-to-head match results", "two-alternative forced choice
dataset", "game results dataset scores", "tournament match dataset", "Elo
rating dataset", "Bradley-Terry model dataset", "sports match results
dataset", "esports match dataset", "chess games dataset", "model comparison
arena battles").

**This session's work**: neither file can go through `irw_batch_updated.py`/
`irw_triage_updated.py` (built for the ordinal core standard) — did a
title-only keyword scan of the full files instead (regex include list of
on-topic phrases, regex exclude list of the dominant false-positive
clusters: taxonomy/animal-behavior papers matching "distractor"/"multiple
choice" out of context for nominal, and pairwise-comparison-in-biology/
medicine papers matching "pairwise"/"head-to-head" out of context for
competitions). Scripts and shortlists:
- `candidates_nominal_shortlist.csv` (57 rows) — supersedes the earlier
  hand-filtered `candidates_nominal_filtered.csv` (38 rows) as the working
  shortlist; ~30 rows overlap, each file also has some rows the other
  missed (the old file's discrete-choice-econometrics and visual/auditory-
  distractor-psychophysics rows are excluded here as off-topic; two
  plausible misses from the old file worth a manual look later: "AI-
  Enhanced Distractors and Test Quality" (Mendeley 10.17632/45dv52zf7f) and
  "Illustrative AI-Generated and Student-Generated MCQs... Item-Level
  Discrimination Indices").
- `candidates_competitions_shortlist.csv` (53 rows) — supersedes
  `candidates_competitions_filtered.csv` (17 rows) likewise; the old file's
  AHP pairwise-comparison-of-decision-criteria row is kept here as
  ambiguous (criteria don't "win" the way competitions entities do) and
  several Bradley-Terry/pairwise PLOS figshare rows turned out to be
  single supplementary tables of derived model estimates, not raw
  comparison data — excluded.

**License + structure spot-check** (WebFetch against each repo's landing
page / API; not fully downloaded and inspected, so treat as first-pass
screening, not a final accept/reject call):

Nominal — promising:
- **ASAP-SAS Handwritten** (Zenodo 10.5281/zenodo.8088866) — CC BY 4.0.
  Handwritten-response extension of the well-known ASAP Short Answer
  Scoring dataset; single zip archive, not yet opened to confirm per-
  student text + human score columns.
- **Self-Coding open-ended survey data** (Dataverse 10.7910/DVN/E4AJZF,
  "Self-Coding: A Method to Assess Semantic Validity and Bias when Coding
  Open-Ended Responses") — **CC0 1.0**. Real per-respondent open-ended
  survey text in a Stata `.tab` file (`Self Coding Survey Data, for
  Stata.tab`) — best-confirmed nominal candidate found this session, not
  yet downloaded/mapped to id/item/text.
- **COS101 open-ended exam responses** (Figshare
  10.6084/m9.figshare.32109718, "2025/2026 Students' Responses to
  Open-Ended Questions on COS101... FUHSO, Nigeria") — CC BY 4.0. Single
  Excel file of real student exam responses paired with model answers
  (built for an AI short-answer-grading study); not yet opened.
- **Automated Essay Grading Dataset — 2,550 Undergrad Business/Auditing
  Students** (Zenodo 10.5281/zenodo.18856923) — CC BY 4.0, 85 accounting
  questions, but **files are access-restricted** on Zenodo (login/request
  required) — license is fine, access is the blocker.
- **NepAES Nepali essay scoring** (Zenodo 10.5281/zenodo.16760033) — CC BY
  4.0, but the file list (`mbart50_p*`/`nep_p*` CSVs) looks like it may be
  pre-computed embeddings rather than raw essay text — needs a look before
  treating as usable.

Nominal — license-blocked:
- **"Combining Human and Automated Scoring Methods in Experimental
  Assessments of Writing"** (Dataverse 10.7910/DVN/J9KSHU) — **CC BY-NC-SA
  4.0**. NonCommercial clause fails the "explicitly and verifiably open"
  bar (see memory `feedback_license_verification`) — do not process
  without an author-permission email.

Competitions — promising:
- **World Padel Tour historical match data** (Zenodo 10.5281/zenodo.7860242)
  — CC BY 4.0, single `historico_partidos_wpt.csv`, Spanish-language
  scraped match history; not yet opened. Padel is not an already-covered
  sport (see dedup check below) — this is the strongest surviving
  competitions candidate.
- **Chess Game Dataset** (Zenodo 10.5281/zenodo.10344773), **FIDE chess
  game evaluations** (Zenodo 10.5281/zenodo.17636050, 1.2M games), and
  **League of Legends KR High Elo 5v5 Match Data** (Zenodo
  10.5281/zenodo.6636849) — all CC BY 4.0, all real match data, but
  **downgraded to low priority**: chess and League of Legends are both
  already-covered domains in the existing competitions tables (`lichess`,
  `league_of_legends` — see dedup check below), which are broader,
  API-sourced, and presumably better-maintained than these one-off Zenodo
  mirrors. Only worth revisiting if one of these adds something the
  existing source structurally can't (e.g. FIDE's OTB-rated-player pool
  vs `lichess`'s online games) — not assumed true, not checked.
- **Sparse-networks-in-football Elo methodology dataset**
  (tandf Figshare 10.6084/m9.figshare.31049599) — CC BY 4.0,
  `real_data_set.csv` (42.5 MB) — similarly downgraded: football/soccer is
  already covered by `eufootball_2010-2020` in the existing tables, and
  this dataset's own framing (testing Elo-rating *methodology* on real
  data, not a general-purpose match-results release) makes it a worse fit
  than a dedicated match-results source anyway.
- ~~Portfolio salience via Bradley-Terry, Brazilian cabinet positions
  (Dataverse 10.7910/DVN/HJZSIM)~~ — **already in IRW** as
  `zucco2019_portfoliosalience` per the existing-tables dedup check below.
  Struck from consideration; the initial recommendation of this dataset in
  an earlier version of this entry was wrong — caught by ben-domingue
  asking whether the shortlist had been checked against the existing
  competitions/nominal table sheets, which it hadn't been until this
  correction.

Competitions — noise found and excluded (documented so it isn't re-
investigated): PLOS figshare "Bradley-Terry model estimates for
Experiment N" tables (single supplementary result tables, not raw
comparison data); "Elo ratings of the top 20 players" (same, derived
summary table); AHP pairwise-comparison-of-decision-criteria dataset
(criteria, not competitors); several ETF/stock-performance and medical
"head-to-head" datasets that matched the term literally but are unrelated
domains; Leela Chess Zero self-play datasets (12 Kaggle-mirrored Zenodo
records) — technically fit the agent_a/agent_b schema (AI models playing
each other) but weren't license/structure-checked this session, noted
here rather than dropped in case Ben wants synthetic self-play data
considered later.

**Dedup check against existing nominal/competitions IRW tables
(2026-08-01, prompted by ben-domingue)**: the DOI-level exclusion in
`irw_discover_updated.py` only excludes DOIs already in the *core-standard*
IRW dictionary Google Sheet — nominal/competitions tables live in two
separate sheets
([competitions](https://docs.google.com/spreadsheets/d/1WZZYyVC2cmw8CUJM69qP0F_ZlQjQfdkCZbdsG-8mUrs/edit?gid=0),
[nominal](https://docs.google.com/spreadsheets/d/12tM4vADKcUm5LGOGRwQ5_HKkdYa3mZUaKbFUqgs2U_w/edit?gid=0))
that the discovery script never reads, so nothing in this search was
excluded against them. Fetched both and checked the shortlists by hand:
- **Competitions sheet already contains**: `lichess`, `tennis_co_uk`,
  `dota_2`, `MLB_Baseball`, `NHL_hockey`, `cricket`, `debate`,
  `league_of_legends`, `table_tennis`, `badminton`, `ufc`, `olympics`,
  `track_and_field`, `counterstrike`, `starcraft_2`, `cards_bridge`,
  `scrabble`, `go_game`, `poker`, plus DOI-backed
  `collegefb_2021and2022`/`epl_matches_2021-2022`/`nba_2012-2018`/
  `nfl_2010-2019`/`nhl_post1917`/`eufootball_2010-2020`/`mlb_through2023`,
  plus pairwise-comparison entries `bradleyterry2_cems`/
  `elochoice_physical`/`t20_hyper`/**`zucco2019_portfoliosalience`
  (10.7910/DVN/HJZSIM — exact match to a candidate this entry had
  recommended before this correction)**/`guinaudeau2024_largechambers`/
  `friedman2019_risk_*`. Confirmed exact-DOI duplicate: HJZSIM (struck
  above). Confirmed same-domain-already-covered (not exact DOI matches,
  but redundant enough to deprioritize): chess (`lichess`), League of
  Legends (`league_of_legends`), football/soccer (`eufootball_2010-2020`).
  Padel and table tennis/badminton/UFC/track-and-field/olympics domains
  from this session's shortlist did not overlap.
  Sheet also has additional rows with only `Public`/`Private` status
  populated (no table name yet) — not reviewed in detail.
- **Nominal sheet already contains**: `preference_inventory`, `asap20train`
  (ASAP 2.0 argumentative-essay corpus, 10.1016/j.asw.2025.100954 —
  related lineage to but a different DOI/release from this session's
  ASAP-SAS Handwritten candidate), `wilmer-*-rmet-normative-data-set-2022`
  (×2), `himmelstein-berlin_numeracy-2025`, `much_tte_2025_matrixreasoning`,
  `much_tte_2025_concentrationtask`, `borges_brazil_residency_2024_cbt`/
  `_pbt`, `persuade_learningagency` (student persuasive-writing corpus —
  same essay-scoring family as `asap20train`), `blum_2018_imak_nominal`,
  `hachenberger_2025_stroop_main_nominal`/`_pilot_nominal`. No exact-DOI
  overlap with this session's nominal shortlist. The essay-scoring/
  short-answer-corpus domain is not a blank slate (`asap20train` +
  `persuade_learningagency` already cover ASAP-lineage and persuasive-essay
  corpora) — downgrades ASAP-SAS Handwritten to lower priority for the
  same reason as chess/LoL above (closely related to already-covered
  territory, not confirmed to add anything new). **Self-Coding open-ended
  survey data (DVN/E4AJZF, CC0) and COS101 open-ended exam responses
  (Figshare, CC BY 4.0) remain non-overlapping** — different response
  type (survey/exam short-answer coding, not persuasive-essay scoring) —
  and are now the strongest surviving nominal candidates.
  Sheet also has additional rows with incomplete metadata past the first
  13 — not reviewed in detail.

Neither shortlist has been downloaded/converted to IRW format yet — this
session was discovery + first-pass license/structure screening only, per
the "real pass ... not eyeballing all 6912/6163 rows" instruction. See
`TODO.md` for what's left.

**Follow-up (2026-08-01, same day): three surviving candidates downloaded,
opened, and converted to first-draft IRW-format CSVs** in
`automated_finding/output_noncore/` (kept out of `irw_output/` since these
aren't the core ordinal standard; `output_noncore/` gitignored the same
way). Structure confirmed real and clean in all three cases — these are
draft conversions for review, not yet uploaded to Redivis or pasted into
any dictionary sheet, and not yet QC'd against the resp-error/imputation
checks `datastandard.md` requires for the core standard (unclear how many
of those apply verbatim to `text`-column data — worth a decision before
shipping).

- ~~**Nominal — Boydstun (2021) open-ended poverty-cause survey**
  (Dataverse DVN/E4AJZF, CC0 1.0)~~ — **ruled out-of-scope by ben-domingue
  (2026-08-01), reason not recorded.** Was converted to
  `boydstun_2021_povertycause_text.csv`/`_selfcode.csv` (free-text poverty
  attributions + self-coded individual/government_society/other category
  per response); both output files and `data/boydstun_2021_povertycause.py`
  removed. Don't re-surface this DOI as a nominal candidate without
  checking with Ben first on what made it out-of-scope (politically
  charged survey topic? something about the self-coding design not fitting
  the nominal criteria cleanly? unconfirmed either way).
- **Competitions — Costa & Giné (2023) World Padel Tour match history**
  (`data/costa_gine_2023_wpt_matches.py`, source: Zenodo 10.5281/
  zenodo.7860242, CC BY 4.0). File was UTF-16LE with BOM (not UTF-8 as the
  `.csv` extension implied — `file`/`iconv` needed to catch this before
  parsing). 17,661 raw rows (2018-2023, Spanish tour data) -> 17,583
  matches after dropping 78 rows where the winner string didn't cleanly
  match either team ("agent" = a doubles pair, formatted "Player1 /
  Player2"); `score_a`/`score_b` = sets won (parsed from `set1`-`set3`
  columns, matches with a `0-0` placeholder set treated as unplayed);
  `date` = tournament start date converted to Unix time;
  `winner` = `a`/`b`. `homefield` left blank throughout — WPT is a neutral
  pro tour, no home team concept. Extra `cov_tournament`/`cov_year`/
  `cov_category` (Femenino/Masculino)/`cov_round` columns kept.
- **Nominal — COS101 open-ended CS exam responses** (`data/
  cos101_2026_openended.py`, source: Figshare 10.6084/m9.figshare.32109718,
  CC BY 4.0). 294 Nigerian undergrad CS students, 3 open-ended exam
  questions each (privacy/security tradeoffs, computer-virus influence on
  OS security design, microprocessor history) -> 882 id/item/text rows.
  Full question wording is in the source `.xlsx` header row (printed by
  the script, not carried into the output CSV) — needed for an itemtext
  pass later, same as any other table.

None of the three has gone through a human QC pass yet (per-item rare-
value scan doesn't obviously apply to free-text `text` columns the way it
does to numeric `resp`; a person still needs to spot-check for the nominal
equivalent — e.g. gibberish/copy-pasted/off-topic responses, or the
padel score-parsing logic's handling of retired/walkover matches). See
`TODO.md` for the review step.

**Correction (2026-08-02)**: this entry and the one above wrongly claimed
no biblio/dictionary-sheet process exists for these standards — it does,
`metadata/comps_biblio.csv`/`nominal_biblio.csv` (same column format as
core `metadata/biblio.csv`), confirmed as pipeline-regenerated snapshots
of the two Google Sheets Ben linked (rows matched exactly). First drafted
`biblio_comps_padel.csv`/`biblio_nominal_cos101.csv` in *that* format —
wrong target: `metadata/comps_biblio.csv`/`nominal_biblio.csv` is what the
metadata pipeline *produces from* the sheet, not the staging format that
gets pasted into it. Corrected (ben-domingue caught it) to the actual
automated_finding biblio-staging format documented in memory
`feedback_dict_format` (`table, table.lower, Description, URL (for data),
Reference, DOI (for paper), Original License, Custom License, Public
Reshare?, Derived License, Custom License, Notes, Contributor, Date`) —
`costa_gine_2023_wpt_matches` (no associated paper; Reference/DOI point
to the Zenodo deposit itself) and `cos101_2026_openended` (same, points
to the Figshare deposit; single author Temidayo Omotehinwa), both
`Original License`/`Derived License` = CC BY 4.0, `Contributor` =
automated, `Public Reshare?` = Public.

**Uploaded to Redivis (confirmed 2026-08-02, ben-domingue)**: both
`output_noncore/*.csv` files gone from disk as expected — the padel and
COS101 tables are now the first-ever competitions/nominal tables shipped
by this pipeline. `biblio_comps_padel.csv`/`biblio_nominal_cos101.csv`
still need pasting into the respective Google Sheets, and neither table
has had a human QC pass — see `TODO.md`.

## "Human eye" sheet review follow-through (2026-08-01)

Padma K hand-reviewed 31 rows of the "Human eye" tab (all `human_review`
candidates the automated pipeline couldn't confidently column-map) and
marked Decision = Yes/Maybe/No (12/9/10). Went through all 12 Yes rows to
see which were actually processable — a human "Yes" here means "worth a
GitHub issue," not "verified IRW-ready," and it showed: only 5 of the 12
were real, usable item-response data.

**Processed (5 new tables, all QC-clean, license-verified CC0/CC BY):**
- `iandolo_2021_asq.csv` — 40-item Attachment Style Questionnaire, 348
  respondents (Spain/Italy/Japan), cov_country/age/gender/romantic_status.
  Dropped 3 isolated `7`s on a nominally 1-6 scale (data-entry errors, one
  per item, cross-checked per-item per datastandard.md).
- `dasilva_2019_hexaco24.csv` — 24-item HEXACO short form (Portuguese),
  240 respondents, itemcov_dimension/itemcov_reverse_scored from the
  source file's own item→dimension table.
- `mendes_2019_snycq.csv` — 12-item Short New York Cognition Questionnaire
  (continuous 0-100 VAS), 248 respondents × 7 pre/post-scan
  administrations (wave), from the MPI-Leipzig connectome dataset
  (DVN/VMJ6NV). That dataset's Dataverse `termsOfUse` says "CC0 ... with
  the following additional/modified terms and conditions:" and then
  states none — resolved as effectively unrestricted CC0, not a real
  caveat. Canonicalized the source file's inconsistent `specific`/`vague`
  column naming (same bipolar item, labeled differently across
  administration blocks) into one item.
- `tutrin_2020_meq30.csv` — 15-item MEQ-30 mystical-experience subscale
  (0-5 scale), 81 respondents, extracted from one column-block inside a
  190-item Russian Freediving Federation survey (DVN/DEJQM4) where most
  other columns are opaque federation-specific items with no recoverable
  meaning — only the clearly-labeled MEQ-30 block was extracted.
- `lee_2025_nursing_exam.csv` — 50-item binary (correct/incorrect) exam
  responses, 117 examinees (111 nursing students + 6 generative AI
  platforms), DVN/PWV6H2. The triage row had originally picked "Dataset 2.
  Domains of items" (item metadata, not responses) as the data file — the
  real response matrix was "Dataset 1" on the same landing page, sitting
  right next to it.

**Skipped (Yes but not actually usable):**
- DASS-8/12/21 caregivers (figshare 21393054) — every sheet is derived
  statistical output (Mann-Whitney rank tables, CFA-implied correlation
  matrices), no raw item responses anywhere in the file.
- Migration risk questionnaire (DVN/QFNHTI) — a free-text/checkmark
  risk-category cross-tab (destination countries, transport modes), not
  numeric ordinal item data.
- COPSOQ III Czech "Additional file 2" (figshare 31311364) — factor
  loadings and per-item descriptive stats (M/SD/skew/kurtosis) only, no
  raw responses.
- Parental Behavior Inventory (figshare 30445876) — all 8 sheets are
  supplementary tables (loadings, item wording, a blank instrument form),
  no filled-in respondent data.
- AI Decision Dependence & Cognitive Caution 2025 (figshare 30747542) —
  article no longer resolves via the figshare API (404); likely taken
  down or made private since triage ran.

**Discovered as duplicates of already-processed IRW content:**
- Media Freedom IRT (DVN/ENOEQS) — already in the repo as
  `data/MMF_Solis_2020.r` (issue #599), already uploaded.
- Cognitive Assessment Data Matrix (figshare 32519529, "...Anonymized")
  is the **same dataset** as figshare 32114668 ("...DATA_MATRIX_TRANSLATED"),
  already processed in batch 3 as `yandun2026_attention/memory/language/
  logical_thinking` (same 4 authors, identical per-respondent values —
  32114668's raw file has real children's full names in a `NAME` column,
  32519529 is a pseudonymized republish of the exact same rows). Wrote and
  then deleted a redundant `yanduncartagena_2026_cognitive_matrix.py`
  before catching this — comparing against `TITLE`/author name in
  `search_terms_log.csv`-style dedup wouldn't have caught this since it's
  a different DOI; only diffing actual cell values against
  `data/yandun2026_cognitive.py`'s known column-boundary logic surfaced it.
  **While comparing, found a real bug in the already-shipped batch-3
  tables**: `yandun2026_cognitive.py`'s column boundaries for the
  Language/Logical-Thinking subscales are off by one column — `language`
  (cols 14-18) wrongly includes "Relates numbers with clues" (a Logical
  Thinking item per the source header), and `logical_thinking` (cols
  19-21) is missing it, so it only has 3 of the true 4 items. Confirmed
  against the raw header's own group-boundary row (`Language and
  Communication` spans exactly 4 columns, `Logical Thinking` spans 4, not
  5/3). Tracked as an open fix in `TODO.md` — the already-uploaded
  `yandun2026_language`/`yandun2026_logical_thinking` Redivis tables need
  reprocessing.

Biblio rows for the 5 new tables are in `biblio_humaneye_batch1.csv`,
ready to paste into the dictionary sheet.

The 9 Maybe-decision rows were left untouched — per the sheet's own
legend ("Maybe = start github issue and @ someone"), that's a manual
GitHub-issue workflow outside this pipeline, not a processing queue item.

## Continuous/bounded-response repo-based discovery (Batch 21) (2026-08-01)

Same 32-term list as PLOS batch 14 (see that entry), translated into 8
languages, run against `irw_discover_updated.py`'s repository connectors
(Dataverse/Zenodo/OSF/Dryad/Figshare/DataCite/Scholars Portal/SURF).

- English run: 737 candidates, all 32/32 queries completed cleanly.
- International run: 378 candidates, all 256/256 queries (32 terms × 8
  languages) completed — ran ~2h05m in the background.
- Merged + deduped by `doi`: 1,115 → 1,030. Excluded one further row before
  triage: `DVN/EHBGOW` (six `.dta` files up to 1.58GB each) — the same
  file that OOM-killed triage in batches 19 and 20 per the standing
  "no file-size guard" pipeline-improvement note. 1,029 candidates went to
  triage.
- Triage (`irw_batch_updated.py`) crashed twice with no traceback (killed,
  not a Python exception — consistent with an external kill, not a bug)
  before completing; checkpoint/`--resume` picked each one back up cleanly
  with zero rework. Final triage: 4 `good`, 75 `human_assistance`, 13
  `not_item_response`, 887 `no_usable_file`, 23 `license_restricted`, 25
  `download_failed`, 2 `error`.
- Retriage (`irw_retriage_ha.py`) on the 75 `human_assistance` rows: 23
  `not_item_response`, 23 `aggregate_continuous` (drop both), 21
  `human_review` (staged to `human_review_continuous.csv`, needs pasting
  into the "Human eye" sheet), 7 `worth_retrying`, 1 `recoverable_format`.
- All 4 `good` + 8 `worth_retrying`/`recoverable_format` rows (12 total)
  hand-reviewed by downloading and inspecting each:
  - **Not usable — wrong unit of analysis / not item-response data**: "Do
    Large Language Models Simulate Moral Identity?" (DVN/TLKXAZ) — rows
    are LLM names, not people, and the two columns are pre-aggregated
    means, not raw items; "Quantifying Cognitive Decline through Driving
    Behavior: DRIVES" (DVN/KX1BYC) — raw GPS/vehicle telemetry
    (speed/altitude/odometer), not a psychometric instrument at all,
    despite the `dup_id_item` triage flag reading like repeated-measures
    item data; "Data from: Seed vernalization and gibberellic acid...
    horseweed" (USDA ADC) — plant biology, the "text-coded Likert" flag
    was a false trigger on an unrelated categorical variable.
  - **Not usable — file is metadata/codebook/summary, not raw response
    data**: "Who Cares? Measuring Differences in Preference Intensity"
    (DVN/W27GR5) — the only file in the Dataverse entry is an SPSS
    variable codebook, no actual data file was ever deposited; "Assessing
    gastro-intestinal related quality of life in cystic fibrosis: PedsQL
    GI validation" (PLOS/figshare) — entirely `score_*` composite/subscale
    totals, no raw items present; "Gender-based differences in ADS-S
    questionnaire item scores" (PLOS/figshare) — a scraped PLOS results
    table (group means/SDs/t-values), not raw data; "Replication Data for:
    How negative partisanship affects voting behavior in Europe"
    (DVN/GVNEI2) — the only file is a 19-row CSES country-level coding
    scheme, not person-level survey responses.
  - **Not usable — aggregate/party-level, not individual responses**:
    "Replication data for: Does Inclusiveness Affect Divisiveness?"
    (DVN/28131) — rows are political parties/elections (e.g. "PSOE 2012"),
    columns are researcher-coded party characteristics, not individual
    respondents' item responses.
  - **Deferred — needs multi-scale split**: "Teachers' attitude towards
    lifelong learning" (figshare 31836016, Haraseniuc & Maier 2026, CC BY
    4.0, N=70) — genuinely real data, 56 fully self-documented Romanian
    Likert items, but the item numbering resets to "1." six times,
    revealing 7 bundled instruments (ad-hoc openness-to-content scale,
    conscientiousness/procrastination, self-confidence, the validated ATI
    affinity-for-technology scale, self-efficacy, criticism-tolerance, and
    a love-of-learning disposition scale — several with reverse-worded
    items). Needs a careful per-block split, not rushed through in this
    pass. Full block boundaries recorded in `TODO.md` for whoever picks
    this up next.
  - **Deferred — needs the source manuscript**: visual-impairment
    functional-mobility kinematics dataset (DVN/0LWF5Z, Ahulló-Fuster et
    al. 2026, CC0, N=54) — the `QUEST_*` column names are misleading; the
    dataset description states the actual instrument is an adapted
    NASA-TLX, not the QUEST assistive-tech satisfaction scale. Clean 7
    items × 4 conditions, 0-5 range, no missingness — structurally ready,
    but NASA-TLX's "Performance" subscale is reverse-coded relative to its
    other 5 subscales and the manuscript (needed to map columns to
    subscales) isn't findable via web search — likely unpublished, very
    recent deposit. Not scripted blind.
  - **Deferred, ambiguous, needs paper text**: "Visual Context Affects
    Children's and Adults' Cognitive Load Engaged in Predictive Language
    Processing" (DVN/AAJSJ7) — the retriage flag was right that it's
    semicolon-delimited, but the actual content (an ICA-preprocessed file
    with B/S/V/G/A/N/P-prefixed column blocks) looks like EEG component or
    eye-tracking window data, not scale items — needs the paper to
    determine whether this fits IRW's item-response format at all before
    investing in a re-parse.
- Two ~300MB+ downloaded files (DRIVES telemetry, the child-tax-credit
  candidate that was skipped without a full download given its size and
  off-topic economic-microsimulation domain) were deleted from
  `downloads/` after review rather than left on disk.

Net: this batch's `good`/`worth_retrying` pool turned out to be almost
entirely false positives once opened — a reminder that `n_items`/`n_participants`
triage heuristics catch shape, not content. Zero tables shipped this pass;
two real leads parked pending paper access.

## PLOS ONE worth_retrying backlog sweep — batches 6/9/10/11/12/13/14 (2026-08-01)

Ben asked for a full hand-review pass on the `worth_retrying`/`recoverable_format`
backlog across 7 retriage files so they could be retired. Two tracks:

**Track A — named deferred candidates already identified in TODO.md** (11
candidates across batches 10/11/14, each previously deferred with a
specific reason): 8 resolved (5 processed, 3 confirmed still too complex
to rush), 3 left as-is.

**Track B — never-individually-reviewed `worth_retrying` rows** (batches
6/9/12/13, ~186 rows total, none previously opened): screened at scale
with a purpose-built scan script (downloads each candidate's SI file(s),
runs `triage_dataset()`, prints shape/columns/flag) rather than one-by-one
manual downloads — full output saved to `scan_plos_batch{6,9,12,13}_worthretrying.log`
in this directory (gitignored like other `*.log` files, but no longer
scratchpad-only). From that screen, the highest participant×item
candidates were hand-opened and verified individually.

### Tables shipped this pass (10 papers, 32 tables)

- `yang_2026_crisis_coping` (`10.1371/journal.pone.0350928`, CC BY 4.0,
  N=1033): 4 tables — Rumination Response Scale (22i, 3 subscales
  verified item-by-item against the paper's stated item lists — exact
  match), PARS-3 physical activity (3i), Duan's College Students' Stress
  Response Questionnaire (32i, 5-subscale coping measure, no per-item
  subscale breakdown available so shipped as one block), ERQ (14i). Raw
  file had a 3-row merged header plus 6 trailing blank/formula-artifact
  rows (dropped) — one artifact row had a leaked `610`/`423` value in an
  ERQ column, resolved by dropping the artifact rows rather than treating
  it as a normal data-entry error.
- `reinwarth_2023_domains_wellbeing` (`10.1371/journal.pone.0279701`, CC
  BY 4.0, N~2465, same file as the already-shipped `reinwarth_2023_loneliness3`/
  `_phq4`): 3 more tables — 8-item domain-importance battery, 8-item
  domain-satisfaction battery, 6-item psych-symptoms battery (content
  resembles HADS-A/D items but uniform per-item response format doesn't
  match HADS's item-specific wording, shipped under a descriptive name).
  The file's `q13`/"FLZ" battery, previously assumed to be the raw FLZ
  life-satisfaction questionnaire, turned out to be FLZ's own derived
  weighted importance×satisfaction index (range -12 to +20) — not shipped.
- `rowe_2016_cfs_strain` (`10.1371/journal.pone.0159386`, CC BY 4.0, N=80,
  2x2 CFS-vs-healthy x strain-vs-sham design): 3 tables — 5 symptom
  items x 7 timepoints (0-10 VAS), Beck Anxiety Inventory (21i), MFI-20
  (20i, excluding its own "R"-suffixed recalculated-duplicate columns).
- `kuehner_2017_mw_rumination` (`10.1371/journal.pone.0184488`, CC BY 4.0,
  N=43 x 50 probes): 1 table. This resolves the old "ambiguous t0_*/DoM/
  ToM" note — those columns turned out to be unlabeled fractional
  (already-averaged) composites and PANAS-6 sums, not raw items; only
  `MW`/`RUM` (1-7 each) are genuine single-value raw probe ratings,
  shipped together as a 2-item battery per the no-single-item-scale rule.
- `robbins_2019_dairy_tiestall` (`10.1371/journal.pone.0216544`, CC BY
  4.0, N=802 across 2 framing samples merged with `cov_framing`): 3
  tables, 3 items each (risk/quality belief, farm-type belief, and a
  third "has" battery whose exact wording wasn't found in the article
  text but whose column-name structure and independent 1-7 range justify
  treating it as its own scale).
- `silva_2018_body_image` (`10.1371/journal.pone.0199480`, CC BY 4.0,
  N~2198 Brazilian university students): 5 tables — MBDS (12i, continuous
  0.1-5.0), BSQ-8 (8i, item numbers confirmed against the published short
  form), WHOQoL-BREF (20i), Perceived Health Competence Scale (8i), TFEQ
  (18i). `Code_identification` was not a reliable person id (spot-checked
  duplicates and found different Age/Sex under the same code) — row
  position used instead.
- `trevisan_2018_mscs` (`10.1371/journal.pone.0206800`, CC BY 4.0,
  N=1178, from the MSCS validation study previously only known by an old
  general-backlog note "N=734, 40 items"): 2 tables — 77-item MSCS
  (excluding its own "_R" reverse-coded duplicate columns and subscale
  totals) and AQ-50 (50 binary items). No id column in the raw file — row
  position used.
- `liu_2017_cancer_exercise` (`10.1371/journal.pone.0169375`, CC BY 4.0,
  N=350 Chinese early-stage cancer patients): 7 tables from one 139-column
  file with no item-level labels but clear per-block subscale-total
  columns confirming instrument boundaries — 2 confidently named (MCMQ
  coping, 20i; SSRS social support, 10i, its own items legitimately have
  different per-item ranges hence a wide pooled 1-20 range) and 5 shipped
  under generic names pending a paper-text pass to confirm exact
  instrument identity (communication 3i, two unidentified scales D/O at
  7i/6i, a 22-item likely benefit-finding scale, a 27-item likely
  FACT-G-structured QoL scale).
- `colomer_perez_2021_self_care` (`10.1371/journal.pone.0260827`, CC BY
  4.0, N~920): 2 tables — Appraisal of Self-Care Agency (ASA-A, 24i) and
  SOC-13 (13i, its own reverse-worded items keep the `INVSOC` prefix from
  the raw file).
- `brederecke_2020_self_image` (`10.1371/journal.pone.0230331`, CC BY
  4.0, N=1367 German general population): 2 tables — Self-Image Scale
  (11i) and PHQ-4 (4i).

All 32 tables passed the per-item degenerate-value scan (no item with
<2 distinct response values) before being left in `irw_output/`.

### Track A candidates not shipped

- French school-subject self-concept study (`10.1371/journal.pone.0230103`,
  Chanal & Paumier 2019) — richer than the old TODO note suggested: 5
  domain self-concept scales (Ecole/Maths/Francais/Anglais/EducPhy, 33
  items each) plus an embedded ~32-item Big Five inventory plus
  achievement-goal (Ev/App) items plus actual school grades in the same
  file. Structure now mapped (see column list in this entry's git diff)
  but not split — too much for one rushed pass, same call as the
  Romanian teachers survey from the continuous-search batch.
- Dutch self/other/meta-personality study (`10.1371/journal.pone.0272095`,
  1086 columns) and psychosomatic rehabilitation gender-effects study
  (`10.1371/journal.pone.0256916`, 494 columns, cryptic suffixed variable
  names) — not opened this pass; both already flagged as large/complex in
  the original TODO note and nothing changed that assessment.
- Auricular Acupuncture exam-anxiety study (`10.1371/journal.pone.0168338`)
  — left as originally noted, low priority (N=44, mostly composite
  STAI-subscale readings).

### Track B: confirmed skips (spot-checked, not raw item data)

Representative sample of what was opened and rejected, categorized by
failure mode (full detail in the scan logs): pre-computed composite/
subscale-total scores only (e.g. body-dissatisfaction/muscle-mass/eating
scores in `0322635`, CBCL/YSR subscale totals in `0254953`, Type A/D
personality subscale scores in `0161840`); cognitive-task performance
scores rather than psychometric items (Stroop/TMT/Tower of London in
`0288386`, Operation-Span/Ravens/Grit in `0206555`, grammar-learning
declarative/procedural memory scores in `0158812`); wrong unit of
analysis (CEO/firm panel data in `0280758`, not individual survey
respondents); a coding-scheme/codebook file rather than person-level data
(`0202818`'s 5-item "N=788" candidate, unchanged from its original
listing). PedsQL-GI (`0225004` from the continuous batch, noted here for
completeness) is the same failure mode as several of these.

### Track B: still open — screened but not individually verified

~186 rows were screened via the scan script; the ones above and the
confirmed-skip sample were opened and checked, but a large pool of
structurally-promising candidates (`n_participants x n_items` in the
thousands, titles suggesting real validated-instrument administrations)
were **not** individually hand-verified this pass — screening at this
volume via title/shape alone, after this session's repeated experience of
promising-looking rows turning out to be composite scores or wrong-unit
data, isn't reliable enough to either ship or discard without opening
each file. 62 such candidates remain, full list with DOIs and titles in
this directory's git history / `BATCH_LOG.md` diff for this entry (top 20
by size):

`0255569` (risks/benefits, huge N), `0234997` (longitudinal mental health,
N=9484), `0283772` (elders' life satisfaction Czech, N=1023x103i),
`0209845` (children's beliefs, 214 items), `0249943` (adolescent
depression factor structure), `0289551` (Malay DERS, "psychometric
properties" title), `0194569` (suffering-images exposure), `0201216`
(narcissistic personality mindreading), `0135377` (smokers wellbeing/
mindfulness), `0236987` (trait creativity), `0288563` (social support/
identification), `0229926` (moral foundations stereotypes), `0280313`
(resident-physician burnout), `0258606` (pandemic coping), `0188476`
(decisional balance/processes of change), `0333390` (Korean pre-sleep
arousal, "psychometric properties" title), `0197276` (job crafting),
`0119395` (symbolic/non-symbolic quantity spatial learning), `0224159`
(emerging-adult romantic anxiety/avoidance), `0212304` (depressive
symptom types). 42 more below that size threshold, same file.

**Update (2026-08-01, ben-domingue): the remaining 62-candidate pool was
written off, not pursued further.** `plos_batch{6,9,12,13}_retriage.csv`
deleted, and (2026-08-01, ben-domingue confirmed the decision was final)
the `scan_plos_batch{6,9,12,13}_worthretrying.log` files deleted too — the
DOI list above (and this entry generally) is now the only surviving
record. If any of the 62 are wanted later, re-fetch via
`irw_discover_plos.py`'s `process_one()` on the DOI.

**QC catch (2026-08-01, ben-domingue): 3 of the 32 shipped tables had
isolated data-entry errors this pass's per-item degenerate-value scan
missed** (that scan only catches *no variation*, not *rare-value
outliers* — the actual gap). `rowe_2016_mfi20`: MFI8 and MFI15 each had
exactly one respondent (of 80) with a 0 on an otherwise strict 1-5
instrument — dropped (2 cells). `rowe_2016_symptoms`: respondent ID 230
had 9.5 in both FatiguePOST and BodypainPOST at the same wave, the only
fractional values among 2,800 otherwise-integer 0-10 readings — dropped
(2 cells). `trevisan_2018_mscs`: MSCS_54==3.88 and MSCS_66==3.64 (two
different respondents), the only 2 fractional values among 90,706
otherwise-integer 1-5 cells — dropped (2 cells). All three scripts in
`data/` updated to filter these before writing output; `irw_output/*.csv`
regenerated. Two other flagged values were checked and found *not* to be
errors: `liu_2017_communication`'s 0s are a well-populated real response
category (55/1/4 respondents per item), and `silva_2018_mbds`'s
fractional values are the instrument's own official per-item scoring
formula (importance/10 x Likert), confirmed via the paper's Methods text
— not imputation. `liu_2017_scale_d`'s rare "3" ceiling (2/351) and
`liu_2017_ssrs_support`'s S2 (350 respondents at 4, one at 1) remain
unresolved — plausible but not verifiable against a confirmed instrument
name/codebook.

## yandun2026 batch-3 column-boundary bug fixed (2026-08-01)

Fixed the off-by-one `SUBSCALES` column ranges in `data/
yandun2026_cognitive.py` identified in the "Discovered as duplicates of
already-processed IRW content" note above: `language` was cols 14-18 (5
items, wrongly including "Relates numbers with clues"), `logical_thinking`
was cols 19-21 (3 items, missing it). Corrected to language cols 14-17 (4
items) / logical_thinking cols 18-21 (4 items), confirmed against the raw
header's own group-boundary row (`Language and Communication` spans 4
columns, `Logical Thinking` spans 4). Regenerated all 4 subscale CSVs
(attention/memory unchanged, language 500->400 responses, logical_thinking
300->400 responses) into `automated_finding/irw_output/cleaned/`;
`cleaned_index.csv` updated. **Re-uploaded to Redivis (confirmed
2026-08-02, ben-domingue)** — `irw_output/cleaned/` and `cleaned_index.csv`
removed from disk as expected.

## PLOS ONE batch 15 (2026-08-01)

30 terms pulled from the recyclable non-PLOS pool in `search_terms_log.csv`
(per the `TODO.md` "Large pool of recyclable PLOS search terms" item),
favoring generic-but-established construct/scale names not yet tried
against PLOS: resilience, self-esteem, self-control, locus of control,
social support, emotional intelligence, parenting sense of competence,
family resilience, body image, academic burnout, meaning in life, work
engagement, psychological safety, organizational justice, problematic
smartphone use, fear of missing out, exercise self-efficacy, relationship
satisfaction, intimate partner violence, dyadic adjustment, acculturative
stress, post-traumatic growth, pain catastrophizing, illness perception,
right-wing authoritarianism, conspiracy mentality, self-regulated
learning, growth mindset, career adaptability, delay discounting. All 30
logged in `search_terms_log.csv`.

`python3 irw_discover_plos.py <30 terms> --out plos_batch15_triage.csv`,
run in the background (~2h10m wall clock).

**Triage**: 2,335 candidates → **33 `good`** (1.41% — the best hit rate of
any PLOS batch to date, beating batch 13's previous high of 0.91%), 450
`human_assistance`, 1,770 `no_usable_file`, 37 `not_item_response`, 27
`download_failed`, 17 `error`, 1 `crashed` (isolated to its own worker
process per the crash-isolation design — did not affect the rest of the
run).

**Retriage** (`irw_retriage_ha.py`) on the 450 `human_assistance` rows →
`plos_batch15_retriage.csv`: 144 `human_review`, 121 `aggregate_continuous`
(drop), 94 `worth_retrying`, 89 `not_item_response` (drop), 2
`recoverable_format`. `human_review_plos_batch15.csv` (144 rows) staged,
ready to paste into the "Human eye" sheet. `plos_batch15_worthretrying.csv`
(96 rows: 94 `worth_retrying` + 2 `recoverable_format`) staged for a future
hand-review pass — not yet reviewed.

**Good-candidate review** (all 33 hand-checked per SKILL.md's "needs a human glance more than usual" note — fetched the full SI file list per candidate and loaded each tabular file to inspect real columns/shapes, not just the triage-flagged file): 7 papers processed -> 22 tables, 1 duplicate caught, 3 skipped as not-a-fit, 22 deferred.

**Processed** (`biblio_plos_batch15.csv`, 22 rows):
- `ngo_2025_green_*` (`10.1371/journal.pone.0323879`, N=237): standard
  Theory-of-Planned-Behaviour battery, 5 constructs x 4 items each, 1-5 --
  `_green_attitude`, `_green_subjective_norm`, `_green_pbc`,
  `_green_purchase_intention`, `_green_purchase_behavior`.
- `zeng_2025_academic_buoyancy_efa`/`_cfa` (`10.1371/journal.pone.0318347`):
  two separate samples, not the same instrument administered twice -- EFA
  sample (N=209, all 32 candidate items) and CFA sample (N=423, the
  21-item subset retained after EFA item reduction).
- `fitriana_2022_hapwork_efa`/`_field` (`10.1371/journal.pone.0261617`):
  Happiness at Work Scale validation, EFA sample (N=105, 31 items) and
  field-study sample (N=370, 18-item final scale + demographics).
- `komura_2026_gqs_*`/`_mdmt_*` (`10.1371/journal.pone.0340449`, N=148):
  two validated instruments administered together in a human-AI creative
  collaboration study -- Godspeed Questionnaire Series (5 subscales,
  anthropomorphism/animacy/likeability/perceived_intelligence/
  perceived_safety, 1-5) and Multi-Dimensional Measure of Trust (4
  subscales, reliable/capable/ethical/sincere, 0-7).
- `yang_2026_igd_criteria`/`_benefits` (`10.1371/journal.pone.0351550`,
  N=1032 adolescent gamers, 2 waves): 9 raw DSM-5 IGD criteria items
  (binary) and 4 perceived-benefit rating items (1-10) -- derived severity
  sum scores/diagnosis flags (`dIGD_S`/`sIGD_S`/`dG_IGD`/`sG_IGD`) not
  shipped. `_benefits` had a repeated-constant-fractional-value pattern
  (e.g. 4.44 exactly 4 times) on an otherwise strictly-integer 1-10 scale
  in a handful of cells -- consistent with mean/imputed substitution for
  missing responses, not genuine raw ratings; dropped (13 cells).
- `lee_2020_vr_usability` (`10.1371/journal.pone.0238437`, N=60): 17-item
  VR mental-illness-simulation usability scale, 0-10. `satisfaction_level`/
  `communication_competency`/`VR_experience` single categorical ratings
  kept as text covariates, not shipped as items (no single-item scales).
- `cox_2024_feedback_perceptions` (`10.1371/journal.pone.0300205`, N=29):
  5-item feedback-perceptions survey, pre/post intervention (wave=1/2).

**Duplicate caught**: "The impact of classroom interaction on willingness
to communicate..." (`10.1371/journal.pone.0328226`, Liu et al.) is the
*same paper* already processed in batch 13 as `liu_2025_classroom_interaction`/
`_willingness_communicate`/`_speaking_selfefficacy`/`_foreign_lang_enjoyment`
-- slipped through this run's DOI-exclusion filter (1,109 DOIs excluded at
discovery time), most likely because the exclusion list snapshot predates
batch 13's dictionary-sheet paste. Not reprocessed.

**Correction (2026-08-01, same day, ben-domingue): the "animal study"
skips were re-examined** -- IRW's core id/item/resp format doesn't
require human respondents, only a valid id/item/resp shape, and the
original skip (mice/dogs in batch 15's own review, above) was an
unwarranted overgeneralization from that precedent rather than an actual
standing rule. Re-inspected both at the raw-column level:
- `muller_2016_dog_inhibition` (`10.1371/journal.pone.0147753`, N=41
  dogs): the paper bundles 4 different tasks in one file, but only the
  inhibitory-control (cylinder) task has a genuine multi-item structure --
  `Inhibition1`/`Inhibition2`/`Inhibition3`, 3 trials, 0/1/2 ordinal,
  confirmed real variation (33/5/1 and similar splits, not degenerate).
  resp=0 is a valid third scale point, not a missing code -- standard
  cylinder/detour-task scoring (0 = no inhibition/direct approach, 1 =
  partial detour, 2 = full successful detour), and appears with real
  frequency per trial (1/10/4 occurrences), not an isolated fluke. The
  other 3 tasks (size-constancy, on/off, four-string) are each a single
  binary/latency outcome per dog -- not multi-item, so not shipped.
  `InhibitionScore` (a derived summary, not a consistent raw sum of the 3
  trials) not shipped either. cov_sex/cov_treatment kept.
- ~~`fushuku_2023_mouse_temperature`~~ (`10.1371/journal.pone.0292649`,
  N=20 mice): added, then **removed same-day (ben-domingue catch)** --
  a circadian body-temperature time series is a physiological/biomarker
  measurement, not a response to any item or stimulus. It happened to be
  structurally shippable as id/item/resp (id=mouse, item=time-of-day,
  resp=temperature), but shape alone isn't the bar -- IRW's format not
  requiring *human* respondents doesn't mean it accepts *any*
  continuous-measurement table that fits the id/item/resp shape. Script
  and output deleted. The paper's other 4 SI files were already
  correctly left out (see original note, since superseded): S2
  heart-rate/locomotor blocks with unlabeled repeated columns; S3 a wide
  organ-weight/plasma-metabolite panel with mixed units and a stray
  units-header row; S4 an elevated-plus-maze table with only 1-2
  non-derived raw items; S5 a pure statistical-test-result table, not
  data at all.
`muller_2016_dog_inhibition` added to `biblio_plos_batch15.csv`.

**Skipped as not-a-fit** (2):
- "Design and psychometric evaluation of schools' resilience tool..."
  (`10.1371/journal.pone.0253906`): an 11-expert content-validity-index
  panel rating 91 items, not respondent survey data -- different genre,
  too small a rater panel to be useful.
- "Hurts less, lasts longer"... benzathine penicillin
  (`10.1371/journal.pone.0302493`): the only quantitative data is a single
  NRS pain rating repeated across 5 timepoints -- one item, violates the
  no-single-item-scale rule.

**Second review pass (2026-08-01, same day, ben-domingue): full column-level
inspection of all 21 remaining deferred candidates.** 13 of the 21 turned
out to be processable after all with a closer look (several had been
deferred on first pass purely from shape/title without opening the full
column list) -- 12 papers processed -> 31 more tables
(`biblio_plos_batch15.csv` was 55 rows total at this point; see the later
"Correction" note above for the mouse-temperature table that was added
then removed, bringing the final count to 54):
- `wu_2024_proactive_personality`/`_resilience`/`_self_control`/
  `_video_addiction` (`0312597`, N=560): 4 clean column-prefix blocks
  (A/B/C/D), construct names inferred from paper order.
- `gerber_2022_altruism`/`_self_esteem` (`0276665`, N=256, pre/post
  wave=1/2): ALT (14i, 0-4) and EST (9i, -2 to 2) blocks shipped; a third
  20-item TIM/EMO/SOC/ACT block with reverse-worded items and an unclear
  construct name was NOT shipped -- needs the paper.
- `pakseresht_2021_gmfood_risk_ranking` (`0252580`, N=535): only the
  clean 4-item risk-dimension ranking task shipped; the file's
  scenario-contingent sub-item ratings and inconsistent-scale
  responsibility-allocation items were left out (needs the paper to
  interpret the randomized scenario-assignment design safely).
- `fadhliah_2022_disaster_media_trust` (`0264089`, N=75): 8 named-channel
  rating items shipped from S1; S2 (all-`Unnamed:` columns, no real
  headers) not shipped.
- `kowal_2021_kidney_donor_body_image` (`0249397`, N=25): 35-item body-image
  questionnaire; a 9999 sentinel value in 3 items filtered as missing.
- `chuang_2018_disease_checklist` (`0194178`, N=60): 10-item binary
  chronic-disease checklist (not the paper's main outcome scale, which
  isn't in this file); constant-zero `disease3` dropped.
- `qiang_2025_red_tape`/`_ne_scale`/`_job_performance`/`_surface_acting`/
  `_job_dissatisfaction`/`_coping`/`_workplace_friendship`/
  `_abusive_supervision` (`0327359`, N=396): 8 tables -- 2 column-code
  blocks (RE, NE) plus 6 more scales split from the file's own numbered,
  fully-worded item text (17-42 in the original questionnaire); item 35's
  Chinese-language duplicate of item 36 dropped, single-item column 42
  (daily overtime) not shipped, and an ambiguous duplicate `CO`-prefixed
  8-column block left out.
- `yoshimura_2026_es_scale`/`_isu_scale`/`_psych_safety` (`0346791`,
  N=522): 3 column-prefix blocks; `ps3m` confirmed as psychological
  safety by both its prefix and the paper's own construct naming.
  `retain_care`/`retain_general` (single-item outcomes) not shipped.
- `wijesinghe_2025_sustained_agile_usage` (`0316538`, N=391): only the
  SAU (Sustained Agile Usage) block shipped, matching the paper's
  headline construct by name; ~10 other 2-5-letter-coded blocks in the
  same file are mostly single-item or unlabeled and were left out.
- `bartoli_2022_badge_notifications` (`0270888`, N=1009): item = named
  app, resp = badge-notification enablement (0/100 binary encoding, left
  as-is).
- `fatima_2025_mslq` (`0319763`, N=349): the 81-item MSLQ from
  `S1_Dataset`; `S1_Appendix` (8-expert CVI panel, same small-panel genre
  as other skips) not shipped.
- `wang_2026_perceived_usefulness`/`_teaching_presence`/
  `_technology_anxiety`/`_attitude`/`_behavioral_intention` (`0346229`,
  N=500): standard TAM battery, 5 clean column-prefix blocks.
- `rodriguezmuniz_2016_washback_survey` (`0167544`, N=51): 17-item teacher
  survey; open-text `OA1-OA6`/`Remarks` columns not shipped.

**Confirmed as not-a-fit** (1 more): HK animal-assisted humane education
SEL study (`0249033`, N=110) -- the `Prosocial_T0/T1/T2` etc. columns'
value ranges (e.g. 6-25) confirm they're derived subscale sum scores, not
raw items; the paper's actual raw item data isn't in this file.

**Still deferred** (7 of the 21, genuinely needs more time or the source
paper): PMO strategic-plans survey (`0306702`, N=303, 9 distinct Likert
blocks with no item text or construct labels -- needs the paper to name
them safely); kinesthetic-robot-programming curricula study (`0294786`,
N=28, 6 bundled SI files with per-task workload/confidence deltas,
custom multi-file logic needed); WFH/hybrid-workplace-flexibility
preference study (`0348206`, N=751, 335 columns with conditional/
skip-logic sparsity, needs dedicated time to understand the Qualtrics
structure); Thailand migrant-worker discrimination/violence study
(`0300388`, N=494, cryptic q-number columns, most of the q75-124 range
didn't even reach 50% non-missing in this pass -- needs a codebook);
medicinal-plants naturalistic-memory study (`0214300`, N=200, unclear
whether rows are individual respondents or already-aggregated citation
counts -- needs verification); PROMPTa writing-skills assessment study
(`0337342`, N=46, messy duplicate-column two-cohort structure with
P/M/E-suffixed rubric dimensions, needs untangling); learning-emotion
offline-environment study (`0294407`, N=128, item values run into the
hundreds, inconsistent with individual Likert responses -- likely
corpus-level word-frequency counts, not per-respondent data, probably
not a fit at all). `plos_batch15_triage.csv` still holds these 7 rows.

**Non-human candidates revisited across past batches (2026-08-01,
prompted by the batch-15 dog/mouse correction above):** searched
`BATCH_LOG.md` for prior "animal"/non-human skips.
- Batch 13's archerfish symbol-value-discrimination study
  (`10.1371/journal.pone.0174044`) was skipped with the reasoning
  "non-human subjects (fish), out of IRW's scope" -- re-opened and
  confirmed still not worth shipping, but for a different reason: its
  only SI file is a 12-row per-fish shot-count summary (3 shape-choice
  counts + a derived total), too thin and already session-aggregated to
  be a meaningful raw item-response table. The "out of scope" framing was
  wrong; the thinness/aggregation judgment stands.
- Batch 11's "Personality predicts dispersal and settlement" mesocosm
  dataset (figshare 32605179) was skipped as "animal behavioral ecology
  data... not human item responses" -- re-opened, and one file
  (`models_all_data_FIN.csv`) turned out to be a genuine repeated-trial
  personality assay (activity/bite-count/time-vigorous x2 trials each,
  N=79 fish, continuous) rather than the spatial/temporal territory-
  tracking data in the deposit's other 5 files. Shipped briefly as
  `gismann_2026_fish_personality`, then **removed same-day (ben-domingue
  call, 2026-08-01)**: the `time_vigorous_s_{1,2}` items are a
  response-time-like measure (seconds spent in a behavioral state) mixed
  into the same `resp` column as the count/index items (`bites`,
  `activity`) -- IRW convention keeps response time in its own `rt`
  column rather than folding it into `resp` as if it were an ordinary
  item. Dropped rather than restructured (e.g. splitting `time_vigorous`
  into a proper `rt` column against a 2-item `bites`/`activity` table),
  per ben-domingue's simplicity call. Script and output deleted. Still
  correctly excludes the deposit's other 5 tracking files, per the
  original re-examination.
No other animal/non-human skips found in `BATCH_LOG.md`'s history beyond
this and the archerfish case above.

**QC follow-up (2026-08-01, ben-domingue): value-semantics checks on the
non-human/edge-case tables.**
- `komura_2026_mdmt_reliable`/`_capable`/`_ethical`/`_sincere` (MDMT,
  Multi-Dimensional Measure of Trust): resp=0 confirmed valid, not a
  missing/sentinel code. Per-item value counts form a smooth, contiguous,
  roughly unimodal distribution from 0 up through 7 (e.g. `mdmt_capable_1`:
  {0:2, 1:3, 2:11, 3:22, 4:31, 5:33, 6:32, 7:14}) -- a sentinel code would
  show up as an isolated spike disconnected from the natural distribution,
  not a smooth left tail. Consistent with MDMT's published 0("Not at
  all")-7("Extremely") response format. A few items (`capable_4`,
  `ethical_3/4`, `sincere_*`) simply had no 0 responses in this N=148
  sample -- sampling variation, not evidence of a different scale.
- `muller_2016_dog_inhibition`: resp=0 confirmed valid -- standard
  cylinder/detour-task scoring (0 = direct/no-inhibition approach, 1 =
  partial detour, 2 = full successful detour on first attempt), occurring
  10/1/4 times across the 3 trials respectively, not an isolated fluke.

## PLOS ONE batch 15 — final resolution of the 7 deferred candidates (2026-08-02)

Re-examined all 7 with the same full-column inspection method; 5 turned
out processable, 2 genuinely need a person. `biblio_plos_batch15_deferred.csv`
(17 rows, 5 papers) and `human_review_plos_batch15_deferred.csv` (2 rows)
staged.

**Processed** (5 papers -> 17 tables):
- `sandhu_2024_pmo_q13`/`_q16`/`_q18`/`_q19`/`_q20`/`_q21`/`_q22`/`_q23`/
  `_q24`/`_q26`/`_q32` (`0306702`, N=303): 11 distinct 1-5 Likert blocks
  shipped under their raw Qualtrics codes (no item text/construct labels
  in the file), same generic-naming treatment already used for `qiang_
  2025_ne_scale`/`yoshimura_2026_es_scale` etc. in this batch. Real
  per-block N variation consistent with skip logic (193-260 respondents
  per block out of 303).
- `ajaykumar_2023_nasa_tlx`/`_experience` (`0294786`, N=27): the standard
  NASA-TLX (6 items) and a 5-item prior-experience block, pulled out of
  the paper's 6 bundled SI files -- the other 4 (per-task unsuccessful-
  demo counts, task times, suboptimality/force-torque deltas, body-part
  interaction counts) are derived/per-condition metrics, not a clean item
  set, and stay unshipped.
- `chuemchit_2024_partner_violence`/`_nonpartner_violence` (`0300388`,
  N=405/494): re-examination found 2 clean, clearly-named 5-item binary
  scales (violence by type: economic/cyber/psychological/physical/
  sexual) hiding among the ~65 cryptic q-number columns that caused the
  original defer -- the missingness pattern in the partner-violence items
  (89/494 NaN) is consistent with legitimate skip logic (only asked if
  the respondent had a partner in the past 12 months), not a data
  problem. The cryptic q-columns themselves remain unshipped.
- `dasilva_2019_medicinal_plants` (`0214300`, N=200): confirmed the
  `Code` column is an individual respondent identifier (e.g. "1F21" =
  subject 1, female, 21yo), resolving the original uncertainty. resp is
  0 (not mentioned) or a 1-15 order-of-mention code from a free-list
  salience task -- the value range exactly matching the item count
  supports the rank-order reading over a count/binary one.
- `puro_2025_prompta_writing` (`0337342`, N=46): shipped only the
  simpler of the file's two side-by-side column blocks for the same 46
  students (Pre Test, 9 per-round task scores, Post Test); the second
  block's P/M/E-suffixed columns are consistently higher-valued and
  their exact meaning (different rubric? different rater?) isn't
  documented in the file, so left unshipped.

**Human review** (2, `human_review_plos_batch15_deferred.csv`):
- WFH/hybrid-workplace-flexibility preference study (`0348206`, N=751):
  335 columns with extensive Qualtrics conditional/skip-logic sparsity --
  needs dedicated time to map the branching structure, not a quick
  column-prefix read.
- Learning-emotion offline-environment study (`0294407`, N=128): item
  values run into the hundreds (e.g. "Joy" up to 663), inconsistent with
  any individual Likert/rating response -- looks like corpus-level
  word-frequency counts from automated text analysis rather than raw
  per-respondent item data; needs a person to confirm against the paper
  before it could ever be shipped.

## PLOS ONE batch 15 — resolution of the 96-row worth_retrying/recoverable_format pool (2026-08-02)

Full per-row disposition of `plos_batch15_worthretrying.csv` (94
`worth_retrying` + 2 `recoverable_format`). Re-fetched and inspected every
row's SI file at the column level (not just the retriage reason string).

**Duplicates caught** (2, not reprocessed): `10.1371/journal.pone.0206800`
(MSCS) already shipped as `trevisan_2018_mscs` (batch 9's QC-catch entry);
`10.1371/journal.pone.0230331` (Self-Image Scale) already shipped as
`brederecke_2020_self_image`. Same DOI-exclusion-staleness pattern as the
Liu duplicate caught earlier in this batch.

**Processed** (13 papers -> 74 tables, `biblio_plos_batch15_worthretrying.csv`):
- `dasilva_2018_mbds`/`_bsq`/`_whoqol`/`_phcs`/`_tfeq` (`0199480`, N up to
  2096): 5 validated instruments (item subsets) bundled in one file --
  MBSRQ-style body-areas items, Body Shape Questionnaire, WHOQOL-BREF,
  Perceived Health Competence Scale, Three-Factor Eating Questionnaire.
- `wang_2024_emotion1`-`5` (`0303965`, N=1460): 5 achievement-emotion
  subscales, unlabeled construct names (no item text in file).
- `jiang_2024_*` (`0312338`, N=707): **21 tables** from one file -- a
  huge bundle of column-prefix-coded subscales (student thriving/
  institutional integrity/growth mindset/campus-involvement domains).
  Item columns held **text-coded 7-point Likert responses in Chinese**
  (不同意/同意/有些同意/etc.) -- recoded 1-7 via an explicit map. This
  and the `an_2020`/`huang_2023`/`chen_2021` recodes below are new
  non-English text-Likert cases beyond the English ones `SKILL.md`
  already documents.
- `jablonska_2020_instagram_addiction`/`_profile_grooming`/
  `_upward_comparison`/`_downward_comparison`/`_rses`/`_hads`/`_swls`
  (`0229354`, N=974): text-coded English 7-point Likert recoded; the
  54-item battery split cleanly by full item-text content into 7 scales,
  three of them recognizable validated instruments (Rosenberg Self-Esteem
  Scale, an HADS-style anxiety/depression set, Satisfaction With Life
  Scale).
- `yu_2025_mobile_addiction`/`_bedtime_procrastination`/
  `_physical_activity` (`0331340`, N=376, 3 waves T0/T1/T2): raw items
  for all 3 scales, "Average score" columns (derived) excluded.
- `huang_2023_b_scale`/`_c_scale`/`_d_scale`/`_e_scale` (`0290452`,
  N=631): 4 column-prefix blocks; the c (binary) and e (4-point) blocks
  each had a handful of out-of-range values (22/44/11/33 etc.) on
  otherwise strictly-bounded items -- a digit-duplication data-entry
  pattern (e.g. "2" mistyped as "22") -- filtered.
- `wesselmann_2018_drri`/`_social_support`/`_pcl`/`_trait_anxiety`/
  `_state_anxiety`/`_needs`/`_distress`/`_ostracism`/`_msp` (`0208438`,
  N up to 128): **9 tables**, no usable id column in the file (row index
  used instead) -- includes a raw PTSD Checklist (PCL-20) and a
  Multidimensional Scale of Perceived Support. `*R`-suffixed
  reverse-coded duplicate columns and derived composite totals excluded.
- `an_2020_efl_self_regulated` (`0240094`, N=525): 49-item scale. The
  SPSS export kept numeric string codes for the Likert midpoints (2-6)
  but exported the two endpoint labels as Chinese text that had been
  mis-decoded as Latin-1 (recovered via
  `.encode('latin1').decode('gb18030')`) -- a new failure mode worth
  remembering for future non-English `.sav` files with partially-corrupt
  value labels. Q51 (values up to 197, not part of the 1-7 scale)
  excluded.
- `chen_2021_acculturation`/`_enculturation` (`0258323`, N=310): 2
  24-item subscales, text-coded English frequency Likert ("never" ...
  "always") recoded 1-5.
- `avilatamayo_2022_empl_stab`/`_work_envir`/`_skills_dev`/`_workf_div`/
  `_work_life` (`0266711`, N=433): 5 named CSR subscales, text-coded
  7-point Likert recoded; a stray non-integer value (4.368159) appearing
  alongside the text categories looked like a mean-imputed substitute for
  missing responses and was dropped.
- `shan_2020_pd`/`_hs`/`_ph`/`_f`/`_cs`/`_g` (`0240103`, N=202): 6
  column-prefix blocks, text-coded 5-point agreement Likert recoded.
- `kokoszka_2022_soc`/`_hamd`/`_zjn`/`_who5`/`_paid` (`0263766`,
  semicolon-delimited, N=100): 5 named validated instruments (Sense of
  Coherence, Hamilton Depression Rating Scale, WHO-5, Problem Areas In
  Diabetes) bundled in one file. SOC block had a `99` sentinel/missing
  code (isolated single occurrences on an otherwise 1-5 scale) -- filtered.
- `rodriguezquiroga_2024_epistemic_trust` (`0311352`,
  semicolon-delimited, N=1018): 15-item Epistemic Trust, Mistrust, and
  Credulity Inventory.

All 74 tables passed the standard per-item degenerate/rare-value scan
(no flags).

**Confirmed skip, not a fit** (11): systematic-review/scoping-review
datasets where rows are papers or measures, not people (`0305567`
teleworking, `0311889` dance, `0338521` personality-measures) --
`0256497` (all open-text feedback, no Likert items) -- `0229138`,
`0163281`, `0276734` (pure aggregated/descriptive-statistics summary
tables, not respondent-level data) -- `0315442` (expert-panel
content-validity table, same genre as the earlier schools'-resilience-
tool/MSLQ-appendix skips) -- `0269012` (demographics only, qualitative
study) -- `0343308` (item-development/factor-loading meta-table, not
respondent data) -- `0344768` (N=9 scenario-summary table, not real
per-respondent data).

**Human review** (45 rows, `human_review_plos_batch15_worthretrying.csv`):
mostly datasets whose numeric columns turned out to be derived composite/
subscale totals rather than raw items (confirmed by column-name/value-
range inspection, e.g. named `*_score`/`*Total`/`*Scale` columns with
in-range-but-clearly-pre-aggregated values), plus a handful of
structurally ambiguous or overly complex cases (dyadic Z-scored data,
1086-column multi-rater/multi-wave personality battery, video-level
rather than person-level units of analysis, thin single-item-only files).
Full per-row reasons are in the conversation record for this session;
each needs a person with more time or the source paper, not further
automated inspection.

**Confirmed structurally good, not yet scripted** (25 -- an explicit,
tracked follow-up, distinct from human_review since these don't need
human judgment on fit, just scripting time): `0247993` (elderly social
support network composition, Slovenia), `0207458` (interpersonal justice
climate, 32 items, text-Likert), `0214914` (patient safety climate, 33
items), `0189592` (Vienna brachial-plexus psychosocial, binary C/D/E item
blocks only), `0242902` (health mindsets/protective behaviors), `0291207`
(sex-trafficking coping self-efficacy, 10 abuse-type severity items),
`0228961` (nudging creativity, 6-item pre-scale), `0295514` (luxury
purchase intention, 30 items, full text), `0237846` (neuroticism +
smartphone addiction, full text), `0288563` (social support/cognitive
appraisals, 2 scales), `0273763` (conspiracy thinking, 3 scales incl.
26-item SCATI), `0323811` (frontline servant leadership, many named
2-4-letter-coded subscales), `0255445` (carbon-reduction pro-environmental
behavior, 15 items), `0209845` (children's jealousy/friendship beliefs,
several scales), `0199924` (entrepreneurial intention Italy), `0283850`
(entrepreneurial intention Transdanubia, full text), `0201007` (GYPES
patient empowerment, 15 items), `0338728` (organizational resilience UAE,
14 items, full text), `0205559` (coaching justice, match-level repeated
observations), `0236987` (trait creativity/mood, experience-sampling
data), `0237710` (diabetes medication adherence Ghana), `0252329`
(couples extrinsic emotion regulation, full text, small N), `0262716`
(anxiety Bangladesh, 6 raw GAD-7-style items among a huge N=2313), `0270420`
(dental-learner adaptability, small N=18 but clean), `0310351`
(cross-cultural acculturation measures, 35+ items). `plos_batch15_worthretrying.csv`
kept on disk until these are resolved (script or human-review handoff).

## PLOS ONE batch 15 — scripting the 25 confirmed-good candidates (2026-08-02)

Worked through the "confirmed structurally good, not yet scripted" list.
`biblio_plos_batch15_worthretrying_round2.csv` (66 rows, 24 papers) staged.

**Reclassified on closer inspection** (1): `0252329` (couples extrinsic
emotion regulation) turned out to be a 23-expert content-validity panel
(raters' fields: "Methodologist"/"Health Psychology"/etc., responses
"Suitable"/"Essential") -- not respondent data. Same genre as the other
CVI-panel skips this batch (schools' resilience tool, MSLQ appendix,
Delphi table). Not scripted.

**Processed** (24 papers -> 66 tables):
- `cugmas_2021_elderly_social_support` (`0247993`, N=558): support-
  network composition by relationship type (count, not binary as
  originally assumed -- corrected after inspecting the actual value
  distribution).
- `pecino_2018_justice_climate`/`_extrarole_wfb` (`0207458`, N=442): the
  40 "cl"-prefixed columns turned out to span **two different** text-coded
  6-point scales (confirmed by checking each column's own category set,
  not just the shared prefix) -- a "how many coworkers" climate scale
  (items 1-6) and a personal frequency scale (items 7-40) -- shipped as
  two tables rather than one mixed-scale table.
- `deilkas_2019_patient_safety_climate` (`0214914`, N=112): 62 of the
  file's ~74 "Q"-numbered columns share one 5-point agreement scale;
  the rest (Q2/Q3/Q3a-g: a "Very good"-"Very bad" scale; Q66-74:
  demographics) were excluded after the same per-column category-set
  check.
- `hruby_2018_interview_a`-`_e` (`0189592`, N=8): recovered a second,
  entirely different table buried in the same sheet below the SF-36/
  FKB-20 data (a structured-interview scoring block starting at row 21,
  needing `header=21` to parse) -- 5 binary blocks. With N=8, several
  items had zero variance across all 8 cases; dropped per-item (each
  block keeps >=2 items after filtering).
- `johnhenderson_2020_health_mindset`/`_disinfection_behavior`
  (`0242902`, N=192): one isolated out-of-range value (11 on a 1-5 item)
  dropped as a data-entry error.
- `twis_2024_adverse_experience_types` (`0291207`, N=93): 10 of 11
  "*Scale"-suffixed columns are themselves the raw per-type severity
  items (not aggregates, despite the name) -- `CSAbuseScale` (constant
  0) dropped.
- `agogue_2020_self_perceived_creativity` (`0228961`, N=200).
- `majeed_2024_luxury_purchase` (`0295514`, N=267, full item text kept).
- `petrocchi_2020_neuroticism` (`0237846`, N=160): only the 10-item
  neuroticism block shipped -- the file's `Smartphone_addiction_*` items
  were >55% blank (96/160 empty on item 1 alone) and excluded as too
  sparse to be reliable, a judgment call not caught by the original
  triage.
- `gillman_2023_appraisals`/`_pss` (`0288563`, N=412): both blocks had
  scattered unique-looking fractional values (e.g. 2.227143) on
  otherwise strictly integer items -- the same mean/interpolation-
  imputation signature caught earlier in `yang_2026_igd_benefits` --
  filtered to integers only.
- `arnulf_2022_conspiracy_thinking`/`_general_knowledge` (`0273763`,
  N=398): only `CT2` (14i) and `GK` (12i, binary) shipped -- `CT1`'s
  response cells had the item text itself leaked into them (unusable),
  and `SCATI` (70i) turned out to be a forced-choice nominal code
  (SF/MT/MF/ST-style) rather than an ordinal Likert response, so doesn't
  fit the core standard.
- `song_2025_ep`/`_sb`/`_ac`/`_fg`/`_co`/`_au`/`_hu`/`_st`/`_sc`/`_lwb`/
  `_wwb`/`_pwb`/`_pj`/`_cs`/`_er` (`0323811`, N=486): **15 tables** from
  one file, using a generic column-prefix auto-detection helper (regex
  `^([A-Za-z]+)(\d+)$`, group by prefix, require >=2 members) -- the
  same technique paid off again in `idemudia_2025` and had already been
  used for `jiang_2024_student_thriving` earlier in this batch; worth
  keeping as a standard first move on any large unlabeled-block file.
- `singleton_2021_carbon_reduction` (`0255445`, N=106).
- `lavallee_2019_sseb`/`_oseb`/`_loneliness`/`_jealousy`/`_harmony`/
  `_cas` (`0209845`, N up to 280): 6 clean baseline scales shipped; the
  file's scenario-condition blocks (VIG/INT/STB/etc. x4 conditions) and
  large derived-column tail were not -- needs the paper.
- `molino_2018_d5_scale`/`_d6_scale` (`0199924`, N=658): text-coded
  Italian endpoints ("Per niente d'accordo"/"Del tutto daccordo")
  recoded.
- `makai_2023_entrepreneurial_transdanubia` (`0283850`, N=144, full
  item text kept).
- `acunamora_2018_gypes` (`0201007`, N=273): a 999 sentinel (131/404
  responses on item 1 alone) filtered as missing.
- `muir_2025_resilience_opinions`/`_behaviours` (`0338728`, N=70): same
  per-column category-set check found two different scales under
  sequential item numbering (opinions: agree/disagree; behaviours:
  frequency); a handful of combined multi-select cells (e.g. "Agree,
  Strongly Agree", a checkbox-entry artifact) dropped.
- `debacker_2018_decisionjustification`/`_justice_appraisal` (`0205559`,
  N=96, `match_number` used as `wave`).
- `zhang_2020_trait_creativity_mood` (`0236987`, N=54, experience-
  sampling, `day` used as `wave`): a duplicate-named `tired`/`tired.1`
  column pair confirmed NOT to be a read artifact (only 5% value
  agreement) -- both kept as distinct items.
- `afaya_2020_general_knowledge`/`_diet_knowledge`/`_monitoring_
  knowledge`/`_exercise_knowledge`/`_medication_knowledge`/
  `_footcare_knowledge`/`_complications_knowledge` (`0237710`, N=330):
  **7 tables**, one per diabetes-knowledge domain.
- `anjum_2022_gad7` (`0262716`, N=2313): 6 of the 7 standard GAD-7 items
  (E20 in the file is an intro screening item, not part of the battery).
- `otaki_2022_dental_adaptability` (`0270420`, N=18, small).
- `idemudia_2025_d101`/`_e201`/`_s101`/`_s201`/`_s301`/`_t101`/`_t201`
  (`0310351`, N=329): **7 tables**, same generic prefix-detection
  approach as `song_2025`; same imputation-fraction pattern as
  `gillman_2023` found and filtered.

All 66 tables re-scanned after the imputation-fraction and zero-variance
fixes above -- clean, no remaining flags. Two stale intermediate files
from mid-fix iterations (`muir_2025_organizational_resilience.csv`,
`pecino_2018_interpersonal_justice.csv`, both superseded by their
2-table splits) deleted before finalizing.

**Recurring lesson this round**: several files that looked like one
mixed-up scale on first pass (`pecino_2018`, `muir_2025`) were actually
*two* different response scales sharing one column-numbering sequence --
checking each column's own category set (not just trusting a shared
name prefix) caught this every time it happened. Worth doing by default
on any multi-item block before assuming it's a single scale.

## PLOS ONE batch 15 — user adjudication pass on resp/rt semantics (2026-08-02)

Ben spot-checked several tables' actual response semantics; two findings
required removing tables, one required a script fix.

- **`dasilva_2018_mbds`/`_bsq`/`_whoqol`/`_phcs`/`_tfeq` removed** (all 5
  tables from `10.1371/journal.pone.0199480`). `mbds` turned out to have
  79% fractional values, smoothly and densely distributed (0.1, 0.2, 0.3
  ... up to 5.0) -- not the rare-isolated-imputation pattern caught
  elsewhere in this batch, but a distribution consistent with averaged/
  computed composite scores rather than raw single-item Likert
  responses. Given that finding, all 5 tables from this file (which the
  original QC pass had marked clean, since the "<5% fractional" rare-
  imputation check doesn't catch a *majority*-fractional column) were
  removed rather than assuming only `mbds` was affected. Script and
  biblio rows deleted.
- **`dasilva_2019_medicinal_plants` removed** (`10.1371/journal.pone.0214300`).
  The shipped "order-of-mention" interpretation of the 0-15 values
  doesn't hold up against the actual distribution: order-of-mention
  should make low values (1-6) common and high values (15) rare, but the
  data shows the reverse (15 occurs 175x, 2 occurs 2x) -- the true
  meaning of the non-zero values is unknown. Script and biblio row
  deleted.
- **`jiang_2024_*` (all 21 tables) regenerated** with a script fix: the
  source's `totalseconds` field (one whole-survey completion-time scalar
  per respondent, duplicated across every item-row) had been mapped to
  the `rt` column name. Per datastandard.md, `rt` is reserved for
  response-level (per-item) timing; a single value copied across an
  entire respondent's rows is not that. Renamed to `cov_completion_time_s`
  and reshipped as a covariate instead. New standing rule saved to memory
  (`feedback_rt_column_scope`) so this isn't repeated on a future batch.
- **Confirmed valid, no change needed**: `debacker_2018_*` resp=0 (smooth
  0-5 distribution, real low anchor); `kokoszka_2022_who5` resp=0 (WHO-5's
  own official scale is 0-5, "At no time" to "All of the time");
  `cugmas_2021_elderly_social_support` (genuine relationship-type
  counts, 0-14); `puro_2025_prompta_writing` (raw ~8-20-point rubric
  scores); `jiang_2024_*` completion-time *values* themselves (a
  milliseconds reading would put even the slowest respondent under 7
  seconds for a 100+-item survey, which is impossible -- seconds is the
  only plausible unit, matching the source's own `totalseconds` label).
- **`hruby_2018_interview_a`-`_e` removed at Ben's request** (N=8, too
  small). Script, all 5 output tables, and biblio rows deleted.
- **Genuinely uncertain, flagged not resolved**: `zhang_2020`'s
  `tired`/`tired.1` pair -- correctly aligned at the observation level
  (the original "5% agreement" note was a miscalculation, grouped
  incorrectly by `id` alone without accounting for repeated
  observations), the two columns correlate at r=0.74 with a real but
  moderate spread between them -- consistent with either a same-item
  test-retest check within one ESM prompt, or two distinct Chinese mood
  words both glossed as "tired" in English. Left as two separate items
  (already the safer choice), semantic distinction unresolved.

Biblio files updated: `dasilva_2018_*` rows removed from
`biblio_plos_batch15_worthretrying.csv`, `dasilva_2019_medicinal_plants`
row removed from `biblio_plos_batch15_deferred.csv`,
`hruby_2018_interview_*` rows removed from
`biblio_plos_batch15_worthretrying_round2.csv`. **Next step (Ben's
request): consolidate all of this batch's separate biblio/human_review
staging files (deferred, worthretrying round 1, worthretrying round 2)
into a single biblio CSV and a single human_review CSV once adjudication
is finished.**

## PLOS ONE batch 15 — consolidation (2026-08-02)

Merged the 3 separate biblio staging files (`biblio_plos_batch15_deferred.csv`
17 rows, `biblio_plos_batch15_worthretrying.csv` 69 rows post-adjudication,
`biblio_plos_batch15_worthretrying_round2.csv` 61 rows post-adjudication)
into `biblio_plos_batch15_final.csv` (146 rows, no duplicate table names)
and the 2 human_review staging files
(`human_review_plos_batch15_deferred.csv` 2 rows,
`human_review_plos_batch15_worthretrying.csv` 45 rows) into
`human_review_plos_batch15_final.csv` (47 rows, no duplicate DOIs). The 5
source files deleted after merging.

Cross-checked the 146-row biblio against `irw_output/` and found it
empty. Initial read was that Ben had cleared it ahead of upload and the
consolidated files would need a regenerate-then-upload step -- wrong:
moments later Ben confirmed the biblio/human_review/data files were
already uploaded and pasted (see `TODO.md`'s entries, both marked done).
`irw_output/` being empty was simply the normal post-upload cleanup,
same as every other batch. `biblio_plos_batch15_final.csv`,
`human_review_plos_batch15_final.csv`, and the now-superseded
`plos_batch15_worthretrying.csv` (the original 96-row triage/retriage
source, no longer needed once every row's disposition was captured
downstream) all deleted. `dasilva_2018_body_image.py`,
`dasilva_2019_medicinal_plants.py`, and `hruby_2018_brachial_plexus.py`
were deleted outright per the adjudication findings earlier in this
session; `jiang_2024_student_thriving.py` was fixed in place (the
`cov_completion_time_s` rename) and its 21 tables regenerated and
uploaded with that fix applied.

## Standing rule: minimum sample size (2026-08-02)

ben-domingue set a permanent floor for this pipeline: never ship a
dataset with fewer than 50 unique `id` values; ask before shipping
anything with 50-99. Saved to memory `feedback_min_sample_size`. Applies
to every batch from now on, not just PLOS ONE discovery.

## Pooled SAPA-Project personality table, 2017-2024 (2026-08-02)

`data/sapa-personality.R` (existing `sapa_personality` table, 2013-2014
window) and `data/icar_sapa.R` (existing `icar_sapa` table, 2010-2013
window, cognitive ability not personality) were checked for redundancy at
ben-domingue's request before adding a third SAPA table -- confirmed not
redundant with each other (different constructs, non-overlapping windows,
no item overlap).

TODO.md had 7 not-yet-processed SAPA-Project annual personality releases
(2017 through 2023-24, DVN/PNGUT5, DVN/7A9YMV, DVN/FUUB2Q, DVN/YOEEDQ,
DVN/JOGYUD, DVN/BVF52I, DVN/3BTT82, all CC0 1.0) awaiting a scope decision.
Downloaded all 7 SAPAdata CSVs directly (file ids 10988792, 10988863,
10988866, 10988879, 10988881, 10988884, 10988887) and confirmed their
135-item `q_###` column header is byte-identical across all 7 (hashed) --
same fixed item bank every year, only the respondent cohort changes.
Given that, and that the existing `sapa_personality` table is already a
single continuous-window table (not split internally), ben-domingue
decided (2026-08-02) to pool all 7 years into one new table with
`cov_year`, rather than 7 separate tables or a single-year-only table.

Full pooled population is ~2,284,508 unique respondents / ~155.7M
item-response rows -- far larger than typical for this pipeline (would be
~8-12GB as plain CSV). ben-domingue's direction: take a random sample of
1,000,000 respondents (seed=42) after pooling, save as plain CSV, and
document the sampling in the biblio Notes field. Per-year raw ids are
file-local and overlap across years (2017-2019 files even share id values
up into the millions from what looks like a shared master-rownumber
space), so `id` is a composite `"<orig_id>_<year>"` string rather than a
numeric offset.

Wrote `data/condon_2024_sapa_personality.py` (fetches each year's SAPAdata
CSV directly from Dataverse by file id, concatenates, samples, melts to
long format). First run wrote to `automated_finding/` directly (not
`irw_output/`) per ben-domingue's initial request, since he wanted to
upload it somewhere separate from the rest of that day's batch; output
confirmed correct (68,188,858 rows, 999,998 ids -- 2 short of 1,000,000
because a couple of sampled respondents had zero non-NA item responses
and dropped out during the NA-drop step -- 135 items, resp 1-6, all 7
years present). ben-domingue then decided (same session) to add it to
Redivis alongside the rest of the current batch instead, so the file was
moved into `irw_output/` and the script's `OUT_PATH` updated to write
there directly on any future re-run.

Biblio entry (`biblio_condon_2024_sapa_personality.csv`, 1 row) written
noting: the sampling method, the composite-id scheme, and its relationship
to `sapa_personality` (non-overlapping window, different and larger item
pool -- no respondent or item duplication) and `icar_sapa` (unrelated
construct). Uploaded to Redivis and pasted into the dictionary sheet
(confirmed 2026-08-02, ben-domingue); `irw_output/condon_2024_sapa_personality.csv`
and `biblio_condon_2024_sapa_personality.csv` gone from disk as expected.

## PLOS ONE batch 16 (2026-08-02)

30 search terms recycled from `search_terms_log.csv`'s non-PLOS pool per
`SKILL.md`'s reuse method (Big Five personality, cognitive reflection, stop
signal, theory of mind, math anxiety, emotion regulation, impulsivity,
self-compassion, attachment style, loneliness, grief, mindfulness, moral
reasoning, trust in government, social emotional learning, eysenck
personality, narcissistic/dark-triad/psychopathic/borderline personality,
generalized anxiety disorder, social/health/death anxiety, panic disorder,
bipolar disorder, emotional exhaustion, posttraumatic stress, childhood
trauma, perceived stress) — logged to `search_terms_log.csv`.
`irw_discover_plos.py` run: 3,065 candidates -> 18 `good` + 527
`human_assistance` (rest `no_usable_file`/`not_item_response`/
`download_failed`/`error`/`timeout`). `irw_retriage_ha.py` on the
`human_assistance` bucket -> 98 `worth_retrying` + 1 `recoverable_format` +
155 `human_review` + 163 `aggregate_continuous` + 110 `not_item_response`.

**New standing rule applied for the first time this batch**: ben-domingue
set a minimum-N floor when invoking this session (`feedback_min_sample_size`
memory) — never ship N(unique id)<50, ask before shipping 50-99. Of the 18
`good` rows: 3 dropped for N<50 (selfish-intentions N=48, emotion-regulation/
face-recognition N=42, eye-contact-perception N=22), 4 in the 50-99 band
were all declined by ben-domingue when asked (mindfulness/compassion N=56,
health policy attitudes N=59, avoidance/anxiety-over-time N=91, schools'
resilience tool N=91), 1 (`0235595`, imitation task, N=121) turned out to be
a duplicate of a candidate already deferred from batch 13 — left alone
rather than reprocessed.

Of the remaining 10 `good` candidates (N>=100): `qiang_2025_red_tape` (DOI
`0327359`) turned out to be an **exact duplicate** of a paper already fully
processed and uploaded in batch 15 (`data/qiang_2025_red_tape.py` already
existed on disk with 8 tables shipped) -- confirms the discovery-run DOI
exclusion list wasn't fully refreshed before this run; not reprocessed, no
changes made to the existing script. 6 more were structurally disqualified
after inspection (all confirmed via the source paper's own Methods text
rather than guessed):
- `0236271` (puppy behavior test) -- confirmed via WebFetch that the "Data
  averaged" sheet is an inter-rater average across 3 assessors, not raw
  single-administration scores. Skipped.
- `0201698` (positive/negative affect, Spanish children) -- confirmed all 5
  columns (PA, SPdict, PRdict, FRdict, HDdict) are summed PANAS-C/CASAFS
  subscale composites, not raw items. Skipped.
- `0352434` (MBSR perioperative HCC) -- mostly HADS/SUPPH subscale sums;
  the one repeated-measures raw column (NRS pain, 4 timepoints) is a single
  item, which the standing no-single-item-scale rule excludes. Skipped.
- `0246894` (COVID-19 unusualness/stress network study, Korea) -- all 6
  columns are subscale composite sums (values up to 36, too large for a
  single Likert item); consistent with prior findings on this exact DOI
  from an earlier batch (`BATCH_LOG.md` lines ~1269/1356). Skipped.
- `0268756` (handwriting allographic features) -- per-letter forensic
  handwriting feature codes (stroke shape, crossbar position, etc.), not
  psychological item response; a possible nominal-standard candidate but
  out of scope for the core pipeline this pass. Skipped.
- `0276665` (Swiss summer camp socio-emotional development) -- genuine
  92-item pre/post multi-scale battery with reverse-coded ("R"-suffix)
  items, but bundles at least 3 distinct scales under one item-numbering
  sequence with unclear boundaries -- needs the paper's Measures section
  mapped in detail. Deferred, not skipped; added to
  `plos_deferred_candidates.csv`.

Remaining 3 `good` candidates shipped, 7 tables, 3 papers (all confirmed
via WebFetch against the source paper's Methods text before scripting):
- `daiku_2021_dirty_dozen`/`_lie_scale`/`_lying_frequency` (`0249815`,
  Daiku, Serota & Levine 2021, "A few prolific liars in Japan", N=305):
  Dark Triad Dirty Dozen (12i), lie scale (3i, paper notes the authors
  themselves excluded it from their own analysis for low reliability but
  it's genuine raw data), and a 10-item lying-frequency-by-target/channel
  count scale. The `guilt`/`ability`/`acceptance`/`confidence` columns were
  confirmed to be 4 unrelated single-question measures (not sub-items of
  one scale) -- not shipped, since each is a single-item measure on its
  own. `totallie` (aggregate) and `lastlie` (categorical text) also not
  shipped.
- `horiuchi_2024_attachment`/`_dissociation`/`_rsmsm` (`0298214`, Horiuchi,
  Nishimura, Taniike & Tachibana 2024, N=214 Survey 1 / N=225 Survey 2):
  ADAS-R-derived attachment items (20i), Child Dissociative Checklist
  (20i, same Survey-1 sample), and the paper's own new RS-MSM scale (20i,
  separate Survey-2 sample). Both raw files needed a 2-3 row header offset
  (blank super-header + group-label row before the real column names).
- `jimenezherrera_2022_moral_sensitivity` (`0270049`, Jimenez-Herrera et
  al. 2022, Moral Sensitivity Questionnaire Spanish validation, N=751,
  9 items).

**`worth_retrying` pool (98 rows)**: bulk-checked all DOIs against
`BATCH_LOG.md`/`TODO.md` before any manual review -- 32 were already-known
duplicates from earlier batches (batches 6/8/9/10/11/12/13/14/15's
worth_retrying/deferred pools, e.g. `0262716` = `anjum_2022_gad7`), left
untouched. Of the 66 genuinely-new rows, the top ~13 by N were downloaded
and inspected (25 more have no parseable N and weren't reached this pass).
4 papers shipped, 11 tables:
- `pavic_2022_vaccine_conspiracy`/`_natural_immunity`/`_healthcare_trust`/
  `_science_literacy` (`0264722`, Pavic & Suljok 2022, N=577): 4 named
  instruments (Shapiro et al. vaccine-conspiracy scale 7i, VAX
  natural-immunity subscale 3i, Shea et al. healthcare-trust scale 8i,
  Oxford/Eurobarometer science-literacy scale 15i binary). `_rec`
  (reverse-coded duplicate) and `_total` (composite) columns excluded;
  text-Likert labels recoded to 1-5 (confirmed via `WebFetch` against the
  paper's Measures section for what each prefix means).
- `tuason_2021_covid_coping_enjoy`/`_loneliness_emotional`/
  `_loneliness_social`/`_wellbeing`/`_sense_of_agency` (`0248591`, Tuason,
  Guss & Boyd 2021, "Thriving during COVID-19", N=938): author-created
  23-item COVID coping/enjoyment checklist (binary), De Jong
  Gierveld/Van Tilburg loneliness scale (emotional + social subscales, 3i
  each, text "Yes"/"More or less"/"No" recoded 0-2), an 8-item wellbeing
  scale, and the 6-item Sense of Agency Scale. The WB (coded 18-24) and
  S_Agency (coded 97-105) columns initially looked like a data artifact --
  confirmed via cardinality check (WB: exactly 7 distinct values per item,
  matching a 7-point scale; S_Agency: exactly 9, matching the paper's
  stated 9-point Likert) that these are just an offset raw-value coding
  from the source survey platform, not corrupted data. `_rec` and
  `_Total`/`_Mn`/`_overall` columns excluded as reverse-duplicates/
  composites.
- `gumus_2025_dietarian_identity` (`0327116`, Gumus, Macit, Demirci &
  Kizil 2025, Turkish Dietarian Identity Questionnaire validation, N=487,
  33 items): used the file's own pre-recoded `DIQ##value` numeric columns
  (1-7) rather than the parallel text-Likert `DIQ##` columns holding the
  same items; `Total*` subscale-sum columns excluded.
- `machado_2020_cat_separation` (`0230999`, Machado, Oliveira, Machado,
  Ceballos & Sant'Anna 2020, cat separation-related-problems questionnaire,
  N=223 cats): 7-item binary problem-behavior checklist; non-human
  respondents (id = cat, owner is a covariate), consistent with prior
  `muller_2016_dog_inhibition` precedent that IRW's format doesn't require
  human respondents. Housing/environment columns (access to toys, outdoor
  access, etc.) are covariates, not part of the same construct -- not
  shipped as items.

6 more of the top-13 were inspected and skipped/deferred (all confirmed,
not guessed):
- `0153663` (predicting higher-ed performance) -- subject-level exam/GPA
  scores across different domains (English/Math/Psychology raw test
  scores, HS grades, course credits), not a Likert item battery. Skipped.
- `0284383` (CAM/homeopathy beliefs) -- every column already a computed
  subscale/composite score (Big Five traits, numeracy, death anxiety,
  etc.), no raw items present. Skipped.
- `0268773` (Chinese college students anxiety/depression) -- all 6 columns
  are named composite instruments (SF-36 PCS/MCS, PSQI, depression,
  anxiety totals), no raw items. Skipped.
- `0154145` (facial affect labeling, schizophrenia/BPD) -- derived
  task-accuracy ratios and clinical composite scores (BPDSI, PANSS, BDI),
  not raw Likert items. Skipped.
- `0217482` (leader-follower dyad job resources) -- all columns are
  mean-centered/standardized (z-scored) derived variables, not raw items.
  Skipped.
- `0278201` (fWHR/mandibular-angle vs. personality) -- the 16 personality
  columns are Cattell 16PF primary-factor scores (already-scored composite
  output of a full battery), not raw item responses. Skipped.
- `0189915` (Sierra Leone health-insurance willingness-to-pay, N=4648) --
  large (83-column) household survey with cryptic section codes
  (SAQ/SBQ/SCQ/SDQ/SEQ) spanning unrelated topics (livestock, demographics,
  health); the actual WTP items aren't identifiable without the survey
  instrument/codebook. Deferred, not skipped; added to
  `plos_deferred_candidates.csv`.
- `0220658` (trust/proximity vaccine propensity, N=1006) -- only 4 items,
  each on a different response scale/construct (trust, 2 likelihood
  ratings, 1 belief rating); too heterogeneous to treat as one coherent
  instrument without more text from the paper. Deferred; added to
  `plos_deferred_candidates.csv`.

Remaining ~53 of the 66 genuinely-new `worth_retrying` rows (mostly N<100
or unparsed-N) not individually reviewed this pass -- `plos_batch16_
triage.csv`/`plos_batch16_retriage.csv` held them; per the pattern used in
the batches 6/9/12/13 sweep, these are being written off rather than kept
open-ended, since the highest-N/most-promising rows were already covered.

Two staging biblio files this batch: `biblio_plos_batch16.csv` (7 rows,
the `good`-candidate tables) and `biblio_plos_batch16_worthretrying.csv`
(11 rows, the `worth_retrying`-pool tables) -- left as separate files per
ben-domingue's mid-batch instruction to remove each as its own tables are
added, rather than consolidated into one file first.

## First scheduled monthly discovery run + triage (2026-08-03)

Landed the first live run of `irw_discover_monthly.py` (a new script added
this batch -- see its own docstring and `README.md` for the incremental
`--since`-per-term design): 100 terms against OSF+Dataverse. The cloud
routine that ran it hit two access issues that shaped how the output got
handled -- both worth knowing about before relying on this routine again:
- The container's egress allowlist blocked `api.osf.io` and
  `dataverse.harvard.edu` outright on the first scheduled fire; fixed by
  widening the environment's network egress allowlist, then re-run
  succeeded.
- The routine's GitHub App lacks write access to this repo, so it
  couldn't push its branch/PR on the successful run either -- it sent the
  two output files (`monthly_candidates_2026-08-03.csv`,
  `search_terms_log.csv` rows) directly instead. Landed manually: cross-
  checked the 223 raw hits against the live IRW dictionary (the routine's
  own exclusion check had separately failed on a Google Sheets egress
  block) and deduped, dropping 13 already-known-DOI rows and 80 in-run
  duplicates (one dataset matching multiple search terms) -- 130 unique
  candidates. GitHub App write access still needs to be granted by a repo
  admin before a future run can open its own PR; until then this manual
  landing step repeats each month.

Full triage (`irw_batch_updated.py`) on the 130: 1 `good`, 38
`human_assistance`, 3 `not_item_response`, 81 `no_usable_file`, 1
`license_restricted` (cc-by-nc-sa, correctly excluded), 6
`download_failed` (4 transient-looking 403s on Dataverse, plus 2 real
parsing bugs -- a UTF-8 decode error and a CSV field-count mismatch --
not yet investigated).

**Pipeline fix found via this batch**: `.tab` files (Dataverse's default
archival format for tabular data) were invisible to the whole
discover/triage pipeline -- absent from `TABULAR_EXT`, and even if added
there, `load_table()`'s `_read_tabular` only special-cased `.tsv` for
tab-separated parsing, so a `.tab` file would've been silently misread
with a comma separator. Fixed both (now recognizes and correctly parses
`.tab`). Confirmed real impact, not theoretical: 2 of the first 10 rows
in this batch flipped from `no_usable_file` to `human_assistance` once
fixed, including one of the batch's named-instrument candidates (Bem
Sex-Role Inventory replication data, `10.7910/DVN/R6WE4P`). This is a
standing gap, not specific to this batch -- some unknown number of past
Dataverse `no_usable_file` rows in earlier batches may have had a `.tab`
file available; re-triaging historical batches to find out is a scope
decision left open, not done as part of this fix.

Retriage (`irw_retriage_ha.py`) on the 38 `human_assistance` rows: 9
`not_item_response` (drop), 20 `aggregate_continuous`, 4 `worth_retrying`
(not yet reviewed -- see URLs in the retriage CSV), 5 `human_review`
(needs a person; includes the Ukrainian SOA-questionnaire candidate).
Note the Bem Sex-Role Inventory candidate above landed in
`aggregate_continuous` on this automated pass (dup_id_item ratio 11x) --
flagged as a judgment call worth a manual second look given it's a
named, validated instrument, not acted on further this batch.

The 1 `good` candidate was written up: Falih (2026), a CC0 Harvard
Dataverse deposit ("maladaptive daydreaming, depression, anxiety and
stress data", N=262) containing two distinct instruments in one raw
`.tab` file -- Maladaptive Daydreaming Scale-16 (0-10 scale) and DASS-21
(0-3 scale) -- split into two output tables per datastandard.md's
one-instrument-per-file rule: `falih_2026_mds16` and `falih_2026_dass21`
(`data/falih_2026_mds16.py`, `data/falih_2026_dass21.py`). Six all-null
section-header artifact columns in the raw file (`MDS16`, `DASS21`,
`DEPRESSI`, `ANXIETY`, `STRESS`, `V52`) were dropped rather than shipped
as empty items/covariates. Both tables passed full QC (unique id,
integer-only responses, no sentinel/imputed values, no aggregate
totals in the item list). Staged as `biblio_falih_2026.csv` (2 rows) --
not yet pasted into the dictionary sheet.

Not yet done from this batch, left open in `TODO.md`: the 6
`download_failed` retries, the 2 real parsing-bug investigations, the 4
`worth_retrying` and 5 `human_review` rows from the retriage pass, and
manually checking the OSF pages for the three named-instrument
candidates (Vanderbilt ADHD Diagnostic Parent Rating Scale, BDI-II,
Resuscitation Self-Efficacy Scale for Nurses) that triaged
`no_usable_file` even after the `.tab` fix -- their landing pages may be
hiding a file behind a restricted sub-component rather than truly
having none.

## PLOS ONE batch 17 (2026-08-03)

Ran the 30 already-logged-but-never-executed terms found orphaned in
`search_terms_log.csv` (dated 2026-08-02, tagged `plos_batch17_triage.csv`
but with no corresponding output file, `BATCH_LOG.md` entry, or `TODO.md`
item -- an earlier session apparently logged the terms without ever running
or landing the discovery pass, consistent with this repo's documented
Dropbox-sync file-loss pattern). Recycled non-PLOS instrument/construct
terms per `SKILL.md`'s reuse method: item response theory, reaction time
task, reading fluency, phonological awareness, mathematics achievement,
stroop, n-back, patient reported outcomes, numeracy, phonics, lexical
decision, word recognition, depression, anxiety, stress, psychopathy,
neuroticism, pain, reading comprehension, narcissism, PTSD, ADHD, autism
spectrum, substance use, vocabulary, spelling, working memory, inhibition,
fatigue, wellbeing.

**Mid-run incident**: a per-candidate worker (crash-isolated via
`ProcessPoolExecutor`, `irw_discover_plos.py`) hit a `FutureTimeoutError`
and, instead of being killed, ran on unattended for 30+ minutes, growing to
~22GB RSS and dropping host free memory to 332MB of 30GB before being
SIGTERM'd by hand. Root cause: `pool.shutdown(wait=False,
cancel_futures=True)` only drops futures that haven't started yet --
`ProcessPoolExecutor` has no public API to kill an already-running task, so
the timed-out worker kept executing (almost certainly deep in an `.xlsx`
parse, a known memory-blowup pattern per `README.md`'s Prerequisites note)
even after the driver logged a `timeout` row and moved on. Fixed by adding
`_kill_pool_workers()`, which grabs the pool's underlying
`multiprocessing.Process` objects via the `_processes` internal (stable
across CPython 3.3-3.13 in practice) and forcibly `.terminate()`s/`.kill()`s
them on timeout. Landed mid-run, so it didn't help this run's own
orphaned worker (already loaded with the old code) but applies to every
run from here on. Not a size-guard gap -- `MAX_FILE_BYTES` (2026-08-02)
guards download size, not in-memory parse size, and this file was well
under the 200MB download ceiling.

3660 candidates -> 24 `good` + 512 `human_assistance` + 99
`not_item_response` + 26 `error` + 25 `download_failed` + 2970
`no_usable_file` + 3 `timeout` + 1 `crashed` (the crash: a single
corrupt file segfaulted its isolated worker, correctly recorded and the
batch continued). Retriage (`irw_retriage_ha.py`) on the 512
`human_assistance` rows: 101 `worth_retrying` + 146 `human_review` + 183
`aggregate_continuous` + 82 `not_item_response`.

**Good-candidate review** (24 rows): applied the standing min-N rule first
(`feedback_min_sample_size`) -- 9 dropped for N<50, 1 (N=91, avoidance-
behavior/anxiety study) referred to ben-domingue who said ship if otherwise
clean. Of the 15 survivors, full inspection (downloaded every file,
checked `extract_si_files()`'s complete SI list, checked column
values/ranges) found:
- **Real, shippable**: `hicks_2020_bioveda` (16 binary items, N=770),
  `stachl_2020_belonging` (13 items 0-4, N=183, "." sentinel), `bittencourt_
  2021_dfs2` (Brazilian-Portuguese Dispositional Flow Scale 2, 36 items
  1-5, N=681), `hewei_2022_msva_purchase` (14 items 1-5, N=752;
  completion-time column parsed to `cov_completion_time_s`, IP+geolocation
  column dropped as PII), `carney_2023_substance_use` (8-substance binary
  checklist, N=414), `sun_2026_eap_syllabus` (4 distinct question blocks
  under one 1-5 scale, split into 4 files -- usage/difficulty/content/
  methods -- by item-numbering reset, N=650 each), `shen_2020_sas20`
  (Zung SAS-20, merged from 5 per-hospital files with identical columns,
  id offset per hospital, text-coded Likert like "considerable
  time(3.0)" decoded to its embedded number, N=1647).
- **False positives, dropped**: `10.1371/journal.pone.0193861` (bibliometric
  systematic review of citation metrics, not human item response),
  `10.1371/journal.pone.0142551` (file holds only derived signal-detection
  stats -- counts, z-scores, d'/c -- no raw per-trial responses),
  `10.1371/journal.pone.0143395` (only composite "Depressive symptoms"/
  "GALES" scores + genotype, no raw items), `10.1371/journal.pone.0180298`
  (only baseline/follow-up composite anxiety scores, no raw items),
  `10.1371/journal.pone.0238022` (triage's n_participants=112 was actually
  the row count -- true N=14 unique subjects, below the min-N floor;
  second SI file is fMRI ROI activation, not item data anyway),
  `10.1371/journal.pone.0215433` (Ghana Multidimensional Poverty Index --
  derived/weighted deprivation indicators from a household economic
  survey, not psychometric item responses despite fitting the mechanical
  binary-item schema).
- **Deferred, too complex to rush**: `10.1371/journal.pone.0299971`
  (health-literacy self-care survey bundling at least 6 distinct scales --
  ACCESS/10, INT/7, ATT/10, SE/8, SC/15, a 66-item HL block, FL/6 --
  including reverse-coded `_R` duplicate columns needing exclusion; named
  3 of the 4 confirmed instruments via WebFetch of the Methods text but
  the HL/SC blocks need more paper time).

**worth_retrying pool** (101 rows, N from 22 to 6297): per ben-domingue's
direction, hand-reviewed the top 15 by N rather than all 101 or none.
Found 2 more real, shippable tables: `yu_2015_family_environment` (Family
Environment Scale, 21 raw items E1-E21 kept, 10 derived subscale-total
columns excluded, N=4582 -- caught a real id-column bug: the raw `Number`
column is *not* a unique person id, rows sharing a `Number` have different
Gender/Age, so `id` falls back to row index per `datastandard.md`'s
"Missing person ID" guidance) and `jelinek_2021_cdi` (Children's
Depression Inventory, 27 items 0-2, N=1515, `cov_sub_sample` distinguishes
the paper's CFA/EFA subsamples). 2 more deferred as genuinely promising
but too complex for this pass (added to `plos_deferred_candidates.csv`):
HELMA health-literacy scale (`10.1371/journal.pone.0149202`, 7 named
subscales with inconsistent response encodings per block -- some
text-coded frequency Likert, one correct/incorrect) and a 231-column
Portuguese preoperative-stress file (`10.1371/journal.pone.0263275`)
bundling genuine IDATE (Brazilian STAI) state/trait items and an SRQ item
among medication-dosage and VAS columns. The other 11 of the top 15 were
firm/historical/physiological data (EMG sensor signals, 18th-century
baptism records, firm-year panel data), composite-scores-only files (SF-36/
PSQI/CES-D totals, Big-Five/CRT/numeracy totals, neuropsych test batteries,
session-level averages/SDs), stimulus materials (pre-rated word-pair norms,
not respondent data), or demographic/derived-index survey data with no
coherent item battery (UDAYA India adolescent survey) -- confirmed
not-a-fit, not shipped. Remaining 86 unreviewed rows written off per the
established batches-6/9/12/13/16 pattern; DOI/title/n/items are in
`plos_retriage_batch17.csv` if reconsidered later.

**Output**: 12 tables across 9 papers -> `biblio_plos_batch17.csv` (12
rows), staged for Redivis upload + dictionary paste.
`human_review_plos_batch17.csv` (146 rows) staged for the "Human eye"
sheet. All 30 search terms already carried the `plos_batch17_triage.csv`
tag in `search_terms_log.csv` from the earlier orphaned logging, so no
further logging needed this batch.

## Backlog-resolution pass across 13 deferred/open items (2026-08-03)

Ben-domingue gave explicit steering for this pass: "anything that is
low-priority or hard to recover, let's give up (and strike from list)" --
bias toward closing items out rather than deferring again. Worked through
every open deferred candidate and monthly-discovery follow-up item on the
list (parallelized across 4 sub-agents for the paper-read-heavy PLOS items
plus direct work on the monthly-discovery bucket). Net result: **24 new
IRW tables processed** (11 papers/datasets), **1 general pipeline bug
fixed**, **7 items struck** with reasons logged, **1 dataset newly
license-blocked** (logged, not lost).

### Processed -> `biblio_backlog_resolution.csv` (24 rows, ready for
Redivis upload + dictionary paste)

- **HELMA health-literacy scale** (`10.1371/journal.pone.0149202`, PLOS
  batch17 deferred, N=582) -> 7 tables (`ghanbari_2016_helma_access/
  _reading/_understand/_appraise/_use/_comm/_numeracy`). The S4 scoring
  manual didn't match the raw `.sav` columns, so each subscale's response
  encoding was verified directly from per-item value_counts instead of
  trusting the manual: access/reading/understand/appraise/use/comm are
  clean 1-5 Likert, numeracy is clean binary correct/incorrect (confirming
  the original triage flag). `data/ghanbari_2016_helma.py`.
- **Swiss summer camp socio-emotional study** (`10.1371/journal.pone.0276665`,
  PLOS batch16 deferred, `good`-flagged, N=256, 92 items) -> 3 tables
  (`gerber_2022_altruism`, `_selfesteem`, `_eas_temperament`). The paper's
  Measures section cleanly mapped every column: adapted Self-Report
  Altruism Scale (14 items), Maintier & Alaphilippe self-esteem
  questionnaire (9 items), French EAS temperament questionnaire (20 items,
  4 subscales x 5, reverse-coded "R"-suffix items flipped per the paper's
  own convention). One-off camp-control columns (S8-S10/Q10/Q12) dropped.
  `data/gerber_2022_swisscamp.py`.
- **Imitation task** (`10.1371/journal.pone.0235595`, PLOS batch13
  deferred) -> `vaporova_2020_imitation` (3 binary items, N=82). The
  "multi-block layout issue" was just a stacked Infants/Children +
  Adults sheet with two different column sets; the imitation scale only
  exists in the first (regular) block. `data/vaporova_2020_imitation.py`.
- **Illusory-body-ownership embodiment questionnaire**
  (`10.1371/journal.pone.0277080`, PLOS batch13 deferred) ->
  `preussmattsson_2022_ownership` (24 items = 6 statements x 4 conditions,
  N=50). The originally-flagged sheet (N=30) is below the N=50 floor, but
  a second sheet in the same workbook ("SCR Experiment-Questionnaire")
  administers the identical 6-item questionnaire to a different N=50
  sample -- used that instead, clearing the floor without a judgment call.
  No out-of-range values found on inspection. `data/preussmattsson_2022_ownership.py`.
- **Situational-motivation EMA study** (`10.1371/journal.pone.0307369`,
  the same DOI deferred separately in both batch 9 and batch 13 -- resolved
  once, closing both TODO entries) -> 2 tables (`strohacker_2024_bmzi_motive`,
  `strohacker_2024_arms_readiness`; 11 and 10 items, N=22, 519 EMA
  sessions, `wave` = session sequence). Turned out simpler than the old
  triage note suggested: the raw sheet is a flat one-row-per-session table
  once an embedded codebook row is skipped -- a header-offset issue, not
  deep reconstruction. `data/strohacker_2024_situational.py`.
- **MnemoCity Task usability survey** (`10.1371/journal.pone.0161858`,
  PLOS batch12 deferred) -> `rodriguezandres_2016_mnemocity_usability` (9
  items, N=160). Paper's Methods text cleanly separated the 9 raw 1-5
  Likert usability/satisfaction items from derived CBTT/MnemoCity
  cognitive-task scores and composite means. `data/rodriguezandres_2016_mnemocity_usability.py`.
- **Clinton-voter activism longitudinal study**
  (`10.1371/journal.pone.0221754`, PLOS batch8 deferred) -> 2 tables
  (`dwyer_2019_clinton_cesd`, `dwyer_2019_clinton_activist`). The raw
  `.sav` already has an explicit `Wave` column (1=T2, 2=T3) with genuinely
  varying CESD responses -> mapped to `wave` 2/3; the 8-item Activist
  scale is baseline-only (constant across a person's wave-rows) so shipped
  cross-sectionally. `data/dwyer_2019_clinton_activism.py`.
- **Emotional-eating chain-mediation study**
  (`10.1371/journal.pone.0280701`, PLOS batch8 deferred) -> 4 tables
  (`yang_2023_emotional_eating_eesr/_cesd/_uppsp/_ders`; EES-R 23 items,
  CES-D 20, UPPS-P short form 20, DERS 36). The cryptic `@10.`/`@11.`-style
  block labels were matched to instrument item counts from the paper's
  Measures section. `data/yang_2023_emotional_eating.py`.
- **Chinese EFL learning study** (`10.1371/journal.pone.0280919`, PLOS
  batch8 deferred) -- **struck**: the 481-vs-942 row mismatch traced to a
  non-unique `index` key (even `Gender` differs across rows sharing the
  same index in 243/285 duplicated-index groups) -- not a clean dedupe or
  wide-to-long artifact, and per steering non-English item-level recoding
  on top of that isn't worth pursuing. Row was never in
  `plos_deferred_candidates.csv` (tracked only in `TODO.md`); removed from
  `TODO.md`.
- **Children's implicit/voluntary attention-in-time study**
  (`10.1371/journal.pone.0123625`, PLOS batch12 deferred) -- **struck**:
  checked all 62 per-participant sheet headers directly -- 4 different
  column schemas across sheets (not uniform), so a trivial glob+concat
  isn't possible; genuine per-sheet reconciliation needed. Struck per the
  hard-to-recover steering. Removed from `TODO.md`.
- **Portuguese preoperative-stress study**
  (`10.1371/journal.pone.0263275`, PLOS batch17 deferred) -- **struck**:
  the paper's Methods section revealed the IE*/IT*-prefixed columns are
  NOT full IDATE state/trait scales -- they're 4-item fragments surviving
  an IRT-based item-reduction into a novel pooled "B-MEPS" instrument
  (drawing from a reduced STAI, MADRS, SRQ-20, and FSPQ), with no codebook
  resolving each fragment's original response-category semantics. Removed
  from `plos_deferred_candidates.csv`.

### Struck outright (per explicit "give up on hard-to-recover" steering)

- **PLOS ONE batch17 -- 86 of 101 unreviewed `worth_retrying` rows**:
  written off per the established batches-6/9/12/13/16 pattern.
  `plos_retriage_batch17.csv` deleted. Removed from `TODO.md`.
- **PLOS ONE batch14 Auricular Acupuncture exam-anxiety study**
  (`10.1371/journal.pone.0168338`, N=44) -- already flagged low-priority;
  confirmed no new reason to revisit. Row removed from
  `plos_deferred_candidates.csv`; already had a fuller writeup earlier in
  this log, so no new TODO ghost entry.
- **Batch21 Romanian teachers' lifelong-learning survey**
  (figshare `10.6084/m9.figshare.31836016`, N=70) -- 7 bundled instruments
  in one non-English file needing per-item reverse-coding judgment calls
  across a non-English instrument; exactly the "hard to recover" case per
  steering. Real, clean, CC BY 4.0 data -- left on the table by choice, not
  because it's unusable, in case a future pass wants to revisit with more
  time. Removed from `TODO.md`.
- **Batch21 visual-impairment functional-mobility kinematics dataset**
  (Dataverse `DVN/0LWF5Z`, N=54) -- one fresh WebSearch attempt for the
  source manuscript (title search + author-name search) still turned up
  nothing findable as of 2026-08-03; struck per steering (missing paper
  blocks the NASA-TLX subscale-order mapping, can't guess it). Removed
  from `TODO.md`.

### Monthly discovery (2026-08-03) follow-ups resolved

- **Pipeline fix**: `load_table()` in `irw_triage_updated.py` now falls
  back to `latin-1` when a `.csv`/`.tab` file fails UTF-8 decoding, instead
  of failing the whole candidate outright. Confirmed real impact: one of
  the 6 `download_failed` rows (`10.7910/DVN/33EY6I`) was a
  semicolon-delimited Hungarian math-anxiety dataset that decodes cleanly
  under latin-1 -- turned out to be a near-duplicate of an
  already-known/already-flagged `aggregate_continuous` dataset
  (`10.7910/DVN/XOPDQ5`, "Expectancies... Mathematics Anxiety"), so not
  reprocessed, but the fix itself is general and should help future runs.
- **4 Dataverse 403s** (`DVN/TZPHXF`, `DVN/DLW5QY`, `DVN/ZKYKW0`,
  `DVN/JQEYBB`): confirmed via the dataset API that none of the underlying
  files are actually access-restricted (all `restricted: null`), so the
  403 isn't a real permissions gate -- retried directly with `curl`, all 4
  still 403'd. Per steering, one retry was enough; struck.
- **Field-count-mismatch CSV** (`osf.io/y2mcb`, "Database_March 2025.csv"):
  investigated directly -- semicolon-delimited Hungarian file with
  unescaped embedded newlines/quotes in free-text open-ended answer
  columns (health-behavior goals), not a fixable delimiter/encoding issue,
  and the bulk of the content is open-ended text rather than item
  responses anyway. Logged as a known limitation, not pursued further.
- **4 `worth_retrying` rows** from `irw_retriage_ha.csv`, each given a real
  look:
  - `10.7910/DVN/OLOMAI` ("The Trait-State-Experience Pathway...") ->
    **processed**: `nabizadehchianeh_2026_tempsa` (TEMPS-A short form, 39
    binary items, N=713 after dropping 3 duplicate-ID rows -- the actual
    cause of the original `dup_id_item` QC failure). Derived
    TEMPS-A-subscale totals and SAM pleasure/arousal ratings excluded
    (different instrument / composite scores). `data/nabizadehchianeh_2026_tempsa.py`.
  - `osf.io/gdbq2` (bystander/moral-disengagement study, `JSP_Bystander_SPSS__data.sav`)
    -- structurally excellent (clean id, 8 well-labeled instrument blocks:
    ERQ, distancing, bystander behavior, bystander intervention, moral
    disengagement, GSE, POMS, subjective well-being; N=1122, all clean
    ordinal ranges) but the OSF node has **no license set at all** (checked
    via API, not an unresolved UUID) -- per the license rule, not
    processed. Logged to `license_blocked_candidates.csv` instead of
    silently dropped, since it's otherwise a strong candidate.
  - `10.7910/DVN/ZA15RI` (Spanish-language "Psychological Uses of AI in
    Adolescence" scale-development study) -- **struck**: multiple bundled
    Spanish-language instruments (a novel MPUAI scale, HPN happiness item,
    SS social-support scale) under one numbering sequence needing
    per-block mapping in a non-English file; hard-to-recover per steering.
  - `10.7910/DVN/IRIKMP` (Namibian drought-adaptation psychosocial survey,
    300 columns) -- **struck**: mostly one-off multi-select
    concern/barrier checkbox columns rather than coherent Likert scale
    blocks; would need substantial digging to locate the actual named
    psychosocial-outcome scales.
- **5 `human_review` rows** staged to `human_review_monthly_20260803.csv`
  for the "Human eye" sheet (unchanged from `irw_retriage_ha.py`'s
  classification: reaction-time trial data with an uninformative item
  column, a 2-participant correspondence database, a heart-failure
  diet-intervention pilot with no clear item columns, a Kenya/Malawi
  managerial-personality dataset, and the Ukrainian SOA-questionnaire
  codebook-only file).
- **3 named-instrument OSF candidates flagged `no_usable_file`** -- checked
  each for a hidden/restricted sub-component:
  - Vanderbilt ADHD Diagnostic Parent Rating Scale (`osf.io/9urkt`):
    confirmed genuinely no data file -- only a masked manuscript and R
    analysis scripts (`.Rmd`, no raw data attached). Struck.
  - Resuscitation Self-Efficacy Scale for Nurses (`osf.io/5amfx`):
    confirmed the OSF node has zero files and zero child components.
    Struck.
  - **BDI-II in Mexican University Students** (`osf.io/6dutb`) --
    **processed**: a real data file (`BDI.dat`) was hiding behind an
    extension (`.dat`) the pipeline doesn't recognize as tabular. The
    project's own `CODEBOOK.txt` documents it precisely: 21 tab-separated
    columns, no header, each 0-3 ordinal (the 21 BDI-II items). License
    resolved via the OSF license-id lookup (`563c1cf88c5e4a3877f9e96a` ->
    "CC-By Attribution 4.0 International"). N=508.
    `marquezpalacios_2026_bdi2` -> `data/marquezpalacios_2026_bdi2.py`.
- **Bem Sex-Role Inventory** (`10.7910/DVN/R6WE4P`) -- landed in
  `aggregate_continuous` on the automated retriage pass (mis-detected id
  column driving a spurious `dup_id_item` ratio). Manual check confirmed
  20 clean, self-descriptively-named raw BSRI trait-rating items
  ("Willing to take risks", "Forceful", "Warm", ... -- the standard 20-item
  short form), 1-7 Likert, no missingness, N=695. No id column in the
  source file -- used row index. **Processed**: `holden_2026_bsri` ->
  `data/holden_2026_bsri.py`.

### Housekeeping

Three scripts from the parallelized sub-agents (`data/dwyer_2019_clinton_activism.py`,
`data/rodriguezandres_2016_mnemocity_usability.py`,
`data/yang_2023_emotional_eating.py`) initially read their raw SI file
from a local `automated_finding/scratch_raw/` cache the sub-agent created,
rather than fetching remotely like every other script in `data/` --
patched all three to fetch directly from the PLOS SI URL
(`https://journals.plos.org/plosone/article/file?type=supplementary&id=<DOI>.s001`)
matching the established convention, re-ran and re-verified identical
output, then deleted `scratch_raw/` (would have silently broken
reproducibility otherwise). `irw_triage.csv`, `irw_retriage_ha.csv`, and
`monthly_candidates_2026-08-03.csv` deleted now that every row has been
captured here or in a staged CSV.

**Output this pass**: 24 tables across 11 papers/datasets ->
`biblio_backlog_resolution.csv` (24 rows), staged for Redivis upload +
dictionary paste. `human_review_monthly_20260803.csv` (5 rows) staged for
the "Human eye" sheet. 1 dataset newly added to
`license_blocked_candidates.csv`. 7 items struck with reasons above. 1
general pipeline fix (latin-1 fallback in `load_table()`).

**False-alarm note**: `biblio_plos_batch17.csv` and its 12 `irw_output/*.csv`
files were found missing from disk partway through this pass. Initially
treated as accidental data loss and reconstructed from this entry's detail
plus each `data/*.py` script's Source/DOI header comments (all 9 scripts
re-run, row/id/item counts matched the log above). Turned out to be a
false alarm: ben-domingue was concurrently working in the same repo during
this session, confirmed the upload/dictionary-paste (catching and fixing a
real bug along the way -- `carney_2023_substance_use`'s Description field
had an unescaped internal comma breaking the CSV), and deleted the files
per the normal post-upload cleanup convention -- reflected in `TODO.md`'s
now-`[x]` entries for both files. The reconstructed files were deleted
again once this was discovered, to match the legitimate post-upload state.
Worth knowing for future sessions: `automated_finding/` is a live working
directory the user may be editing concurrently, not an exclusively
agent-owned scratch space -- re-check TODO.md/BATCH_LOG.md and consider
`git status`/mtimes before treating a missing staging CSV as data loss.

## 2026-08-03: PLOS ONE 4-paper `good`-candidate review (manual, ad hoc)

Four PLOS ONE papers flagged `good` by `irw_discover_plos.py` were reviewed
by hand (fetch full SI file list per article, not just the triage-flagged
file, per the "human glance" rule).

- **`10.1371/journal.pone.0287795`** (concealable stigmatized identities in
  academic science/engineering) -- **skipped**. Triage flagged S2 Appendix
  (de-identified data, N=2013) as tabular, but it contains only demographic
  classification / identity-holding indicators (gender, race, income,
  first-gen status, 8 binary "do you hold identity X" flags) -- not a
  coherent multi-item psychometric scale with a shared underlying
  construct. The actual Likert-scale measure described in Methods (4-point
  concealable-stigma ratings, 1=not stigmatized to 4=extremely
  stigmatized) is not in this file; only its regression results are shared
  (S4 Table). No raw item-response data to ship.
- **`10.1371/journal.pone.0180298`** (avoidance behavior, social anxiety
  disorder vs. specific phobia) -- **skipped**. S1/S2 Dataset (SAD n=91,
  phobia n=130) each contain only 6 columns: participant id, "General
  anxiety baseline/follow-up" (BAI total, values like 21/10/6 consistent
  with a 0-63 sum score, not 0-3 per-item), "Avoidance" (single aggregate
  score), number of disorders, treatment flag. Derived/aggregate scores
  only -- no raw BAI or avoidance-situation item-level data shared.
- **`10.1371/journal.pone.0256283`** (ICT integration in teacher education,
  Spain) -- **processed**, 3 tables from one raw response sheet
  (`journal.pone.0256283_S2_File.xlsx`, actually `.s003` -- `.s001` is a
  TIFF diagram, `.s002` the survey-instrument PDF): `valverdeberrocoso_
  2021_sqd` (24 items, 1-6, N=251), `valverdeberrocoso_2021_tictip` (28
  items, 1-6, N=251 -- raw sheet has one more TICTIP item than the paper's
  reported 27, shipped as administered rather than guessing which one the
  paper's factor analysis dropped), `valverdeberrocoso_2021_learning_
  design` (22 items across SPA/RES/PRA dimensions via `item_family`, 1-6,
  N=251). No covariates in the raw sheet despite Methods describing
  demographics. No imputation language found in the article text.
  `data/valverdeberrocoso_2021_ict.py`.
- **`10.1371/journal.pone.0186045`** (leader evaluation and team
  cohesiveness) -- **processed**, `pietraszkiewicz_2017_leader_eval`: team
  members' other-ratings of their leader on 4 skill items (management,
  moderation, empathy, motivation), 0-10 scale with a documented 99=no-data
  sentinel (confirmed via the file's own DataDictionary sheet), 2 waves
  (Time I month 3 / Time II month 9), N=258. The parallel `SelfEvaluation`
  sheet (leaders self-rating, same 4 items/waves) was **not** shipped:
  only 45 leaders, below the N>=50 floor. Also dropped: single-item
  OOE1/OOE2 (overall rating) and FutureL1/"Future L2" (binary
  team-cohesiveness network question) -- both single-item measures;
  O_Attendance2 (wave-2-only covariate, not an item); NameL/NamesM (PII,
  real names) and duplicate "Gender M"/"Gender L" columns.
  `data/pietraszkiewicz_2017_leader_eval.py`.

All 4 articles confirmed CC BY 4.0 on the article page itself ("This is an
open access article distributed under the terms of the Creative Commons
Attribution License...").

**Output**: 4 tables across 2 papers -> `biblio_plos_4paper_review.csv`
(4 rows), staged for Redivis upload + dictionary paste. 2 papers skipped
(1 derived-scores-only, 1 not-item-response-data) -- no further action
needed on those two.

## 2026-08-03 -- PLOS ONE batch 18: 4-paper review (8 tables shipped, 1 skipped)

Reviewed 4 PLOS ONE papers flagged `good` by `irw_discover_plos.py` triage,
each already confirmed with a downloadable tabular SI file and CC BY 4.0
license on the article page (all 4 license statements individually
re-confirmed on the article page during this review, verbatim: "This is an
open access article distributed under the terms of the Creative Commons
Attribution License..."). For each, fetched the full article page (Methods,
Data Availability, full Supporting Information list, not just the file
triage flagged) before deciding.

- **Ordak (2026)**, "Statistical misreasoning in online content about
  vaccines" (DOI `10.1371/journal.pone.0355341`) -- **processed**. Only one
  SI file (S1 File, `.s001`): 597 anti-vaccination Facebook posts, each
  hand-coded 0/1 for presence of 10 statistical-misreasoning types
  (correlation-causation fallacy, base rate neglect, denominator neglect,
  cherry picking, relative-vs-absolute risk error, small sample fallacy,
  intuitive reasoning error, random fluctuation misinterpretation,
  overinterpretation of percentages, graphical scale misreading). No
  survey instrument -- the focal unit (`id`) is the post, not a person,
  same category as the previously-shipped dog-cognition table. Binary
  checklist-style coding fits the item-response shape cleanly: clean data,
  no NaN, no sentinel, N=597 posts x 10 items, `resp` 0/1.
  `data/ordak_2026_vaccine_misreasoning.py`.
- **Evans et al. (2023)**, "Outcomes of a social media campaign to promote
  COVID-19 vaccination in Nigeria" (DOI `10.1371/journal.pone.0290757`) --
  **processed, 2 tables**. Triage flagged S1 Dataset (`.s003`) as the
  tabular file, but the article also has an S2 File codebook (`.s002`,
  DOCX) that was essential to interpret the raw column names -- fetched
  and read it before writing the script. 3-wave RCT-style survey (baseline
  + 2 follow-ups) with `treat` (campaign vs. comparison state, derived
  from state but itself a raw group-assignment field, not a composite) and
  two distinct 5-item 1-5 Likert scales per wave: a vaccine-hesitancy index
  (benefit/everyone/safe/stress/unneces) and a pro-vaccination social-norms
  scale (close/family/friends/healthc/nigerian), split into 2 output files
  per the one-scale-per-file rule. Excluded as derived/aggregate: `fivec*`/
  `norms*` (row-mean composites, codebook marks with `*`), `vaxxed*`/
  `ltfu*` (derived binaries), and the single-item primary vaccination-status
  outcome (not a scale). Checked the paper's imputation language explicitly
  ("imput" appears 15x) -- confirmed it only describes downstream
  carry-forward and multiple-imputation-by-chained-equations robustness
  checks performed in Stata for analysis, not baked into the shared raw
  file; the wave-2/3 NaN counts match the reported attrition pattern
  exactly, confirming this is the pre-imputation raw file.
  `data/evans_2023_vaccine_hesitancy.py` (N=1933, 5 items, resp 1-5),
  `data/evans_2023_vaccination_norms.py` (N=1933, 5 items, resp 1-5).
- **Fragaszy et al. (2015)**, "'Vision for Action' in Young Children
  Aligning Multi-Featured Objects" (DOI `10.1371/journal.pone.0140033`) --
  **skipped, N too small**. Only SI file is S1 Table (`.s001`): downloaded
  and inspected -- confirmed genuinely trial-by-trial categorical/ordinal
  alignment scoring (success/failure per trial, clock-face alignment
  rubric per attempt, contact-angle categories), not raw kinematic/motion-
  capture data, so it would have been in-scope on content grounds (same
  reasoning that let the earlier dog-cognition dataset through). But the
  raw data has only 27 unique children (`Subject and trial` column parses
  to 27 distinct subject codes across 372 trial rows) -- well under the
  N>=50 floor, so skipped regardless of shape. No nonhuman primate raw
  data was in the SI file (the primate comparison in the paper draws on
  other published studies, not new data attached here).
- **Choy et al. (2022)**, "Career choice of tourism students in a
  triple-whammy crisis" (DOI `10.1371/journal.pone.0279411`) --
  **processed, 5 tables**. Only SI file (S1 Data, `.s001`) already had
  clean construct-prefixed item columns (Affect1-3, Extraneous1-4,
  Intent1-3, Lifelong1-3, Resilience1-4), 6-point Likert (1=Disagree
  strongly...6=Agree strongly per Methods), split into 5 files (one per
  construct) per the one-scale-per-file rule. Found and filtered a `-999`
  missing-value sentinel present on every item column (5-45 occurrences
  per item) -- numerically it sits far outside the 1-6 range so it's an
  unambiguous sentinel, not a borderline judgment call.
  `data/choy_2022_career_choice.py` writes all 5:
  `choy_2022_affect` (N=366, 3 items), `choy_2022_extraneous_events`
  (N=402, 4 items), `choy_2022_intent_career` (N=402, 3 items),
  `choy_2022_lifelong_career` (N=391, 3 items), `choy_2022_resilience`
  (N=402, 4 items); all resp 1-6.

**Output**: 8 tables across 3 papers -> `biblio_plos_batch18.csv` (8 rows),
staged for Redivis upload + dictionary paste. 1 paper skipped (N=27 < 50
floor) -- no further action needed on it.

## 2026-08-03: PLOS ONE 4-paper `good`-candidate review #2 (manual, ad hoc)

Four more PLOS ONE papers flagged `good` by `irw_discover_plos.py` were
reviewed by hand (fetched full article + SI file list per paper, not just
the triage-flagged file).

- **`10.1371/journal.pone.0245964`** (SME Blockchain-loan adoption,
  extended complexity theory) -- **processed**. Only one tabular SI file
  (`S1 Data.csv`, `.s002`; `.s001` is a DOCX appendix) -- exactly the one
  triage flagged. 5 constructs (perceived risk, reward sensitivity,
  perceived fairness, complexity, usage intention) x 3 items, 7-pt Likert,
  no covariates in the file. All 15 items clean integers 1-7, N=296.
  -> `sun_2021_blockchain_loan_adoption` (296 ids, 15 items, resp 1-7).
  `data/sun_2021_blockchain_loan_adoption.py`.
- **`10.1371/journal.pone.0182239`** (depression/anxiety/smartphone
  addiction in university students) -- **processed**, 3 tables from one
  raw file (`S1 Dataset.xls`, only SI file). SPAI-26 (4-pt Likert),
  PHQ-2 (0-3), GAD-2 (0-3) are three distinct instruments -> one file
  each per datastandard.md. Subscale/total columns
  (Compulsive_Behavior/Functional_Impairment/Withdrawal/Tolerance/
  TotAddiction_Score, Depression_score, Anxiety_score) excluded as
  composites. Missing values coded as literal string "." throughout
  (items and covariates) -- coerced to NaN and dropped.
  -> `matarboumosleh_2017_spai26` (683 ids, 26 items, resp 1-4),
  `matarboumosleh_2017_phq2` (416 ids, 2 items, resp 0-3),
  `matarboumosleh_2017_gad2` (417 ids, 2 items, resp 0-3).
  `data/matarboumosleh_2017_smartphone_depr_anx.py`.
- **`10.1371/journal.pone.0346696`** (GAI-assisted learning, human-AI
  collaboration) -- **processed**, 7 tables from one raw file (`S1
  File.xlsx`, only SI file; opaque `Q1..Q39` column names). The HTML
  article renders Table 2 ("Measurement Items and Sources") as an image,
  so the Q-number -> construct/item-code mapping was pulled from the PLOS
  full-text XML asset instead (`.../article/asset?id=...xml`), which has
  the table as real text: TTF=Q5-9, RA=Q10-14, SE=Q15-19, IS=Q20-24,
  Exploration=Q25-29, Exploitation=Q30-34, LE=Q35-39 (7 constructs x 5
  items, 7-pt Likert). Items renamed to their construct-prefixed codes
  (TTF1..TTF5 etc.) per Table 2 rather than left as raw Q-numbers.
  Q1/Q2/Q4 (identity, GAI-usage duration, academic field) and
  Q3_Choice1-5 (GAI-tool multi-select checkboxes) kept as covariates. All
  35 items clean integers 1-7, N=207. -> `zeng_2026_gai_ttf`,
  `_role_adapt`, `_self_efficacy`, `_inst_support`, `_exploration`,
  `_exploitation`, `_learning_effect` (207 ids, 5 items each, resp 1-7).
  `data/zeng_2026_gai_learning.py`.
- **`10.1371/journal.pone.0348206`** (WFH/hybrid workplace flexibility
  preferences during COVID-19) -- **skipped, not item-response data**.
  Triage flagged `S2 File.xlsx` (751 respondents, 335 columns); inspected
  the actual file plus `S1 File` (the DOCX survey instrument). The core
  measure is a best-worst-scaling discrete-choice experiment (14 choice
  tasks x 4 attribute-combinations, `Q3.2_1`..`Q3.15_4`) plus scattered
  multi-select checkboxes, categorical demographics, and several
  ambiguous free-text/derived columns (`hair`, `nail`, `summing`,
  `marking`) with no codebook resolving them cleanly. This is a choice
  experiment, not a rateable Likert item battery -- doesn't fit the
  standard long id/item/resp schema without extensive, uncertain
  codebook reverse-engineering (datastandard.md's "process data and
  trials" edge case: flag for human review rather than force-fitting).

All 4 articles confirmed CC BY 4.0 on the article page itself ("This is an
open access article distributed under the terms of the Creative Commons
Attribution License...").

**Output**: 11 tables across 3 papers -> `biblio_plos_batch_2026_08_03.csv`
(11 rows), staged for Redivis upload + dictionary paste. 1 paper skipped
(best-worst-scaling choice experiment, not Likert item data).

## 2026-08-03: PLOS ONE batch 18 — discovery, retriage, good-candidate review, and RData cleanup

**Discovery**: 30 English terms recycled from `search_terms_log.csv` (non-
PLOS rows not yet tried against PLOS, per the term-reuse method in
`SKILL.md`) run against PLOS ONE via `irw_discover_plos.py` ->
`plos_batch18_triage.csv` (1,998 candidates: 18 `good`, 337
`human_assistance`, rest `no_usable_file`/`not_item_response`/
`download_failed`/`error`/`timeout`).

**Pipeline bug found and fixed mid-run**: `irw_discover_plos.py`'s
`process_one_isolated()` called `pool.shutdown(wait=False,
cancel_futures=True)` *before* `_kill_pool_workers(pool)` on a
`FutureTimeoutError` — but `shutdown()` clears `pool._processes` to
`None`, so `_kill_pool_workers` then crashed with `AttributeError:
'NoneType' object has no attribute 'values'`. This propagated all the way
out of `main()`, silently killing the whole batch while the timed-out
worker was left running unsupervised (exactly the "abandoned worker"
failure mode the function's own docstring already warned about — the
fix for that just hadn't been ordered correctly). Fixed by reordering
(kill workers first, then shutdown) and defensively guarding against
`None` in `_kill_pool_workers`. Recovered by killing the stuck
process/orphaned worker and resuming with `--resume` (skipped the 168
candidates already captured before the crash).

**Retriage** (`irw_retriage_ha.py` on the 337 `human_assistance` rows):
116 `human_review` (-> `human_review_plos_batch18.csv`, staged for the
"Human eye" sheet), 99 `aggregate_continuous`, 65 `not_item_response`, 57
`worth_retrying` (not yet reviewed — see `TODO.md`).

**Good-candidate review**: of 18 `good` rows, 2 skipped pre-emptively for
N<50 (football-VR N=14, flicker-light N=24) without spending review time.
Remaining 16 papers split across 4 parallel background agents (4 papers
each), each independently reading the full article + all SI files (not
just the one triage flagged), verifying raw-vs-derived data, and writing
processing scripts per `datastandard.md`. Results: 12 papers processed ->
33 tables total; 4 skipped (2 aggregate/derived-only, 1 choice-experiment
structure out of schema scope, 1 N=27 after inspection). Per-paper detail
already in this log under "PLOS ONE 4-paper `good`-candidate review",
"PLOS ONE 4-paper `good`-candidate review #2", "PLOS ONE batch 18" (Ordak/
Evans/Choy), and the Nam/Jung/Shin/Yang group (Shin skipped for
aggregate-only data, the other 3 processed -> 10 tables, biblio rows
written directly to `biblio_plos_batch18_full.csv` since that group's
agent didn't stage its own file). All 4 groups' staging CSVs consolidated
into one `biblio_plos_batch18_full.csv` (33 rows) after verifying every
referenced `irw_output/*.csv` exists with the correct schema and N>=50;
the 4 individual per-group staging files were deleted once merged.

**RData cleanup (ben-domingue, 2026-08-03): stop writing `.RData` output
files in this pipeline, CSV only.** Redivis upload only ever consumes the
`.csv`; the parallel `pyreadr.write_rdata(...)` call that had crept into
~20 `data/*.py` scripts (inherited from `CLAUDE.md`'s general "both `.csv`
and `.RData`" convention for the main `data/` pipeline, which does not
apply to `automated_finding`) was dead weight. Stripped the RData-writing
code from all 20 affected scripts (including the 3 group-B/C/D scripts
just written this batch), deleted all `.RData` files already generated in
`irw_output/`, and added an explicit note to `datastandard.md`'s "Enforce
column order and save" section stating CSV-only overrides the general
convention for this pipeline specifically, so this doesn't recur.

**Output this pass**: 33 tables across 12 papers -> `biblio_plos_batch18_full.csv`,
staged for Redivis upload + dictionary paste. `human_review_plos_batch18.csv`
(116 rows) staged for the "Human eye" sheet. 57 `worth_retrying` rows still
need hand review (left open in `TODO.md`). 1 pipeline bug fixed
(`irw_discover_plos.py` timeout-handler crash). 1 standing convention
change (CSV-only output, codified in `datastandard.md`).

## 2026-08-04: PLOS ONE batch 18 worth_retrying review

Worked through the 57 `worth_retrying` rows left open from batch 18's retriage
(`plos_retriage_batch18.csv`), per the standing note in `TODO.md`.

**Triage before review**: checked all 57 DOIs against `BATCH_LOG.md`/`TODO.md`
for prior appearances first (search terms across PLOS batches keep
resurfacing the same articles). 7 were exact-DOI duplicates already
reviewed/struck in earlier batches — skipped without re-review:
`10.1371/journal.pone.0272095` (batch 10/13, Dutch self/other/meta-personality,
deferred as too complex, unrelated to this decision), `0168338` (batch 14,
struck for good, N=44), `0234997` (batch 10, all composite totals),
`0256001` (batch 10, T1-T4 composite columns), `0272987` (batch 9, all
composite scores), `0270464` (batch 9/10, composite-only), `0203336` (batch
9, BSI/FSB composite scores). 16 more had no resolved `n_participants`/
`n_items` from the automated triage pass — held out rather than reviewed
blind; left open in `TODO.md` with the DOI list for a follow-up pass.

**Review of the remaining 34**: split into 3 groups (~11-12 each) and
reviewed in parallel by 3 agents. Each agent fetched the full article page
+ ALL Supporting Information files (not just the first — `process_one()`'s
single-file inspection is exactly why these needed a second look) and
applied the standard checks: explicit CC0/CC-BY/CC-BY-SA confirmed on the
page, N>=50, no single-item scales, raw item-level responses vs.
pre-computed composite/subscale totals (the dominant reason for skips this
batch — see below).

**Processed (13 papers -> 17 tables, all CC BY 4.0)**:
- `zhou_2025_ehealth_literacy` (8i) / `_peer_relationship` (16i) — Chinese
  university students, N=14,892; composite id (region-group + within-group
  Number, since Number resets per group) since the raw Number column
  wasn't globally unique. `10.1371/journal.pone.0330637`
- `hayek_2022_attitude` (4i) / `_subj_norm` (3i) / `_self_efficacy` (5i) —
  Theory-of-Planned-Behaviour survey of Lebanese secondary students, N=345,
  -2..2 scale. `10.1371/journal.pone.0265595`
- `ribeiro_2024_msk_hq` (14i) — European Portuguese MSK-HQ, N=190, baseline
  (T0) only (T1 item-level responses weren't shared, only a T1 total).
  `10.1371/journal.pone.0308623`
- `stolz_2015_death_attitudes` (6i) / `_authoritarianism` (8i) — Austrian
  national euthanasia-attitudes survey, N=1958/1965; authoritarianism scale
  matches the paper's own S2 Table (alpha=0.79). `10.1371/journal.pone.0124320`
- `doustmohammadian_2017_fnlit` (58i) — Food and Nutrition Literacy scale,
  Iranian elementary schoolchildren, N=373, 10 sub-domains, 0-4 scale.
  `10.1371/journal.pone.0179196`
- `koo_2016_comm_technique_use` (12i) / `_opinion` (18i) — Maryland nurse
  practitioners' oral-health-literacy communication survey, N=212/211, 1-4
  scale, value 9 ("not applicable") filtered as sentinel.
  `10.1371/journal.pone.0146545`
- `mccarlie_2022_ortho_literacy` (11i) — binary orthodontic-literacy quiz,
  N=159 (paper's own abstract says 172; triage's N=58 estimate was simply
  wrong). `10.1371/journal.pone.0273328`
- `latifi_2026_insect_fear` (32i) — Insect Fear Questionnaire, Iranian
  schoolchildren, N=1369, 1-5 scale. `10.1371/journal.pone.0344126`
- `teodorini_2020_modafinil_attitudes` (8i) — attitudes toward modafinil for
  cognitive enhancement, N=284 of 345 total rows (168-column file, only
  Q10.1_1-8 was a genuine Likert battery, rest was drug-use
  history/checkboxes/free text). `10.1371/journal.pone.0227818`
- `duong_2025_tbl_experience` (19i) / `_confidence` (4i) — team-based-learning
  pre/post study, Vietnamese nursing students, N=186, mapped pre/post to
  `wave` 1/2; two other scale blocks in the same file (TBL-SAI, class
  engagement) not shipped — ambiguous raw-vs-recoded column pairs (e.g.
  `D4_Q` vs `D4`) couldn't be resolved without the original questionnaire.
  `10.1371/journal.pone.0323656`

**Skipped (21, dominant reason: SI file has only pre-computed composite/
subscale totals, not raw items)**: `0243958` (exam scores by course, not
item responses), `0267580` (incoherent single-item vaccination-intention
outcome), `0273579` (PHQ/GAD/ULS/DOCS/RFS totals only, CC0 but content
doesn't qualify), `0152457` (demographics/MMSE total only), `0222929`
(FSS/MADRS totals only), `0199605` (DASS/Rosenberg/SWEMWBS totals only),
`0323489` (PSQI total + actigraphy metrics only), `0241982` (composite
totals, one column explicitly mean-imputed), `0270427` (N=41, below
minimum, also weak battery), `0342247` (categorical
professional-practices survey, not ordinal item response), `0311248`
(physical-activity outcome measures, no Likert battery), `0267181` (ASD-MBQ
subscale/composite totals only), `0254953` (clinical t-scores/diagnostic
flags only), `0294593` (fractional composite/latent-variable SEM scores),
`0326825` (project-level matrices, not person-level), `0308973` (aggregate
observer/self totals only), `0200609` (mean/composite construct scores
only, codebook confirms), `0271030` (5-column aggregate subscale file),
`0154240` (rich multi-scale file but Spanish text-category responses need
verified official scoring keys not evident from the data alone — flagged
for dedicated future processing rather than shipped this pass), `0217482`
(mean/Z-score composites only), `0342678` (PROMIS T-scores + single-item
measures only), `0315442` (Delphi panel, N=panelists well under 50 by
design), `0136786` (EEG/P300 + composite neuropsych scores, physiological
not item-level), `0196718` (N=49, below minimum, and composite totals
only).

No license-blocked candidates this pass — every skip was content-driven;
all 34 reviewed articles carried an explicit CC BY 4.0 (or CC0) statement.

**Output this pass**: 17 tables across 13 papers ->
`biblio_batch18_worthretrying.csv`, staged for Redivis upload + dictionary
paste (open in `TODO.md`). 16 rows with unresolved n_participants/n_items
still need a manual look (open in `TODO.md` with the DOI list).
`plos_retriage_batch18.csv` deleted.

## 2026-08-04: PLOS ONE batch 18 nan-count review

Follow-up to the worth_retrying review above: the 16 rows whose automated
triage pass couldn't resolve a clean n_participants/n_items were held out
of that pass rather than guessed at. Reviewed all 16 directly this session
(fetched each article page, listed every SI file via `extract_si_files()`,
downloaded and manually inspected each tabular one — same standard checks:
explicit CC-BY/CC0 confirmed on page, N>=50, no single-item scales, raw
items vs. composite/aggregate totals). All 16 carried explicit CC BY 4.0.

**Processed (5 papers -> 14 tables)**:
- `jaracz_2017_temperament` (109i, binary) / `_job_stress` (8i, 0-5) —
  Polish nurses/civil servants, N=200 (of 258 raw rows; 58 rows with every
  scale column blank, no group label either, dropped as non-respondents).
  MBI_WE/MBI_DEP/MBI_ocena_wm/MBI_general composite columns excluded.
  `10.1371/journal.pone.0176698`
- `fan_2025_mbi_exhaustion` (9i) / `_accomplishment` (8i) /
  `_depersonalization` (5i) — full raw 22-item Maslach Burnout Inventory,
  split into its 3 standard subscales, resident physicians in China,
  N=636, 0-6 scale. `10.1371/journal.pone.0324707`
- `weatherspoon_2015_family_physicians_freq`/`_effectiveness` (17i each,
  N=69/55) and `_pediatricians_freq`/`_effectiveness` (17i each,
  N=194/158) — companion survey to the already-shipped
  `koo_2016_comm_technique_*` (same Horowitz/Kleinman research group,
  same 1-5-scale-with-9-sentinel instrument design, different professional
  populations). `10.1371/journal.pone.0119855`
- `kuczyk_2024_facemask_fba` (42i) / `_fbe` (27i) — expectations/
  experiences wearing face masks in German inpatient/day hospitals, N=142,
  5-pt agreement (SAV numeric-coded, no text mapping needed once read with
  `apply_value_formats=False`). `10.1371/journal.pone.0304140`
- `fukuda_2021_health_literacy` (46i) / `_info_reliability` (8i) /
  `_withholding_behavior` (6i) — Japanese educators' COVID-19 survey,
  N=994-1000, HLS-EU-Q47-style task-difficulty scale (item 39 missing from
  source) plus an information-source-trust scale and a binary
  activity-withholding scale, all in the same file. No id column in
  source; row index used. `10.1371/journal.pone.0257552`

**Skipped (11)**: `0277323` (systematic-review study-characteristics
table, not item response), `0339999` (CGSS extract of heterogeneous
single demographic/attitude items — gender, birth year, religion,
education, political trust — not a coherent multi-item scale),
`0257726` (PLOS SI file is only a stimulus-image catalog; real response
data is at Mendeley Data `10.17632/68mkyrb4n3.1`, not chased this pass —
logged as a lead in `TODO.md`), `0229772` (clinical/lab dataset — dosing,
staging, lab values — not item-response), `0189592` (N=30, below minimum,
also a header-offset file not worth fixing at that N), `0299537` (N=35,
below minimum), `0299736` (N=18, below minimum, and the one scale column
present is an aggregate score anyway), `0276734` (PLOS SI file is only a
descriptive-statistics summary table; real database is at GitHub/Zenodo
`10.5281/zenodo.6793420`, not chased this pass — logged as a lead),
`0269201` (idep./ddep. columns are binary multi-select checkbox flags,
not an ordinal scale), `0345874` (categorical vignette-choice data,
N~3 coaches, far below minimum), `0259364` (N=22, below minimum).

No license-blocked candidates — every skip was content- or N-driven.

**Output this pass**: 14 tables across 5 papers ->
`biblio_batch18_nancount.csv`, staged for Redivis upload + dictionary
paste (open in `TODO.md`). 2 external-repo leads (Mendeley, Zenodo) not
yet chased, logged in `TODO.md` for the regular repo-based pipeline.

## PLOS ONE batch 19 (2026-08-04)

**Discovery**: 30 terms recycled from `search_terms_log.csv` (non-PLOS,
English-only, not yet tried on PLOS ONE, per the SKILL.md term-reuse
method) — self-efficacy, sleep quality, empathy, attachment, life
satisfaction, big five, occupational stress, job stress, coping,
self-concept, positive and negative affect, parenting style, alcohol use
disorder, eating attitudes, academic self-efficacy, procrastination,
flourishing, subjective wellbeing, ethnic identity, job satisfaction,
burnout, suicidal ideation, transformational leadership, employee
engagement, social media addiction, nomophobia, marital satisfaction,
romantic jealousy, child temperament, moral injury. 2,657 candidates ->
26 `good` + 507 `human_assistance` + rest `no_usable_file`/`error`/etc.
One `crashed` row (a corrupt `.sav`) correctly isolated by the per-worker
crash handling, batch continued normally.

**Retriage** (`irw_retriage_ha.py` on the 507 `human_assistance` rows):
148 `human_review`, 134 `aggregate_continuous`, 128 `not_item_response`,
95 `worth_retrying`, 2 `recoverable_format`.

**Good-candidate review**: 26 `good` rows split by N — 5 below the N=50
floor skipped outright without review (a dental lab bond-strength study
N=7, two N<25 lab studies, a Ghanaian pediatric-pain-instrument
content-validity study N=13, a Kawaii-emotions study N=42). The remaining
21 (N>=50) were split into 3 groups of 7 and reviewed in parallel by 3
agents (fetch full article page + every SI file, not just the one the
automated triage grabbed; verify license/N/raw-vs-composite per the
standard checks).

Result: **16 papers -> 51 tables**, all CC BY 4.0:
- `malinowska_2021_saq_physicians`/`_nurses` (41i each) — Polish Safety
  Attitudes Questionnaire, N=738/1190. `10.1371/journal.pone.0260926`
- `lunacortes_2019_satisfaction`/`_self_congruity`/`_social_value`/
  `_isncc`/`_interperson_conn`/`_isnbi` (6 tables, N=444) — Gen-Y tourist
  virtual-social-network survey, Spain. `10.1371/journal.pone.0217758`
- `martinezsoto_2024_spiritual_leadership` (26i, N=299) — Colombian
  Adventist teachers, Fry's spiritual leadership model.
  `10.1371/journal.pone.0299671`
- `zhao_2025_nat_env_perception`/`_leisure_involvement`/
  `_place_attachment`/`_restor_env_perception`/`_psych_recovery_eval` (5
  tables, N=199) — Changsha urban forest park survey.
  `10.1371/journal.pone.0325755`
- `saputra_2023_system_quality`/`_info_quality`/`_perceived_ease_of_use`/
  `_perceived_usefulness`/`_job_performance` (5 tables, N=118) —
  information-system job-performance survey.
  `10.1371/journal.pone.0285293`
- `cooper_2018_offensive_topics`/`_funny_topics` (34i each, N=1637) —
  instructor humor gender-perception study.
  `10.1371/journal.pone.0201258`
- `liu_2023_brand_trust`/`_attitude`/`_subjective_norm`/
  `_perceived_control`/`_purchase_intention`/`_purchase_behavior` (6
  tables, N=544) — agricultural regional-brand consumer study.
  `10.1371/journal.pone.0295133`
- `thanh_2025_attitude`/`_perceived_control`/`_green_behavior`/
  `_green_knowledge`/`_environ_concern` (5 tables, N=407) — employee
  green-behavior survey. `10.1371/journal.pone.0320053`
- `zhang_2025_coercive_pressure`/`_normative_pressure`/
  `_environ_awareness`/`_self_efficacy`/`_green_supply_intent` (5 tables,
  N=292) — Chinese manufacturing green-supply-chain study.
  `10.1371/journal.pone.0322200`
- `salleh_2023_aim_iam_fim` (12i, N=170) — Malay AIM-IAM-FIM
  implementation-outcome scale; the paper's claimed n=235 CFA sample
  turned out to be byte-identical to the n=170 EFA sample across all 4
  candidate source URLs (2 PLOS SI files + 2 Dataverse DOIs) — only the
  one real dataset shipped. `10.1371/journal.pone.0294238`
- `ahmed_2019_wellbeing` (4i, ONS4-style) / `_food_consumption` (14i, FCS)
  — Ghana sugarcane/oil-palm/jatropha wellbeing survey, N=850.
  `10.1371/journal.pone.0215433`
- `fisher_2019_belonging`/`_structure`/`_preparedness` (2i each, N varies
  353-466) — underrepresented-minority/women PhD STEM survey.
  `10.1371/journal.pone.0209279`
- `karpudewan_2022_stp_efa` (33i, N=300) / `_stp_cca` (29i, N=397) —
  Malaysian STEM-teaching-practices instrument, 2 independent validation
  samples. `10.1371/journal.pone.0268509`
- `jiang_2025_sacie`/`_teaching_motivation`/`_inclusive_efficacy`/
  `_empathy` (4 tables, N=240) — pre-service teacher empathy/inclusive
  education. `10.1371/journal.pone.0321066`
- `dahlstrom_2022_scoare` (20 constructs, retrospective pre/post -> wave,
  N=159) — research-mentor workshop evaluation.
  `10.1371/journal.pone.0262418`
- `gesbert_2021_tdeq` (25i, N=64) — Talent Development Environment
  Questionnaire, Swiss elite youth soccer players; N=64 falls in the
  50-99 borderline band, shipped per ben-domingue's explicit approval
  (2026-08-04) since the data was otherwise clean/genuinely raw.
  `10.1371/journal.pone.0246823`

**Skipped (10)**: `0287795` (each column is a distinct demographic/identity
indicator, not repeated items of one instrument), `0201698` (only a
composite PA score + dichotomized indicators), `0295904` (only
derived/grouped covariates, real CD-RISC raw items never actually shared
despite being described in the paper), `0249033` (composite subscale
totals at 3 timepoints only), `0254795` (composite wellbeing index +
unrelated single-item covariates only) — all false positives on the
automated `good` flag, confirming the standing "good needs a human glance"
caution. Plus the 5 N<50 rows skipped pre-review (dental lab study N=7,
two lab studies N=10/24, pediatric-pain content-validity study N=13,
Kawaii-emotions study N=42).

No license-blocked candidates — all 26 `good` rows carried explicit CC BY
4.0.

**Output this pass**: 51 tables across 16 papers ->
`biblio_batch19_good.csv`, staged for Redivis upload + dictionary paste
(open in `TODO.md`). `human_review_plos_batch19.csv` (148 rows) staged for
the "Human eye" sheet (open in `TODO.md`). 95 `worth_retrying` rows not
yet hand-reviewed (open in `TODO.md`, same pattern as batch 18).

## PLOS ONE batch 19 — worth_retrying review (2026-08-09)

Reviewed `plos_retriage_batch19.csv`'s 95 `worth_retrying` rows. **38 were
duplicate DOIs already reviewed and decided (all skips) in earlier
batches** (0199605, 0135377, 0150312, 0194569, 0323489, 0230103, 0197276,
0256983, 0122311, 0280919, 0200129, 0277516, 0269012, 0258606, 0278201,
0338521, 0345874, 0294593, 0262465, 0277323, 0212914, 0343308, 0321373,
0217482, 0270464, 0200609, 0272095, 0272987, 0292302, 0322635, 0305567,
0224159, 0234997, 0288386, 0252329, 0268773, 0315442, 0171186, 0223482 —
same "search terms keep resurfacing the same PLOS articles" pattern noted
in batch 18's review) — not re-reviewed, since their content-driven skip
reasons (composite/aggregate-only, N<50, not-item-response, etc.) don't
change on a resurface.

**56 genuinely new DOIs** split into 3 groups of ~19 and reviewed in
parallel by 3 agents (each fetching the full article page + ALL Supporting
Information files, verifying CC BY license, N>=50, item-level-not-composite
structure per the standard checks).

Result: **23 papers -> 70 tables**, all CC BY 4.0:
- `malik_2018_individual_motivation`/`_organizational_motivation`/
  `_social_motivation` (22i/36i/14i, N=360) — physician motivation tool,
  Lahore, Pakistan. `10.1371/journal.pone.0209546`
- `sinche_2017_skill_development`/`_skill_importance` (15i each, N=7278/3820)
  — PhD transferable-skills evaluation. `10.1371/journal.pone.0185023`
- `sugiura_2015_disaster_characteristics` (40i, N=1407) — personal
  characteristics of 2011 Great East Japan Earthquake survivors.
  `10.1371/journal.pone.0130349`
- `ali_2021_phq9`/`_gad7`/`_isi`/`_iesr`/`_spfi` (9i/7i/7i/22i/16i, N~165-170)
  — COVID-19 nurses wellbeing, Kenya; text-category responses re-coded
  ordinally via keyword rank functions. `10.1371/journal.pone.0254074`
- `okamura_2018_eol_attitude`/`_burnout` (6i/17i, N=261) — end-of-life-care
  attitude/burnout, Japan. `10.1371/journal.pone.0202277`
- `batistafoguet_2021_mlq` (45i, N=300) — Multifactor Leadership
  Questionnaire, Prolific/US sample only (Catalan Police sample was DOCX
  documentation, not tabular). `10.1371/journal.pone.0254329`
- `vonhippel_2023_fsfi` (21i, N=428) — Female Sexual Function Index items
  extracted from an otherwise qualitative/demographic breast-cancer
  survivorship survey CSV. `10.1371/journal.pone.0293298`
- `yang_2023_green_brand_image`/`_perceived_value`/`_consumption_intent`
  (12i/3i/4i, N=341) — green agricultural-brand consumer study, China.
  `10.1371/journal.pone.0292633`
- `butt_2022_user_satisfaction`/`_task_tech_fit`/`_performance_impact`/
  `_cognitive_absorption`/`_actual_usage`/`_institutional_factors` (6
  tables, N=404) — online-learning cognitive-absorption study.
  `10.1371/journal.pone.0269609`
- `petrowski_2019_tics` (57i, N=2463) — Trier Inventory for Chronic Stress
  short version, German sample. `10.1371/journal.pone.0222277`
- `lai_2023_social_adaptability`/`_parent_relation_father`/
  `_parent_relation_mother`/`_teacher_student_rel`/`_peer_relationship` (5
  tables, N~1322-1324) — AI-in-education adolescent social-adaptability
  study. `10.1371/journal.pone.0283170`
- `campos_2023_oes`/`_pidaq`/`_swls` (7i/24i/5i, N=7593) — aesthetic dental
  treatment/orofacial appearance/life satisfaction, Finland/Brazil.
  `10.1371/journal.pone.0287235`
- `dussel_2022_pcl17`/`_hads14` (17i/14i, N=780) — psychological symptoms
  in French hospital workers during COVID-19 first wave.
  `10.1371/journal.pone.0267032`
- `forycka_2022_mbi_gss`/`_mswbi`/`_rs14` (16i/7i/14i, N~1075-1395) —
  Polish medical students resilience/wellbeing/burnout, COVID-19 era.
  `10.1371/journal.pone.0261652`
- `direkvand_2022_mjsi` (25i, N=121) — Iranian midwives job-satisfaction
  instrument. `10.1371/journal.pone.0262665`
- `decamp_2022_online_discussion` (12i, N=117) — online teaching-practices
  self-report instrument. `10.1371/journal.pone.0275880`
- `petrowski_2020_attachment` (12i, N=2381) — ECR-based attachment scale,
  1-7. `10.1371/journal.pone.0230864`
- `pierro_2018_selfforgive_s1`/`_s2`/`_s3`, `_locomotion_s1`/`_s3`/`_s4`,
  `_assessment_s1`/`_s3`/`_s4`, `_posaffect_s3`, `_negaffect_s3`,
  `_tf_past`/`_present`/`_future_s4`, `_hfs_s4` (15 tables across 4 studies,
  N=85-323 per study) — self-forgiveness/regulatory-mode study.
  `10.1371/journal.pone.0193357`
- `konerding_2019_patientsatisfaction` (7i, N=1884) — short SERVQUAL-based
  patient-satisfaction scale, 6 European countries.
  `10.1371/journal.pone.0197924`
- `jo_2023_sni`/`_sno`/`_pbc`/`_arp`/`_crp`/`_cfs` (6 tables, N=345) —
  social-networking-intensity/isolation-risk study, university students.
  `10.1371/journal.pone.0283997`
- `girma_2021_phq9`/`_oslo3` (9i/3i, N=546) — depression among pregnant
  women, Jimma, Ethiopia. `10.1371/journal.pone.0250927`
- `reyes_2022_eheals` (8i, N=528) — eHealth Literacy Scale, undergraduates.
  `10.1371/journal.pone.0266802`
- `pedroso_2021_ifsq_laissezfaire`/`_pressuring`/`_restriction`/
  `_responsiveness` (11i/17i/11i/12i, N=465) — Infant Feeding Style
  Questionnaire, cross-cultural adaptation, Brazil.
  `10.1371/journal.pone.0257991`

**Skipped (23)**: `0276794` (aggregate subscale composites only, not raw
items), `0310193` (single-item happiness measure only), `0338906`
(third-party AAMC data, not authorized for public sharing), `0187367`
(self-report vs. actual grades, not a psychometric instrument), `0258484`
(data explicitly not shareable), `0343275` (technical energy-grid data,
not survey), `0255746` (claimed EPDS/DASS-21/PSQI/PSS items not actually
in the SI file, only demographics/binary outcomes), `0173768` (N=26),
`0227877` (real data hosted at figshare, not the PLOS SI — external lead,
not chased), `0339591` (composite-only wave totals, not raw MSES/ESSS/
GAD-7 items), `0314338` (ambiguous Chinese-labeled construct-to-column
mapping, item count mismatch vs. paper text — flagged for human review
rather than guessed), `0296290` (dairy-cow microbiome data, not item
response), `0312010` (ambiguous interleaved demographic/item columns,
inconsistent per-item coding schemes — flagged for human review),
`0319473` (scoping review, not primary data), `0312750` (categorical
yes/no eating-behavior items, not an ordinal scale), `0202230` (rat
lever-press behavioral data, not survey items), `0217595` (SI file has
only covariates, no item-level AUDIT-C data despite Data Availability
claim), `0160805` (subscale/total scores only, no raw items), `0294896`
(genomic/SNP cohort data, not psychometric items), `0279871` (N=41),
`0161076` (ecology/plant-parasite paper, not human item response),
`0203689` (composite subscale averages only, no raw CFPQ items), `0242326`
(aggregate correlation/regression tables only, no raw items).

**Deferred, N in the 50-99 borderline band (10, structurally clean but
below the usual N>=100 comfort zone)**: `0192774` (N=83, cataract
surgery wellbeing), `0201641` (N=82, HIV posttraumatic growth), `0346872`
(N=62, bipolar affect/impulsivity), `0233412` (N=81, dezocine
depression), `0224254` (N=54, EI training), `0218017` (N=80, music/affect
regulation), `0180041` (N=64, choice-induced preference/depression),
`0241041` (N=53, Tactile Biography questionnaire), `0150375` (N=58, heart
rate/attachment), `0151747` (N=60, heart rate variability/attachment).
**ben-domingue decision (2026-08-09): skip all 10** rather than ship —
below the comfort threshold despite being clean.

No license-blocked candidates — all 23 shipped papers carried explicit
CC BY 4.0.

**Output this pass**: 70 tables across 23 papers ->
`biblio_batch19_worthretrying.csv`, staged for Redivis upload + dictionary
paste (open in `TODO.md`). This closes out batch 19's `worth_retrying`
backlog end-to-end; `plos_retriage_batch19.csv` deleted.

### QC spot-check pass on batch 19 worth_retrying output (2026-08-09)

ben-domingue spot-checked per-item `resp` distributions across the 70
newly-shipped tables and flagged 6 suspicious patterns before upload. Two
turned out to be real bugs, three were genuine scale-range mismatches
against the source paper's documented Methods text, and two were false
alarms (data confirmed genuine on inspection):

- **`ali_2021_spfi`** (real bug): the freq-family value map had a text
  typo -- `"A little bit"` where the raw file's actual category text is
  `"Very Little"` -- so every genuine "Very Little" response silently
  mapped to NaN and was dropped, which is why `resp=1` never appeared in
  items 7-16. Fixed the map to match the raw text exactly (also
  tightened the true-family map to a contiguous 0-4 code, dropping an
  unused "Very Little" key that never matched anything in that family).
  Re-shipped with `resp` 0-4 for both families (was 0-5/0-4 with a gap).
- **`reyes_2022_eheals`** (real bug): row 0 of the source CSV is a
  Qualtrics codebook "Key: 1 = ..." row, not a respondent. The
  digit-extraction regex pulled a stray "1" out of that key text for
  every item and shipped a fake `id=1` respondent (resp=1 on all 8
  items, garbled `cov_*` values containing the raw key text itself). Now
  dropped before processing; N corrected 528 -> 527.
- **`lai_2023_parent_relation_father`/`_mother`** (scale-range fix):
  shipped as 1-6, but the paper's Methods text (confirmed via WebFetch)
  documents an 18-item, 5-point (1-5) Parent-Child Relationship scale.
  `FUQIN1` alone had 62/1319 responses of 6 while its mother-report
  counterpart `MUQIN1` had zero -- inconsistent with a genuine shared 1-6
  scale for that item -- so capped to 1-5 (all other stray 6s across both
  blocks were isolated single-row artifacts anyway). Also noted: the raw
  file has 20 FUQIN/MUQIN columns vs. the paper's stated 18 items; which
  2 are extra/non-scale is unresolved without the actual codebook, so all
  20 are still shipped as-is.
- **`lai_2023_teacher_student_rel`** (scale-range fix): shipped as 0-6,
  but the paper documents 7 items on a 5-point (1-5) scale; the 0s/6s
  were isolated single-row artifacts. Capped to 1-5.
- **`lai_2023_peer_relationship`** (scale-range fix): shipped as 0-6, but
  the paper documents 18 items on a 6-point (1-6) scale (6 is a genuine,
  common response, unlike the father/mother scale above). The 0s were
  isolated single-row artifacts on 3 items. Floor corrected to 1.
- **`pierro_2018_tf_future_s4`** (false alarm, no change): `resp=1` never
  appears on any of the 4 future-focus items. Checked the raw SPSS file
  directly -- genuinely no `1.0` values in the source data (N=189); past-
  and present-focus items in the same study do have a couple of 1s, so
  this reads as real (if skewed) respondent behavior on the future-focus
  items specifically, not a coding/label mismatch.
- **`vonhippel_2023_fsfi`** (false alarm, no change): `resp=6` appears
  only 4 times, exclusively on `fsfi_19`. Confirmed the source's own
  category text for that item explicitly includes "more than once per
  day" as a 6th response option beyond the other items' 0-5 range --
  genuine, not an artifact of the rank-coding function.

All 5 affected scripts (`ali_2021_covid_nurses_wellbeing.py`,
`lai_2023_social_adaptability.py`'s 4 relationship-scale outputs,
`reyes_2022_eheals.py`) re-run and re-verified; `irw_output/*.csv`
regenerated and `biblio_batch19_worthretrying.csv`'s Notes column updated
per-table with the fix. No table's N or item count changed except
`reyes_2022_eheals` (528 -> 527, the fake key-row respondent removed).

## PLOS ONE batch 20 (2026-08-10)

Discovery run with 30 recycled search terms pulled from the non-PLOS pool
in `search_terms_log.csv` (per `SKILL.md`'s term-recycling guidance —
~1,016 candidates were available; picked 30 clean instrument/construct/
task names spanning cognitive tasks, clinical/psychopathology constructs,
and org-behavior constructs): executive function, numerical cognition,
response style, reaction time, attentional control, cognitive flexibility,
temporal discounting, risk perception, probabilistic reversal learning,
dyslexia, alexithymia, schizotypy, interoceptive awareness, self-harm,
non-suicidal self-injury, intolerance of uncertainty, need for closure,
humor styles, boredom proneness, system justification, just world belief,
moral foundations, stereotype threat, academic dishonesty, compulsive
buying, doomscrolling, technoference, abusive supervision, perceived
organizational support, entrepreneurial intention.

2,478 candidates -> 17 `good` + 355 `human_assistance` + 2,015
`no_usable_file` + 53 `not_item_response` + 27 `download_failed` + 11
`error`. Retriage (`irw_retriage_ha.py`) on the `human_assistance` bucket:
52 `worth_retrying`, 116 `human_review`, 129 `aggregate_continuous`, 58
`not_item_response`.

**`good`-candidate review**: 3 of 17 dropped pre-review for N<50
(archerfish symbol-value task N=12, non-human; eye-contact-perception task
N=22; cerebral-palsy eye-tracking-vocabulary study N=40). Remaining 14
reviewed in 2 parallel passes (fetch full article + all SI files, verify
license/raw-vs-composite/item structure). Result: **10 papers processed
-> 10 tables**, all CC BY 4.0:
- `abukhalaf_2025_housing_risk`/`_disaster_prep` (10.1371/journal.pone.0310665,
  N=816): hurricane risk-perception + preparedness-intention items.
  Shipped as **continuous 0-1 resp**, not discretized to 1-5 -- the
  paper's own Methods text (Sec 3.3) states responses use a "Likert or
  Rising scales format" translated to a continuous 0.0-1.0 metric, and the
  raw file has genuine non-anchor decimal values confirming this.
- `zvi_2022_harassment_perception`/`_rei`/`_legal_judgment`
  (10.1371/journal.pone.0272606, N=211, lawyers + law students): 3
  distinct scales in one SI file (11-item vignette perception 1-5, 24-item
  Rational-Experiential Inventory 1-5, 27-item legal-judgment ratings 1-7)
  -> 3 tables per the "multiple scales in one file" rule.
- `kitayama_2022_hweat`/`_hweat_retest` (10.1371/journal.pone.0268124):
  18-item Japanese Healthy Work Environment Assessment Tool, 1-5 Likert.
  Main validation sample (S2 Data, N=202) and a separate test-retest
  sample (S1 Data, N=50, 2 waves) shipped as 2 tables -- correct SI file
  indices confirmed by reading the article's Supporting Information list
  text directly (S1 Data = .s003, S2 Data = .s004; .s001/.s002 are
  unrelated DOCX supplements).
- `xiao_2026_entrepreneurial_intention` (10.1371/journal.pone.0352807,
  N=1389): 40-item, 7-construct entrepreneurship survey, 1-5 Likert.
  2 extra column blocks (IC1-7, CS1-11, 18 cols) excluded -- absent from
  the paper's own Variable Codebook sheet, construct undocumented.
- `iqbal_2022_curriculum_skills` (10.1371/journal.pone.0265880, N=482):
  38-item, 6-construct curriculum-delivery/entrepreneurial-skills survey,
  1-7 Likert. 3 isolated single-cell outliers (CM3=23, CM5=32, ICT2=32)
  dropped as data-entry errors.
- `ritzel_2020_farmer_burden` (10.1371/journal.pone.0241075, N=801): 13-item
  administrative-burden/compliance-cost/psychological-cost/knowledge
  survey, response range genuinely varies by sub-battery (1-4 to 1-8). No
  person-ID column in the source file -- row index used as id.

4 of 14 skipped: penalty-kicking task (10.1371/journal.pone.0135423,
per-participant aggregated percentages, not raw trial data), freeway-rain
driving-risk study (10.1371/journal.pone.0149442, single-item ordinal
outcome), Spanish-children affect study (10.1371/journal.pone.0201698,
composite/dichotomized subscale scores only), Berlin PrEP study
(10.1371/journal.pone.0260168, heterogeneous single items with mixed
response scales, no coherent instrument). 3 more skipped from group B:
caste/labor-market self-confidence study (10.1371/journal.pone.0327299,
single-item belief question, rest is task performance/demographics),
concealable-stigmatized-identities study (10.1371/journal.pone.0287795,
heterogeneous identity-classification questions, no uniform response
scale), college-employment-willingness study (10.1371/journal.pone.0278164,
N=12,897 but categorical/free-text/checkbox mix, not a Likert scale).

**One `good` candidate caught and struck after deeper inspection**:
Japanese-schoolteachers radiation-risk-perception study
(10.1371/journal.pone.0212917, N=550, 21 items) -- the paper's Methods
text describes a uniform 1-4 response scale ("1) Yes, 2) Probably, 3)
Probably not, 4) No") for all 21 items, but the actual SI data (correct
file, .s003, confirmed by reading the article's SI list) shows 19 of 21
items using only codes {1,2}, one using {2,3}, and one using {4,5} -- a
per-item code-shift pattern inconsistent with a single coherent 4-point
scale answered by 550 people (implausible that ~90% of items got zero
"probably not"/"no" responses). Reads as heterogeneous single-choice
items with their own codebooks rather than the described psychometric
scale. Not shipped; not re-flagged for human_review since the underlying
ambiguity (mismatch between paper text and file) needs the actual
questionnaire/codebook, not just another automated pass.

`worth_retrying` (52 rows) and `human_review` (116 rows,
`human_review_plos_batch20.csv`) not yet reviewed/pasted this session --
open items, see `TODO.md`. `plos_batch20_triage.csv` and
`plos_retriage_batch20.csv` retained until both are closed out.

### QC catch on batch 20 output (2026-08-10)

ben-domingue asked whether the fractional values in
`abukhalaf_2025_housing_risk`/`_disaster_prep` were valid or imputed.
Checked: each item column had a small number of cells (4-12 out of 816)
holding a single repeated non-anchor decimal shared across several
*different* respondents (e.g. 7 different ids all =0.4199 on
`risk1_flood`; 9 different ids all =0.5708 on `risk1_wind_damage`) rather
than distinct per-respondent values -- a true continuous slider would not
produce the exact same decimal across unrelated people. No imputation
language found in the paper's text, but the pattern is unambiguous mean/
constant imputation for missing responses. Fixed `abukhalaf_2025_housing_risk.py`
to snap resp to 4 decimal places and keep only the genuine anchor values
(0/.25/.5/.75/1 for the 13 risk items, 0/.1/.../.9/1.0 for the 3
preparedness items), dropping 90 imputed cells from housing_risk and 4
from disaster_prep. Also corrected the biblio Description/Notes fields
(previously described as "continuous 0-1", now correctly described as a
discrete 5-point/11-point anchor scale) and re-verified zero non-anchor
values remain in either output file.

### PLOS ONE batch 20 worth_retrying — group 1 review (2026-08-10)

Reviewed 17 of the 52 `worth_retrying` rows (first group of a 3-way split
of `plos_retriage_batch20.csv`'s pool). For every candidate, fetched the
full article page and downloaded every SI file that looked tabular (not
just the one file `irw_discover_plos.py`'s triage happened to pick),
per SKILL.md's "needs a human glance more than usual" note.

**3 papers -> 6 tables shipped**, all CC BY 4.0, all N>=105:
- `wiedemann_2021_risk_perception`/`_text_readability`
  (10.1371/journal.pone.0253762, N=344): a single German-language SPSS
  file (`.s007`, no SI caption -- identified as the raw data file via its
  SPSS variable labels, since the other 6 SI files are PDF questionnaire/
  vignette text) holds 2 distinct instrument blocks, F01-F06 (risk-
  communication perception, 5 items) and F11-F16 (semantic-differential
  text-readability rating, 6 items), both 7-point -- split per the
  "multiple scales in one file" rule.
- `monier_2026_sti`/`_pot` (10.1371/journal.pone.0352176, N=105-107):
  single XLSX SI file (header on row 2, banner row above), 2 scales --
  10-item French Self-Transcendence Inventory and a 7-item Passage-of-
  Time-judgment battery (subjective speed of time passing at 7 different
  time referents, consistent "_7vite" column suffix). Source `ID` resets
  within each of the 2 diagnostic groups (Parkinson's/control), so
  `id` = group + ID (composite, verified unique) instead. 16 fully-blank
  trailing rows (no group, no item data -- a sheet-extension artifact)
  dropped before building `id`. One isolated out-of-range value
  (STI1=8 on an otherwise 1-7 scale, single occurrence) dropped as a
  data-entry error.
- `schmidt_2017_pds`/`_fas` (10.1371/journal.pone.0182845, N=232/236):
  single SPSS file (`pd.read_spss` needed `convert_categoricals=False`
  -- default returns German value-label text instead of numeric codes,
  caught before shipping). Most of the file is composite indices/task-
  performance scores, but 2 short raw-item instruments survive: German
  Pubertal Development Scale (3 items, 1-4) and Family Affluence Scale II
  (4 items, response range genuinely varies 0-2/0-3 by item per the
  paper's Methods). No person-ID column -- row index used as `id`. One
  isolated fractional value dropped per table (pub_2_1=2.5, ses_3_1=1.5)
  as data-entry errors.

**11 of 14 remaining candidates skipped** -- all had a Data Availability
statement pointing to genuine SI files, but none held raw item-level
psychometric data on inspection:
- `0117947` (theory of mind/sharing preschoolers): file holds only
  composite task-outcome variables (accuracy/RT scores), no Likert items.
- `0121651` (ADHD EF training RCT): file holds only derived task/subscale
  totals (SSRT, Stroop interference scores, CBTT/Raven norm scores,
  VVGK subscale sums) -- no raw item responses.
- `0139930` (abacus training, math/task-switching): file holds only
  composite RT/accuracy scores, several already Z-standardized.
- `0154145` (facial affect labeling, schizophrenia/BPD): file holds only
  per-condition aggregate accuracy/error rates (e.g. `f_a_100`, `f_a_ratio`),
  not raw per-trial labeling responses.
- `0164382` (psychological distance, children's future preferences): file
  holds only composite task scores (drink/TV/game sub-scores, similarity-
  task totals), not Likert items.
- `0192837` (napping/CBM-Appraisal PTSD-analogue training): the file's
  `mood1`-`mood5` columns don't match the paper's own description (Methods
  states a 0-10 Likert mood scale; raw values range up to 62) -- mismatch
  between described instrument and actual data, same pattern that struck
  the batch-20 radiation-risk-perception `good` candidate. Rest of file is
  pre-summed clinical totals (`sum_BDI`, `sum_PTCI*`, `sum_IES`, etc).
- `0195239` (autistic traits/social anxiety, 2 studies): both SI files
  hold only composite task-condition accuracy scores plus SPAI/AQ totals
  -- no raw items.
- `0212482` (physical-activity breaks, EF/academic achievement): file
  holds only composite/index/t-score columns, no raw items.
- `0220658` (trust/proximity/vaccine propensity): file has only 4-5
  heterogeneous single-item covariates (trust, 2 risk-likelihood
  questions, news consumption, vaccine belief) -- no coherent multi-item
  instrument, same "heterogeneous single items" pattern as the Berlin
  PrEP skip in the earlier good-candidate pass.
- `0270464` (staff burnout/child behavior, 2-yr longitudinal): paper's
  Methods confirms the Chinese CBCL has 112 raw items, but the shared file
  only contains `Int_1`-`Int_12`/`Ext_1`-`Ext_12`/`Total_1`-`Total_12` --
  these are subscale-total scores *per wave* (up to 12 waves, matching
  `no_waves`), not per-item raw responses.
- `0288386` (EF/psychopathology dimensional models): file has only 6
  columns, all composite task/dimension scores (Stroop/TMT/ToL + BASC
  dimension totals), no raw items.
- `0346872` (bipolar affect/impulsivity): all 3 SI files inspected --
  S1 Data is sociodemographic/clinical-scale *totals* only (BIS
  total+subscales, MADRS, YMRS, PANAS total/positive/negative), S2/S3
  Data are mediation-analysis regression-coefficient tables, not raw
  data. No raw item-level data anywhere in this paper's SI.

**1 skipped for data-provenance concern, not a content problem**:
`0331030` (seborrheic dermatitis, anxiety/personality/QoL) structurally
had 2 real raw-item scales (21-item Beck Anxiety Inventory, 0-3; a
7-item Bortner-personality-labeled block, 1-8) with clean per-item
distributions -- but the paper's own abstract states the study was
conducted on "210 adult South Dakota patients" while every author is
affiliated with a hospital in Ankara, Turkey, and the SI file's only
person-identifier column ("ad soyad" = "name surname") is non-unique
(duplicated across rows with different ages/genders, i.e. not a real
per-person id despite the label). Both signals independently suggest the
paper text and/or SI file may not be reliably authored/curated -- not
shipped; not re-flagged for human_review since the issue is
authenticity/provenance, not something a closer read of the Methods
would resolve.

Output: `biblio_batch20_wr_group1.csv` (6 rows), 6 files in
`irw_output/`. Groups 2 and 3 of the 52-row `worth_retrying` pool were
handled separately in parallel (see `biblio_batch20_wr_group2.csv` if
present) -- `plos_retriage_batch20.csv` retained until all groups close
out.

### PLOS ONE batch 20 worth_retrying — group 2 review (2026-08-10)

Reviewed 16 of the 52 rows (second group of the 3-way split), same method
(full article + all SI files, license/N/raw-vs-composite/no-single-item
checks).

**4 papers -> 9 tables shipped**, all CC BY 4.0:
- `skurvydas_2024_vigour` (10.1371/journal.pone.0307744, N=1140): 4-item
  BRUMS Vigour subscale, 0-4. Rest of S1 Dataset (IPAQ, SSREIT, PSS-10,
  single-item ratings) is pre-aggregated totals -- excluded.
- `gordils_2021_interracial_comp`/`_discrimination`/`_intergroup_anxiety`/
  `_behavioral_avoidance`/`_interracial_trust`
  (10.1371/journal.pone.0245671, N=2549): 5 distinct scales (5/9/4/11/4
  items, all 1-7) in one file -> 5 tables. Study 1 (S1 Data) + Study 2
  (S4 Data) merged (paper confirms identical procedures), Study 2 ids
  offset +100000; both filtered to `AttentionCheck==2` (Study 1 N=847
  exactly matches the paper; Study 2 lands at 1702 vs. the paper's
  reported 1645 -- likely a race-comparison-only subset not applied here,
  documented as a judgment call in Notes).
- `sun_2016_risky_choice_graph` (10.1371/journal.pone.0146914, N=189):
  4-item binary risky-choice task (probability-bet vs. money-bet), resp
  1/0, Experiment 1 only (Experiment 2 N=43 only has per-person
  aggregates; Experiment 3 N=140 only a single trial).
- `janoffbulman_2016_moralmotives_s1`/`_s2`
  (10.1371/journal.pone.0152479, N=311/295): 30-item Model of Moral
  Motives Scale, 1-7, kept as 2 separate study tables rather than merged
  (no "identical to Study 1" language for Study 2 in the paper).
  Subscale-composite and manipulation/attention-check columns excluded;
  Study 3 (country-level aggregate, N=32) out of scope.

12 skipped, all for composite/derived-only data or N too small on closer
inspection: `0210272` (aggregated RT/accuracy only), `0338521`
(scoping-review rows, not respondents), `0172144` (only figure means/SEs
shared per Data Availability, raw data DUA-restricted), `0194574`
(population-normed percentiles / single composite scores, not raw items
-- same pattern as the retracted `stenson_2021_sleep_emotion`), `0121478`
(genuinely raw item data across MMSE/ADAS/NPI/SF-12/QoL-AD x3 waves, but
true N=30 per-arm -- triage's n_participants=73 was wrong), `0329815`
(PRISMA-ScR study-extraction spreadsheet, not participant data),
`0317981` (retrospective chart-review abstraction, no item structure),
`0277247` (only derived binary loneliness classification shared, not the
raw 3-item scale), `0138698` (all candidate columns already-computed
task/IQ composites), `0256983` (same paper as the retracted batch-7
`stenson_2021_sleep_emotion` -- re-verified all 8 SI files still
pre-averaged), `0125124` (all 113 columns derived subscale totals/
proportions/trimmed-mean RTs), `0241694` (PLOS SI is stimulus-validation
stats only; linked Figshare deposit has only proprietary unreadable
E-Prime/E-Merge binaries).

Output: `biblio_batch20_wr_group2.csv` (9 rows), 9 files in `irw_output/`.

### PLOS ONE batch 20 worth_retrying — group 3 review (2026-08-10)

Reviewed the remaining 16 rows (third group). This group's agent stalled
mid-run (600s watchdog) after having already scripted most candidates; a
resume pass confirmed no work was lost, verified every already-written
output via pandas (N/item count/resp range), finished the 3 unreviewed
candidates, and built the biblio CSV.

**8 papers -> 15 tables shipped**, all CC BY 4.0:
`abouhashish_2025_chatgpt_attitudes` (N=240, 40 items),
`biswas_2024_digital_center_quality` (N=332, 26 items),
`busch_2022_course_alleviate`/`_exacerbate` (N=1175/1176),
`derubeis_2017_bdi`/`_arsq` (N=72, 3 waves),
`vanteffelen_2020_pid5_hostility`/`_trait_anger`/`_aq_hostility`/`_foa`/
`_rpq` (N=347-376, 5 scales from one file), `selm_2019_climate_knowledge`
(N=199, 3 items), `audretsch_2021_entrepreneurial_ecosystems` (N=1849, 15
items), `kiraly_2024_perinatal_mh_freq`/`_symptoms` (N=96, 16/19 items).

8 skipped: `0178759` (only composite/z-score/sum columns), `0266940`
(SI is ANOVA summary tables only), `0226953` (exam/homework scores, not
item-response format), `0338906` (third-party AAMC data, not authorized
for public re-sharing per its own terms), `0119395` (pre-aggregated
proportion-correct per item block, not raw trial responses), `0211618`
(composite subscale totals only), `0216149` (raw data buried in a messy
multi-sheet exploratory workbook with derived/exclusion sheets, ambiguous
which sheet is authoritative -- skipped for reliability rather than
guessing), `0351397` (EEG/ERP summary statistics and per-subject task
metrics, not item-response data; N=39 also below the floor).

Output: `biblio_batch20_wr_group3.csv` (15 rows), 15 files in
`irw_output/`.

### PLOS ONE batch 20 worth_retrying — all 3 groups consolidated (2026-08-10)

All 52 `worth_retrying` rows now closed out end-to-end (3 pre-filtered
for N<50 before review: story-time cerebellar-activation study N=22,
facial-disgust/estradiol study N=44, language-skills longitudinal study
N=41). Combined total across the 3 groups: **15 papers -> 30 tables**,
all CC BY 4.0, merged into `biblio_batch20_worthretrying_final.csv` (30
rows; the 3 per-group files deleted after merging, content fully
captured here). All 30 `irw_output/*.csv` files verified present with
sane N/item-count/resp-range via pandas. `plos_retriage_batch20.csv`
deleted -- this closes out PLOS ONE batch 20 end-to-end (`good` candidates
already shipped 2026-08-10, `human_review` rows already pasted
2026-08-10).

### QC pass on batch 20 worth_retrying output (2026-08-10)

ben-domingue caught two issues in the just-consolidated output before
upload:
- **`abouhashish_2025_chatgpt_attitudes`**: `cov_year_of_study` values
  carried a stray bullet+tab prefix copied straight from the source
  checkbox form (e.g. `"•\tFourth Year"`) plus inconsistent
  capitalization (`"Fourth year"` vs `"Fourth Year"` vs `"third year"`).
  Fixed in `abouhashish_2025_chatgpt_attitudes.py` to strip the
  bullet/tab/whitespace prefix and title-case the result; regenerated
  (now cleanly `First/Second/Third/Fourth Year`, N/item counts unchanged).
- **`gordils_2021_interracial_comp`/`_discrimination`/
  `_intergroup_anxiety`/`_behavioral_avoidance`** (not `_interracial_trust`,
  which was clean): ben-domingue asked whether the fractional resp values
  were imputed. Checked directly against the raw Study 2 (S4 Data) file --
  each scale's *second* item column (COMP2, DISCRIM2, ANX2, AVOID2) was
  bit-for-bit identical to that scale's own pre-computed composite mean
  column (e.g. `AVOID2 == AVOID`) for all 1774 Study-2 rows, a spreadsheet
  artifact (dragged-formula or copy/paste error in the source file), not a
  genuine raw response -- exactly the kind of imputed/derived value
  datastandard.md's "checking for imputed values" rule exists to catch.
  Study 1's own item2 columns were verified unaffected (integer-only, no
  match to any composite). Fixed `gordils_2021_interracial.py` to null out
  the four corrupted Study-2 columns before melting; all 4 affected
  outputs regenerated with zero fractional resp values remaining (N
  unchanged at 2549, item counts unchanged). `biblio_batch20_worthretrying_
  final.csv`'s Notes column updated per-table with both fixes.

## PLOS ONE batch 21 (2026-08-10)

Discovery run with 30 recycled search terms pulled from the non-PLOS pool
in `search_terms_log.csv` (per `SKILL.md`'s term-recycling guidance;
filtered to ASCII/English-looking terms not yet tried against PLOS,
~982 candidates available): academic procrastination, imposter syndrome,
grit, eating disorder, body dissatisfaction, climate anxiety, vaccine
hesitancy, workplace ostracism, moral disengagement, financial literacy,
sense of belonging, dark triad, cyberbullying, gaming disorder, religious
coping, forgiveness, psychological capital, work-life balance, parenting
stress, sport confidence, self-determination, racial prejudice,
conspiracy beliefs, medication adherence, trust in science, gratitude,
career indecision, sexual harassment, weight stigma, teacher
self-efficacy.

1,921 candidates -> 18 `good` + 319 `human_assistance` + 1,523
`no_usable_file` + 35 `not_item_response` + 14 `download_failed` + 12
`error`. Retriage (`irw_retriage_ha.py`) on the `human_assistance`
bucket: 52 `worth_retrying`, 115 `human_review`, 77 `aggregate_continuous`,
75 `not_item_response`.

**`good`-candidate review**: 5 of the 18 were duplicates of candidates
already reviewed and skipped in earlier batches (caught by DOI grep
against `BATCH_LOG.md` before review, saving re-work): `0327299`
(caste-equality, single-item belief question -- batch 20), `0260168`
(Berlin PrEP, heterogeneous single items -- batch 20), `0348206`
(WFH/hybrid-workplace, best-worst-scaling choice experiment, not Likert
-- batch 15), `0295904` (dieticians turnover, real CD-RISC items
described in the paper but never actually shared in the file -- batch
18), `0254795` (physicians wellbeing, composite index only -- batch 18).
Remaining 7 reviewed (fetch full article + SI files, verify
license/raw-vs-composite/N/item structure). Result: **3 papers processed
-> 24 tables**, plus 1 more paper -> 1 table (25 total), all CC BY 4.0
except one CC0:
- `yuebo_2024_online_learning` (10.1371/journal.pone.0297515, N=245): ISS
  model + TPACK survey, 10 distinct 4-5-item constructs (sysquality,
  srvquality, infoquality, use, satisfaction, netbenefit, tk, tck, pck,
  tpack) in one SI file -> 10 tables per the multiple-scales rule.
  Aggregate TK/TCK/PCK/TPACK mean columns excluded.
- `anh_2026_finwellbeing` (10.1371/journal.pone.0340002, N=306): financial
  socialization/technology/capability survey, 6 constructs (finsocial
  ization, ai_adoption, finbehavior, finwellbeing, finliteracy,
  digitaltrust) -> 6 tables.
- `pang_2023_nev_adoption` (10.1371/journal.pone.0285815, N=309): new
  energy vehicle adoption survey, 8 constructs (perceived_usefulness/
  ease_use/risk/cost/enjoyment, media_influence, social_norms,
  behavioral_intent) -> 8 tables.
- `baaziz_2023_sms2` (10.1371/journal.pone.0295262, N=780, CC0): 18-item
  Arabic Sport Motivation Scale (SMS-II). Note: the article's own
  caption-to-file mapping for its 3 SI files was internally inconsistent;
  `.s003` (780-row combined EFA+CFA sample) used instead of the captioned
  `.s001`, confirmed via HTTP redirect inspection.

3 of the 7 skipped: `0207691` (AAA gender-bias, observational coding of
conference Q&A rounds -- id resets each round, not a stable person
identifier, not a self-report instrument), `0118221`
(Mindfulness/Compassion, only composite empathic-responsiveness indices
+ a binary outcome, no raw items), `0131613` (Sexism/gaming, behavioral
game-performance data -- kills/deaths, coded comments -- not a
self-report instrument). All 3 had triage N/item counts that didn't match
actual file content, another confirmation of the standing "good needs a
human glance" caution.

All 25 outputs re-verified directly (N/item count/resp range/no-null-id)
after the agent's report. `biblio_plos_batch21.csv` (25 rows) staged in
`automated_finding/` for the dictionary sheet.

`human_review_plos_batch21.csv` (115 rows) staged for the "Human eye"
sheet. `worth_retrying` (52 rows) not yet reviewed -- open item, see
`TODO.md`. `plos_batch21_triage.csv` and `plos_batch21_retriage.csv`
retained until both are closed out.

### PLOS ONE batch 21 worth_retrying — review begins (2026-08-10)

52 `worth_retrying` rows from `plos_batch21_retriage.csv` triaged before
deep review by grepping each DOI against this log for prior verdicts
(same method as batch 9's backlog-sweep and batch 20's group reviews):

**18 of 52 are duplicates of candidates already confirmed as content
problems in earlier batches** -- not re-reviewed, skip reasons carried
forward as previously recorded: `0211618`/`0272987` (composite subscale
totals only), `0276794`/`0322635` (aggregate subscale composites only),
`0343308` (item-development/factor-loading meta-table, not primary
data), `0271030` (5-column aggregate subscale file), `0302350`
(heterogeneous demographic/clinical survey, no item structure),
`0319473`/`0338521`/`0305567` (scoping reviews / rows-are-papers-not-
people, not primary respondent data), `0160805` (subscale/total scores
only, no raw items), `0267580` (incoherent single-item vaccination-
intention), `0267181` (ASD-MBQ physical-activity outcome measures, no
Likert battery), `0280758` (CEO/firm panel data, not individual survey),
`0203336` (BSI/FSB subscale totals + physiology only, composite),
`0315442` (Delphi expert-panel tables, not respondent-level),
`0206555` (video-game-expertise database, not respondent data),
`0294593` (fractional composite/latent-variable SEM scores only).

1 more (`0195766`, cichlid fish mate-preference study) dropped
pre-review on "non-human" grounds alone -- ben-domingue confirmed the
drop is fine to leave as-is here, but flagged that reasoning as wrong in
general (IRW's schema is species-agnostic); `SKILL.md` updated with a
standing rule so future non-human candidates get evaluated on content
merits, not species.

**33 remain, split into 2 parallel review groups** (17 + 16, same
fetch-article-plus-SI / license / raw-vs-composite / N / item-structure
method as batch 20). 9 of the 33 carry prior-batch context worth
prioritizing (real item-level data previously confirmed present but
left unscripted for lack of codebook time): `0227877` (atlas of
personality -- real data reportedly on Figshare, not the PLOS SI itself,
external lead not yet chased), `0258606`/`0197276` (in an earlier
"screened but not hand-verified" pool, genuinely unknown either way),
`0252329` (couples emotion-regulation questionnaire, "confirmed
structurally good, not yet scripted"), `0272095` (Dutch self/other/meta
personality, 1086-col multi-rater HEXACO), `0280919` (Chinese EFL
learning, real items w/ Chinese-text Likert labels + 481-vs-942 row
mismatch to resolve), `0314338` (PE-teacher/student sports study,
ambiguous Chinese-labeled construct-to-column mapping), `0230103`
(French school-subject self-concept, 249 cols/5 domain scales, has a DOB
column to strip), `0257577` (disordered-eating-in-athletes, N=802, 3
waves, ~20 subscale prefixes in a 665-col file). Results to follow.

### PLOS ONE batch 21 worth_retrying — all 33 non-duplicate candidates resolved (2026-08-10)

Both parallel groups (17 + 16 candidates) finished and independently
re-verified with pandas (N/item count/resp range/no-null-id) before
merging. **14 papers -> 55 tables shipped**, all CC BY 4.0:

Group A (7 papers -> 22 tables): `pilch_2021_coping_covid` (coping
behavior/protection motivation/fear-of-COVID/IPIP-BFM-20 personality, 4
tables), `shineha_2024_genome_edited_food` (public+expert attitudes
toward genome-edited food, 3 tables), `marquessanchez_2023_kidmed`
(KIDMED dietary index, 1 table), `chanal_2020_selfconcept` (5
school-subject self-concept domains -- Ecole/Maths/Francais/Anglais/
EducPhy, DOB/PII column stripped, 5 tables), `zhao_2025_digital_literacy`
(CFPS panel digital-literacy items with a `wave` column, N=6202, 1
table), `weeldenburg_2022_target_pe` (BRPEQ motivation + TARGET-MTPQ, id
column false-alarm resolved, 2 tables), `de_vries_2022_hexaco` (HEXACO
self/other/meta -- successfully unpacked the previously-deferred
1086-column multi-rater structure with a `rater` column on the "other"
table -- plus BAT burnout core+secondary and EWWS well-being, 6 tables).

Group B (7 papers -> 33 tables): `sondell_2018_dementia_motivation`
(staff-rated motivation, text-Likert recoded per paper, 1 table),
`dominguez_2018_job_crafting` (JCS/UWES/MBI/ITL, resolves the previously
"unknown quality" `0197276` lead, 4 tables), `stoyel_2021_disordered_
eating` (the flagged priority lead -- N=802, 3-wave EDI/PANAS/EDE-Q
subscale battery, 21 tables), `antes_2020_pdm` (professional
decision-making, pre/post binary items, 1 table), `benitezsillero_2021_
bullying` (EBIPQ, N=1441, 1 table), `dong_2025_teacher_leadership`
(text-Likert recoded per paper, 1 table), `taylorabdulai_2025_covid_
vaccine` (Yes/No item batteries, 4 tables).

19 papers skipped, one line each: `0227877` (**external lead, not
chased** -- real data is at Figshare `10.6084/m9.figshare.c.4792323`, not
the PLOS SI), `0252329` (23-expert content-validity panel, not respondent
data), `0280919` (unresolvable 481-vs-942 row mismatch from a non-unique
index key), `0152462` (web-log pageviews + exam grades only, no survey
data), `0334407` (genuinely qualitative thematic-interview data),
`0314338` (Chinese-labeled columns don't reconcile with the paper's
described instruments), `0294723` (opaque letter-prefixed columns, no
codebook, mismatched vs. paper), `0284553` (demographics only, no
item-level data), `0267055`/`0313189` (composite/derived index variables
only), `0328215` (SI is a variable-extraction codebook, not primary
data), `0294116` (raw-item SI covers only N=40, below the floor),
`0321423` (SI is included-studies characteristics tables, a scoping
review of *other* scales), `0295239` (no tabular SI, only DOCX
appendices), `0213015` (composite WHOQOL domain scores + pre-aggregated
flags only), `0262639` (session/presentation-level behavioral coding, not
person-level self-report -- same failure mode as the AAA-conference paper
skipped in this batch's `good` review), `0283720` (SI is the blank survey
instrument, no responses), `0238372` (raw-response SI covers only N=49),
`0241188` (all columns are derived composite indices).

All 55 outputs independently re-verified (N/item count/resp range/no
null ids) after both agents' reports -- clean. `biblio_plos_batch21_
worthretrying.csv` (55 rows, merged from both groups) staged in
`automated_finding/` for the dictionary sheet. This closes out PLOS ONE
batch 21 end-to-end (`good` candidates already shipped, `human_review`
rows already pasted). `plos_batch21_triage.csv` and `plos_batch21_
retriage.csv` deleted -- content fully captured here.

### QC pass on batch 21 output, prompted by ben-domingue (2026-08-10)

ben-domingue asked three targeted questions about resp semantics before
upload: are `de_vries_2022_hexaco_meta`'s non-integer values imputed?
Do `sondell_2018_dementia_motivation`'s and `stoyel_2021_*`'s resp=0
values indicate missingness?

- **`de_vries_2022_hexaco_meta`**: yes, a real problem. 69 of 38304 cells
  (0.18%) held non-integer values (e.g. 3.5) despite the paper's Methods
  stating a plain integer 1-5 HEXACO scale, with no documented
  half-point option. Confirmed the values are present in the raw SPSS
  file itself (not a script artifact) and isolated to the meta-perception
  rater slot only -- self/other perception tables from the same file have
  zero non-integer cells. No explanation found in the paper; treated as
  an unexplained artifact per datastandard.md's imputation-check rule and
  dropped. Fixed `de_vries_2022_hexaco.py` to filter non-integer resp in
  both the `melt_and_save()` helper and the separately-coded
  other-perception block; regenerated (N=399, items=96, resp 1-5 clean
  integers; the other 3 HEXACO/BAT/EWWS tables from the same script were
  already clean and unaffected). Biblio Notes updated.
- **`sondell_2018_dementia_motivation`**: resp=0 confirmed genuine, not
  missingness. Fetched the article directly: "Each participant's
  eagerness to participate was classified using a five-point Likert
  scale [0, no motivation (is present without participating); 1, low
  motivation...]" -- 0 is staff's lowest-motivation rating for a
  participant who is present but not engaged, a real observed category,
  not a non-response code. No fix needed.
- **`stoyel_2021_*`**: resp=0 confirmed genuine for both instrument
  families. EDI subscales (drive_thinness/body_dissat/bulimia/
  maturity_fears/interocept_awareness/ineffectiveness/perfectionism/
  interpersonal_distrust, coded 0-3): the paper states "numerical scores
  of 0 0 0 1 2 3 were applied respectively" to the underlying 6-point
  Never..Always response, i.e. the three lowest-severity raw categories
  are conventionally collapsed to a single 0 -- a standard, published EDI
  scoring rule, not missingness (each output row is still one raw item
  response transformed by a documented per-item rule, not a
  cross-item composite). EDE-Q subscales (restraint/eating_concern/
  shape_concern/weight_concern/binge_purge, coded 0-6): 0 = "not at all"/
  "no days" on the EDE-Q's standard 0-6 frequency/severity anchor, a
  well-established instrument convention; distribution shape (smooth,
  monotone-declining from 0) is consistent with a real lowest-severity
  anchor rather than a sentinel. No fix needed.

**Follow-up (persistent-issue fix, not just this batch's output):** this
is the second time in this batch alone that a `resp` semantics question
(0 = valid vs. missingness; non-integer = imputed vs. genuine) needed a
person to ask before shipping. `datastandard.md`'s "What to verify
before saving" checklist items 4 and 10 strengthened: item 4 now
requires *positively confirming* every recurring value's meaning against
the paper's own text (not just checking that it's not statistically rare
or isolated -- a real non-response code can be common and smoothly
distributed too) and flagging for human review rather than shipping
when the paper is silent; item 10 now requires acting on a non-integer-
on-integer-scale signal (explain or drop) rather than treating it as
merely a "note it and move on" observation. See `datastandard.md` for
the updated text.

## PLOS ONE batch 22 (2026-08-10)

30 recycled English search terms (validated instrument/construct names
already used successfully against non-PLOS sources per `search_terms_log.csv`,
never before tried against PLOS ONE, per `SKILL.md`'s term-recycling
guidance): organizational citizenship behavior, work locus of control,
creative self-efficacy, internet gaming disorder, exercise motivation, sport
motivation, athletic identity, physical self-concept, couple satisfaction,
sexual function, health-related quality of life, illness anxiety, climate
change attitudes, civic engagement, political trust, implicit bias, media
literacy, need for cognition, vocational identity, career self-efficacy,
prospective memory, reading motivation, mathematics self-concept, STEM
attitudes, prolonged grief disorder, trait anxiety, hedonic wellbeing,
eudaimonic wellbeing, psychological wellbeing, optimism scale. All logged to
`search_terms_log.csv`.

`irw_discover_plos.py` run: 1,684 candidates -> 1,344 `no_usable_file` + 272
`human_assistance` + 27 `not_item_response` + 16 `download_failed` + 15
`error` + 10 `good`. `irw_retriage_ha.py` on the `human_assistance` bucket:
90 `aggregate_continuous`, 77 `human_review`, 54 `worth_retrying`, 51
`not_item_response`.

**Dedup pass before review**: cross-checked all 10 `good` + 54
`worth_retrying` DOIs against this file's own history (grep on the 7-digit
`pone.XXXXXXX` suffix) — 48 were exact-DOI repeats of candidates already
reviewed and struck in earlier batches (search terms keep resurfacing the
same PLOS articles across different query terms, expected, not re-reviewed).
That left 35 genuinely new candidates (7 `good` + 28 `worth_retrying`), split
into two groups of ~17-18 and reviewed in parallel by 2 agents, each fetching
the full article page + ALL Supporting Information files (not just the one
`process_one()` flags) and applying the standard license/N>=50/no-single-item/
raw-vs-composite checks.

**Result: 15 papers -> 38 tables shipped, all CC BY 4.0.**

Group A (10 papers -> 23 tables): `zeng_2025_megaproject_msr`/`_seap`/`_ecm`
(39/11/15-item megaproject social-responsibility survey, Chinese-led Thailand
infrastructure, N=458), `tomioka_2022_srh_importance`/`_sufficiency`/
`_support_types`/`_future_needs` (Japanese nurse survey on
adolescent/young-adult cancer-patient sexual/reproductive health support,
N=865), `wang_2026_veteran_expectations` (3-item behavioral-expectations
scale, Chinese veterans, N=624; raw file N=624 vs. paper's 525
post-validity-screen N -- shipped as-is, all rows clean and in-range),
`buczel_2022_inoculation_belief` (6-item misinformation-belief scale 1-11,
inoculation-technique RCT, N=137, `treat` column; a companion composite
accuracy-count block excluded per the composite-exclusion rule),
`cacciatore_2021_isel`/`_crisis_care_satisfaction`/`_ongoing_satisfaction`
(12/9/9-item bereaved-parent grief-support scales, N=345-362),
`beck_2021_hads`/`_iesr`/`_pss10`/`_cdrisc10` (14/22/10/10-item COVID-19
cohort battery, N=214-279, `cov_role` patient-vs-relative; triage's
text-coded-Likert flag was a false positive, item columns were already clean
numeric), `akrawi_2025_sclc` (13-item Dutch SCLC scale, pharmacy-technician
simulation training, N=129; dup_id_item flag traced to one accidental
data-entry ID reuse, not repeated measures -- row index used as id),
`gabriel_2026_knowledge_correct`/`_knowledge_confidence`/`_media_use`
(9/9/6-item German farmer/advisor agricultural-knowledge survey, N=2022,
binary knowledge quiz confirmed genuinely binary via codebook, not Likert),
`alasmari_2025_ai_trust_confidence`/`_compare` (4/5-item AI-trust survey,
N=327-335; "Unsure" responses on the compare scale treated as non-response
and dropped, 8 all-Unsure respondents excluded from that table), `xu_2022_
ples_aa` (16-item PLES-AA scale across 4 dimensions, Chinese tertiary-ed
administrators, N=197; dup_id_item flag traced to one accidental participant
ID reuse -- row index used as id). One naming correction made mid-review:
`buczel_2022_inoculation_belief` was initially mis-attributed to
"Pennycook" by a sub-review pass before being corrected to the paper's
actual authors (Buczel, Szyszka, Siwiak, Szpitalak & Polczyk).

Group B (5 papers -> 15 tables): `zheng_2015_ibdq` (32-item Chinese IBDQ,
ulcerative colitis QoL, N=224; source name-initials id column not unique,
row index used instead), `wekker_2018_mfsq` (18-item McCoy Female Sexuality
Questionnaire, RCT 5-year follow-up, N=177, `treat` column; scattered
non-integer cells on an integer 1-7 scale found and dropped per
datastandard.md's imputation-check rule -- paper only documents
mean-imputation at the domain-score level, but contamination reached raw
item cells in the shared file), `roettl_2018_game_attitude`/`_arousal`/
`_brand_attitude`/`_brand_recognition`/`_scepticism` (6/3/24/8/9-item video
game-technology/brand-placement battery, 2D/3D/VR between-subjects, N=234,
`cov_condition`; triage's 1.6x duplicate-ratio flag was a false signal from
varying brand-column counts, confirmed via condition value counts matching
the paper's N exactly; single-item `F25_Presence` excluded), `zubair_2021_
psm`/`_political_support`/`_altruism`/`_social_impact`/`_org_performance`
(5/3/4/4/8-item public-service-motivation/organizational-performance survey,
N=405, zero missing; kept PSM1 despite the paper dropping it from its own
measurement model for low factor loading -- this is raw item data, not the
paper's analysis subset), `ganbat_2022_pollution_symptoms`/`_disease_risk`/
`_leave_type` (8/5/5-item binary wintertime-absenteeism checklists,
Ulaanbaatar private-sector survey, N=1329; a 4th "reasons for absence"
block excluded -- 66-68% `8888` not-applicable sentinel since it's only
answered by the absent subset, not the full sample).

**19 papers skipped** (content/N failures, one line each): `0265087`
(aggregate demographic table only), `0304580` (country-year macro panel, no
item structure), `0200483` (headerless file, no codebook to confirm a
recurring value's meaning), `0199002` (only per-subject aggregate outcomes
shared, no raw trial data), `0118697` (USDA food-composition data, not human
responses), `0256590` (economic/demographic household variables, not
psychometric items), `0293541` (N=16, nominal checkbox responses),
`0260224` (app-usage behavioral log, no validated-scale items), `0267931`
(no id/item/wave columns, pre-binarized + already kNN-imputed), `0257487`
(raw checkbox items don't align 1:1 with respondent IDs; the alternate file
is a derived agreement code, not a raw item), `0162911` (every SF-36 column
already a subscale/summary composite), `0170891` (single composite Kiddy-
KINDL total per wave, already mean-imputed), `0318986` (one stance code per
video, effectively single-item), `0272652` (real per-patient file is
composite IIEF/IPSS sums only, also N~51), `0312826` (literature
data-extraction/charting table, no respondents), `0177398` (N=22), `0171610`
(sensor event-log data, N=6), `0124797` (neuroimaging cluster-coordinate
tables, zero person-level rows, also access-gated), `0275372` (N=29;
otherwise clean raw 3-wave 13-item deliberation-voting data -- worth
revisiting if a larger-sample version appears).

**1 held for borderline N, not shipped**: `0311487` (natural
soundscapes/mood recovery, N=68 unique participants in the 50-99 band) --
also independently disqualified on content grounds (both SI files hold only
pre-summed STAI-S/UWIST-MACL composite scores, not raw items), so the N
question didn't need ben-domingue's sign-off this time, but noting the band
for the record per `feedback_min_sample_size`.

All 38 output CSVs independently re-verified after both agents' reports
(N/item count/resp range/no null ids) -- clean. `biblio_plos_batch22.csv`
(38 rows, merged from both groups' review) staged in `automated_finding/`
for the dictionary sheet. `human_review_plos_batch22.csv` (77 rows) staged
for the "Human eye" sheet. This closes out PLOS ONE batch 22 end-to-end.
`plos_batch22_triage.csv`, `plos_batch22_retriage.csv`, and all
`plos_batch22_good*.csv`/`plos_batch22_worthretrying*.csv`/
`plos_batch22_group*.csv` intermediate files deleted -- content fully
captured here.

### PLOS ONE batch 23 — discovery + full review, all 3 groups (2026-08-11)

Discovery: `irw_discover_plos.py` run with 30 recycled English search
terms pulled from `search_terms_log.csv`'s non-PLOS pool (per the
"Large pool of recyclable PLOS search terms" backlog item) —
`enneagram personality`, `depression anxiety stress`, `mood disorder`,
`ptsd symptom`, `teacher stress`, `stress resilience`,
`interpersonal competence`, `emotional self-efficacy`, `hostility`,
`shame`, `guilt`, `coparenting`, `alcohol dependence`, `drug use disorder`,
`racial identity`, `work values`, `social phobia`, `bereavement`,
`obsessive compulsive`, `organizational commitment`,
`transactional leadership`, `servant leadership`, `leader-member exchange`,
`organizational trust`, `organizational justice`, `knowledge sharing`,
`problematic social media use`, `cyberchondria`, `phubbing`,
`online gaming addiction`. 1,884 candidates -> 13 `good` + 314
`human_assistance`. Retriage (`irw_retriage_ha.py`) on the 314 gave 40
`worth_retrying` + 106 `human_review` + 86 `aggregate_continuous` + 82
`not_item_response`. 4 of the 13 `good` rows were pre-filtered out for
N<50 before review (11p, 20p, 27p — also non-human/mouse — and a 20p case)
per `feedback_min_sample_size`, leaving 9 `good` + 40 `worth_retrying` = 49
candidates split into 3 groups of ~16-17 and reviewed in parallel by 3
agents, each fetching the full article + ALL Supporting Information files
(not just the one the automated pass inspected) and applying the standard
license/N>=50/no-single-item/raw-vs-composite checks.

**Overall result: 14 papers -> 28 tables shipped, all CC BY 4.0.** No
candidate landed in the 50-99 borderline-N band needing ben-domingue's
sign-off this batch — every skip failed on a harder criterion (composite-
only data, confirmed N<50, not respondent item-response data at all, e.g.
chart-review/case-registry/animal-electrophysiology/qualitative studies).
28 output CSVs independently re-verified after all three groups' reports
(N/item count/resp range/no-null ids) — clean. `biblio_plos_batch23.csv`
(28 rows, merged from the three groups' staging files) staged for the
dictionary sheet; `human_review_plos_batch23.csv` (106 rows) staged for
the "Human eye" sheet.

#### Group A — 16 hand-assigned candidates

Fetched each article's full text
(Methods/Measures, Data Availability, license) plus the complete Supporting
Information file list (not just the one the automated triage inspected),
then downloaded and pandas/pyreadstat-inspected every candidate SI file.

**6 papers -> 13 tables shipped, all CC BY 4.0:**
- `alves_2017_hamd17` (17-item Hamilton Depression Rating Scale, raw
  clinician-rated items, N=291; sentinel 999 on item 5 — matches the
  paper's documented single missing value — filtered).
- `busch_2023_stigma` (8 binary concealable-stigmatized-identity self-report
  items, N=1970).
- `ni_2025_relationship_network`/`_strategic_orientation`/
  `_knowledge_transfer`/`_open_innovation` (8/3/4/9-item Likert battery on
  Chinese SME innovation behavior, N=329, clean 1-5, no missing).
- `tasaygar_2025_bai` (21-item Beck Anxiety Inventory, N=210; PII name
  column dropped and also found non-unique across distinct patients so row
  index used as id instead; one isolated soru5=4 value dropped as a
  data-entry error against the 0-3 scale) and `tasaygar_2025_sdasi` (4 raw
  SDASI severity components from the same file; one isolated non-integer
  value on the extent item dropped).
- `klatt_2016_speed_estimation` (48-trial raw verbal car-speed-estimate
  task, continuous km/h, N=60; the file's road-crossing-behavior columns
  were per-condition aggregates over repeated trials, not raw
  single-observation responses, and were not shipped).
- `muharam_2022_srq29` (29-item SRQ mental-health screening, binary, N=159;
  PII name/phone columns dropped, row index used as id).
- `nordhoff_2021_trust`/`_motive`/`_safety` (12/4/6-item Likert scales on
  trust/motive/safety for SAE Level 2 automated cars, N=112-116 after
  filtering; sentinel code 99 — documented in the paper as "prefer not to
  respond"/"not applicable" — filtered out; row index used as id, no id
  column in source).

**10 papers skipped** (content failures, one line each): `0131613`
(behavioral game-performance counts — kills/deaths/comment tallies — not
item responses), `0279360` (accuracy columns are means over ~9 trials per
condition, a computed composite, not raw per-trial data — same failure
mode as the `stenson_2021_sleep_emotion` retraction), `0180298` (shared
file has only pre-computed composite anxiety/avoidance scores, no raw
items), `0273579` (CC0, otherwise strong 5-wave longitudinal design, but
the "minimal data set" SI file holds only composite PHQ/GAD/ULS/DOCS/RFS
totals per visit, no raw items), `0217482` (dyadic leader-follower "pairwise
data matrix" SI file holds only composite/centered/z-scored variables, no
raw IaW/WE/OLBI items), `0161840` (SPSS file holds only composite
Type-A/Type-D/HADS/etc. scores, no raw items — also used hot-deck
imputation on composites per the paper, moot since no raw data present),
`0241991` (background-data file holds only composite scale totals and
graph-theory network metrics, no raw items), `0234997` (SPSS file holds
only composite BL/FU scale scores, no raw items), `0150312` (SPSS file
holds only composite scale scores, no raw items).

All 13 output CSVs verified with pandas (N/item count/resp range/no-null
ids) after writing. `biblio_plos_batch23_groupA.csv` (13 rows) merged into
`biblio_plos_batch23.csv` along with Groups B and C below.

#### Group B — 16 candidates

Same method as Group A: full article text + all SI files fetched and
inspected per candidate, not just the one the automated triage pass
opened.

**2 papers -> 3 tables shipped, all CC BY 4.0:**
- `yang_2018_cesd` (20-item CES-D-style depression scale, 1-4, N=358) and
  `yang_2018_anxiety` (companion 20-item anxiety scale, 1-4, N=358) — from
  a study of female migrant entertainment-venue workers in China. Raw
  items were hiding in a 270-column SAV file alongside dozens of
  precomputed subscale sums/covariates; confirmed the E1-E20/E21-E40
  blocks are genuinely raw (range 1-4, not the much larger summed range).
- `witus_2022_narrator_perception` (3-item narrator-perception scale —
  trustworthy/comforting/knowledgeable, 1-4, N=809 — only respondents in a
  video arm of a COVID-19 vaccination-video RCT answered these; verified
  against the S1 Appendix's full survey-flow diagram and item text). No id
  column in source, row index used per datastandard.md; `cov_narrator_
  gender` records the male/female narrator arm.

**14 papers skipped**, one line each: `0233831` (SSRS/CD-RISC/SCL-90,
N=1472 — SI file has only subscale scores/means, no raw items), `0270464`
(role stress/burnout/CBCL, longitudinal — only per-wave subscale totals),
`0294593` (info literacy — SI file literally labeled "Mean of IL" etc., no
raw items), `0224254` (EI training RCT, N=54 — only subscale/total scores,
also would have been borderline-N even if raw), `0211618` (humour/
reappraisal — only derived indices, no raw items), `0272987` (irrational
beliefs, multi-study — checked all 5 SI files, every one composite-only),
`0195239` (autistic traits/social cognition — RT/accuracy from flanker and
visual-search tasks, not a Likert item response), `0350293` (QoL post-DBS-
OCD — paper states QoL was collected as qualitative interview text, not
numeric), `0254953` (CBCL/YSR DSM scales — only subscale sums), `0203689`
(CFPQ/PPAPP parenting — only subscale scores, incl. parent/staff/
difference versions), `0269443` ("mixed method" motherhood study — Data
Availability statement says passive data isn't public yet, and the only
quantitative instrument, PHQ-9, isn't in either shared SI file), `0199605`
(retirement time-use/mental health — only scale totals), `0315442` (Delphi
PSNS questionnaire — actual expert panel is N=16, not the 61 the automated
triage reported; below N=50), `0279871` (food marketing/attentional bias —
article text confirms final analytic N=41; below N=50).

No candidates landed in the 50-99 borderline-N band this group. Files:
3 scripts in `data/` (`yang_2018_cesd.py`, `yang_2018_anxiety.py`,
`witus_2022_narrator_perception.py`), 3 CSVs in `irw_output/`,
`biblio_plos_batch23_groupB.csv` (3 rows, merged into `biblio_plos_
batch23.csv`).

#### Group C — 17 candidates (mostly unresolved n/item count from the
automated pass — header-offset, non-tabular, or genuinely not item-
response data)

Same method as Groups A/B.

**6 papers -> 12 tables shipped, all CC BY 4.0:**
- `naja_2024_challenges` (5-item binary "which challenges do you face"
  checklist, N=371, dieticians in the UAE; the triage-reported "27 items"
  was a miscount — the SI file's other columns are recoded covariates plus
  one derived binary resilience group, not raw CD-RISC items).
- `shi_2021_gentrification` (23-item, 1-5 Likert SEM survey on super-
  gentrification drivers, N=209 — matched triage's report exactly).
- `zhang_2024_attractiveness`/`_expertise`/`_parasocial`/`_viewer_dsp`/
  `_streamer_dsp`/`_gift_intention` (6 constructs, 23 items total, N=325,
  1-5 Likert, all clean — pan-entertainment live-streaming gift-giving
  study).
- `simard_2018_fgf2_behavior` (7-item mouse behavioral battery — FST/EPM/
  OF outcome measures, N=67 mice, `treat`=Fluoxetine vs Vehicle; same
  animals verified across all 3 test sheets via exact-match merge).
- `orovou_2021_pcl5` (20-item PCL-5 PTSD checklist, 0-4, N=469) and
  `orovou_2021_lec5` (17 binary trauma-exposure items, companion LEC-5)
  from the same Greek psychometric-validation study; response anchors
  confirmed via SPSS value labels.
- `warwas_2022_sharing_economy` (8 binary Yes/No sharing-economy
  participation items recoded to 1/0, N=1000, Polish demographic survey).

**11 papers skipped**, one line each: `0294151` (maternal separation rats
— real data is multi-block electrophysiology/behavioral Excel sheets;
behavioral-score block only ~30 rats/group, rest is raw per-event synaptic-
current time series, not person-item structured), `0192329` (rat cerebral
cortex microstructure — SI file is aggregate effect-size/CI summary by
brain region, composite/derived), `0309205` (rare-disease clustering — 912
families not the reported 11598, sparse case-level phenotype listing with
only positive endorsements, a case registry not a fixed-item instrument),
`0163811` (autopsy consent — confirmed chart-audit database, one row per
patient, no repeated-item structure), `0307349` (caregiver anxiety — SAV
file, N=80, only precomputed subscale/total scores for STAI/PSS/MBI/etc.,
no raw item columns despite a rich named-instrument battery), `0259364`
(VR provider survey — genuine 62-item instrument but only 17 complete
respondent records, under N=50), `0317981` (self-harm Kenya — confirmed
retrospective chart-review, one row per patient), `0242326` (Caprara et
al. self-efficacy study, N=1695, 3 named scales — only a codebook + figure-
data SI files found, no raw-response file; flagged in `TODO.md` for a
second SI-list check rather than written off outright), `0172144` (PTSD/
gender fear generalization — paper states raw data is in a restricted VA
computing environment, only figure means/SEs shared), `0345874` (coaching
power, Foucauldian — quantitative component is only 30 rows, 10 scenarios
x 3 coaches, plus primarily qualitative), `0319473` (stepped care — this
is a scoping review of 68 studies, not a primary survey; the "dataset" is
study-level extraction data, not respondent item responses).

All license checks CC BY 4.0 confirmed on the article page. Files: 7
scripts in `data/` (`naja_2024_challenges.py`, `shi_2021_gentrification.py`,
`zhang_2024_giftgiving.py`, `simard_2018_fgf2_behavior.py`,
`orovou_2021_pcl5.py`, `warwas_2022_sharing_economy.py` — the zhang script
produces all 6 tables), 12 CSVs in `irw_output/`,
`biblio_plos_batch23_groupC.csv` (12 rows, merged into `biblio_plos_
batch23.csv`).

This closes out PLOS ONE batch 23's discovery + `good`/`worth_retrying`
review end-to-end. `plos_batch23_triage.csv`, `plos_batch23_retriage.csv`,
`plos_batch23_good.csv`, `plos_batch23_worthretrying.csv`, and the three
`biblio_plos_batch23_group{A,B,C}.csv` files are being deleted now that
their content is captured here and merged into `biblio_plos_batch23.csv`.

#### Post-review ordinality fixes (2026-08-11, ben-domingue's questions)

Two shipped tables were revised after ben-domingue questioned whether
`resp` was ordinally meaningful:

- **`simard_2018_fgf2_behavior` -> `simard_2018_epm_behavior`, dropped to
  EPM only.** The original 7-item file bundled outcome measures from three
  distinct standardized behavioral tests (FST/EPM/OF) into one table, and
  two of those items (`fst_latency_immobility_s`, `of_latency_centre_s`)
  were time-to-first-occurrence latencies -- response-time-like measures,
  not substantive responses in their own right, per
  `feedback_rt_column_scope`. Removing the two latency items left FST and
  OF with only 1 item each, below IRW's 2-item minimum, so those two
  scales couldn't ship standalone; there's no accuracy-type reframing
  available for behavioral-duration measures the way there was for
  klatt's speed task (no "true" target being judged), so per
  ben-domingue's direction the fix was to ship EPM only (3 items: time in
  open arms, % of distance in open arms, total distance traveled -- no
  latency component in any of the three). `data/simard_2018_fgf2_
  behavior.py` deleted, replaced by `data/simard_2018_epm_behavior.py`;
  old combined output/biblio row replaced with the EPM-only table (N=67
  mice, unchanged).
- **`klatt_2016_speed_estimation` — `resp` changed from raw verbal speed
  estimate to signed estimation error.** ben-domingue pointed out the true
  speed of each approaching car is known (45/50/55 km/h, encoded in every
  item's own name, e.g. `@44898_nis_45_trottoir`), so the raw estimate
  alone doesn't capture what the study is actually measuring
  (over/under-estimation of an approaching car's speed). `resp` is now
  `estimate - true_target_speed` per trial (parsed from the item name),
  preserving the same within-item ordinal direction (higher = greater
  overestimation) while tying the response to accuracy rather than a
  free-floating magnitude judgment. `data/klatt_2016_speed_estimation.py`
  updated in place; N/item count unchanged (60 ids, 48 items), resp range
  now -45 to 50 (signed error, km/h) instead of 10-100 (raw estimate).

Both fixes verified by re-running each script and diffing `biblio_plos_
batch23.csv`'s table list against `irw_output/*.csv` (28 tables, exact
match). No other batch-23 tables were affected.

## PLOS ONE batch 24 (2026-08-11)

**Term selection**: continued drawing from the recyclable non-PLOS English
term pool (`SKILL.md`'s method) instead of inventing new terms. Filtering
`search_terms_log.csv` to non-PLOS, not-yet-tried-on-PLOS rows and running
each candidate through `langdetect` (the previous ASCII-only filter had
let ASCII-safe non-English terms like "Angst"/"dolor"/"Antwortstil" through
undetected in earlier passes) gave a clean pool. 30 terms used this batch:
academic motivation, organisational citizenship behaviour, organizational
learning, sedentary behaviour, health behavior, relationship quality,
relationship commitment, school readiness, early literacy, heritage
culture, somatic symptoms, critical thinking, career maturity,
task-switching, sustained attention, reading self-concept, morphological
awareness, mathematical fluency, eating pathology, dissociative symptoms,
complicated grief, interoception, tic severity, selective mutism,
perfectionism, openness to experience, reactive aggression, hope theory,
emotional granularity, helicopter parenting. Logged in
`search_terms_log.csv`.

2,048 candidates -> 11 `good` + 319 `human_assistance` + 1,645
`no_usable_file` + 48 `not_item_response` + 14 `error` + 10
`download_failed` + 1 `crashed`. Retriage (`irw_retriage_ha.py`) on the
`human_assistance` bucket gave 41 `worth_retrying` + 103 `human_review` +
112 `aggregate_continuous` + 63 `not_item_response`.

Before review, the combined `good`+`worth_retrying` pool (52 rows) was
checked against `BATCH_LOG.md` for DOIs already decided in earlier
batches -- 9 duplicates found (all previously skipped as composite-only or
not-a-fit: `0253906`, `0249033`, `0201698`, `0253779`, `0277516`,
`0304132`, `0262465`, `0302350`, `0294151`), leaving 43 fresh candidates
(7 good + 36 worth_retrying). Split into 3 groups of ~14-15 and reviewed
in parallel, same method as batch 23: full article text + all Supporting
Information files fetched and inspected per candidate, not just the file
the automated triage pass opened; license/N>=50/no-single-item/raw-vs-
composite checks applied throughout.

**12 papers -> 28 tables shipped, all CC BY 4.0:**

Group A (4 papers -> 18 tables):
- `liem_2024_customer_pressure`/`_env_mgmt_acct`/`_attitude_env`/
  `_green_competitive_adv`/`_perceived_benefit_ema`/`_cleaner_production`/
  `_perceived_benefit_cp` (7 tables, `10.1371/journal.pone.0306616`, N=234
  Vietnamese manufacturing managers, 1-5 Likert across 7 constructs).
- `ravenscroft_2017_transition` (`10.1371/journal.pone.0179904`, N=306
  parents across 8 EU countries, 25 ordinal 1-5 items the paper itself
  analyzed as one PCA battery; non-comparable checkbox/categorical fields
  in the same file dropped).
- `mohammed_2021_patient_safety_culture` (42-item HSOPSC, 1-5) and
  `mohammed_2021_job_satisfaction` (5-item companion scale)
  (`10.1371/journal.pone.0245966`, N=411 Ethiopian health care
  professionals; derived composite dimension scores in the same file
  excluded).
- `li_2025_marketing_exploration`/`_exploitation`/`_culture`/`_learning`/
  `_operation`/`_corporate_performance`/`_market_environment`/
  `_policy_environment` (8 tables, `10.1371/journal.pone.0326329`, N=352
  individuals at 47 Chinese heritage-brand firms, 7-point Likert). QC
  catch: Policy Environment items (PE2-PE5) had non-integer values, some
  exceeding the stated 1-7 max (e.g. PE2=7.35) -- a multiplicative
  artifact affecting ~11% of rows -- filtered to integer 1-7 values only
  rather than guessing the multiplier.

Group B (3 papers -> 4 tables):
- `mascherini_2021_meddiet` (`10.1371/journal.pone.0252395`, N=1383,
  11-item Med Diet Score food-frequency scale, 0-5, two waves pre/during
  Italian COVID lockdown; the same file's PGWBI-A wellbeing scale was
  subscale-composite-only, excluded).
- `rivero_2022_piccolo_mother`/`_father` (`10.1371/journal.pone.0266762`,
  N=155 each, 29-item PICCOLO observational parenting checklist, 0-2,
  separate mother/father raters on the same children).
- `binette_2022_extinction` (`10.1371/journal.pone.0264797`, N=63 rats,
  42-item trial/block-level freezing measure, 0-100 continuous). Two
  strain sheets (Long-Evans N=31, Wistar N=32) individually fell below
  N=50; merged into one file with `cov_strain` and an id offset since both
  share an identical core 3-phase design -- non-human subjects evaluated
  purely on structural fit per `SKILL.md`'s standing rule, not excluded
  for being rats.

Group C (5 papers -> 6 tables):
- `albeitawi_2025_preceptor_needs` (`10.1371/journal.pone.0337101`, N=400
  Jordanian clinical educators, 7-item 4-point priority-rating scale).
- `zou_2025_critical_thinking` (70-item Critical Thinking Disposition
  Inventory, 7-pt) and `zou_2025_task_difficulty` (5-item difficulty
  scale, `wave`=1-3 across 3 writing tasks) (`10.1371/journal.pone.0324486`,
  N=201 college students).
- `szameitat_2015_multitask_examples` (43-item, -3 to 3, "is this an
  example of multitasking") and `szameitat_2015_occupation_multitask`
  (15-item, 0-6, multitasking demand per occupation)
  (`10.1371/journal.pone.0140371`, N=366/347).
- `corti_2023_academic_adaptation` (`10.1371/journal.pone.0294440`, N=953
  Spanish university students, 7-item academic-adaptation Likert scale).

**23 papers skipped**, one line each: `0279255` (value-added scores --
pre-computed VA quartile rankings/imputation notebooks, not raw items),
`0325183` (eye-tracking cerebral palsy, N=30, below N>=50), `0349399`
(EFL linguistic complexity -- columns are computed linguistic indices per
essay, not item responses), `0246449` (ADHD cognitive training follow-up
-- only subscale totals at each timepoint, also N=49), `0212482` (PA
brain breaks -- only derived cognitive composite scores), `0282137`
(IPAQ validity/asthma -- only IPAQ-derived aggregate MET-minute
variables, not the 8 raw items), `0224254` (EI training RCT -- only
EQ-i/STEU/STEM subscale/total scores), `0280758` (CEO narcissism -- firm-
year archival/constructed data, no legitimate id/item/resp mapping),
`0311369` (ESG/TFP manufacturing policy -- firm-year archival financial
panel, not survey items), `0225669` (business process improvement --
real Phase-2 Likert data exists but every item value is a suspicious
long-decimal average, e.g. 4.904761904761905, consistent with an already-
aggregated score not a raw rating; Phase-1 data separately N=22), `0271030`
(demoralization -- only 3 mean scale scores per subject), `0321373`
(anxiety/depression/Big Five -- only scale totals), `0177765` (GPAQ vs
SenseWear -- only derived MET-minute summaries, raw GPAQ items not
provided), `0199605` (retirement time use -- only composite totals and
pre-aggregated time-use hours), `0224159` (romantic attachment -- only
composite scores), `0200129` (perimenopausal quality of health -- only
subscale-level composite scores), `0278201` (fWHR/personality -- only
16PF's already-scored factor scores), `0139930` (abacus training -- only
condition-averaged accuracy/RT, not raw trial-level data), `0177398`
(story time/cerebellar activation, N=22, below N>=50), `0317077` (biology
exam questions -- item-attribute coding of questions, no examinees, not
a person-item table), `0341317` (AI MCQ Bloom's -- rater-coded scores of
questions, not people), `0230495` (conservation causal models --
study-level literature coding of ~1,027 papers, not person-item data),
`0207589` (anti-saccades/Parkinson's -- every column already a per-subject
aggregate, no raw trial/item data), `0286787` (OSCE nursing -- opaque
uncoded variable names, no accessible codebook, Dryad link 404s, >=3
instruments bundled with inconsistent naming -- flagged for human
follow-up rather than guessed), `0216149` (executive functions structure
-- confirmed composite-only across all 8 tasks), `0187098` (sleep
deprivation/divided attention -- composite-only per-condition metrics),
`0150435` (DAOA/schizophrenia -- only genotyping data shared, no
neurocognitive battery in SI despite being described in Methods),
`0284383` (CAM/homeopathy beliefs -- every substantive column a
pre-computed mean/sum score).

**2 candidates in the N=50-99 borderline band, not shipped, no
ben-domingue decision yet**: `0335166` (nursing literacy practices,
Karolinska -- N=67, 10 closed ordinal 1-4 items on note-taking practices
found in a secondary "Original dataset for analysis" sheet after the
primary WebFetch summary missed it); `0229591` (early visual language/
deaf children -- analytic-sample N=56, subset of a larger 254-row
multi-wave file with partly opaque item codes mixed with already-scored
subtest scores).

**1 candidate skipped on both N and format grounds**: `0173584` (Socratic
dialog effectiveness) -- N=81 (borderline) and raw per-problem responses
are open-ended qualitative strategy descriptions, not numeric; would need
a scoring rubric applied first even if N were resolved.

All license checks CC BY 4.0 confirmed on the article page. Files: 11
scripts in `data/` (`liem_2024_env_stewardship.py`,
`ravenscroft_2017_transition.py`, `mohammed_2021_patient_safety.py`,
`li_2025_marketing_capability.py`, `mascherini_2021_meddiet.py`,
`rivero_2022_piccolo_mother.py`, `rivero_2022_piccolo_father.py`,
`binette_2022_extinction.py`, `albeitawi_2025_preceptor_needs.py`,
`zou_2025_critical_thinking.py` -- produces both `zou_2025_*` tables --
`szameitat_2015_multitask.py` -- produces both `szameitat_2015_*` tables
-- and `corti_2023_academic_adaptation.py`), 28 CSVs in `irw_output/`,
`biblio_plos_batch24.csv` (28 rows, merged from
`biblio_plos_batch24_group{A,B,C}.csv`).

`human_review_plos_batch24.csv` (103 rows, from `irw_retriage_ha.py`)
staged for the "Human eye" sheet.

## PLOS ONE batch 25 (2026-08-11)

Discovery run: 30 recycled non-PLOS English terms (health behaviour,
physical fitness, creative thinking, career exploration, processing
speed, oral reading fluency, print awareness, text comprehension,
mathematical reasoning, fraction knowledge, emotion dysregulation,
proactive aggression, basic psychological needs, ambivalence over
emotional expression, scientific reasoning, fake news discernment,
overprotective parenting, authoritative parenting, harsh parenting,
fathering, sibling relationship, family cohesion, academic help-seeking,
academic cheating, cooperative learning, teacher-student relationship,
thriving at work, work meaningfulness, turnover intention, ethical
leadership), pulled from the `TODO.md` recyclable-terms pool per the
usual method (filter `search_terms_log.csv` to non-PLOS English rows not
yet tried against PLOS, `langdetect`-checked, hand-filtered for clean
instrument/construct names). All 30 logged to `search_terms_log.csv`.

`irw_discover_plos.py` result: 1,650 candidates -> 6 `good` + 278
`human_assistance` (+ 1,281 `no_usable_file`, 48 `not_item_response`, 13
`error`, 12 `download_failed`, 1 `timeout`). `irw_retriage_ha.py` on the
`human_assistance` bucket: 41 `worth_retrying`, 87 `human_review`, 84
`aggregate_continuous`, 66 `not_item_response`.

**`good` review (6 candidates)**: 2 below N>=50 dropped immediately
(`0253779` altered-states flicker N=24, `0243811` songbird vocal
preference N=12). `0201698` (positive/negative affect, Spanish children)
inspected and skipped -- all substantive columns (PA, SPdict/PRdict/
FRdict/HDdict) are pre-computed composite/dichotomized scores, no raw
items despite a header-offset read initially suggesting otherwise. 3
shipped: `grandahl_2017_hpv_beliefs` (15-item 6-point HPV-belief scale,
Swedish adolescents, N=753 -> 731 after "Do not know" treated as
non-response per datastandard.md), `zhu_2026_llm_meteorology_performance`
(5-item 1-5 LLM-performance rating, meteorology grad students, N=348),
`tsai_2017_treeit` (older-adults' TAM + Zhang et al.'s 14 usability
heuristics for a social platform UI, N=101 -- 17 separate tables: TAM
PU/PEOU/BI plus H1-H14, each heuristic named and item-counted directly
from the paper's Methods text since the raw column groups (H1-1..H1-6
etc.) needed the article to disambiguate exact per-heuristic item counts
correctly -- an initial guess at the split was wrong on 4 of the 14 and
caught by a KeyError before any output was saved).

**`worth_retrying` review (41 rows)**: 21 were exact-DOI duplicates of
candidates already decided (skipped, mostly composite-only) in earlier
batches (6/8/9/10/15/16/18/19/24) -- not re-reviewed, matches the
established batches-6/9/12/13/16/18 pattern of the same PLOS articles
resurfacing under different search terms. Of the 20 genuinely new DOIs:
3 ruled out from the title/caption alone without downloading (`0133213`
seabird recruitment sample-size table, not participant data; `0311564`
scoping-review data-extraction table; `0258200` firm-year archival R&D
panel, not survey items). Of the remaining 17 downloaded and inspected:
4 shipped (`han_2015_peer_assisted_learning`: 12-item 1-5 course
evaluation, N=205; `he_2019_flipped_classroom_attitudes`/`_satisfaction`:
12-item/8-item 1-5 scales from a pharmacy-education RCT, N=137, "9" =
not-applicable sentinel filtered; `theobald_2017_group_dynamics`:
2-item 1-6 comfort/dominator perception scale with `wave`=Topic (3
group-work rounds), N=684); 9 skipped as composite/aggregate-only or
otherwise not item-response (`0334111` aging/rural — IADL/GDS/SWEMWBS are
pre-scored totals; `0244603` and `0270999` preschool/referee fitness —
heterogeneous-unit physical test batteries, not a coherent item scale;
`0334232` facial-expression-engagement — correlation/results tables only;
`0339378` ADHD Delphi priorities — a variable dictionary, not response
data; `0351407` tDCS post-COVID — composite clinical characteristics,
N=55; `0240843` UDAYA India adolescents — all columns are derived survey
indices/covariates, no raw item battery; `0283117` children's friendship
nominations — sociometric structure too far from id/item/resp to fit
without a deeper look; `0157447` STEM-pipeline confidence — huge messy
multi-institution survey with no clear person-ID column, deferred rather
than guessed); 4 deferred, not shipped this pass (see TODO.md): `0242967`
counterfactual-reasoning task (N=54, real per-trial correctness data, but
in the 50-99 borderline band -- needs ben-domingue's decision per
`feedback_min_sample_size`); `0151634` music-listening ESM study (N=967,
1502 observations, but "goals"/"effects" columns are 1-10 rankings across
6 goal categories per observation -- structure needs more time to map
correctly, not rushed); `0138269` sentence-comprehension reading task
(item values are response-time-derived scores divided by syllable count,
not Likert responses -- `rt`-column semantics unclear, deferred);
`0329483` Arabic-language artistic-skills/academic-engagement
questionnaire (N=102, real ~26-item 1-5 Likert data, CC BY 4.0, but item
labels are in Arabic and need translation before shipping -- deferred).

**Result**: 6 papers -> 23 tables (`biblio_plos_batch25.csv`, 23 rows).
Scripts in `data/`: `grandahl_2017_hpv_beliefs.py`,
`zhu_2026_llm_meteorology_performance.py`, `tsai_2017_treeit.py` (17
tables), `han_2015_peer_assisted_learning.py`,
`he_2019_flipped_classroom.py` (2 tables), `theobald_2017_group_dynamics.py`.
`human_review_plos_batch25.csv` (87 rows, from `irw_retriage_ha.py`)
staged for the "Human eye" sheet.

## Europe-PMC connector batch 1 (2026-08-12)

First real batch run of `irw_discover_pmc.py` (mode 2), the new
Europe-PMC-based multi-journal connector added this session (see
`journal_scout/journal_yield_summary.md` for how the 11-journal
`JOURNALS` list was chosen, and the SKILL.md "Europe-PMC-based
multi-journal search" section for how the connector works).

**Term selection**: recycled 10 terms already validated against PLOS ONE
from `search_terms_log.csv` (per the "Term selection" rule in that mode's
SKILL.md section — a term proven to surface real candidates elsewhere is
worth trying on a new search surface before inventing new ones): Rosenberg
self-esteem scale, Perceived Stress Scale, Satisfaction with Life Scale,
Ten Item Personality Inventory, State-Trait Anxiety Inventory, Pittsburgh
Sleep Quality Index, Raven's Progressive Matrices, Self-Compassion Scale,
PANAS, Strengths and Difficulties Questionnaire. Run against all 11
journals in `JOURNALS` (PLOS excluded by design — stays on
`irw_discover_plos.py`).

**Result**: 888 candidates processed (`pmc_batch1_triage.csv`), 0
crashed/timeout. Flags: 466 `no_usable_file`, 274 `license_restricted`,
117 `human_assistance`, 13 `not_item_response`, 7 `good`, 6 `error`, 4
`download_failed`, 1 `file_too_large`. Two journals (Multivariate
Behavioral Research, Applied Psychological Measurement) returned zero
candidates for these terms — consistent with `journal_scout`'s finding
that both are very low-volume in Europe PMC, not a bug. PeerJ's `good`
rate (5/160 ≈ 3.1%) came in well above the ~1% PLOS ONE baseline, matching
`journal_scout`'s prediction that PeerJ would outperform PLOS ONE on
data-like supplementary yield.

**Manual review of all 7 `good` candidates** (a `good` flag here needs a
human glance more than usual — same caution as the PLOS pipeline, since
`irw_discover_pmc.py` also only inspects the first tabular file in the
archive, not the whole manifest):

- **Rejected, false positive — PCIQ-F** (`10.1186/s12874-021-01376-w`,
  bmcmrm): the auto-picked file is an item-development/face-validity
  review table (panel clarity/importance ratings + an editorial "decision
  taken" column like "Rewritten"), not respondent-level item responses.
- **Rejected, false positive — cannabis anxiety/depression**
  (`10.7717/peerj.2782`, peerj): despite the title, the auto-picked file
  is a substance-use/exclusion-screening form (caffeine/alcohol/
  tobacco/cannabis use in the last 8/24h, psychiatric history) — not the
  actual anxiety/depression scale. No other tabular file exists in the
  archive to recover the real scale data from.
- **Shipped as-is (2)**: PANAS fibromyalgia and Maslach Burnout
  Inventory-Student Survey — both clean single-instrument files, no
  covariate/item mixups.
- **Shipped after manual re-work (3 papers -> 9 tables)**: Hospice
  Comfort Questionnaire (auto-picked file was a strict subset of a richer
  file with 12 additional covariates — used the richer one instead);
  Cloninger personality study (one file bundled 4 distinct instruments —
  TCI, SWLS, PANAS, a Social Support scale — split into 4 tables per
  datastandard.md's one-scale-per-file rule); spinal cord injury QoL (one
  file bundled WHOQOL-BREF + SWLS + 13 demographic/clinical covariates the
  auto-triage had counted as items — split into 2 tables, covariates moved
  out). All three needed the file/column-level review that `good` alone
  doesn't guarantee — see each script's QC-note comment for specifics.

Every response scale was verified per-item (not merged min/max) with no
values isolated to a single item, and confirmed as pure integers (no
imputation artifacts) before shipping. License confirmed CC BY 4.0 on all
5 papers via Europe PMC's own `license` field (not scraped HTML).

**Result: 5 papers -> 11 tables** (`biblio_pmc_batch1.csv`, 11 rows), all
CC BY 4.0, all N>=189. Scripts in `data/`: `estevezlopez_2016_panas.py`,
`lopezgomez_2025_mbi_ss.py` (3 tables), `xu_2025_hcq_p.py`,
`lee_2024_cloninger.py` (4 tables), `altahla_2024_sci_qol.py` (2 tables).

### PMC connector batch 1 — retriage of the 117 `human_assistance` rows (2026-08-12)

`pmc_batch1_triage.csv` was deleted after the `good` rows above were
captured, per the normal end-of-batch cleanup — but that meant its 117
`human_assistance` rows never got the `irw_retriage_ha.py` (Step 2b) pass
the PLOS pipeline does routinely. Regenerated the triage CSV by rerunning
the same 10 terms from batch 1 (887 candidates this time vs 888 — one row
came back `timeout` instead of clean, otherwise an exact match including
the same 7 `good` hits) and ran `irw_retriage_ha.py` on it.

**Retriage result** (117 rows): 20 `not_item_response` (drop), 33
`aggregate_continuous` (drop), 33 `human_review` (genuinely ambiguous —
written to `human_review_pmc_batch1.csv`, staged for the "Human eye"
sheet), 31 `worth_retrying` (plausible data worth a second look — see
open `TODO.md` item). 31/888 ≈ 3.5%, in line with the ~2-4% additional
yield this step recovers on PLOS batches.

### PMC connector batch 2 + PLOS ONE batch 26 (2026-08-12)

Two more discovery runs kicked off in parallel — Europe PMC (mode 2) and
PLOS (mode 1) hit different domains (`www.ebi.ac.uk` vs
`api.plos.org`/`journals.plos.org`), so `polite_get`'s per-domain rate
limiter doesn't create any contention between them.

- **PMC connector batch 2** (`pmc_batch2_triage.csv`): 10 more terms
  recycled from the PLOS-validated pool in `search_terms_log.csv`:
  Warwick-Edinburgh Mental Wellbeing Scale, Yale Food Addiction Scale,
  Yale-Brown Obsessive Compulsive Scale, Wisconsin Card Sorting Task,
  Zimbardo Time Perspective Inventory, body image, attachment style,
  burnout, alexithymia, career decision making. Run against all 11
  `JOURNALS`.
- **PLOS ONE batch 26** (`plos_batch26_triage.csv`): 10 terms recycled
  from the repo-connector-validated pool (not yet run against PLOS):
  UCLA Loneliness Scale, resilience scale, narcissism scale, gratitude
  scale, mindfulness scale, rumination scale, empathy scale, aggression
  scale, creativity scale, religiosity scale. Run against
  `plosone,mentalhealth,globalpublichealth`.

### PLOS ONE batch 26 — result (2026-08-12)

497 candidates processed. Flags: 381 `no_usable_file`, 107
`human_assistance`, 6 `not_item_response`, 1 `error`, 1 `download_failed`,
1 `good`.

**The 1 `good` candidate was reviewed and skipped, not shipped**:
"Mental health in gay, lesbian and bisexual medical students"
(`10.1371/journal.pmen.0000108`, PLOS Mental Health, N=404). The
supplementary file has a literal `Endereço de e-mail` (Portuguese for
"Email address") column — real participant emails attached to detailed
psychological data (Beck Depression Inventory, STAI, an internalized-
homophobia/sexual-identity scale, a resilience scale, a QoL scale) for a
small, narrow population (LGB medical students, likely one institution).
A hard PII violation under `datastandard.md`'s checklist regardless of the
paper's own CC BY license, and the combination of identity + mental-health
data + a narrow population is a re-identification risk that goes beyond
"just drop the email column" — skipped entirely per ben-domingue's
decision (2026-08-12), not processed further. (Also, independent of the
PII issue: the file bundles ~6 distinct instruments across 206 columns
with conditional gay/lesbian-vs-bisexual branching, so this would have
been a substantial multi-table split even without the PII problem.)

107 `human_assistance` rows not yet retriaged (open item, see `TODO.md`).

Both this batch and PMC connector batch 2 (previous entry) hit different
domains, confirmed no rate-limit contention running concurrently.

### PMC connector batch 2 — result (2026-08-12)

412 candidates processed. Flags: 234 `no_usable_file`, 126
`license_restricted`, 43 `human_assistance`, 6 `not_item_response`, 2
`good`, 1 `download_failed`.

**New standing policy, decided this batch**: any PII in a raw source file
now means skip the whole candidate, not scrub-and-ship the offending
column. See the new hard rule in this file's SKILL.md Step 4 and
`feedback_pii_skip_entirely` in auto-memory. Applied to both `good`
candidates below:

- **Skipped — nursing profession social-representation survey**
  (`10.7717/peerj.13903`, peerj, N=141, 48 items): raw file has a real
  `date of birth` column (actual birthdates, e.g. `1995-05-04`, not just
  birth years) plus a couple of open-text "please specify who" columns.
  On its own this would have been a routine fix (drop the DOB column, ship
  the rest — the 48 opinion items themselves are not sensitive), but per
  the new blanket policy it's skipped outright rather than re-litigated as
  "low severity."
- **Shipped — AI computing leasing adoption survey**
  (`10.1016/j.heliyon.2024.e36620`, heliyon, N=281): clean, no PII,
  sequential `NO` id. 18 items split into 6 three-item constructs
  (innovation, risk, performance expectancy, price value,
  task-technology fit, usage), 1-7 scale, matching the `multi_scale*`
  flag. See `data/` script below for the split.

**Result: 1 paper -> 6 tables** (`biblio_pmc_batch2.csv`, 6 rows). Script:
`data/sun_2024_ai_leasing_adoption.py`.

### Human review sheet deprecated (2026-08-12)

The old queue Google Sheet's "human eye" tab (and, along with it, the
sibling "to be processed" tab this pipeline never used) is deprecated —
it had grown to ~4,846 rows and become unmanageable to review. Decided
by ben-domingue.

Replacement: `human_review/` in this repo now holds one permanent,
git-tracked CSV per batch (`human_review_<mode>_batch<N>.csv`, e.g. the
existing `human_review_pmc_batch1.csv`) instead of rows staged for
pasting into the sheet. These files are never deleted — same standing-
record treatment as `license_blocked_candidates.csv` and
`search_terms_log.csv`. Only rows whose `flag`/`refined_flag` is
literally `human_review` go here; `worth_retrying`/`recoverable_format`/
`wrong_file_selected`/etc. rows still need machine follow-up and continue
to be tracked as open `TODO.md` items with their own retriage CSV on disk,
unchanged from prior practice.

The old sheet's "human eye" tab was exported once to
`human_review/googlesheet_humaneye.csv` (4,846 rows) as a frozen
historical snapshot before being retired.

`irw_discover_updated.py`'s `_load_auto_exclusions()` now also reads every
`doi` column across `human_review/*.csv` and excludes those DOIs from new
discovery runs, on top of the existing IRW-dictionary exclusion — so a
candidate a person already reviewed and passed on won't resurface in a
later batch. `irw_discover_plos.py` and `irw_discover_pmc.py` share this
function, so the exclusion applies to all three discovery modes.
`.gitignore`'s blanket `human_review_*.csv` rule (previously treating
these as regenerable per-batch temp output) was removed so the folder can
actually be tracked in git.

Updated: `SKILL.md`, `README.md`, `.gitignore`, `irw_discover_updated.py`,
`irw_process_queue.py` (docstring note only, already stale/not run),
`TODO.md` (resolved the one open "needs pasting" item for
`human_review_pmc_batch1.csv`).

43 `human_assistance` rows not yet retriaged (open item, see `TODO.md`).

### worth_retrying review — pmc1/plos26/pmc2 (2026-08-12)

Retriaged the two leftover `human_assistance` triage files
(`plos_batch26_triage.csv` 107 rows, `pmc_batch2_triage.csv` 43 rows) with
`irw_retriage_ha.py`: PLOS batch 26 -> 41 `human_review` (written to
`human_review/human_review_plos_batch26.csv`), 32 `aggregate_continuous`,
23 `not_item_response` (both dropped), 11 `worth_retrying`. PMC batch 2 ->
19 `human_review` (written to `human_review/human_review_pmc_batch2.csv`),
11 `aggregate_continuous`, 6 `not_item_response` (dropped), 7
`worth_retrying`.

Then reviewed all `worth_retrying` rows across all three sources
(pmc_batch1_retriage.csv 31 + plos26 11 + pmc2 7 = 49 rows, 45 unique DOIs
after 4 overlaps between pmc1/pmc2) by re-downloading each candidate's raw
file and running it through `coerce_to_irw()`/inspecting the actual
category values — the retriage heuristic's `reasons` string is a
classification signal, not a verified verdict, and this pass found it
wrong in both directions: several `worth_retrying` rows turned out to be
aggregate/composite data (not raw items) mis-triaged as recoverable, and
conversely `10.7717/peerj.18225` had genuine raw GAD-7/PHQ-9 items sitting
in the file that `coerce_to_irw()`'s column-detection simply missed
entirely (worth flagging: this heuristic gap likely affects other
`worth_retrying`/`human_review` rows too, not just this one candidate).

**Shipped: 3 papers -> 8 tables** (`biblio_pmc_batch3.csv`):
- `10.7717/peerj.20868` (Han et al. 2026, insomnia/anxiety/depression
  network analysis in elderly Jiangsu Province adults, N=2086, CC BY 4.0)
  -> `han_2026_gad7`, `han_2026_phq9`, `han_2026_isi`. Two earlier SI
  files (s001/s002.xlsx) held a messier alternate insomnia/depression item
  set (one insomnia item was a malformed comma-concatenated 3-value
  string); s006.xlsx was used instead — clean, complete, codebook-matching
  raw GAD-7/PHQ-9/ISI-7 items plus pre-computed `*_Score` totals (excluded
  as aggregates). ISI items are internally consistent 5-point scales but
  vary item-to-item between 0-4 and 1-5 coding — permitted per
  datastandard.md since direction/range only needs to be consistent
  *within* each item.
- `10.7717/peerj.16375` (Valdivia Ramos et al. 2023, Mexican OMS-HC stigma
  scale, N=556, CC BY 4.0) -> `valdivia_2023_oms`. 15 items, 5-category
  text Likert recoded 1-5; no raw id column, row index used.
- `10.7717/peerj.7369` (Gea-Caballero et al. 2019, PES-NWI short-form
  validation, N=269, CC BY 4.0) -> `geacaballero_2019_pes_nwi` (30-item
  4-point Likert) + `geacaballero_2019_pes_nwi_short` (31-item yes/no
  short-form being validated against it) — one file bundled two parallel
  item sets over the same constructs, split per datastandard.md's "one
  file per scale" rule. A couple of Likert categories had raw typos
  ("alsolutely disagree", "absolutely disagree.") normalized before
  mapping.
- `10.7717/peerj.18225` (Shu et al. 2024, adolescent family/school status
  and depression/suicidal-ideation study, N=1190, CC BY 4.0) ->
  `shu_2024_gad7`, `shu_2024_phq9`. The retriage heuristic flagged this as
  `worth_retrying` on a "low-confidence id" reason and only surfaced 6
  guessed item columns (all non-instrument covariates) — the raw
  GAD1-7/PHQ1-9 columns were sitting right there in the file, just missed
  by `coerce_to_irw()`'s automatic item detection. `id` = `number`
  (verified unique). A couple of categories had trailing-period typos
  ("Not at all.") normalized before mapping.

**Skipped (27 of 45, not real per-item response data or below the min
sample floor)** — grouped by reason:
- *Aggregate/composite scores mistaken for raw items* (the column names
  matched a known instrument but held pre-computed subscale/scale totals,
  not per-item responses): `10.7717/peerj.3928` (LADA QoL — also had a
  nonsense id column, `BMI`), `10.7717/peerj.10752` (MEIM), `10.7717/peerj.14240`
  (postpartum depression/QoL), `10.7717/peerj.2978` (dental anxiety — id
  fallback was `age`), `10.7717/peerj.17308` (magic-watching wellbeing —
  id fallback was `Duration`), `10.1371/journal.pone.0233831` (SCL-90,
  Chinese subscale names not items), `10.1371/journal.pone.0196718` (pain
  burden HIV, Portuguese scale totals), `10.1371/journal.pone.0239002`
  (3-wave subscale totals across 5 named scales), `10.1371/journal.pone.0234997`
  (baseline/follow-up scale totals), `10.1371/journal.pone.0284383`
  (construct-level composite scores).
- *Not survey/item-response data at all* (mis-triaged structural false
  positives): `10.1186/s12889-020-09058-w` (a demographic stats-summary
  table), `10.1038/s41598-025-33041-3` (a correlation matrix),
  `10.1371/journal.pone.0269327` (a factor-model fit-index table),
  `10.1186/s12889-025-25237-z` (a measurement-invariance fit table),
  `10.1371/journal.pmen.0000333` (a participation-count table),
  `10.1371/journal.pgph.0003340` (a literature-search log),
  `10.1371/journal.pone.0152462` (clickstream/action-log data, 135k rows),
  `10.7717/peerj.19587` (a family demographic table, no instrument),
  `10.1038/s41598-025-12221-1` (business-type summary counts).
- *Wrong file / not usable as shared*: `10.7717/peerj.18378` (the SI file
  was a data dictionary/codebook, not the data itself; no other file
  available).
- *Structurally real but not a coherent human item-response battery*:
  `10.7717/peerj.16617` (hormone assay values mixed with genotype codes),
  `10.7717/peerj.17468` (AI-chatbot vignette ratings with inconsistent,
  non-comparable per-column scale ranges — not a human Likert battery),
  `10.7717/peerj.18676` (n_id=2 after melt — aggregated rater-level data,
  not per-respondent), `10.7717/peerj.14730` (sheep attention-bias study —
  legitimate animal behavioral data per this pipeline's non-human policy,
  but the "items" are heterogeneous non-comparable metrics — times,
  counts, binary flags — not one coherent scale).
- *Too messy to be worth the decode time this pass*: `10.7717/peerj.15582`
  (leishmaniasis study — every text category has inconsistent typos:
  "stronglly agree", "disagrree", "netural").
- *Below the min-sample floor*: `10.7717/peerj.21309` (epilepsy QoL,
  N=32 — see `feedback_min_sample_size`).

**Deferred (14 of 45)**: genuinely promising, real item batteries that
need more work than this pass had time for — a paper-text check, a
multi-scale split, a wave-aware script, non-English translation, or (for
two) a ben-domingue N=50-99 call. Written to the new standing file
`pmc_deferred_candidates.csv` (same treatment as `plos_deferred_candidates.csv`
— never delete). Full list with reasons is in the file; see `TODO.md` for
the summary.

One fetch failure (`10.7717/peerj.2319`, Europe PMC timeout) is included
in the deferred count — needs a retry, not a data problem.

Cleaned up: `pmc_batch1_triage.csv`/`pmc_batch1_retriage.csv`,
`plos_batch26_triage.csv`/`_retriage.csv`, `pmc_batch2_triage.csv`/`_retriage.csv`
all deleted — every actionable row is now in `human_review/`,
`irw_output/`+`biblio_pmc_batch3.csv`, `pmc_deferred_candidates.csv`, or
this entry.

### Sample-size floor tightened: N<50-99 ask -> N<100 skip outright (2026-08-12)

Ben-domingue simplified `feedback_min_sample_size`: the old rule ("N<50
skip, N 50-99 ask ben-domingue first") is now "N<100 skip outright, no
asking required." Applied for the first time in the next entry (the 14
deferred-candidate resolution), which is why two of that batch's N=50-99
candidates were skipped without a go/no-go question.

### Resolution of the 14 deferred PMC candidates (2026-08-12)

Worked through every row in `pmc_deferred_candidates.csv` (open since the
"worth_retrying review — pmc1/plos26/pmc2" entry above) — read each
paper's full text, re-fetched raw files via Europe PMC's
`supplementaryFiles` endpoint (PLOS's own SI listing for the one PLOS ONE
row), and either wrote a bespoke `data/*.py` script or logged a skip
reason. Full column reads (not just triage-heuristic-sampled columns)
were done for every candidate per the deferral notes' own instructions.

**Shipped: 9 papers -> 30 tables** (`biblio_pmc_deferred.csv`, 30 rows,
all CC BY 4.0, confirmed per-paper via Europe PMC's `license` field or
the article's own CC BY notice):

- `10.7717/peerj.18809` (Galgam et al. 2025, WHOQOL-BREF among African
  medical/health science students, N=349) -> `galgam_2025_whoqol_bref`.
  26-item scale with 4 different response-wording families (poor-good,
  satisfaction, amount/degree, frequency) all sharing an internal 1-5
  leading-digit code; items 1-2 lacked the leading digit and were mapped
  from the supplementary codebook sheet instead.
- `10.7717/peerj.20153` (Burgess et al. 2025, SOAS anthropomorphism scale,
  N=120 children) -> `burgess_2025_soas`. The title's "6-item" scale is
  the *result* of the paper's own CFA-based item reduction from an
  original 13 -- Table 4's "Final factor loading" column identifies the
  surviving items (SOAS5/7/9/10/11/12) exactly; baseline + ~14-day retest
  shipped as 2 waves.
- `10.7717/peerj.15053` (Gizaw et al. 2023, 2-wave PHQ-9, Addis Ababa
  healthcare providers, N=577 observations) -> `gizaw_2023_phq9`. The
  deferred note assumed `hw_id` was a real cross-wave person key, but it
  fails datastandard.md's uniqueness check outright (collides across
  people with different ages even *within* one wave) -- shipped as row
  index id instead, i.e. two cross-sectional PHQ-9 samples rather than a
  linked panel.
- `10.7717/peerj.16184` (Agarwal et al. 2023, DREEM educational-
  environment scale, N=300) -> `agarwal_2023_dreem`. The deferred note's
  "24-item, 2-condition" guess didn't match the file at all -- full
  column read + paper text confirmed the real DREEM instrument (50 items,
  3 true waves: precovid/covid/postcovid). One source column-name typo
  (`q37precobid` for `precovid`) handled explicitly. precovid columns
  were text-labelled, covid/postcovid columns were the same underlying
  0-4 codes without SPSS labels attached -- verified identical coding
  scheme before merging.
- `10.7717/peerj.17265` (Abdullah et al. 2024, abdominal-bloating SEM
  study, N=323) -> 12 tables (`abdullah_2024_bsq_sevgen`/`_sev24`,
  `_hbbloat_attitude`/`_subjnorm`/`_pbc`, `_hpbbloat_diet`/`_awareness`/
  `_physact`/`_stress`/`_treat`, `_ssbloat`, `_blqol`). Full paper read
  confirmed 6 distinct named instruments (HB-Bloat's 3 subscales,
  HPB-Bloat's 5 subscales, BSQ-M's 2 subscales, SS-Bloat, BLQoL-M), each
  present in the file only as an item-reduced subset (e.g. HB-Bloat's
  13-item attitude subscale down to 3 retained columns) -- one file per
  subscale per datastandard.md. Two single-item constructs (I1
  "intention", P5, an isolated item with no paired code) excluded per the
  no-single-item-scale policy. Two isolated out-of-stated-range values
  (a single 6 on a 1-5 item in two different subscales) dropped as
  data-entry errors, not real anchors.
- `10.7717/peerj.16295` (Moon & Kim 2023, coping/self-esteem/pregnancy-
  stress among married immigrant pregnant women, N=206) -> 6 tables
  (`moon_2023_selfesteem`, `_korean_proficiency`, `_coping_problem`,
  `_coping_emotion`, `_spousal_support`, `_pregnancy_stress`). Note: the
  deferred CSV's title field for this DOI was simply wrong ("sports
  participation") -- verified the correct paper via full-text XML before
  proceeding. Full read found 5 scales, not the 3 the deferral note
  guessed at (self-esteem, Korean proficiency, stress-coping) --
  spousal-support and pregnancy-stress items were also present and
  shippable. `9` is a shared cross-scale missing-code sentinel (dropped);
  a `6` appearing exactly once per item across all 11 pregnancy-stress
  items (same respondent row each time, scale is confirmed 1-4 via the
  file's own value labels) dropped as a sentinel/entry error. Several
  items' text labels only exported for the first item per scale (an SPSS
  export quirk) -- mapped back to the same numeric codes as their
  sibling items.
- `10.7717/peerj.5756` (Cucchi, Hampton & Moulton-Perkins 2018, RFQ
  mentalizing study in eating disorders, N=229) -> 6 tables
  (`cucchi_2018_rfq`, `_scoff`, `_pts`, `_kims`, `_tas20`, `_rmet`). The
  deferred note had only inspected 25 of 162 columns; a full read found
  five more shippable raw-item instruments beyond RFQ that the note never
  saw (SCOFF, IRI Perspective-Taking, KIMS, TAS-20, RMET), while
  confirming RFQc/RFQu really are a nonlinearly-*recoded* (0-3)
  transformation of the raw RFQ1-8 items (not additional raw items) per
  the paper's own Table 2. RMET's raw `EYES1-36` selection codes are
  categorical (which of 4 words chosen), not ordinal, so the file's own
  per-item `correct`/`incorrect` scoring columns were shipped instead.
- `10.7717/peerj.9990` (Dalky et al. 2020, SF-36 among Syrian refugee
  women, N=523) -> `dalky_2020_sf36`. The file's `factor_1..36` and named
  subscale columns are the RAND 0-100 *transformed* scoring output;
  shipped the genuine raw SF-36 items instead, identified via each
  column's own SPSS value-label metadata (35 items: PF, role-physical,
  role-emotional, social functioning, pain, the combined vitality+mental-
  health 9-item block, general health perceptions, and the general-
  health/health-transition single items).
- `10.1371/journal.pone.0277247` (Mistry et al. 2022, loneliness among
  Bangladeshi older adults, N=2077, PLOS ONE) -> `mistry_2022_hardship`.
  8-item binary hardship/concern battery, confirmed consistently coded
  1=no/2=yes across all 8 items via the file's own Stata value labels.
  The paper's abstract confirms this is two *independent* cross-sectional
  survey rounds (1032 in 2020, 1045 in 2021), not a panel -- `round`
  shipped as a covariate, not `wave`. The single-item loneliness outcome
  (`lone`) kept as a covariate rather than its own file (no-single-item
  policy).

**Skipped (5 of 14)**:
- `10.7717/peerj.19326` (N=53) and `10.7717/peerj.12078` (N=99) -- skipped
  outright under the new N<100 floor (see previous entry). No
  ben-domingue go/no-go needed under the new rule; the Spanish-
  translation work `peerj.19326` would have needed was not done.
- `10.7717/peerj.2319` (N=50) -- the Europe PMC fetch that previously
  timed out succeeded on retry, but both SI files turned out to be
  "Distribution of the TCI subscales across subjects and specialties"
  tables -- pre-computed TCI (Temperament and Character Inventory)
  subscale scores, not raw items -- so this would have been an
  aggregate-only skip regardless of sample size; N=50 also fails the new
  floor independently.
- `10.7717/peerj.19403` (deferred CSV claimed N=591) -- the ZTPI/LPFS/PICD
  item batteries the deferral note flagged were real, but a full read
  found the file is mostly blank-padded rows: only 126 of 591 rows carry
  any data at all, and only 63 of those have the raw ZTPI items (LPFS and
  PICD are present only as pre-computed subscale totals, no raw items for
  either). The paper's own participant-count breakdown by education level
  sums to exactly 63 (2+8+31+9+13), confirming N=63 is the real usable
  sample, not 591. N=63<100 -> skip under the new floor.
- `10.1038/s41598-024-58598-3` (PBAT-1/2/3 EMA daily-diary study, N=113)
  -- skipped for PII, not scripted. The raw file has `LocationLatitude`/
  `LocationLongitude` columns populated for essentially every one of
  11,865 rows (488 unique locations clustering around Frankfurt,
  Germany) -- real GPS coordinates, a hard PII violation under the
  pipeline's blanket PII policy regardless of how clean the rest of the
  data (the VID/Session-ID id/wave structure the deferral note flagged)
  would otherwise have been.

`biblio_pmc_deferred.csv` (30 rows) is ready for ben-domingue to upload to
Redivis and paste into the dictionary sheet — standard pattern, not yet
confirmed done (see `TODO.md`). `pmc_deferred_candidates.csv` deleted —
every row is now accounted for above (shipped, skipped-and-logged, or, in
`peerj.2319`'s case, skipped after a successful retry showed the data
itself doesn't qualify).

## PMC weekly high-yield discovery+triage batch 3 (2026-08-12)

Scheduled routine run (`irw_discover_pmc_monthly.py --mode weekly`, PR #1612)
found 60 candidates across HIGH_YIELD_TERMS x JOURNALS (0/15 terms fully
covered before hitting `--limit=60`): 1 `good`, 30 `human_assistance`, 20
`no_usable_file`, 3 `not_item_response`, 3 `license_restricted`, 2
`download_failed`, 1 `error`. `irw_retriage_ha.py` sub-classified the 30
`human_assistance` rows: 10 `not_item_response`, 9 `aggregate_continuous`,
9 `worth_retrying`, 2 `human_review`.

**Shipped (18 tables, 6 papers, all CC BY 4.0, all N>=116):**
- `10.7717/peerj.18709` (Altahla et al. 2024, spinal-cord-injury QoL, the
  batch's one `good` row) -> `altahla_2024_whoqol` / `_swls`. The raw
  workbook's 4 sheets included a `GP` (healthy comparison, n=223) sheet
  the original triage never saw (only read the first sheet) -- combined
  with the SCI sheet (n=189) via `cov_group`, ids offset +100000 for GP.
  A 30-person test-retest subsample (`participants test`/`re test`
  sheets) was left unshipped -- its own 1-30 id numbering can't be
  reliably linked back to the main sample's ids.
- `10.7717/peerj.3034` (Alexander 2017, attachment/binge eating) ->
  `alexander_2017_dsi` / `_ecr`. Raw file had junk annotation rows
  ("*Differentiation of self(DSI)" etc.) mixed into the data rows and a
  non-unique `Subject code` -- dropped via numeric coercion, row index
  used as `id`. 4 more instruments in the same file (PA, EAS, Binge EA,
  Anti-fat) not processed this pass -- see TODO.md.
- `10.7717/peerj.16035` (Silva et al. 2023, ECOHIS) -> `silva_2023_ecohis`.
  13 raw items shipped; 4 composite/scoring columns (SCORE, ESRED,
  escoreF1/2) excluded -- these caused the original aggregate_continuous
  flag.
- `10.7717/peerj.4903` (Medvedev 2018, well-being constructs) ->
  `medvedev_2018_oxh` / `_ql` / `_sl` / `_pan` (Oxford Happiness, a QoL
  scale, SWLS, PANAS). Each item had a reverse-scored duplicate column
  (`OXH1R` = 7-`OXH1`, etc.) -- excluded per resp_direction*, only the
  as-recorded raw items shipped.
- `10.7717/peerj.17910` (Li et al. 2024, physique anxiety/food addiction)
  -> `li_2024_fa` / `_bdyz` / `_spa` / `_sad`. `_bdyz` genuinely only has
  4 of a presumably-longer body-image scale (items 1/2/6/9) in the raw
  file -- not a parsing error, confirmed by inspecting the raw columns
  directly.
- `10.7717/peerj.1464` (Lee et al. 2015, parental temperament) ->
  `lee_2015_cbcl` (100-item Korean CBCL only). The same file has a large
  multi-informant JTCI temperament battery (child/mother/father-report,
  7 subscales each, i-/m-/p- prefixed columns) that's genuinely
  recoverable item data but wasn't disentangled this pass -- needs the
  paper's Methods text to confirm subscale-abbreviation mapping per
  informant. See TODO.md.
- `10.7717/peerj.16295` (Moon et al. 2023, immigrant pregnant women) ->
  `moon_2023_selfesteem` / `_coping` / `_support` / `_pregstress`. The
  original "low-confidence id column" retriage flag was a false
  positive -- the raw .sav has an unambiguous `id` column. Each scale
  used `9` (support additionally had one non-integer `1.6`) as a
  sentinel for a handful of cells -- filtered by the scale's own
  observed valid range rather than a blanket dropna.

**Not recoverable (aggregate_continuous, confirmed composite/derived-only
by inspecting raw columns directly rather than re-guessing from the QC
heuristic):**
- `10.7717/peerj.5451` (oral health QoL, n=769) -- all 18 non-demographic
  columns are pre-computed clinical/composite indices (SOHO, senseofcoherence,
  locus, pufaindex, TDI, etc.), no raw item columns at all.
- `10.7717/peerj.4484` (temperament/character, n=72) -- TCI subscale
  export pattern (`_raw`/`_Miss`/`_cut` suffixes only), same
  pre-computed-subscale-only shape as the `peerj.2319` TCI case in the
  backlog-resolution entry above. No raw items.
- `10.7717/peerj.10904` (cardiovascular coping, n=42) -- mostly
  physiological/statistical derived columns; a genuine but marginal
  3-item x ~5-timepoint SAM (Self-Assessment Manikin) battery is present
  but not extracted this pass (small n, small item count, wave-structure
  verification needed) -- see TODO.md.
- `10.7717/peerj.13162` (maternal self-efficacy, Chilean adolescent
  mothers, n=79) -- genuinely recoverable (6 real subscales: selfreg,
  adaptivefunctioning, affect, socialcommunication, interaction,
  socialemotionaldevelopment, each with its own `_sum` composite to
  exclude) but not processed this pass given the number of subscales
  needing individual verification -- see TODO.md.

**`worth_retrying` (9 rows) disposition:**
- `10.7717/peerj.16295` -> processed, see above (4 tables).
- `10.7717/peerj.16617` (performance anxiety, hormonal) -- raw file is
  cortisol/progesterone/amylase assay values plus 3 single subscale-sum
  columns (Somatic/Worry/Concentration-Disruption items), no raw item
  columns. Skip.
- `10.7717/peerj.21309` (epilepsy QoL) -- raw file gives GAD-7/HDRS/
  QOLIE-10 only as single composite Score columns, not itemized. Skip.
- `10.7717/peerj.19326` (executive functioning QoL, Spanish, n=53) --
  SF-12 (12 items) and a 23-item scale (EPY) are genuinely present as
  named item columns, but stored as SPSS labeled-categorical values with
  no numeric code surviving `pd.to_numeric` -- needs the .sav's value
  labels decoded. N=53 also falls in the 50-99 ask-first band. Deferred
  to TODO.md pending both the decode and a ben-domingue go/no-go.
- `10.7717/peerj.19467` (Buteyko breathing, asthma) -- text-coded
  categorical responses (`rarely`/`mostly`/`sometimes`, etc.) with no
  confirmed ordinal order, and one item block (`YK1_F1` etc.) turned out
  to be free-text activity names, not scale responses. Skip pending the
  paper's response-key.
- `10.7717/peerj.4305` (postnatal depression) -- EPDS/DASS/BDI/PAI all
  given only as single composite Score columns; remaining columns are
  statistical dummy-coded variables. Skip.
- `10.7717/peerj.16864` (medical students, cognitive/affective) -- real
  text-Likert item columns (e.g. "Frequently"/"Sometimes"/"Rarely"/
  "Seldom") but "Rarely" vs "Seldom" have no confirmed relative order,
  and the same sheet mixes in an unrelated academic-integrity/bullying
  item block. Skip pending the paper's response key.
- `10.7717/peerj.18378` (parenting styles, NSSI) -- the .xlsx supplementary
  file is a 3-column codebook (Variable/Code/Description), not response
  data; the actual data is in a `.rar` archive not opened this pass.
  `wrong_file_selected`, not `worth_retrying` -- see TODO.md.
- `10.7717/peerj.17308` (magic and positive emotions) -- SWLS and other
  named scales present only as single composite-total columns (not
  itemized). Skip.

**2 `human_review` rows** (`10.7717/peerj.18167` e-cigarettes/dental
students, `10.7717/peerj.14128` children's temperament/injuries) written to
`human_review/human_review_pmc_batch3.csv` — permanent record, replacing
the deprecated "human eye" sheet.

**2 `download_failed` rows** (`10.7717/peerj.17440`, `10.7717/peerj.2421`)
are an environment bug, not a data problem — both are legacy `.xls` files
and the triage sandbox was missing `xlrd`. Worth a manual retry with
`pip install xlrd`. **1 `error` row** (`10.7717/peerj.18828`,
`'int' object has no attribute 'lower'`) is a real bug in
`irw_discover_pmc.py`'s triage logic, not yet fixed — see TODO.md.

`biblio_pmc_batch3.csv` (18 rows) is ready for ben-domingue to upload to
Redivis and paste into the dictionary sheet.
`pmc_monthly_candidates_weekly_2026-08-12.csv` and
`pmc_retriage_weekly_2026-08-12.csv` deleted — every row is now accounted
for above (shipped, skipped-and-logged, or deferred to TODO.md).

## Duplicate-processing incident: moon_2023 / peerj.16295 (2026-08-12)

`10.7717/peerj.16295` (PMC10629385, Moon & Kim 2023) was shipped twice
today via two uncoordinated pathways: the 11:30 "resolve 14 deferred PMC
candidates" pass (`data/moon_2023_pregnancy_stress.py`, 6 tables) and the
15:05 "PMC weekly batch 3" pass (`data/moon_2023_selfesteem.py`, 4
overlapping/lower-quality tables). Root cause: `pmc_seen_dois.csv` didn't
exist until the 14:17 weekly discovery run created it, so that run's fresh
search had nothing to exclude the DOI on, and the dictionary-based
exclusion only catches DOIs already uploaded to Redivis, not ones shipped
locally hours earlier. Both biblio CSVs got uploaded before the
duplication was noticed; ben-domingue resolved it directly on Redivis by
dropping the 4 tables from the newer (15:05) pass and keeping the 6-table
version from the deferred-candidate pass. Fix: Step 3 in SKILL.md now
requires grepping `data/*.py`
for the DOI before writing a new script, regardless of what
`pmc_seen_dois.csv` says. `data/moon_2023_selfesteem.py` deleted from the
repo as part of this cleanup.

## PLOS batch 27 worth_retrying manual review (2026-08-12)

Manually reviewed all 5 `worth_retrying` DOIs from PLOS ONE batch 27's
`irw_retriage_ha.py` output (fetched each article page plus every
Supporting Information file, not just the first tabular one). DOI dedup
checked first (`grep -rl "DOI: <doi>" data/*.py`) -- none previously
shipped.

**Shipped (3 papers, 7 tables):**
- `10.1371/journal.pone.0270974` (Wen 2022, PYD scale) -> two independent
  samples (S1 Data n=476, S2 Data n=471, no overlapping ids), 26-item
  Positive Youth Development scale, 1-5 Likert, clean. Data Availability
  files don't confirm a rural/urban correspondence for S1 vs S2, so files
  are named `wen_2022_pyd_s1`/`_s2` after the SI item rather than guessing
  a rural/urban label. Script: `data/wen_2022_pyd.py`.
- `10.1371/journal.pone.0246931` (Carus 2021, snowboard speed) -> thin but
  genuine 2-item table (GPS-tracked actual speed vs self-estimated speed,
  km/h), n=312. Reported n/items from the automated pass (312/8) mostly
  matched; the other 6 columns in the source file are derived
  error/percent-error values excluded as composites. Script:
  `data/carus_2021_snowboard_speed.py`.
- `10.1371/journal.pone.0194569` (Powell 2018, empathy/trust/economic
  decisions) -> richest of the five. Confirmed via the paper's Methods text
  ("the same measures as described in Experiment 1 were used" in
  Experiment 2) that QCAE, Trust, and the affect/memory checks were
  identically administered across both experiments, so the two subsamples
  (n=317 + n=202, non-overlapping ids after +100000 offset for Experiment
  2) were merged into single files, giving n=523. Four scales shipped:
  31-item QCAE (1-4 Likert), 3-item Trust (1-4 Likert), 5-item affective
  state (1-4 Likert), 5-item binary incidental-memory check. Composite
  columns (CE/AE/TrustScore/MemoryScore, economic-game decision variables)
  excluded. Script: `data/powell_2018_empathy.py`.

**Skipped (2 papers):**
- `10.1371/journal.pone.0154145` (van Dijke 2016, facial affect labeling in
  schizophrenia/BPD) -- the only SI file (`SI_raw data face processing.sav`,
  n=153) contains only per-condition aggregate error counts and ratios
  (e.g. `f_a_100`, `h_n_ratio`) computed across trials, not raw per-trial
  labeling responses. No genuine item/trial-level data available. Skip:
  content problem (aggregate-only).
- `10.1371/journal.pone.0272987` (Turner 2022, irrational beliefs/worker
  mental health) -- reported n=51/items=5 from the automated pass was
  wrong; true N is 362 per study (Study 1 and Study 2, cross-sectional, not
  repeated-measures). However all 5 SI data files (S1 File R script, S2/S4
  File CSVs, S3/S5 File SAVs) turned out to be latent-profile-analysis
  inputs: standardized/z-scored composite subscale scores (e.g. `intrin`,
  `MentalWellbeing`, `Depression` as a single per-person total), not raw
  item-level responses to the underlying instruments (iPBI, R-MAWS,
  SWEMWBS, PSS, Procrastination Scale, ITS). No raw item data was ever
  shared for any of the six named instruments. Skip: content problem
  (aggregate/composite-only), independent of the N correction.

`biblio_plos_batch27_worthretrying.csv` (7 rows) is ready for ben-domingue
to upload to Redivis and paste into the dictionary sheet.

**PLOS ONE batch 27 — 5 more `worth_retrying` DOIs, full manual review:**

A separate set of 5 DOIs classified `worth_retrying` by `irw_retriage_ha.py`
in batch 27 were fetched in full (article page + all SI files) and
hand-inspected.

Shipped (3 papers, 11 output tables):
- `10.1371/journal.pone.0314338` (Liu, Yan & Li 2025, PE teacher support /
  middle-school sport participation, China) -- Dryad-hosted SAV (S1 File),
  n=879 confirmed via `id.nunique()`. Raw file has 7 distinct item-prefix
  groups (JSZC/YDJC/YDLQ/NLGZ/YDCY/JJQX/XLJK) plus a trailing block of
  already-computed subscale sums/means (excluded as composites). The
  paper's English text only explicitly names 4 instruments while the data
  has 7 prefix groups, so each prefix group was shipped as its own file
  under a neutral label rather than guessing an unconfirmed English
  construct name. Scripts: `data/liu_2025_teacher_support.py` ->
  `liu_2025_teacher_support` (15 items, 1-7), `liu_2025_perceived_competence`
  (4 items, 1-5), `liu_2025_ydlq` (10 items, 1-5), `liu_2025_nlgz` (4 items,
  1-5), `liu_2025_ydcy` (5 items, 0-5), `liu_2025_jjqx` (10 items, 1-5),
  `liu_2025_xljk` (12 items, binary 0/1).
- `10.1371/journal.pone.0284366` (Babaei et al. 2023, community oral-health
  trial, Tehran schoolchildren) -- S1 File is the CONSORT PDF, actual SAV
  data is S2 File; n=739 confirmed. 3 raw item groups across 3 waves
  (baseline/1yr/2nd follow-up): child hygiene behavior (3 items, 1-5 +
  6="do not know" sentinel filtered), mother-reported hygiene behavior (3
  items, same scale), caries/gum knowledge-attitude (16 items, 1-4
  agree/disagree + 5="do not know" sentinel filtered, one stray
  non-integer glitch value dropped). Excluded DI/CI/OHIS clinical exam
  indices and reverse-coded companion columns (QD*.A0 etc.) as composites.
  `IC` column is intervention/control group, not an identity card -- no
  PII. Script: `data/babaei_2023_oral_health.py` ->
  `babaei_2023_child_hygiene_behavior`, `babaei_2023_mother_hygiene_behavior`,
  `babaei_2023_oral_kap`.
- `10.1371/journal.pone.0169668` (Gholami et al. 2017, periodontal-knowledge
  mass-media campaign, Iranian adults) -- S1 File SAV, n=543 confirmed. The
  raw `BaselineFollow.N.Knowledge.Qx` columns store the *chosen
  multiple-choice option code* (nominal, 4-5 options + "don't
  know"/"no answer" sentinels), not an ordinal response, so `resp` was
  built from the paired `.recoded` correct/incorrect (0/1) columns instead
  -- the genuine per-item scored response used in the paper. 3 items x 3
  waves (baseline + 2 follow-ups). Script:
  `data/gholami_2017_periodontal_knowledge.py` ->
  `gholami_2017_periodontal_knowledge`.

Skipped (2 papers):
- `10.1371/journal.pone.0203689` (Gubbels et al. 2018, energy-balance
  parenting practices, child-care triads) -- the shared SAV (S2 File) 
  contains only already-computed subscale scores (e.g.
  `PPDietChildcontrol`, `SPPAEngagement`) -- decimal means, not raw
  item-level responses. No raw item column exists anywhere in the file.
  Skip: content problem (composite-only, no genuine `resp` data available).
- `10.1371/journal.pone.0252543` (Padrós-Blázquez et al. 2021, GSAM
  enjoyment-modulator scale, Morelia adults) -- the shared XLSX (S2 File)
  has 571 rows but a `cod` (participant id) column that is non-null for
  only 128 of them (matching the triage's reported n=128) with an
  unexplained `study` grouping column (values up to 405, mostly NaN) that
  doesn't reconcile with the paper's reported N (1884: 273 pilot + 1611
  final). No codebook or Methods text clarifies what the extra 443
  id-less rows represent or how `study` maps to the pilot/final samples.
  Flagged as ambiguous rather than guessed at -- skip pending author
  contact or further clarification, not a clean content/PII/N failure.

11 new rows appended to `biblio_plos_batch27_worthretrying.csv` (now 18
rows total) for ben-domingue to upload to Redivis and paste into the
dictionary sheet.

## PLOS ONE batch 27 — full accounting (2026-08-12)

Batch 27 (`plos_batch27_triage.csv`, 1,667 candidates from 30 recycled
non-PLOS search terms) closed out end-to-end.

**`good` candidates (9), reviewed directly:** 6 fell below the N=50 floor
(N=16/22/24/28/14/48) and were skipped outright. One (N=232, "What drives
consumer participation in virtual CSR?", `10.1371/journal.pone.0342470`)
looked strong on paper but its 19 "item" columns turned out to be
per-respondent averages of several underlying survey questions each
(values like 3.75/4.25/4.33/4.67 aren't reachable on a single Likert item)
-- skipped as aggregate/composite, not raw response data. Two more
(N=83 "RE-AIM cognitive health pilot" `10.1371/journal.pone.0260934`; N=82
"Procedural Metacognition and False Belief Understanding in 3- to
5-Year-Olds" `10.1371/journal.pone.0141321`) are real raw-item candidates
in the 50-99 ask-first band -- not shipped, added to TODO.md.

**A fifth group (schafer/music-listening), full manual review:** 1 of 5
shipped -- `10.1371/journal.pone.0151634` (Schafer et al. 2016, music
listening goals/effects) -> two 3-item diary-episode scales (`wave` =
episode order), n=121 respondents / 1502 episodes (the automated pass's
reported n=967 was wrong -- real n confirmed by unique-id count). Script:
`data/schafer_2016_music_goals_effects.py` -> `schafer_2016_music_goals`,
`schafer_2016_music_effects`. The other 4 in this group were skipped for
content reasons after full article+SI review: `10.1371/journal.pone.0152928`
(water intake CRT -- only pre-computed daily-intake estimates deposited,
no raw FFQ items), `10.1371/journal.pone.0318986` (conspiracy videos --
video-level content-analysis data, not person x item), `10.1371/journal.
pone.0289686` (Poland historical partitions -- school-level aggregate
administrative data, no individual respondents), `10.1371/journal.pone.
0224159` (romantic attachment anxiety, n=1502 confirmed but only
pre-computed subscale-mean columns deposited, no raw ECR/support/control
items).

**4 candidates with unresolved n_participants/n_items from the automated
pass, hand-checked:** 1 shipped -- `10.1371/journal.pone.0261717` (Srivani
et al. 2022, Education 4.0 / English-learning agreement scale) -> 11 raw
items (0-2 agreement scale), n=145, a sparse -1 sentinel (20/1595 cells,
isolated to 5 of 11 items) dropped as data-entry artifact. Script:
`data/srivani_2022_education4.py` -> `srivani_2022_education4`. 1 deferred
to the 50-99 band -- `10.1371/journal.pone.0241721` (Theory of Mind
longitudinal stability): the one clean extractable item battery inside a
131x334-column mega-file (Wellman-style ToM tasks) only has n=66
non-missing respondents; needs a ben-domingue go/no-go plus real
extraction effort given the surrounding derived columns. 2 skipped for
content: `10.1371/journal.pone.0202494` (Dutch orthopaedic sport-advice
survey -- all 4 SI files are pre-aggregated physician-survey summary
tables, no per-respondent data) and `10.1371/journal.pone.0289081`
(Scholars180 optometry presentation assessment -- both raw-data SI files
have only n=43, below floor).

**7 more candidates with unresolved counts, skipped by title/content match
without a full fetch** (scoping reviews, a Delphi-technique expert panel,
a qualitative interpretive-vignette study, a rat electrophysiology study,
and an ML facial-expression-recognition engagement study -- none of these
structurally contain a person x item response matrix, unlike the 4 above
which were plausible enough to warrant checking): `10.1371/journal.pone.
0345874` (underwater rugby coaching vignette study), `10.1371/journal.pone.
0334232` (facial expression recognition/ML), `10.1371/journal.pone.0225243`
(Delphi technique hospital community benefit), `10.1371/journal.pone.
0272531` (eye-movement translation/paraphrase task -- not an item-response
task), `10.1371/journal.pone.0338521` (personality-across-cultures scoping
review), `10.1371/journal.pone.0294151` (rat synaptic activity, not item
response), `10.1371/journal.pone.0285226` (MENA digital-health scoping
review).

**3 candidates skipped outright for N<50** (no review needed):
`10.1371/journal.pone.0270427` (n=41), `10.1371/journal.pone.0177398`
(n=22), `10.1371/journal.pone.0224326` (n=24).

**11 candidates in the 50-99 ask-first band, not shipped, added to
TODO.md** for a ben-domingue go/no-go: the 2 `good`-flagged ones above,
the 1 `worth_retrying` ToM-longitudinal one above, plus 8 more
`worth_retrying` rows never individually content-reviewed since they're
gated on the N decision first: `10.1371/journal.pone.0218017` (n=80,
music/negative affect, 41 items), `10.1371/journal.pone.0151747` (n=60,
attachment/HRV, 88 items), `10.1371/journal.pone.0117947` (n=86, ToM &
sharing preschool, 7 items), `10.1371/journal.pone.0241041` (n=53, Tactile
Biography questionnaire, 14 items), `10.1371/journal.pone.0257274` (n=83,
dying-within-dyads palliative care, 23 items), `10.1371/journal.pone.
0150375` (n=58, attachment/HRV ostracism, 63 items), `10.1371/journal.pone.
0149777` (n=54, 30 Days Wild nature engagement, 12 items), `10.1371/
journal.pone.0203664` (n=61, L2 acquisition PE intervention refugees, 7
items).

**Second worth_retrying group (Liu/Babaei/Gholami/Gubbels/Padros-Blazquez)
and third group (Wen/Carus/Powell/van Dijke/Turner)** covered in the two
entries immediately above this one.

**Net result for batch 27:** 8 papers shipped, 21 tables total (2
schafer_2016 + 1 srivani_2022 + 7 liu_2025 + 3 babaei_2023 + 1 gholami_2017
+ 2 wen_2022 + 1 carus_2021 + 4 powell_2018). `biblio_plos_batch27_
worthretrying.csv` (21 rows) is ready for ben-domingue to upload to Redivis
and paste into the dictionary sheet. `human_review/human_review_plos_
batch27.csv` (78 rows) is the permanent human-review record, no action
needed. `plos_batch27_triage.csv` and `plos_batch27_retriage.csv` can be
deleted once the biblio CSV is confirmed uploaded.

## PMC connector batch 4 — 7 `worth_retrying` candidates, manual review (2026-08-12)

Full manual review (article page + all supplementary files via
`{PMCID}/supplementaryFiles`) of the 7 `worth_retrying` rows from PMC
connector batch 4's retriage. License confirmed CC BY for all 7 via
Europe PMC's `resultType=core` `license` field. Verdicts:

- **Shipped — Gobbens (2018), "Associations of ADL and IADL disability with
  physical and mental dimensions of quality of life in people aged 75
  years and older," PeerJ, `10.7717/peerj.5425`, PMC6087617.** SI file
  `peerj-06-5425-s001.sav` (377 rows, all age ≥75, no PII) has three clean
  raw-item scales: 11-item ADL, 7-item IADL (both 1-4), and the 12-item
  SF-12. `data/gobbens_2018_adl_iadl_sf12.py` → `gobbens_2018_adl.csv`
  (377 ids), `gobbens_2018_iadl.csv` (377 ids), `gobbens_2018_sf12.csv`
  (374 ids).
- **Shipped — Amarilla-Donoso et al. (2020), "Quality of life after hip
  fracture: a 12-month prospective study," PeerJ, `10.7717/peerj.9215`,
  PMC7304420.** SI file `peerj-08-9215-s001.sav` (224 ids, unique
  `ID_BASDAT`, no PII) is a longitudinal baseline/1-month/6-month/1-year
  cohort with four raw-item instruments: 12-item SF-12, 5-item EQ-5D,
  10-item Barthel Index, 8-item Lawton-Brody IADL — each written with a
  `wave` column (1-4) rather than one column per timepoint.
  `data/amarilla_2020_hip_fracture.py` → `amarilla_2020_sf12.csv`,
  `amarilla_2020_eq5d.csv`, `amarilla_2020_barthel.csv`,
  `amarilla_2020_lawton_brody.csv` (224 ids each, natural attrition by
  wave, lowest N=202 at 1-year).
  Verified n_items reported by the automated triage (91) was wrong — the
  real per-scale item counts are 12/5/10/8.
- **Shipped — Almuqbil et al. (2022), "Postpartum depression and
  health-related quality of life: a Saudi Arabian perspective," PeerJ,
  `10.7717/peerj.14240`, PMC9575671.** SI file `peerj-10-14240-s001.xlsx`
  has a clean 10-item EPDS (0-3, 253 complete respondents) plus
  SUM/categorical/numerical aggregates (excluded) and an SF-12 block. The
  SF-12 block was **not** shipped — its response columns are free text
  with many rows holding concatenated multi-answer strings (e.g. "Most of
  the time,  A good bit of the time") rather than one clean category per
  cell, not reliably parseable without guessing. `data/almuqbil_2022_
  epds.py` → `almuqbil_2022_epds.csv` (253 ids, 10 items).
  Reported n_items (43) was wrong — real EPDS item count is 10; the 43
  count evidently included SF-12/demographic columns.
- **Skipped — "Analysis of influence of physical health factors on
  subjective wellbeing of middle-aged and elderly women in China,"
  `10.1186/s12889-022-12655-6`, PMC9169341.** SI file (CFPS-derived
  panel, 4997 ids × 2 waves) has exactly one response-like variable
  (`happy`, a single subjective-wellbeing item, 1-5) with every other
  column a person-level demographic/health covariate (income, social
  status, chronic disease, smoking, etc.) — not an item battery, fails
  the "at least 2 distinct items" rule.
- **Skipped — "Analysis of influencing factors of anxiety and depression
  in maintenance hemodialysis patients...," `10.7717/peerj.16068`,
  PMC10518163.** SI file (n=120) has only pre-computed `SAS score`/`SDS
  score` totals, no raw anxiety/depression items.
- **Skipped — "The impact of COVID-19 on the achievement of public school
  students in British Columbia...," `10.1016/j.heliyon.2025.e42851`,
  PMC11891674.** SI file (`mmc1.xlsx`, 3765 rows) is district/province-
  level aggregate proficiency counts (`DATA_LEVEL` = "District Level" /
  "Province Level"), not per-student response data — no `id` unit exists
  at the individual level.
- **Skipped — "The severity of mobile phone addiction and its
  relationship with quality of life in Chinese university students,"
  `10.7717/peerj.8859`, PMC7271884.** SI file (`.sav`, n=2312) has only a
  pre-computed `MobilePhoneAddictionScore1` total, no raw addiction-scale
  items.

`grep -rl "DOI: <doi>" data/*.py` confirmed none of the 7 had been shipped
via any earlier pathway before this review. `biblio_pmc_batch4_
worthretrying.csv` (8 rows: 3 papers, 3+4+1 tables) is ready for
ben-domingue to upload to Redivis and paste into the dictionary sheet.

## PMC batch 4, worth_retrying manual review (5 candidates, 2026-08-12)

Manual full review (article + all supplementary files via the
`/supplementaryFiles` zip endpoint, not just the first tabular file) of 5
`worth_retrying` rows from the PMC batch-4 retriage. `grep -rl "DOI: <doi>"
data/*.py` confirmed none of the 5 had been shipped via any earlier
pathway. All 5 papers are CC BY 4.0 (verified via Europe PMC core
`license` field).

- **Skipped — "Internet addiction and poor quality of life...suicidal
  ideation of senior high school students in Chongqing, China,"
  `10.7717/peerj.7357`, PMC6719746.** SI file `peerj-07-7357-s001.sav`
  (n=26688) has only pre-computed composite/binary columns (DEP 12-60
  depression total, QOL 6-30 total, IA 1-2 binary internet-addiction
  classification, SI 0-1 binary suicidal-ideation flag) — no raw item
  data at all, and the person-level `ID` column is non-unique (2925
  unique values across 26688 rows). Reported n=26688/items=6 reflects
  this administrative dataset's row count, not usable item-response data.
- **Skipped — "Pronounced social inequality in health-related factors and
  quality of life in women and men from Austria...overweight or obese,"
  `10.7717/peerj.6773`, PMC6510219 — reconsidered as ship, see below.**
  (Initial read of the 567-column ATHIS microdata extract looked like an
  administrative dump; on closer inspection columns LQ1-LQ26 are the raw
  WHOQOL-BREF items the paper's QOL domain scores are computed from.)
- **Shipped — Burkert & Freidl (2019), PeerJ, `10.7717/peerj.6773`,
  PMC6510219.** SI file `peerj-07-6773-s001.sav` is the full ATHIS
  2014/2015 microdata (567 cols); most of it is unrelated survey content,
  but LQ1-LQ26 are the raw WHOQOL-BREF items (1-5 Likert, German
  variable labels in the .sav metadata) underlying the paper's four
  domain scores. No missing values, no PII (only birth-related column is
  a 3-level birth-country code, not a DOB). `data/burkert_2019_
  whoqol_bref.py` → `burkert_2019_whoqol_bref.csv` (15771 ids, 26 items).
  Reported n_items (41) was wrong — real WHOQOL-BREF item count is 26.
- **Skipped — "Nicotine smoking is associated with impaired cognitive
  performance in Pakistani young people," `10.7717/peerj.11470`,
  PMC8179217.** SI file `peerj-09-11470-s001.xlsx` (5 sheets, n~102) has
  only per-subject summary/aggregate scores per cognitive test (MMSE
  total, Edinburgh Handedness Inventory total, PRM percent-correct, CRT
  raw score) — no trial-level or item-level responses anywhere in the
  workbook, all sheets have subjects as columns with a single aggregate
  score row per test.
- **Shipped — Mancone, Tosti, Corrado & Diotaiuti (2024), PeerJ,
  `10.7717/peerj.18195`, PMC11470773.** SI file `peerj-12-18195-s001.sav`
  (n=160) has Rey Auditory Verbal Learning Test 5-trial raw scores:
  SESS_1-5 (correct-recall count per trial, 0-15) and INTRU_1-5
  (intrusion-error count per trial) — genuine per-trial repeated
  measures, not the paper's reported aggregate outcomes
  (TOTALE_Repetitions/TOTAL_INTRUSIONS/DELAYED_RECALLS/
  FALSE_RICOGNITIONSI, excluded). Split into two files per trial-score
  type. `data/mancone_2024_ravlt.py` →
  `mancone_2024_ravlt_recall.csv` (160 ids, 5 items) and
  `mancone_2024_ravlt_intrusion.csv` (160 ids, 5 items).
- **Shipped — Arza-Moncunill, Medina-Mirapeix & Martin-San Agustin (2023),
  PeerJ, `10.7717/peerj.16246`, PMC10588714.** SI file
  `peerj-11-16246-s004.sav` (n=272) has the 43 retained items of the
  Expectations of Physiotherapists Questionnaire (7-point Likert, "very
  much disagree" to "very much agree" per the paper's Methods). Split by
  area per SI file `peerj-11-16246-s005.docx`'s item-to-subtheme mapping:
  clinical care (22 items) and administrative activities (21 items).
  `data/arzamoncunill_2023_epq.py` →
  `arzamoncunill_2023_epq_clinical.csv` (272 ids, 22 items) and
  `arzamoncunill_2023_epq_admin.csv` (272 ids, 21 items).

`biblio_pmc_batch4_manual5.csv` (5 rows for the 3 shipped tables/5 files)
is ready for ben-domingue to upload to Redivis and paste into the
dictionary sheet.

## PMC batch 4, worth_retrying manual review (10 no-resolved-N candidates, 2026-08-12)

Manual full review (article + all supplementary files via the
`/supplementaryFiles` zip endpoint) of 10 `worth_retrying` rows from PMC
batch 4's retriage that had no resolved participant/item count from the
automated pass. `grep -rl "DOI: <doi>" data/*.py` confirmed none of the 10
had been shipped via any earlier pathway. Licenses confirmed CC BY 4.0 for
all 10 via Europe PMC core `license` field.

- **Shipped — Allen, Interian, Reddy, Rodriguez & Myers (2025), PeerJ,
  `10.7717/peerj.19057`, PMC11892457.** SI file
  `peerj-13-19057-s001.xlsx` sheet `questionnaire_scoring` (n=156 rows,
  145 after dropping 11 pilot/`test_only` administrations flagged in the
  `summary` sheet) has three raw-item instruments: the 27-item Kirby
  Monetary Choice Questionnaire (binary smaller-sooner/larger-later
  choices), the 16-item short Barratt Impulsiveness Scale (0-3), and the
  20-item UPPS-P (1-4). IDs are a mix of plain integers and cohort-coded
  strings (e.g. `001SP23`) — kept as strings per datastandard.md rather
  than force-coercing to numeric (an earlier draft of the script did that
  and silently dropped 51 valid string-ID participants down to 94; fixed
  before shipping). Other item pools in the same sheet (`be`/`bb`/`ba`/`a`
  prefixes: BDI-II, BAS/BIS, ATQ items) have ~54% missingness (only
  administered to a subset) and were left out. `data/allen_2025_
  delaydiscount.py` → `allen_2025_delaydiscount.csv`, `allen_2025_bis.csv`,
  `allen_2025_upps.csv` (145 ids each).
- **Shipped — Zhao & Zhou (2024), PeerJ, `10.7717/peerj.18134`,
  PMC11466236.** SI file `peerj-12-18134-s001.sav` (n=1106, 884 with
  valid item data) is a two-wave (T1/T2) panel of Chinese senior high
  schoolers with three raw-item instruments at both waves: 6-item
  depression, 6-item anxiety, 12-item NSSI (all 0-4 frequency).
  Aggregate `T1D/T2D/T1A/T2A/T1N/T2N` totals excluded. Written with a
  `wave` column (1=T1, 2=T2) per datastandard.md's longitudinal
  convention rather than separate T1/T2 item names. `data/zhao_2024_
  nssi.py` → `zhao_2024_depression.csv`, `zhao_2024_anxiety.csv`,
  `zhao_2024_nssi.csv` (884 ids each).
- **Shipped — Khattak, Ehsan, Khalid, Iqbal, Chaudhary, Baig, Alsharari &
  Memon (2026), PeerJ, `10.7717/peerj.21098`, PMC13156951.** SI file
  `peerj-14-21098-s001.sav` (n=400 practicing dentists) has three raw
  binary-item instruments: 4-item attitude (agree/disagree; item 4 does
  not exist, only 1/2/3/5 retained by the original authors), 4-item
  clinical readiness (yes/no), 4-item confidence. The `knowledge` column
  is a pre-computed low/moderate/high composite and excluded.
  `data/khattak_2026_blscpr.py` → `khattak_2026_attitude.csv`,
  `khattak_2026_cr.csv`, `khattak_2026_confidence.csv` (400 ids each).
- **Shipped — Reuter, Forster & Kruger (2021), PeerJ, `10.7717/peerj.12528`,
  PMC8679900.** SI file `peerj-09-12528-s001.xlsx` has four sheets; two
  are clean homogeneous item batteries with no person-ID column in the
  source (anonymous survey rows, row index used as `id` per
  datastandard.md): `Emotions` (39-item binary mood/emotion checklist,
  n=514) and `Mental health` (6-item campus-life/social-connection scale,
  mixed Yes/No and Less/About-the-same/More response options mapped to
  0/1 and 0/1/2 respectively, n=519). The other two sheets
  (`Longitudinal data I`/`II`) are heterogeneous single-purpose
  health-behavior counts in mixed units (hours, days, times) plus a
  handful of suicide-ideation items — not a psychometric scale, left out
  (could be revisited separately). `data/reuter_2021_emotions.py` →
  `reuter_2021_emotions.csv` (514 ids), `reuter_2021_campuslife.csv`
  (519 ids).
- **Skipped — "The impact of history of depression and access to weapons
  on suicide risk assessment: a comparison of ChatGPT-3.5 and
  ChatGPT-4," `10.7717/peerj.17468`, PMC11143969.** SI file is ChatGPT-3.5
  vs. ChatGPT-4 risk ratings on suicide-risk vignettes (`Model` column:
  3.0/4.0, 80 rows each) — AI-generated model output, not human item
  response data.
- **Skipped — "Depression and bipolar disorder subtypes differ in their
  genetic correlations with biological rhythms," `10.1038/
  s41598-022-19720-5`, PMC9492698.** SI file is LDSC genetic-correlation
  and MAGMA gene-level summary statistics (SNP/gene aggregate tables),
  not person-level item response data.
- **Skipped — "Association of heat shock protein polymorphisms with
  patient susceptibility to coronary artery disease comorbid depression
  and anxiety in a Chinese population," `10.7717/peerj.11636`,
  PMC8216166.** SI file has only pre-computed `GAD-7 score`/`PHQ-9 score`
  totals plus SNP genotype columns — no raw depression/anxiety item data
  anywhere in the workbook (Sheet2/Sheet3 empty).
- **Human review — "Self-reported depression and anxiety rates among
  females with cutaneous leishmaniasis in Hubuna, Saudi Arabia,"
  `10.7717/peerj.15582`, PMC10289083.** SI file `peerj-11-15582-s001.sav`
  has only n=69 unique respondents (50-99 band) and opaque unlabeled
  columns (`VAR00008`...`VAR00048`) needing the paper's text to interpret
  — not resolved in this pass, needs a human decision per the min-sample-
  size policy rather than an automated ship/skip.
- **Human review — "An extended research of crossmodal correspondence
  between color and sound in psychology and cognitive ergonomics,"
  `10.7717/peerj.4443`, PMC5835347.** Two SI files: Exp1
  (`peerj-06-4443-s001.xlsx`, color-hue matching to abstract properties
  like Sharpness/Roughness/Tempo/Pitch, 20 trials × n=52 unique subjects —
  50-99 band) and Exp2 (`peerj-06-4443-s002.xlsx`, sound-color pairing
  accuracy/RT, n=20 — below the N=50 floor, skip that part). Exp1's
  response is a chosen RGB hex color code per trial, not a
  straightforward numeric scale value — would need a considered categorical/
  numeric encoding decision even setting aside the borderline N; flagged
  for human review rather than guessing at an encoding.
- **Skipped — "Influence of diurnal variations on cognitive coordination
  and misunderstanding in elite male handball players," `10.7717/
  peerj.20370`, PMC12812274.** SI file is aggregate count/percentage
  summary tables by match and category (e.g. "Similar"/"Complementary"/
  "Contradictory"/"Misunderstanding" sharing modes per match), not raw
  per-player/per-trial response data — no individual-level `id` unit
  exists in the file.

`biblio_pmc_batch4_manual10.csv` (11 rows for the 4 shipped papers/11
tables) is ready for ben-domingue to upload to Redivis and paste into the
dictionary sheet.

## PMC batch 4 — full accounting (2026-08-12)

Europe-PMC-connector batch 4 (`pmc_batch4_triage.csv`, 1,502 candidates
from 30 recycled non-PMC terms, heavy on named instruments, across all 11
`JOURNALS`) closed out end-to-end. Flags: 10 `good`, 128 `human_assistance`,
540 `license_restricted`, 30 `not_item_response`, 779 `no_usable_file`, plus
a handful of `error`/`download_failed`/`file_too_large`/`timeout`.
`irw_retriage_ha.py` sub-classified the 128 `human_assistance` rows: 48
`aggregate_continuous`, 39 `worth_retrying`, 21 `not_item_response`, 20
`human_review` (written to `human_review/human_review_pmc_batch4.csv`,
permanent record, no action needed).

**`good` candidates (10), reviewed directly:** 2 were repeat known false
positives from PMC batch 1 (`10.1186/s12874-021-01376-w` PCIQ-F
item-development table; `10.7717/peerj.2782` cannabis
exclusion-screening form -- both skipped again without re-review, same
reasoning as batch 1). 3 skipped: `10.7717/peerj.1611` (rat pharmacokinetics,
N=20), `10.7717/peerj.3508` (video game cognitive screen, N=16),
`10.7717/peerj.4837` (lumpfish welfare, N=20) -- all below the N=50 floor.
1 skipped for content: `10.7717/peerj.17902` (alfalfa leafcutting bee
study) -- ecological/behavioral count data (offspring/cocoon counts per
capsule/cage/nest), not a person x item response structure despite the
non-human note in SKILL.md (that note applies to genuine repeated
item/trial batteries on animal subjects, not field-ecology outcome
counts). 1 deferred to the 50-99 ask-first band: `10.7717/peerj.17536`
(serum proteomics cognitive impairment, verified N=50-63 across messy
multi-header sheets, real MMSE/MoCA data but needs real extraction
effort). 3 shipped: `10.7717/peerj.17174` (Kilic 2024, taekwondo
nutrition/mental toughness, N=276) -> `kilic_2024_nutrition_attitude`
(21 items, 1-5), `kilic_2024_mental_toughness` (11 items, 1-5);
`10.7717/peerj.12604` (Pauli & Wilhelmy 2021, PPOS-D6, N=332) ->
`pauli_2021_ppos_d6` (6 items, 0-5), `pauli_2021_coercion_attitudes` (15
items, 0-5, same sample); `10.7717/peerj.11474` (Morales et al. 2021,
ASMR/emotion regulation, N=177 confirmed, reported N=179 was slightly off)
-> `morales_2021_erq` (10 items, 1-7), `morales_2021_asmr15` (15 items,
1-5). Scripts: `data/kilic_2024_taekwondo.py`, `data/pauli_2021_ppos_d6.py`,
`data/morales_2021_asmr.py`.

**39 `worth_retrying` rows, split into 4 parallel review passes** (full
article + all supplementary files fetched per candidate via Europe PMC's
`supplementaryFiles` endpoint):

*Group 1 (7 candidates) -- 3 shipped, 8 tables:* `10.7717/peerj.5425`
(Gobbens 2018, ADL/IADL/SF-12, N=377/377/374) -> `data/gobbens_2018_adl_
iadl_sf12.py`; `10.7717/peerj.9215` (Amarilla-Donoso et al. 2020, hip
fracture, SF-12/EQ-5D/Barthel/Lawton-Brody, longitudinal N=224, reported
items=91 was wrong -- real per-scale counts 12/5/10/8) -> `data/amarilla_
2020_hip_fracture.py`; `10.7717/peerj.14240` (Almuqbil et al. 2022, EPDS,
N=253, reported items=43 was wrong -- real=10, SF-12 block skipped as
unparseable) -> `data/almuqbil_2022_epds.py`. 4 skipped: `10.1186/
s12889-022-12655-6` (single-item outcome, fails >=2-items rule),
`10.7717/peerj.16068` (pre-computed SAS/SDS totals only), `10.1016/
j.heliyon.2025.e42851` (district-level aggregate counts, no individual
id), `10.7717/peerj.8859` (pre-computed addiction-score total only).

*Group 2 (7 candidates) -- 5 shipped, 12 tables:* `10.7717/peerj.19587`
(Hen-Herbst & Fogel 2025, family routines/QoL, pre/during-COVID wave,
N=253) -> `data/hen-herbst_2025_family_routines.py` (3 files: routine
frequency 28 items 1-4, routine importance 28 items 1-3, family QoL 21
items 1-5; an undocumented FCOPE battery excluded, response scale never
confirmed in this paper's Methods); `10.7717/peerj.18676` (Mohamed et al.
2024, PPOS medical students, N=143, reported items=26 was wrong -- 8 were
composite/transformed scores) -> `data/mohamed_2024_ppos.py` (18 items,
1-6, wave=year2/year4); `10.7717/peerj.2245` (Johannisson 2016, IPIP-NEO-120,
N=200, auto-triage had rows/columns inverted -- real N=200/120 items not
155/200) -> `data/johannisson_2016_ipip_neo.py`; `10.7717/peerj.10752`
(Habibi et al. 2021, MEIM, N=426, auto pass had grabbed the wrong SI file
-- the real 12-item raw file was s001.csv not s002.csv) -> `data/habibi_
2021_meim.py`; `10.7717/peerj.16384` (Liu et al. 2023, hypertension-doctor
medication-adherence survey, N=236, 6 genuine multi-item batteries,
single-item questions excluded) -> `data/liu_2023_medication_adherence.py`.
1 deferred to the 50-99 band: `10.7717/peerj.19403` (Sterna et al. 2025,
time perception/personality disorders, ZTPI-20 genuine but only 63 of 126
rows carry any item data, verified N=63). 1 skipped for PII: `10.7717/
peerj.18800` (disaster medicine training) -- all 3 raw .sav files carry a
real 10-digit institutional student ID number (confirmed via the English
codebook as "Öğrenci No: Student Number"), skipped whole per the PII
policy rather than dropping the column.

*Group 3 (5 candidates) -- 3 shipped, 5 tables:* `10.7717/peerj.6773`
(Burkert & Freidl 2019, WHOQOL-BREF, N=15771, reported "41 items" was
wrong -- real data is the raw 26-item WHOQOL-BREF buried in a 567-column
ATHIS microdata extract) -> `data/burkert_2019_whoqol_bref.py`; `10.7717/
peerj.18195` (Mancone et al. 2024, RAVLT 5-trial raw recall/intrusion
scores, N=160) -> `data/mancone_2024_ravlt.py` (2 files); `10.7717/
peerj.16246` (Arza-Moncunill et al. 2023, EPQ, N=272, 43 items split
clinical/admin per the SI's own subtheme mapping) -> `data/arzamoncunill_
2023_epq.py` (2 files). 2 skipped: `10.7717/peerj.7357` (Chongqing
internet addiction/suicidal ideation, N=26688 reported but SI has only
pre-computed composite/binary columns plus a non-unique id, no raw items);
`10.7717/peerj.11470` (Pakistani nicotine cognition, only per-subject
aggregate test scores across all 5 SI sheets, no trial-level data).

*Group 4 -- 10 candidates with unresolved n_participants/n_items from the
automated pass, hand-checked -- 4 shipped, 11 tables:* `10.7717/
peerj.19057` (Allen et al. 2025, delay discounting/impulsivity, N=145
after excluding 11 pilot rows) -> `data/allen_2025_delaydiscount.py` (3
files: MCQ 27 binary items, BIS 16 items, UPPS-P 20 items); `10.7717/
peerj.18134` (Zhao & Zhou 2024, NSSI/depression/anxiety, N=884, T1/T2
wave) -> `data/zhao_2024_nssi.py` (3 files); `10.7717/peerj.21098`
(Khattak et al. 2026, BLS/CPR dentist survey, N=400) -> `data/khattak_
2026_blscpr.py` (3 files, 4 binary items each); `10.7717/peerj.12528`
(Reuter et al. 2021, COVID-19 student wellbeing, N=514/519) -> `data/
reuter_2021_emotions.py` (2 files). 4 skipped: `10.7717/peerj.17468`
(ChatGPT suicide-risk comparison -- confirmed AI model output, not human
data), `10.1038/s41598-022-19720-5` (LDSC/MAGMA gene-level aggregate
stats only), `10.7717/peerj.11636` (composite GAD-7/PHQ-9 totals + SNP
genotypes only, no raw items), `10.7717/peerj.20370` (handball diurnal
variation, aggregate match-level tables only). 2 deferred: `10.7717/
peerj.15582` (leishmaniasis, verified N=69, plus opaque unlabeled
columns), `10.7717/peerj.4443` (crossmodal color/sound, Exp1 N=52 with
RGB-hex trial responses needing an encoding decision; Exp2 N=20 skipped
outright).

**Net result for PMC batch 4:** 15 papers shipped from the worth_retrying
pool (3+5+3+4) + 3 from the good pool = 18 papers, 8+12+5+11+6 = 42 tables
total. `biblio_pmc_batch4.csv` (42 rows) is ready for ben-domingue to
upload to Redivis and paste into the dictionary sheet.
`human_review/human_review_pmc_batch4.csv` (20 rows) is the permanent
human-review record, no action needed. `pmc_batch4_triage.csv` and
`pmc_batch4_retriage.csv` can be deleted once the biblio CSV is confirmed
uploaded.

**4 more candidates in the 50-99 ask-first band, not shipped, joining the
9 already flagged directly from the retriage output:** `10.7717/
peerj.17536` (serum proteomics, N=50-63, messy structure), `10.7717/
peerj.19403` (ZTPI, N=63, half the rows blank), `10.7717/peerj.15582`
(leishmaniasis, N=69), `10.7717/peerj.4443` Exp1 (crossmodal color/sound,
N=52, RGB-hex encoding question). Combined PMC batch 4 ask-band total:
13 candidates.

## QC pass on PLOS batch 27 / PMC batch 4 output, and policy corrections (2026-08-12)

ben-domingue spot-checked several of today's shipped tables and caught
real issues, plus a policy-application error that had crept back in.

**Policy correction — the N=50-99 "ask-first band" no longer exists.**
`feedback_min_sample_size` was already flattened to a hard N>=100 skip
floor earlier the same day (2026-08-12, resolving the old 50-99 ask-first
band from 2026-08-01), but today's PLOS batch 27 and PMC batch 4 write-ups
both re-introduced an "awaiting ben-domingue go/no-go" holding pattern for
24 N<50-100 candidates combined (11 PLOS + 13 PMC). Corrected: all 24 are
simply skipped, no decision needed, per the already-standing rule. Added
to `SKILL.md`'s Step 4 explicitly so this doesn't happen a third time.

**`liu_2025_ydcy` (PLOS batch 27 / actually a PLOS 0314338 Liu 2025 table,
listed under PMC batch 4 write-up by mistake -- it's `data/liu_2025_
teacher_support.py`, a PLOS ONE script):** `YDCY1` was constant (resp=1
for all 879 respondents, confirmed within every `cov_grade` level) -- a
gating/filter question, not a real scale item. `YDCY3`'s 58 zero values
were isolated to that single item, no 0s anywhere else in the 5-item
block -- the exact cross-item data-entry-error signature `datastandard.md`
describes. Fixed: dropped `YDCY1` from the item set, tightened `YDCY`'s
valid range to 1-5. Regenerated (`liu_2025_ydcy.csv`: 4 items, resp 1-5,
was 5 items resp 0-5); biblio row corrected.

**`carus_2021_snowboard_speed` — removed entirely.** On review this
doesn't fit the item-response schema: its 2 "items" were a GPS-tracked
actual speed and a self-estimated speed, i.e. an objective physical
measurement paired with a subjective estimate used to compute a
bias/calibration score, not two responses to comparable stimuli. Same
problem class as the previously-rejected fish/mouse physiological-
measurement candidates (`fushuku_2023_mouse_temperature`,
`gismann_2026_fish_personality`, both PLOS batch 15). Script and output
deleted; biblio row removed.

**`reuter_2021_campuslife` — removed entirely.** Mixed 4 binary Yes/No
items with 2 three-point Less/About the same/More items under one file
with no confirmed underlying instrument name -- the same "heterogeneous
single-purpose survey items rather than a psychometric scale" problem the
script itself already used to justify excluding the "Longitudinal data"
sheets in the same workbook. `reuter_2021_emotions.csv` (the genuine
39-item checklist from the same paper) is unaffected and still shipped.
Output deleted, script trimmed to only produce `reuter_2021_emotions`,
biblio row removed.

**`wen_2022_pyd_s1`/`_s2` — merged into one file.** Same 26-item Positive
Youth Development scale, same response scale, given to two independently-
recruited samples (no overlapping raw ids) -- ben-domingue's explicit
preference (2026-08-12) is to collapse same-instrument multi-sample data
into one file with a `cov_study` column rather than ship split files, the
same pattern `powell_2018_empathy.py` already used correctly for its own
Experiment 1/2 merge. Rewrote `data/wen_2022_pyd.py` to merge both samples
into `wen_2022_pyd.csv` (947 ids, 26 items, resp 1-5, `cov_study`=s1/s2).
Caught a real bug while doing this: the first offset attempt (+100000 for
S2 ids) collided with S1, whose raw `fid` values are household-style codes
already exceeding 470000 -- fixed to offset dynamically past S1's actual
observed max. New memory `feedback_collapse_same_instrument` records this
preference generally; also added to `SKILL.md`'s Step 4.

**Confirmed clean, no action needed:** `amarilla_2020_barthel`'s resp
values (0/5/10/15) are the Barthel Index's standard per-item scoring
(different items have different maxima by design -- feeding/bathing cap
at 5-10, transfers/mobility cap at 15), not an error.
`mancone_2024_ravlt_recall`'s resp values (3-15) are raw per-trial
words-recalled counts against a 15-word list, standard RAVLT scoring, also
not an error.

Net change to today's totals: PLOS batch 27 now 8 papers / 19 tables (was
21 -- lost carus's 1 table, wen's 2-file split collapsed to 1); PMC batch
4 now 18 papers / 41 tables (was 42 -- lost reuter_campuslife's 1 table).
Both biblio CSVs regenerated and re-verified against `irw_output/`.

## 2026-08-12 -- Batch 28, group 2: 23-candidate manual review (mixed PLOS/PMC pool)

Reviewed a 23-row mixed pool (`/tmp/batch28_5_group2.csv`: plos_good/
plos_wr/pmc_good/pmc_wr) one candidate at a time -- fetched the article
page + Data Availability statement for each, downloaded and inspected
every Supporting Information / Europe-PMC-supplementary file (not just
the first), checked license/N/PII/raw-vs-composite per candidate. 8
papers shipped -> 11 tables; 15 skipped.

**Shipped** (all CC BY 4.0, `grep -rl "DOI: ..." data/*.py` confirmed no
prior duplicate before writing):
- `jaen_2024_odor_id.py` -- 10.1371/journal.pone.0301264 (9-item NIH
  Toolbox Odor ID, binary correct/incorrect, n=845). Used the "NIH Tolbox
  Sensory items" sheet of S1 Data, not the messier raw "Monell Data"
  sheet in the same workbook.
- `ellis_2016_calculus_instructor.py` -> 2 tables (`ellis_2016_calc_
  instrqual`, `ellis_2016_calc_instrprac`) -- 10.1371/journal.pone.0157447
  (n=4925/4931). S2 File's 37-column raw survey mixes SAT/ACT scores,
  single yes/no items, and checklist "reason" items with two clean 8-item
  6-point-Likert batteries (Q18Post_*, Q19Post_*); only those two were
  kept as items. `Institution` column is confirmed by the codebook (S2
  File readme) to be a random anonymous per-institution id, not PII.
- `quinn_2023_roommate_cesd.py` -- 10.1371/journal.pone.0286709 (20-item
  CES-D, 3 waves, n=490 individuals from 245 roommate dyads). SPSS file
  has actor(`_A`)/partner(`_P`) columns for every item; kept actor-only
  to avoid double counting/ambiguous focal-unit assignment. `id` =
  `Dyad_ID*10 + Indiv_ID` (verified unique).
- `sun_2026_tiktok_travel.py` -- 10.1371/journal.pone.0349305 (29-item,
  7-point Likert, n=406).
- `shinohara_2021_testimony.py` -- 10.1371/journal.pone.0261075 (9
  behavioral-response measures -- reward-allocation ranks + explicit
  evaluation ratings toward puppets -- n=128 children).
- `temesgen_2025_elephant_conflict.py` -> 2 tables (`temesgen_2025_
  elephant_park_attitude`, `temesgen_2025_elephant_conserv_attitude`) --
  10.7717/peerj.19428 (two 7-item, 5-point-Likert attitude batteries,
  n=395 households, Ethiopia). Europe PMC's supplementary CSV embeds
  several stacked tables (household demographics, 2 attitude tables, a
  logistic-regression table) in one file with no delimiter between them;
  parsed by fixed row ranges. The source table's own footnote states
  "0=missing value" -- filtered as sentinel, not a real scale point.
- `liu_2022_fragmented_reading.py` -> 2 tables (`liu_2022_fragreading_
  frq`, `liu_2022_fragreading_cdq`) -- 10.7717/peerj.13861 (22-item FRQ +
  11-item CDQ, both 5-point Likert, n=916 Chinese university students).
- `regalado_2023_tourism_value.py` -- 10.1371/journal.pone.0286923
  (19-item, 5-point Likert, n=384). DAS text read as a future promise
  ("will be made available") but both listed SI files (S1/S2, identical
  content) already contain the full raw item data -- didn't skip on the
  DAS wording alone without checking the actual files.

`biblio_batch28_group2.csv` (11 rows) prepared for Redivis upload +
dictionary-sheet paste -- not yet confirmed by ben-domingue as of this
writing; see `TODO.md`.

**Skipped, N<100 (flat floor, no ask-first band):** 10.1371/
journal.pone.0181209 (n=47), 10.1371/journal.pone.0122311 (n=44),
10.7717/peerj.2319 (n=50), 10.7717/peerj.5441 (n=62), 10.1371/
journal.pone.0246446 (n=14 grackles), 10.1371/journal.pone.0224282 (n=76
rats), 10.1371/journal.pone.0189592 (n=8 brachial-plexus patients).

**Skipped, aggregate/composite only (no raw item-level file):**
10.1371/journal.pone.0199605 (retirement mental health -- S1 File is
baseline/post *_total subscale scores only, e.g. `base_dass_total`,
`base_rosenberg`, no per-item columns); 10.1371/journal.pone.0290153
(Hungarian aphasia screening test HAST -- "HAST scores"/"WAB scores"
sheets are subtest totals, e.g. word comprehension/naming/fluency sums,
not raw item-level pass/fail); 10.1371/journal.pone.0279255 (Luxembourg
value-added scores -- OSF repo confirmed to hold only school VA
quartile-ranking aggregates, already flagged `plos_good` but the "good"
SI file was itself the aggregate, not raw).

**Skipped, no raw item file despite DAS claim:** 10.1371/
journal.pone.0115135 (BDI depression x genetic-variant study, n=888) --
all 6 SI files are SNP/genotype figures and tables (S1/S2 Fig, S1-S4
Table); no BDI item-level or even total-score file was ever attached,
despite the DAS stating "all relevant data are within ... Supporting
Information files".

**Skipped, not item-response data:** 10.1016/j.heliyon.2024.e30702 (pure
molecular biology -- RBM15/YTHDF2/CD82 trophoblast mechanism study, no
survey/behavioral data at all); 10.7717/peerj.14014 (mouse peripheral
monoamine/hormone biomarker levels via ELISA, no survey data);
10.1186/s12889-025-25430-0 (a scoping review + thematic analysis, not a
primary dataset).

**Skipped, marginal fit / data-quality concerns -- logged rather than
shipped, could be revisited:** 10.1371/journal.pone.0311248 (smartphone-
use-reduction study, n=490) -- S2 File's only two constructs are single-
item continuous measures (self-reported minutes of phone screen time,
step count) at 2 waves; only 2 distinct "items" total and each is itself
a single-item measure duplicated across waves rather than a real
multi-item scale, plus the step-count column has implausible outliers
(up to 243,000 steps/day) that would need real per-row QC before
shipping. Judged not worth the cleanup effort relative to construct
thinness; flagged here rather than silently dropped in case someone
wants to revisit with more per-row outlier work.

No PII found in any candidate reviewed this batch (checked every shipped
file's full column list, not just the columns used).

## Batch 28, group 1 (2026-08-12)

Reviewed a 23-row mixed pool (`/tmp/batch28_5_group1.csv`: plos_good/
plos_wr/pmc_good/pmc_wr, PLOS ONE + PeerJ/Sci Reports/BMC Public Health)
by hand -- for each PLOS row, fetched the full article page and inspected
every Supporting Information attachment (not just the first tabular one);
for each PMC row, pulled Europe PMC's `supplementaryFiles` bundle (or the
publisher's direct static-content URL when the EuropePMC zip endpoint
truncated on a couple of large multi-file bundles) and full-text XML.

**Shipped (3 papers, 4 tables):** `data/bukurov_2022_comq12sf36.py` ->
`bukurov_2022_comq12` (12-item COMQ-12, n=246, 2 waves) +
`bukurov_2022_sf36` (36-item SF-36, n=246) -- S5 Appendix (SAV) held raw
per-item COMQ-12/SF-36 responses alongside ~90 derived/scaled/factor-score
columns that were excluded. `data/miedema_2023_ecs40.py` ->
`miedema_2023_ecs40` (40-item binary Economic Coercion Scale item pool,
n=930, Bangladesh survey, bilingual Yes/No response text recoded 1/0).
`data/alfort_2023_finger_fx_prom.py` -> `alfort_2023_finger_fx_prom`
(46-item hand/arm PROM, Diffic/Often/Bother blocks all raw 1-5, n=5504,
2 waves baseline/follow-up) -- pulled from a 21341-row Swedish Fracture
Register extract; only ~25% of registered fracture cases completed the
PROM, but that subset clears the N>=100 floor easily. All four verified
CC BY 4.0 on the article page itself, no PII in any of the three raw
files (checked every column, not just the ones used), no dupe DOI in
`data/*.py`. `biblio_batch28_group1.csv` (4 rows) ready for Redivis
upload + dictionary-sheet paste.

**Skipped, N<100 (triage n confirmed, no need to open the file further):**
`10.1371/journal.pone.0284300` (biology knowledge quiz, n=98),
`10.1371/journal.pone.0197161` (nursing rotation, n=50),
`10.1371/journal.pone.0196481` (ARMD vision, n=47),
`10.1371/journal.pone.0222096` (rat ABR audiograms, n=30),
`10.1371/journal.pone.0118221` (mindfulness/compassion, n=56),
`10.7717/peerj.13944` (finger-tapping, n=30, also only 2 items).

**Skipped, not real item-response data (composite/aggregate/qualitative/
non-human-subject-instrument only):**
- `10.1371/journal.pone.0217482` (leader independence): S1 Data is
  already a "pairwise data matrix" of dyad-level composite/Z-scored scale
  totals (`A_WE`, `A_EXHAU`, etc.), not raw items.
- `10.1371/journal.pone.0193861` ("metric" term usage review): a
  systematic-review paper; its SI is PDFs/XLSX study-inventory lists, no
  respondent data at all.
- `10.1371/journal.pone.0334407` (Saudi adolescents, obesity
  perceptions): S1 File is qualitative interview coding (Theme/Subtheme/
  Feedback text), not numeric item responses.
- `10.1371/journal.pone.0256497` (reproductive PROM feasibility): S1 Data
  is a mix of open-text usability feedback and single sum scores, a
  feasibility study rather than raw scale items.
- `10.1371/journal.pone.0249719` (osteopathic-care PROM UK): both SI
  files contain only pre-computed sum/composite scores (`BQ baseline sum
  score`, GRoC/satisfaction single ratings), no raw items.
- `10.1371/journal.pone.0190042` (maternal separation rats): SI sheets are
  physiological/behavioral-apparatus measures (zone times, EtOH intake,
  body weights) across weeks, not item-response data -- same class as
  previously-rejected fish/mouse physiological-measurement candidates.
- `10.1371/journal.pone.0338328` (DeepSeek vs ChatGPT exam performance):
  AI model output comparison, not human item responses.
- `10.7717/peerj.21222` (skin-cancer screening preferences/trust): the
  attached CSV (1403 x 363) is clinical/demographic/lesion-count exam
  data; the paper's actual "preference"/"trust" survey items are not
  present as columns anywhere in the file (likely reported only as
  in-text aggregate stats) -- wrong-file-for-the-construct, not a raw
  item battery.
- `10.1038/s41598-023-49465-8` (MRI brain-age dementia conversion):
  MOESM1 xlsx is aggregate summary/comparison tables only.
- `10.7717/peerj.2987` (K6 item-response pattern analysis): s001.xlsx is
  aggregate frequency-count tables per response category (secondary
  analysis of an existing survey), not per-person raw data.
- `10.1186/s12889-022-12500-w` (multi-lingual COVID workplace-prevention
  survey): MOESM2 (`Survey Data`, n=627) is a heterogeneous checklist of
  yes/no/categorical items about unrelated topics (masking, testing
  policy, who-pays, training, vaccination) rather than a single coherent
  scale/instrument -- same "heterogeneous single-purpose survey items"
  problem class that got `reuter_2021_campuslife` removed post-review
  2026-08-12.
- `10.7717/peerj.17676` (PCSK9 inhibitor / rat cognition): Europe PMC has
  no tabular supplementary file at all for this article (figures only) --
  `no_usable_file`, not a content-quality skip.

**Ambiguous -- flagged for a human decision, not shipped, not simply
skipped:** `10.1371/journal.pone.0208004` (Risk knowledge of people with
relapsing-remitting MS, RIKNO 2.0 + MSKQ questionnaires, n=1219, S1
Dataset SAV). This is a strong, clean, CC-BY, N>=1200 candidate with real
per-item structure -- but the raw items are multiple-choice with full
answer-text response options (not numeric/ordinal), and `datastandard.md`
requires `resp` to be numeric. The source questionnaire (S1 Appendix DOCX)
marks each item's correct answer via Word run-level underline formatting
("For each question, the correct answer is underlined"), which *could* be
parsed to build a correct/incorrect (0/1) scoring key, but the underline
spans didn't cleanly align to full answer-option text in a spot check
(e.g. one item's underline landed on the word "correct" in the question
stem rather than on an answer option) -- automating this reliably across
19 RIKNO + 25 MSKQ items in 6 languages carries real risk of a silently
wrong scoring key. Left unprocessed rather than guess; worth a human
building the correct-answer key by hand from S1 Appendix if this is
revisited.

No PII found in any of the four shipped files (COMQ-12/SF-36, ECS-40,
finger-fracture PROM) -- reviewed every raw column, not just the ones
used, including the Swedish Fracture Register extract's 211 columns
(only clinical event dates and hospital-internal surgeon codes, no names
or dates of birth).

## 2026-08-12 -- PLOS ONE batch 28 + PMC batch 5: discovery, and batch 28
## group 3 (22-candidate manual review, mixed PLOS/PMC pool)

Ran parallel discovery: `irw_discover_plos.py` (PLOS ONE batch 28, 30
terms recycled from the non-PLOS pool of `search_terms_log.csv` per
SKILL.md's term-selection rule) and `irw_discover_pmc.py` (PMC batch 5,
30 terms recycled from the non-PMC pool). PLOS batch 28: 1,419 candidates
-> 10 `good`, 252 `human_assistance`, rest excluded (`no_usable_file` etc).
PMC batch 5: 737 candidates -> 4 `good`, 73 `human_assistance`, 256
`license_restricted`, rest excluded.

`irw_retriage_ha.py` on both `human_assistance` pools: PLOS 28 -> 38
`worth_retrying`, 67 `human_review` (-> `human_review/human_review_plos_
batch28.csv`), 84 `aggregate_continuous`, 63 `not_item_response`. PMC 5 ->
16 `worth_retrying`, 18 `human_review` (-> `human_review/human_review_pmc_
batch5.csv`), 24 `aggregate_continuous`, 15 `not_item_response`.

Combined the two batches' `good` (14) + `worth_retrying` (54) pools = 68
candidates, split into 3 groups of ~23 and reviewed in parallel (see
group 1 and group 2 entries above). Group 3's 22-candidate review:

**Shipped -- 2 papers, 10 tables**, both CC BY 4.0, no duplicate DOI found
in `data/*.py`:
- `10.1371/journal.pone.0280919` (Hua et al 2023, Chinese university EFL
  blended-teaching survey, n=942) -> `data/hua_2023_efl_learning_scales.py`
  -> `hua_2023_efl_academic_self_concept` (26 items, 1-6),
  `_course_experience` (16 items, 1-5), `_study_engagement` (14 items,
  1-7), `_academic_procrastination` (3 items, 1-5).
- `10.1371/journal.pone.0321999` (Li et al 2025, sports-tourism
  social-media revisit-intention survey, n=435) ->
  `data/li_2025_sports_tourism_socialmedia.py` ->
  `li_2025_socmedia_usefulness`/`_enjoyment`/`_infoquality`/`_satisfaction`/
  `_ewom`/`_revisit` (3-6 items each, 1-5).

**Skipped (19)**: below N>=100 floor (5: pone.0200971 rat N~72,
pone.0348196 N=55, pone.0207589 N=76 composite, pone.0231077 N=85,
peerj.16295-adjacent pone.0308973 N~50-52); composite/pre-computed data
only, no raw items (11: pone.0246894, pone.0322635, pone.0207589,
pone.0231077, pone.0321373, pone.0283117 residualized/z-score derived
vars, pone.0240439 one-off physiological assays, peerj.16799,
s12889-025-25237-z CFA fit tables only, s41598-021-98736-9 composite +
N=96, s41598-025-17956-5 aggregate stats only); wrong data type entirely
(3: pone.0174500 clinical measurements only, pone.0275045 systematic-
review coding sheet, s41598-025-33041-3 transcriptomic data only); real
PII found in the raw file, whole candidate skipped (3: pone.0321373 real
phone numbers, pone.0122522 name/phone/birth date/postal code,
peerj.13903 real date of birth).

**Flagged for human review, not auto-decided**: `10.7717/peerj.12040`
(dementia schedule, 811 rows x 424 cols, real item-level data spanning
cognitive/depression/IADL/medical/socioeconomic instruments, CC BY) --
the declared n=101 doesn't match any obvious `id` column (`EDNumber`
alone gives 101 uniques but is household/enumeration-district level, not
respondent level); needs a codebook before the true respondent id and
scale boundaries can be trusted.

All 25 tables across groups 1/2/3 consolidated into
`biblio_plos28_pmc5.csv` (25 rows, 13 papers), all `irw_output/*.csv`
files verified present -- see `TODO.md` for the pending upload item.
`plos_batch28_triage.csv`, `plos_batch28_retriage.csv`,
`pmc_batch5_triage.csv`, `pmc_batch5_retriage.csv`,
`biblio_batch28_group{1,2,3}.csv`, and the `/tmp` staging CSVs deleted --
fully captured in this entry and in `biblio_plos28_pmc5.csv`.

## Batch 29 (PLOS) / Batch 6 (PMC) / repo-mode response-time push (2026-08-13)

Targeted response-time discovery across all three modes in parallel, per
`datastandard.md`'s `rt` column (per-item response-level attribute, seconds,
paired with a valid `resp` -- not a whole-survey completion time). New terms
(checked against `search_terms_log.csv` first; most obvious RT task names
like Stroop/flanker/go-no-go/IAT/Posner/n-back/digit span/reading span/
visual search/mental rotation were already extensively searched in batch 18
and batch 19 and skipped as duplicates): **response time, response latency,
decision time, choice reaction time, simple reaction time, mouse-tracking
task, self-paced reading**. Dropped "psychomotor vigilance task" before
searching -- PVT trials have no accuracy dimension (responded/lapsed only),
so there's no valid `resp` to pair with `rt`. English-only for PLOS/PMC;
repo mode also translated into the standard 8 languages (63 queries total).
All terms logged in `search_terms_log.csv`.

**PLOS batch 29**: 662 candidates -> 4 `good`, 59 `human_assistance`
(retriaged: 9 worth_retrying, 24 human_review -> `human_review/
human_review_plos_batch29.csv`, 20 aggregate_continuous, 6
not_item_response), 28 not_item_response, 6 download_failed, 1 error.
Of the 4 `good`: only `10.1371/journal.pone.0190634` (Wingenbach et al.
2018, N=111) cleared the N>=100 floor; the other 3 (pone.0279360 N=58,
pone.0298534 N=20, pone.0123625 N=62) skipped outright.

**Written then retracted**: `data/wingenbach_2018_facial_emotion_rt.py` ->
N=111, 28 items (9 emotions x 3 intensity levels + neutral), `resp` =
unbiased hit-rate accuracy per condition (Wagner's-formula bias-corrected
%correct, 0-100), `rt` = mean response latency per condition in seconds.
Confirmed the "good flag needs a human glance" rule from SKILL.md: the
triage script's own pick (S1 Data) was a separate valence/arousal
mood-rating instrument, not the task data at all -- the real accuracy data
was S2 ("Unbiased hit rates data") and RT was S3 ("Response latencies
data"), found by reading the article's full SI file list. But both S2 and
S3 values are themselves **means across ~12 actors per condition**, not
raw per-trial responses -- exactly the composite-disguised-as-response
failure mode `datastandard.md`'s "Aggregate/index columns masquerading as
raw responses" section already documents from the `stenson_2021_
sleep_emotion` retraction (PLOS ONE batch 6, 2026-07-28: a mean/contrast
score across ~15 trials shipped as a raw per-trial rating). Missed the
same check here -- should have confirmed against the paper's Methods that
each S2/S3 cell was a single raw observation before shipping, not after.
Caught and retracted by ben-domingue 2026-08-13 before upload: **the IRW
is meant to hold trial-level responses specifically -- a per-subject
per-condition mean, even when correctly computed and even when it varies
meaningfully by item, doesn't qualify, no exception for RT/accuracy
tasks.** Script, `irw_output/wingenbach_2018_facial_emotion_rt.{csv,RData}`,
and `biblio_rt_batch29.csv` all deleted; no biblio row for this batch.

**PMC batch 6**: only 52 candidates total across the `JOURNALS` list for
these 7 terms -- thin surface for this construct in Europe PMC's covered
journals. 0 `good`; 3 `human_assistance` retriaged to 1 worth_retrying, 2
human_review (`human_review/human_review_pmc_batch6.csv`). The 1
worth_retrying (`PMC12376440`, text-coded Likert item columns) not chased
further this batch -- not RT-related, off this batch's target construct.

**Repo mode** (`candidates_rt_batch.csv`, 372 candidates across Zenodo/OSF/
Dryad/Figshare/DataCite/Dataverse): 0 `good`, 0 worth_retrying on first
pass; 15 `human_assistance` retriaged to 3 worth_retrying, 3 human_review
(`human_review/human_review_repo_rt_batch.csv` -- see note below on
filename), 3 aggregate_continuous, 6 not_item_response. The most promising
miss: `10.6084/m9.figshare.11320100` (Grundy, "The specificity and
reliability of conflict adaptation: A mouse-tracking study" -- Flanker +
Stroop tasks, per-trial `error` (accuracy) and `RT` columns, condition =
congruent/incongruent) was auto-flagged `not_item_response` because the
triage script picked up a spurious 2-value id column on the wide raw-data
sheet; manual inspection confirmed real per-trial structure (13536 rows,
96 trials x 2 tasks) but **N=71 participants, below the N>=100 floor** --
skipped, not a triage bug worth fixing. Of the 3 worth_retrying: a
discrete-choice pharmacy-preference study (N=6688) and a heart-rate-
complexity/cognitive-task study (text-Likert items) are both off this
batch's RT/accuracy target and logged in `TODO.md` as open leads rather
than chased now; a third (`Table 6.xls`, PLOS figshare, "Mean (SDs)
log-transformed RTs...") turned out to be a 5.6KB aggregate summary table,
not raw per-subject data -- dropped.

**Takeaway**: this batch shipped zero tables in the end. Response-time-
as-primary-outcome data is doubly scarce in this pipeline's reachable
sources: (1) most RT tasks in the literature run N<100 (typical
cognitive-psych lab sample sizes) -- tripped up 3 of 4 PLOS `good` rows
and the one strong repo-mode candidate (Grundy, N=71); (2) even the one
candidate that cleared N>=100 turned out to report per-condition means
rather than raw per-trial responses once actually inspected, which is
disproportionately likely for RT/accuracy tasks specifically since authors
routinely pre-aggregate trials into condition means before ever
publishing supplementary data. Confirmed 2026-08-13: **no exception to
trial-level-only for RT data** -- see the retraction note above. Future RT
searches should expect a very low true-good rate even among triage `good`
flags and verify trial-level-ness explicitly before writing a script, not
just before shipping.

`plos_batch29_triage.csv`, `plos_batch29_retriage_ha.csv`,
`pmc_batch6_triage.csv`, `pmc_batch6_retriage_ha.csv`, `candidates_rt_batch.csv`,
`irw_triage_rt.csv`, `irw_triage_rt_retriage_ha.csv` can be deleted --
fully captured in this entry, nothing pending upload from this batch.

**PR #1625 follow-up (2026-08-14 alt-source ad hoc run) -- all 3 `good`
rows are false positives, none shippable.** Human-reviewed each of the 3
`good` flags from the zenodo/dryad/figshare/datacite/scholars_portal/surf
alt-source discovery run:

- **Cognitive Activation Strategies and Self-Efficacy** (figshare
  10.25415/ujhb.33093377.v1, UJ repo, CC BY) -- real raw per-teacher
  Likert data, genuinely two separate scales in one workbook ("Cognitive
  activation" 24 items, "Self-efficacy" 26 items) that the triage script
  only partially counted (missed the second sheet entirely). But **N=64
  on both sheets, below the N>=100 floor** -- skipped outright, not a
  triage bug worth chasing further.
- **From Hesitation to Confidence: Longitudinal Changes in Medical
  Students' Presentation Skills and Anxiety** (figshare
  10.6084/m9.figshare.33110519.v2, CC BY) -- the workbook's only two
  sheets are "Students" (demographics) and "Summary table"; the "2 items"
  the triage script counted are literally columns named `Pre`/`Post`,
  themselves composite pre/post anxiety scores, plus `pre-A`...`post-F`
  columns that are per-subscale composite averages -- no raw item-level
  sheet exists anywhere in the file. Same failure mode as the
  `wingenbach_2018` retraction (composite/index columns masquerading as
  raw responses) -- dropped, not processed.
- **Validity and reliability of the Vietnamese version of the Index
  Dental Anxiety and Fear** (figshare 10.6084/m9.figshare.33140489.v1,
  Le, Son 2026, CC BY) -- real raw per-respondent item-level data,
  correctly flagged `multi_scale` (4 real subscales: IDAF-4C 8 items,
  IDAF-P 5 items, IDAF-S 10 items, DFS 20 items, N=291 first
  administration). Would otherwise have been the one real shippable lead
  from this batch, but **the "Second administration" file (test-retest,
  N=111) in the same dataset entry has a column of actual respondent full
  names** (Vietnamese names, e.g. "Võ Ngọc Hoài An") sitting next to the
  anonymized "Responser N" placeholder column -- confirmed present for
  the file's respondents, not a one-off. Per the 2026-08-12 PII rule
  (skip the whole candidate, never scrub-and-ship just the offending
  column), the entire candidate is skipped, including the otherwise-clean
  First administration file, since it's the same dataset/respondent pool.

**Takeaway**: the automated triage `good` flag doesn't check sample size
against the N>=100 floor or detect composite/aggregate columns
disguised as items -- both slipped past QC checks that only look for
structural/format errors, not content-level correctness. Worth adding
both checks to the triage script itself rather than relying on a human
catching every batch; logged as an open item in TODO.md.

## PLOS monthly full-sweep re-run + `--per-term-cap` fix verification (2026-08-15)

Verified the `--per-term-cap` fix (see `project_automated_finding_routines`
memory / commit `5d2c007`) by re-running `irw_discover_plos_monthly.py
--mode full` locally: 100/100 terms visited in one pass (vs 2/100 stuck on
"personality"/"grit" pre-fix), 95 candidates triaged -> `plos_monthly_
candidates_full_2026-08-15.csv` (2 `good`, 17 `human_assistance`, 74
`no_usable_file`, 2 `not_item_response`).

**Both `good` rows skipped, N<100 floor**: `10.1371/journal.pone.0180298`
(anxiety/avoidance, n=91) and `10.1371/journal.pone.0286080` (COVID-19
nurse vital-signs interpretation, n=24).

**17 `human_assistance` rows retriaged** (`irw_retriage_ha.py`): 5
`not_item_response`, 7 `aggregate_continuous` (auto-dropped), 5
`human_review` (hand-inspected below). All 5 `human_review` rows had
wildly-wrong `n_participants` in the original triage row -- the
low-confidence auto-mapping that failed with `dup_id_item` also botched
the row count, so a fresh direct download+re-parse was needed for each
before any N-floor judgment was possible (do NOT trust `n_participants`
on a `dup_id_item`-flagged row):

- `10.1371/journal.pone.0292844` (math anxiety, real N=97 not 2) -- still
  under the 100 floor once corrected. Skip.
- `10.1371/journal.pone.0159561` (financial education/impulsivity, N=414)
  -- N is fine, but `Extraversion1/2`, `Agreeableness1/2`, etc. range
  11-40 and `Risk1/2` range 5-20: these are summed subscale **totals**,
  not raw items (2 "items" per trait with that wide a range can't be
  single Likert responses). Reclassify `aggregate_continuous`, skip.
- `10.1371/journal.pone.0279062` (Bangladeshi adolescents' online
  addictive behaviors, N=428, cc-by) -- **real item-level data**, 4
  validated instruments in one file: `IGDS9-SF1`-`9` (gaming disorder),
  `GDT1`-`4`, `PHQ1`-`9` (depression), `GAD1`-`7` (anxiety), `BSMAS1`-`6`
  (Bergen social media addiction) -- each with an accompanying `Sum_*`
  composite column to exclude. Genuinely promising; flagged
  `worth_retrying`, script not yet written.
- `10.1371/journal.pone.0334555` (construction-industry political
  skill/relationship conflict, N=230, cc-by) -- **real item-level data**,
  clean short item codes already close to IRW-ready: `p1`-`p8` (political
  skill), `r1`-`r4` (relationship continuity), `u1`-`u8` (uncertainty),
  `c1`-`c3` (conflict), 1-5 Likert values. Flagged `worth_retrying`,
  script not yet written.
- `10.1371/journal.pone.0341726` (community pharmacist job
  satisfaction/mental health, N=385, cc-by) -- real item-level PSS-10/
  GAD-7/PHQ-9 batteries are in the file (0-3 Likert values confirmed) but
  buried under extremely verbose full-question-text column headers mixed
  with one-off demographic/yes-no items; needs careful column-range
  identification before a script can be written. Flagged `worth_retrying`
  (more work needed than the other two), not `human_review` since the
  content question is resolved -- only the extraction mechanics remain.

Triage artifact kept on disk (not deleted) until the 3 `worth_retrying`
scripts are written: `plos_monthly_2026-08-15_retriage_ha.csv`.

## PLOS monthly re-run — 2 worth_retrying scripts written (2026-08-15)

Wrote and verified processing scripts for 2 of the 3 `worth_retrying`
candidates surfaced above:

- `data/islam_2022_online_addiction.py` (`10.1371/journal.pone.0279062`,
  N=428, cc-by) -> 5 tables: `islam_2022_igds9sf` (9 items, 1-5),
  `islam_2022_gdt` (4 items, 1-5), `islam_2022_phq9` (9 items, 0-3),
  `islam_2022_gad7` (7 items, 0-3), `islam_2022_bsmas` (6 items, 1-5).
  No `id` column in source -- row index used. 9 non-PII covariates carried
  through (`cov_age`, `cov_sex`, `cov_marital_status`,
  `cov_academic_grades`, `cov_family_type`, `cov_monthly_income`,
  `cov_living_status`, `cov_hours_internet_use`, `cov_hours_playing_game`).
  `Sum_*` composite columns excluded. No imputation language found in the
  article text.
- `data/huo_2025_construction_partnerships.py`
  (`10.1371/journal.pone.0334555`, N=230, cc-by) -> 4 tables:
  `huo_2025_project_uncertainty` (8 items), `huo_2025_relationship_
  conflict` (4 items), `huo_2025_relationship_continuity` (3 items),
  `huo_2025_political_skill` (8 items), all 1-5. No `id` column and no
  covariates at all in the source SI file (paper mentions gender/tenure/
  work-status controls were collected but they aren't in the shared
  file). **Item-prefix mapping required reading the paper's Measures
  section, not just eyeballing column names**: raw columns are
  `p1`-`p8`/`r1`-`r4`/`u1`-`u8`/`c1`-`c3`, and a naive guess (`r`=
  continuity, `c`=conflict) would have been backwards -- the paper states
  "project uncertainty using eight items" (matches `u`, 8 cols),
  "relationship conflict based on four-item scale" (matches `r`, 4 cols),
  "relationship continuity...using three items" (matches `c`, 3 cols),
  and the shortened 8-item Political Skill Inventory (matches `p`, 8
  cols) -- confirmed by item-count cross-check against each prefix's
  actual column count, not assumed from the letters themselves.

`biblio_plos_monthly_2026-08-15.csv` (9 rows) prepared for Redivis
upload + dictionary-sheet paste, following the standard column order
(license "CC BY 4.0", Contributor "automated", Public Reshare "Public").
Third candidate (`10.1371/journal.pone.0341726`) left open in `TODO.md`
-- needs column-range extraction work before it can be scripted.
`plos_monthly_2026-08-15_retriage_ha.csv` deleted, fully captured here.

## PMC backlog sweep — good/human_assistance follow-up (2026-08-16)

Ben pointed at commit `3167335c34b826f0cf06c2118046c9aa41e3adf1` -- a
93-candidate full-mode `irw_discover_pmc.py` run (100 terms x `JOURNALS`)
that was **never merged to `main`** (it's the child of `d16de99`, which
*is* on `main`, but the candidates-CSV commit itself is dangling --
fetched directly by SHA via `git fetch origin <sha>` since no branch
contains it). Its 2 `good` + 25 `human_assistance` rows had not been
acted on. Recovered the candidates CSV from the dangling commit and
worked the pool:

**`good` (2 rows):**
- `10.7717/peerj.6254` (Matranga & Lumia 2019, THinK HPV-knowledge
  questionnaire, N=220, cc-by) -> `data/matranga_2019_hpv_knowledge.py`,
  16 items (`q1`-`q16`), resp 1-6, covariates `cov_recruitment_group`
  (Ob/Gyn dept vs. university clinic), `cov_age`, `cov_education`,
  `cov_place_of_birth`, `cov_place_of_living`. No PII (place-of-birth/
  living are categorical region codes, not free text).
- `10.1038/s41598-024-66435-w` (dispersal-ability radiation study,
  N=9) -- skipped outright, below the N>=100 floor.

**`human_assistance` (25 rows) -> `irw_retriage_ha.py`:** 10
`human_review`, 8 `worth_retrying`, 6 `aggregate_continuous`, 1
`not_item_response`.
- 10 `human_review` rows written to
  `human_review/human_review_pmc_batch7.csv` (all shared the generic
  "No clear automated classification" reason, not the usually-recoverable
  "could not confidently identify item columns" one -- not spot-checked
  further here).
- Of the 8 `worth_retrying` rows, investigated the ones with usable N:
  - `10.7717/peerj.19127` (Ajlan & Ashri 2025, dental faculty stem-cell
    knowledge/attitude, N=101 after dropping 1 duplicate `Fsno`, cc-by)
    -> `data/ajlan_2025_stemcell_knowledge.py`, 30 items (the file's
    "a"-suffixed numeric recodes of each Yes/No/Likert item), mixed
    3-/4-level ordinal scales per item (expected for this instrument).
    Covariates: age bracket, gender, nationality, speciality (all
    categorical, no PII in the free-text "specify" columns either --
    just nationality/speciality names).
  - `10.7717/peerj.3928` (ADDQoL-19/DTSQ-s diabetes QoL, N=372
    apparent) -- the "dup_id_item" flag was real duplicate `Code`
    values, not a longitudinal wave column; and the file itself only
    exposes 2 raw items per instrument (rest are subscale/total
    composites) -- not usable, dropped.
  - `10.7717/peerj.14740` (IFIH1/DHX58 hepatitis chronicity, N=1334
    apparent) -- raw file is SNP genotype data (`rs####` columns), not
    item-response data at all -- dropped, `not_item_response` in
    substance even though retriage called it `worth_retrying`.
  - `10.7717/peerj.20207` (N=52) and `10.7717/peerj.9845` (N=19) --
    below the N>=100 floor regardless of the id-mapping question,
    dropped.
  - `10.7717/peerj.20689` (N=59) -- below the N>=100 floor, dropped.
  - `10.7717/peerj.20180` (TRX training) and `10.7717/peerj.18241`
    (parental thermal conditions) -- text-coded Likert columns, N not
    yet checked; left open in `TODO.md`.
- Of the 6 `aggregate_continuous` rows, investigated the ones with N>=100:
  - `10.7717/peerj.20310` (Sinsopa & Tripakornkusol 2025, modified
    STOP-Bang OSA screening, N=188, cc-by) -- reclassified: the file mixes
    8 binary screening items with continuous anthropometric inputs and
    composite scores; the binary items themselves are genuine per-item
    data -> `data/sinsopa_2025_stopbang.py`, 7 items (dropped `bmi35`,
    constant/zero-variance in this BMI<35 inclusion-criteria sample),
    resp 0/1.
  - `10.7717/peerj.13069` (lacunes/T2DM cognitive impairment, N=227) --
    file is composite-only (MMSE grouping, Lacunar Score, Total SVD
    Score), no raw item columns -- dropped.
  - `10.7717/peerj.7208` (bee sulfoxaflor olfactory conditioning,
    N=102) -- the flagged file is one row per bee with an aggregated
    "learning level" count across trials, not per-trial data -- dropped.
  - `10.7717/peerj.19801` (N=92) and `10.7717/peerj.19555` (N=18) --
    below the N>=100 floor, dropped without further content review.
  - `10.1038/s41598-023-42115-z` (aversive-traits study, N=151) -- not
    yet checked against the paper text to confirm genuine continuous
    per-item ratings vs. a composite export; left open in `TODO.md`.
- `10.7717/peerj.17565` (herring gull diet preference) -- confirmed
  `not_item_response` (scraped article-prose fragment, not a dataset),
  dropped.

`biblio_pmc_backlog_2026-08-16.csv` (3 rows) prepared for Redivis upload
+ dictionary-sheet paste. The original dangling-commit candidates CSV and
the retriage output were both scratch files (never committed to the
repo) and are not tracked anywhere beyond this writeup.

## PMC monthly run 2026-08-16 clobbered the same-day backlog sweep

Ben pointed at commit `f34a51ed` -- the cron'd PMC monthly full-mode run
(20:58 UTC, 91 candidates: 0 `good`, 7 `human_assistance`, 41
`license_restricted`, 33 `no_usable_file`, 3 `not_item_response`, 5
`download_failed`, 2 `error`), merged to `main` as PR #1638.

**The defect.** `irw_discover_pmc_monthly.py` names its default output
`pmc_monthly_candidates_<mode>_<UTC-date>.csv`. That disambiguates weekly
from full, but *not* two full-mode runs on the same day -- and this
morning's manual backlog sweep (`3167335c`, issue #1637) had already
written that exact path. The evening run opened it `"w"` and replaced 93
rows with 91. Merging PR #1638 carried both commits onto `main`
(correcting this morning's writeup above: `3167335c` was dangling *at the
time it was written*, but PR #1638 later brought it in -- and clobbered
its file in the same merge). Verified: `git merge-base --is-ancestor` says
both `3167335c` and `f34a51ed` are ancestors of `origin/main`.

Two things limited the damage. The two runs share **zero PMCIDs** (93 vs
91, fully disjoint) -- the `pmc_seen_dois.csv` store did its job, so no
triage work was duplicated and the search space isn't exhausted. And the
morning run's 2 `good` + 25 `human_assistance` rows were already worked in
the entry above, so what was actually lost was the audit record of the
other 66 rows (the `license_restricted` / `no_usable_file` verdicts) --
the rows that keep a later sweep from re-triaging the same articles.

**Recovered.** Morning content restored to
`pmc_monthly_candidates_full_2026-08-16.csv` (93 rows) from `3167335c`;
evening content moved to `pmc_monthly_candidates_full_2026-08-16-2.csv`
(91 rows) -- i.e. the names the fix below would have produced. Both runs
had logged the same `output_file` in `search_terms_log.csv`; the
91-candidate row now points at the `-2` name.

**Fixed.** New `resolve_out_path()` in `irw_discover_updated.py` appends
`-2`, `-3`, ... when the default path is taken, printing a notice; an
explicit `--out` still overwrites (caller's choice). Wired into all three
scheduled discovery scripts -- `irw_discover_monthly.py`,
`irw_discover_plos_monthly.py`, `irw_discover_pmc_monthly.py` -- since all
three had the identical line. Suffixed names still start with `OUT_PREFIX`,
so `irw_discover_monthly.py`'s per-term `--since` lookup (which recognizes
its own rows by that prefix) keeps matching them.

## Dataverse WAF block recorded as a successful search (2026-08-17)

Prompted by reviewing commit `a1ed152` ("Log repos backlog-acceleration full
sweep (2026-08-17)"): 100 terms x `osf,dataverse`, 0 candidates. The 0 is
unremarkable on its own -- `irw_discover_monthly.py` is incremental and every
row carried `since=2026-08-14`, a 3-day OSF window. The problem was what the
run wrote down about Dataverse.

**The bug.** `discover()` tracks hard-blocked sources in `_blocked_sources`
and correctly stops calling them after the first `SourceBlocked` (the
fail-fast added 2026-08-14 in `64f0610`), but never told the caller.
`irw_discover_monthly.py` built its log note from `args.sources`
unconditionally, so all 100 rows asserted `sources=osf,dataverse` when
Dataverse had WAF-challenged every single request. `last_run_date()` reads
those rows on the next fire and advances `--since` accordingly -- so the
unsearched window was about to be skipped permanently, invisibly, with each
run re-certifying the gap as covered. Note the irony: that function's
docstring goes to real lengths to prevent exactly this failure for the
*source-set-mismatch* case, but a source that was in the set and silently
failed walked straight through the same guard.

Already happened twice: the 2026-08-14 monthly run was blocked too (its
output file contains 3 hits, all `osf`, 0 `dataverse`), and its rows claimed
`since=2026-08-03`. So Dataverse's genuinely-unsearched window was
2026-08-03 -> 2026-08-17 and widening every fire.

**Not a cloud-sandbox problem.** Probed from a local (non-cloud) IP:
`x-amzn-waf-action: challenge`, HTTP 202, 0 bytes -- identical from a browser
UA, from no UA, and on the homepage as well as `/api`. Site-wide block at
Harvard's edge; no header, UA, or backoff change touches it. Every other
connector (osf, zenodo, dryad, datacite, surf, aussda, plos, pmc eutils)
returned 200 in under 2s the same minute. This is single-source fragility,
not the automation being flagged.

**Fixed, three parts:**
- `blocked_sources()` in `irw_discover_updated.py` exposes the set
  `discover()` already tracked. Any caller that records what it searched must
  subtract it first.
- `irw_discover_monthly.py` logs only reachable sources, appends
  `blocked=<names>`, and warns on stderr. A blocked source therefore never
  advances its own `--since`; the next run finds no covering row and falls
  back (the fallback only ever searches *wider*, so it is always safe).
  PLOS/PMC monthlies were checked and need no change -- they gate on a
  seen-DOI ledger, not a date window, so a failed source there burns nothing.
- `search_terms_log.csv`: the 200 false rows (08-14, 08-17) corrected in
  place to `sources=osf; blocked=dataverse (retroactive correction ...)`.
  The code fix alone would not have healed a hole already written to disk.
  Verified after: a `osf dataverse` run now resumes from 2026-08-03, while an
  `osf`-only run keeps its tight 2026-08-17 watermark.

**Mitigation -- DataCite backfills a blocked repository.** `_DATACITE_SKIP`
filtered out `harvard dataverse` because the direct connector covered it;
while that connector is blocked the exclusion made Dataverse *doubly*
invisible (blocked at the front door, filtered at the side door). DataCite
still indexes it fine -- `publisher:"Harvard Dataverse" AND personality`
returns 321 DOIs. `_effective_datacite_skip()` now lifts a publisher's skip
exactly when its own connector is blocked, per `_DATACITE_FALLBACK_FOR`
(mapped for all 8 connectors, not just dataverse). Self-restoring: nothing
blocked next run means nothing un-skipped. Confirmed live -- with dataverse
blocked, DataCite surfaced `10.7910/dvn/rl99ks` (JobCannon Psychometric
Response Dataset), which the run would otherwise never have seen.

The backfill deliberately does *not* count as having searched the source:
DataCite's index is partial, so the `--since` window still reopens later.

**Second bug, found by smoke-testing that mitigation.** The backfill was
inert in the one mode that needs it. DataCite exposes only
`publicationYear` ("2026"), and `discover()`'s `--since` filter compared
raw strings: `"2026" < "2026-08-03"` is lexicographically True, so *every*
current-year DataCite record was being dropped -- precisely the recent ones
an incremental run wants. This was a live bug independent of the WAF
incident; DataCite has been in `SOURCES` all along, so any `--since` run
has been silently discarding its entire current-year yield. Now routed
through `_older_than()`, which compares at the coarsest granularity the two
values share: a year-only date is dropped only when its year precedes the
cutoff's year. Errs toward keeping, matching the existing rule that a
missing date isn't evidence a hit is old.

**Third gap, and the one that would have made all of the above cosmetic.**
The backfill was dormant where it mattered: `DEFAULT_SOURCES` was
`["osf", "dataverse"]`, so the scheduled repos routine never queried
DataCite at all and the skip-lifting logic could only fire for someone
passing `--sources ... datacite` by hand. `datacite` is now in the defaults,
listed last so the connectors it backfills for have their block detected
first. It earns its place independent of the WAF too -- it reaches ICPSR, UK
Data Service, DANS and hundreds of repositories no other connector covers,
with `_DATACITE_SKIP` preventing duplication of the ones that do.

One-time cost: `last_run_date()` requires a prior row whose sources are a
superset of the current set, so widening the set makes all 100 terms fall
back to the 90-day lookback (2026-05-19) for a single run rather than assume
DataCite was covered by history it never took part in. Deliberate -- the
fallback only ever searches wider. Runs after that re-narrow to the
incremental window.

Verified end-to-end against live services with Dataverse genuinely blocked:
fail-fast fires, DataCite lifts the skip, the year-only date survives
`--since 2026-01-01`, and `10.7910/dvn/krwi6e` (Validation of the Turkish
AI-Specific Teacher Attitude Questionnaire, 2026) comes back -- a Harvard
Dataverse record the pipeline was blind to on all three counts before.

**Also available, unused so far:** `dataverse.harvard.edu/oai?verb=Identify`
(OAI-PMH) returns 200 -- not behind the challenge. A worthwhile second route
if the WAF persists and the DataCite backfill proves too thin.

**Housekeeping note:** the cloud routine writes CRLF line endings into
`search_terms_log.csv` while local scripts write LF, so the file is mixed.
Harmless to `csv`, but a whole-file rewrite in text mode silently normalizes
every line and turns a 200-row edit into a 3,600-row diff. Four legacy rows
also carry unquoted commas in `notes` (they parse as 5 fields); irrelevant to
the monthly rows, but `_parse_logged_sources` would see a truncated note if
one ever landed in that shape.

## Triage burned WAF-blocked candidates as permanent verdicts (2026-08-17)

Follow-up to the entry above, and the more damaging half of it. Fixing
discovery only moved the problem one stage down: the same WAF blocks
triage's fetch paths (`_dataverse_files()` -> `/api/datasets/:persistentId`
and `polite_get()` -> `/api/access/datafile/`, both 202/0 bytes), so the
DataCite backfill was surfacing Harvard Dataverse candidates that triage
then could not open.

What happened to them was worse than "download_failed". `resolve_data_files()`
caught every exception and returned an empty file list, which is
indistinguishable from a dataset that genuinely has no tabular file -- so
`process_one()` recorded `no_usable_file`, reason "no resolvable tabular
file on landing page". That is a *sticky* verdict, and `run_batch()` appended
every triaged key to `repo_triage_seen_keys.csv` regardless of flag. Net
effect: a WAF-blocked candidate was permanently retired, with a false reason
on record, and would never be retried even after the block lifted. Same bug
class as the discovery-watermark one, one stage downstream and worse -- the
discovery version lost a date window, this one loses specific datasets.

**Fixed:**
- `FileListUnreachable` separates "couldn't reach the listing" from "read the
  listing, nothing tabular in it". `resolve_data_files()` raises instead of
  returning empty; `process_one()` maps both it and `SourceBlocked` to
  `download_failed`.
- `TRANSIENT_FLAGS = {"download_failed", "error"}` are excluded from
  `repo_triage_seen_keys.csv`. Retryable is not the same as evaluated. This
  is general -- it protects against any source outage, not just this WAF.
- `_dataverse_files()` detects `x-amzn-waf-action: challenge` and raises
  `SourceBlocked`; `run_batch()` then skips that source's remaining rows for
  the rest of the run (still recording them retryably) instead of spending a
  doomed 30s request per row.

Verified against the live block with 3 real Harvard Dataverse DOIs: one
request made rather than three, all three flagged `download_failed` with the
WAF reason, and nothing written to the seen-keys ledger.

**Ledger checked, no repair needed.** No Harvard Dataverse keys were retired
during the block window -- `repo_triage_seen_keys.csv` has 153 entries dated
2026-08-14 and none are `10.7910/DVN` or dataverse.harvard.edu (the 08-14
monthly run found only OSF hits, and the 08-17 run found nothing to triage).
The bug was live but hadn't yet cost us a specific dataset. It would have on
the next scheduled run, since `34a4ed6` had just started feeding Dataverse
candidates back into triage via DataCite.

## Cloud vs. local for the Dataverse search — revisited, no change (2026-08-17)

Asked whether these searches should move off the cloud routines. They
shouldn't; location is the wrong axis.

`202` + `x-amzn-waf-action: challenge` is a *JavaScript* challenge: the
client is expected to execute `challenge.js` and return a token. `requests`
and `curl` cannot, so they are blocked on any network. Confirmed by
reproducing identically from a local IP and from the cloud sandbox, with a
browser UA, with no UA, and on the site root as well as `/api`. Moving the
Dataverse search local restores nothing.

The axis that would matter is headless-HTTP-client vs. real browser, and we
are deliberately not crossing it -- see the TODO item for why (circumvents a
deliberate access control, brittle, and a bad long-term posture toward a
repository the project depends on). The sanctioned route is an allowlist
request; draft written to `dataverse_allowlist_request.md` for ben-domingue
to review and send via support.dataverse.harvard.edu.

Cloud routines themselves are fine and stay as they are. The one
cloud-specific access incident was the 2026-08-03 egress allowlist blocking
`api.osf.io`/`dataverse.harvard.edu` (fixed by widening it), and the GitHub
App write limitation from that same entry is resolved -- routines now push
their own branches and open their own PRs (#1636, #1638) and commit directly
(`a1ed152`). PMC and PLOS routines are landing candidates unattended. These
are narrow fixed-domain API connectors, a different shape of work from the
broad multi-domain web research that the sandbox whitelist genuinely does
break.

## Harvard's answer: deliberate, temporary, site-wide (2026-08-17, ticket #423164)

Reply to the allowlist request, same day:

> Harvard University IT has temporarily restricted non-browser API access to
> the site, in response to higher than usual traffic that has been impacting
> site performance and availability. This should be a temporary measure, and
> we expect to restore API access again once site traffic is back under
> control, and a more permanent solution is in place.

Confirms the diagnosis exactly -- deliberate, site-wide, aimed at
non-browser clients generally, nothing to do with IRW specifically or with
where our requests originate. It also settles the strategy: **wait, don't
chase.** No allowlist was granted, and pressing for a personal exception
while they are actively shedding load would be unlikely to work and a poor
posture toward a repository this project depends on. The TODO item is closed
to further action; only the restoration watch remains.

For the record on whether we contributed: our Dataverse footprint is ~500
discovery requests spread over ~4 minutes (100 terms x <=5 pages, 0.5s
spacing), plus triage at 1.5s/domain. Not plausibly a driver of a
site-performance incident, but worth knowing the number if they ever ask.

**Recovery burst -- the non-obvious consequence, and it needs handling.**
Every self-healing property built today compounds into a single spike aimed
at the site the moment it reopens:
- dataverse's `--since` window reopens at 2026-08-03 and widens every day
  the block persists (correct, and the whole point of the 759afc7 fix);
- all 100 terms already fall back to the 90-day lookback because datacite
  joined DEFAULT_SOURCES in 34a4ed6;
- every candidate held retryably by the ac92152 triage fix re-enters the
  queue at once, each costing a listing fetch plus a file download.

So the first post-restoration run is the widest, heaviest run this pipeline
has ever pointed at Harvard Dataverse -- landing on a site that just told us
it is struggling with traffic. Individually each behaviour is right; together
they are exactly the wrong first impression after asking for consideration.

Plan: make the first pass after restoration deliberately small and slow -- a
subset of terms, reduced `max_pages`, raised `PER_DOMAIN_DELAY` -- and only
return to normal cadence once it completes cleanly. Tracked as TODO item
(1b). Nothing to change until access actually returns; re-probe with
`curl -sI https://dataverse.harvard.edu/api/info/version`.

## Two content-level gaps in the `good` flag, closed (2026-08-17)

Longstanding TODO item, motivated by all 3 `good` rows in PR #1625 turning
out unshippable. Both fixes land in `irw_triage_updated.py` -- the TODO
guessed `irw_batch_updated.py`, but `triage_dataset()`/`run_qc()` is where
flags are actually decided.

**1. Sample-size floor.** `MIN_PARTICIPANTS = 100`, enforced as its own
terminal flag `below_min_n` rather than as a QC failure. A QC failure routes
to `human_assistance`, which would be wrong here: N is not something a human
can adjudicate or a script can fix, so a reviewer would only re-derive "too
small" by hand. Checked *after* the content gate, so a file that isn't item
response data is still reported as `not_item_response` -- the more useful
diagnosis -- rather than as too small. Caught PR #1625's N=64 case.

**2. Composite columns masquerading as items.** This is the subtle one: a
summary table melts into a perfectly well-formed id/item/resp frame and
passes every structural check above it. The only tell is what the items are
NAMED. `composite_items*` flags labels naming a computed quantity -- all of
them is a `fail` (-> human_assistance), some is a `warn`. Caught PR #1625's
`Pre`/`Post` + `pre-A`...`post-F` case, the same failure mode as the
`wingenbach_2018` retraction.

Matching is deliberately token-wise rather than substring, because the
obvious implementation is wrong in both directions: `meaning_1` must not
trip on "mean" and `scoreboard_2` must not trip on "score", while
`anxiety_total` and `PHQ9_score` must. `pre`/`post` are matched only against
a whole label (optionally with a short subscale suffix like `pre-A`), since
`pre_anxiety_3` is a genuine raw item at a pre-wave, not a composite.

Verified on both PR #1625 shapes, a clean N=150 control that must still flag
`good` (it does), a mixed file where one stray `total_score` sits among 10
real items (stays `good`, warns -- one composite shouldn't sink a real
scale), the N=99/100 boundary, and 14 label unit-cases including every
substring trap above.

`FLAG_ORDER` in `irw_batch_updated.py` gained `below_min_n`, placed after
`not_item_response` so the summary still sorts actionable flags first.

**Unrelated pre-existing breakage noticed while checking imports:**
`irw_process_queue.py` no longer imports -- it wants `QUEUE_SHEET_URL` from
`irw_discover_updated.py`, removed in `0bc73c8` when the queue sheet was
deprecated (2026-08-12). Not touched here; the script is likely obsolete
along with the sheet, but it should be either fixed or deleted rather than
left as a module that raises on import.

## Issue #1597 — TISP dataset (2026-08-17)

Manual, issue-driven processing rather than a discovery run — GitHub issue
[#1597](https://github.com/ben-domingue/irw/issues/1597) proposed by
@sinew-07, who asked to see the automated tooling applied to it as a worked
example.

- **Source**: Mede et al. (2025), *Perceptions of science, science
  communication, and climate change attitudes in 68 countries – the TISP
  dataset*, Scientific Data 12:114, DOI `10.1038/s41597-024-04100-7`.
  Data at <https://osf.io/5c3qd/>, file `02_data/survey-data/ds_main.csv`.
- **License**: OSF node reports license id `563c1cf88c5e4a3877f9e96a`;
  `GET https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96a/` resolves to
  "CC-By Attribution 4.0 International" — verified open, proceed.
- **Duplicate check**: no `data/*.py` embeds this DOI, and no
  `metadata/biblio.csv` row matches TISP/Mede/the DOI. Net-new.
- **File choice**: `ds_main` (cleaned, unweighted, N=71,922) over `ds_final`
  (adds post-stratification weights, drops to N=69,534) and `ds_full` (raw
  uncleaned) — keeps the full valid sample, per the issue's proposal.
- **Script**: `data/mede_2025_tisp.py`, downloading straight from the OSF
  file id so it's reproducible without a local copy. Source CSV is
  semicolon-delimited, UTF-8-with-BOM, and has a few invalid bytes in
  free-text columns (read with `encoding_errors="replace"`; those columns
  aren't carried through).
- **15 tables written.** The issue proposed only the four scales the data
  descriptor psychometrically validates; ben-domingue asked (2026-08-17) to
  add the remaining item batteries in the same questionnaire too, so all 15
  are shipped:

  | table | items | rows | ids | resp |
  |---|---|---|---|---|
  | `mede_2025_trust_scientists` | 12 | 862,607 | 71,915 | 1–5 |
  | `mede_2025_scipop` | 8 | 575,008 | 71,917 | 1–5 |
  | `mede_2025_outspokenness` | 3 | 215,638 | 71,912 | 1–5 |
  | `mede_2025_sdo` | 4 | 282,881 | 70,788 | 1–10 |
  | `mede_2025_sciinfo` | 10 | 714,665 | 71,901 | 1–7 |
  | `mede_2025_sciengage` | 4 | 287,182 | 71,908 | 1–7 |
  | `mede_2025_normperc` | 6 | 429,449 | 71,895 | 1–5 |
  | `mede_2025_willvul` | 3 | 210,348 | 70,463 | 1–5 |
  | `mede_2025_goals_priority` | 4 | 287,278 | 71,908 | 1–5 |
  | `mede_2025_goals_tackle` | 4 | 287,231 | 71,896 | 1–5 |
  | `mede_2025_clim_emotions` | 9 | 643,228 | 71,910 | 1–5 |
  | `mede_2025_clim_government` | 7 | 502,882 | 71,902 | 1–5 |
  | `mede_2025_clim_polsupport` | 5 | 331,613 | 69,927 | 1–3 |
  | `mede_2025_clim_weather_past` | 6 | 428,753 | 71,514 | 1–5 |
  | `mede_2025_clim_weather_future` | 6 | 407,894 | 68,056 | 1–5 |

  Named `mede_2025_*` per the `authorname_year_construct` convention rather
  than the issue's proposed `tisp_mede_2025_*` prefix (confirmed with
  ben-domingue).

- **Where the response ranges come from — do not shortcut this on a rerun.**
  The master questionnaire
  (`05_survey-materials/questionnaire/master/core-questionnaire_english.docx`,
  a `.docx` whose `word/document.xml` unzips to readable text) lists every
  block's numbered answer options verbatim, including the source variable
  name per row. That is the authoritative codebook here; the paper's prose
  only gives endpoint anchors for most batteries. Reading it caught a real
  in-range sentinel:

  **`CLIM_POLSUPPORT` is "Not at all (1) / Moderately (2) / Very much (3) /
  Not applicable (4)"** — 4 is a non-response code, not a scale point. It is
  ~5% of responses and, crucially, sits at a near-identical rate on all five
  items (3,395–4,539), so the cross-item *isolation* check in
  `datastandard.md` would have passed it. This is exactly the failure mode
  that section's "a distribution-shape check alone is not sufficient" warning
  describes. Valid max is set to 3 so the 4s are dropped. Every other
  battery's options are a plain 1–5 or 1–7 ladder with no extra category, and
  `SCIINFO`/`SCIENGAGE`'s smallest-at-the-top 1–7 shape is a genuine frequency
  ladder ("Never" … "Once or more per day"), not a hidden code.

- **Mechanical re-verification of all 15 tables after the sentinel finding**
  (prompted by ben-domingue asking whether the other tables had been
  re-checked on the same basis — the first pass had been an eyeball over a
  printed option dump, which is the same kind of check that nearly missed
  `CLIM_POLSUPPORT`). Redone as code, two ways:
  1. Scanned *every* numbered option label anywhere in the questionnaire
     against a non-response regex (`don't know|not applicable|prefer not|no
     opinion|refuse|n/a`). Exactly three hits besides the polsupport one, and
     all three are demographic, not item, columns: `DEM_GENDER` "Prefer not
     to say (99)" and `DEM_POL_conservative`/`DEM_POL_right` "I don't know
     (99)". All are coded `99`, all already NA in `ds_main`, none reachable
     as a `resp`.
  2. Per table, compared the shipped `resp` value set against the code set
     its own questionnaire block offers. 13 matched automatically;
     `TRUST_SCI` and `WILLVUL` needed a manual read because their variable
     names sit at line-start rather than in parentheses (60 option lines =
     12 items x 5, and 15 = 3 x 5, codes exactly 1-5, all substantive).
     No table ships a value absent from its codebook, and no table ships a
     non-substantive code.
- **`SCIENGAGE`'s 7 was queried and kept — deliberately.** 967 people report
  engaging in science-related *public protests* "once or more per day",
  which reads implausibly. It is not a sentinel: it is the documented top of
  the same frequency ladder `SCIINFO` uses, and the item's distribution is a
  smooth monotone decay (50,943 / 6,240 / 4,409 / 3,639 / 3,094 / 2,453 /
  967) — the *opposite* of the polsupport signature, which was a flat ~5%
  bump sitting at the top code at near-identical rates across all items.
  What it actually reflects is extreme/acquiescent responding: those 967
  respondents average 4.14 sevens across the 10 `SCIINFO` items vs 0.38 for
  everyone else, and 26.5% of them straight-line all four `SCIENGAGE` items
  vs 8.3% baseline. That is respondent behaviour, not a coding artifact, so
  it stays — filtering it would be silently editing the source. Downstream
  users can model it; a future reader tempted to "clean" it should read this
  note first.
- **QC (all 15)**: every item uses exactly its documented category set — the
  per-item distinct-category count equals the expected count on every item of
  every table, so there are no unfiltered sentinels and no isolated
  data-entry values. No duplicate `id`+`item`, no NaN, no fractional `resp`,
  column order `id,item,resp,cov_*` everywhere. `id` is the row index (source
  `ID_QUALTRICS` is unique per row but a non-numeric string). No imputation:
  `imput`, `MICE`, `LOCF`, `mean substitution` have zero occurrences in the
  paper's full text. PII scan over every string column (email/IP regex,
  counts only, values never printed) found zero hits; the free-text
  `DEM_GENDER_2_TEXT` column is dropped.
- **Batteries not fielded in every country** — all verified as whole-country
  omissions by design, not sparse damage (every country still present in a
  given table has ≥975 rows in it): SDO and weather-past drop 1 country
  (Malaysia; Albania), willvul 1 (Mexico), polsupport 2 (Argentina,
  Malaysia), weather-future 3 (Brazil, Malaysia, Mexico).
- **13 covariates carried through**: sample/team, country, continent, survey
  language, gender, age, age group, education, income (USD; source uses a
  comma decimal separator, converted), political conservatism, left–right
  placement, religiosity, urban/rural.
- **Biblio rows**: `biblio_issue1597.csv` (15 rows). **Done 2026-08-17** —
  ben-domingue uploaded all 15 tables to Redivis and pasted the biblio rows,
  then cleared the `irw_output/` files and the staging CSV as usual.
- **Deliberately excluded**: the single-item measures in the same file
  (`BENEFIT_ONESELF`, `TRUST_METHOD`, `TRUST_PEW`, `CLIM_TRUST`,
  `BENEFIT_REGION_MOST`/`_LEAST`) — IRW does not take single-item tables.

## Harvard Dataverse WAF block lifted (2026-08-17)

HMDC replied on ticket #423164 (https://help.hmdc.harvard.edu/Ticket/Display.html?id=423164):
"Scripted API access restrictions have been lifted. We're keeping an eye on
site traffic, but hope the traffic mitigation work we've done will prevent us
from needing to disable it again. Just beware that may be necessary if traffic
does spike back to where it was before."

Verified independently the same day, not taken on faith:
- `curl -sS -o /dev/null -w '%{http_code}' https://dataverse.harvard.edu/api/info/version` -> `200`
- `GET /api/search?q=grit+scale&type=dataset&per_page=2` -> `200` with real
  dataset JSON (e.g. `doi:10.7910/DVN/VBKUSG`, "Grit scale for Indian Adults").
  No `x-amzn-waf-action: challenge`, no 202/0-byte response.

So the block was site-wide and temporary exactly as they said, and waiting
rather than escalating or engineering around it was the right call. No code
change is needed to recover: the blocked-source handling added during the
outage is self-clearing — the dataverse `--since` window reopens from
2026-08-03, the DataCite publisher backfill switches itself off once dataverse
answers, and candidates parked as retryable re-enter triage on the next run.

**Open action: the first post-restoration run must be deliberately small and
slow** (see TODO.md item 1b). Their message explicitly reserves the right to
re-disable scripted access if traffic spikes back, and our self-healing design
otherwise aims a compounding burst at them the moment they reopen: a two-week
`--since` window, all 100 terms on a 90-day lookback, and the whole retryable
backlog re-triaging at once. Subset the terms, cut `max_pages`, raise
`PER_DOMAIN_DELAY` for that first pass, then return to normal cadence.

## Throttled first post-restoration Dataverse run (2026-08-17)

Executed the small-and-slow first pass required by TODO item 1b, immediately
after the WAF block lifted.

```
python3 irw_discover_monthly.py --mode weekly --sources dataverse \
  --out monthly_candidates_weekly_2026-08-17.csv
python3 irw_batch_updated.py monthly_candidates_weekly_2026-08-17.csv \
  --out monthly_triage_weekly_2026-08-17.csv
```

Deliberately scoped: the 15-term `HIGH_YIELD_TERMS` subset rather than the
~100-term `TERM_LIST`, and `--sources dataverse` alone so osf/datacite
couldn't muddy the read on whether Dataverse itself was healthy. ~75 requests
max at the built-in 0.5s page spacing, a few minutes wall clock.

**Dataverse is genuinely healthy.** All 15 terms returned from a live search;
all 15 `search_terms_log.csv` rows recorded `sources=dataverse` with no
`blocked=` segment, which is the honest-degradation machinery affirmatively
confirming the source was reached (contrast the 2026-08-17 full run's rows,
which carry the retroactive `blocked=dataverse` correction). Every term's
`--since` computed to 2026-08-03, confirming that correction took.

5 candidates -> 2 human_assistance, 1 not_item_response, 1 below_min_n,
1 download_failed.

- The `download_failed` is **not** a WAF re-block: a 403 on
  `DVN/7P3PFB`, whose license reads "access can be requested from the
  authors" — a real access restriction. Left out of
  `repo_triage_seen_keys.csv` for a later retry per normal behavior, but it
  will keep 403ing; not worth chasing.
- Two CC0 `human_assistance` rows worth eyes, both flagged only because
  `resp` had >50 unique values after the melt (the continuous/aggregate
  heuristic), so both need the usual manual check of whether real ordinal
  items are in there:
  - `DVN/TG1GYA` "Wellbeing, Race, Rurality and SES" — N=530,920, 42 items.
    Large enough to be worth real attention.
  - `DVN/X2C2PL` preoperative anxiety, gynecologic surgery, Vietnam —
    N=394, 59 items.

Notably the ~2-week reopened window yielded only 5 candidates from these 15
terms, so the feared recovery burst was modest in practice. Cleared to return
to normal cadence (`--mode full`, full source set, scheduled routines).

**Housekeeping:** `dataverse_allowlist_request.md` deleted 2026-08-17 as moot.
It held the allowlist request Ben sent to support@dataverse.harvard.edu on
2026-08-17; no allowlist was ever granted or needed, since HMDC lifted the
restriction site-wide instead (ticket #423164). Full text recoverable from git
history at commit `06ddd0c` if the block ever returns and a request is worth
re-sending — but note its central ask (allowlist us specifically) was the
wrong frame: the restriction was deliberate, temporary, and site-wide, and
waiting was what actually worked.

## GitHub issue #1562 — figshare 7582019 (2026-08-18)

Issue #1562 pointed at
`10.6084/m9.figshare.7582019.v1` (Da Silva & Ramos 2019, "Incomplete
Information Choices, Cognitive Ability and Personality", CC BY 4.0).

**Already partly processed.** The deposit's HEXACO-24 block shipped on
2026-08-01 as `dasilva_2019_hexaco24` via the "human eye" sheet review
follow-through — the `grep -rl "DOI: <doi>" ../data/*.py` duplicate check
in Step 3 caught it before any new work was done. Issue #1562 is therefore
a re-surfacing of an already-covered deposit, not a new candidate.

**What was still unshipped, and is now: 1 new table.**
- `dasilva_2019_crt.csv` — 3-item Cognitive Reflection Test (bat-and-ball,
  machines, lily pads), binary correct/incorrect, Portuguese, 211
  respondents, 633 rows. Scoring is the depositors' own (`Acerto N`
  columns on the workbook's "Completas" sheet); per-person sums reproduce
  their `Acertos Total` column exactly (284 = 284), so nothing was
  re-scored from the free-text answers.
- **id space is shared with `dasilva_2019_hexaco24`** — both follow "Base
  de dados" row order, and all 211 CRT ids are a subset of that table's
  240, so the two tables join per respondent.
- The join to recover those ids is on the submission timestamp, not the
  answer text: "Completas" stores cleaned numeric versions of the
  free-text answers ("100 minutos" → `100.0`), so an answer-text join
  fails on ~21 rows. One timestamp is shared by two distinct respondents;
  they're separable because only one answered all three CRT items, which
  every "Completas" respondent did by definition.
- **Workbook items 4-6 dropped.** They're a conditional alternate form,
  shown only to respondents who said they already knew the classic items,
  and were answered by 22 people — far under the N>=100 floor. Shipping
  them would have made a sparse block of an otherwise complete table.

Biblio row for the dictionary sheet: `biblio_issue1562.csv` (1 row).

## GitHub issue #233 — Harvard Dataverse DVN/QOO7QX (2026-08-18)

Issue #233 pointed at `doi:10.7910/DVN/QOO7QX`, "PROMIS Pediatric Measure
Evaluation" (Forrest, deposited 2020-12-21, published 2021-02-16). **CC0 1.0**,
confirmed on the Dataverse landing page's own license block (`rightsIdentifier:
CC0-1.0`), not a bare UUID. Not in the dictionary — no `QOO7QX` row, and the
existing `promis1wave1_*` tables are the *adult* PROMIS Wave 1 study
(`DVN/0NGAKG`), a different data collection.

**20 new tables**, ~1.38M responses, from `data/forrest_2021_promis_peds.py`.
Ten PROMIS pediatric item banks, each fielded in a child self-report and a
parent-proxy edition, calibrated on a sample pooled across school, clinic and
internet-panel settings:

| construct | child (ids / items) | proxy (ids / items) |
|---|---|---|
| family_belonging | 1845 / 55 | 960 / 55 |
| family_involve | 1845 / 58 | 958 / 58 |
| global_health | 3635 / 18 | 1807 / 21 |
| life_satisfaction | 1992 / 56 | 963 / 56 |
| meaning_purpose | 1895 / 55 | 926 / 55 |
| phys_activity | 2011 / 79 | 1032 / 79 |
| phys_stress | 1843 / 43 | 924 / 43 |
| positive_affect | 1869 / 53 | 909 / 53 |
| psych_stress | 1874 / 64 | 913 / 64 |
| strength | 1824 / 25 | 917 / 25 |

Decisions worth recording:
- **Child and proxy kept as separate files, not merged with a `rater` column.**
  The two editions are separately-worded, separately-calibrated instruments —
  the proxy items carry a `_PX`/`_Proxy` suffix and are reworded in the third
  person ("My child's life was perfect") — so they are two scales, not one
  scale with two raters.
- **`id` is `childid` for child files and `parentid` for proxy files.** Each
  proxy parent appears exactly once and rates exactly one child, so `parentid`
  identifies the rated child too; `childid` is missing for ~3% of proxy rows
  and so is not usable there. The global-health proxy file is the exception —
  it ships no `parentid` at all, and its `childid` is complete and unique.
- **Non-ordinal first categories dropped, per item.** Five items code a "not
  applicable" state as category 1 below the ordinal anchors: `PedGlobal9`/`10`
  (1 = Do not go to school), `PedGlobal12` (1 = Do not work a job), `PAC_M_016`
  (1 = Did not have recess), `PAC_M_019` (1 = Did not take gym/PE class), plus
  their proxy twins. Those responses were dropped — it's 728 responses on
  `PAC_M_016` alone, i.e. common enough to pass a rarity check while still not
  being a scale point. **"None" is not one of these**: on `PAC_M_029`/`030`/
  `067` and `PAC_S_003` it is the bottom of a duration scale ("None" / "Less
  than 15 minutes" / ... / "60 minutes or more") and was kept.
- **Composites dropped**: `cfull_theta`/`pfull_theta`/`cSF8_theta`/`cSF4_theta`
  and their SEs (IRT scores), and `pgh7`/`pgh7px` (sum of the PGH-7 items).
- **Duplicate ids.** Each child file had at most one exactly-duplicated row
  (dropped as redundant). Four proxy files had one id appearing twice with
  *conflicting* responses; both records were dropped, since there is no basis
  for picking one.
- **Covariates mapped to labels** from the deposit's codebook PDFs (gender,
  ethnicity, race, setting, chronic condition, respondent relationship, parent
  education); age and grade left numeric. The race codes are bit-flag values
  (1/2/4/8/16/32) but no combined value ever occurs, so each maps to one label.
- Sparse items are genuine, not a processing artifact: `PedGlobal4_Proxy` has
  176 responses because the source only asked it of 176 parents (the codebook
  shows 1631 missing), and `Global01_ProxyA`/`ProxyB` are two wordings of the
  same question, both fielded near-universally.

**Item text is available for every one of these 20 tables** — the deposit ships
20 codebook PDFs (plus `MySQLWorkbench.pdf` covering the proxy global-health
items) with the full stem and every response-option label. Item names were kept
in source form specifically so they join. Worth an `irw-auto-itemtext` pass
once these are uploaded.

Biblio rows for the dictionary sheet: `biblio_issue233.csv` (20 rows).

## Step 2b retriage of the four unlogged scheduled runs (2026-08-24)

The four scheduled cloud routines that ran 2026-08-18 → 2026-08-20 each
opened a PR carrying only its candidate CSV and committed its
seen-keys/search-terms bookkeeping to `main`, but **none of them ran
Step 2b**, none wrote `human_review/` rows, and none were logged here.
Confirmed by the absence of a `refined_flag` column in all four CSVs
(cf. the "Cloud runs skip retriage" note). Runs covered:

| run | PR | branch | rows | flags |
|---|---|---|---|---|
| PLOS weekly 2026-08-18 | #1664 | `automated/plos-weekly-2026-08-18` | 56 | 45 no_usable_file, 6 human_assistance, 5 below_min_n |
| PMC backlog 2026-08-19 | #1666 | `automated/pmc-backlog-2026-08-19` | 13 | 7 no_usable_file, 5 license_restricted, 1 human_assistance |
| PMC weekly 2026-08-19 | #1668 | `automated/pmc-weekly-2026-08-19` | 54 | 30 no_usable_file, 17 license_restricted, 3 below_min_n, 2 not_item_response, 2 human_assistance |
| repos backlog 2026-08-20 | #1673 | `automated/repos-backlog-2026-08-20` | 19 | 10 below_min_n, 4 human_assistance, 2 license_restricted, 2 download_failed, 1 no_usable_file |

No `good` rows in any of the four. Retriage of the 13 `human_assistance`
rows (11 distinct candidates — `DVN/NGRR1Q` appeared 3×) gave
5 `human_review`, 6 `aggregate_continuous`, 2 `worth_retrying`. The
`human_review` rows are archived as `human_review/human_review_plos_batch30.csv`,
`human_review_pmc_batch8.csv`, `human_review_pmc_batch9.csv`, and
`human_review_repo_2026-08-20.csv`.

**Every lead was then downloaded and inspected by hand** (the retriage
buckets are heuristic; three of them were wrong in both directions):

Drops — genuinely composite, no item-level data in the deposit:
- `10.1371/journal.pone.0277351` (Buddhism precepts / neuroticism, N=644):
  file holds `Neuro`, `CSI_dep`, `PSStot`, `SBI5-PP` — scale totals only.
- `10.1371/journal.pone.0339591` (exercise self-efficacy, 371 rows):
  `T1..T4 Exercise self-efficacy` totals only. Retriage called this
  `worth_retrying` on a longitudinal-design guess; the waves are real but
  each wave carries one composite, so it would be a single-item table.
- `10.1371/journal.pone.0276794` (adolescent well-being, N=377): six
  dichotomised subscale indicators × 2 waves, built for the LCA. Retriage
  called it `worth_retrying` on a text-Likert guess; the `.sav` is numeric
  0/1 composites.

Drops — not item-response data (these were the `human_review` rows, all
resolvable from the column list alone):
- `10.7717/peerj.14971` — maize combining-ability / grain-nutrient trial.
- PMC11225727 (`10.1016/...`, generative-AI-in-healthcare) — a qualitative
  review table (`Ranked by relevance`, `What`, `Why`, `How`, ...).
- `10.7910/DVN/CORNFB` — a systematic-review extraction sheet
  (`AI systems object of study`, `Antecedents`, `Mediators`, ...).
- `10.1371/journal.pone.0313538` and `10.1371/journal.pone.0242267` are
  left as genuine human_review: 0242267's CSV has a single tab-joined
  header cell (`id\tI1\tI2\t...`) — a delimiter problem, not a content one,
  and worth a re-read.

Real finds — three IRW-eligible datasets the runs would otherwise have
buried in the `human_assistance` bucket:
- **`10.1371/journal.pone.0279071`** (PLOS ONE, CC BY, N=1087): Chinese
  COVID stress survey, `S1_Dataset.xlsx`, item stems as column headers —
  PSS-10, a 28-item mood scale, a 20-item coping scale, and more. The
  `>50 unique values` trip came from the survey-metadata columns (`序号`,
  `所用时间`) being melted in with the items.
- **`10.1038/s41598-024-65095-0`** (Sci Rep, CC BY, N=1587): PSQI
  components, 10-item Barthel ADL, PHQ-9 (`P1..P9`), 3-item loneliness,
  alongside the composites that tripped the heuristic.
- **`10.7910/DVN/NGRR1Q`** (Harvard Dataverse, CC0, N=1200 × 2 waves):
  diaspora-attachment survey experiment with real Likert grids
  (`Q3grid_1..4`, `Q6grid_1..4`, `Q8grid_1..7`, `Q14_*`, `Q15_*`) plus a
  `treatment_group` column that maps to `treat`.

The 2 `download_failed` rows both resolve to "not openly accessible",
not to a transient error — reclassify rather than retry:
- `10.7910/DVN/7P3PFB` — dataset terms read "Access can be requested from
  the authors", so it was never open in the first place.
- `10.7910/DVN/FG3CCK` — dataset license is CC0 but the API reports
  `restricted=True` on `Replication_data.tab` itself.

**Pipeline note (Dataverse downloads):** `irw_batch_updated.py` builds a
bare `/api/access/datafile/<id>` URL and `requests` follows the `303`, so
the 403 it recorded here is a real, permanent access restriction, not a
transient fetch error. The gap is in the *classification*: a restricted
file lands in `download_failed`, which is a retry bucket, so it will be
re-attempted forever. `_dataverse_files()` already parses the file records
that carry `restricted` — worth flagging those as access-restricted at
resolve time instead. Note also that a deposit-level CC0 license does not
imply file-level access (`FG3CCK` is CC0 with `restricted=True` on the only
data file).
