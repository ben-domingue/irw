library(dplyr)
library(tidyr)
library(stringr)

# X_MR* hold the selected elements as a 20-character string of 0s and 1s
# (codebook: "Character vector"). Read as numbers they became floats such as
# 1.11110001e+19, losing leading zeros and digits (irw#2513), so read them as
# text.
hdr <- names(read.csv("tte_data.csv", nrows = 1))
df <- read.csv("tte_data.csv",
               colClasses = setNames(ifelse(grepl("^X_MR", hdr), "character", NA), hdr))

colnames(df)

df <- df %>%
  select(-matches("MRt|MRm|CTt")) %>%
  rename(id = ID, group = Group, cov_age = Age, cov_gender = Gender, cov_education = Education, cov_language = Language, cov_country = Country, cov_device = Device,
         cov_ac = AC, cov_disruptions = Disruptions)

df_ao <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), AO01:AO12) %>%
  pivot_longer(AO01:AO12,
               names_to = "item",
               values_to = "resp")

df_ef <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("EF"), -c(EF_01, EF_02)) %>%
  pivot_longer(EF01_01:EF05_02,
               names_to = "item",
               values_to = "resp") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "_01|_02"))

df_cm <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("CM"), -c(CM_01, CM_02, CM_03)) %>%
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
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("X_CT")) %>%
  pivot_longer(X_CT01_01:X_CT09_03,
               names_to = "item",
               values_to = "resp_raw") %>%
  mutate(wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    str_ends(item, "_03") ~ 3,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^X_")) %>%
  mutate(item = str_remove(item, "_01|_02|_03"))

df_ct_code <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("Y_CT"), -c(Y_CT_01, Y_CT_02, Y_CT_03)) %>%
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
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions, X_MRp01, X_MRp02)) %>%
  pivot_longer(X_MRp01:X_MRp02,
               names_to = "item",
               values_to = "resp") %>%
  mutate(item = str_remove(item, "^X_"))

df_mrp_rt <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions, T_MRp01, T_MRp02)) %>%
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
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("X_MR"), -starts_with("X_MRp")) %>%
  pivot_longer(X_MR01_01:X_MR20_02,
               names_to = "item",
               values_to = "resp_raw") %>%
  mutate(resp_raw = na_if(trimws(resp_raw), ""),  # 4 blank cells = no response
         wave = case_when(
    str_ends(item, "_01") ~ 1,
    str_ends(item, "_02") ~ 2,
    TRUE ~ NA_integer_
  ), item = str_remove(item, "^X_")) %>%
  mutate(item = str_remove(item, "_01|_02"))

df_mr_code <- df %>%
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("Y_MR"), -starts_with("Y_MRp")) %>%
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
  select(c(id, group, cov_age, cov_gender, cov_education, cov_language, cov_country, cov_device, cov_ac, cov_disruptions), starts_with("T_MR"), -starts_with("T_MRp")) %>%
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

# Design (Much et al., 2025, JOPD 13(1), "Study design"; codebook `Group`): participants were
# randomly assigned to Group 1 (non-speeded instruction first) or Group 2 (speeded first). The
# matrix test ran as two 10-item blocks (MR01-10 = block 1 = wave 1, MR11-20 = block 2 = wave 2),
# each under a different instruction. Concentration (t1-t3) and current motivation (t1-t3) were
# measured before and after the blocks, effort after each block, action orientation before any
# instruction; none of those items were answered under an instruction.
# `treat` therefore means (irw#2513, decided 2026-09-28):
#   matrixreasoning: 1 = item answered under the speeded instruction (group x block), 0 = non-speeded;
#   every other table: 1 = assigned to Group 2 (speeded block first), 0 = Group 1, i.e. the
#   randomised order. `wave` keeps the measurement occasion. The bare `group` column is dropped
#   (recoverable from treat, and not a standard column).
# cov_ac = attention checks passed (0-3); cov_disruptions = the authors' 11-category coding of
# open responses about disruptions (codebook `AC`, `Disruptions`).
std_order <- function(d) {
  lead <- intersect(c("id", "item", "resp", "resp_raw", "wave", "treat", "rt"), names(d))
  d[, c(lead, setdiff(names(d), lead))]
}
order_treat <- function(d) {
  d %>% mutate(treat = as.integer(group == 2)) %>% select(-group) %>% std_order()
}

df_mr <- df_mr %>%
  mutate(treat = as.integer((group == 1 & wave == 2) | (group == 2 & wave == 1))) %>%
  select(-group) %>%
  std_order()

# na = "": a literal "NA" types the column string on Redivis (irw#2029).
write.csv(df_mr, "much_tte_2025_matrixreasoning.csv", row.names = FALSE, na = "")
##write.csv(df_mrp, "much_tte_2025_unsolvablepersistence.csv", row.names = FALSE) ##removed 4-17-2025 by BD, responses not ordinal
write.csv(order_treat(df_ct), "much_tte_2025_concentrationtask.csv", row.names = FALSE, na = "")
write.csv(order_treat(df_cm), "much_tte_2025_currentmotivation.csv", row.names = FALSE, na = "")
write.csv(order_treat(df_ef), "much_tte_2025_effort.csv", row.names = FALSE, na = "")
write.csv(order_treat(df_ao), "much_tte_2025_actionorientation.csv", row.names = FALSE, na = "")
