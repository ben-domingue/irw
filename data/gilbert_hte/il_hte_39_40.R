# IL-HTE Econ, 39/40: Berry (2022) JDE - Cognitive Skill/Computation
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Note - the items are **different** from baseline to followup.

berry_long <- read_dta(glue("{raw}/39 y1_raw.dta")) |> 
  select(s_id = id,
         treat = rct_edit,
         school = y1_schoolno,
         grade = y1_standard,
         cov_ethnicity = b1_q105,
         cov_home_lang = b1_q106,
         cov_religion = b1_q107,
         # baseline cognitive test
         b1_q1001:b1_q1010,
         # endline cognitive test
         f1_q801:f1_q810,
         # endline computation
         contains("f1_q9")
         ) |> 
  # group 3 is control group
  mutate(treat = if_else(treat == 3, 1, 0),
         # clustered at school-grade level
         cluster_id = glue("{school}_{grade}"),
         across(contains("cov_"), ~ factor(.)),
         cov_ethnicity = case_when(
           cov_ethnicity == 1 ~ "Chewas",
           cov_ethnicity == 2 ~ "Lomwe",
           cov_ethnicity == 3 ~ "Yao",
           cov_ethnicity == 4 ~ "Ngoni",
           cov_ethnicity == 5 ~ "Tumbuka",
           cov_ethnicity == 6 ~ "Other"
         ),
         cov_home_lang = case_when(
           cov_home_lang == 1 ~ "Chichewa",
           cov_home_lang == 2 ~ "Tumbuka",
           cov_home_lang == 3 ~ "Yao",
           cov_home_lang == 4 ~ "English",
           cov_home_lang == 5 ~ "Other"
         ),
         cov_religion = case_when(
           cov_religion == 1 ~ "Catholic",
           cov_religion == 2 ~ "CCAP",
           cov_religion == 3 ~ "Muslim",
           cov_religion == 4 ~ "Baptist",
           cov_religion == 5 ~ "Anglican",
           cov_religion == 6 ~ "Other Christian",
           cov_religion == 7 ~ "None",
           cov_religion == 8 ~ "Other"
         )
         ) |> 
  # score the measures, by taking the test manually...!
  pivot_longer(b1_q1001:f1_q920, names_to = "item", 
               values_to = "response") |> 
  drop_na(response) |> 
  # remove unknown cluster ides
  filter(!str_detect(cluster_id, "NA")) |> 
  # some missing treat
  drop_na(treat)

berry_scoring <- berry_long |> 
  distinct(item) |> 
  mutate(
    correct_response = c(
      # baseline cog
      1, 2, 3, 6, 2, 7, 3, 4, 5, 1,
      # endline cog
      2, 1, 1, 5, 4, 8, 3, 7, 5, 1,
      # endline comp
      3, 1, 4, 3, 2, 2, 2, 3, 2, 1,
      3, 5, 3, 1, 5, 4, 1, 5, 2, 5
    )
  )

berry_wide <- berry_long |> 
  left_join(berry_scoring, by = "item") |> 
  mutate(score = if_else(response == correct_response, 1, 0)) |> 
  select(-response, -correct_response) |> 
  pivot_wider(names_from = item, values_from = score)

# use the baseline score for _a as there are no pre items there
berry_pre <- berry_wide |>
  rasch_score("b1_")

# score the baseline measure
berry2022_p <- berry_wide |>
  mutate(baseline = fscores(berry_pre)[,],
         std_baseline = scale(baseline)[,]) |>
  select(s_id, std_baseline)

# separate by test
berry2022_i <- berry_wide |> 
  pivot_longer(c(contains("b1"), contains("f1")), 
               names_to = "item", values_to = "score") |> 
  mutate(time = if_else(str_detect(item, "b1"), 0, 1),
         outcome = if_else(str_detect(item, "q8"), "cog", "comp")) |> 
  drop_na(score)

berry2022_a <- berry2022_i |> 
  filter(outcome == "cog") |> 
  left_join(berry2022_p, by = "s_id") |>
  arrange(s_id, item, time)

berry2022_b <- berry2022_i |> 
  filter(outcome == "comp")

rm(berry2022_i, berry2022_p, berry_scoring, berry_long)
