library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-country,
         -introelapse,
         -testelapse,
         -surveyelapse,
         -education,
         -urban,
         -gender,
         -engnat,
         -age,
         -screenw,
         -screenh,
         -hand,
         -religion,
         -orientation,
         -race,
         -voted,
         -married,
         -familysize,
         -major,
         -ends_with('o'),
         -ends_with('i')) |>
  # replace invalid values with NA
  mutate(across(starts_with('tipi') | ends_with('a'), ~if_else(. == 0, NA, .)),
         # add ID variable
         id = row_number())

# create separate df for response times to merge onto their respective items later
times <- df |>
  select(id, 
         ends_with('e')) |>
  # pivot long by ID
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  # match response time variable names to their corresponding item ID
  mutate(item = str_replace(item, 'e', 'a'),
         # convert response time from milliseconds to seconds
         rt = rt / 1000)

df <- df |>
  # drop time variables
  select(-ends_with('e')) 

df <- df |>
  # pivot data to be long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  left_join(times, by=c('id', 'item'))

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
save(df, file="artistic_preferences.Rdata")
