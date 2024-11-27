# Data: https://osf.io/n26mb/
#  Paper: 
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("Final_COVIDiSTRESS_Vol2_cleaned.csv")
df <- df |>
  rename(id=ResponseId)

# ---------- Process Identity Dataset ----------
identity_df <- df |> 
  select(id, starts_with("identity"), -ends_with("midneutral"))
identity_df <- pivot_longer(identity_df, cols=-id, values_to="resp", names_to="item")
identity_df <- identity_df[!is.na(identity_df$resp), ]

save(identity_df, file="ECPS_Sahm_2024_Identity.Rdata")
write.csv(identity_df, "ECPS_Sahm_2024_Identity.csv", row.names=FALSE)

# ---------- Process Stree Related Dataset ----------
stress_df <- df |>
  select(id, starts_with("perceived_stress"), starts_with("primary_stressor"), starts_with("secondary_stressor"), -ends_with("Appl"))
stress_df <- pivot_longer(stress_df, cols=-id, values_to="resp", names_to="item")
stress_df <- stress_df[!is.na(stress_df$resp), ]

save(stress_df, file="ECPS_Sahm_2024_Stress.Rdata")
write.csv(stress_df, "ECPS_Sahm_2024_Stress.csv", row.names=FALSE)

# ---------- Process Perceived Support Dataset ----------
support_df <- df |>
  select(id, starts_with("perceived_support"), -ends_with("Appl"), -ends_with("midneutral"))
support_df <- pivot_longer(support_df, cols=-id, values_to="resp", names_to="item")
support_df <- support_df[!is.na(support_df$resp), ]

save(support_df, file="ECPS_Sahm_2024_Support.Rdata")
write.csv(support_df, "ECPS_Sahm_2024_Support.csv", row.names=FALSE)

# ---------- Process Staying Safe & Compliance Dataset ----------
sscd_df <- df |>
  select(id, starts_with("compliance"), starts_with("socialinfluence"), -ends_with("Appl"))
sscd_df <- pivot_longer(sscd_df, cols=-id, values_to="resp", names_to="item")
sscd_df <- sscd_df[!is.na(sscd_df$resp), ]

save(sscd_df, file="ECPS_Sahm_2024_SSCD.Rdata")
write.csv(sscd_df, "ECPS_Sahm_2024_SSCD.csv", row.names=FALSE)

# ---------- Process Vaccine Dataset ----------
vaccine_df <- df |>
  select(id, starts_with("vaccine"), -ends_with("midneutral"))
vaccine_df <- pivot_longer(vaccine_df, cols=-id, values_to="resp", names_to="item")
vaccine_df <- vaccine_df[!is.na(vaccine_df$resp), ]

save(vaccine_df, file="ECPS_Sahm_2024_Vaccine.Rdata")
write.csv(vaccine_df, "ECPS_Sahm_2024_Vaccine.csv", row.names=FALSE)

# ---------- Process Trust Dataset ----------
trust_df <- df |>
  select(id, starts_with("trust"))
trust_df <- pivot_longer(trust_df, cols=-id, values_to="resp", names_to="item")
trust_df <- trust_df[!is.na(trust_df$resp), ]

save(trust_df, file="ECPS_Sahm_2024_Trust.Rdata")
write.csv(trust_df, "ECPS_Sahm_2024_Trust.csv", row.names=FALSE)

# ---------- Process Deal with Things in Life Dataset ----------
DTL_df <- df |>
  select(id, starts_with("resilience"), starts_with("uncertainty"))
DTL_df <- pivot_longer(DTL_df, cols=-id, values_to="resp", names_to="item")
DTL_df <- DTL_df[!is.na(DTL_df$resp), ]

save(DTL_df, file="ECPS_Sahm_2024_DTL.Rdata")
write.csv(DTL_df, "ECPS_Sahm_2024_DTL.csv", row.names=FALSE)

# ---------- Process Information Acquisition Dataset ----------
ia_df <- df |>
  select(id, starts_with("information"), -ends_with("TEXT"))
ia_df <- pivot_longer(ia_df, cols=-id, values_to="resp", names_to="item")
ia_df <- ia_df[!is.na(ia_df$resp), ]

save(ia_df, file="ECPS_Sahm_2024_IA.Rdata")
write.csv(ia_df, "ECPS_Sahm_2024_IA.csv", row.names=FALSE)

# ---------- Process Distrust Dataset ----------
distrust_df <- df |>
  select(id, starts_with("misperception"), starts_with("conspir"), starts_with("antiex"))
distrust_df <- pivot_longer(distrust_df, cols=-id, values_to="resp", names_to="item")
distrust_df <- distrust_df[!is.na(distrust_df$resp), ]

save(distrust_df, file="ECPS_Sahm_2024_Distrust.Rdata")
write.csv(distrust_df, "ECPS_Sahm_2024_Distrust.csv", row.names=FALSE)

# ---------- Process Moral Values Dataset ----------
moral_df <- df |>
  select(id, starts_with("moral"), -ends_with("midneutral"))
moral_df <- pivot_longer(moral_df, cols=-id, values_to="resp", names_to="item")
moral_df <- moral_df[!is.na(moral_df$resp), ]

save(moral_df, file="ECPS_Sahm_2024_Moral.Rdata")
write.csv(moral_df, "ECPS_Sahm_2024_Moral.csv", row.names=FALSE)

# ---------- Process Emotions Dataset ----------
emotion_df <- df |>
  select(id, starts_with("emotion"), -ends_with("midneutral"))
emotion_df <- pivot_longer(emotion_df, cols=-id, values_to="resp", names_to="item")
emotion_df <- emotion_df[!is.na(emotion_df$resp), ]

save(emotion_df, file="ECPS_Sahm_2024_Emotion.Rdata")
write.csv(emotion_df, "ECPS_Sahm_2024_Emotion.csv", row.names=FALSE)