# Paper: https://osf.io/preprints/psyarxiv/du6ah
# Data: https://osf.io/vmy4q/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("PDP_data.csv")
df <- df |>
  mutate(id = row_number()) |>
  select(-starts_with("AC"), -education, -age, -gender)

# ------ Process PDP-dilemmas Dataset ------
pdp_df <- df |>
  select(ends_with("_C"), ends_with("_IC"), id)
pdp_df <- pivot_longer(pdp_df, cols=-id, names_to="item", values_to="resp")

##bd edit: 1/2 responses converted to 0/1
save(pdp_df, file="CPDMMC_Kunnari_2020_PDP.Rdata")
write.csv(pdp_df, "CPDMMC_Kunnari_2020_PDP.csv", row.names=FALSE)

# ------ Process High-conflict Dilemmas Dataset ------
hcd_df <- df |>
  select(-ends_with("_C"), -ends_with("_IC"))
hcd_df <- pivot_longer(hcd_df, cols=-id, names_to="item", values_to="resp")

save(hcd_df, file="CPDMMC_Kunnari_2020_HCD.Rdata")
write.csv(hcd_df, "CPDMMC_Kunnari_2020_HCD.csv", row.names=FALSE)
