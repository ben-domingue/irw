# IL-HTE Econ, 64: Zhao (2023) TIES - Social-Emotional Learning
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Using the ASQ average as the baseline measure

zhao2023 <- read_dta(glue("{raw}/64 AS_data_imputed.dta")) |> 
  # all this extra stuff
  select(-starts_with("_")) |> 
  # generate a student id
  mutate(s_id = row_number()) |> 
  select(s_id, treat = tx, cluster_id = schoolid_att,
         # ASQ subtests
         base_COMM, base_GMOT, base_FMOT, base_PSLV, base_PSOC,
         cov_household_size = hh_num,
         cov_tch_exp = t_dm_yrs_teach,
         cov_female = childgender,
         cov_health = childhealth,
         contains("end_emotion_")) |> 
  # create the baseline score
  rowwise() |> 
  mutate(baseline = mean(c_across(contains("base_")), na.rm = TRUE)) |> 
  ungroup() |> 
  mutate(std_baseline = scale(baseline)[,]) |> 
  select(-baseline, -contains("base_")) |> 
  pivot_longer(contains("end_emotion"), names_to = "item", values_to = "polyscore") |> 
  # dichotomize
  mutate(score = if_else(polyscore > 1, 1, 0),
         time = 1) |> 
  drop_na(score)
