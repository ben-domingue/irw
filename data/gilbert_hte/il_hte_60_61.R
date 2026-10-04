# IL-HTE Econ, 60/61: Lyall (2019) APSR - Government Support/Violence attitudes
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# There are multiple randomizations in this study, here, we're just taking the initial randomization to a vocational training program.

lyall2019 <- read_csv(glue("{raw}/60 INVEST_Panel_anon.csv")) |> 
  select(s_id = reg_no, treat = TVETassign, block_id = block, 
         tot = TVETgraduate,
         cov_age = age,
         cov_female = female,
         contains("rr"), contains("vio"),
         contains("endline"),
         time = endline) |> 
  arrange(s_id, time) |> 
  # based on rep kit and article, RR6 isn't used. Unclear why, so exlcuding
  select(-c(RR6, married.base, currentANSFfrnds:locgovcorruption)) |> 
  # turn treat into a dummy
  mutate(treat = if_else(treat == "TREAT", 1, 0),
         # RR7-10 are pro-taliban, reverse
         across(RR7:RR10, ~ 1 - .),
         # the use violence items are 0-3, dichotomize to make comparable with others
         # across(viousepolice:viouseleader, ~ if_else(. > 1, 1, 0)),
         block_id = parse_number(block_id)
         ) |> 
  # as in zhou, there are some duplicated IDs
  distinct(s_id, time, .keep_all = TRUE) |> 
  # pivot to long
  pivot_longer(c(contains("RR"), contains("vio")), 
               names_to = "item", values_to = "polyscore") |> 
  arrange(s_id, item, time) |> 
  mutate(outcome = if_else(str_detect(item, "RR"), "govt. support", "violence")) |> 
  drop_na(polyscore)

lyall2019_a <- lyall2019 |> 
  filter(outcome == "govt. support") |> 
  rename(score = polyscore)

lyall2019_b <- lyall2019 |> 
  filter(outcome == "violence") |> 
  # heavy right skew, dichotomize at 0
  mutate(score = if_else(polyscore > 0, 1, 0))

rm(lyall2019)
