# IL-HTE Econ, 49: Daniel (2017) Trials - Psychological Distress
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Only the SRQ-20 items (adults) have baseline measurements; the MDAT which is the primary outcome for children does not.

daniel2017 <- read_csv(glue("{raw}/49 KUSAMALA_DATA.csv")) |> 
  # there is no child ID, make one
  mutate(s_id = row_number()) |> 
  select(s_id, cluster_id = group_number, treat = arm, 
         cov_age = baseline_caregiver_age,
         cov_any_school = baseline_caregiver_school,
         cov_literate = baseline_able_to_write_name,
         cov_income = baseline_12_mon_typical_income,
         contains("SRQ")) |> 
  drop_na(cluster_id) |> 
  mutate(cov_literate = cov_literate - 1) |> 
  # select(s_id, contains("SRQ")) |> 
  pivot_longer(contains("SRQ"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = case_when(
    str_starts(item, "baseline") ~ 0,
    str_starts(item, "discharge") ~ 1,
    str_starts(item, "followup") ~ 2
  ),
   item = str_remove_all(item, "baseline_|discharge_|followup_|srq20_"),
  item = substr(item, 1, 12)
  ) |> 
  arrange(s_id, item, time)
