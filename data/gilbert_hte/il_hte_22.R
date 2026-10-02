# IL-HTE Econ, 22: Berry (2018) World Development - Financial Literacy
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

berry2018 <- read_dta(glue("{raw}/22 analysis.dta")) |> 
  select(s_id = unique, cluster_id = schid, treat = samp,
         cov_male = gender,
         cov_age = age,
         # baseline
         prfspnd:prfsavprntonly,
         # endline
         end_prfsavprntbuy:end_prfsavevrytime) |> 
  mutate(
    # any treatment vs control
    treat = if_else(treat == 0, 0, 1),
    # reverse code
    across(c(prfspnd, prftmpt, prfsavedfclt:prfsavprntonly,
             end_prfsavprntbuy:end_prfsavlvhm, end_prfsavadultonly, end_prfsavprntonly,
             end_prfsavspndbetter), ~ 3 - .)) |> 
      # pivot to long
  select(contains("_id"), treat, contains("cov_"),
         prfspnd:end_prfsavevrytime) |> 
  pivot_longer(prfspnd:end_prfsavevrytime, 
               names_to = "item", values_to = "polyscore") |> 
  mutate(time = if_else(str_detect(item, "end_"), 1, 0),
         score = if_else(polyscore > 1, 1, 0),
         item = str_remove(item, "end_")) |> 
  drop_na(polyscore) |> 
  arrange(s_id, item, time)
