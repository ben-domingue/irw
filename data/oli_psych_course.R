library(tidyverse)
library(readr)
library(janitor)

df <- read_delim('OLI-Psych_Q9.txt')

df <- df |>
  clean_names(case = 'snake') |>
  select(-total_score) |>
  pivot_longer(cols = -user_id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)

items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$user_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('user_id' = "unique(df$user_id)")) |>
  # drop character item variable
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="oli_psych_course.Rdata")
