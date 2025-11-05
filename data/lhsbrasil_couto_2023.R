library(dplyr)
library(haven)

data <- readRDS("lhs_br.rds") 
data <- data%>%
  rename(cov_gender = gender,
         cov_age = age,
         cov_income = monthly.income,
         cov_education = education,
         cov_state = state)

pivot_scale <- function(data, prefix) {
  data %>%
    zap_labels()%>%
    select(id, starts_with("cov_"), starts_with(prefix)) %>%
    pivot_longer(
      cols = starts_with(prefix),
      names_to = "item",
      values_to = "resp"
    )
}

scales <- c("SES", "PSS", "LHS")

for (scale in scales) {
  data_sub <- pivot_scale(data, scale)
  write.csv(data_sub, paste0("lhsbrasil_couto_2023_", tolower(scale), ".csv"), row.names = FALSE)
}