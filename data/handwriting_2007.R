library(tidyverse)
library(readxl)

df <- read_excel("hw-spr2007-paper-tests-detailed.xls", 
                 sheet = "ROWS")

names(df) <- tolower(names(df))

df <- df |>
  mutate(wave = case_when(`test (pre/post/ret)` == 'Post' ~ 1,
                          `test (pre/post/ret)` == 'Pre' ~ 0,
                          `test (pre/post/ret)` == 'Retention' ~ 3),
         treatment = case_when(condition == 'CogTutor(1)' ~ 'control',
                               condition == 'CTEx(2)' ~ 'control + examples',
                               condition == 'CTExNoFB(3)' ~ 'control + examples + feedback',
                               condition == 'HW(4)' ~ 'treatment')) |>
  select(id,
         treatment,
         wave,
         `item #`,
         score) |>
  rename(item = `item #`,
         resp = score)

# --- second dataset on mental outcomes ---

mental <- read_excel("hw-spr2007-mental-effort-results.xls", 
                     sheet = "ROWS", skip = 13)

names(mental) <- tolower(names(mental))

mental <- mental |>
  mutate(wave = as.numeric(NA),
         treatment = '') |>
  select(`anon id`,
         treatment,
         wave,
         `how much mental effort`,
         `mental effort compared to normal`,
         `source of mental effort`) |>
  pivot_longer(cols = -c(`anon id`, wave, treatment),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(item = case_when(item == "how much mental effort" ~ 11,
                          item == "mental effort compared to normal" ~ 12,
                          item == "source of mental effort" ~ 13)) |>
  rename(id = `anon id`)

# ---- combine datasets ---

df <- rbind(df, mental)

ids <- as.data.frame(unique(df$id))
ids <- ids |>
  mutate(id_num = row_number())

df <- df |>
  # merge IDs with df
  left_join(ids, by=c('id' = "unique(df$id)"))  |>
  mutate(person_id = id_num,
         id_num = paste0(person_id, '_', wave)) |>
  # drop character item variable
  select(person_id, id_num, treatment, wave, item, resp) |>
  rename(id = id_num) |>
  # use item_id column as the item column
  arrange(person_id, item, wave) |>
  mutate(id = if_else(str_ends(id, '_NA'), str_replace(id, '_NA', ''), id))

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="handwriting_2007.Rdata")
