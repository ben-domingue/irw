library(tidyverse)
library(readr)

df <- read_csv("DieGuessingTask_Raw.csv")

df <- df |>
  select(subject,
         trial,
         iscorrect_self) |>
  rename(resp = iscorrect_self,
         item = trial)


ids <- as.data.frame(unique(df$subject))
ids <- ids |>
  arrange(unique(df$subject)) |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(ids, by=c('subject' = "unique(df$subject)"))|>
  # drop character item variable
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="differences_spotting_study3_die.Rdata")
