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
  mutate_all(~ replace(., (. == -1) | (. == 0), NA)) |>
  # create ID variable
  mutate(id = row_number()) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  mutate(item = as.numeric(str_replace(item, 'q', '')))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="close_relationships.Rdata")

