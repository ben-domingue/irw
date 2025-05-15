library(dplyr)
library(tidyr)

df <- read.csv("data.csv")

df$id <- seq(1, nrow(df))

df <- df %>%
  rename(cov_gender = gender, cov_age = age) %>%
  select(id, starts_with("cov"), Q1:Q40) %>%
  pivot_longer(Q1:Q40,
               names_to = "item",
               values_to = "resp")

write.csv(df, "narcissistic_personality_inventory.csv", row.names = FALSE)
