library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-country) |>
  # create ID variable
  mutate(id = row_number()) |>
  # pivot dataframe to be long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # remove character from item ID variable
  mutate(item = as.numeric(str_replace(item, 'q', '')))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="preference_inventory.Rdata")
