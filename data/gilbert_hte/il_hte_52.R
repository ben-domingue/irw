# IL-HTE Econ, 52: Abaluck (2022) Science - COVID Symptoms
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

abaluck_pre <- read_dta(glue("{raw}/52 baseHH_data.dta")) |> 
  select(s_id = caseid,
         cov_household_size = member_count,
         sm_a_1:sm_a_11) 

abaluck_pre_p <- abaluck_pre |> 
  select(s_id, contains("cov_"))

abaluck_pre_i <- abaluck_pre |> 
  select(s_id, starts_with("sm_")) |> 
  pivot_longer(contains("sm"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = 0)

abaluck2022_p <- read_dta(glue("{raw}/52 followupSurvey_data.dta")) |> 
  select(s_id = caseid, treat = treatment, block_id = pairID, cluster_id = union,
         sm_a_1:sm_a_11) |> 
  # weird issue - there are duplicate IDs in the post file, not the pre file
  # taking the highest value for each id
  # logic is that the question is asking if someone in the household has the symptom
  # we'll be most conservative
  lazy_dt() |> 
  group_by(s_id) |> 
  mutate(across(contains("sm_"), ~ max(.))) |> 
  distinct(s_id, .keep_all = TRUE) |> 
  as_tibble()
  
abaluck2022 <- abaluck2022_p |> 
  select(s_id, contains("sm_")) |> 
  pivot_longer(contains("sm"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = 1) |> 
  bind_rows(abaluck_pre_i) |> 
  arrange(s_id, item, time) |> 
  left_join(abaluck2022_p, by = "s_id") |> 
  select(-contains("sm_")) |> 
  drop_na(treat) |> 
  left_join(abaluck_pre_p, by = "s_id")

rm(abaluck_pre, abaluck_pre_i, abaluck_pre_p, abaluck2022_p, abaluck_score)
