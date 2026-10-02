# IL-HTE Econ, 32: Maruyama (2022) IJER - Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

maruyama_wide_t1 <- read_csv(glue("{raw}/32 student_test_7_baseline.csv")) |> 
  select(s_id = ID_IE_test,
         cov_urban = urban.rural,
         cov_age = Age,
         cov_male = Sex,
         cov_repeat_grade = Repeated,
         contains("Correct_or_Wrong")) |> 
  # seem to be some duplicate questions
  # take the first 20 as these are what the codebook suggests
  select(s_id, contains("cov_"), Q1_Correct_or_Wrong_G7:Q20_Correct_or_Wrong_G7) |> 
  mutate(cov_urban = if_else(cov_urban == "Urbana", 1, 0))

# bring in endline
maruyama_wide_t2 <- read_csv(glue("{raw}/32 student_test_7_endline.csv")) |> 
  select(s_id = ID_IE_test, 
         cluster_id = ID_IE, 
         treat = treatment, 
         contains("Correct_or_Wrong")) |> 
  mutate(treat = if_else(treat == "Control", 0, 1))

# make person file
maruyama2022_p <- maruyama_wide_t1 |>
  select(-contains("Q"),) |>
  left_join(select(maruyama_wide_t2, contains("_id"), treat))

# items
maruyama2022_i_pre <- maruyama_wide_t1 |> 
  select(s_id, contains("Q")) |> 
  pivot_longer(contains("Q"), names_to = "item", values_to = "score") |> 
  mutate(time = 0) |> 
  drop_na(score)

maruyama2022_i_post <- maruyama_wide_t2 |> 
  select(s_id, contains("Q")) |> 
  pivot_longer(contains("Q"), names_to = "item", values_to = "score") |> 
  mutate(time = 1) |> 
  drop_na(score)

maruyama2022_i <- maruyama2022_i_pre |> 
  bind_rows(maruyama2022_i_post) |> 
  mutate(item = parse_number(item))

maruyama2022 <- maruyama2022_i |> 
  left_join(maruyama2022_p, by = "s_id") |> 
  arrange(s_id, item, time)

rm(maruyama2022_i, maruyama2022_i_post, maruyama2022_i_pre, maruyama2022_p,
   maruyama_wide_t1, maruyama_wide_t2)
