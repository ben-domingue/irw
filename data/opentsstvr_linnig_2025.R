library(dplyr)

data <- read.csv2('Open_TSST_VR_data_study_1.csv', header = TRUE)

data <- data %>%
  rename(
    treat = condition,
    id = subject,
    cov_age = age,
    cov_BMI = BMI,
    cov_VR_experience = VR_experience,
    cov_VR_frequency = VR_frequency,
    cov_TICS_sum = TICS_sum,
    cov_SCL_GSI = SCL_GSI,
    cov_FNE_sum = FNE_sum,
    cov_SIAS_GES = SIAS_GES
  )

data_long <- data %>%
  pivot_longer(
    cols = -c(treat, id, starts_with("cov_")),
    names_to = "item",
    values_to = "resp"
  )

data_long <- data_long %>%
  mutate(
    construct = case_when(
      str_detect(item, "^VAS_") ~ "VAS",
      str_detect(item, "^IPQ") | str_detect(item, "^SPQ") ~ "VR",
      str_detect(item, "^SSQ") ~ "SSQ",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(construct))  # ignore HR and salivary (no construct assigned)


subjective_stress <- data_long %>%
  filter(construct == "VAS") %>%
  select(-construct)%>%
  mutate(wave = parse_number(item),
         item = str_remove(item, "[0-9]+$"))

virtual_reality_experience <- data_long %>%
  filter(construct == "VR") %>%
  select(-construct)

simulator_sickness <- data_long %>%
  filter(construct == "SSQ") %>%
  select(-construct)

write.csv(subjective_stress, "opentsstvr_linnig_2025_study1_vas.csv", row.names = FALSE)
write.csv(virtual_reality_experience, "opentsstvr_linnig_2025_study1_vrexperience.csv", row.names = FALSE)
write.csv(simulator_sickness, "opentsstvr_linnig_2025_study1_ssq.csv", row.names = FALSE)


data <- read.csv2('Open_TSST_VR_data_study_2.csv', header = TRUE)

data <- data %>%
  rename(
    treat = condition,
    id = subject,
    cov_age = age,
    cov_BMI = BMI,
    cov_sex = sex,
    cov_VR_experience = vr_exp,
    cov_VR_frequency = vr_exp_frequ,
    cov_TICS_SCORE = TICS_SCORE,
    cov_MSCL_GSI = MSCL_GSI,
    cov_FNE_SCORE = FNE_SCORE,
    cov_SIAS_SCORE = SIAS_SCORE,
    cov_order =order
  )%>%
  mutate(cov_order = as.integer(factor(cov_order)))

data_long <- data %>%
  pivot_longer(
    cols = -c(treat, id, starts_with("cov_")),
    names_to = "item",
    values_to = "resp"
  )

data_long <- data_long %>%
  mutate(
    construct = case_when(
      str_detect(item, "^VAS_") ~ "VAS",
      str_detect(item, "^IPQ") | str_detect(item, "^SPQ") ~ "VR",
      str_detect(item, "^SSQ") ~ "SSQ",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(construct))  # ignore HR and salivary (no construct assigned)


subjective_stress <- data_long %>%
  filter(construct == "VAS") %>%
  select(-construct)%>%
  mutate(wave = parse_number(item),
         item = str_remove(item, "[0-9]+$"))

virtual_reality_experience <- data_long %>%
  filter(construct == "VR") %>%
  select(-construct)

simulator_sickness <- data_long %>%
  filter(construct == "SSQ") %>%
  select(-construct)

write.csv(subjective_stress, "opentsstvr_linnig_2025_study2_vas.csv", row.names = FALSE)
write.csv(virtual_reality_experience, "opentsstvr_linnig_2025_study2_vrexperience.csv", row.names = FALSE)
write.csv(simulator_sickness, "opentsstvr_linnig_2025_study2_ssq.csv", row.names = FALSE)
