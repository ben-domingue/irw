library(tidyr)
library(dplyr)

df <- read.csv("Smoking Perseverance Data.csv")

df <- df %>%
  select(-c("Day", "Hour")) %>%
  pivot_longer(c("i44":"i47"),
               names_to = "item",
               values_to = "resp")

colnames(df) <- tolower(colnames(df))

df$date <- df$time * 3600

df <- df %>%
  select(id, item, resp, date)

write.csv(df, "smoking_perseverance_mcneish_2025.csv", row.names = FALSE)
