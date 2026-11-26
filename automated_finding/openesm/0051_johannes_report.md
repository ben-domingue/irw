# openESM 0051_johannes: plan

Johannes (2021). Dutch undergraduate students using social media. 8x semi-random with at least 45 minutes between surveys.
Data: 0051_johannes_ts.tsv, 2,828 rows, 77 people. Licence: CC BY 4.0 (original: CC BY 4.0).

## Proposed tables

**johannes_2021_wilhelm_schoebi_shor** (6 items, scale 1..7)
- `awake`: At this moment, I feel: (observed 1.0..7.0, n=1,684)
- `discontent`: At this moment, I feel: (observed 1.0..7.0, n=1,684)
- `calm`: At this moment, I feel: (observed 1.0..7.0, n=1,684)
- `without_energy`: At this moment, I feel: (observed 1.0..7.0, n=1,684)
- `well`: At this moment, I feel: (observed 1.0..7.0, n=1,684)
- `tense`: At this moment, I feel: (observed 1.0..7.0, n=1,684)

**johannes_2021_affect** (4 items, scale 1..7)
- `happy`: At this moment, I feel: (observed 1.0..7.0, n=1,684)
- `stressed`: How much stress are you experiencing right now? (observed 1.0..7.0, n=1,684)
- `vigilance_salience_mediated`: In the last half an hour, how much were you thinking about mediated interactions (e.g., ph (observed 1.0..7.0, n=1,684)
- `salience_ft_f`: In the last half an hour, how much were you thinking about face-to-face interactions? (observed 1.0..7.0, n=1,684)

**johannes_2021_valence** (3 items, scale 1..7)
- `valence_mediated`: How pleasant were those thoughts about mediated interactions? (observed 1.0..7.0, n=1,684)
- `valence_ft_f`: How pleasant were those thoughts about face-to-face interactions? (observed 1.0..7.0, n=1,684)
- `valence_activity`: How pleasant was what you were doing in the last half an hour? (observed 1.0..7.0, n=1,684)

**johannes_2021_cognitive_load** (1 items, scale 1..7)
- `concentration_extent`: The activity required all my mental capacities. (observed 1.0..7.0, n=579)

**johannes_2021_attention** (3 items, scale 1..7)
- `vigilance_reactibility`: In the last half an hour, when I received an online message, I immediately gave it my full (observed 1.0..7.0, n=1,684)
- `vigilance_monitoring`: In the last half an hour, I was constantly monitoring what was happening online. (observed 1.0..7.0, n=1,684)
- `social_pressure_phone`: In the last half an hour, I felt a social obligation to be available for mediated interact (observed 1.0..7.0, n=1,684)

## Candidates (decide)

- `prompt_duration`: How long participants took to fill out a probe (in seconds)
- `reactibility_survey`: The time between receiving the survey and opening the survey (in seconds)
- `concentrated_activity_binary`: In the last half an hour, I was engaged in a performance-related activity (e.g., an activi

## Not shipped

- `date`: Date: Date
- `time_prompt`: PosixCt: Time of the prompt
- `survey_taken`: binary: Survey taken
- `time_survey`: PosixCt: Time of the survey
- `number_days_total`: numeric: Total number of days
- `prompt_id`: numeric: Identifier variable for the prompt
- `fraction_of_days_with_notification`: numeric: Fraction of days with notification
- `phone_use`: numeric: Phone use duration
- `social_media_use`: numeric: Social media use duration
- `social_media_use_no_notification`: numeric: Social media use without notification duration
- `reactibility_notification_avg`: numeric: Average notification reactibility
- `reactibility_notification_sd`: numeric: Variability notifcation reactibility
- `reactibility_social_notification_avg`: numeric: Average social media notification reactibility
- `reactibility_social_notification_sd`: numeric: Variability social media notification reactibility
- `concentrated_activity_alone`: categorical: Concentrated activity company

## Flags (each needs a `resolution` in the spec)

1. `wave` = each person's prompts numbered in scheduled_time order (openESM time columns, best first: ['scheduled_time', 'time_prompt', 'time_survey']). `date` = scheduled_time as Unix seconds. Data run 2018-02-26 08:15 .. 2018-05-24 18:05 as written. Set date.window from the paper's collection period.
2. Time zone of scheduled_time. Written with a `Z`, but in 0072_neubauer and 0056/0057_ryvkina the `Z` stamps are local time. Hour-of-day counts as written: 7h:156, 8h:216, 9h:234, 10h:220, 11h:203, 12h:269, 13h:227, 14h:238, 15h:257, 16h:238, 17h:208, 18h:259, 19h:103. No Unix time column to check against: compare with the paper. Set date.tz to 'UTC' if the stamps are true UTC, or to the study's IANA zone (e.g. 'Europe/Berlin') if they are local time, and say how you know in date.tz_evidence.
3. time order and ['counter'] order disagree for 2798 prompts. Usually the time stamp is right (in 0018_bailon the file listed App rows before Web rows); confirm.
4. 1 proposed table(s) hold a single item (johannes_2021_cognitive_load). Decide for each whether it belongs with a neighbouring table of the same questionnaire, stands alone, or is not shipped.
5. Tables are a first guess from file order, response scale, source, prompts asked at, and column-name prefixes. Read the codebook and split or merge so each table is one instrument or subscale (datastandard.md, 'One file per scale'); rename each `<author>_<year>_<construct>`, and set `script` to the record's name.
6. `candidates` holds columns that may or may not be items (binary checkboxes, counts, rating scales whose coding gives no anchors -- prompt_duration, reactibility_survey). Move any that are responses into a table; the rest go to `not_shipped` with a reason. prompt_duration, reactibility_survey, concentrated_activity_binary
7. openESM says cross-sectional (baseline) data exist. Covariates such as age and gender are not handled by this tool: add them by hand to the generated script if wanted (neubauer_2023_stecco does), or note why not.
8. Read openESM's additional_comments: 'some participants pre-excluded due to compliance by authors'
9. Licence: openESM 'CC-BY 4.0'; original deposit 'CC BY 4.0' (OSF API, node ps3rk). IRW carries openESM's label when it is stricter (ruled 2026-10-04); if the two differ, the difference goes in the notes and in the report to openESM.
10. `reference` is drafted from openESM's BibTeX. Check it against the paper's DOI: the year (online vs print), page range and author list are where it goes wrong.
