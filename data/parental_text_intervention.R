library(tidyverse)
library(haven)
library(labelled)

df <- read_stata('g1g2_summertext_public.dta')

df <- df |>
  select(s_moreresearchid,
         starts_with('s_ss_')) |>
  mutate(s_ss_physicalint_book7g = if_else(s_ss_physicalint_book7g == 2.5, NA, s_ss_physicalint_book7g),
         s_ss_physicalint_book7d = if_else(s_ss_physicalint_book7d == 2.5 | s_ss_physicalint_book7d == 1.5, NA, s_ss_physicalint_book7d),
         s_ss_physicalint_book7c = if_else(s_ss_physicalint_book7c == 2.5, NA, s_ss_physicalint_book7c),
         s_ss_physicalint_book7b = if_else(s_ss_physicalint_book7b == 1.5, NA, s_ss_physicalint_book7b),
         s_ss_digitalint_book5e = if_else(s_ss_digitalint_book5e == 1.5 | s_ss_digitalint_book5e == 2.5, NA, s_ss_digitalint_book5e),
         s_ss_digitalint_book5c = if_else(s_ss_digitalint_book5c == 1.5, NA, s_ss_digitalint_book5c),
         across(starts_with('s_ss_digitalint_book5'), ~. + 1),
         across(starts_with('s_ss_physicalint_book7'), ~. + 1)) |>
  pivot_longer(cols = -s_moreresearchid,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$s_moreresearchid))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('s_moreresearchid' = "unique(df$s_moreresearchid)")) |>
  # drop character item variable
  select(id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item)

# remove label from resp
df$resp <- remove_labels(df$resp)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="parental_text_intervention.Rdata")
