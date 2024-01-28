library(tidyverse)
library(readr)
library(janitor)


df <- read_delim('ds4666_tx_All_Data_6786_2021_0303_044455.txt')

df <- df |>
  clean_names(case = 'snake') |>
  filter(attempt_at_step == 1) |>
  select(anon_student_id,
         time,
         time_zone,
         duration_sec,
         problem_name,
         step_name,
         outcome) |>
  mutate(time = paste0(time, " ", time_zone),
         date = as.numeric(as.POSIXct(time, format="%Y-%m-%d %H:%M:%OS")),
         resp = case_when(outcome == 'CORRECT' ~ 1,
                          outcome == 'INCORRECT' | outcome == 'HINT' ~ 0),
         problem_name = paste0(problem_name, step_name)) |>
  rename(rt = duration_sec) |>
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
save(df, file="chemistry_tutor.Rdata")
