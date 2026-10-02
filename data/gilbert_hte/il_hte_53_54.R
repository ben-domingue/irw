# IL-HTE Econ, 53/54: Saha (2023) Reproductive Health - Women's Empowerment/Consent
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

saha2023 <- read_csv(glue("{raw}/53 GOC_Combined Data.csv")) |> 
  select(s_id = resp_s, time = tos, treat,
         cov_pursue_career = q157,
         cov_mobile_phone = q201,
         cov_attend_school = q136,
         cov_in_school = q138,
         contains("515"), contains("602")) |> 
  select(-c(q602g, q602go)) |> 
  arrange(s_id) |>
  # covariates
  mutate(
    across(cov_pursue_career:cov_mobile_phone, ~ 
                  if_else(. == "Yes", 1, 0)),
    across(cov_attend_school:cov_in_school, ~ if_else(. == 1, 1, 0))
         ) |> 
  # 515 - recode to 1 = agree, 0 = disagree/can't say
  mutate(across(contains("q515"), ~ if_else(. == "Agree", 1, 0)),
         # 602 - code to numeric
         across(contains("q602"), ~ case_when(
           . == "Not at all confident" ~ 0,
           . == "Somewhat not confident" ~ 1,
           . == "Somewhat confident" ~ 2,
           . == "Extremely confident" ~ 3
         )),
         # reverse code 515 items as needed
         # 602 are all positive
         across(c(q515a, q515b, q515h, q515m, q515j, q515k, q515l), ~ 1 - .),
         # make treat numeric
         treat = if_else(treat == "Treatment group", 1, 0),
         time = if_else(time == "Baseline", 0, 1)
         ) |> 
  # some covariates only present in baseline - fill in
  group_by(s_id) |> 
  mutate(
    across(contains("cov_"), ~ max(., na.rm = TRUE))
    ) |> 
  ungroup() |> 
  # pivot to long
  pivot_longer(starts_with("q"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  arrange(s_id, item, time) |> 
  mutate(outcome = if_else(str_detect(item, "515"), "515", "602"),
         # covariates got messed up if BOTH missing
         across(contains("cov_"), ~ if_else(. == -Inf, NA_real_, .)))

saha2023_a <- saha2023 |> 
  filter(outcome == "515")

saha2023_b <- saha2023 |> 
  filter(outcome == "602") |> 
  rename(polyscore = score) |> 
  # super left skewed; use 2 as cutoff
  mutate(score = if_else(polyscore > 2, 1, 0))

rm(saha2023)
