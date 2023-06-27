library(tidyverse)
library(readxl)
library(janitor)

df <- read_excel('Survey master anon.xls')

df <- df |>
  clean_names(case = 'snake') |>
  select(custom_data,
         start_date,
         42:ncol(df)) |>
  mutate(start_date = paste0(start_date, " CT"),
         date = as.numeric(as.POSIXct(start_date, format="%Y-%m-%d %H:%M:%OS")),
         across(starts_with('evaluating'), ~. + 4)) |>
  select(-start_date) |>
  pivot_longer(cols = -c(custom_data, date),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$custom_data))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('custom_data' = "unique(df$custom_data)")) |>
  # drop character item variable
  select(id, date, item_id, resp) |>
  rename(item = item_id) |>
  # use item_id column as the item column
  arrange(id, item, date)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="chinese_vocabulary_learning.Rdata")