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
