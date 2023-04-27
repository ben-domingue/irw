library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded columns
  select(-education,
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
         -introelapse,
         -testelapse,
         -surveyelapse,
         -uniquenetworklocation,
         -screensize,
         -country,
         -ends_with('i'),
         -starts_with('drug')) |>
  mutate(id = row_number(),
         # replace invalid values with NA
         across(starts_with('tipi') | ends_with('a'), ~if_else(. == 0, NA, .)))


times <- df |>
  select(id,
         ends_with('e')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  mutate(rt = rt / 1000,
         item = str_replace(item, 'e', 'a'))


df <- df |>
  select(-ends_with('e')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  left_join(times,
            by=c('id', 'item'))

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
save(df, file="fisher_temperment.Rdata")