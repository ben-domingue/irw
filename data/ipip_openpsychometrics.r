# Paper
# Data: https://openpsychometrics.org/_rawdata/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("data.csv")
df$id <- seq_len(nrow(df))
df <- df |>
  rename(cov_age=age, cov_gender=gender)

common_cols = c("id", "cov_age", "cov_gender")
# ---------- Assertiveness ----------
as_df <- df |>
  select(common_cols, starts_with("AS"))
as_df <- pivot_longer(as_df, cols=-common_cols, values_to="resp", names_to="item")
as_df <- as_df[as_df$resp != 0, ]

write.csv(as_df, paste0("ipip_openpsychometrics_as", ".csv"), row.names = FALSE)
save(as_df, file = paste0("ipip_openpsychometrics_as", ".RData"))
# ---------- Social Confidence ----------
sc_df <- df |>
  select(common_cols, starts_with("SC"))
sc_df <- pivot_longer(sc_df, cols=-common_cols, values_to="resp", names_to="item")
sc_df <- sc_df[sc_df$resp != 0, ]

write.csv(sc_df, paste0("ipip_openpsychometrics_sc", ".csv"), row.names = FALSE)
save(sc_df, file = paste0("ipip_openpsychometrics_sc", ".RData"))
# ---------- Adventurousness ----------
ad_df <- df |>
  select(common_cols, starts_with("AD"))
ad_df <- pivot_longer(ad_df, cols=-common_cols, values_to="resp", names_to="item")
ad_df <- ad_df[ad_df$resp != 0, ]

write.csv(ad_df, paste0("ipip_openpsychometrics_ad", ".csv"), row.names = FALSE)
save(ad_df, file = paste0("ipip_openpsychometrics_ad", ".RData"))
# ---------- Dominance ----------
do_df <- df |>
  select(common_cols, starts_with("DO"))
do_df <- pivot_longer(do_df, cols=-common_cols, values_to="resp", names_to="item")
do_df <- do_df[do_df$resp != 0, ]

write.csv(do_df, paste0("ipip_openpsychometrics_do", ".csv"), row.names = FALSE)
save(do_df, file = paste0("ipip_openpsychometrics_do", ".RData"))