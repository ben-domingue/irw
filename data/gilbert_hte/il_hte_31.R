# IL-HTE Econ, 31: Duflo (2015) i3e - Academic Achievement
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# At baseline and endline, this study has dichotomous scores for the ASER test. We use these and combine language and math together because there are only 3 items in each set. It's not totally clear what these are from the replication materials, but they seem to indicate some sort of passing cut score.

# because so few items, combine reading and math
duflo2015 <- read_dta(glue("{raw}/31 primaryschools_final.dta")) |> 
  select(s_id = child_id, cluster_id = school_id,
         block_id = stratum, treat = treatment, 
         cov_female = female,
         cov_age = age,
         base_aser_read_2:base_aser_read_4,
         base_aser_math_2:base_aser_math_4,
         end_aser_read_2:end_aser_read_4,
         end_aser_math_2:end_aser_math_4) |> 
  # combine treatments
  mutate(treat = if_else(treat == 1, 0, 1)) |> 
  # pivot to long
  pivot_longer(contains("aser"), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "base"), 0, 1),
         item = str_remove_all(item, "base_"),
         item = str_remove_all(item, "end_")) |> 
  arrange(s_id, item, time)
