# IL-HTE Econ, 29/30: Banerji (2017) AEJ - Language/Math (Child Sample)
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# b = baseline, e = endline
banerji_wide <- read_dta(glue("{raw}/27 ml_merged.dta")) |> 
  # dropping those without assessments
  drop_na(b_caser, e_caser) |> 
  # the cluster variable appears to be a randomization block
  # child data set so children are clustered within house holds
  select(treat = treatment, block_id = cluster, cluster_id = hh_id,
         lineno,
         cov_sex = sex,
         cov_age = age,
         # c is for child outcome
         contains("b_caser"), contains("e_caser"),
         rcode) |> 
  mutate(
    cov_male = if_else(cov_sex == 1, 1, 0),
    # unique id
    s_id = glue("{cluster_id}-{lineno}"),
    # dichotomize treatment
    treat = if_else(treat == 1, 0, 1),
    # score the reading test, as the mother example
    across(c(b_caser_pic1:b_caser_pic10, e_caser_pic1:e_caser_pic10,
             b_caser_lang_para), ~ if_else(. == 1, 1, 0)),
    across(c(b_caser_lang_lttrs, e_caser_lang_lttrs), ~ if_else(. == 11, 1, 0)),
    across(c(b_caser_lang_word1:b_caser_lang_word2, e_caser_lang_word1:e_caser_lang_word2),
           ~ if_else(. == 6, 1, 0)),
    # additional endline qs
    across(e_caser_lang_para:e_caser_lang_stry, ~ if_else(. == 1, 1, 0)),
    # score the math test
    across(c(b_caser_math_read1, e_caser_math_read1), ~ if_else(. == 9, 1, 0)),
    across(c(b_caser_math_ident1, e_caser_math_ident1,
             b_caser_math_ident2, e_caser_math_ident2,
             b_caser_math_ident3, e_caser_math_ident3), ~ if_else(. == 6, 1, 0)),
    across(c(b_caser_math_read2, e_caser_math_read2), ~ if_else(. == 11, 1, 0)),
    across(c(b_caser_math_add1:b_caser_math_subtr2,
             e_caser_math_add1:e_caser_math_subtr3), ~ if_else(. == 1, 1, 0))
  ) |> 
  # drop extraneous vars
  select(treat, block_id, cluster_id, s_id, cov_age, cov_male, 
         b_caser_pic1:b_caser_math_subtr2,
         e_caser_pic1:e_caser_math_subtr3) |> 
  select(-b_caser_math)

# pivot to long, separate
banerji2017_c <- banerji_wide |> 
  pivot_longer(c(b_caser_pic1:b_caser_lang_para,
                 e_caser_pic1:e_caser_lang_stry), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "b_"), 0, 1),
         item = str_remove_all(item, "b_|e_")) |> 
  arrange(s_id, item, time) |> 
  select(-contains("caser"))

banerji2017_d <- banerji_wide |> 
  pivot_longer(c(b_caser_math_read1:b_caser_math_subtr2, 
               e_caser_math_read1:e_caser_math_subtr3), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_detect(item, "b_"), 0, 1),
         item = str_remove_all(item, "b_|e_")) |> 
  arrange(s_id, item, time) |> 
  select(-contains("caser"))

rm(banerji2017_p_child, banerji_lit, banerji_wide, banerji_math)
