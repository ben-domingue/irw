# IRW Automated Finding — TODO

## Cleaning scripts (irw_output/queue/ → irw_output/cleaned/)

For each: inspect queue file, write cleaning script in `data/`, save to `irw_output/cleaned/`, update `cleaned_index.csv`, add biblio sheet entry.

- [ ] `10_6084_m9_figshare_30903575_v2.csv` — Conspiracy Belief (autistic traits, schizotypy) — `human_assistance`; multi_scale (needs splitting), resp_ordinal
- [ ] `10_7910_dvn_nfrees.csv` — Burnout Assessment Tool (IRT, teachers) — multi_scale
- [ ] `10_7910_dvn_2iblrk.csv` — Personality + financial behaviour (handwriting)
- [ ] `10_7910_dvn_dwplbc.csv` — Self-reported Political Preference in China — multi_scale
- [ ] `10_7910_dvn_iek9pw.csv` — Personality + Entrepreneurship (Brazil) — multi_scale
- [ ] `10_6084_m9_figshare_26130403_v1.csv` — Quarter-Life Crisis (career indecision, wellbeing)
- [ ] `10_7910_dvn_y75cp2.csv` — Non-cognitive traits of DPT learners — multi_scale

## Pipeline improvements

- [ ] Re-run discovery with Zenodo fixed (hyphen bug committed) — Zenodo was completely down last run, all results missed
- [ ] Review 210 `human_assistance` rows in `triage.csv` for overlooked candidates
- [ ] Expand search terms — executive function tasks, reaction time paradigms, educational tests not yet covered

## Housekeeping

- [ ] Update `cleaned_index.csv` status from `cleaned` → `submitted` for the 4 uploaded datasets (pcss, mfq, dass21 x2) once Redivis upload is confirmed
