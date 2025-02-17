# Paper: https://pubmed.ncbi.nlm.nih.gov/31665694/
# Data: https://osf.io/3ba2z/
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

data_df <- read.csv("scl90_osf.csv")
data_df <- data_df |>
  mutate(id=row_number())
data_df <- data_df |>
  rename(cov_gender=gender, cov_age=age, cov_VEM_diagnosis_general=VEM.diagnosis.general)

SCL_df <- data_df %>%
  select(starts_with("SCL", ignore.case = FALSE), id, cov_gender, cov_VEM_diagnosis_general, cov_age)
SCL_df <- remove_na(SCL_df)
SCL_df <- pivot_longer(SCL_df, cols=-c(id, cov_gender,cov_VEM_diagnosis_general, cov_age), names_to="item", values_to="resp")
SCL_df$resp <- as.numeric(SCL_df$resp)
SCL_df$resp <- ifelse(SCL_df$resp %in% 0:4, SCL_df$resp, NA)

save(SCL_df, file="aappss_malpas_2019_scl.rdata")
write.csv(SCL_df, "aappss_malpas_2019_scl.csv", row.names=FALSE)