setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)
library(haven)
#-------------------------------- Study 1a-1c ----------------------------------
df_1a <- read_sav("Data_1a.sav") %>%
  mutate(id = paste0("1a_", row_number()))
df_1b <- read_sav("Data1b.sav") %>%
  mutate(id = paste0("1b_", row_number()))
df_1c <- read_sav("Data1c.sav") %>%
  mutate(id = paste0("1c_", row_number()))

df_long_1a <- df_1a %>%
  pivot_longer(
    cols = starts_with("Verification_") | starts_with("Fusion_") | starts_with("Fightdie_"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(cov_gender=as.numeric(Sex)) %>%
  mutate(item_family = "country",
         cov_study = "1a",
         treat = NA,
         wave = NA)  %>% 
  select(id, cov_gender, cov_age=Age, cov_study, treat, wave, item_family, item, resp)

df_long_1b <- df_1b %>%
  pivot_longer(
    cols = starts_with("Verification_") | starts_with("Fusion_") | starts_with("Fightdie_"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(cov_gender=as.numeric(Sex)) %>%
  mutate(item_family = "freedom",
         cov_study = "1b",
         treat = NA,
         wave = NA) %>%
  select(id, cov_gender, cov_age=Age, cov_study, treat, wave, item_family, item, resp)

df_long_1c <- df_1c %>%
  pivot_longer(
    cols = starts_with("Verification_") | starts_with("Fusion_") | starts_with("Fightdie_"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(cov_gender=as.numeric(Sex)) %>%
  mutate(item_family = "leader",
         cov_study = "1c",
         treat = NA,
         wave = NA) %>%
  select(id, cov_gender, cov_age=Age, cov_leader=Leader, cov_study, treat, wave, item_family, item, resp)

#-------------------------------- Study 2 ----------------------------------
df_2 <- read_sav("Data_2.sav")
df_long_2 <- df_2 %>%
  mutate(id = paste0("2_", row_number())) %>%
  pivot_longer(
    cols = starts_with("Verification_") | starts_with("Fusion_") | starts_with("Fightdie_") | starts_with("Evaluators_"),
               names_to = "item",
               values_to = "resp") %>%
  mutate(cov_gender=as.numeric(Sex), treat=as.numeric(CONDIT), item_family="country",
         cov_study="2", wave=NA) %>%
  select(id, cov_gender, cov_age=Age, cov_study, treat, wave, item_family, item, resp)
#-------------------------------- Study 3 ----------------------------------
df_3 <- read_sav("Data3.sav")
df_3 <- df_3 %>%
  mutate(id = paste0("3_", row_number())) %>%
  rename(
    cov_gender = Sex,
    cov_age = Age,
    treat = CONDIT
  )

wave1_vars <- c("Fusion_1_T1", "Fusion_2_T1", "Fusion_3_T1", "Fusion_4_T1",
                "Fusion_5_T1", "Fusion_6_T1", "Fusion_7_T1")

df_wave1 <- df_3 %>%
  select(id, cov_gender, cov_age, treat, all_of(wave1_vars)) %>%
  pivot_longer(
    cols = all_of(wave1_vars),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(wave = 1)

wave2_vars <- c(
  "Verification_1", "Verification_2", "Verification_3",
  "Fusion_1_T2", "Fusion_2_T2", "Fusion_3_T2", "Fusion_4_T2",
  "Fusion_5_T2", "Fusion_6_T2", "Fusion_7_T2",
  "Fightdie_1", "Fightdie_2", "Fightdie_3", "Fightdie_4",
  "Fightdie_5", "Fightdie_6", "Fightdie_7",
  "Evaluators_1", "Evaluators_2", "Evaluators_3", "Evaluators_4",
  "Evaluators_5", "Evaluators_6", "Evaluators_7"
)

df_wave2 <- df_3 %>%
  select(id, cov_gender, cov_age, treat, all_of(wave2_vars)) %>%
  pivot_longer(
    cols = all_of(wave2_vars),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(wave = 2)

df_long_3 <- bind_rows(df_wave1, df_wave2) %>%
  mutate(
    cov_gender = as.numeric(cov_gender),
    treat = as.numeric(treat),
    item_family = "country",
    cov_study = "3"
  ) %>%
  select(id, cov_gender, cov_age, cov_study, treat, wave, item_family, item, resp) %>%
  arrange(id, wave)
#-------------------------------- Study 4 ----------------------------------
df_4 <- read_sav("Data4.sav") %>%
  mutate(id = paste0("4_", row_number()))

df_long_4 <- df_4 %>%
  pivot_longer(
    cols = starts_with("Verification_") | starts_with("Relational_") |
      starts_with("Fusion_") | starts_with("Fightdie_"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(
    cov_gender = as.numeric(Sex)
  ) %>%
  mutate(item_family = "country", treat=NA, wave=NA, cov_study="4") %>%
  select(id, cov_gender, cov_age = Age, cov_study, treat, wave, item_family, item, resp)
#-------------------------------- Study 5 ----------------------------------
df_5a <- read_sav("Data5a.sav") %>%
  mutate(id = paste0("5a_", row_number()))
df_long_5a <- df_5a %>%
  pivot_longer(
    cols = matches("^VERIF|^FUSION|^Sacrifices|^Sincerity", ignore.case = FALSE),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(
    cov_gender = as.numeric(Sex)
  ) %>%
  mutate(item_family = "gang", treat=NA, wave=NA, cov_study="5a") %>%
  select(id, cov_gender, cov_age = Age, cov_gang = Name_gang, cov_study, treat, wave, item_family, item, resp)

df_5b <- read_sav("Data5b.sav")  %>%
  mutate(id = paste0("5b_", row_number()))
df_long_5b <- df_5b %>%
  pivot_longer(
    cols = matches("^VERIF|^FUSION|^Sacrifices|^Sincerity", ignore.case = FALSE),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(
    cov_gender = as.numeric(Sex)
  ) %>%
  mutate(item_family = "group", treat=NA, wave=NA, cov_study="5b") %>%
  select(id, cov_gender, cov_age = Age, cov_band = Name_band, cov_study, treat, wave, item_family, item, resp)
#-------------------------------- Supplementary Study ----------------------------------
df_supp <- read_sav("Data_supp.sav")
df_supp <- df_supp %>%
  mutate(id = paste0("supp_", row_number())) %>%
  rename(
    cov_gender = Sex,
    cov_age = Age,
  ) %>%
  mutate(treat = as.numeric(CONDIT), cov_study="supp", wave=NA, item_family="country")

df_long_supp <- df_supp %>%
  pivot_longer(
    cols = starts_with("Fusion_") | starts_with("Verification_") | starts_with("Fightdie_"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_gender, cov_age, cov_study, treat, wave, item_family, item, resp)
#-------------------------------- Combine Data ---------------------------------
df <- bind_rows(df_long_1a, df_long_1b, df_long_1c, df_long_2, df_long_3, df_long_4, df_long_5a, df_long_5b, df_long_supp) %>%
  select(id, cov_gender, cov_age, cov_study, treat, wave, item, item_family, resp) %>%
  mutate(id = as.numeric(factor(id, levels = str_sort(unique(id), numeric = TRUE))))
write_csv(df, "identity_fusion_gomez_2025.csv")
