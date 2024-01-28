library(tidyverse)
library(haven)
library(labelled)

df <- read_stata('g1g2_analyticfile_public.dta')

df <- df |>
  select(s_id,
         s_itt_consented,
         starts_with('s_mmrp'),
         starts_with('s_sci'),
         starts_with('s_ss')) |>
  select(-contains('taught'),
         -contains('total'),
         -ends_with('_r1'),
         -ends_with('_r2'),
         -ends_with('response'),
         -ends_with('std'),
         -ends_with('write'),
         -ends_with('end'),
         -ends_with('evid'),
         -ends_with('claim'),
         -s_mmrp) |>
  mutate(across(starts_with('s_mmrp'), ~if_else(. == 1.5 | . == 2.5, NA, .))) |>
  pivot_longer(cols = -c(s_id, s_itt_consented),
               names_to = 'item',
               values_to = 'resp')

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$s_id))
ids <- ids |>
  arrange(unique(df$s_id)) |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('s_id' = "unique(df$s_id)")) |>
  # drop character item variable
  select(id, s_itt_consented, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id,
         treatment = s_itt_consented) |>
  arrange(id, item) |>
  drop_na()

# remove label from resp
df$resp <- remove_labels(df$resp)
df$treatment <- remove_labels(df$treatment)


# print response values
table(df$resp)

# save df to Rdata file
save(df, file="content_literacy_interention_g1.Rdata")

