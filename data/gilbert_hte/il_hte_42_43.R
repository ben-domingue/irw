# IL-HTE Econ, 42/43: Hussam (2022) AER - Mental Health/Cognitive Test
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# They combine a few measures for mental health; we follow their original approach.

# Mental Health:

# -   PHQ-9

# -   Perceived Stress

# -   Satisfaction with Life

# -   Locus of Control

hussam2022 <- read_dta(glue("{raw}/42 endline_processed.dta")) |> 
  # b means baseline
  # block appears to be a cluster, not a randomization block
  select(s_id = hhid1, cluster_id = b_block,
         # we care about the work treatment
         treat = b_treat_work,
         cov_female = gender,
         cov_household_size = member_count,
         phq_1:phq_9, b_phq_1:b_phq_9,
         # stress a has been reverse coded already
         stress_a_index, stress_b, stress_c,
         b_stress_a_index, b_stress_b, b_stress_c,
         life_satisfaction_a:life_satisfaction_d,
         b_life_satisfaction_a:b_life_satisfaction_d,
         # for locus of control a and c need to be reversed
         locus_of_control_a:locus_of_control_d,
         b_locus_of_control_a:b_locus_of_control_d,
         # digit span
         digit_spanforward_1a:digit_spanforward_7b,
         digit_spanbackward_1a:digit_spanbackward_7b,
         b_digit_spanforward_1a:b_digit_spanforward_7b,
         b_digit_spanbackward_1a:b_digit_spanbackward_7b,
         # math q
         math_literacy_a:math_literacy_c,
         b_math_literacy_a:b_math_literacy_c
         ) |> 
  # reverse code
  mutate(across(c(locus_of_control_a, locus_of_control_c,
                  b_locus_of_control_a, b_locus_of_control_c), ~ 7 - .),
         # stress a is 1-8 not 0-7, fix
         across(contains("a_index"), ~ . - 1)
         ) |> 
  # score so that higher is more positive, reverse stress and phq
  mutate(across(phq_1:phq_9, ~ 7 - .),
         across(stress_a_index:stress_c, ~ 7 - .),
         across(b_phq_1:b_phq_9, ~ 7 - .),
         across(b_stress_a_index:b_stress_c, ~ 7 - .)) |> 
  # no variance items have to be removed
  select(-c(b_digit_spanbackward_6b, b_digit_spanbackward_7a,
            b_digit_spanbackward_7b, 
            digit_spanforward_7a, digit_spanforward_7b,
            digit_spanbackward_6a, digit_spanbackward_6b)) |> 
  # all of the digit span items appear to be coded 1 = correct, 2 = wrong
  mutate(across(contains("digit_"), ~ if_else(. == 1, 1, 0))) |> 
  # pivot to wide
  pivot_longer(phq_1:b_math_literacy_c, names_to = "item", values_to = "polyscore") |> 
  mutate(time = if_else(str_starts(item, "b_"), 0, 1),
         item = str_remove_all(item, "b_"),
         outcome = if_else(str_detect(item, "phq|stress|locus|satisfaction|mental"), "mental health", "cognitive")) |> 
  arrange(s_id, item, time) |> 
  drop_na(polyscore)

# split
hussam2022_a <- hussam2022 |> 
  filter(outcome == "mental health") |> 
  # dichotomize - it works out so that 4 is the cutpoint for each!
  mutate(score = if_else(polyscore < 4, 0, 1))

hussam2022_b <- hussam2022 |> 
  filter(outcome == "cognitive") |> 
  mutate(score = polyscore) |> 
  select(-polyscore)

rm(hussam2022)
