library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded columns
  select(-gender,
         -accuracy,
         -country,
         -age) |>
  # replace invalid values with NA
  mutate_all(~ replace(., . == 0, NA)) |>
  # create ID variable
  mutate(id = row_number()) |>
  # pivot dataframe to be long by item
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
save(df, file="hypersensitive_narcissism.Rdata")
