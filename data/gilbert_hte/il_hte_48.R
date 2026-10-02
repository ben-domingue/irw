# IL-HTE Econ, 48: Cardenas (2023) JRCE - Child Development
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Recoding the polytomous from no/sometimes/yes to yes = 1, other = 0.

# The ASQ items vary by age - leaving them as constant for now or else we get \> 500 items. Maybe return to this.

cardenas2023 <- read_dta(glue("{raw}/48 completa.dta")) |> 
  select(s_id = ID_HOG_IND, cluster_id = ID_LOC, ChildID, time = wave,
         cov_female = sexo1,
         item_age = cuest,
         treat = tipo_grupo, 
         COM_01_ASQ:SOCI_06_ASQ) |> 
  drop_na(ChildID) |> 
  select(-ChildID) |> 
  # recode treatment
  mutate(treat = if_else(treat == 1, 1, 0),
         # a random 9 in one item
         MOTF_01_ASQ = if_else(MOTF_01_ASQ == 9, NA_real_, MOTF_01_ASQ),
         time = time - 1,
         cov_female = if_else(cov_female == 2, 1, 0)
         ) |> 
  # pivot to long
  pivot_longer(contains("ASQ"), 
               names_to = "item", values_to = "polyscore") |> 
  mutate(score = if_else(polyscore == 3, 1, 0)) |> 
  drop_na(polyscore) |> 
  arrange(s_id, item, time)
