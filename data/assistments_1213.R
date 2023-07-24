library(readr)
library(tidyverse)
library(janitor)

df <- read_csv('2012-2013-data-with-predictions-4-final.csv')

df <- df |>
  select(user_id,
         problem_id,
         start_time,
         end_time,
         correct) |>
  # convert timestamp to unix time
  mutate(date = as.numeric(as.POSIXct(start_time, format="%Y-%m-%d %H:%M:%OS")),
         end_time_unix = as.numeric(as.POSIXct(end_time, format="%Y-%m-%d %H:%M:%OS")),
         rt = end_time_unix - date)

# create item IDs for each survey item
items <- as.data.frame(unique(df$problem_id))
items <- items |>
  arrange(unique(df$problem_id)) |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$user_id))
ids <- ids |>
  arrange(unique(df$user_id)) |>
  mutate(id = row_number())


df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("problem_id" = "unique(df$problem_id)")) |>
  left_join(ids, 
            by=c("user_id" = "unique(df$user_id)")) |>  
  # rename variables
  rename(resp = correct) |>
  # drop character item variable
  select(id, item, date, resp, rt) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="assistments_1213.Rdata")
