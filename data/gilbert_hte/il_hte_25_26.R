# IL-HTE Econ, 25/26: Schreinemachers (2020) GFS - Food Knowledge/Preferences
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# they have parent and student data, focusing on student here
schrein2020 <- read_csv(glue("{raw}/25 Survey data_anonymized.csv")) |> 
  select(s_id = HHID, cluster_id = A9, treat = treatment,
         time = endline,
         cov_female = A3,
         cov_child_age = B2_a,
         contains("S11"),
         contains("S14")) |> 
  mutate(treat = if_else(treat == "Treatment", 1, 0)) |> 
  # score the remainder of the test
  mutate(
    across(c(S14_3, S14_6, S14_10, S14_13), ~ if_else(. == 1, 1, 0)), # 1 correct
    across(c(S14_2, S14_7, S14_8, S14_11), ~ if_else(. == 2, 1, 0)), # 2 correct
    across(c(S14_1, S14_4, S14_9, S14_12, S14_14), ~ if_else(. == 3, 1, 0)), # 3 correct
    across(c(S14_5, S14_15), ~ if_else(. == 4, 1, 0)), # 4 correct
  )  |> 
  # pivot to long
  pivot_longer(starts_with("S1"), 
               names_to = "item",
               values_to = "polyscore") |> 
  # dichotomize at midpoint
  mutate(score = if_else(polyscore > 2, 1, 0),
         outcome = if_else(str_starts(item, "S11"), "pref", "know")) |> 
  # age covariate is only at time 0, fill in
  group_by(s_id) |> 
  mutate(cov_child_age = mean(cov_child_age, na.rm = TRUE)) |> 
  ungroup() |> 
  # drop missing item responses
  drop_na(polyscore)

# separate into the separate outcomes
schrein2020_a <- schrein2020 |> 
  filter(outcome == "pref") |> 
  arrange(s_id, item, time)

schrein2020_b <- schrein2020 |> 
  filter(outcome == "know") |> 
  mutate(score = polyscore) |> 
  select(-polyscore) |> 
  arrange(s_id, item, time)

rm(schrein2020)
