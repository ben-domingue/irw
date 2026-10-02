# IL-HTE Econ, 74: Gilbert (2024) AME - Vocabulary
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

gilbert2024_b <- read_csv(glue("{raw}/74 more_vocab_anon.csv")) |> 
  rename(cluster_id = sch_id, treat = s_itt_consented,
         std_baseline = s_maprit_1819w_std, score = correct,
         item = item_num) |>
  # here, time 0 is post test
  mutate(time = time + 1)
