library(tidyverse)
library(readr)

# ---- 11th graders, SY 11-12
pact11_1112 <- read_csv('PACT 11 11_12 clean.csv')

names(pact11_1112) <- tolower(names(pact11_1112))

drop_vars <- c()

for (i in 1:ncol(pact11_1112)) {
  unique_vals <- unique(pact11_1112[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(pact11_1112)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(pact11_1112)[i])
  }
  
  if (class(pact11_1112[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(pact11_1112)[i])
  }
}

pact11_1112 <- pact11_1112 |>
  select(-`...1`,
         -ends_with('r'),
         -all_of(drop_vars),
         -contains('raw'),
         -period,
         -school,
         -lep,
         -contains('.'),
         -frpl,
         -ell,
         -et3nicity,
         -grade,
         -frl,
         -sped,
         -site,
         -tvc,
         -tested,
         -ends_with('_tot'),
         -ends_with('_ssq'),
         -ends_with('_nce'),
         -ends_with('_mc'),
         -ends_with('_rc'),
         -ends_with('_ess'),
         -ends_with('_se'),
         -ends_with('_csu'),
         -starts_with('mrs')) |>
  mutate_all(~ replace(., . == 99, NA)) |>
  mutate(cond = if_else(cond == 9, NA, cond)) |>
  pivot_longer(cols = -c(sid, cond),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)
  


# ---- 11th graders, SY 12-13
pact11_1213 <- read_csv('PACT11 12_13 clean.csv')

names(pact11_1213) <- tolower(names(pact11_1213))

drop_vars <- c()

for (i in 1:ncol(pact11_1213)) {
  unique_vals <- unique(pact11_1213[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(pact11_1213)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(pact11_1213)[i])
  }
  
  if (class(pact11_1213[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(pact11_1213)[i])
  }
}

pact11_1213 <- pact11_1213 |>
  select(-`...1`,
         -ends_with('r'),
         -all_of(drop_vars),
         -contains('raw'),
         -school,
         -tid,
         -grade,
         -starts_with('gtr'),
         -starts_with('tr'),
         -starts_with('ty'),
         -ends_with('_tst'),
         -ends_with('_dt'),
         -starts_with('utts'),
         -lep,
         -frl,
         -starts_with('taks'),
         -contains('sped'),
         -starts_with('re_'),
         -dist,
         -status,
         -nw_grd,
         -starts_with('fcat_'),
         -econ_dis,
         -prmlg,
         -period,
         -ends_with('_tot')) |>
  mutate(across(starts_with('mr_'), ~if_else(. == 0, NA, .))) |>
  pivot_longer(cols = -c(sid, cond),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)


# 8th grade, SY 11-12
pact8_1112 <- read_csv('PACT8 11_12 Clean.csv')

names(pact8_1112) <- tolower(names(pact8_1112))

drop_vars <- c()

for (i in 1:ncol(pact8_1112)) {
  unique_vals <- unique(pact8_1112[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(pact8_1112)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(pact8_1112)[i])
  }
  
  if (class(pact8_1112[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(pact8_1112)[i])
  }
}

pact8_1112 <- pact8_1112 |>
  select(-all_of(drop_vars),
         -ends_with('r'),
         -contains('raw'),
         -`...1`,
         -school,
         -tested,
         -starts_with('mrs'),
         -lep,
         -esl,
         -sped,
         -starts_with('ut'),
         -ends_with('_rc'),
         -ends_with('_mc'),
         -tvc,
         -ends_with('tot'),
         -period,
         -ends_with('ess'),
         -ends_with('ssf'),
         -ends_with('ssq'),
         -ends_with('nce'),
         -ends_with('csu'),
         -contains('race'),
         -frl,
         -prmlang,
         -proflvl,
         -vrtsclsc,
         -mtpasssc,
         -quanlex,
         -starts_with('fcat'),
         -district,
         -con1,
         -starts_with('yt'),
         -deg,
         -starts_with('pd'),
         -matches("^e\\d"),
         -emn,
         -matches("^i\\d"),
         -matches("^a\\d[[:alpha:]]"),
         -imn,
         -matches("^si\\d"),
         -simn,
         -ends_with('_se'),
         -ends_with('_ssw')) |>
  mutate(across(starts_with('ras') | starts_with('mslq'), ~if_else(. == 0, NA, .))) |>
  rename(cond = condition) |>
  pivot_longer(cols = -c(sid, cond),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)


# 8th grade, SY 12-13

pact8_1213 <- read_csv('PACT8 12_13 Clean.csv')

names(pact8_1213) <- tolower(names(pact8_1213))

drop_vars <- c()

for (i in 1:ncol(pact8_1213)) {
  unique_vals <- unique(pact8_1213[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(pact8_1213)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(pact8_1213)[i])
  }
  
  if (class(pact8_1213[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(pact8_1213)[i])
  }
}

pact8_1213 <- pact8_1213 |>
  select(-`...1`,
         -tid,
         -grade,
         -period,
         -column.11,
         -status,
         -dist,
         -chsch,
         -gender,
         -ends_with('r'),
         -all_of(drop_vars),
         -contains('raw'),
         -period,
         -school,
         -lep,
         -ends_with('_mc'),
         -ends_with('_rc'),
         -grade,
         -frl,
         -sped,
         -status,
         -econ_dis,
         -starts_with('re_'),
         -ends_with('_tst'),
         -starts_with('uts'),
         -qms,
         -qmt,
         -ends_with('ss'),
         -ends_with('nce'),
         -starts_with('fcat_'),
         -ends_with('_ps'),
         -ends_with('_mt'),
         -ends_with('_cm'),
         -ends_with('_rw'),
         -starts_with('utts'),
         -esl,
         -sped_cd,
         -prmlg,
         -tl1,
         -cgt,
         -starts_with('ty'),
         -starts_with('tr'),
         -x) |>
  mutate_all(~ replace(., . == 99, NA)) |>
  pivot_longer(cols = -c(sid, cond),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)

# --

voco <- read_csv('VOCO clean.csv')

names(voco) <- tolower(names(voco))

drop_vars <- c()

for (i in 1:ncol(voco)) {
  unique_vals <- unique(voco[[i]])
  unique_len <- length(unique_vals)
  
  if (unique_len == 1 & is.na(unique(unique_vals[1]))) {
    drop_vars <- append(drop_vars, names(voco)[i])
  }
  
  if (unique_len == 2 & (is.na(unique_vals[1]) | is.na(unique_vals[2]))) {
    drop_vars <- append(drop_vars, names(voco)[i])
  }
  
  if (class(voco[[i]]) == 'character') {
    drop_vars <- append(drop_vars, names(voco)[i])
  }
}

voco <- voco |>
  select(-all_of(drop_vars),
         -`...1`,
         -ends_with('r'),
         -ends_with('raw'),
         -ends_with('_ss'),
         -ends_with('_nce'),
         -ends_with('_ess'),
         -ends_with('_tst'),
         -contains('age'),
         -starts_with('re_'),
         -ends_with('sum'),
         -ends_with('_rw'),
         -ends_with('_dt'),
         -ends_with('_ri'),
         -ends_with('_ge'),
         -ends_with('_rc'),
         -ends_with('_lw'),
         -ends_with('_tot'),
         -ends_with('_is'),
         -ends_with('_ls'),
         -ends_with('_tac'),
         -ends_with('_tcc'),
         -ends_with('_tf'),
         -ends_with('_tn'),
         -ends_with('_va'),
         -ends_with('_fa'),
         -ends_with('_na'),
         -ends_with('_ls'),
         -ends_with('_qm'),
         -ends_with('_ia'),
         -status,
         -school,
         -chsch,
         -period,
         -grade,
         -dob,
         -gender,
         -frl,
         -lep,
         -sped,
         -dp_12,
         -dp_12,
         -read8_12,
         -reade1_13,
         -tows1_96,
         -tows1_97,
         -tows1_98,
         -tows1_99,
         -tows1_100,
         -tows1_101,
         -tows1_102,
         -tows1_103,
         -tows1_104,
         -dp_13) |>
  pivot_longer(cols = -c(sid, cond),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T)


# COMBINE WAVES

df <- rbind(pact8_1112, pact8_1213, pact11_1112, pact11_1213, voco)

items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$sid))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('sid' = "unique(df$sid)")) |>
  # drop character item variable
  select(id, cond, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id,
         treatment = cond) |>
  arrange(id, item)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="pact_project.Rdata")
