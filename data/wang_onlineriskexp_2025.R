library(readxl)
library(tidyr)
library(dplyr)

df <- read_xlsx("journal.pone.0319700.s001.xlsx")

df$id <- seq(1, nrow(df))

df <- df %>%
  rename(cov_gender = "XB")

df_ore <- df %>%
  select(id, cov_gender, starts_with("FX")) %>%
  pivot_longer(-c(id, cov_gender),
               names_to = "item",
               values_to = "resp")

df_na <- df %>%
  select(id, cov_gender, starts_with("Na"), -"NA-M") %>%
  pivot_longer(-c(id, cov_gender),
               names_to = "item",
               values_to = "resp")

df_an <- df %>%
  select(id, cov_gender, starts_with("An"), -"Anxiety-M") %>%
  pivot_longer(-c(id, cov_gender),
               names_to = "item",
               values_to = "resp")

df_in <- df %>%
  select(id, cov_gender, starts_with("RJ")) %>%
  pivot_longer(-c(id, cov_gender),
               names_to = "item",
               values_to = "resp")

write.csv(df_ore, "wang_onlineriskexp_2025.csv", row.names = FALSE)
write.csv(df_na, "wang_onlineriskexp_2025_negativeatt.csv", row.names = FALSE)
write.csv(df_an, "wang_onlineriskexp_2025_anxiety.csv", row.names = FALSE)
write.csv(df_in, "wang_onlineriskexp_2025_interpersonalsecurity.csv", row.names = FALSE)
