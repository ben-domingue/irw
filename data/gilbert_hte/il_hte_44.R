# IL-HTE Econ, 44: Lee (2022) IJGP - Mental Health
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Only assessing the primary, mental health outcome. However, because the number of items on the SWEMWBS is low (7) and the sample is small, which led to convergence issues, adding in the Geriatric Depression Scale (reverse coded) as well as an overall index of mental health.

lee2021 <- read_sav(glue("{raw}/44 Lee 2022.sav")) |> 
  select(s_id = Study_no, treat = Randomized_group,
         tot = mITT,
         cov_age = Age,
         cov_sex = Sex,
         cov_educ = Education,
         contains("SWEMWBS_0"), contains("SWEMWBS_1"),
         contains("SWEMWBS_2"),
         contains("GDS_0"), contains("GDS_1"),
         contains("GDS_2")) |> 
  # group 2 is control
  mutate(treat = if_else(treat == 1, 1, 0),
         tot = if_else(tot == 1, 1, 0),
         # missings on TOT should be 0s
         tot = replace_na(tot, 0),
         cov_sex = cov_sex - 1,
         # reverse code depression items to reflect mental health
         # based on a 2PL model, it looks like the 0/1 have already been
         # coded to reflect depression, so reverse all of them
         across(contains("GDS"), ~ 1 - .)
         ) |> 
  # pivot to long
  pivot_longer(matches("SWEMWBS|GDS"), names_to = "item", values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  mutate(time = word(item, 2, sep = "_"),
         test = word(item, 1, sep = "_"),
         q = word(item, 3, sep = "_"),
         item = glue("{test}_{q}"),
         score = case_when(
    str_detect(item, "GDS") ~ polyscore,
    str_detect(item, "SWEM") & polyscore > 3 ~ 1,
    .default = 0
  )) |> 
  arrange(s_id, item, time) |> 
  select(-test, -q)
