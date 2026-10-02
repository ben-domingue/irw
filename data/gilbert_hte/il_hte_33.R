# IL-HTE Econ, 33: Aladysheva (2017) i3e - Social Trust
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

alady2017 <- read_dta(glue("{raw}/33 ie_lsbs_data.dta")) |> 
  select(s_id = ids_fin, wave, treat = T4,
         cov_male = male,
         cov_age = age,
         cov_kyrgyz = krg,
         cov_uzbek = uzb,
         cov_other_eth = oth,
         cov_ethnic_minority = ethn_min,
         # trust related questions seem most relevant here
         o3b1_tr1:i_blf_oprt
         ) |> 
  # make 0 the baseline time
  mutate(time = wave - 1) |> 
  select(-wave) |> 
  # pivot to long
  pivot_longer(o3b1_tr1:i_blf_oprt, names_to = "item",
               values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  # recode ordinal variables
  # 1-4 scale, split midpoint
  # 1-5 scale, 3 = neutral, split at > 3
  mutate(
    score = case_when(
      str_starts(item, "o") & polyscore > 2 ~ 1,
      str_starts(item, "i") & polyscore > 3 ~ 1,
      .default = 0
    )
  ) |> 
  # reverse code (based on dichotomous)
  mutate(
    r = if_else(item %in% c("i_blf_lng", "i_blf_clt",
                  "o3b1_blf6", "i_blf_qiet",
                  "i_blf_trst", "i_blf_compl"), 1, 0),
    score = if_else(r == 1, 1 - score, score),
    polyscore = if_else(r == 1, 6 - polyscore, polyscore)
    )
