library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-gender,
         -country,
         -age) |>
  # replace invalid values with NA
  mutate_all(~ replace(., . == -1, NA)) |>
  # change all item responses to 0/1 binaries
  mutate_all(~ replace(., . == 2, 0)) |>
  # create ID column
  mutate(id = row_number()) |>
  # pivot data to be long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # remove character from item ID variable
  mutate(item = as.numeric(str_replace(item, 'q', '')))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="psychoneurotic_inventory.Rdata")

