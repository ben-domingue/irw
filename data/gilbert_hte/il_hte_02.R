# IL-HTE Econ, 2: Kim (2023) JEP - Reading Comprehension
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# raw data
kim2023 <- glue("{raw}/02 item_response_public.dta") |> 
  read_dta()

# separate into item and person dfs
kim2023_i <- kim2023 |> 
  select(s_id,
         item = s_q_num, 
         score = s_correct) |> 
  mutate(time = 1) |> 
  arrange(s_id, item)

kim2023_p <- kim2023 |> 
  distinct(s_id, .keep_all = TRUE) |> 
  select(s_id,
         cluster_id = sch_id,
         block_id = sch_stratum,
         treat = s_itt_consented, 
         std_baseline = s_maprit_1819w_std,
         s_white_num:s_homelang_eng) |> 
  # add the prefix cov_ to all covariates
  rename_with(~paste0("cov",
                      sub("s_*", "_", .)), 
                   starts_with("s_")) |> 
  rename(s_id = cov_id) |> 
  # restandardize the baseline
  mutate(std_baseline = scale(std_baseline)[,])

# combine
kim2023 <- kim2023_i |> 
  left_join(kim2023_p, by = "s_id")

rm(kim2023_i, kim2023_p)
