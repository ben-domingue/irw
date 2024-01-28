library(tidyverse)
library(readr)

df <- read_csv("SolvableItemsSelection_Summary_CombinedSampleN=135.csv")

df <- df |>
  select(subject,
         age,
         starts_with('perform_pic')) |>
  pivot_longer(cols = -c(subject, age),
               names_to = 'item',
               values_to = 'resp')

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$subject))
ids <- ids |>
  arrange(unique(df$subject)) |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('subject' = "unique(df$subject)"))|>
  # drop character item variable
  select(id, age, item.y, resp) |>
  rename(item = item.y) |>
  # use item_id column as the item column
  arrange(id, item) |>
  drop_na()

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="differences_spotting_study2.Rdata")
