# IL-HTE Econ, 63: Hoffmann (2018) i3e - Indebtedness
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

hoffmann2018 <- read_dta(glue("{raw}/63 Public_household.dta")) |> 
  select(s_id = srl, cluster_id = panch_code, contains("_dummy"),
         treat = status,
         cov_female_head = BL_head_gender,
         cov_household_size = BL_num_mem,
         cov_owns_land = BL_land,
         # items
         BL_any_loan, BL_entitle, BL_any_debt, BL_any_informal_loan,
         EL_any_loan, EL_entitle, EL_any_debt, EL_any_informal_loan
         ) |> 
  # strata are dummy variables, convert to single block_id
  mutate(across(contains("_dummy"), ~ if_else(. == 0, NA, .))) |> 
  pivot_longer(contains("_dummy"), names_to = "block_id", values_to = "i") |> 
  drop_na(i) |> 
  select(-i) |> 
  mutate(block_id = parse_number(block_id)) |> 
  # put in long format
  pivot_longer(BL_any_loan:EL_any_informal_loan,
               names_to = "item", values_to = "score") |> 
  mutate(time = if_else(str_detect(item, "BL_"), 0, 1),
         item = str_remove_all(item, "BL_|EL_")) |> 
  arrange(s_id, item, time) |> 
  drop_na(score)
