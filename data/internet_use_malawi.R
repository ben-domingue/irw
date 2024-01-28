library(tidyverse)
library(readr)
library(janitor)

df <- read_csv('Internet_Addiction_Malawi_Data.csv')

df <- df |>
  clean_names(case = 'snake') |>
  select(sn,
         starts_with('to_assess_your'),
         starts_with('in_the_last')) |>
  mutate(across(starts_with('to_assess_your'), ~case_when(. == '1=Rarely' ~ 1,
                                                          . == '2=Occasionally' ~ 2,
                                                          . == '3=Frequently' ~ 3,
                                                          . == '4=Often' ~ 4,
                                                          . == '5=Always' ~ 5,
                                                          . == '0=Does not Apply' | . == '99=Missing' ~ NA)),
         across(starts_with('in_the_last'), ~case_when(. == '1' ~ 1,
                                                       . == 'No' ~ 0))) |>
  rename(id = sn) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)
  
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
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="internet_use_malawi.Rdata")