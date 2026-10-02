# IL-HTE Econ, 16: de Barros (2023) EJ - Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Note: Pre and post items appear different but measure the same construct (math).

# randomization data
debarros_randomization <- read_dta(glue("{raw}/16 Randomization.dta")) |> 
  select(cluster_id = school_ID, block_id = strata, treat = T)

# baseline data
debarros_baseline <- read_dta(glue("{raw}/16 written_data baseline.dta")) |> 
  select(s_id = STS_ID, cluster_id = school_ID, 
         cov_gender = Gender,
         cov_age = Student_age,
         q1:q1127_oral) |> 
  left_join(debarros_randomization, by = "cluster_id") |> 
  mutate(cov_male = if_else(cov_gender == 1, 1, 0)) |> 
  select(-cov_gender)

debarros2023_p <- debarros_baseline |>
  select(contains("_id"), contains("cov_"), treat)

debarros_i_pre <- debarros_baseline |> 
  select(s_id, starts_with("q")) |> 
  pivot_longer(starts_with("q"), names_to = "item", values_to = "score") |> 
  mutate(time = 0)

# put together
debarros_i_post <- read_dta(glue("{raw}/16 written_data endline.dta")) |> 
  select(s_id = STS_ID, q3002:q4018) |> 
  pivot_longer(contains("q"),
               names_to = "item",
               values_to = "score") |> 
  mutate(time = 1)

debarros2023_i <- debarros_i_pre |> 
  bind_rows(debarros_i_post) |> 
  arrange(s_id, item, time) |> 
  drop_na(score)

debarros2023 <- debarros2023_i |> 
  left_join(debarros2023_p, by = "s_id") |> 
  arrange(s_id, item, time)

rm(debarros2023_i, debarros2023_p, debarros_i_post, debarros_i_pre,
   debarros_randomization, debarros_baseline, debarros_irt)
