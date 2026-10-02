# IL-HTE Econ, 65/66/67: O'Connor (2024) MH&P - Mental Health
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Omitting the primary outcome (MHRES) because it's continuous. The paper says matched pairs, but the blocking variable is not in the data set, so ignoring.

oconnor2023 <- read_csv(glue("{raw}/65 community_sport.csv")) |> 
  clean_names() |> 
  # remove extra stuff at the bottom
  drop_na(progress) |>
  # clean up covariates (based on paper)
  mutate(treat = if_else(treat_ctrl == 1, 1, 0),
         cov_male = if_else(gender == 2, 1, 0),
         cov_age = case_when(
           age_bracket == 1 ~ "18-24",
           age_bracket == 2 ~ "25-34",
           age_bracket == 3 ~ "35-44",
           age_bracket == 4 ~ "45-59",
           age_bracket == 5 ~ "60+"
         ),
         # some duplicate IDs (but different responses)
         # remake
         s_id = row_number()
         ) |> 
  # limit to relevant vars
  select(s_id, cluster_id = club_code, treat,
         cov_age, cov_male,
         # outcome 1: knowledge of resources, use full scale
         contains("mhl_"),
         # outcome 2: help seeking range/ghsq
         contains("ghsq"),
         # outcome 3: mental health stigma - based on article
         # labelled BINT in data but SODIST in article, still 4 items on
         # same scale, so keeping
         contains("bint")
         ) |> 
  # remove sum scores
  select(-contains("tot"), -contains("sqrt"),
         -contains("lg")) |> 
  # pivot to long
  pivot_longer(bomhl_1:bint_4_t2, 
               names_to = "item", values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  mutate(outcome = word(item, 1, 1, sep = "_"),
         time = if_else(str_detect(item, "t2"), 1, 0),
         # remove suffix from item
         item = str_remove(item, "_t2"),
         # all on 5-point scales, dichotomize at 1/2 vs. 3/4/5
         # for first 2, cut at 4 for last outcome because much more positive scores/ceiling
         score = if_else(polyscore > 2, 1, 0)
         )

# break into different outcomes
oconnor2023_a <- oconnor2023 |> 
  filter(str_detect(outcome, "mhl")) |> 
  select(-outcome)

oconnor2023_b <- oconnor2023 |> 
  filter(outcome == "ghsq") |> 
  select(-outcome)

oconnor2023_c <- oconnor2023 |> 
  filter(outcome == "bint") |> 
  select(-outcome) |> 
  mutate(score = if_else(polyscore > 4, 1, 0))

rm(oconnor2023)
