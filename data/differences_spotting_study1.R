library(tidyverse)
library(readr)

df <- read_csv('UnsolvableItemsSelection_Raw_CombinedSampleN=131.csv')

df <- df |>
  filter(ischeat == 0)

# create item IDs for each survey item
items <- as.data.frame(unique(df$zhaocha_pic))
items <- items |>
  arrange(unique(df$zhaocha_pic)) |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$subject))
ids <- ids |>
  arrange(unique(df$subject)) |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("zhaocha_pic" = "unique(df$zhaocha_pic)")) |>
  left_join(ids, by=c('subject' = "unique(df$subject)"))  |>
  # drop character item variable
  select(id, item, iscorrect) |>
  # use item_id column as the item column
  arrange(id, item) |>
  rename(resp = iscorrect)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="differences_spotting_study1.Rdata")
