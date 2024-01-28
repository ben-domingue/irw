library(tidyverse)
library(readr)
library(janitor)

df <- read_delim('PACT Geom Angles Data F98.txt')

df <- df |>
  clean_names(case = 'snake') |>
  select(student,
         problem,
         success,
         time) |>
  rename(rt = time,
         resp = success) |>
  drop_na()

items <- as.data.frame(unique(df$problem))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$student))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("problem" = "unique(df$problem)")) |>
  left_join(ids, by=c('student' = "unique(df$student)")) |>
  # drop character item variable
  select(id, item_id, resp, rt) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="geometry_course.Rdata")

