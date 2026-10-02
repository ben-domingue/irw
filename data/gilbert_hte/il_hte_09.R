# IL-HTE Econ, 9: Hidrobo (2016) AEJ - Domestic Violence
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

hidrobo2016 <- glue("{raw}/09 DV_baseline_followup.dta") |> 
  read_dta() |> 
  select(s_id = a01, treat = bl_p_treat, 
         cluster_id = bl_a05,
         cov_female = bl_b02,
         cov_age = bl_b04,
         # get the survey questions
         contains("el_t"), contains("bl_t")) |> 
  select(-matches("el_.*b"), -matches("bl_.*b"),
         # remove irrelevant questions
         # (based on stata labels and replication files)
         -c(el_tnohaymujer:el_tb), -c(bl_tnohaymujer:bl_tb)) |> 
  mutate(cov_female = if_else(cov_female == 2, 1, 0)) |>
  # pivot to long
  pivot_longer(contains("_t"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  # get time based on item prefix
  # make item names constant across time
  mutate(time = if_else(str_detect(item, "bl_"), 0, 1),
         item = str_remove(item, "bl_|el_")) |> 
  arrange(s_id, item, time)
