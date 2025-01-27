# Data: https://osf.io/n26mb/
#  Paper: https://econtent.hogrefe.com/doi/epdf/10.1027/1015-5759/a000858
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("Final_COVIDiSTRESS_Vol2_cleaned.csv")
df <- df |>
  rename(id=ResponseId)

# ---------- Process Identity Dataset ----------
identity_df <- df |> 
  select(id, starts_with("identity"), -ends_with("midneutral"), age, gender, residing_country, relationship_status, dependents_no, live_alone)
identity_df <- pivot_longer(identity_df, cols=-c(id, age, gender, residing_country, relationship_status, dependents_no, live_alone), values_to="resp", names_to="item")
identity_df <- identity_df[!is.na(identity_df$resp), ]
colnames(identity_df) <- ifelse(
  colnames(identity_df) %in% c("id", "resp", "item"), 
  colnames(identity_df), 
  paste0("cov_", colnames(identity_df))
)

save(identity_df, file="ecps_sahm_2024_identity.rdata")
write.csv(identity_df, "ecps_sahm_2024_identity.csv", row.names=FALSE)

# ---------- Process Stree Related Dataset ----------
stress_df <- df |>
  select(id, starts_with("perceived_stress"), starts_with("primary_stressor"), starts_with("secondary_stressor"), -ends_with("Appl"), age, gender, residing_country, occupation, relationship_status, dependents_no, live_alone, covid_self)
stress_df <- pivot_longer(stress_df, cols=-c(id, age, gender, residing_country, occupation, relationship_status, live_alone, covid_self, dependents_no), values_to="resp", names_to="item")
stress_df <- stress_df[!is.na(stress_df$resp), ]
colnames(stress_df) <- ifelse(
  colnames(stress_df) %in% c("id", "resp", "item"), 
  colnames(stress_df), 
  paste0("cov_", colnames(stress_df))
)

save(stress_df, file="ecps_sahm_2024_stress.rdata")
write.csv(stress_df, "ecps_sahm_2024_stress.csv", row.names=FALSE)

# ---------- Process Perceived Support Dataset ----------
support_df <- df |>
  select(id, starts_with("perceived_support"), -ends_with("Appl"), -ends_with("midneutral"), age, gender, residing_country, occupation, relationship_status, live_alone, covid_self, dependents_no)
support_df <- pivot_longer(support_df, cols=-c(id, age, gender, residing_country, occupation, relationship_status, live_alone, covid_self, dependents_no), values_to="resp", names_to="item")
support_df <- support_df[!is.na(support_df$resp), ]
colnames(support_df) <- ifelse(
  colnames(support_df) %in% c("id", "resp", "item"), 
  colnames(support_df), 
  paste0("cov_", colnames(support_df))
)

save(support_df, file="ecps_sahm_2024_support.rdata")
write.csv(support_df, "ecps_sahm_2024_support.csv", row.names=FALSE)

# ---------- Process Staying Safe & Compliance Dataset ----------
sscd_df <- df |>
  select(id, starts_with("compliance"), starts_with("socialinfluence"), -ends_with("Appl"), age, gender, education, residing_country, relationship_status, live_alone, covid_self, dependents_no)
sscd_df <- pivot_longer(sscd_df, cols=-c(id, age, gender, education, residing_country, relationship_status, live_alone, covid_self, dependents_no), values_to="resp", names_to="item")
sscd_df <- sscd_df[!is.na(sscd_df$resp), ]
colnames(sscd_df) <- ifelse(
  colnames(sscd_df) %in% c("id", "resp", "item"), 
  colnames(sscd_df), 
  paste0("cov_", colnames(sscd_df))
)

sscd_df$item_family <- with(sscd_df, ifelse(
  grepl("^compliance", item), 1,
  ifelse(grepl("^socialinfluence_nor1", item), 2,
         ifelse(grepl("^socialinfluence_nor2", item), 3, NA)
  )
))

save(sscd_df, file="ecps_sahm_2024_sscd.rdata")
write.csv(sscd_df, "ecps_sahm_2024_sscd.csv", row.names=FALSE)

# ---------- Process Vaccine Dataset ----------
vaccine_df <- df |>
  select(id, starts_with("vaccine"), -ends_with("midneutral"), age, gender, education, residing_country,covid_self)
vaccine_df <- pivot_longer(vaccine_df, cols=-c(id, age, gender, education, residing_country,covid_self), values_to="resp", names_to="item")
vaccine_df <- vaccine_df[!is.na(vaccine_df$resp), ]
colnames(vaccine_df) <- ifelse(
  colnames(vaccine_df) %in% c("id", "resp", "item"), 
  colnames(vaccine_df), 
  paste0("cov_", colnames(vaccine_df))
)

save(vaccine_df, file="ecps_sahm_2024_vaccine.Rdata")
write.csv(vaccine_df, "ecps_sahm_2024_vaccine.csv", row.names=FALSE)

# ---------- Process Trust Dataset ----------
trust_df <- df |>
  select(id, starts_with("trust"),  age, gender, education, residing_country,covid_self)
