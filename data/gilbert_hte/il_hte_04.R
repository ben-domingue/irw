# IL-HTE Econ, 4: Blattman et al. (2017) AER - Crime and Violence
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# We consider any treatment vs. no treatment. The Likert scale items are dichotomized so 0 = no report of the relevant behavior, 1 = any report.

blattman2017 <- glue("{raw}/04 STYL_Final.dta") |> 
  read_dta() |> 
  # limit to relevant variables
  select(s_id = partid, 
         block_id = tp_strata,
         round, 
         # dichotomous 1 = any treatment
         treat = treatment,
         # assignment and compliance vars
         treat_tp = tpassigned,
         treat_cash = cashassigned,
         treat_both = tpcashass,
         tot_tp = tptreatonly,
         tot_cash = cashtreatonly,
         tot_both = tpcashtreat,
         # covariates
         cov_age = ageexact_b,
         cov_educ = educ_b,
         cov_health = health_resc_b,
         # these are the relevant questions
         # _b means baseline
         # _e means endline
         matches("bad.*resc_b"), matches("bad.*resc_e"),
         # get rid of extraneous variables
         -contains("lc_"), -contains("thi"))  |>
  # overall compliance var
  # this is a dummy for receiving any treatment
  rowwise() |> 
  mutate(tot = max(tot_tp, tot_cash, tot_both)) |> 
  ungroup() |> 
  # pivot to long
  pivot_longer(contains("bad"), names_to = "item", values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  # identify timing from item suffix
  mutate(time = if_else(str_detect(item, "_b"), 0, round),
         # dichotomize so 1 = any report
         score = if_else(polyscore > 0, 1, 0)
  ) |> 
  select(-round) |> 
  # ensure no duplicates
  distinct() |> 
  arrange(s_id, item, time) |> 
  # keep baseline, endline, and followup
  # midline has very few observations
  filter(! time %in% c(2,4)) |> 
  mutate(
    # time is now 0, 1, 2
    time = if_else(time == 5, 2, time),
    # remove suffix from item now that we have the time variable
    item = str_remove(item, "_b|_e"),
    ) |> 
  select(-c(treat_tp:tot_both))
