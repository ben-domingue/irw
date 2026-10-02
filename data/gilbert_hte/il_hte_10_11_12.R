# IL-HTE Econ, 10/11/12: Kim (2021) EPR - Reading Self Concept/Vocabulary
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Note: Based on the Stata data set, the MMRP items have already been reverse coded.

kim2021 <- read_dta(glue("{raw}/10 g1g2_analyticfile_public.dta")) |> 
  select(s_id,
         treat = s_itt_consented,
         cluster_id = school_grade,
         block_id = stratum,
         std_baseline = s_maprit_1819w_std,
         cov_white = s_white_num,
         cov_black = s_black_num,
         cov_asian = s_asian_num,
         cov_hispanic = s_hispanic_num,
         cov_male = s_male_num,
         cov_lep = s_lep_num,
         cov_iep = s_iep_num,
         cov_ses_low = s_ses_low,
         cov_ses_med = s_ses_med,
         cov_ses_high = s_ses_high,
         s_grade_center,
         contains("mmrp"),
         contains("s_ss"),
         contains("s_sci")) |> 
  select(-c(s_mmrp:s_mmrp_std)) |> 
  # make numeric
  mutate(across(contains("s_mmrp"), ~ parse_number(as.character(.))),
         # uncenter grade
         grade = if_else(s_grade_center > 0, 2, 1)
         )
  # # reverse code selected MMRP items
  # mutate(across(c(s_mmrp1, s_mmrp4, s_mmrp5,
  #                 s_mmrp7, s_mmrp8, s_mmrp10,
  #                 s_mmrp15, s_mmrp17, s_mmrp18,
  #                 s_mmrp19, s_mmrp20), ~ 4 - .))

# get the mmrp long
kim2021_a_i <- kim2021 |> 
  pivot_longer(contains("mmrp"),
               names_to = "item",
               values_to = "polyscore") |> 
  mutate(
    # a few non-integer polyscores, round down
    polyscore = floor(polyscore),
    score = if_else(polyscore == 1, 0, 1),
    time = 1,
    ) |> 
  drop_na(score) |> 
  select(s_id, item, time, score, polyscore) |> 
  drop_na()

# vocabulary items are response choices, not correct
# have to take the test to generate correct response
correct_answers <- crossing(
  grade = c(1,2),
  test = c("sci", "ss"),
  num = 1:12,
  let = c("a", "b", "c", "d")
) |> 
  as_tibble() |> 
  mutate(item = glue("s_{test}{num}{let}"),
         # manually input correct answers by taking the test
         correct = c(
           # G1 science
           1,0,1,0,
           1,0,0,1,
           1,0,1,0,
           1,1,0,0,
           0,1,1,0,
           1,0,1,0,
           1,0,0,1,
           0,1,1,0,
           0,1,0,1,
           0,1,1,0,
           1,1,0,0,
           1,0,0,1,
           # G1 social studies
           0,1,0,1,
           1,0,0,1,
           0,1,1,0,
           1,1,0,0,
           1,0,0,1,
           0,1,0,1,
           1,0,0,1,
           0,1,1,0,
           1,1,0,0,
           0,0,1,1,
           1,0,1,0,
           1,0,0,1,
           # G2 science
           0,0,1,1,
           1,0,0,1,
           0,1,0,1,
           1,0,1,0,
           1,0,1,0,
           0,1,1,0,
           0,0,1,1,
           0,1,1,0,
           1,1,0,0,
           1,0,0,1,
           0,1,1,0,
           0,1,0,1,
           # G2 social studies
           1,0,1,0,
           0,1,0,1,
           1,0,1,0,
           0,1,1,0,
           0,1,1,0,
           1,1,0,0,
           0,0,1,1,
           1,0,1,0,
           1,0,1,0,
           1,0,0,1,
           0,1,0,1,
           1,1,0,0
         )
         )

kim2021_scored <- kim2021 |> 
  pivot_longer(c(s_ss1a:s_ss12d, s_sci1a:s_sci12d),
               names_to = "item",
               values_to = "response") |> 
  select(s_id, treat, std_baseline, item, response, grade) |> 
  drop_na(response) |> 
  left_join(correct_answers, by = c("grade", "item")) |> 
  mutate(correct_response = if_else(response == correct, 1, 0)) |> 
  group_by(grade, s_id, test, num) |> 
  summarise(correct_sum = sum(correct_response)) |> 
  ungroup() |> 
  mutate(score = if_else(correct_sum == 4, 1, 0),
         item = glue("{test}{num}"))

# break into g1 and g2 because they had different questions
# but one vocabulary test because they are all vocab words
kim2021_b_i <- kim2021_scored |> 
  filter(grade == 1) |> 
  left_join(kim2021, by = "s_id") |> 
  select(s_id, item, score) |> 
  mutate(time = 1) |> 
  drop_na()

kim2021_c_i <- kim2021_scored |> 
  filter(grade == 2) |> 
  left_join(kim2021, by = "s_id") |> 
  select(s_id, item, score) |> 
  mutate(time = 1) |> 
  drop_na()

# person level
kim2021_p <- kim2021 |> 
  select(contains("_id"), treat, contains("cov_"), std_baseline)

# combine into relevant outcomes
kim2021_a <- kim2021_a_i |> 
  left_join(kim2021_p, by = "s_id")

kim2021_b <- kim2021_b_i |> 
  left_join(kim2021_p, by = "s_id")

kim2021_c <- kim2021_c_i |> 
  left_join(kim2021_p, by = "s_id")

rm(kim2021_a_i, kim2021_b_i, kim2021_c_i, kim2021_p, kim2021,
   kim2021_scored)
