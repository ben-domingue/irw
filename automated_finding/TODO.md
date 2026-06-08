# IRW Automated Finding — TODO

## Cleaning scripts (irw_output/queue/ → irw_output/cleaned/)

For each: inspect queue file, write cleaning script in `data/`, save to `irw_output/cleaned/`, update `cleaned_index.csv`, add biblio sheet entry.

- [x] `10_6084_m9_figshare_30903575_v2.csv` — Conspiracy Belief / AQ-10 / Schizotypy — 5 scale files (`conspiracy_belief_schizotypy_asd__*.csv`)
- [x] `10_7910_dvn_nfrees.csv` — Burnout Assessment Tool — `burnout_assessment_tool_teachers.py`
- [x] `10_7910_dvn_2iblrk.csv` — Personality + Financial + Handwriting — 2 scale files (`personality_financial_handwriting__*.csv`)
- [x] `10_7910_dvn_dwplbc.csv` — Political Preference China — `political_preference_china.csv`
- [x] `10_7910_dvn_iek9pw.csv` — Personality + Entrepreneurship (Brazil) — 5 scale files (`personality_entrepreneurship_brazil__*.csv`)
- [x] `10_6084_m9_figshare_26130403_v1.csv` — Quarter-Life Crisis — 3 scale files (`quarter_life_crisis__*.csv`)
- [x] `10_7910_dvn_y75cp2.csv` — DPT Non-Cognitive Traits — 6 scale files (`dpt_noncognitive_traits__*.csv`)

## Biblio sheet entries needed

Add entries for each dataset to the IRW biblio Google Sheet:
- `10_6084_m9_figshare_30903575_v2` — Conspiracy Belief / AQ-10 / Schizotypy study
- `10_7910_dvn_2iblrk` — Personality + Financial Behaviour + Handwriting
- `10_7910_dvn_dwplbc` — Self-reported Political Preference in China
- `10_7910_dvn_iek9pw` — Personality + Entrepreneurship (Brazil)
- `10_6084_m9_figshare_26130403_v1` — Quarter-Life Crisis
- `10_7910_dvn_y75cp2` — DPT Non-Cognitive Traits

## Pipeline improvements

- [ ] Re-run discovery with Zenodo fixed (hyphen bug committed) — Zenodo was completely down last run, all results missed
- [ ] Review 210 `human_assistance` rows in `triage.csv` for overlooked candidates
- [ ] Expand search terms — executive function tasks, reaction time paradigms, educational tests not yet covered
