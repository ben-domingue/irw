library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
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
         -voted,
         -married,
         -familysize,
         -major,
         -starts_with('race'),
         -nerdy,
         -asd,
         -country,
         -introelapse,
         -testelapse,
         -surveyelapse) |>
  # replace invalid values with NA
  mutate(across(starts_with('tipi') | starts_with('q'), ~if_else(. == 0, NA, .)),
         # add ID variable
         id = row_number()) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp')

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="nerdy_personality.Rdata")