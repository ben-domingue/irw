library(tidyverse)
library(readr)
library(janitor)


df <- read_csv("Task_3_dataset/checkins_lessons_checkouts_training.csv")

df <- df |>
  clean_names(case = 'snake') |>
  mutate(user_id = user_id + 1,
         date = as.numeric(as.POSIXct(timestamp, format="%Y-%m-%d %H:%M:%OS"))) |>
  rename(id = user_id,
         resp = is_correct) |>
  select(id, question_id, resp, date)

# create item IDs for each survey item
items <- as.data.frame(unique(df$question_id))
items <- items |>
  arrange(unique(df$question_id)) |>
  mutate(item = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("question_id" = "unique(df$question_id)")) |>
  # drop character item variable
  select(id, date, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="neurlps_2022.Rdata")
