library(tidyverse)
library(readr)

df <- read_csv('dissertation data.csv')

df <- df |>
  clean_names(case = 'snake') |>
  select(student,
         problem,
         correct) |>
  rename(resp = correct)

# create item IDs for each survey item
items <- as.data.frame(unique(df$problem))
items <- items |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$student))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("problem" = "unique(df$problem)")) |>
  left_join(ids, by=c('student' = "unique(df$student)"))  |>
  # drop character item variable
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="blocked_interleaved_instruction.Rdata")
