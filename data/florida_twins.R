##############################
##NOTE: 12-10-2024 from BD. id has been replaced with person_id now that we have functionality to handle wave. this change was made manually, code does not reflect this update.
##############################


library(tidyverse)
library(readr)

# ------ WAVE 1 DATASET
df1 <- read_csv('Wave 1 Child LDBase.csv')

names(df1) <- tolower(names(df1))

auths <- df1 |>
  select(student_id0,
         contains('auth'))

authsb <- auths |>
  select(student_id0,
         contains('b')) |>
  # recode invalid responses as NA, change remaining responses to 0/1 binary
  mutate(across(starts_with('auth'), ~if_else(. == 0, NA, .)),
          across(starts_with('auth'), ~if_else(. == 1, 0, .)),
          across(starts_with('auth'), ~if_else(. == 2, 1, .)))

# save names of vars in this df to drop and later merge back onto the full df
auth_names <- names(authsb[2:ncol(authsb)])

df1 <- df1 |>
  # drop unneeded variables
  select(-all_of(auth_names),
         -reading_grades0,
         -reading_grades1,
         -starts_with('npar'),
         -starts_with('nnpar'),
         -starts_with('par'),
         -starts_with('artcorrect'),
         -starts_with('artfalse'),
         -starts_with('arttpe'),
         -starts_with('artppk'),
         -starts_with('artspk'),
         -starts_with('classsp'),
         -starts_with('classcm'),
         -starts_with('classca'),
         -starts_with('schattach'),
         -starts_with('schbond'),
         -starts_with('schactiv'),
         -starts_with('schneg'),
         -starts_with('reading_social'),
         -starts_with('reading_grades'),
         -starts_with('reading_curiosity'),
         -starts_with('reading_competition'),
         -starts_with('reading_involvement'),
         -starts_with('reading_work'),
         -starts_with('reading_efficacy'),
         -starts_with('reading_recognition'),
         -starts_with('panas_pa'),
         -starts_with('panas_na'),
         -starts_with('cadsyv_pos'),
         -starts_with('cadsyv_dar'),
         -starts_with('cadsyv_pro'),
         -starts_with('cadsyv_neg'),
         -starts_with('cadsyv_soc'),
         -starts_with('cadsyv_resp'),
         -starts_with('cadsyv_dis'),
         -starts_with('friends_bad'),
         -starts_with('friends_school'),
         -starts_with('friends_good'),
         -contains('info_sharing'),
         -bin,
         -ain,
         -id1,
         -contains('total'),
         -starts_with('childchaos'),
         -starts_with('bg_id'),
         -starts_with('identifier'),
         -starts_with('tid'),
         -`...1`,
         -twinid,
         -gender_master,
         -pair_gender,
         -multiple,
         -zygparsum,
         -zyg_par,
         -fid) |>
  left_join(authsb, by='student_id0') |>
  select(-starts_with('student_id')) |>
  # add participant ID
  rename(family_id = famid,
         age = qage) |>
  pivot_longer(cols = -c(id0, family_id, age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = 1)


# ----- WAVE 2 DATASET

df2 <- read_csv('wave2multitwinq718 LDBase_0.csv')
names(df2) <- tolower(names(df2))

df2 <- df2 |>
  select(-`...1`,
         -starts_with('bg_id'),
         -starts_with('bfcrr_twin'),
         -contains('hair'),
         -contains('eyes'),
         -starts_with('bfcrr_peas'),
         -starts_with('bfcrr_sim'),
         -starts_with('bfcrr_pretend'),
         -starts_with('btid'),
         -starts_with('fid'),
         -twinid,
         -gender_master,
         -pair_gender,
         -multiple,
         -contains('info_sharing'),
         -contains('total'),
         -id1,
         -ain,
         -bin,
         -zygparsum,
         -zyg_par,
         -starts_with('bpals_parentperformance'),
         -starts_with('bpals_parentdissonance'),
         -starts_with('artcorrect'),
         -starts_with('artfalse'),
         -starts_with('arttpe'),
         -starts_with('bpals_classroomapproach'),
         -starts_with('bpals_classroomavoid'),
         -starts_with('bpals_classroommaster'),
         -starts_with('bpals_teacheravoid'),
         -starts_with('bpals_teacherapproach'),
         -starts_with('bpals_teachermastery'),
         -starts_with('bpanas_na'),
         -starts_with('bpanas_pa'),
         -starts_with('bcadsyv_pos'),
         -starts_with('bcadsyv_dar'),
         -starts_with('bcadsyv_pro'),
         -starts_with('bcadsyv_neg'),
         -starts_with('bcadsyv_soc'),
         -starts_with('bcadsyv_resp'),
         -starts_with('bcadsyv_dis'),
         -starts_with('bfriends_bad'),
         -starts_with('bfriends_school'),
         -starts_with('bfriends_good'),
         -contains('sub'),
         -contains('bdweckincremental'),
         -contains('bdweckentity'),
         -contains('qoccup'),
         -starts_with('bgritconsistency'),
         -starts_with('bgritperseverance'),
         -starts_with('bart')) |>
  rename(age = bq2age) |>
  pivot_longer(cols = -c(id0, age, famid),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = 2) |>
  rename(family_id = famid)


# ------- WAVE 3 DATASET

df3 <- read_csv('w3multitwinq818 LDBase.csv')

names(df3) <- tolower(names(df3))

df3 <- df3 |>
  select(-`...1`,
         -starts_with('bg_id'),
         -twinid,
         -contains('gender'),
         -multiple,
         -id1,
         -fid,
         -contains('hair'),
         -contains('eyes'),
         -starts_with('cfcrr_peas'),
         -starts_with('cfcrr_sim'),
         -starts_with('cfcrr_pretend'),
         -contains('info_sharing'),
         -contains('total'),
         -contains('hemt'),
         -contains('occup'),
         -contains('_text'),
         -zygparsum,
         -zyg_par,
         -cpar140,
         -contains('info_sharing'),
         -starts_with('artcorrect'),
         -starts_with('artfalse'),
         -starts_with('cpanas_na'),
         -starts_with('cpanas_pa'),
         -contains('friends_bad'),
         -contains('friends_school'),
         -contains('friends_good'),
         -contains('sub'),
         -contains('cdweckincremental'),
         -contains('cdweckentity'),
         -starts_with('cdbi_sum'),
         -starts_with('cleq_schoolstress'),
         -starts_with('cleq_interpersonalstress'),
         -starts_with('cleq_schoolevents'),
         -starts_with('cleq_interpersonalevents'),
         -starts_with('cleq_stress'),
         -starts_with('cleq_events'),
         -contains('cart'),
         -starts_with('cweeklytv')) |>
  rename(age = cq3age) |>
  mutate(across(contains('hwk'), ~ . + 1),
         across(contains('grades'), ~if_else(. == 7, NA, .))) |>
  pivot_longer(cols = -c(id0, age, famid),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) |>
  mutate(wave = 3) |>
  rename(family_id = famid)


# ---- merge three waves datasets

df <- rbind(df1, df2, df3)

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

ids <- as.data.frame(unique(df$id0))
ids <- ids |>
  mutate(id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  left_join(ids, by=c('id0' = "unique(df$id0)"))  |>
  mutate(person_id = id,
         id = paste0(person_id, '_', wave)) |>
  # drop character item variable
  select(person_id, id, family_id, wave, age, item_id, resp) |>
  # use item_id column as the item column
  rename(item = item_id) |>
  arrange(person_id, item, wave)

# print response values
table(df$resp)

# save df to Rdata file
save(df, file="florida_twins.Rdata")
