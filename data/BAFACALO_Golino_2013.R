# Paper: https://openpsychologydata.metajnl.com/articles/10.5334/jopd.af
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/23150
library(tidyr)
library(dplyr)

load("BAFACALO_DATASET.RData")
df <- BAFACALO_DATASET
df <- df |> # Remove demographic data columns
  select(-scholarity_father, -scholarity_mother, 
         -household_income, -previous_school_type,
         -sex, -class_number) |>
  select(-N, -P1, -P2, -P3, -FF, -FI1, -FI2, # Remove aggregate statistics
         -portuguese, -english, -math, -biology, -physics, 
         -chimestry, -geography, -history) |>
  rename(id=participant_id)

FIS_df <- df %>%
  select(id, age, starts_with("Ii"), starts_with("RLi"), starts_with("RGi"))

CIS_df <- df %>%
  select(id, age, starts_with("V1i"), starts_with("V2i"), starts_with("V3i"))
CIS_df <- CIS_df %>% # Mutate column value types for merging purpose
  mutate(across(-c(id, age), as.double)) 

SMS_df <- df %>%
  select(id, age, starts_with("MA1i"), starts_with("MA2i"), starts_with("Mvi")) 
SMS_df <- SMS_df %>% # Mutate column value types for merging purpose
  mutate(across(-c(id, age), as.double)) 

BVPS_df <- df %>%
  select(id, age, starts_with("VZi"), starts_with("CFi")) 
BVPS_df <- BVPS_df %>% # Mutate column value types for merging purpose
  mutate(across(-c(id, age), as.double)) 

FIS_df <- pivot_longer(FIS_df, cols=-c(id, age), names_to='item', values_to='resp')
CIS_df <- pivot_longer(CIS_df, cols=-c(id, age), names_to='item', values_to='resp')
SMS_df <- pivot_longer(SMS_df, cols=-c(id, age), names_to='item', values_to='resp')
BVPS_df <- pivot_longer(BVPS_df, cols=-c(id, age), names_to='item', values_to='resp')

save(FIS_df, file="BAFACALO_Golino_2013_FIS.Rdata")
save(CIS_df, file="BAFACALO_Golino_2013_CIS.Rdata")
save(SMS_df, file="BAFACALO_Golino_2013_SMS.Rdata")
save(BVPS_df, file="BAFACALO_Golino_2013_BVPS.Rdata")
write.csv(FIS_df, "BAFACALO_Golino_2013_FIS.csv", row.names=FALSE)
write.csv(CIS_df, "BAFACALO_Golino_2013_CIS.csv", row.names=FALSE)
write.csv(SMS_df, "BAFACALO_Golino_2013_SMS.csv", row.names=FALSE)
write.csv(BVPS_df, "BAFACALO_Golino_2013_BVPS.csv", row.names=FALSE)
