##https://github.com/ben-domingue/irw/issues/920#event-17081987494



                                        # start with the knowledge test
# only at endline and followup
ekin2025_a_post <- read_xlsx(glue("{raw}/95 Immediate Test.xlsx")) |> 
  clean_names() |> 
  select(id = 1, treat = 2, cov_male = 3, cov_repeat_year = 4,
         # items
         contains("kfq")
         ) |> 
  mutate(cov_male = cov_male - 1,
         wave = 1) |> 
  pivot_longer(contains("kfq"), names_to = "item", values_to = "resp")

ekin2025_a_fup <- read_xlsx(glue("{raw}/95 Delayed Test.xlsx")) |> 
  clean_names() |> 
  select(id = 1, treat = 2, cov_male = 3, cov_repeat_year = 4,
         # items
         contains("kfq")
         ) |> 
  mutate(cov_male = cov_male - 1,
         wave = 2) |> 
  pivot_longer(contains("kfq"), names_to = "item", values_to = "resp")

ekin2025_a <- bind_rows(ekin2025_a_post, ekin2025_a_fup) |> 
  arrange(id, item, wave)

rm(ekin2025_a_post, ekin2025_a_fup)

write_csv(ekin2025_a, glue("{clean}/gilbert_meta_95.csv"))

# AI attitude
# includes baseline and endline
ekin2025_b_pre <- read_xlsx(glue("{raw}/96 Pre-Intervention Survey on Critical Approach to AI.xlsx")) |> 
  clean_names() |> 
  rename(treat = 2, cov_male = 3, cov_repeat_year = 4) |> 
  mutate(cov_male = cov_male - 1) |> 
  pivot_longer(5:last_col(), names_to = "item", values_to = "resp") |> 
  mutate(wave = 0)

ekin2025_b_post <- read_xlsx(glue("{raw}/96 Post-Intervention Survey on Critical Approach to AI.xlsx")) |> 
  clean_names() |> 
  rename(treat = 2, cov_male = 3, cov_repeat_year = 4) |> 
  mutate(cov_male = cov_male - 1) |> 
  pivot_longer(5:last_col(), names_to = "item", values_to = "resp") |> 
  mutate(wave = 1)

ekin2025_b <- bind_rows(ekin2025_b_pre, ekin2025_b_post) |> 
  arrange(id, item, wave)

rm(ekin2025_b_pre, ekin2025_b_post)

write_csv(ekin2025_b, glue("{clean}/gilbert_meta_96.csv"))
