library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded columns
  select(-nis_score,
          -country,
          -introelapse,
          -testelapse,
          -surveyelapse,
          -education,
          -urban,
          -gender,
          -engnat,
          -age,
          -hand,
          -religion,
          -orientation,
          -race,
          -voted,
          -married,
          -familysize,
          -major,
          -`...97`,
          -`...98`) |>
  # replace invalid values with NA
  mutate(across(starts_with('tipi') | starts_with('q'), ~if_else(. == 0, NA, .)),
         # add participant ID column
         id = row_number())

# create separate df for response times to merge onto their respective items later
times <- df |>
  # drop response time variables
  select(id, 
         starts_with('e')) |>
  # pivot long by ID
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  mutate(item = str_replace(item, 'e', 'q'))

df <- df |>
  # drop the response time variables
  select(-starts_with('e')) |>
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
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="nonverbal_immediacy.Rdata")
