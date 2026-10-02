# IL-HTE Econ, 7/8: Kim (2024) Dev. Psy. - Vocabulary/Reading Comprehension
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

kim2024 <- glue("{raw}/07 08 morelongitudinal_2021_wide_public.dta") |> 
  read_dta() |> 
  select(s_id, treat = s_itt_consented, 
         tot = s_more_full_spiral,
         cluster_id = sch_id,
         std_baseline = s_mapritread_std1819w,
         s_black_num:s_ses_high,
         contains("s_vocab"), contains("s_cc"), 
         contains("stratum")) |> 
  # drop AIG, constant
  select(-s_aig_num) |> 
  # create single block variable
  mutate(block_id = case_when(
    stratum2 == 1 ~ 2,
    stratum3 == 1 ~ 3,
    stratum4 == 1 ~ 4,
    stratum5 == 1 ~ 5,
    stratum6 == 1 ~ 6,
    stratum7 == 1 ~ 7,
    .default = 1
  ))

# break into item and person
# separate datasets, then recombine
kim2024_a_i <- kim2024 |> 
  select(s_id, contains("s_vocab")) |> 
  pivot_longer(contains("s_vocab"),
               names_to = "item",
               values_to = "score") |> 
  drop_na(s_id, score) |> 
  mutate(time = 1)

kim2024_b_i <- kim2024 |> 
  select(s_id, contains("s_cc")) |> 
  pivot_longer(contains("s_cc"),
               names_to = "item",
               values_to = "score") |> 
  drop_na(s_id, score) |> 
  mutate(time = 1)

kim2024_p <- kim2024 |> 
  select(contains("_id"), treat, tot, std_baseline,
         s_black_num:s_ses_high) |> 
  # restandardize to present sample
  mutate(std_baseline = scale(std_baseline)[,]) |> 
  # add the prefix cov_ to all 
  rename_with(~paste0("cov",
                      sub("s_*", "_", .)), 
                   starts_with("s_")) |> 
  rename(s_id = cov_id)

# combine
kim2024_a <- kim2024_a_i |> 
  left_join(kim2024_p, by = "s_id")

kim2024_b <- kim2024_b_i |> 
  left_join(kim2024_p, by = "s_id")

rm(kim2024_a_i, kim2024_b_i, kim2024_p, kim2024)
