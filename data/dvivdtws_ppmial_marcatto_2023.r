# Paper:
# Data: https://osf.io/8mj73/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

study_df <- read.csv("data.csv",sep = ";")
study_df <- study_df |>
  mutate(id= row_number())

# ---------- Process DTW Dataset ----------
dtw_df <- study_df %>%
  select(starts_with("dtw"), id, Gender, Age, Language)
dtw_df  <- remove_na(dtw_df)
dtw_df <- pivot_longer(dtw_df, cols=-c(id, Gender, Age, Language), names_to="item", values_to="resp")
dtw_df <- dtw_df |>
  rename(cov_gender = Gender, cov_age = Age, cov_language = Language)

save(dtw_df, file="dvivdtws_ppmial_marcatto_2023_dtw.Rdata")
write.csv(dtw_df, "dvivdtws_ppmial_marcatto_2023_dtw.csv", row.names=FALSE)

# ---------- Process OCS Dataset ----------
OCS_df <- study_df %>%
  select(starts_with("OCS"), id, Gender, Age, Language)
OCS_df <- remove_na(OCS_df)
OCS_df <- pivot_longer(OCS_df, cols=-c(id, Gender, Age, Language), names_to="item", values_to="resp")
OCS_df <- OCS_df |>
  rename(cov_gender = Gender, cov_age = Age, cov_language = Language)

save(dtw_df, file="dvivdtws_ppmial_marcatto_2023_ocs.Rdata")
write.csv(dtw_df, "dvivdtws_ppmial_marcatto_2023_ocs.csv", row.names=FALSE)

# ---------- Process OCB Dataset ----------
OCB_df <- study_df %>%
  select(starts_with("OCB"), id, Gender, Age, Language)
OCB_df <- remove_na(OCB_df)
OCB_df <- pivot_longer(OCB_df, cols=-c(id, Gender, Age, Language), names_to="item", values_to="resp")
OCB_df <- OCB_df |>
  rename(cov_gender = Gender, cov_age = Age, cov_language = Language)

save(dtw_df, file="dvivdtws_ppmial_marcatto_2023_ocb.Rdata")
write.csv(dtw_df, "dvivdtws_ppmial_marcatto_2023_ocb.csv", row.names=FALSE)

# ---------- Process CWB Dataset ----------
CWB_df <- study_df %>%
  select(starts_with("CWB"), id, Gender, Age, Language)
CWB_df <- remove_na(CWB_df)
CWB_df <- pivot_longer(CWB_df, cols=-c(id, Gender, Age, Language), names_to="item", values_to="resp")
CWB_df <- CWB_df |>
  rename(cov_gender = Gender, cov_age = Age, cov_language = Language)

save(dtw_df, file="dvivdtws_ppmial_marcatto_2023_cwb.Rdata")
write.csv(dtw_df, "dvivdtws_ppmial_marcatto_2023_cwb.csv", row.names=FALSE)

# ---------- Process SNAQ Dataset ----------
SNAQ_df <- study_df %>%
  select(starts_with("SNAQ"), id, Gender, Age, Language)
SNAQ_df <- remove_na(SNAQ_df)
SNAQ_df <- pivot_longer(SNAQ_df, cols=-c(id, Gender, Age, Language), names_to="item", values_to="resp")
SNAQ_df <- SNAQ_df |>
  rename(cov_gender = Gender, cov_age = Age, cov_language = Language)


save(dtw_df, file="dvivdtws_ppmial_marcatto_2023_snaq.Rdata")
write.csv(dtw_df, "dvivdtws_ppmial_marcatto_2023_snaq.csv", row.names=FALSE)