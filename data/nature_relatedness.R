library(tidyverse)
library(readr)

df <- read_delim('data-final.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-education,
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
         -country,
         -introelapse,
         -testelapse,
         -surveyelapse,
         -ends_with('i')) |>
  # add participant ID number
  mutate(id = row_number(),
         across(starts_with('tipi') | ends_with('a'), ~if_else(. == 0, NA, .)))

# create df with item response times to merge onto item responses later
times <- df |>
  # select only id and response time variables
  select(id,
         ends_with('e')) |>
  # pivot long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  # match item id pattern from main dataframe
  mutate(item = str_replace(item, 'e', 'a'),
         # convert response times from milliseconds to seconds
         rt = rt / 1000)

df <- df |>
  select(-ends_with('e')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  left_join(times, 
            by = c('id', 'item'))

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
save(df, file="nature_relatedness.Rdata")
