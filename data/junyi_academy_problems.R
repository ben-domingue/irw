library(tidyverse)
library(readr)
library(janitor)

df <- read_csv('junyi_ProblemLog_original.csv')

df <- df |>
  clean_names(case = 'snake') |>
  filter(count_attempts == 1) |>
  select(user_id,
         problem_number,
         time_done,
         time_taken,
         correct) |>
  mutate(resp = case_when(correct == 'TRUE' ~ 1,
                          correct == 'FALSE' ~ 0)) |>
  rename(date = time_done,
         rt = time_taken) 

ids <- as.data.frame(unique(df$user_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  left_join(ids, by=c('user_id' = "unique(df$user_id)")) |>
  # drop character item variable
  select(id, date, item_id, resp, rt) |>
  arrange(id, item, date)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="junyi_academy_problems.Rdata")
