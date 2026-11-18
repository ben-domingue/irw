# openESM 0075_ballou: plan

Ballou (2025). 18-40 year old people who play video games. 1x/day at 2 pm local time.
Data: 0075_ballou_ts.tsv, 16,346 rows, 1284 people. Licence: CC0 1.0 (original: TODO).

## Proposed tables

**ballou_2025_gaming** (6 items, scale 1..7)
- `gaming_autonomy`: I could play in the way I wanted. (observed 1.0..7.0, n=12,409)
- `gaming_wish_else`: I often found myself wishing I could do something else. (observed 1.0..7.0, n=12,409)
- `gaming_progress`: I felt that I made progress while playing. (observed 1.0..7.0, n=12,409)
- `gaming_disappointed`: I felt disappointed with my performance. (observed 1.0..7.0, n=12,409)
- `gaming_relationships`: I felt I formed relationships with other players and/or characters. (observed 1.0..7.0, n=12,409)
- `gaming_toxic`: Interactions with other players and/or characters felt toxic to me. (observed 1.0..7.0, n=12,409)

**ballou_2025_needs** (6 items, scale 1..7)
- `needs_autonomy_satisfied`: The next statements tap into your experiences today. Please indicate for each of the state (observed 1.0..7.0, n=16,044)
- `needs_autonomy_frustrated`: The next statements tap into your experiences today. Please indicate for each of the state (observed 1.0..7.0, n=16,044)
- `needs_competence_satisfied`: The next statements tap into your experiences today. Please indicate for each of the state (observed 1.0..7.0, n=16,044)
- `needs_competence_frustrated`: The next statements tap into your experiences today. Please indicate for each of the state (observed 1.0..7.0, n=16,044)
- `needs_relatedness_satisfied`: The next statements tap into your experiences today. Please indicate for each of the state (observed 1.0..7.0, n=16,044)
- `needs_relatedness_frustrated`: The next statements tap into your experiences today. Please indicate for each of the state (observed 1.0..7.0, n=16,044)

**ballou_2025_how_stressful** (7 items, scale 1..4)
- `how_stressful_argument`: How stressful was this stressful event? Argument or disagreement (observed 1.0..4.0, n=513)
- `how_stressful_discrimination`: How stressful was this event? Discrimination (observed 2.0..4.0, n=43)
- `how_stressful_friend_rel`: How stressful was this event? Issue affecting a friend or relative (observed 1.0..4.0, n=393)
- `how_stressful_health`: How stressful was this event? Health issue (observed 2.0..4.0, n=594)
- `how_stressful_home_issue`: How stressful was this event? Home issue (observed 1.0..4.0, n=521)
- `how_stressful_other`: How stressful was this event? Other (observed 1.0..4.0, n=531)
- `how_stressful_work_school`: How stressful was this event? Work or school issue (observed 1.0..4.0, n=473)

**ballou_2025_sleep_quality** (1 items, scale 1..5)
- `sleep_quality`: How do you rate the quality of your sleep? "Sleep Quality" is your sense of whether you sl (observed 1.0..5.0, n=16,054)

## Candidates (decide)

- `played24hr`: Played Last 24 Hours
- `had_stress`: Did anything happen to you in the last 24 hours that most people would consider stressful?
- `affective_valence`: How are you feeling right now?
- `life_satisfaction`: I was satisfied with my life today.

## Not shipped

- `date`: Date: Date
- `survey_duration`: numeric: Survey Duration
- `social_singleplayer`: other: Single-player
- `social_friends_realworld`: other: Real-world Friends
- `social_friends_online`: other: Online-only Friends
- `social_strangers`: other: Strangers
- `most_recent_game`: freetext: Most Recent Game
- `most_recent_game_plat`: categorical: Most Recent Game Platform
- `displaced_activity`: freetext: Displaced Activity
- `bpnsfs_dup_item`: other: Duplicated Item
- `bpnsfs_dup_score`: other: Duplicated Item Score
- `bpnsfs_failed_att_check`: other: Failed Attention Check
- `stress_events_argument`: categorical: Argument
- `stress_events_discrimination`: categorical: Discrimination
- `stress_events_friend_rel`: categorical: Friend or Relative
- `stress_events_health`: categorical: Health
- `stress_events_home`: categorical: Home
- `stress_events_other`: categorical: Other
- `stress_events_work_school`: categorical: Work or School
- `day_type`: categorical: Day Type
- `baseline_day`: Date: Baseline Day
- `ideal_baseline_day`: Date: Ideal Baseline Day
- `n_valid`: numeric:
- `original_wave`: other:

## Flags (each needs a `resolution` in the spec)

1. no time stamps or counter: `wave` = (day - day_min) * beeps_per_day + (beep - beep_min) + 1. Check beeps_per_day against the sampling scheme ('1x/day at 2 pm local time'); no `date`.
2. 1 proposed table(s) hold a single item (ballou_2025_sleep_quality). Decide for each whether it belongs with a neighbouring table of the same questionnaire, stands alone, or is not shipped.
3. Tables are a first guess from file order, response scale, source, prompts asked at, and column-name prefixes. Read the codebook and split or merge so each table is one instrument or subscale (datastandard.md, 'One file per scale'); rename each `<author>_<year>_<construct>`, and set `script` to the record's name.
4. `candidates` holds columns that may or may not be items (binary checkboxes, counts, rating scales whose coding gives no anchors -- affective_valence, life_satisfaction). Move any that are responses into a table; the rest go to `not_shipped` with a reason. played24hr, had_stress, affective_valence, life_satisfaction
5. openESM says cross-sectional (baseline) data exist. Covariates such as age and gender are not handled by this tool: add them by hand to the generated script if wanted (neubauer_2023_stecco does), or note why not.
6. Read openESM's additional_comments: 'Part of the "open play" project; more video game and time use data and additional surveys available on Zenodo and GitHub (https://github.com/digital-wellbeing/open-play). Find the modified license on GitHub and Zenodo.'
7. Licence: openESM 'CC0 1.0 - modified'; original deposit 'TODO' (not OSF or Zenodo; read https://github.com/digital-wellbeing/open-play/tree/main/data). IRW carries openESM's label when it is stricter (ruled 2026-10-04); if the two differ, the difference goes in the notes and in the report to openESM.
8. `reference` is drafted from openESM's BibTeX. Check it against the paper's DOI: the year (online vs print), page range and author list are where it goes wrong.
