library(tidyverse)
library(readr)
library(janitor)

# Each source CSV has one MORE field per data row than it has header names,
# because the leading subject-label column is unnamed. Left to itself read_csv
# lines the names up from the left, so "Choice_1" lands on the subject label,
# "Choice_2" on trial 1, and the final trial of every study has no name and is
# dropped. Name the first column explicitly so the trials line up and none is lost.
read_igt <- function(path, n_trials) {
  read_csv(path, col_names = c("subj", paste0("trial_", seq_len(n_trials))),
           skip = 1, show_col_types = FALSE)
}
choice95 <- read_igt('choice_95.csv', 95)
choice100 <- read_igt('choice_100.csv', 100)
choice150 <- read_igt('choice_150.csv', 150)

# batch process datasets in enviroment
all_objects <- ls()
dataframe_names <- all_objects[sapply(all_objects, function(x) is.data.frame(get(x)))]

# iterate over each dataframe
for (name in dataframe_names) {
  # get the dataframe object
  dataset <- get(name)
  
  # convert the variable names to lowercase
  new_names <- tolower(names(dataset))
  # add df name to beginning of trial variable names to distinguish trial_2 from df choice100 from trial_2 from df choice150
  new_names <- paste0(name, new_names)
  new_names <- if_else(str_detect(new_names, 'subj$'), 'id', new_names)
  
  # reassign new names to dataframe
  names(dataset) <- new_names
  
  dataset <- dataset |>
    # reshape dataframes to be long by id and item
    pivot_longer(cols = -id,
                 names_to = 'item',
                 values_to = 'resp') |>
    # remove characters from subject IDs so that they're numeric
    mutate(id = as.numeric(str_remove_all(id, 'Subj_')),
           # recode invalid response values as NA
           resp = if_else(resp > 4, NA, resp)) |>
    drop_na()

  # assign the modified dataframe back to the environment
  assign(name, dataset)
}

choice100 <- choice100 |>
  # update participant IDs of choice100 so that they start at 16 (last ID of participant in choice95 is 15)
  mutate(id = id + 15)

choice150 <- choice150 |>
  # update participant IDs of choice150 so that they start at 520 (last ID of participant in choice95 is 519)
  mutate(id = id + 519)

# combine item responses from different studies
df <- rbind(choice95, choice100, choice150)

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
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="iowa_gambling_task.Rdata")
