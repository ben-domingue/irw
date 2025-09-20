setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)

df <- readRDS("data.rds")

items <- c("own.ccb", "other.ccb.main", "other.ccb.part",
          "other.ccb.attr", "other.ccb.trend", "other.ccb.know",
          "discuss", "exp.change.high", "exp.change.low",
          "own.change", "exp.support.high", "exp.support.low",
          "own.support", "efficacy")

df_long <- df %>%
  # convert factor/ordered factor items to numeric
  mutate(
    own.ccb = as.numeric(as.character(own.ccb)),
    discuss = as.numeric(as.character(discuss)),
    own.change = as.numeric(as.character(own.change)),
    own.support = as.numeric(as.character(own.support)),
    efficacy = as.numeric(as.character(efficacy))
  ) %>%
  # Replace 999 with NA 
  mutate(efficacy = ifelse(efficacy == 999, NA, efficacy)) %>%
  # cond -> treat
  mutate(
    treat = case_when(
      cond == "Intervention" ~ 1,
      cond == "Control" ~ 0,
      TRUE ~ NA_real_
    )
  ) %>%
  rename(id = ID, cov_age = age, cov_gender = sex) %>%
  pivot_longer(
    cols = all_of(items),
    names_to  = "item",
    values_to = "resp"
  ) %>%
  select(id, cov_age, cov_gender, treat, item, resp)

write_csv(df_long, "climatechange_geiger_2025.csv")
