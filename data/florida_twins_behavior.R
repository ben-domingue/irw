library(tidyverse)
library(readr)

df <- read_csv('multiparentandchild0311 LDBase.csv')

names(df) <- tolower(names(df))

df <- df |>
  select(-starts_with('panas_pa'),
         -starts_with('panas_na'),
         -starts_with('ecs_ec'),
         -starts_with('ecs_imp'),
         -starts_with('rcads_mdd'),
         -starts_with('rcads_ocd'),
         -starts_with('rcads_gad'),
         -starts_with('rcads_pda'),
         -starts_with('rcads_sad'),
         -starts_with('rcads_sp'),
         -starts_with('cadsyv_pos'),
         -starts_with('cadsyv_dar'),
         -starts_with('cadsyv_pro'),
         -starts_with('cadsyv_neg'),
         -starts_with('cadsyv_soc'),
         -starts_with('cadsyv_resp'),
         -starts_with('cadsyv_dis'),
         -starts_with('tas_autonomic'),
         -starts_with('tas_offtask'),
         -starts_with('tas_thoughts'),
         -starts_with('friends_bad'),
         -starts_with('friends_school'),
         -starts_with('friends_good'),
         -contains('hem'),
         -contains('chaos'),
         -starts_with('p_'),
         -starts_with('p_panas'),
         -contains('pdbd'),
         -contains('feeling'),
         -pair_gender,
         -zyg_par,
         -starts_with('bg_id'),
         -`...1`,
         -starts_with('id'),
         -contains('swan'),
         -twinid) |>
  mutate(id = row_number()) |>
  pivot_longer(cols = -c(id, famid),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  rename(family_id = famid)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())


df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, family_id, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="florida_twins_behavior.Rdata")
