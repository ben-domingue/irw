library(tidyverse)
library(readr)

df <- read_csv("DotsTask_Raw.csv")

df <- df |>
  select(subject,
         trial,
         iscorrect) |>
  rename(resp = iscorrect)

# create item IDs for each survey item
items <- as.data.frame(unique(df$trial))
items <- items |>
  arrange(unique(df$trial)) |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$subject))
ids <- ids |>
  arrange(unique(df$subject)) |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("trial" = "unique(df$trial)")) |>
  left_join(ids, by=c('subject' = "unique(df$subject)")) |>
  # drop character item variable
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="differences_spotting_study3_dots.Rdata")
