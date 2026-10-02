# IL-HTE Econ, 27/28: Banerji (2017) AEJ - Language/Math (Mother Sample)
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# intervention for mothers, looking at mother outcomes
# b = baseline, e = endline
banerji_wide <- read_dta(glue("{raw}/27 ml_merged.dta")) |> 
  # we only want mothers
  filter(lineno == mother_lineno) |> 
  # the cluster variable appears to be a randomization block
  select(treat = treatment, block_id = cluster, s_id = hh_id,
         cov_age = age,
         contains("b_maser"), contains("e_maser"),
         rcode) |> 
  drop_na(b_maser_mother_lineno) |> 
  mutate(
    # dichotomize treatment
    treat = if_else(treat == 1, 0, 1),
    # score the reading test
    across(c(b_maser_pic1:b_maser_pic10, e_maser_pic1:e_maser_pic10,
             b_maser_lang_para:b_maser_lang_chname), ~ if_else(. == 1, 1, 0)),
    across(c(b_maser_lang_lttrs, e_maser_lang_lttrs), ~ if_else(. == 11, 1, 0)),
    across(c(b_maser_lang_word1:b_maser_lang_word2, e_maser_lang_word1:e_maser_lang_word2),
           ~ if_else(. == 6, 1, 0)),
    # additional endline qs
    across(e_maser_lang_para:e_maser_lang_vilname, ~ if_else(. == 1, 1, 0)),
    # score the math test
    across(c(b_maser_math_read1, e_maser_math_read1), ~ if_else(. == 9, 1, 0)),
    across(c(b_maser_math_ident1, e_maser_math_ident1,
             b_maser_math_ident2, e_maser_math_ident2,
             b_maser_math_ident3, e_maser_math_ident3), ~ if_else(. == 6, 1, 0)),
    across(c(b_maser_math_read2, e_maser_math_read2), ~ if_else(. == 11, 1, 0)),
    across(c(b_maser_math_add1:b_maser_mobile_dial2,
             e_maser_math_add1:e_maser_mobile_dial1), ~ if_else(. == 1, 1, 0))
  ) |> 
  # drop extraneous vars
  select(treat, block_id, s_id, cov_age, rcode, b_maser_pic1:b_maser_mobile_dial2,
         e_maser_pic1:e_maser_mobile_dial1)

# pivot to long, separate
banerji2017_a <- banerji_wide |> 
  pivot_longer(c(b_maser_pic1:b_maser_lang_chname, e_maser_pic1:e_maser_lang_vilname), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "b_"), 0, 1),
         item = str_remove_all(item, "b_|e_")) |> 
  arrange(s_id, item, time) |> 
  select(-contains("maser"))

banerji2017_b <- banerji_wide |> 
  pivot_longer(c(b_maser_math_ident1:b_maser_mobile_dial2, 
                 e_maser_math_read1:e_maser_mobile_dial1), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "b_"), 0, 1),
         item = str_remove_all(item, "b_|e_")) |> 
  arrange(s_id, item, time) |> 
  select(-contains("maser"))

rm(banerji2017_p, banerji_math, banerji_lit, banerji_wide)
