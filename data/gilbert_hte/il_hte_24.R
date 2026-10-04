# IL-HTE Econ, 24: Llaurado (2014) BMJ - Health
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.
# Run il_hte_00_setup.R first (libraries, `raw`/`clean` paths, rasch_score()).

llaurado2024 <- read_xls(glue("{raw}/24 BBDD EdAl_2 study and glossari.xls")) |> 
  clean_names() |> 
  drop_na(id_children) |> 
  # ids unique by school + child
  mutate(s_id = glue("{id_school}-{id_children}")) |> 
  select(s_id, cluster_id = id_school, treat = group,
         cov_gender = gender,
         cov_ethnicity = ethnic,
         cov_age = age1,
         mbreakfast, xbreakfast, contains("fruit"),
         contains("veg"), contains("fish"), contains("fast_food"),
         contains("legumes"), contains("candy"), contains("pasta"),
         contains("oil")) |> 
  # reverse code bad things
  mutate(across(c(m_fast_food, x_fast_food, mcandy, xcandy), ~ 1 - .),
         # looks like some weren't dichotomized properly according to codebook
         # fix
         across(contains("fruit"), ~ if_else(. > 0, 1, 0))
         ) |> 
  mutate(cov_male = if_else(cov_gender == 1, 1, 0),
         cov_ethnicity = case_when(
           cov_ethnicity == 1 ~ "Western Europe",
           cov_ethnicity == 2 ~ "Eastern Europe",
           cov_ethnicity == 3 ~ "Latin America",
           cov_ethnicity == 4 ~ "Northern Africa",
           cov_ethnicity == 5 ~ "Southern Africa",
           cov_ethnicity == 6 ~ "China",
           cov_ethnicity == 7 ~ "USA"
         )) |> 
  select(-cov_gender) |> 
  # pivot to long
  select(contains("_id"), treat, contains("cov_"),
         starts_with("m"), starts_with("x")) |> 
  pivot_longer(c(starts_with("m"), starts_with("x")), 
               names_to = "item", values_to = "score") |> 
  drop_na(score) |> 
  mutate(time = if_else(str_starts(item, "m"), 0, 1),
         item = str_remove(item, "m_|x_"),
         item = str_remove(item, "m|x")) |> 
  arrange(s_id, item, time)
