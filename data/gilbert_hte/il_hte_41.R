# IL-HTE Econ, 41: Mohohlwane (2023) JREE - Literacy
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# w1 seems to be baseline, w2 first followup
moho2023 <- read_dta(glue("{raw}/41 EGRS2.dta")) |> 
  select(cluster_id = NatEmis, 
         treat = treatment, block_id = w1_S_strata,
         cov_male = w1_LA_learner_boy,
         cov_age = w1_LA_best_age,
         cov_homelang_zulu = w2_LA_Language_Zulu,
         # this appears to be the baseline score
         std_baseline = w1_LA_is_SD1,
         # word recognition
         w2_LA_q2_1:w2_LA_q2_18,
         # letter recognition
         w2_LA_q4_1:w2_LA_q4_80,
         # more word recognition
         w2_LA_q5_1_1:w2_LA_q5_1_18,
         # sight word
         w2_LA_q5_2_1:w2_LA_q5_2_18,
         starts_with("w3_LA_task"),
         starts_with("w4_LA_task"),
         starts_with("w4_LA_written"),
         starts_with("w5_LA_HL"),
         starts_with("w5_LA_EFAL"),
         starts_with("w5_LA_eng"),
         starts_with("w5_LA_hl_orf")
         ) |> 
  # combine treatments, create student ID
  mutate(
    s_id = row_number(),
    treat = if_else(treat == 1, 0, 1)
  ) |> 
  select(-contains("auto_stop"), -contains("time"),
         -contains("att"), -contains("60s"),
         -starts_with("w3_LA_task6")) |> 
  # pivot to long
  pivot_longer(starts_with("w"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = case_when(
    str_starts(item, "w2") ~ 1,
    str_starts(item, "w3") ~ 2,
    str_starts(item, "w4") ~ 3,
    str_starts(item, "w5") ~ 4
  ),
  item = str_remove(item, "w2_|w3_|w4_|w5_")
  ) |> 
  arrange(s_id, item, time) |> 
  # a handful of non 0 or 1 responses, no clue what these are, remove
  filter(score %in% c(0,1))
