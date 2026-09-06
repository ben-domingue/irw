library(tidyverse)
library(readr)

# Project KIDS, LDbase (https://ldbase.org). Both files download without an
# account and are open-licensed.
ITEM_URL <- "https://ldbase.org/system/files/datasets/2021-05/PK_ItemLevelData.csv"
# Total Scores data (DOI 10.33009/ldbase.1620844399.85a0, ODC-By): carries
# `treatment` (RCT arm) and `project` (which of the 9 RCTs), linkable to the
# item-level file on PK_ID. See issue #416.
FULL_URL <- "https://ldbase.org/system/files/datasets/2021-08/PK_FullData.csv"

ldbase_csv <- function(file, url) {
  if (!file.exists(file)) download.file(url, file, mode = "wb", quiet = TRUE)
  read_csv(file, show_col_types = FALSE)
}

df_raw  <- ldbase_csv('PK_ItemLevelData.csv', ITEM_URL)
df_full <- ldbase_csv('PK_FullData.csv',      FULL_URL)

# Attach the RCT arm and study id before pk_id is dropped. `treat` is
# defined as binary treatment/control in datastandard.md, so the 59
# participants coded 2 (a third arm, in projects 3 and 5) and the 1 with no
# value are left blank rather than folded into either group; cov_project
# keeps the 9 RCTs distinguishable.
df_full <- df_full |>
  select(PK_ID, treatment, project) |>
  mutate(treat = if_else(treatment %in% c(0, 1), treatment, NA_real_),
         cov_project = project) |>
  select(PK_ID, treat, cov_project)
df_raw <- df_raw |> left_join(df_full, by = "PK_ID")

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


drop_vars <- setdiff(drop_vars, c("treat", "cov_project"))

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

# person-level columns carried onto every response row at the end
person_cols <- df_raw |> select(id, treat, cov_project)
df_raw <- df_raw |> select(-treat, -cov_project)

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
df <- df |> left_join(person_cols, by = "id")

df$check <- str_sub(df$item, 1, 5)

df_ctopp <- df %>%
  filter(grepl("ctopp",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_mf <- df %>%
  filter(grepl("wj_mf",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_kbit <- df %>%
  filter(grepl("kbit",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")


df_wj_lw_grade <- df %>%
  filter(grepl("wj_lw",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_lw_wave <- df %>%
  filter(grepl("wj_lw",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_pc_grade <- df %>%
  filter(grepl("wj_pc",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_pc_wave <- df %>%
  filter(grepl("wj_pc",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_pv_grade <- df %>%
  filter(grepl("wj_pv",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_pv_wave <- df %>%
  filter(grepl("wj_pv",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_ak_grade <- df %>%
  filter(grepl("wj_ak",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_ak_wave <- df %>%
  filter(grepl("wj_ak",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_sa <- df %>%
  filter(grepl("wj_sa",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_wa_grade <- df %>%
  filter(grepl("wj_wa",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_wa_wave <- df %>%
  filter(grepl("wj_wa",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_wf <- df %>%
  filter(grepl("wj_wf",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_ap <- df %>%
  filter(grepl("wj_ap",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_qc <- df %>%
  filter(grepl("wj_qc",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_told_grade <- df %>%
  filter(grepl("told",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_told_wave <- df %>%
  filter(grepl("told",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_spell_grade <- df %>%
  filter(grepl("wj_sp",df$check), grepl("g",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_wj_spell_wave <- df %>%
  filter(grepl("wj_sp",df$check), grepl("w",wave))%>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_tosrec <- df %>%
  filter(grepl("tosre",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

df_topel <- df %>%
  filter(grepl("topel",df$check)) %>%
  select(id, item, resp, wave_temp, treat, cov_project) %>%
  rename("wave" = "wave_temp")

# Output goes to the standard location, and the three arguments below are not
# cosmetic -- each repairs a defect that reached the published tables (#416,
# all three measured on the live corpus 2026-09-04):
#
#   na = ""       the default `na = "NA"` wrote the literal string "NA" wherever
#                 `treat` or `wave` was missing. Redivis then typed those
#                 columns as *strings* with "NA" as a third level: 16 of the 23
#                 tables carried 25,242 such `treat` values, and sibling tables
#                 disagreed on the type of the same column.
#   as.integer    `wave` was a character column, so it published quoted and was
#                 typed string in some tables and integer in others.
#   drop-empty    kbit has no wave (see the `mutate(wave = NA)` above), so it
#                 shipped 80,865 rows of a column whose every value was "NA".
#
# Run from `data/`; override with IRW_OUT if you keep outputs elsewhere.
OUT <- Sys.getenv("IRW_OUT", file.path("..", "automated_finding", "irw_output"))
dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
irw_write <- function(df, name) {
  if ("wave" %in% names(df)) df$wave <- as.integer(df$wave)
  df <- df[, colSums(!is.na(df)) > 0, drop = FALSE]
  write.csv(df, file.path(OUT, name), row.names = FALSE, na = "")
}

irw_write(df_ctopp, "project_kids_ctopp.csv")
irw_write(df_wj_mf, "project_kids_wj_mf.csv")
irw_write(df_kbit, "project_kids_kbit.csv")
irw_write(df_wj_lw_grade, "project_kids_wj_lwid_grade.csv")
irw_write(df_wj_lw_wave, "project_kids_wj_lwid_wave.csv")
irw_write(df_wj_pc_grade, "project_kids_wj_pc_grade.csv")
irw_write(df_wj_pc_wave, "project_kids_wj_pc_wave.csv")
irw_write(df_wj_pv_grade, "project_kids_wj_pv_grade.csv")
irw_write(df_wj_pv_wave, "project_kids_wj_pv_wave.csv")
irw_write(df_wj_ak_grade, "project_kids_wj_ak_grade.csv")
irw_write(df_wj_ak_wave, "project_kids_wj_ak_wave.csv")
irw_write(df_wj_sa, "project_kids_wj_sa.csv")
irw_write(df_wj_wa_grade, "project_kids_wj_wa_grade.csv")
irw_write(df_wj_wa_wave, "project_kids_wj_wa_wave.csv")
irw_write(df_wj_wf, "project_kids_wj_wf.csv")
irw_write(df_wj_ap, "project_kids_wj_ap.csv")
irw_write(df_wj_qc, "project_kids_wj_qc.csv")
irw_write(df_told_grade, "project_kids_told_grade.csv")
irw_write(df_told_wave, "project_kids_told_wave.csv")
irw_write(df_wj_spell_grade, "project_kids_wj_spell_grade.csv")
irw_write(df_wj_spell_wave, "project_kids_wj_spell_wave.csv")
irw_write(df_tosrec, "project_kids_tosrec.csv")
irw_write(df_topel, "project_kids_topel.csv")
