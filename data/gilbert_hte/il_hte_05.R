# IL-HTE Econ, 5: Woods (2021) PLoS One - Health Literacy
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

woods2021 <- glue("{raw}/05 lifelabtrial.dta") |> 
  read_dta() |> 
  # clean the responses
  # 0 is baseline, 12 is followup
  # based on the stata code, it looks like the fdpregh have already been reversed
  # even though the label says "not"
  select(s_id = serial, cluster_id = School, 
         treat = intervention,
         contains("g2"), 
         -c(lifesty0g2, fdqual0g2, vigexerx0g2, liteexerx0g2,
            lifesty12g2, fdqual12g2, vigexerx12g2, liteexerx12g2),
         gender, cov_age = age) |> 
  # 1 is male
  mutate(cov_male = if_else(gender == 1, 1, 0)) |> 
  select(-gender) |> 
  # pivot to long
  pivot_longer(contains("g2"),
               names_to = "item",
               values_to = "score") |> 
  # get the time and make the item names consistent
  mutate(time = if_else(str_detect(item, "12g"), 1, 0),
         item = str_remove(item, "12g2|0g2")) |> 
  drop_na(score) |> 
  arrange(s_id, item, time)
