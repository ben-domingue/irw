## Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OUI9LS
## Licence: Public Domain
## https://github.com/ben-domingue/irw/issues/859#event-16481040428

krakowski2025 <- read_dta(glue("{raw}/83 misinformation_data.dta")) |> 
  mutate(id = row_number()) |> 
  # select relevant variables
  select(id, treat = treat_bin, tot = debate, block_id = schoolen,
         cov_age = age, cov_hh_size = hh_size,
         cov_politics = preferred_party,
         pre_need1:pre_conspiracy_item5,
         need1:conspiracy_item5,
         pre_trust_tv:trust_social) |> 
  drop_na(treat) |> 
  # code prefer not to reply as missing for conspiracy items
  mutate(across(contains("conspiracy"), ~ if_else(. == 99, NA_real_, .))) |> 
  # pivot to long
  pivot_longer(pre_need1:trust_social, names_to = "item",
               values_to = "resp") |> 
  drop_na(resp) |> 
  # differentiate pre/post
  mutate(wave = if_else(word(item, 1, 1, sep = "_") == "pre", 0, 1),
         item = str_remove(item, "pre_"),
         test = word(item, 1, 1, sep = "_") |> tm::removeNumbers()) |> 
  arrange(id, test, item, wave)

# export by outcome
krakowski2025 |> 
  filter(test == "need") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_83.csv"))

krakowski2025 |> 
  filter(test == "conspiracy") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_84.csv"))

krakowski2025 |> 
  filter(test == "trust") |> 
  select(-test) |> 
  write_csv(glue("{clean}/gilbert_meta_85.csv"))
