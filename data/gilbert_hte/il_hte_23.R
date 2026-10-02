# IL-HTE Econ, 23: Bang (2022) ECEJ - Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

bang2022 <- read_xlsx(glue("{raw}/23 Assessment_Master File_Shared.xlsx")) |> 
  clean_names() |> 
  select(s_id = student_data_id, cluster_id = teacher_id,
         block_id = block,
         treat = condition, 
         contains("wave")) |> 
  # something weird happening with item 6 on both waves, 
  # not dichotomous like others
  # based on raw response, looks like "6" is a fully correct answer
  mutate(across(contains("_6code"), ~ if_else(. == 6, 1, 0))) |> 
  # get rid of raw responses
  # and summary stuff at the end
  select(-contains("response"), -c(wave1_score:wave2_pct_only)) |> 
  select(contains("_id"), treat, 
         contains("wave")) |> 
  pivot_longer(contains("wave"), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "wave1"), 0, 1),
         item = str_remove(item, "wave1_|wave2_")) |> 
  arrange(s_id, item, time)
