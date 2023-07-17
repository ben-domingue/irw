library(tidyverse)
library(readr)
library(janitor)

df <- read_csv('Study1_TReATQ_RH_NFC_DATA_raw.csv')

df <- df |>
  clean_names(case = 'snake') |>
  select(sub_id,
         age,
         starts_with('soc_'),
         starts_with('nfc_'),
         starts_with('rh_'),
         magazines_in_print,
         magazines_on_line,
         fiction_books,
         fantasy_science_fiction,
         literature,
         non_fiction,
         books,
         newspapers_on_line,
         newspapers_in_print,
         mystery_adventure,
         romance,
         sports,
         nature,
         biography,
         history,
         self_help,
         other,
         autobiography,
         -rh_8) |>
  # rescale all NFC and SOC items so that their values are all photos
  mutate(across(starts_with('nfc_') | starts_with('soc_'), ~. + 4)) |>
  rename(id = sub_id) |>
  pivot_longer(cols = -c(id, age),
               names_to = 'item',
               values_to = 'resp')

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())


df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, age, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="approaches_to_text_study1.Rdata")

