library(tidyverse)
library(readr)
library(janitor)

df <- read_delim("All_Data_1826_2013_0408_075715_forReimport.txt")

df <- df |>
  clean_names(case = 'snake') |>
  select(anon_student_id,
         cf_server_adjusted_event_time,
         problem_name,
         duration_sec,
         outcome) |>
  mutate(date = as.numeric(as.POSIXct(cf_server_adjusted_event_time, format="%Y/%m/%d %H:%M:%OS")),
         resp = case_when(outcome == 'Correct' ~ 1,
                          outcome == 'InCorrect' | outcome == 'Hint' | outcome == 'HINT' ~ 0)) |>
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
save(df, file="fractions_experiment.Rdata")