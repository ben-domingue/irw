# IL-HTE Econ, 62: Wilson-Barthes (2024) SS&M - Depression (PHQ-4)
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

wilson <- read_dta(glue("{raw}/62 GISHE_data_clean.dta")) |> 
  select(s_id = participant_id, treat = tx, time,
         cluster_id = study_group_id,
         # phq4 items - already reverse coded
         pleasure_in_doing_things:unable_to_stop_worrying,
         cov_female = gender,
         cov_age = age,
         cov_county = county,
         cov_no_edu = educ1,
         cov_primary_edu = educ2,
         cov_secondary_edu = educ3,
         cov_tertiary_edu = educ4,
         cov_income_50 = mos_income_bin,
         cov_weight = weight
         # some impossible values for height, excluding
         ) |> 
  mutate(time = (time-1)/6) |> 
  arrange(s_id, time)

# get person info just from baseline
wilson_p <- wilson |> 
  filter(time == 1) |> 
  select(s_id, treat, contains("cov_"))

wilson2024 <- wilson |> 
  select(-c(treat, contains("cov_"))) |> 
  pivot_longer(pleasure_in_doing_things:unable_to_stop_worrying,
               names_to = "item",
               values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  # looks like only assessed at baseline, midline, and followup
  arrange(s_id, item, time) |> 
  mutate(score = if_else(polyscore > 0, 1, 0)) |> 
  left_join(wilson_p, by = "s_id")

rm(wilson, wilson_p)
