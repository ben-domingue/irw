library(readr)
library(tidyverse)

df <- read_csv('2015_100_skill_builders_main_problems.csv')

df <- df |>
  # drop unneeded variable
  select(-sequence_id) |>
  # rename response variable to IRW standards
  rename(resp = correct)

# create item IDs for each assistment item
items <- as.data.frame(unique(df$log_id))
items <- items |>
  arrange(unique(df$log_id)) |>
  mutate(item = row_number())

# create unique IDs for each user
ids <- as.data.frame(unique(df$user_id))
ids <- ids |>
  arrange(unique(df$user_id)) |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("log_id" = "unique(df$log_id)")) |>
  # merge user IDs with df
  left_join(ids, 
            by=c("user_id" = "unique(df$user_id)")) |>  
  # select only needed variables
  select(id, item, resp) |>
  # sort df by user ID and item ID
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="assistments_1516.Rdata")
