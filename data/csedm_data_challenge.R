library(tidyverse)
library(readr)
library(janitor)

# import and process item response data
df <- read_csv('Predict.csv')

df <- df |>
  # standardize variable names to lowercase
  clean_names(case = 'snake') |>
  # select relevant variables
  select(subject_id, problem_id, ever_correct)

# create item IDs for each survey item
items <- as.data.frame(unique(df$problem_id))
items <- items |>
  mutate(item_id = row_number())

# create numerical IDs for each participant in df
ids <- as.data.frame(unique(df$subject_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item and participant IDs with df
  left_join(items, 
            by=c("problem_id" = "unique(df$problem_id)")) |>
  left_join(ids,
            by=c("subject_id" = "unique(df$subject_id)")) |>
  # drop character item variable
  select(id, item_id, ever_correct) |>
  # use item_id column as the item column
  # use ever_correct as the resp column
  rename(item = item_id,
         resp = ever_correct) |>
  # recode resp column to be aligned with IRW standards
  mutate(resp = case_when(resp == 'TRUE' ~ 1,
                          resp == 'FALSE' ~ 0)) |>
  # sort df by participant and item id
  arrange(id, item)

# print response values
table(df$resp)
# ----

# import and process process data
process <- read_csv('MainTable.csv')

process <- process |>
  # convert column names to lowercase
  clean_names(case = 'snake') |>
  # keep necessary columns
  select(subject_id,
         server_timestamp,
         problem_id,
         event_type,
         event_id) |>
  # convert timestamp to unix time
  mutate(server_timestamp = paste(server_timestamp, "ET"),
         timestamp = as.numeric(as.POSIXct(server_timestamp, format="%Y-%m-%d %H:%M:%OS"))) |>
  # rename column to IRW standards
  rename(event = event_type) |>
  # merge item and participant IDs with process df
  left_join(items, 
            by=c("problem_id" = "unique(df$problem_id)")) |>
  left_join(ids,
            by=c("subject_id" = "unique(df$subject_id)"))

# for generate item IDs for items only in process df, not in original IR df
items2 <- as.data.frame(unique(process[is.na(process$item_id),]$problem_id))
items2 <- items2 |>
  mutate(item_id2 = row_number() + max(process$item_id, na.rm = T))

process <- process |>
  # join new item IDs with process df
  left_join(items2,
            by=c('problem_id' = 'unique(process[is.na(process$item_id), ]$problem_id)')) |>
  # for process df items without IDs, replace their NA values with new item IDs
  mutate(item_id = if_else(is.na(item_id), item_id2, item_id),
         # assign participant ID to one participant only in process df that's missing participant ID
         id = if_else(is.na(id), max(process$id, na.rm = T) + 1, id)) |>
  # keep only revelant columns
  select(id, item_id, timestamp, event) |>
  # use item_id column as the item column
  arrange(id, item_id, timestamp) |>
  group_by(id, item_id) |>
  # create index for temporal order of events by item
  mutate(event_id = row_number()) |>
  ungroup() |>
  select(id, item_id, event_id, timestamp, event) |>
  # rename item_id according to IRW standards
  rename(item = item_id)


# save IR and process data to Rdata file
attr(df, which='process') <- process
save(df, file="csedm_data_challenge.Rdata")
