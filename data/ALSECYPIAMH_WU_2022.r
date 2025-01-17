Data: https://osf.io/jqzbx/
  Paper: 
  library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}


preStudy_df <- read_sav("CPS Pre-Study.sav")
study1 <- read_sav("CPS Study 1.sav")
study2 <- read_sav("CPS Study 2.sav")

preStudy_df [] <- lapply(preStudy_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

study1[] <- lapply(study1, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

study2[] <- lapply(study2, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

preStudy_df <- preStudy_df|>
  rename(id=PID)
study1 <- study1|>
  rename(id=PID)
study2 <- study2|>
  rename(id=PID)

# ---------- Process CPS Datasets ----------
CPS_PRE_df <- preStudy_df |>
  select(starts_with("CPS"), id)
colnames(CPS_PRE_df) <- c("CPS_BS1", "CPS_BS2", "CPS_BS3", "CPS_BS4", "CPS_GD1", "CPS_GD2", "CPS_GD3", "CPS_GD4", "CPS_M1", "CPS_M2", "CPS_M3",  "CPS_M4", "id")
CPS_PRE_df <- remove_na(CPS_PRE_df)
CPS_PRE_df  <- pivot_longer(CPS_PRE_df, cols=-c(id), names_to="item", values_to="resp")

CPS_Study1_df <- study1 |>
  select(starts_with("CPS"), id)
CPS_Study1_df  <- remove_na(CPS_Study1_df)
CPS_Study1_df <- pivot_longer(CPS_Study1_df, cols=-c(id), names_to="item", values_to="resp")

CPS_Study2_df <- study2 |>
  select(starts_with("CPS"), id)
CPS_Study2_df <- remove_na(CPS_Study2_df)
CPS_Study2_df <- CPS_Study2_df |>
  select(-CPS, -CPS_M, -CPS_GD, -CPS_BTS)
CPS_Study2_df <- pivot_longer(CPS_Study2_df, cols=-c(id), names_to="item", values_to="resp")


CPS_PRE_df $ group <- "pre_study"
CPS_Study1_df $ group <- "study1"
CPS_Study2_df $ group <- "study2"

CPS_df <- rbind(CPS_PRE_df,CPS_Study1_df,CPS_Study2_df )

save(CPS_df, file="ALSECYPIAMH_WU_2022_CPS.Rdata")
write.csv(CPS_df, "ALSECYPIAMH_WU_2022_CPS.csv", row.names=FALSE)

# ---------- Process SDQ Datasets ----------
SDQ_df <- study2 |>
  select(starts_with("SDQ"), id)
SDQ_df <- remove_na(SDQ_df)
SDQ_df <- pivot_longer(SDQ_df, cols=-c(id), names_to="item", values_to="resp")

save(SDQ_df, file="ALSECYPIAMH_WU_2022_SDQ.Rdata")
write.csv(SDQ_df, "ALSECYPIAMH_WU_2022_SDQ.csv", row.names=FALSE)

# ---------- Process SWEMBS Datasets ----------
SWEMWBS_df <- study2 |>
  select(starts_with("SWEMWBS"), id, -SWEMWBS)
SWEMWBS_df <- remove_na(SWEMWBS_df)
SWEMWBS_df <- pivot_longer(SWEMWBS_df, cols=-c(id), names_to="item", values_to="resp")

save(SWEMWBS_df, file="ALSECYPIAMH_WU_2022_SWEMWBS.Rdata")
write.csv(SWEMWBS_df, "ALSECYPIAMH_WU_2022_SWEMWBS.csv", row.names=FALSE)

# ---------- Process SWLS Datasets ----------
SWLS_df <- study2 |>
  select(starts_with("SWLS"), id, -SWLS)
SWLS_df <- remove_na(SWLS_df)
SWLS_df <- pivot_longer(SWLS_df, cols=-c(id), names_to="item", values_to="resp")

save(SWLS_df, file="ALSECYPIAMH_WU_2022_SWLS.Rdata")
write.csv(SWLS_df, "ALSECYPIAMH_WU_2022_SWLS.csv", row.names=FALSE)

# ---------- Process PEI Datasets ----------
PEI_df <- study2 |>
  select(starts_with("PEI"), id)
PEI_df <- remove_na(PEI_df)
PEI_df <- PEI_df |>
  select(-PEI)
PEI_df <- pivot_longer(PEI_df, cols=-c(id), names_to="item", values_to="resp")

save(PEI_df, file="ALSECYPIAMH_WU_2022_PEI.Rdata")
write.csv(PEI_df, "ALSECYPIAMH_WU_2022_PEI.csv", row.names=FALSE)

# ---------- Process NEI Datasets ----------
NEI_df <- study2 |>
  select(starts_with("NEI"), id)
NEI_df <- remove_na(NEI_df)
NEI_df <- NEI_df |>
  select(-NEI)
NEI_df <- pivot_longer(NEI_df, cols=-c(id), names_to="item", values_to="resp")

save(NEI_df, file="ALSECYPIAMH_WU_2022_NEI.Rdata")
write.csv(NEI_df, "ALSECYPIAMH_WU_2022_NEI.csv", row.names=FALSE)

# ---------- Process PHQ Datasets ----------
PHQ_df <- study2 |>
  select(starts_with("PHQ"), id)
PHQ_df <- remove_na(PHQ_df)
PHQ_df <- pivot_longer(PHQ_df, cols=-c(id), names_to="item", values_to="resp")

save(PHQ_df, file="ALSECYPIAMH_WU_2022_PHQ.Rdata")
write.csv(PHQ_df, "ALSECYPIAMH_WU_2022_PHQ.csv", row.names=FALSE)

# ---------- Process Empathy Datasets ----------
Empathy_df <- study2 |>
  select(starts_with("Empathy"), id, -ends_with("r"),-Empathy)
Empathy_df <- remove_na(Empathy_df)
Empathy_df <- pivot_longer(Empathy_df, cols=-c(id), names_to="item", values_to="resp")

save(Empathy_df, file="ALSECYPIAMH_WU_2022_Empathy.Rdata")
write.csv(Empathy_df, "ALSECYPIAMH_WU_2022_Empathy.csv", row.names=FALSE)

# ---------- Process MIL Datasets ----------
MIL_df <- study2 |>
  select(starts_with("MIL"), id)
MIL_df <- remove_na(MIL_df)
MIL_df <- pivot_longer(MIL_df, cols=-c(id), names_to="item", values_to="resp")

save(MIL_df, file="ALSECYPIAMH_WU_2022_MIL.Rdata")
write.csv(MIL_df, "ALSECYPIAMH_WU_2022_MIL.csv", row.names=FALSE)

# ---------- Process PIL Datasets ----------
PIL_df <- study2 |>
  select(starts_with("PIL"), id)
PIL_df <- remove_na(PIL_df)
PIL_df <- PIL_df |>
  select(-PIL)
PIL_df <- pivot_longer(PIL_df, cols=-c(id), names_to="item", values_to="resp")

save(PIL_df, file="ALSECYPIAMH_WU_2022_PIL.Rdata")
write.csv(PIL_df, "ALSECYPIAMH_WU_2022_PIL.csv", row.names=FALSE)