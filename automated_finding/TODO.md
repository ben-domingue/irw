# IRW Automated Finding — TODO

## Cleaning scripts (irw_output/queue/ → irw_output/cleaned/)

**Priority queue (new good candidates, not yet processed):**
- [x] `10_7910_dvn_ireejj.csv` — AI Awareness & Attitudes in Bosnia (386p / 51i) — already on Redivis (karajko2025_ai_benefit/risk/governance/trust from batch 4); skip
- [x] `10_7910_dvn_atlxc5.csv` — Non-compliance task replication data (414p / 32i) — already on Redivis (xu2024_noncompliance/self_efficacy/emotional_exhaust/turnover_intent/unethical_behav from batch 4); skip
- [x] `osf_h6gqf.csv` — Resting state fMRI / Dark Triad DDDT (129p / 3 subscale sums) — skipped; only subscale sum scores, not individual item responses

- [x] `10_6084_m9_figshare_30903575_v2.csv` — Conspiracy Belief / AQ-10 / Schizotypy — 5 scale files
- [x] `10_7910_dvn_nfrees.csv` — Burnout Assessment Tool
- [x] `10_7910_dvn_2iblrk.csv` — Personality + Financial + Handwriting — 2 scale files
- [ ] `10_7910_dvn_dwplbc.csv` — Political Preference China — on hold (0-response ambiguity; anchor labels not documented)
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
- [x] Process `recoverable_format` cases — results:
  - DVN/AAJSJ7: skipped — fixation count data from psycholinguistics experiment, not Likert responses
  - Soccer/Lindström 2021 (osf.io/14980251): 4 files (lindstrom2021_honesty_humility/team_identification/conscientiousness/violent_intentions); N=212-231; 1-7 Likert
  - HEXACO Teamwork/Zähl 2023 (osf.io/jb94w): 7 files (zaehl2023_hexaco + 6 TWQ subscales); N=54; 1-5 Likert
  - Sleep Quality/Merlo 2025 (figshare 30195541): 5 files (merlo2025_eet + 4 eng subscales); N=1065; PSQI+TECH excluded
  - Biblio entries in /tmp/biblio_batch5.csv (16 rows)
- [ ] Process 7 SAPA annual releases (2017–2024) — all CC0, none in IRW yet (existing entries are DVN/AD9RVY and DVN/SD7SVE, different releases)
  - DOIs: DVN/PNGUT5 (2017), DVN/7A9YMV (2018), DVN/FUUB2Q (2019), DVN/YOEEDQ (2020), DVN/JOGYUD (2021), DVN/BVF52I (2022), DVN/3BTT82 (2023-24)
  - Batch script grabbed ItemInfo.csv (codebook); actual data is SAPAdata{dates}.csv (35–193MB each)
  - File IDs: 10988792, 10988863, 10988866, 10988879, 10988881, 10988884, 10988887
  - Format: wide sparse (person × q_number items), 1-6 Likert + NA, ~135 items; covariates: sex, age, english
  - Decision needed: process all 7 years separately, most recent only, or pool with cov_year
- [ ] Spot-check top `worth_retrying` cases (AI Literacy 1146p/54i, Cognitive Dissonance 1201p/39i, Body Checking 216p/180i, Conspiracy Belief 373p/109i)
