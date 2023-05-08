library(tidyverse)
library(readr)
library(janitor)

master <- read_delim('algebra_2006_2007_master.txt')

train <- read_delim('algebra_2006_2007_train.txt')

test <- read_delim('algebra_2006_2007_test.txt')

# clean variable names and drop unneeded variables
master <- master |>
  clean_names() |>
  select(anon_student_id,
         problem_name,
         step_name,
         step_start_time,
         correct_first_attempt)

# clean variable names and drop unneeded variables
train <- train |>
  clean_names() |>
  select(anon_student_id,
         problem_name,
         step_name,
         step_start_time,
         correct_first_attempt)

# clean variable names and drop unneeded variables
test <- test |>
  clean_names() |>
  select(anon_student_id,
         problem_name,
         step_name,
         step_start_time,
         correct_first_attempt)

# combine test, train, and master datasets
df <- rbind(master, train, test) 

df <- df |>
  # drop duplicate rows
  filter(!is.na(step_start_time)) |>
  # rename variables to be consistent with irw standards
  rename(id = anon_student_id,
         resp = correct_first_attempt) |>
  # create one item variable
  mutate(item = paste0(problem_name, step_name),
         # convert date variable to unix time
         step_start_time = paste0(step_start_time, ' EST'),
         date = as.numeric(as.POSIXct(step_start_time, format="%Y-%m-%d %H:%M:%OS"))) |>
  select(-problem_name,
         -step_name,
         -step_start_time)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp, date) |>
  # use item_id column as the item column
  rename(item = item_id)

# create numerical participant IDs
ids <- as.data.frame(unique(df$id))
ids <- ids |>
  mutate(num_id = row_number())

df <- df |>
  # merge numerical IDs with df
  left_join(ids, 
            by=c("id" = "unique(df$id)")) |>
  # drop character item variable
  select(num_id, item, resp, date) |>
  # use item_id column as the item column
  rename(id = num_id)

# response counts
table(df$resp)

# save df to Rdata file
save(df, file="cmu_algebra_2007.Rdata")
