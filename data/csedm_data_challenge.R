library(tidyverse)
library(readr)
library(janitor)

train0 <- read_csv("CV/Fold0/Training.csv")
train1 <- read_csv("CV/Fold1/Training.csv")
train2 <- read_csv("CV/Fold2/Training.csv")
train3 <- read_csv("CV/Fold3/Training.csv")
train4 <- read_csv("CV/Fold4/Training.csv")
train5 <- read_csv("CV/Fold5/Training.csv")
train6 <- read_csv("CV/Fold6/Training.csv")
train7 <- read_csv("CV/Fold7/Training.csv")
train8 <- read_csv("CV/Fold8/Training.csv")
test0 <- read_csv("CV/Fold0/Test.csv")
test1 <- read_csv("CV/Fold1/Test.csv")
test2 <- read_csv("CV/Fold2/Test.csv")
test3 <- read_csv("CV/Fold3/Test.csv")
test4 <- read_csv("CV/Fold4/Test.csv")
test5 <- read_csv("CV/Fold5/Test.csv")
test6 <- read_csv("CV/Fold6/Test.csv")
test7 <- read_csv("CV/Fold7/Test.csv")
test8 <- read_csv("CV/Fold8/Test.csv")

df <- rbind(train0, train1, train2, train3, train4, train5, train6, train7, train8,
            test0, test1, test2, test3, test4, test5, test6, test7, test8)

names(df) <- tolower(names(df))

df <- df |>
  arrange(subjectid, problemid, startorder, firstcorrect, evercorrect, usedhint, attempts) |>
  group_by(subjectid, problemid, startorder, firstcorrect, evercorrect, usedhint, attempts) |>
  mutate(dup = row_number()) |>
  filter(dup == 1) |>
  mutate(resp = case_when(firstcorrect == 'TRUE' ~ 1,
                   firstcorrect == 'FALSE' ~ 0)) |>
  ungroup()

# create item IDs for each survey item
items <- as.data.frame(unique(df$problemid))
items <- items |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$subjectid))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("problemid" = "unique(df$problemid)")) |>
  left_join(ids, by=c('subjectid' = "unique(df$subjectid)")) |>
  # drop character item variable
  select(id, item, resp) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="csedm_data_challenge.Rdata")