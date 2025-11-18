library(dplyr)
library(haven)

data <- read.csv2("CRS_dec.csv")

data <- data%>%
  rename(id = ID,
         cov_sex = sex,
         cov_country = COUNTRY)

pivot_scale <- function(data, prefix) {
  data %>%
    select(id, starts_with("cov_"), matches(paste0("^", prefix, "_\\d+$"))) %>%
    pivot_longer(
      cols = starts_with(prefix),
      names_to = "item",
      values_to = "resp"
    )
}

scales <- c("CRS", "enrich", "p_stress","lie")

for (scale in scales) {
  data_sub <- pivot_scale(data, scale)
  write.csv(data_sub, paste0("crspolish_więsyk_2024_", scale, ".csv"), row.names = FALSE)
}