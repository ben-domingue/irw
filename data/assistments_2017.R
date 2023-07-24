library(tidyverse)
library(readr)
library(janitor)

df <- read_csv('anonymized_full_release_competition_dataset.csv')

df <- df |>
  clean_names(case = 'snake') |>
  select(student_id,
         start_time,
         problem_id,
         time_taken,
         correct) |>
  rename(resp = correct,
         rt = time_taken,
         date = start_time,
         item = problem_id)


# create unique IDs for each user
ids <- as.data.frame(unique(df$student_id))
ids <- ids |>
  arrange(unique(df$student_id)) |>
  mutate(id = row_number())

df <- df |>
  # merge user IDs with df
  left_join(ids, 
            by=c("student_id" = "unique(df$student_id)")) |>  
  # keep only relevant variables
  select(id, item, date, resp, rt) |>
  # sort df by user ID then item ID
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="assistments_2017.Rdata")
