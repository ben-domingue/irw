# IL-HTE Econ, 55: Wang (2023) JPEM - Academic Achievement
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Using the `any_treat` variable to indicate any treatment.

wang2023 <- read_dta(glue("{raw}/55 IVR_Data.dta")) |> 
  select(s_id = CHILD_ID, cluster_id = VILLAGE_ID, 
         treat = any_treat,
         cov_age = child_age,
         cov_male = child_gen,
         cov_father_ed = father_edu_years,
         cov_mother_ed = mother_edu_years,
         cov_income = family_income,
         e1_item1:e1_item15, baseline_literacy_score, baseline_numeracy_score) |> 
  # average and standardize the baseline score
  mutate(baseline = (baseline_literacy_score + baseline_numeracy_score)/2,
         std_baseline = scale(baseline)[,],
         time = 1) |> 
  pivot_longer(contains("e1"), names_to = "item", values_to = "score") |> 
  select(-c(baseline_literacy_score:baseline))
