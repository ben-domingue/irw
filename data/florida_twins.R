library(tidyverse)
library(readr)

# ------ WAVE 1 DATASET
df1 <- read_csv('Wave 1 Child LDBase.csv')

names(df1) <- tolower(names(df1))

df1 <- df1 %>%
  filter(twinid == 0)

auths <- df1 |>
  select(student_id0,
         contains('auth')) |>
  select(student_id0,
         contains('b')) |>
  # recode invalid responses as NA, change remaining responses to 0/1 binary
  mutate(across(starts_with('auth'), ~if_else(. == 0, NA, .)),
         across(starts_with('auth'), ~if_else(. == 1, 0, .)),
         across(starts_with('auth'), ~if_else(. == 2, 1, .)))

# save names of vars in this df to drop and later merge back onto the full df
auth_names <- names(auths[2:ncol(auths)])

df1 <- df1 |>
  # drop unneeded variables
  select(-all_of(auth_names),
         -reading_grades0,
         -reading_grades1,
         # -starts_with('npar'),
         # -starts_with('nnpar'),
         # -starts_with('par'),
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
         -id0,
         -contains('total'),
         -starts_with('childchaos'),
         -starts_with('identifier'),
         -starts_with('tid'),
         -`...1`,
         -gender_master,
         -pair_gender,
         -multiple,
         -zygparsum,
         -zyg_par,
         -fid,
         -contains('cqbar')) |>
  left_join(auths, by = "student_id0") |>
  # add participant ID
  rename(family_id = famid,
         cov_age = qage)

