library(tidyverse)
df <-read.csv("FINAL Data - FY 2018-2020_Excluding PII.xlsx - FINAL Data - FY 2018-2020.csv")
names(df) <- tolower(names(df))
df <- df[,-c(2:11)]
df <- df |>
  select(-daterange) |>
  pivot_longer(cols = -responseid,
               names_to = 'item',
               values_to = 'resp')
## 2026-09-08 (#2029): the last three columns of the source spreadsheet are
## empty, so items 54-56 shipped as 26,347 rows of NA each -- against ~14% NA
## for items 49-53. Nothing was destroyed here; they should simply never have
## been published. Drop any item with no response at all before the ids are
## assigned. They are the final three columns, so items 1-53 keep their
## existing numbering and the published table stays comparable.
informative <- df |>
  group_by(item) |>
  summarise(n_resp = sum(!is.na(resp)), .groups = 'drop') |>
  filter(n_resp > 0) |>
  pull(item)
df <- df |> filter(item %in% informative)
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
