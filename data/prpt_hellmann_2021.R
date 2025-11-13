library(dplyr)

uk<- read_delim("PRPT_Data_UK.csv", 
                   ";", escape_double = FALSE, trim_ws = TRUE)
germany <- read_delim("PRPT_Data_Germany.csv", 
                    ",", escape_double = FALSE, trim_ws = TRUE)

names(germany) <- names(germany) |>
  gsub("^BM01_", "RT01_", x = _) |>   # Realistic Threat
  gsub("^KR01_", "CR01_", x = _) |>   # Fear of Crime - part 1
  gsub("^KR02_", "CR02_", x = _) |>   # Fear of Crime - part 2
  gsub("^GE01_", "CO01_", x = _) |>   # Conscientiousness
  gsub("^LE01_", "AM01_", x = _)      # Achievement Motivation

uk <- uk%>%
  mutate(cov_country = "UK",
         id = paste(cov_country, CASE, sep = "_"))

germany <- germany%>%
  mutate(cov_country = "Germany",
         id = paste(cov_country, ...1, sep = "_"))

shared_cols <- intersect(names(uk), names(germany))
data <- rbind(uk[shared_cols], germany[shared_cols])
data <- data %>%
  rename(cov_gender = DE01,
       cov_age = DE02_01,
       cov_nationality = DE03)

pivot_scale <- function(data, prefix) {
  data %>%
    select(id, starts_with("cov_"),starts_with(prefix)) %>%
    pivot_longer(
      cols = -c(id, starts_with("cov_")),
      names_to = "item",
      values_to = "resp"
    )
}
scale_names <- c(
  RT = "realisticthreat",
  CR = "fearofcrime",
  TH = "threat",
  CO = "conscientiousness",
  AM = "achievementmotive",
  SE = "selfesteem"
)

scales <- c("RT", "CR", "TH","CO","AM","SE")
  
for (scale in scales) {
  data_sub <- pivot_scale(data, scale)%>%
    filter(resp != -9)
  write.csv(data_sub, paste0("prpt_hellmann_2021_", scale_names[scale], ".csv"), row.names = FALSE)
}