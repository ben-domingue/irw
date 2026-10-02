# IL-HTE Econ, 70/71/72/73 Banerjee (2017) JEP - Language and Math
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

# Here, it appears that the G1-G2 and G3-G5 were given different tests, so separating. The e1 tests are performing very strangely, so I'm treating e2 as the endline, which seems right when I examine the Stata file. Leaving the e1 in as midline, but I'm not analyzing these.

banerjee2017 <- read_dta(glue("{raw}/70 bihar_analysis.dta")) |> 
  select(cluster_id = villageid, 
         cov_female = female, cov_age = age_year, 
         cov_grade = base_standard,
         treat = treatvillage,
         contains("b_langwrit"), contains("e1_langwrit"), contains("e2_langwrit"),
         contains("b_mathwrit"), contains("e1_mathwrit"), contains("e2_mathwrit"),
         # this separates the samples
         e2_std12, e2_std35
         ) |> 
  # childid was messed up, make new id
  mutate(s_id = row_number()) |> 
  # pivot to long
  pivot_longer(b_langwrit_std12_let_dic1:e2_mathwrit_std35_div_c, 
               names_to = "item",
               values_to = "score") |> 
  drop_na(score) |> 
  # a few outside 0/1, ignore
  filter(score %in% c(0,1)) |> 
  # get other characteristics
  mutate(
    time = case_when(
      str_starts(item, "b_") ~ 0,
      str_starts(item, "e1_") ~ 0.5,
      str_starts(item, "e2_") ~ 1
    ),
    test = if_else(str_detect(item, "langwrit"), "language", "math"),
    item = str_remove(item, "b_|e1_|e2_"),
    item_grade = word(item, 2, 2, sep = "_")
  )

# split into separate files
banerjee2017_c <- banerjee2017 |> 
  filter(e2_std12 == 1, 
         test == "language",
         # make sure the test item lines up with the grade level
         # there appears to be some noise here
         item_grade == "std12")

banerjee2017_d <- banerjee2017 |> 
  filter(e2_std12 == 1, test == "math", item_grade == "std12")

banerjee2017_e <- banerjee2017 |> 
  filter(e2_std35 == 1, test == "language", item_grade == "std35")

banerjee2017_f <- banerjee2017 |> 
  filter(e2_std35 == 1, test == "math", item_grade == "std35")

rm(banerjee2017)
