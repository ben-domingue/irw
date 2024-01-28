library(tidyverse)
library(readr)

df <- read_csv('junyi_ProblemLog_original.csv')

df <- df |>
  # sort df by user, problem number, and problem step
  arrange(user_id, problem_number, time_done) |>
  # keep only first-attempt observations
  filter(count_attempts == 1) |>
  # keep only relevant variables
  select(user_id,
         problem_number,
         exercise,
         time_done,
         time_taken,
         correct) |>
  # recode respond variable to be 0/1 binary
  mutate(resp = case_when(correct == 'TRUE' ~ 1,
                          correct == 'FALSE' ~ 0),
         # recode user_id to have all IDs be positive numbers above 0
         user_id = user_id + 1,
         # create unique items for each problem_id x exercise combination
         item = paste0(problem_number, exercise)) |>
  # rename relevant variables according to IRW standards
  rename(date = time_done,
         rt = time_taken,
         id = user_id)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())


df <- df |>
  left_join(items, by=c('item' = "unique(df$item)")) |>
  # drop character item variable
  select(id, date, item_id, resp, rt) |>
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="junyi_academy_problems.Rdata")
