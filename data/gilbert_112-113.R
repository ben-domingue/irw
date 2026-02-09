weerdt2026 <- read_xlsx(glue("{raw}/112 Data_MainStudy.xlsx")) |> 
  clean_names() |> 
  mutate(cov_male = if_else(gender == "Boy", 1, 0),
         treat = if_else(treatment == "Solo", 0, 1)) |> 
  select(id,
         wave = time,
         cluster_id = class_id,
         block_id = school_id,
         treat,
         cov_male,
         cov_grade = grade, 
         content,
         starts_with("item_")) |>
  pivot_longer(starts_with("item_"),
               names_to = "item",
               values_to = "resp") |> 
  mutate(resp = parse_number(resp)) |> 
  drop_na(resp) |> 
  arrange(id, item, wave)

# crossover experiment, so same students get different treatments
# at different times
# treating as two separate experiments here for the separate outcomes
weerdt2026_a <- weerdt2026 |> 
  filter(content == "Forces") |> 
  select(-content)

weerdt2026_b <- weerdt2026 |> 
  filter(content == "DNA") |> 
  select(-content)

# verify randomization structure
table(weerdt2026_a$treat, weerdt2026_a$cluster_id)
table(weerdt2026_a$treat, weerdt2026_a$block_id)

# export
write_csv(weerdt2026_a, glue("{clean}/gilbert_meta_112.csv"))
write_csv(weerdt2026_b, glue("{clean}/gilbert_meta_113.csv"))
