library(tidyverse)
library(readr)

df <- read_csv('more_2122_anon.csv')

df <- df |>
  select(s_id,
         s_itt_2122,
         s_correct,
         item_id) |>
  rename(id = s_id,
         treatment = s_itt_2122,
         resp = s_correct)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item_id))
items <- items |>
  arrange(unique(df$item_id)) |>
  mutate(item = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item_id" = "unique(df$item_id)")) |>
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="hte_irw.Rdata")