library(readr)
library(tidyverse)
library(janitor)

non_skillbuilder <- read_csv('non_skill_builder_data_new.csv')
skillbuilder <-read_csv('skill_builder_data_corrected_collapsed.csv')

# batch process datasets in enviroment
dataframe_names <- ls()

# iterate over each dataframe
for (name in dataframe_names) {
  # get the dataframe object
  dataset <- get(name)

  dataset <- dataset |>
    select(user_id, problem_id, correct) |>
    arrange(user_id, problem_id) |>
    rename(resp = correct)
  
  # create item IDs for each survey item
  items <- as.data.frame(unique(dataset$problem_id))
  items <- items |>
    mutate(item = row_number())
  
  dataset <- dataset |>
    # merge item IDs with df
    left_join(items, 
              by=c("problem_id" = "unique(dataset$problem_id)")) |>
    # drop character item variable
    select(user_id, item, resp) |>
    # use item_id column as the item column
    arrange(user_id, item)

  # assign the modified dataframe back to the environment
  assign(name, dataset)
}

skillbuilder <- skillbuilder |>
  # adjust item ids for skillbuilder df so that they start after the last unique item ID from the non_skillbuilder df (6907)
  mutate(item = item + 6907)

df <- rbind(non_skillbuilder, skillbuilder)

ids <- as.data.frame(unique(df$user_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  left_join(ids,
            by=c("user_id" = "unique(df$user_id)")) |>
  select(id, item, resp) |>
  mutate(resp = if_else(resp != 0 & resp != 1, NA, resp)) |>
  drop_na()

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="assistments_0910.Rdata")
