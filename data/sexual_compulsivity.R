library(tidyverse)
library(readr)

df <- read_csv('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  select(-gender,
         -score) |>
  # replace all invalid item responses with NA
  mutate_all(~ replace(., . == 0, NA)) |>
  # create id variable
  mutate(id = row_number(),
         age = if_else(age > 100, NA, age)) |>
  # pivot dataframe to be long by item
  pivot_longer(cols = -c(id, age),
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
  select(id, item_id, resp, age) |>
  # use item_id column as the item column
  rename(item = item_id)

# get resp values
table(df$resp)

# save df to Rdata file
save(df, file="sexual_compulsivity.Rdata")  
