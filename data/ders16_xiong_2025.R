setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)
library(haven)

# --------------------------------- ders-16 ------------------------------------
df <- read_sav("Total sample_data.sav")
df_long <- df %>%
  mutate(id=row_number()) %>%
  pivot_longer(
    cols = starts_with("ders"),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_gender=sex, cov_age=age, item, resp)

write_csv(df_long, "ders16_xiong_2025.csv")
# --------------------------------- lec-5 ------------------------------------
df_ado <- read_csv("Adolescent_data.csv")
df_costu <- read_sav("College student_data.sav")
df_comadu <- read_sav("Community adult_data.sav")
df_manpri <- read_sav("Male prisoner_data.sav")
df_all <- bind_rows(df_ado, df_costu, df_comadu, df_manpri)

df_long_lec5 <- df_all %>%
  mutate(id=row_number()) %>%
  pivot_longer(
    cols = starts_with("lec", ignore.case = FALSE),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_gender=sex, cov_age=age, item, resp)
write_csv(df_long_lec5, "lec5_xiong_2025.csv")
# --------------------------------- pcl-5 ------------------------------------
df_long_pcl5 <- df_all %>%
  mutate(id=row_number()) %>%
  pivot_longer(
    cols = starts_with("pcl", ignore.case = FALSE),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_gender=sex, cov_age=age, item, resp)
write_csv(df_long_pcl5, "pcl5_xiong_2025.csv")
# --------------------------------- phq-9 ------------------------------------
df_long_phq9 <- df_all %>%
  mutate(id=row_number()) %>%
  pivot_longer(
    cols = starts_with("phq", ignore.case = FALSE),
    names_to = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_gender=sex, cov_age=age, item, resp)
write_csv(df_long_phq9, "phq9_xiong_2025.csv")
