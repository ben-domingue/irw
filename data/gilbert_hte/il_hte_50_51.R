# IL-HTE Econ, 50/51: Luo (2019) SSM - Parenting Beliefs/Feeding Practices
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

luo_wide <- read_dta(glue("{raw}/50 Luo et al. (2019) data.dta")) |> 
  select(treat = treatment, cluster_id = villid, 
         cov_child_age = agemonth,
         cov_firstborn = ch_firstborn,
         cov_premature = ch_premature,
         cov_height_for_age_z = haz_bl,
         contains("belief"), starts_with("ch_")) |> 
  mutate(s_id = row_number()) |> 
  # remove irrelevant items
  select(-contains("breastfed"), -c(ch_formula, ch_formula_duration, ch_suppl_food))

luo2024_a <- luo_wide |> 
  select(-starts_with("ch_")) |> 
  pivot_longer(starts_with("belief"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "_bl"), 0, 1),
         item = str_remove_all(item, "_bl")) |> 
  arrange(s_id, item, time)

luo2024_b <- luo_wide |> 
  select(-starts_with("belief")) |> 
  pivot_longer(starts_with("ch_"), names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "_bl"), 0, 1),
         item = str_remove_all(item, "_bl")) |> 
  arrange(s_id, item, time)

rm(luo_wide)
