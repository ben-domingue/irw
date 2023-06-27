library(tidyverse)
library(readr)
library(janitor)

late <- read_csv('late.csv')
early <- read_csv('early.csv')
df <- rbind(late, early)

df <- df |>
  clean_names(case = 'snake') |>
  select(subject_id, problem_id, correct_eventually) |>
  mutate(resp = case_when(correct_eventually == 'TRUE' ~ 1,
                          correct_eventually == 'FALSE' ~ 0))


# create item IDs for each survey item
items <- as.data.frame(unique(df$problem_id))
items <- items |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$subject_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("problem_id" = "unique(df$problem_id)")) |>
  left_join(ids, by=c('subject_id' = "unique(df$subject_id)")) |>
  # drop character item variable
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="csedm_data_challenge_fall2019full.Rdata")

