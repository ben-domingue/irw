# Paper: https://link.springer.com/article/10.1007/s12671-023-02144-1#Sec1
# Data: https://osf.io/9jgxs/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(stringr)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

# OSF 9jgxs, data/"amps psychometric eval.csv"
data_df <- read_csv("https://osf.io/download/jeqwd/")

data_df <- data_df |>
  rename(id=STUDY_ID)
data_df <- data_df |>
  rename(cov_NUMBER_MH_DIAGNOSES = NUMBER_MH_DIAGNOSES, 
         cov_AUD_SUD_DIAGNOSES = AUD_SUD_DIAGNOSES, 
         cov_ALCDAYS_PAST8MONTH = ALCDAYS_PAST8MONTH,
         cov_DRUGDAYS_PAST8MONTH = DRUGDAYS_PAST8MONTH)


# PACS, FFMQ, PSS and DERS were measured at baseline and post-treatment, as
# <SCALE>_<k>_BASELINE and <SCALE>_<k>_POST. Until 2026-09-30 both "waves" were
# built from the _POST columns, so every respondent appeared twice with the same
# answers (irw#2433; the tables were withdrawn 2026-09-25). Now each wave reads its
# own columns, and the wave suffix is stripped from the item code (DERS_11, not
# DERS_11_POST), as for AMPS below: one code per question, wave 0 = baseline,
# wave 1 = post (Ben, 2026-09-30).
cov_cols <- c("cov_NUMBER_MH_DIAGNOSES", "cov_AUD_SUD_DIAGNOSES",
              "cov_ALCDAYS_PAST8MONTH", "cov_DRUGDAYS_PAST8MONTH")
build_wave <- function(scale, suffix, wave) {
  items <- grep(paste0("^", scale, "_[0-9]+_", suffix, "$"), names(data_df), value = TRUE)
  df <- remove_na(data_df[, c(items, "id", cov_cols)])
  df <- pivot_longer(df, cols = all_of(items), names_to = "item", values_to = "resp")
  df$item <- sub(paste0("_", suffix, "$"), "", df$item)
  df$wave <- wave
  df
}
for (scale in c("PACS", "FFMQ", "PSS", "DERS")) {
  out <- rbind(build_wave(scale, "BASELINE", 0), build_wave(scale, "POST", 1))
  out <- out[!is.na(out$resp), c("id", "item", "resp", "wave", cov_cols)]
  write.csv(out, paste0("paampsmartsud_saba_2023_", tolower(scale), ".csv"),
            row.names = FALSE, na = "")
}

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