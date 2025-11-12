library(dplyr)
library(stringr)
library(readr)


data1 <- read.csv2('Open_TSST_VR_data_study_1.csv', header = TRUE)

data1 <- data1 %>%
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
  ) %>% 
  mutate(
    cov_sex = 1,
    cov_order = NA,
    study  = 1,
    id = paste(study, id, sep = "_")
  )

data2 <- read.csv2('Open_TSST_VR_data_study_2.csv', header = TRUE)

data2 <- data2 %>%
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
  mutate(cov_order = as.integer(factor(cov_order)),
         study  = 2,
         id = paste(study, id, sep = "_"))

common_cols <- intersect(names(data1), names(data2))
data <- bind_rows(data1[, common_cols], data2[, common_cols])

data_long <- data %>%
  pivot_longer(
    cols = -c(treat, id, starts_with("cov_"), study),
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
  select(-construct)%>%
  filter(grepl("[0-9]", item))

simulator_sickness <- data_long %>%
  filter(construct == "SSQ") %>%
  select(-construct)%>%
  filter(grepl("[0-9]", item))

write.csv(subjective_stress, "opentsstvr_linnig_2025_vas.csv", row.names = FALSE)
write.csv(virtual_reality_experience, "opentsstvr_linnig_2025_vrexperience.csv", row.names = FALSE)
write.csv(simulator_sickness, "opentsstvr_linnig_2025_ssq.csv", row.names = FALSE)

