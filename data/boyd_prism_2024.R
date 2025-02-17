library(dplyr)
library(tidyr)

df <- readRDS("prism_cfa.RDS")

df$id <- 1:nrow(df)

df <- df %>%
  mutate(across(where(haven::is.labelled), as.character))

df <- df %>%
  select(-c("Year", "Often", "Platform")) %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp",
               values_drop_na = T)

write.csv(df, "boyd_prism_2024.csv", row.names=FALSE)
