library(tidyverse)
library(haven)
library(labelled)

df <- read_sav('R305A180293_child-level_CT_v33.sav')

names(df) <- tolower(names(df))

df <- df |>
  select(contains('ss1'),
         contains('ss2'),
         contains('ss3'),
         contains('ss4'),
         contains('ss5'),
         contains('ss6'),
         contains('ss7'),
         contains('ss8'),
         contains('ss9'),
         contains('ss10'),
         contains('as1'),
         contains('as2'),
         contains('as3'),
         contains('as4'),
         contains('as5'),
         contains('as6'),
         contains('as7'),
         contains('as8'),
         contains('as9'),
         contains('as10'),
         starts_with('wj_lw'),
         starts_with('wj_ap'),
         starts_with('dn_1'),
         starts_with('dn_2'),
         starts_with('dn_3'),
         starts_with('dn_4'),
         starts_with('dn_5'),
         starts_with('dn_6'),
         starts_with('dn_7'),
         starts_with('dn_8'),
         starts_with('dn_9'),
         contains('_1s_'),
         contains('_2s_'),
         contains('_3s_'),
         contains('_4s_'),
         contains('_5s_'),
         contains('_6s_'),
         starts_with('box1'),
         starts_with('box2'),
         starts_with('htks1_1'),
         starts_with('htks1_2'),
         starts_with('htks1_3'),
         starts_with('htks1_4'),
         starts_with('htks1_5'),
         starts_with('htks1_6'),
         starts_with('htks1_7'),
         starts_with('htks1_8'),
         starts_with('htks1_9')) |> 
  select(-starts_with('emt1'),
         -starts_with('emt2'),
         -starts_with('emt3'),
         -starts_with('emt4'),
         -ends_with('hapb'),
         -ends_with('sadb'),
         -ends_with('angb'),
         -ends_with('afrb'),
         -ends_with('hapa'),
         -ends_with('sada'),
         -ends_with('anga'),
         -ends_with('afra'),
         -wj_lww_t1,
         -wj_lwss_t1,
         -wj_apw_t1,
         -wj_apss_t1,
         -contains('notes')) |>
  # replace invalid values with NA, change others to 0/1 wrong/right binary
  mutate(across(starts_with('dn'), ~if_else(. == 1, NA, .)),
         across(starts_with('dn'), ~if_else(. == 2, 1, .)),
         across(contains('_1s_') | contains('_2s_') | contains('_3s_') | contains('_4s_') | contains('_5s_') | contains('_6s_'), 
                ~if_else(. == 1, 0, .)),
         across(contains('_1s_') | contains('_2s_') | contains('_3s_') | contains('_4s_') | contains('_5s_') | contains('_6s_'), 
                ~if_else(. == 2, 1, .)),
         across(starts_with('htks'), ~if_else(. == 1, 0, .)),
         across(starts_with('htks'), ~if_else(. == 2, 1, .)),
         across(starts_with('box'), ~if_else(. == 0.5, NA, .)),
         # create participant ID
         id = row_number())

# find variables with no response or single responses to drop
# put them in a list to drop
drop_vars <- c()

for (i in 1:ncol(df)) {
  unique_vals <- unique(df[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(df)[i])
  }
  
  if (unique_len == 2) {
    if (is.na(unique_vals[1]) | is.na(unique_vals[2])) {
      drop_vars <- append(drop_vars, names(df)[i])
    }
  }
}

# drop variables with no responses or singular resposes
df <- df |>
  select(-all_of(drop_vars)) |>
  # pivot df to be long by item
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

# remove obsolete label for resp column
df$resp <- remove_labels(df$resp)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="preschool_sel.Rdata")
