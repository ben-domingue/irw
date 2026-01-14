library(dplyr)
library(haven)

data <- read_sav("PTCI_data.sav")

data <- data%>%
  rename(cov_sex = sex,
         cov_age = age,
         cov_location = location,
         id = ID)

data <- data %>%
  zap_labels()%>%
  select(id, starts_with("cov_"), starts_with("ptci")) %>%
  pivot_longer(
    cols = starts_with("ptci"),
    names_to = "item",
    values_to = "resp")

write.csv(data, "ptcichina_zhan_2024.csv", row.names = FALSE)