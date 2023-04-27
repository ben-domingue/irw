library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unnneeded variables
  select(-ends_with('i'),
         -country,
         -dateload,
         -introelapse,
         -testelapse,
         -surveyelapse,
         -gender,
         -engnat,
         -age,
         -ie) |>
  # add ID variable
  mutate(id = row_number(),
         # replace invalid values with NA
         across(starts_with('tipi') | starts_with('q'), ~if_else(. == 0, NA, .)))

# create separate df for response times to merge onto their respective items later
times <- df |>
  select(id, 
         ends_with('e')) |>
  # pivot long by ID
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  mutate(item = str_replace(item, 'e', 'a'))

df <- df |>
  # drop the response time variables
  select(-ends_with('e')) |>
  # pivot to be long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # pivot data to be long by item
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
  rename(item = item_id) |>
  mutate(item = str_remove(item, 'q'),
         item = str_remove(item, 'a'))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="introversion_extroversion.Rdata")
