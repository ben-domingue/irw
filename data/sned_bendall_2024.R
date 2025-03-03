library(tidyr)
library(dplyr)

df <- read.csv("ProlificDemographicsAllWithScalesOSFAnonomysed.csv")

colnames(df)

df <- df %>%
  select(-c("Started.at", "Completed.at", "Reviewed.at", "Archived.at", "ProlificBatch")) %>%
  rename(id = "ParticipantPrivateID", 
         rt = "Time.taken", 
         cov_age = "Age", 
         cov_gender = "GenderIdentity",
         cov_ethnicity = "Ethnicity.simplified",
         cov_countryofbirth = "Country.of.birth",
         cov_countryofresidence = "Country.of.residence",
         cov_nationality = "Nationality",
         cov_education = "Education") %>%
  pivot_longer(c("RULiving", "RULeisureRural", "RULeisureUrban", "RULocation", "RUMostTime", "MacArthur"),
               names_to = "item",
               values_to = "resp")

write.csv(df, "sned_bendall_2024.csv", row.names = FALSE)