df10 <- df1 %>%
  select(bg_id0, cov_age, ends_with("0")) %>%
  rename(id = bg_id0) %>%
  pivot_longer(cols = -c(id, cov_age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) %>%
  mutate(wave = 1)

df10$item <- substring(df10$item, 1, nchar(df10$item) - 1)

df11 <- df1 %>%
  select(student_id1, cov_age, ends_with("1")) %>%
  rename(id = student_id1) %>%
  pivot_longer(cols = -c(id, cov_age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) %>%
  mutate(wave = 1)

df11$item <- substring(df11$item, 1, nchar(df11$item) - 1)

df1_ <- bind_rows(df10, df11)

df1_ <- df1_[!(grepl("^n", df1_$item) & !grepl("^nes", df1_$item)),] # remove reverted scales

unique(df1_$item)


# ----- WAVE 2 DATASET

df2 <- read_csv('wave2multitwinq718 LDBase_0.csv')
names(df2) <- tolower(names(df2))

df2 <- df2 %>%
  filter(twinid == 0)

df2 <- df2 |>
  select(-`...1`,
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
         -id0,
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
  rename(cov_age = bq2age)

df20 <- df2 %>%
  select(bg_id0, cov_age, ends_with("0")) %>%
  rename(id = bg_id0) %>%
  pivot_longer(cols = -c(id, cov_age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) %>%
  mutate(wave = 2)


df21 <- df2 %>%
  select(bg_id1, cov_age, ends_with("1")) %>%
  rename(id = bg_id1) %>%
  pivot_longer(cols = -c(id, cov_age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) %>%
  mutate(wave = 2)

df2_ <- bind_rows(df20, df21)

df2_$item <- substring(df2_$item, 2, nchar(df2_$item) - 1)

df2_ <- df2_[!(grepl("^n", df2_$item) & !grepl("^nes", df2_$item)),] 

df2_


# ------- WAVE 3 DATASET

df3 <- read_csv('w3multitwinq818 LDBase.csv')

names(df3) <- tolower(names(df3))

df3 <- df3 %>%
  filter(twinid == 0)

df3 <- df3 |>
  select(-`...1`,
         -twinid,
         -contains('gender'),
         -multiple,
         -id1,
         -id0,
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
  rename(cov_age = cq3age) |>
  mutate(across(contains('hwk'), ~ . + 1),
         across(contains('grades'), ~if_else(. == 7, NA, .))) 

df30 <- df3 %>%
  select(bg_id0, cov_age, ends_with("0")) %>%
  rename(id = bg_id0) %>%
  pivot_longer(cols = -c(id, cov_age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) %>%
  mutate(wave = 3)


df31 <- df3 %>%
  select(bg_id1, cov_age, ends_with("1")) %>%
  rename(id = bg_id1) %>%
  pivot_longer(cols = -c(id, cov_age),
               names_to = 'item',
               values_to = 'resp',
               values_drop_na = T) %>%
  mutate(wave = 3)

df3_ <- bind_rows(df30, df31)

df3_$item <- substring(df3_$item, 2, nchar(df3_$item) - 1)

df3_ <- df3_[!(grepl("^n", df3_$item) & !grepl("^nes", df3_$item)),]

# ---- merge three waves datasets

df <- rbind(df1_, df2_, df3_)

unique(df$item)

print(unique(df$item), max = 2000)

df_chaos <- df %>%
  filter(grepl("chaos", item))

df_grades <- df %>%
  filter(grepl("grades", item))

df_nes <- df %>%
  filter(grepl("nes", item))

df_par <- df %>%
  filter(grepl("par", item))

df_class <- df %>%
  filter(grepl("class", item))

df_sch <- df %>%
  filter(grepl("sch", item))

df_read <- df %>%
  filter(grepl("read", item))

df_panas <- df %>%
  filter(grepl("panas", item))

df_cads <- df %>%
  filter(grepl("cads", item))

df_friends <- df %>%
  filter(grepl("friends", item))

df_auth <- df %>%
  filter(grepl("auth", item))

df_pals <- df %>%
  filter(grepl("pals", item))

df_dweck <- df %>%
  filter(grepl("dweck", item))

df_grit <- df %>%
  filter(grepl("grit", item))

df_hwk <- df %>%
  filter(grepl("hwk", item))

df_tech <- df %>%
  filter(grepl("tech", item))

df_media <- df %>%
  filter(grepl("media", item))

df_dbi <- df %>%
  filter(grepl("dbi", item))

df_leq <- df %>%
  filter(grepl("leq", item))

df_game <- df %>%
  filter(grepl("game", item))

write.csv(df_chaos, "florida_twins_chaos.csv", row.names=FALSE)
write.csv(df_grades, "florida_twins_grades.csv", row.names=FALSE)
write.csv(df_nes, "florida_twins_nes.csv", row.names=FALSE)
write.csv(df_par, "florida_twins_par.csv", row.names=FALSE)
write.csv(df_class, "florida_twins_class.csv", row.names=FALSE)
write.csv(df_sch, "florida_twins_sch.csv", row.names=FALSE)
write.csv(df_read, "florida_twins_read.csv", row.names=FALSE)
write.csv(df_panas, "florida_twins_panas.csv", row.names=FALSE)
write.csv(df_cads, "florida_twins_cads.csv", row.names=FALSE)
write.csv(df_friends, "florida_twins_friends.csv", row.names=FALSE)
write.csv(df_auth, "florida_twins_auth.csv", row.names=FALSE)
write.csv(df_pals, "florida_twins_pals.csv", row.names=FALSE)
write.csv(df_dweck, "florida_twins_dweck.csv", row.names=FALSE)
write.csv(df_grit, "florida_twins_grit.csv", row.names=FALSE)
write.csv(df_hwk, "florida_twins_hwk.csv", row.names=FALSE)
write.csv(df_tech, "florida_twins_tech.csv", row.names=FALSE)
write.csv(df_media, "florida_twins_media.csv", row.names=FALSE)
write.csv(df_dbi, "florida_twins_dbi.csv", row.names=FALSE)
write.csv(df_leq, "florida_twins_leq.csv", row.names=FALSE)
write.csv(df_game, "florida_twins_game.csv", row.names=FALSE)
