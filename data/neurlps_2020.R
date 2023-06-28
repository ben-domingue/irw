library(tidyverse)
library(readr)
library(janitor)

test1_private <- read_csv('test_private_answers_task_1.csv')
test1_public <- read_csv('test_public_answers_task_1.csv')
test2_public <- read_csv('test_public_answers_task_2.csv')
test2_public <- test2_public |> rename(IsCorrect = AnswerValue)
test2_private <- read_csv('test_private_answers_task_2.csv')
test2_private <- test2_private |> rename(IsCorrect = AnswerValue)
test4_public <- read_csv('test_public_task_4_more_splits.csv')
test4_public <- test4_public |> select(QuestionId, UserId, AnswerId, IsCorrect)
test4_private <- read_csv('test_private_task_4.csv')
test4_private <- test4_private |> select(-CorrectAnswer, -AnswerValue, -IsTarget)
train1 <- read_csv('train_task_1_2.csv')
train1 <- train1 |> select(-CorrectAnswer, -AnswerValue)
train2 <- read_csv('train_task_3_4.csv')
train2 <- train2 |> select(-CorrectAnswer, -AnswerValue)

df <- rbind(test1_private, test1_public, test2_private, test2_public, test4_private, test4_public, train1, train2)

df <- df |>
  clean_names(case = 'snake') |>
  mutate(count = 1) |>
  group_by(question_id, user_id, answer_id, is_correct) |>
  summarize(count = sum(count)) |>
  ungroup() |>
  filter(count == 1) |>
  select(-count, -answer_id) |>
  mutate(user_id = user_id + 1,
         question_id = question_id + 1) |>
  rename(id = user_id,
         item = question_id,
         resp = is_correct)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="neurlps_2020.Rdata")

