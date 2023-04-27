library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-ip_country,
         -engnat,
         -age,
         -education,
         -gender,
         -urban,
         -orientation,
         -race,
         -religion,
         -hand,
         -introelapse,
         -testelapse,
         -score,
         -fastclicks,
         -starts_with('pqi')) |>
  # add ID variable
  mutate(id = row_number()) |>
  # replace invalid values with NA
  mutate_all(~ replace(., (. == -1) | (. == 0), NA))

# create separate df of just item response times
times <- df |>
  select(id,
         starts_with('lapse')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  mutate(item = str_replace_all(item, 'lapse', 'q'))

df <- df |>
  select(-starts_with('lapse')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  left_join(times, by=c('id', 'item')) |>
  # convert response time from milliseconds to seconds 
  mutate(rt = rt / 1000)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp, rt) |>
  # use item_id column as the item column
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="face_memory_test.Rdata")
