setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

df <- read_csv("data_deidentified.csv")

# Generic Conspiracist Beliefs Scale–5 (GCB-5)
df_gcb5_wave1 <- df %>%
  mutate(wave=1) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("gcb_xxx_"), wave) %>%
  pivot_longer(cols = 4:8,
               names_to = "item",
               values_to = "resp")
df_gcb5_wave2 <- df %>%
  mutate(wave=2) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("t2_gcb_xxx_"), wave)
names(df_gcb5_wave2) <- sub("^t2_", "", names(df_gcb5_wave2))
df_gcb5_wave2 <- df_gcb5_wave2 %>%
  pivot_longer(cols = starts_with("gcb_xxx_"),
               names_to = "item", values_to = "resp")
df_gcb5 <- bind_rows(df_gcb5_wave1, df_gcb5_wave2) %>%
  select(id, cov_age, cov_gender, wave, item, resp) %>%
  arrange(id, wave, item) %>%
  mutate(resp = resp + 4)
# Conspiracy Mentality Questionnaire (CMQ)
df_cmq_wave1 <- df %>%
  mutate(wave=1) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("cmq_xxx_"), wave) %>%
  pivot_longer(cols = 4:8,
               names_to = "item",
               values_to = "resp")
df_cmq_wave2 <- df %>%
  mutate(wave=2) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("t2_cmq_xxx_"), wave)
names(df_cmq_wave2) <- sub("^t2_", "", names(df_cmq_wave2))
df_cmq_wave2 <- df_cmq_wave2 %>%
  pivot_longer(cols = starts_with("cmq_xxx_"),
               names_to = "item", values_to = "resp")
df_cmq <- bind_rows(df_cmq_wave1, df_cmq_wave2) %>%
  select(id, cov_age, cov_gender, wave, item, resp) %>%
  arrange(id, wave, item) %>%
  mutate(resp = resp + 4)
# General Measure of Conspiracism (GMC)
df_gmc_wave1 <- df %>%
  mutate(wave=1) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("gmc_xxx_"), wave) %>%
  pivot_longer(cols = 4:8,
               names_to = "item",
               values_to = "resp")
df_gmc_wave2 <- df %>%
  mutate(wave=2) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("t2_gmc_xxx_"), wave)
names(df_gmc_wave2) <- sub("^t2_", "", names(df_gmc_wave2))
df_gmc_wave2 <- df_gmc_wave2 %>%
  pivot_longer(cols = starts_with("gmc_xxx_"),
               names_to = "item", values_to = "resp")
df_gmc <- bind_rows(df_gmc_wave1, df_gmc_wave2) %>%
  select(id, cov_age, cov_gender, wave, item, resp) %>%
  arrange(id, wave, item) %>%
  mutate(resp = resp + 4)
# American Conspiracy Thinking Scale (ACTS)
df_act_wave1 <- df %>%
  mutate(wave=1) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("act_xxx_"), wave) %>%
  pivot_longer(cols = 4:7,
               names_to = "item",
               values_to = "resp")
df_act_wave2 <- df %>%
  mutate(wave=2) %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("t2_act_xxx_"), wave)
names(df_act_wave2) <- sub("^t2_", "", names(df_act_wave2))
df_act_wave2 <- df_act_wave2 %>%
  pivot_longer(cols = starts_with("act_xxx_"),
               names_to = "item", values_to = "resp")
df_act <- bind_rows(df_act_wave1, df_act_wave2) %>%
  select(id, cov_age, cov_gender, wave, item, resp) %>%
  arrange(id, wave, item) %>%
  mutate(resp = resp + 4)
# One-Item Conspiracy Measure (1CM)
df_1cm_wave1 <- df %>%
  mutate(wave=1) %>%
  select(id, cov_age=age, cov_gender=gender, cm1_xxx_01_x, wave) %>%
  pivot_longer(cols = cm1_xxx_01_x,
               names_to = "item",
               values_to = "resp")
df_1cm_wave2 <- df %>%
  mutate(wave=2) %>%
  select(id, cov_age=age, cov_gender=gender, t2_cm1_xxx_01_x, wave)
names(df_1cm_wave2) <- sub("^t2_", "", names(df_1cm_wave2))
df_1cm_wave2 <- df_1cm_wave2 %>%
  pivot_longer(cols = cm1_xxx_01_x,
               names_to = "item", values_to = "resp")
df_1cm <- bind_rows(df_1cm_wave1, df_1cm_wave2) %>%
  select(id, cov_age, cov_gender, wave, item, resp) %>%
  arrange(id, wave, item) %>%
  mutate(resp = resp + 4)

# Belief in Conspiracy Theories Inventory-21 (BCTI-21)
df_bcti21 <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("sr_bcti_")) %>%
  pivot_longer(cols = 4:24,
               names_to = "item",
               values_to = "resp")
# Persecution and Deservedness Scale (PDS)
df_pds <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("pds_xxx_")) %>%
  pivot_longer(cols = 4:13,
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = resp + 4)
# Schizotypal Personality Questionnaire (SPQ,Odd Beliefs subscale)
df_spq <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("spq_xxx_")) %>%
  pivot_longer(cols = 4:10,
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = resp + 4)
# Agnew’s Anomie Scale (AGN)
df_agn <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("agn_xxx_")) %>%
  pivot_longer(cols = 4:11,
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = resp + 4)
# Need for Chaos Scale (NFC)
df_nfc <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("nfc_xxx_")) %>%
  pivot_longer(cols = 4:10,
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = resp + 4)
# Denialism Scale (DEN)
df_den <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("den_xxx_")) %>%
  pivot_longer(cols = 4:7,
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = resp + 4)
# Van Prooijen’s Coin Toss Task (CF)
df_cf <- df %>%
  select(id, cov_age=age, cov_gender=gender, starts_with("cf_")) %>%
  pivot_longer(cols = 4:14,
               names_to = "item",
               values_to = "resp")

# Export to csv file
write_csv(df_1cm, "onecm_kay_2025.csv")
write_csv(df_act, "act_kay_2025.csv")
write_csv(df_agn, "agn_kay_2025.csv")
write_csv(df_bcti21, "bcti21_kay_2025.csv")
write_csv(df_cf, "cf_kay_2025.csv")
write_csv(df_cmq, "cmq_kay_2025.csv")
write_csv(df_den, "den_kay_2025.csv")
write_csv(df_gcb5, "gcb5_2025.csv")
write_csv(df_gmc, "gmc_kay_2025.csv")
write_csv(df_nfc, "nfc_kay_2025.csv")
write_csv(df_pds, "pds_kay_2025.csv")
write_csv(df_spq, "spq_kay_2025.csv")
