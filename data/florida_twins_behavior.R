library(tidyverse)
library(readr)

df <- read_csv('multiparentandchild0311 LDBase.csv')

names(df) <- tolower(names(df))
co
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
         -`...1`,
         -id1,
         -id0,
         -contains('swan'),
         -twinid,
         -starts_with('n')) %>%
  rename()


df0 <- df %>%
  select(bg_id0, ends_with("0")) %>%
  rename(id = bg_id0) %>%
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)


df1 <- df %>%
  select(bg_id1, ends_with("1")) %>%
  rename(id = bg_id1) %>%
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)

df_ <- bind_rows(df0, df1)

df_$item <- substring(df_$item, 1, nchar(df_$item) - 1)

df_ <- df_[!(grepl("^n", df_$item) & !grepl("^nes", df_$item)),]

unique(df_$item)

# print response values
table(df_$resp)

df_panas <- df_ %>%
  filter(grepl("panas", item))

df_ecs <- df_ %>%
  filter(grepl("ecs", item))

df_rcads <- df_ %>%
  filter(grepl("rcads", item))

df_cads <- df_ %>%
  filter(grepl("^cads_", item))

df_tas <- df_ %>%
  filter(grepl("tas", item))

df_friends <- df_ %>%
  filter(grepl("friends", item))

df_cadsyv <- df_ %>%
  filter(grepl("^cadsyv", item))

length(unique(df_panas$item))
length(unique(df_ecs$item))
length(unique(df_rcads$item))
length(unique(df_cads$item))
length(unique(df_tas$item))
length(unique(df_friends$item))
length(unique(df_cadsyv$item))

write.csv(df_panas, "florida_twins_behavior_panas.csv", row.names=FALSE)
write.csv(df_ecs, "florida_twins_behavior_ecs.csv", row.names=FALSE)
write.csv(df_rcads, "florida_twins_behavior_rcads.csv", row.names=FALSE)
write.csv(df_cads, "florida_twins_behavior_cads.csv", row.names=FALSE)
write.csv(df_tas, "florida_twins_behavior_tas.csv", row.names=FALSE)
write.csv(df_friends, "florida_twins_behavior_friends.csv", row.names=FALSE)
write.csv(df_cadsyv, "florida_twins_behavior_cadsyv.csv", row.names=FALSE)

# # save df to Rdata file
# save(df, file="florida_twins_behavior.Rdata")