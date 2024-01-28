library(tidyverse)
library(readxl)

df <- read_xls('hw-dec2006-paper-tests-detailed.xls', sheet = 2, col_names = T)

names(df) <- tolower(names(df))


df <- df |>
  mutate(treatment = case_when(condition == 'control' ~ 0,
                               condition == 'treatment' ~ 1),
         wave = case_when(`test (pre/post)` == 'Post' ~ 1,
                          `test (pre/post)` == 'Pre' ~ 0)) |>
  select(id,
         treatment,
         wave,
         `item #`,
         score) |>
  rename(item = `item #`,
         resp = score)


ids <- as.data.frame(unique(df$id))
ids <- ids |>
  mutate(id_num = row_number())

df <- df |>
  # merge IDs with df
  left_join(ids, by=c('id' = "unique(df$id)"))  |>
  mutate(person_id = id_num,
         id_num = paste0(person_id, '_', wave)) |>
  # drop character item variable
  select(person_id, id_num, wave, item, resp) |>
  rename(id = id_num) |>
  # use item_id column as the item column
  arrange(person_id, item, wave)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="handwriting_2006.Rdata")
