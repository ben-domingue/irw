# IL-HTE Econ, 1: Gilbert (2023) JEBS - Reading Comprehension
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# read in the raw data
gilbert2023 <- glue("{raw}/01 more_2122_anon.csv") |> 
  read_csv() |> 
  # rename variables
  rename(treat = s_itt_2122,
         score = s_correct,
         item = item_id,
         cluster_id = sch_id) |> 
  arrange(s_id, item) |> 
  mutate(time = 1)

# get standardized baseline; standardize at person level
gilbert2023_p <- gilbert2023 |> 
  select(s_id, treat, cluster_id, s_mapritread2122f) |> 
  distinct() |> 
  arrange(s_id) |> 
  mutate(std_baseline = scale(s_mapritread2122f)[,]) |> 
  select(-s_mapritread2122f)

# item level
gilbert2023_i <- gilbert2023 |> 
  select(s_id, time, item, score)

# merge back together
gilbert2023 <- gilbert2023_i |> 
  left_join(gilbert2023_p, by = "s_id")

rm(gilbert2023_i, gilbert2023_p)
