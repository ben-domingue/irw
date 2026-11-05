library(dplyr)
library(tidyr)

# CRS_dec.csv from the PsychArchives deposit (Więsyk et al. 2024)
data <- read.csv2("CRS_dec.csv", fileEncoding = "UTF-8-BOM")

# One row per respondent. `ID` is NOT a person key: it restarts in each of the six
# samples (`SET`, A-F) and set F holds pairs that share an ID (irw#3237). So `id`
# is the row, and the deposit's own ID and set stay as covariates.
data <- data %>%
  mutate(id = row_number(),
         cov_set = SET,
         cov_source_id = ID) %>%
  rename(cov_sex = sex,
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
  write.csv(data_sub, paste0("crspolish_wiesyk_2024_", tolower(scale), ".csv"), row.names = FALSE, na = "")
}
