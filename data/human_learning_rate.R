library(tidyverse)
library(readr)
library(janitor)


df <- read_delim('ds104_student_step_All_Data_218_2016_0406_071258.txt')

df <- df |>
  clean_names(case = 'snake') |>
  select(anon_student_id,
         problem_name,
         step_duration_sec,
         step_start_time,
         first_attempt) |>
  mutate(step_start_time = paste0(step_start_time, " EST"),
         date = as.numeric(as.POSIXct(step_start_time, format="%Y-%m-%d %H:%M:%OS")),
         resp = case_when(first_attempt == 'correct' ~ 1,
                          first_attempt == 'incorrect' | first_attempt == 'hint' ~ 0)) |>
  rename(rt = step_duration_sec) |>
  drop_na()

items <- as.data.frame(unique(df$problem_name))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$anon_student_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("problem_name" = "unique(df$problem_name)")) |>
  left_join(ids, by=c('anon_student_id' = "unique(df$anon_student_id)")) |>
  # drop character item variable
  select(id, date, item_id, resp, rt) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item, date)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="human_learning_rate.Rdata")
