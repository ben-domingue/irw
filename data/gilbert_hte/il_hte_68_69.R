# IL-HTE Econ, 68/69: Banerjee (2017) JEP - Hindi & Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

banerjee2017 <- read_dta(glue("{raw}/68 haryana_analysis.dta")) |> 
  select(s_id = childid, cluster_id = school_id, block_id = stratum,
         control, cov_female = female, cov_age = age_year, cov_grade = base_standard,
         starts_with("h_q"), starts_with("m_q"),
         starts_with("base_h_q"), starts_with("base_m_q")) |> 
  mutate(treat = 1- control) |> 
  select(-control, -contains("sample")) |> 
  # pivot to long
  pivot_longer(h_q1_1:base_m_q14_c, names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  # identify timepoints and subtests
  mutate(time = if_else(str_starts(item, "base_"), 0, 1),
         test = if_else(str_detect(item, "h_"), "Hindi", "Math"),
         item = str_remove_all(item, "h_|m_|base_m_|base_h_")
         ) |> 
  arrange(s_id, test, item, time) |> 
  # get rid of anything not scored 0 or 1, these are refusals or missings
  filter(score %in% c(0,1))

banerjee2017_a <- banerjee2017 |> 
  filter(test == "Hindi")

banerjee2017_b <- banerjee2017 |> 
  filter(test == "Math")

rm(banerjee2017)
