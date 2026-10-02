# IL-HTE Econ, 13/14/15: Romero (2020) AER - Literacy/Math/Raven's
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# read in the data
romero2020_pre <- read_dta(glue("{raw}/13 Student Baseline.dta")) |> 
  select(s_id = uniqueid_nopii, 
         treat = treatment,
         cluster_id = schoolid_nopii,
         cov_female = gender,
         cov_age = age,
         contains("objectid"), contains("preposition"), contains("daysequence"),
         contains("listening"),
         matches(".*_comp"),
         contains("numdiscrim"), contains("addition"),
         contains("subtraction"), contains("multiplication"),
         contains("division"), contains("shape"), contains("wordprob"),
         -contains("complete"), -contains("example"), -contains("timeremain"),
         -matches(".*_correct"),
         -c(listening_comp_story1, listening_comp_story2, 
            IRT_Composite, addition_level1_counting,
            addition_level2_counting,
            subtraction_level1_counting, subtraction_level2_counting)
         ) |> 
  mutate(cov_female = if_else(cov_female == 2, 1, 0))

# split into language and math
romero2020a_pre <- romero2020_pre |> 
  select(s_id, objectid1:reading_level2_comp5)

romero2020b_pre <- romero2020_pre |> 
  select(s_id, numdiscrim1:last_col())

# get baseline math score for ravens, which doesn't have pre items
romero2020_math <- romero2020b_pre |>
  select(-s_id) |>
  rasch_score(".")

romero2020_p <- romero2020_pre |>
  mutate(baseline_math = fscores(romero2020_math)[,],
         std_baseline_math = scale(baseline_math)[,]) |>
  select(contains("_id"), treat, contains("cov_"), 
         std_baseline_math)

romero2020_a_i <- romero2020a_pre |> 
  pivot_longer(-s_id, names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = 0)

romero2020_b_i <- romero2020b_pre |> 
  pivot_longer(-s_id, names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = 0)

romero2020_post <- read_dta(glue("{raw}/13 Student Endline.dta")) |> 
  select(s_id = uniqueid_nopii,
         contains("objectid"), contains("daysequence"),
         contains("pronoun"), contains("listening"), matches(".*_comp"),
         contains("numdiscrim"), contains("addition"),
         contains("subtraction"), contains("multiplication"),
         contains("division"), contains("shape"), contains("wordprob"),
         contains("raven"),
         -contains("complete"), -contains("example"), -contains("timeremain"),
         -matches(".*_correct"),
         -c(IRT_Composite, IRT_Composite_byg, addition_level1_counting,
            addition_level2_counting,
            subtraction_level1_counting, subtraction_level2_counting,
            raven_test1)
         )

# split into the three outcomes
romero2020_a_i <- romero2020_post |> 
  select(s_id, objectid1:reading_level2_comp2) |> 
  pivot_longer(objectid1:reading_level2_comp2,
               names_to = "item",
               values_to = "score") |> 
  mutate(time = 1) |> 
  bind_rows(romero2020_a_i) 

romero2020_b_i <- romero2020_post |> 
  select(s_id, numdiscrim1:wordprob6_b) |> 
  pivot_longer(numdiscrim1:wordprob6_b,
               names_to = "item",
               values_to = "score") |> 
  mutate(time = 1) |> 
  bind_rows(romero2020_b_i) |> 
  drop_na(score) |> 
  arrange(s_id, time, item)

romero2020_c_i <- romero2020_post |> 
  select(s_id, contains("raven")) |> 
  pivot_longer(contains("raven"),
               names_to = "item",
               values_to = "score") |> 
  mutate(time = 1)

# combine
romero2020_a <- romero2020_a_i |> 
  left_join(romero2020_p, by = "s_id") |> 
  # rename(std_baseline = std_baseline_lang) |> 
  select(-std_baseline_math) |> 
  arrange(s_id, item, time)

romero2020_b <- romero2020_b_i |> 
  left_join(romero2020_p, by = "s_id") |> 
  arrange(s_id, item, time) |> 
  # rename(std_baseline = std_baseline_math) |> 
  select(-std_baseline_math)

romero2020_c <- romero2020_c_i |> 
  left_join(romero2020_p, by = "s_id") |> 
  rename(std_baseline = std_baseline_math)

rm(romero2020_a_i, romero2020_b_i, romero2020_c_i,
   romero2020_p, romero2020_post, romero2020_lang,
   romero2020_math, romero2020_pre, romero2020a_pre,
   romero2020b_pre)
