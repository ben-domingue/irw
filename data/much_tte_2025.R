library(dplyr)
library(tidyr)
library(stringr)

df <- read.csv("tte_data.csv")

colnames(df)

df <- df %>%
  select(-matches("MRt|MRm|CTt")) %>%
  rename(id = ID, group = Group, cov_age = Age, cov_gender = Gender, cov_education = Education, cov_language = Language, cov_country = Country, cov_device = Device)

df_ao <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), AO01:AO12) %>%
  pivot_longer(AO01:AO12,
               names_to = "item",
               values_to = "resp")

df_ef <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("EF"), -c(EF_01, EF_02)) %>%
  pivot_longer(EF01_01:EF05_02,
               names_to = "item",
               values_to = "resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "_01|_02"))

df_cm <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("CM"), -c(CM_01, CM_02, CM_03)) %>%
  pivot_longer(CM01_01:CM03_03,
               names_to = "item",
               values_to = "resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    str_ends(item, "_03") ~ 3,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "_01|_02|_03"))

df_ct_raw <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("X_CT")) %>%
  pivot_longer(X_CT01_01:X_CT09_03,
               names_to = "item",
               values_to = "raw_resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    str_ends(item, "_03") ~ 3,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^X_")) %>%
  mutate(item = str_remove(item, "_01|_02|_03"))

df_ct_code <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("Y_CT"), -c(Y_CT_01, Y_CT_02, Y_CT_03)) %>%
  pivot_longer(Y_CT01_01:Y_CT09_03,
               names_to = "item",
               values_to = "resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    str_ends(item, "_03") ~ 3,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^Y_")) %>%
  mutate(item = str_remove(item, "_01|_02|_03"))

df_ct <- df_ct_raw %>%
  left_join(
    df_ct_code %>% select(id, item, wave, resp),
    by = c("id", "item", "wave")
  )

df_mrp_resp <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, X_MRp01, X_MRp02)) %>%
  pivot_longer(X_MRp01:X_MRp02,
               names_to = "item",
               values_to = "resp") %>%
  mutate(item = str_remove(item, "^X_"))

df_mrp_rt <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, T_MRp01, T_MRp02)) %>%
  pivot_longer(T_MRp01:T_MRp02,
               names_to = "item",
               values_to = "rt") %>%
  mutate(item = str_remove(item, "^T_"), rt = rt/1000)

df_mrp <- df_mrp_resp %>%
  left_join(
    df_mrp_rt %>% select(id, item, rt),
    by = c("id", "item")
  )

df_mr_raw <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("X_MR"), -starts_with("X_MRp")) %>%
  pivot_longer(X_MR01_01:X_MR20_02,
               names_to = "item",
               values_to = "raw_resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^X_")) %>%
  mutate(item = str_remove(item, "_01|_02"))

df_mr_code <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("Y_MR"), -starts_with("Y_MRp")) %>%
  pivot_longer(Y_MR01_01:Y_MR20_02,
               names_to = "item",
               values_to = "resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^Y_")) %>%
  mutate(item = str_remove(item, "_01|_02"))

df_mr_rt <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device), starts_with("T_MR"), -starts_with("T_MRp")) %>%
  pivot_longer(T_MR01_01:T_MR20_02,
               names_to = "item",
               values_to = "rt") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^T_")) %>%
  mutate(item = str_remove(item, "_01|_02"), rt = rt/1000)


df_mr <- df_mr_raw %>%
  left_join(
    df_mr_code %>% select(id, item, wave, resp),
    by = c("id", "item", "wave")
  ) %>%
  left_join(
    df_mr_rt %>% select(id, item, wave, rt),
    by = c("id", "item", "wave")
  )

write.csv(df_mr, "much_tte_2025_matrixreasoning.csv", row.names = FALSE)
write.csv(df_mrp, "much_tte_2025_unsolvablepersistence.csv", row.names = FALSE)
write.csv(df_ct, "much_tte_2025_concentrationtask.csv", row.names = FALSE)
write.csv(df_cm, "much_tte_2025_currentmotivation.csv", row.names = FALSE)
write.csv(df_ef, "much_tte_2025_effort.csv", row.names = FALSE)
write.csv(df_ao, "much_tte_2025_actionorientation.csv", row.names = FALSE)
