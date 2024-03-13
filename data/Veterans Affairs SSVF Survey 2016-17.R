library(tidyverse)
df <-read.csv("FINAL Data - FY 2016-2017_Excluding PII.xlsx - FINAL Data - FY 2016-2017.csv")
names(df) <- tolower(names(df))
df <- df[,-c(2:29)]
df <- df |>
  select(-negative,
         -date.range,
         -f37,
         -q7,
         -q8.4.a_6_text,
         -q8.4.b_6_text,
         -q8.4.c_6_text) |>
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
save(df, file="Veterans Affairs SSVF Survey 2016-17.Rdata")
write.csv(df, file="Veterans Affairs SSVF Survey 2016-17.csv",row.names= FALSE)
