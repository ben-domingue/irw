library(tidyverse)
library(readxl)

df <- read_excel("exp1 - UCLA-Kentucky/combined ucla.xlsx")


names(df) <- tolower(names(df))

df <- df |>
  select(studentid, 
         currenttrialstarttime,
         ends_with('correct')) |>
  rowwise() |>
  separate_wider_delim(currenttrialstarttime, delim = " ", names=c('weekday', 'month', 'day', 'time', 'year', 'timezone')) |>
  mutate(month = as.numeric(9),
         date_utc = paste0(year, '-', month, '-', day, ' ', time, ' ', timezone),
         date = as.numeric(as.POSIXct(date_utc, format="%Y-%m-%d %H:%M:%OS"))) |>
  select(studentid,
         ends_with('correct'),
         date) |>
  pivot_longer(cols = -c(studentid, date),
               names_to = 'item',
               values_to = 'resp') |>
  mutate(period = case_when(str_detect(item, 'pre') ~ 'pre',
                            str_detect(item, 'post') ~ 'post'),
         item = str_remove_all(item, 'pre'),
         item = str_remove_all(item, 'post'))

items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$studentid))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('studentid' = "unique(df$studentid)")) |>
  # drop character item variable
  select(id, date, period, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item, date)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="digital_games_kentucky.Rdata")

