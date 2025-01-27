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
         item = paste0(pt1, '_', pt2, '_', pt3),
         wave_temp = '3') |>
  select(id, item, wave, wave_temp, resp) 

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
  mutate(wave_temp = case_when(wave == 'g1' ~ '1',
                          wave == 'g2' ~ '2',
                          wave == 'g3' ~ '3',
                          wave == 'w1' ~ '1',
                          wave == 'w2' ~ '2',
                          wave == 'w3' ~ '3')) |>
  select(id, item, wave, wave_temp, resp) 

# transform kbit assessment variables
kbit <- df_raw |>
  select(id,
         starts_with('kbit')) |>
  pivot_longer(cols = -id,
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = NA, wave_temp = NA) |>
  select(id, item, wave, wave_temp, resp)

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
  mutate(wave_temp = case_when(wave == 'g1' ~ '1',
                               wave == 'g2' ~ '2',
                               wave == 'g3' ~ '3',
                               wave == 'w1' ~ '1',
                               wave == 'w2' ~ '2',
                               wave == 'w3' ~ '3')) |>
  select(id, item, wave, wave_temp, resp)

tosrec2 <- df_raw |>
  select(id,
         starts_with('tosrec_g1c'),
         starts_with('tosrec_g2a')) |>
  pivot_longer(cols = -id,
               names_to = c('pt1', 'wave', 'pt2', 'pt3', 'pt4'),
               names_sep = '_',
               values_to = 'resp',
               values_drop_na = T) |>
  # mutate(wave = case_when(wave == 'g1c' ~ 'g1_end',
  #                         wave == 'g2a' ~ 'g2_beginning'),
  #        item = paste0(pt1, '_', pt2, '_', pt3, '_', pt4)) |>
  mutate(wave_temp = case_when(wave == 'g1c' ~ '1',
                          wave == 'g2a' ~ '2'),
         item = paste0(pt1, '_', pt2, '_', pt3, '_', pt4)) |>
  select(id, item, wave, wave_temp, resp)

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
  mutate(wave_temp = case_when(wave == 'g1' ~ '1',
                               wave == 'g2' ~ '2',
                               wave == 'g3' ~ '3',
                               wave == 'w1' ~ '1',
                               wave == 'w2' ~ '2',
                               wave == 'w3' ~ '3')) |>
  select(id, item, wave, wave_temp, resp) 

df <- rbind(four, kbit, three, tosrec, tosrec2, two)

df$check <- str_sub(df$item, 1, 5)

df_ctopp <- df %>%
  filter(grepl("ctopp",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_mf <- df %>%
  filter(grepl("wj_mf",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_kbit <- df %>%
  filter(grepl("kbit",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")


df_wj_lw_grade <- df %>%
  filter(grepl("wj_lw",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_lw_wave <- df %>%
  filter(grepl("wj_lw",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_pc_grade <- df %>%
  filter(grepl("wj_pc",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_pc_wave <- df %>%
  filter(grepl("wj_pc",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_pv_grade <- df %>%
  filter(grepl("wj_pv",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_pv_wave <- df %>%
  filter(grepl("wj_pv",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_ak_grade <- df %>%
  filter(grepl("wj_ak",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_ak_wave <- df %>%
  filter(grepl("wj_ak",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_sa <- df %>%
  filter(grepl("wj_sa",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_wa_grade <- df %>%
  filter(grepl("wj_wa",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_wa_wave <- df %>%
  filter(grepl("wj_wa",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_wf <- df %>%
  filter(grepl("wj_wf",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_ap <- df %>%
  filter(grepl("wj_ap",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_qc <- df %>%
  filter(grepl("wj_qc",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_told_grade <- df %>%
  filter(grepl("told",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_told_wave <- df %>%
  filter(grepl("told",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_spell_grade <- df %>%
  filter(grepl("wj_sp",df$check), grepl("g",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_wj_spell_wave <- df %>%
  filter(grepl("wj_sp",df$check), grepl("w",wave))%>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_tosrec <- df %>%
  filter(grepl("tosre",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

df_topel <- df %>%
  filter(grepl("topel",df$check)) %>%
  select(id, item, wave_temp, resp) %>%
  rename("wave" = "wave_temp")

write.csv(df_ctopp, "project_kids_ctopp.csv", row.names=FALSE)
write.csv(df_wj_mf, "project_kids_wj_mf.csv", row.names=FALSE)
write.csv(df_kbit, "project_kids_kbit.csv", row.names=FALSE)
write.csv(df_wj_lw_grade, "project_kids_wj_lwid_grade.csv", row.names=FALSE)
write.csv(df_wj_lw_wave, "project_kids_wj_lwid_wave.csv", row.names=FALSE)
write.csv(df_wj_pc_grade, "project_kids_wj_pc_grade.csv", row.names=FALSE)
write.csv(df_wj_pc_wave, "project_kids_wj_pc_wave.csv", row.names=FALSE)
write.csv(df_wj_pv_grade, "project_kids_wj_pv_grade.csv", row.names=FALSE)
write.csv(df_wj_pv_wave, "project_kids_wj_pv_wave.csv", row.names=FALSE)
write.csv(df_wj_ak_grade, "project_kids_wj_ak_grade.csv", row.names=FALSE)
write.csv(df_wj_ak_wave, "project_kids_wj_ak_wave.csv", row.names=FALSE)
write.csv(df_wj_sa, "project_kids_wj_sa.csv", row.names=FALSE)
write.csv(df_wj_wa_grade, "project_kids_wj_wa_grade.csv", row.names=FALSE)
write.csv(df_wj_wa_wave, "project_kids_wj_wa_wave.csv", row.names=FALSE)
write.csv(df_wj_wf, "project_kids_wj_wf.csv", row.names=FALSE)
write.csv(df_wj_ap, "project_kids_wj_ap.csv", row.names=FALSE)
write.csv(df_wj_qc, "project_kids_wj_qc.csv", row.names=FALSE)
write.csv(df_told_grade, "project_kids_told_grade.csv", row.names=FALSE)
write.csv(df_told_wave, "project_kids_told_wave.csv", row.names=FALSE)
write.csv(df_wj_spell_grade, "project_kids_wj_spell_grade.csv", row.names=FALSE)
write.csv(df_wj_spell_wave, "project_kids_wj_spell_wave.csv", row.names=FALSE)
write.csv(df_tosrec, "project_kids_tosrec.csv", row.names=FALSE)
write.csv(df_topel, "project_kids_topel.csv", row.names=FALSE)
