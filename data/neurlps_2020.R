library(dplyr)
library(readr)
library(janitor)

## Eedi / NeurIPS 2020 Education Challenge.
## Source: https://eedi.com/research#data ->
##   https://dqanonymousdata.blob.core.windows.net/neurips-public/data.zip
## Guide: Wang et al. (2020), arXiv:2007.12061.
##
## This script writes TWO tables, and that is deliberate (see ben-domingue/irw#1875).
##
## (1) The challenge released task 1/2 and task 3/4 as separately anonymised
##     datasets. Guide p.8: "IMPORTANT: Question, User and Answer IDs should not
##     be linked between the data for these pairs of tasks!" The ID spaces really
##     do collide -- all 948 task-3/4 QuestionIds, all 6,148 UserIds and all
##     1,508,917 AnswerIds also occur in the task-1/2 files, meaning something
##     different each time. An earlier version of this script rbind'ed the two and
##     set item = question_id + 1, so item codes 1-948 each pooled two different
##     questions and the respondents behind id 1-6148 were merged as well.
##     They are kept apart here as neurips_2020 and neurips_2020_task34.
##
## (2) test_public_answers_task_2.csv / test_private_answers_task_2.csv are the
##     SAME answers as their task_1 counterparts -- identical (QuestionId, UserId,
##     AnswerId) in identical order -- carrying the option the student chose
##     (AnswerValue, 1-4) instead of whether they were right (IsCorrect, 0/1),
##     because task 2 asks entrants to predict the choice rather than the outcome.
##     The earlier version renamed AnswerValue to IsCorrect and rbind'ed them, so
##     resp mixed correctness with option identity across {0,1,2,3,4}, and a
##     dedup step then silently deleted BOTH copies of the 616,871 answers whose
##     chosen option happened to equal the IsCorrect flag. They are not read here:
##     they carry no response the task_1 files do not already carry.

read_answers <- function(file) {
  read_csv(file, show_col_types = FALSE) |>
    select(QuestionId, UserId, AnswerId, IsCorrect)
}

## ---- task 1/2 -------------------------------------------------------------
t12 <- bind_rows(
  read_answers('train_task_1_2.csv'),
  read_answers('test_public_answers_task_1.csv'),
  read_answers('test_private_answers_task_1.csv')
)

## ---- task 3/4 -------------------------------------------------------------
## test_private_task_4_more_splits.csv is the same 51,299 answers as
## test_private_task_4.csv with alternative target flags, so it is not read.
t34 <- bind_rows(
  read_answers('train_task_3_4.csv'),
  read_answers('test_private_task_4.csv'),
  read_answers('test_public_task_4_more_splits.csv')
)

to_irw <- function(df) {
  ## AnswerId is unique within a task pair, so the train/test files partition the
  ## responses rather than overlapping; assert it instead of dedup'ing blind.
  stopifnot(!any(duplicated(df$AnswerId)))
  out <- df |>
    clean_names(case = 'snake') |>
    mutate(id = user_id + 1,
           item = question_id + 1,
           resp = is_correct) |>
    select(id, item, resp)
  stopifnot(!any(duplicated(out[, c('id', 'item')])),
            all(out$resp %in% c(0, 1)))
  out
}

neurips_2020 <- to_irw(t12)
neurips_2020_task34 <- to_irw(t34)

## task 1/2: 19,834,813 responses, 27,613 items, 118,971 respondents
## task 3/4:  1,508,917 responses,    948 items,   6,148 respondents
for (nm in c('neurips_2020', 'neurips_2020_task34')) {
  x <- get(nm)
  cat(sprintf("%-20s %10d responses %7d items %8d ids  resp: %s\n",
              nm, nrow(x), n_distinct(x$item), n_distinct(x$id),
              paste(sort(unique(x$resp)), collapse = ",")))
}

write_csv(neurips_2020, "neurips_2020.csv")
write_csv(neurips_2020_task34, "neurips_2020_task34.csv")
