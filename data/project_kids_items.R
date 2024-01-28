library(tidyverse)
library(readr)

df_raw <- read_csv('PK_ItemLevelData.csv')

names(df_raw) <- tolower(names(df_raw))

# find variables with no response or single responses to drop
# put them in a list to drop
drop_vars <- c()

for (i in 1:ncol(df_raw)) {
  unique_vals <- unique(df_raw[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(df_raw)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(df_raw)[i])
  }
}


df_raw <- df_raw |>
  # drop unneeded variables
  select(-all_of(drop_vars),
         -pk_id,
         -starts_with('ctrs'),
         -starts_with('swan'),
         -starts_with('ssrs'),
         -starts_with('tq')) |>
  # create participant ID
  mutate(id = row_number()) 

# transform tosrec assessment variables
tosrec <- df_raw |>
  select(id,
         starts_with('tosrec_g2c')) |>
  pivot_longer(cols = -id,
               names_to = c('pt1', 'wave', 'pt2', 'pt3'),
               names_sep = '_',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = 'g2_end',
         item = paste0(pt1, '_', pt2, '_', pt3)) |>
  select(id, item, wave, resp) 
  
# transform variables with three underscores       
three <- df_raw |>
  select(id,
         starts_with('ctopp'),
         starts_with('told'),
         starts_with('wj_ak'),
         starts_with('wj_ap'),
         starts_with('wj_lw'),
         starts_with('wj_pc'),
         starts_with('wj_pv'),
         starts_with('wj_qc'),
         starts_with('wj_sa'),
         starts_with('wj_spell'),
         starts_with('wj_wa'),
         starts_with('wj_wf')) |>
  pivot_longer(cols = -id,
               names_to = c('pt1', 'pt2', 'pt3', 'wave'),
               names_sep = '_',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(item = paste0(pt1, '_', pt2, '_', pt3)) |>
  select(id, item, wave, resp) 

# transform kbit assessment variables
kbit <- df_raw |>
  select(id,
         starts_with('kbit')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = NA)

# transform variables with two underscores
two <- df_raw |>
  select(id,
         starts_with('swan'),
         starts_with('topel')) |>
  pivot_longer(cols = -id,
               names_to = c('pt1', 'pt2', 'wave'),
               names_sep = '_',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(item = paste0(pt1, '_', pt2)) |>
  select(id, item, wave, resp)

tosrec2 <- df_raw |>
  select(id,
         starts_with('tosrec_g1c'),
         starts_with('tosrec_g2a')) |>
  pivot_longer(cols = -id,
               names_to = c('pt1', 'wave', 'pt2', 'pt3', 'pt4'),
               names_sep = '_',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = case_when(wave == 'g1c' ~ 'g1_end',
                          wave == 'g2a' ~ 'g2_beginning'),
         item = paste0(pt1, '_', pt2, '_', pt3, '_', pt4)) |>
  select(id, item, wave, resp)

# transform variables with four underscores
four <- df_raw |>
  select(id,
         starts_with('wj_mf')) |>
  pivot_longer(cols = -id,
               names_to = c('pt1', 'pt2', 'pt3', 'pt4', 'wave'),
               names_sep = '_',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(item = paste0(pt1, '_', pt2, '_', pt3, '_', pt4)) |>
  select(id, item, wave, resp) 

df <- rbind(four, kbit, three, tosrec, tosrec2, two)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  rowwise() |>
  mutate(person_id = id,
         id = paste0(id, '_', wave)) |>
  # drop character item variable
  select(id, person_id, item_id, wave, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(id, item, wave) 
  

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="project_kids_items.Rdata")
