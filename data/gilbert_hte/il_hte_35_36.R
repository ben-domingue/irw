# IL-HTE Econ, 35/36: Persson (2020) JESP - Democratic Values/Political Knowledge
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

persson2020 <- read_dta(glue("{raw}/35 Deliberation_Data.dta")) |> 
  select(s_id = studentID, cluster_id = classID, treat = t,
         cov_female = female,
         cov_mother_country_origin = mother,
         cov_father_country_origin = father,
         cov_books_in_home = books,
         # 1 is baseline, 2 is endline
         # items have already been reversed
         contains("values1"), contains("values2"), contains("values3"),
         contains("knowledge1"), contains("knowledge2"), contains("knowledge3"),
         -starts_with("x")) |> 
  # ID 709 is doubled for some reason, distinguish them
  # by renumbering them
  mutate(s_id = row_number(),
         across(cov_mother_country_origin:cov_father_country_origin, ~
                  case_when(
                    . == 1 ~ "Outside Europe",
                    . == 2 ~ "Europe",
                    . == 3 ~ "Nordic Country",
                    . == 4 ~ "Sweden"
                  )),
         cov_books_in_home = case_when(
           cov_books_in_home == 1 ~ "<50",
           cov_books_in_home == 2 ~ "50-100",
           cov_books_in_home == 3 ~ "200-500",
           cov_books_in_home == 4 ~ ">500"
         )) |> 
  # pivot to long
  pivot_longer(c(contains("values"), contains("knowledge")), 
               names_to = "item", values_to = "polyscore") |> 
  drop_na(polyscore) |> 
  mutate(
    time = case_when(
      str_detect(item, "1") ~ 0,
      str_detect(item, "2") ~ 1,
      str_detect(item, "3") ~ 2),
    outcome = if_else(str_detect(item, "values"), "values", "knowledge"),
    item = str_replace_all(item, "[0-9]", "_")
  ) |> 
  arrange(s_id, item, time)

persson2020_a <- persson2020 |> 
  filter(outcome == "values") |> 
  mutate(score = if_else(polyscore > 2, 1, 0))

persson2020_b <- persson2020 |> 
  filter(outcome == "knowledge") |> 
  rename(score = polyscore)

rm(persson2020)