trust_df <- pivot_longer(trust_df, cols=-c(id, age, gender, education, residing_country,covid_self), values_to="resp", names_to="item")
trust_df <- trust_df[!is.na(trust_df$resp), ]
colnames(trust_df) <- ifelse(
  colnames(trust_df) %in% c("id", "resp", "item"), 
  colnames(trust_df), 
  paste0("cov_", colnames(trust_df))
)

save(trust_df, file="ecps_sahm_2024_trust.rdata")
write.csv(trust_df, "ecps_sahm_2024_trust.csv", row.names=FALSE)

# ---------- Process Deal with Things in Life Dataset ----------
DTL_df <- df |>
  select(id, starts_with("resilience"), starts_with("uncertainty"), age, gender, education, occupation, residing_country,covid_self, live_alone)
DTL_df <- pivot_longer(DTL_df, cols=-c(id, age, gender, education, residing_country,occupation, covid_self, live_alone), values_to="resp", names_to="item")
DTL_df <- DTL_df[!is.na(DTL_df$resp), ]
colnames(DTL_df) <- ifelse(
  colnames(DTL_df) %in% c("id", "resp", "item"), 
  colnames(DTL_df), 
  paste0("cov_", colnames(DTL_df))
)

save(DTL_df, file="ecps_sahm_2024_dtlL.Rdata")
write.csv(DTL_df, "ecps_sahm_2024_dtl.csv", row.names=FALSE)

# ---------- Process Information Acquisition Dataset ----------
ia_df <- df |>
  select(id, starts_with("information"), -ends_with("TEXT"), age, gender, education, occupation, residing_country,covid_self, live_alone)
ia_df <- pivot_longer(ia_df, cols=-c(id, age, gender, education, occupation, residing_country,covid_self, live_alone), values_to="resp", names_to="item")
ia_df <- ia_df[!is.na(ia_df$resp), ]
colnames(ia_df) <- ifelse(
  colnames(ia_df) %in% c("id", "resp", "item"), 
  colnames(ia_df), 
  paste0("cov_", colnames(ia_df))
)

save(ia_df, file="ecps_sahm_2024_ia.Rdata")
write.csv(ia_df, "ecps_sahm_2024_ia.csv", row.names=FALSE)

# ---------- Process Distrust Dataset ----------
distrust_df <- df |>
  select(id, starts_with("misperception"), starts_with("conspir"), starts_with("antiex"), age, gender, education, occupation, residing_country,covid_self, live_alone)
distrust_df <- pivot_longer(distrust_df, cols=-c(id, age, gender, education, occupation, residing_country,covid_self, live_alone), values_to="resp", names_to="item")
distrust_df <- distrust_df[!is.na(distrust_df$resp), ]
colnames(distrust_df) <- ifelse(
  colnames(distrust_df) %in% c("id", "resp", "item"), 
  colnames(distrust_df), 
  paste0("cov_", colnames(distrust_df))
)

save(distrust_df, file="ecps_sahm_2024_distrust.rdata")
write.csv(distrust_df, "ecps_sahm_2024_distrust.csv", row.names=FALSE)

# ---------- Process Moral Values Dataset ----------
moral_df <- df |>
  select(id, starts_with("moral"), -ends_with("midneutral"), age, gender, education, occupation, residing_country,covid_self, live_alone)
moral_df <- pivot_longer(moral_df, cols=-c(id, age, gender, education, occupation, residing_country,covid_self, live_alone), values_to="resp", names_to="item")
moral_df <- moral_df[!is.na(moral_df$resp), ]
colnames(moral_df) <- ifelse(
  colnames(moral_df) %in% c("id", "resp", "item"), 
  colnames(moral_df), 
  paste0("cov_", colnames(moral_df))
)

save(moral_df, file="ecps_sahm_2024_moral.rdata")
write.csv(moral_df, "ecps_sahm_2024_moral.csv", row.names=FALSE)

# ---------- Process Emotions Dataset ----------
emotion_df <- df |>
  select(id, starts_with("emotion"), -ends_with("midneutral"), age, gender, education, occupation, residing_country,covid_self, live_alone)
emotion_df <- pivot_longer(emotion_df, cols=-c(id, age, gender, education, occupation, residing_country,covid_self, live_alone), values_to="resp", names_to="item")
emotion_df <- emotion_df[!is.na(emotion_df$resp), ]
colnames(emotion_df) <- ifelse(
  colnames(emotion_df) %in% c("id", "resp", "item"), 
  colnames(emotion_df), 
  paste0("cov_", colnames(emotion_df))
)

save(emotion_df, file="ecps_sahm_2024_emotion.Rdata")
write.csv(emotion_df, "ecps_sahm_2024_emotion.csv", row.names=FALSE)


##note [bd 1-8-2025]
##files edited to remove newline from some columns via the following code:
fns<-list.files(pattern="*.csv")
for (fn in fns) {
    x<-read.csv(fn)
    for (i in 1:ncol(x)) x[,i]<-gsub("\n"," ",x[,i])
    write.table(x,fn,quote=FALSE,row.names=FALSE,sep="|")
}
