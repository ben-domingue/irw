library(tidyverse)
df <-read.csv("FINAL Data - FY 2018-2020_Excluding PII.xlsx - FINAL Data - FY 2018-2020.csv")
names(df) <- tolower(names(df))
df <- df[,-c(2:11)]
df <- df |>
  select(-daterange) |>
  pivot_longer(cols = -responseid,
               names_to = 'item',
               values_to = 'resp')
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())
df <- df |>
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  select(responseid, item_id, resp) |>
  rename(item = item_id)
df <- df %>%
  filter(!resp %in% c(0, 8))
save(df, file="Veterans Affairs SSVF Survey 2018-20.Rdata")
write.csv(df, file="Veterans Affairs SSVF Survey 2018-20.csv",row.names= FALSE)
