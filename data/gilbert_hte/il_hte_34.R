# IL-HTE Econ, 34: Angelucci (2024) AER - Depression
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# `time` = 0.5 is the midline

angelucci2024 <- read_dta(glue("{raw}/34 mhtemp.dta")) |> 
  select(s_id = respid, 
         cluster_id = villid, 
         block_id = strat,
         treat = treatment, 
         cov_female = r_gender,
         cov_marital = r_marstat,
         cov_attend_school = r_school,
         cov_childcare = b9,
         cov_permission_work = b11,
         time = round,
         phq1:phq9) |> 
  # covariates are only inncluded at round 1, fill in
  group_by(s_id) |> 
  mutate(across(contains("cov_"), ~ mean(., na.rm = TRUE))) |> 
  ungroup() |> 
  # round 1 is baseline, round 2 is midline,
  # round 3 is endline
  mutate(time = time - 1,
         time = case_when(
           time == 0 ~ 0,
           time == 1 ~ .5,
           time == 2 ~ 1,
           time == 3 ~ 2,
           time == 4 ~ 3
         ),
         cov_marital = case_when(
    cov_marital == 1 ~ "Currently Married",
    cov_marital == 2 ~ "Never Married",
    cov_marital == 3 ~ "Widowed",
    cov_marital == 4 ~ "Separated/Divorced"
  )) |> 
  # treatment 4 is control
  mutate(treat = if_else(treat == 4, 0, 1),
  ) |> 
  # pivot to long
  pivot_longer(contains("phq"), names_to = "item",
               values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  # dichotomize at midpoint
  mutate(score = if_else(polyscore > 1, 1, 0))
