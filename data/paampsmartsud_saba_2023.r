# Paper: https://link.springer.com/article/10.1007/s12671-023-02144-1#Sec1
# Data: https://osf.io/9jgxs/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)
library(stringr)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

data_df <- read_csv("ampspsychometriceval.csv")

data_df <- data_df |>
  rename(id=STUDY_ID)
data_df <- data_df |>
  rename(cov_NUMBER_MH_DIAGNOSES = NUMBER_MH_DIAGNOSES, 
         cov_AUD_SUD_DIAGNOSES = AUD_SUD_DIAGNOSES, 
         cov_ALCDAYS_PAST8MONTH = ALCDAYS_PAST8MONTH,
         cov_DRUGDAYS_PAST8MONTH = DRUGDAYS_PAST8MONTH)


PACS_POST_df <- data_df  |>
  select(starts_with("PACS")&ends_with("POST"),-("PACS_MEAN_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
PACS_POST_df <- remove_na(PACS_POST_df)
PACS_POST_df  <- pivot_longer(PACS_POST_df, 
                              cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                              names_to="item", values_to="resp")

FFMQ_POST_df <- data_df  |>
  select(starts_with("FFMQ")&ends_with("POST"),-("FFMQ_SUM_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
FFMQ_POST_df <- remove_na(FFMQ_POST_df)
FFMQ_POST_df  <- pivot_longer(FFMQ_POST_df, 
                              cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                              names_to="item", values_to="resp")

PSS_POST_df <- data_df  |>
  select(starts_with("PSS")&ends_with("POST"),-("PSS_SUM_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
PSS_POST_df <- remove_na(PSS_POST_df)
PSS_POST_df  <- pivot_longer(PSS_POST_df, 
                             cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                             names_to="item", values_to="resp")

DERS_POST_df <- data_df  |>
  select(starts_with("DERS")&ends_with("POST"),-("DERS_SUM_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
DERS_POST_df <- remove_na(DERS_POST_df)
DERS_POST_df  <- pivot_longer(DERS_POST_df, 
                              cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                              names_to="item", values_to="resp")

PACS_BASELINE_df <- data_df  |>
  select(starts_with("PACS")&ends_with("POST"),-("PACS_MEAN_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
PACS_BASELINE_df <- remove_na(PACS_BASELINE_df)
PACS_BASELINE_df  <- pivot_longer(PACS_BASELINE_df, 
                                  cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                                  names_to="item", values_to="resp")

FFMQ_BASELINE_df <- data_df  |>
  select(starts_with("FFMQ")&ends_with("POST"),-("FFMQ_SUM_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
FFMQ_BASELINE_df <- remove_na(FFMQ_BASELINE_df)
FFMQ_BASELINE_df  <- pivot_longer(FFMQ_BASELINE_df, 
                                  cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                                  names_to="item", values_to="resp")

PSS_BASELINE_df <- data_df  |>
  select(starts_with("PSS")&ends_with("POST"),-("PSS_SUM_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
PSS_BASELINE_df <- remove_na(PSS_BASELINE_df)
PSS_BASELINE_df  <- pivot_longer(PSS_BASELINE_df, 
                                 cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                                 names_to="item", values_to="resp")

DERS_BASELINE_df <- data_df  |>
  select(starts_with("DERS")&ends_with("POST"),-("DERS_SUM_POST"),id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
DERS_BASELINE_df <- remove_na(DERS_BASELINE_df)
DERS_BASELINE_df  <- pivot_longer(DERS_BASELINE_df, 
                                  cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                                  names_to="item", values_to="resp")

PACS_POST_df$wave <- 0
PACS_BASELINE_df $wave <- 1
PACS_df <-rbind(PACS_POST_df,PACS_BASELINE_df)

save(PACS_df, file="paampsmartsud_saba_2023_PACS.Rdata")
write.csv(PACS_df, "paampsmartsud_saba_2023_PACS.csv", row.names=FALSE)

FFMQ_POST_df $wave <- 0
FFMQ_BASELINE_df $wave <- 1
FFMQ_df <-rbind(FFMQ_POST_df,FFMQ_BASELINE_df)

save(FFMQ_df, file="paampsmartsud_saba_2023_FFMQ.Rdata")
write.csv(FFMQ_df, "paampsmartsud_saba_2023_FFMQ.csv", row.names=FALSE)

PSS_POST_df $wave <- 0
PSS_BASELINE_df $wave <- 1
PSS_df <-rbind(PSS_POST_df,PSS_BASELINE_df)

save(PSS_df, file="paampsmartsud_saba_2023_PSS.Rdata")
write.csv(PSS_df, "paampsmartsud_saba_2023_PSS.csv", row.names=FALSE)

DERS_POST_df $wave <- 0
DERS_BASELINE_df $wave <- 1
DERS_df <-rbind(DERS_POST_df,DERS_BASELINE_df)

save(DERS_df, file="paampsmartsud_saba_2023_DERS.Rdata")
write.csv(DERS_df, "paampsmartsud_saba_2023_DERS.csv", row.names=FALSE)

AMPS_df <- data_df |>
  select(
    matches("^AMPS(?!.*SUM).*_(S3|S6|S9|S12)$", perl = TRUE),  # Selects columns matching regex
    id,
    cov_NUMBER_MH_DIAGNOSES,
    cov_AUD_SUD_DIAGNOSES,
    cov_ALCDAYS_PAST8MONTH,
    cov_DRUGDAYS_PAST8MONTH
  )

AMPS_df<- remove_na(AMPS_df)
AMPS_df  <- pivot_longer(AMPS_df, 
                         cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                         names_to="item", values_to="resp")
AMPS_df <- AMPS_df %>%
  mutate(S_value = str_extract(item, "S\\d+"))  # Extract the "S" number
unique_s_values <- unique(AMPS_df$S_value)
s_mapping <- setNames(seq(0, length(unique_s_values)-1), unique_s_values)

# Map S values to numeric values
AMPS_df <- AMPS_df %>%
  mutate(wave = s_mapping[S_value])

# Remove the S appendix from "item" column
AMPS_df <- AMPS_df %>%
  mutate(item = str_remove(item, "_S\\d+"))

save(AMPS_df, file="paampsmartsud_saba_2023_AMPS.Rdata")
write.csv(AMPS_df, "paampsmartsud_saba_2023_AMPS.csv", row.names=FALSE)

attendance_df <- data_df  |>
  select(starts_with("attendance"), id,cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH)
attendance_df  <- remove_na(attendance_df )
attendance_df  <- pivot_longer(attendance_df, 
                               cols=-c(id, cov_NUMBER_MH_DIAGNOSES,cov_AUD_SUD_DIAGNOSES,cov_ALCDAYS_PAST8MONTH,cov_DRUGDAYS_PAST8MONTH), 
                               names_to="item", values_to="resp")

save(attendance_df, file="paampsmartsud_saba_2023_attendance.Rdata")
write.csv(attendance_df, "paampsmartsud_saba_2023_attendance.csv", row.names=FALSE)