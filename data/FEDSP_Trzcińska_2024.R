# Paper: https://www.sciencedirect.com/science/article/pii/S002209652400153X?casa_token=frUv3Kl3eTIAAAAA:YYuVvzzbk5DFpvFlUAO2XvfWd3qnt6ToOT46ExDaabGezuZsA4-MWgt_stLyebZaZ6EUrsIq
# Data: https://osf.io/sa87b/
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav("data-3.sav")
df <- df |>
  rename(id = number)
df <- df[!is.na(df$child_age_in_months) & !is.na(df$c_PSIAT), ]
df[] <- lapply(df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

# ------ Process PRD Dataset ------
prd_df <- df |>
  select(id, starts_with("p_personal_rel_dep"), -ends_with("R"))
prd_df <- pivot_longer(prd_df, cols=-id, names_to="item", values_to="resp")

save(prd_df, file="FEDSP_Trzcinska_2023_PRD.Rdata")
write.csv(prd_df, "FEDSP_Trzcinska_2023_PRD.csv", row.names=FALSE)

# ------ Process PSPCSA Dataset ------
pspcsa_df <- df |>
  select(id, starts_with("c_PSPCSA"), -c_PSPCSA)
pspcsa_test_df <- pspcsa_df |>
  select(-ends_with("r"))
pspcsa_retest_df <- pspcsa_df |>
  select(id, ends_with("r"))
colnames(pspcsa_retest_df) <- gsub("r", "", colnames(pspcsa_retest_df))

pspcsa_test_df <- pivot_longer(pspcsa_test_df, cols=-id, names_to="item", values_to="resp")
pspcsa_retest_df <- pivot_longer(pspcsa_retest_df, cols=-id, names_to="item", values_to="resp")
pspcsa_test_df$wave <- 0
pspcsa_retest_df$wave <- 1

pspcsa_df <- rbind(pspcsa_test_df, pspcsa_retest_df)

save(pspcsa_df, file="FEDSP_Trzcinska_2023_PSPCSA.Rdata")
write.csv(pspcsa_df, "FEDSP_Trzcinska_2023_PSPCSA.csv", row.names=FALSE)

# ------ Process SMSD Dataset ------
smsd_df <- df |>
  select(id, starts_with("p_SMSD"), -ends_with("R"), -ends_with("total"))
smsd_df <- pivot_longer(smsd_df, cols=-id, names_to="item", values_to="resp")

save(smsd_df, file="FEDSP_Trzcinska_2023_SMSD.Rdata")
write.csv(smsd_df, "FEDSP_Trzcinska_2023_SMSD.csv", row.names=FALSE)

# ------ Process MonKnow Dataset ------
monknow_df <- df |>
  select(id, starts_with("c_MonKnow_"))
monknow_df <- pivot_longer(monknow_df, cols=-id, names_to="item", values_to="resp")

save(monknow_df, file="FEDSP_Trzcinska_2023_MonKonw.Rdata")
write.csv(monknow_df, "FEDSP_Trzcinska_2023_MonKnow.csv", row.names=FALSE)
