library(tidyverse)
library(readr)

df <- read_csv('numbergame_data.csv')

df <- df |>
  select(set, id, rating, rt) |>
  # adjust id variable so that the first unique id is 1
  mutate(id = id + 1) |>
  rename(resp = rating)

# create item IDs for each survey item
items <- as.data.frame(unique(df$set))
items <- items |>
  mutate(item = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("set" = "unique(df$set)")) |>
  # drop character item variable
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="number_pattern_game.Rdata")
