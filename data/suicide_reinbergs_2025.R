library(dplyr)
library(haven)


data <- readRDS("mdss-data-public.Rds") 
data <- data%>%
  mutate(id = row_number())%>%
  rename(cov_gender = gender,
         cov_race = race_fixed,
         cov_trans = trans1,
         cov_locale = locale,
         cov_orientation = orientation,
         cov_income = income,
         cov_kid = kid)

pivot_scale <- function(data, prefix) {
  data %>%
    zap_labels()%>%
    select(id, starts_with("cov_"), matches(paste0("^", prefix, "\\d+$"))) %>%
    pivot_longer(
      cols = starts_with(prefix),
      names_to = "item",
      values_to = "resp"
    )
}

scales <- c("phq", "gad", "stig","soss", "ghsq", "mpfi","stosa","sbqr","dssm")


for (scale in scales) {
  data_sub <- pivot_scale(data, scale)
  write.csv(data_sub, paste0("suicide_reinbergs_2025_", scale, ".csv"), row.names = FALSE)
}
