# IL-HTE Econ, 56: Sebele (2023) - Literacy
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

sebele2023 <- read_dta(glue("{raw}/56 rf_clean_student_data_endline.dta")) |> 
  select(s_id = student_id, cluster_id = school_id, block_id = county,
         treat = treatment_el, 
         tot = treatment_intensity,
         cov_age = age_bl,
         cov_female = gender_bl, # 0 = Male, 1 = Female in source (#2794)
         letter_pass_el, beg_sound_pass_el,
         cvc_pass_el, word_pass_el,
         # no baseline for math so excluding those endline items
         # sentence_pass_el, story_comp_pass_el, word_pass_bl
         # all correct; exclude
         letter_pass_bl, beg_sound_pass_bl, cvc_pass_bl
         ) |> 
  pivot_longer(matches("_bl|_el"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "_bl"), 0, 1)) |> 
  arrange(s_id, item, time) |> 
  mutate(item = str_remove(item, "_bl|_el"))
