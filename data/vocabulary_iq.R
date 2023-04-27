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
         resp2 = if_else(is.na(resp2), 0, resp2),
         # items without responses remain NA
         resp2 = if_else(is.na(resp), NA, resp2)) |>
  # drop original response variable
  select(-resp) |>
  # response2 become response variable
  rename(resp = resp2)
  
# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="vocabulary_iq.Rdata")

