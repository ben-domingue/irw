# IL-HTE Econ, 6: Bruhn (2016) AEJ- Financial Literacy
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# We use the authors' dummy coded items.

bruhn2016 <- glue("{raw}/06 school_intervention_panel_final.dta") |> 
  read_dta() |> 
  select(s_id = id_geral, 
         cluster_id = cd_escola,
         block_id = pair_all,
         treat = treatment, 
         round,
         # covariates
         # these are all dummies
         cov_female = female_coded,
         cov_mom_ed = dumm_rp_08_bl,
         cov_dad_ed = dumm_rp_09_bl,
         cov_welfare = dumm_rp_14_bl,
         cov_home_computer = dumm_rp_23_bl,
         cov_retained = dumm_rp_24_bl,
         cov_unemployed = dumm_rp_49_bl,
         # dummy coded items
         # bl = baseline
         # fup = followup
         dumm_rp_50_bl, dumm_rp_53B_bl, dumm_rp_59_bl, dumm_rp_64A_bl,
         dumm_rp_61_bl, dumm_rp_65A_bl, dumm_rp_93_bl, dumm_rp_94_bl,
         dumm_rp_95_bl, dumm_rp_96_bl,
         dumm_rp_50_fup, dumm_rp_53B_fup, dumm_rp_59_fup, dumm_rp_64A_fup,
         dumm_rp_61_fup, dumm_rp_65A_fup, dumm_rp_93_fup, dumm_rp_94_fup,
         dumm_rp_95_fup, dumm_rp_96_fup) |> 
  # the data structure is strange here
  # bl and fup are in 1 row, but the 2nd followup is in a second row
  # here, I make it full wide, so fup0 is initial, fup1 is delayed
  pivot_wider(names_from = round, values_from = contains("fup")) |>
  # pivot to long
  select(contains("_id"), treat,
         contains("cov_"), contains("dumm_rp")) |> 
  pivot_longer(contains("dumm_rp"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  # get the time based on the item suffix
  mutate(time = case_when(
    str_detect(item, "_bl") ~ 0,
    str_detect(item, "_fup_0") ~ 1,
    str_detect(item, "_fup_1") ~ 2
  )) |> 
  # give items same names across time
  mutate(item = str_remove_all(item, "_bl|_fup_0|_fup_1")) |> 
  arrange(s_id, item, time) |> 
  drop_na(score) |> 
  # appear to be a handful of duplicate item responses, drop
  distinct(s_id, item, time, .keep_all = TRUE)
