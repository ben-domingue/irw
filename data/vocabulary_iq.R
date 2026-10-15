## Vocabulary IQ Test (openpsychometrics.org, VIQT_data.zip). The source file holds
## two instruments side by side: the 45 five-word synonym questions (Q1-Q45, scored
## 0/1 against the codebook key) and the optional 30-item post-test personality
## survey (S1-S30, 1-5 agreement). Until 2026-10 both were one table, which no
## per-table metadata could describe (n_categories was 2 and 6 at once, #3032).
## This script now writes two tables:
##   vocabulary_iq         items 1-45  = Q1-Q45, resp 0/1
##   vocabulary_iq_survey  items 1-30  = S1-S30, resp 1-5
## `id` is the source row number in both, so the two tables join on id.
library(tidyverse)
library(readr)

df <- read_delim('VIQT_data.csv')

# convert column names to lowercase
names(df) <- tolower(names(df))

df <- df |>
  # drop unneeded columns
  select(-score_right,
         -score_wrong,
         -score_full,
         -country,
         -introelapse,
         -testelapse,
         -education,
         -urban,
         -gender,
         -engnat,
         -age) |>
  # create participant ID
  mutate(id = row_number())

# create separate df for response times to merge onto items later
times <- df |>
  # select only time variables
  select(id, 
         starts_with('e')) |>
  # pivot long by ID
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'rt') |>
  # match item ID to that of other dataset
  mutate(item = str_replace(item, 'e', 'q'),
         # convert response time to seconds from milliseconds
         rt = rt / 1000)

df <- df |>
  # drop response time variables
  select(-starts_with('e')) |>
  # replace invalid responses with NA
  mutate_all(~ replace(., . == -1, NA)) |>
  mutate(across(starts_with('s'), ~if_else(. == 0, NA, .))) |>
  # On the vocabulary questions the codebook separates -1 ("subject selected
  # 'don't know'", handled above) from 0 ("subject did not respond to question
  # at all"). Neither is an answer: the source's own score_wrong excludes 0 on
  # every row, so an unanswered question is missing, not wrong (issue #2513).
  mutate(across(starts_with('q'), ~if_else(. == 0, NA, .))) |>
  # pivot df long by item
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp') |>
  # recode responses so that correct answers == 1 and incorrect answers == 0
  mutate(resp2 = case_when((item == 'q1' & resp == 24) | 
                             (item == 'q2' & resp == 3) | 
                             (item == 'q3' & resp == 10) | 
                             (item == 'q4' & resp == 5) | 
                             (item == 'q5' & resp == 9) | 
                             (item == 'q6' & resp == 9) |
                             (item == 'q7' & resp == 17) |
                             (item == 'q8' & resp == 10) |
                             (item == 'q9' & resp == 17) |
                             (item == 'q10' & resp == 10) |
                             (item == 'q11' & resp == 5) |
                             (item == 'q12' & resp == 17) |
                             (item == 'q13' & resp == 9) |
                             (item == 'q14' & resp == 5) |
                             (item == 'q15' & resp == 18) |
                             (item == 'q16' & resp == 18 ) |
                             (item == 'q17' & resp == 3) |
                             (item == 'q18' & resp == 12) |
                             (item == 'q19' & resp == 18) |
                             (item == 'q20' & resp == 18) |
                             (item == 'q21' & resp == 3) |
                             (item == 'q22' & resp == 18) |
                             (item == 'q23' & resp == 6) |
                             (item == 'q24' & resp == 12) |
                             (item == 'q25' & resp == 17) |
                             (item == 'q26' & resp == 10) |
                             (item == 'q27' & resp == 10) |
                             (item == 'q28' & resp == 9) |
                             (item == 'q29' & resp == 9) |
                             (item == 'q30' & resp == 3) |
                             (item == 'q31' & resp == 6) |
                             (item == 'q32' & resp == 10) |
                             (item == 'q33' & resp == 17) |
                             (item == 'q34' & resp == 3) |
                             (item == 'q35' & resp == 17) |
                             (item == 'q36' & resp == 24) |
                             (item == 'q37' & resp == 17) |
                             (item == 'q38' & resp == 5) |
                             (item == 'q39' & resp == 5) |
                             (item == 'q40' & resp == 24) |
                             (item == 'q41' & resp == 5) |
                             (item == 'q42' & resp == 5) |
                             (item == 'q43' & resp == 12) |
                             (item == 'q44' & resp == 10) |
                             (item == 'q45' & resp == 9) ~ 1),
         # The answer key above covers only the 45 vocabulary questions (q1-q45).
         # s1-s30 are the optional post-test personality survey, answered on a
         # 1-5 agreement scale -- they are not vocabulary questions and must not
         # be scored against the key, so their raw response passes through
         # unchanged (issue #1877). A resp scale may differ across items.
         resp2 = case_when(!str_starts(item, 'q') ~ resp,
                           is.na(resp2) ~ 0,
                           .default = resp2),
         # items without responses remain NA
         resp2 = if_else(is.na(resp), NA, resp2)) |>
  # drop original response variable
  select(-resp) |>
  # response2 become response variable
  rename(resp = resp2)
  
# Item codes are positional: q1-q45 -> 1-45 in the test table, s1-s30 -> 1-30 in
# the survey table. The test keeps the numbering it has always had.
df <- df |>
  mutate(block = if_else(str_starts(item, 'q'), 'test', 'survey'),
         item = as.integer(str_sub(item, 2)))

test <- df |> filter(block == 'test') |> select(id, item, resp)
survey <- df |> filter(block == 'survey') |> select(id, item, resp)
stopifnot(nrow(test) == 12173 * 45, nrow(survey) == 12173 * 30,
          all(na.omit(test$resp) %in% 0:1), all(na.omit(survey$resp) %in% 1:5))

# print response values
table(test$resp)
table(survey$resp)

df <- test
save(df, file="vocabulary_iq.Rdata")
write_csv(test, "vocabulary_iq.csv", na = "")
df <- survey
save(df, file="vocabulary_iq_survey.Rdata")
write_csv(survey, "vocabulary_iq_survey.csv", na = "")
