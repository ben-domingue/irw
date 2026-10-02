# IL-HTE Econ, 75: Baron (2021) OSF - Political Engagement
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Note: There are *many* outcomes here, just looking at dichotomous political engagement, as some of the others are complex constructions of other items.

baron2021 <- read_dta(glue("{raw}/75 Full_BArct_Data_panel.dta")) |> 
  select(s_id = sid, time = wave, treat = treatment, block_id = block,
         cov_female = woman, cov_party = inparty,
         cov_white = white, cov_asian = asian, cov_citizen = citizen,
         # items
         plan_vote:sign_petition) |> 
  pivot_longer(plan_vote:sign_petition, 
               names_to = "item",
               values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = (time - 1)/2 )

# # Export The Cleaned Data
