library(dplyr)
library(tidyr)

df <- readRDS('data_from_excel_12_2_2020.rds') %>%
  rename(id = ID)

df <- df %>%
  rename_with(~ paste0("cov_", .), c("Gender", "Age", "Family_status", "Education", "Economical_status"))

df_TEQ <- df %>%
  select(id, cov_Gender, cov_Age, cov_Family_status, cov_Education, cov_Economical_status, TEQ_1:TEQ_16) %>%
  pivot_longer(TEQ_1:TEQ_16, names_to = "item", values_to = "resp") %>%
  filter(!is.na(resp))

df_SocDes <- df %>%
  select(id, cov_Gender, cov_Age, cov_Family_status, cov_Education, cov_Economical_status, SocDes_1:SocDes_5) %>%
  pivot_longer(SocDes_1:SocDes_5, names_to = "item", values_to = "resp") %>%
  filter(!is.na(resp))

df_selfEsteem <- df %>%
  select(id, cov_Gender, cov_Age, cov_Family_status, cov_Education, cov_Economical_status, Self_esteem_1:Self_esteem_10) %>%
  pivot_longer(Self_esteem_1:Self_esteem_10, names_to = "item", values_to = "resp") %>%
  filter(!is.na(resp))

df_BFIN <- df %>%
  select(id, cov_Gender, cov_Age, cov_Family_status, cov_Education, cov_Economical_status, BFIN_1:BFIN_8) %>%
  pivot_longer(BFIN_1:BFIN_8, names_to = "item", values_to = "resp") %>%
  filter(!is.na(resp))

df_Spirit <- df %>%
  select(id, cov_Gender, cov_Age, cov_Family_status, cov_Education, cov_Economical_status, SPIRIT_1:SPIRIT_15) %>%
  pivot_longer(SPIRIT_1:SPIRIT_15, names_to = "item", values_to = "resp") %>%
  filter(!is.na(resp))

df_SCBCS <- df %>%
  select(id, cov_Gender, cov_Age, cov_Family_status, cov_Education, cov_Economical_status, SCBCS_1:SCBCS_5) %>%
  pivot_longer(SCBCS_1:SCBCS_5, names_to = "item", values_to = "resp") %>%
  filter(!is.na(resp))

write.csv(df_TEQ, "teq_novak_2021_teq.csv", row.names=FALSE)
write.csv(df_Spirit, "teq_novak_2021_spirit.csv", row.names=FALSE)
write.csv(df_SocDes, "teq_novak_2021_socdes.csv", row.names=FALSE)
write.csv(df_selfEsteem, "teq_novak_2021_selfesteem.csv", row.names=FALSE)
write.csv(df_SCBCS, "teq_novak_2021_scbs.csv", row.names=FALSE)
write.csv(df_BFIN, "teq_novak_2021_bfin.csv", row.names=FALSE)
 