library(tidyverse)
library(readr)

df <- read_delim('data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded variables
  select(-gender,
         -score) |>
  # replace invalid ages with NA
  mutate(age = if_else(age > 99, NA, age),
         # create id variable
         id = row_number()) |>
  # replace invalid values with NA
  mutate_all(~ replace(., . == 0, NA)) |>
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
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  # recode item responses to be wrong/right 0/1 binaries
  mutate(resp = case_when(resp == 10 ~ 1,
                          resp >= 1 & resp <= 7 ~ 0,
                          is.na(resp) ~ NA))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="experimental_iq.Rdata")
