# IL-HTE Econ, 20: Jiyanthi (2021) Exceptional Children - Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# read in the raw data
jiyanthi2021 <- read_xlsx(glue("{raw}/20 NSF Core_Final Analytic_Harvard Dataverse_12-02-2019.xlsx")) |> 
  clean_names() |>
  select(s_id = student_id, treat = tx,
         cov_male = sex,
         cov_black = black,
         cov_asian = asian,
         cov_white = white,
         cov_hispanic = hispanic,
         cov_multi = multirace,
         cov_frl = frl,
         cov_iep = iep_504,
         contains("tuf4pre_q"), contains("tuf4post_q"),
         contains("tuf5post_q"),
         contains("procedures_pre_q"), contains("procedures_post_q"),
         contains("trans_math_post_q")) |> 
  # drop procedures_pre_q2c because all students got wrong
  select(-procedures_pre_q2c) |> 
  # pivot to long
  select(s_id, treat, contains("cov_"), contains("pre"), contains("post")) |> 
  pivot_longer(c(contains("pre"), contains("post")), names_to = "item", values_to = "score") |>
  # get time from item text and make item names the same
  mutate(time = if_else(str_detect(item, "pre"), 0, 1),
         item = str_remove_all(item, "pre|post")) |> 
  arrange(s_id, item, time)
