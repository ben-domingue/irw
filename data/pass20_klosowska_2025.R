library(dplyr)
library(tidyr)
library(stringr)

df <- read.csv("PASS20_raw_data_online_sample.csv", sep = ";")
df1 <- read.csv("PASS20_raw_data_hospital_sample.csv", sep = ";")

df <- df %>%
  rename(id = ID, cov_age = age, cov_sex = sex, cov_race = race_ethnicity, cov_student = Student,
         cov_employed_full_time = Employed_full_time, cov_employed_part_time = Employed_Part_time,
         cov_unemployed = Unemployed, cov_retired = Retired, cov_pensioner = Pensioner,
         cov_sick_leave = sick_leave, cov_education = education, cov_residence = residence,
         cov_net_monthly_income = net_monthly_income, cov_marital_status = marital_status) 

df1 <- df1 %>%
  rename(id = ID, cov_age = age, cov_sex = sex, cov_race = race_ethnicity, cov_professional_status = professional_status,
         cov_sick_leave = sick_leave, cov_education = education, cov_residence = residence,
         cov_net_monthly_income = net_monthly_income, cov_marital_status = marital_status) 


df_pass <- df %>%
  select(c(id, starts_with("cov"), starts_with("pass"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp)) %>%
  mutate(wave = if_else(str_ends(item, "_2"), 2, 1)) %>%
  mutate(item = str_remove(item, "_2$"))
  

df_dass <- df %>%
  select(c(id, starts_with("cov"), starts_with("dass"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

df_staix <- df %>%
  select(c(id, starts_with("cov"), starts_with("staix"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

df_csq <- df %>%
  select(c(id, starts_with("cov"), starts_with("csq"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

df_pass_hospital <- df1 %>%
  select(c(id, starts_with("cov"), starts_with("PASS"))) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))


write.csv(df_pass, "pass20_klosowska_2025_pass_online.csv", row.names = FALSE)
write.csv(df_dass, "pass20_klosowska_2025_dass_online.csv", row.names = FALSE)
write.csv(df_staix, "pass20_klosowska_2025_staix_online.csv", row.names = FALSE)
write.csv(df_csq, "pass20_klosowska_2025_csq_online.csv", row.names = FALSE)
write.csv(df_pass_hospital, "pass20_klosowska_2025_pass_hospital.csv", row.names = FALSE)
