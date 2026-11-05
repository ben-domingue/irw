library(dplyr)
library(tidyr)
library(haven)

# PTCI_data.sav from https://osf.io/tj8rh/ (file qr6ae)
data <- read_sav("PTCI_data.sav")

# One row per respondent. `ID` is NOT a person key: it restarts across the three
# samples (C2: senior / high / adult) and repeats inside them too, pairing people
# of different sex, age and answers (irw#3237). So `id` is the row, and the
# deposit's own ID and sample stay as covariates.
data <- data %>%
  zap_labels() %>%
  mutate(id = row_number(),
         cov_source_id = ID,
         cov_group = c("senior", "high", "adult")[C2]) %>%
  rename(cov_sex = sex,
         cov_age = age,
         cov_location = location) %>%
  select(id, cov_age, cov_sex, cov_location, cov_group, cov_source_id, starts_with("ptci")) %>%
  pivot_longer(
    cols = starts_with("ptci"),
    names_to = "item",
    values_to = "resp")

write.csv(data, "ptcichina_zhan_2024.csv", row.names = FALSE, na = "")
