# openESM 0003_hawks: plan

Hawks (2023). adults. 3x/day fixed time windows.
Data: 0003_hawks_ts.tsv, 3,109 rows, 122 people. Licence: CC BY-NC 4.0 (original: TODO).

## Proposed tables

**hawks_2023_panas_short_form** (10 items, scale 1..5)
- `nervous`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `afraid`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `enthusiastic`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `distressed`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `excited`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `scared`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `upset`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `alert`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `determined`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)
- `inspired`: Indicate to what extent you felt this way right before you started this survey. (observed 1.0..5.0, n=3,062)

**hawks_2023_anxiety_depression_s** (7 items, scale 1..5)
- `depressed`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)
- `restless_or_fidgety`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)
- `sadness_extreme`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)
- `worried`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)
- `hopeless`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)
- `irritated`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)
- `effort_everything`: Since the last survey, how often have you felt... (observed 1.0..5.0, n=3,062)

**hawks_2023_stress** (6 items, scale 1..5)
- `argument_stress`: Since the last survey, did you have an argument or disagreement with someone? If yes, how  (observed 1.0..5.0, n=3,062)
- `let_pass_stress`: Since the last survey, did anything else happen that you could have argued or disagreed ab (observed 1.0..5.0, n=3,062)
- `friend_relative_stress`: Since the last survey, did anything happen to a close friend or relative that turned out t (observed 1.0..5.0, n=3,062)
- `health_stress`: Since the last survey, did anything stressful happen regarding your personal health? If ye (observed 1.0..5.0, n=3,062)
- `other_stress`: Since the last survey, did anything else happen that most people would consider stressful? (observed 1.0..5.0, n=3,062)
- `covid_stress`: Since the last survey, how much time did you spend thinking about coronavirus/COVID-19? If (observed 1.0..5.0, n=3,062)

**hawks_2023_social_functioning_s** (1 items, scale 1..4)
- `socialfunc_interactions`: Since the last survey, about how many times did you talk or communicate with someone else? (observed 1.0..4.0, n=3,062)

**hawks_2023_sleepiness** (1 items, scale 1..9)
- `alert_sleepiness`: Please indicate your sleepiness during the 5 minutes before this survey by choosing the ap (observed 1.0..9.0, n=3,062)

**hawks_2023_context** (3 items, scale 1..4)
- `going_on`: There is a lot going on around me right now (observed 1.0..4.0, n=3,062)
- `concentrating`: I am having trouble concentrating right now. (observed 1.0..4.0, n=3,062)
- `noisy`: I am in a very noisy place right now. (observed 1.0..4.0, n=3,062)

**hawks_2023_executive_functionin** (6 items, scale 1..5)
- `finish`: To what extent are you currently having difficulty with following through on instructions  (observed 1.0..5.0, n=3,062)
- `organization`: To what extent are you currently having difficulty with organization? (observed 1.0..5.0, n=3,062)
- `mentaleffort`: To what extent are you currently having difficulty with avoiding, disliking, or reluctantl (observed 1.0..5.0, n=3,062)
- `forgetful`: To what extent are you currently having difficulty with being forgetful? (observed 1.0..5.0, n=3,062)
- `fidgeting`: To what extent are you currently having difficulty fidgeting with your hands or feet or sq (observed 1.0..5.0, n=3,062)
- `motor`: To what extent are you currently having difficulty with feeling “on the go” or acting as i (observed 1.0..5.0, n=3,062)

## Candidates (decide)

- `sleep_duration`: Time between typical bed and wake up time
- `social_functioning_composite`: Mean of three social functioning items on a 0-7 scale
- `ds_median_r_tc`: Median reaction time on correct responses
- `test_position`: Position of test within battery
- `crt_median_r_tc`: Median reaction time on correct responses
- `gcpt_dprime`: Accuracy computed as d-prime
- `mot_percent_correct`: Proportion of correct targets

## Not shipped

- `sitting_id`: numeric: Study session id
- `interruptions`: binary: Did anything interrupt
you during this
assessment?
- `study_time`: numeric: Time assessment was completed

## Flags (each needs a `resolution` in the spec)

1. no time stamps or counter: `wave` = (day - day_min) * beeps_per_day + (beep - beep_min) + 1. Check beeps_per_day against the sampling scheme ('3x/day fixed time windows'); no `date`.
2. 2 proposed table(s) hold a single item (hawks_2023_social_functioning_s, hawks_2023_sleepiness). Decide for each whether it belongs with a neighbouring table of the same questionnaire, stands alone, or is not shipped.
3. Tables are a first guess from file order, response scale, source, prompts asked at, and column-name prefixes. Read the codebook and split or merge so each table is one instrument or subscale (datastandard.md, 'One file per scale'); rename each `<author>_<year>_<construct>`, and set `script` to the record's name.
4. `candidates` holds columns that may or may not be items (binary checkboxes, counts, rating scales whose coding gives no anchors -- sleep_duration, social_functioning_composite, ds_median_r_tc, test_position, crt_median_r_tc, gcpt_dprime, mot_percent_correct). Move any that are responses into a table; the rest go to `not_shipped` with a reason. sleep_duration, social_functioning_composite, ds_median_r_tc, test_position, crt_median_r_tc, gcpt_dprime, mot_percent_correct
5. Read openESM's additional_comments: '(none)'
6. Licence: openESM 'CC BY-NC 4.0'; original deposit 'TODO' (not OSF or Zenodo; read https://github.com/zwihawks/PredictingMomentaryCog). IRW carries openESM's label when it is stricter (ruled 2026-10-04); if the two differ, the difference goes in the notes and in the report to openESM.
7. `reference` is drafted from openESM's BibTeX. Check it against the paper's DOI: the year (online vs print), page range and author list are where it goes wrong.
