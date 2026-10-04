# IL-HTE Econ, 57/58/59: Maselko (2020) - Depression (x2), Stress
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Child outcomes do not have baseline, focusing on mother outcomes

maselko2020 <- read_dta(glue("{raw}/57 Bachpan_for_sharing.dta")) |> 
  select(s_id = id, cluster_id = clusterCode,
         time = timepoint, treat = arm,
         cov_age = momAge0,
         cov_household_size = totalPeople0,
         cov_educ = wifeEducYr0,
         cov_num_children = livCh,
         phq1:phq9, scid1now:scid13now,
         pss1:pss10) |> 
  # time 5 is endpoint (3 years)
  mutate(time = time/5) |> 
  # pss items already reversed, remove originals
  select(-c(pss4, pss5, pss7, pss8)) |>
  # based on codebook:
  # for SCID, recode 9 as missing, 3 to 1, otherwise 0
  mutate(across(contains("scid"), ~ case_when(
    . %in% c(1,2) ~ 0,
    . == 3 ~ 1,
    . == 9 ~ NA_real_
  )),
  # reverse code 11 and 12
  across(scid11now:scid12now, ~ 1 - .)
  ) |> 
  # pivot to long
  pivot_longer(c(contains("phq"), contains("scid"), contains("pss")),
               names_to = "item", values_to = "polyscore") |> 
  mutate(outcome = substr(item, 1, 3)) |> 
  arrange(s_id, item, time) |> 
  drop_na(polyscore)

maselko2020_a <- maselko2020 |> 
  filter(outcome == "phq") |> 
  mutate(score = if_else(polyscore > 0, 1, 0))

maselko2020_b <- maselko2020 |> 
  filter(outcome == "sci") |> 
  rename(score = polyscore)

maselko2020_c <- maselko2020 |> 
  filter(outcome == "pss") |> 
  mutate(score = if_else(polyscore > 1, 1, 0))

rm(maselko2020)
