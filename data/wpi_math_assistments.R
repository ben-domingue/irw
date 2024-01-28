library(tidyverse)
library(readr)
library(janitor)

df <- read_delim('dataframe3_aggr.txt.output.txt')

df <- df |>
  clean_names(case = 'snake') |>
  select(student_id,
         itemid,
         correctonfirstattempt,
         seconds,
         full_start_time) |>
  separate_wider_delim(full_start_time, delim = "-", names=c('day', 'month', 'year')) |>
  mutate(month = case_when(month == 'JAN' ~ '01',
                           month == 'FEB' ~ '02',
                           month == 'MAR' ~ '03',
                           month == 'APR' ~ '04',
                           month == 'MAY' ~ '05',
                           month == 'JUN' ~ '06',
                           month == 'JUL' ~ '07',
                           month == 'AUG' ~ '08',
                           month == 'SEP' ~ '09',
                           month == 'OCT' ~ '10',
                           month == 'NOV' ~ '11',
                           month == 'DEC' ~ '01'),
         year = paste0("20", year),
         year = str_replace(year, 'AM', 'ET'),
         full_start_time = paste0(month,'-', day,'-', year),
         date = as.numeric(as.POSIXct(full_start_time, format="%m-%d-%Y %H.%M.%OS"))) |>
  select(-full_start_time,
         -day,
         -month,
         -year) |>
  rename(rt = seconds,
         resp = correctonfirstattempt)

# create item IDs for each survey item
items <- as.data.frame(unique(df$itemid))
items <- items |>
  mutate(item = row_number())

ids <- as.data.frame(unique(df$student_id))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("itemid" = "unique(df$itemid)")) |>
  left_join(ids, by=c('student_id' = "unique(df$student_id)")) |>
  # drop character item variable
  select(id, date, item, resp, rt) |>
  # use item_id column as the item column
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="wpi_math_assistments.Rdata")
