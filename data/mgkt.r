# Paper
# Data: https://openpsychometrics.org/_rawdata/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("data.csv", header = TRUE, sep = ",")
df$id <- seq_len(nrow(df))
df <- df |>
  rename(cov_age=age, cov_engnat=engnat, cov_gender=gender, cov_country=country) |>
  select(id, starts_with("cov"), starts_with("Q"), -ends_with("I"), -ends_with("A"))

df <- df |>
  mutate(across(ends_with("E") & starts_with("Q"), ~ .x / 1000))
df_long <- df |>
  pivot_longer(
    cols = matches("^Q\\d+[SE]$"),  # Select columns like Q1S, Q2E, ...
    names_to = c("item", "type"),
    names_pattern = "Q(\\d+)([SE])",
    values_to = "value"
  ) |>
  pivot_wider(
    names_from = type,
    values_from = value,
    names_prefix = "resp_"
  ) |>
  mutate(item = paste0("Q", item))
df_long <- df_long |>
  rename(resp=resp_S, rt=resp_E)

write.csv(df_long, paste0("mgkt", ".csv"), row.names = FALSE)
save(df_long, file = paste0("mgkt", ".RData"))