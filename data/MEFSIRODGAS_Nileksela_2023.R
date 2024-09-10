# Paper: https://journals.sagepub.com/doi/full/10.1177/10731911221134599?casa_token=deSlptsbKc4AAAAA%3A_C4W1sDCAkNUukk1-SDXC_K1jWHKbzo_hQUjrfPvn4g7nXNLlWkuKkskPcJVxClQGYCKdTagV6A
# Data:https://osf.io/khwzy/?view_only=
library(dplyr)
library(tidyr)
library(haven)
library(readxl)

common_cols = c("id", "age", "group")
# ------ Definition of Helper Functions
days_to_5_point <- function(x) {
  ifelse(x %in% c("0 days", "1 day"), 1,
         ifelse(x %in% c("2 days", "3 days"), 2, 
                ifelse(x %in% c("4 days", "5 days"), 3,
                       ifelse(x == "6 days", 4,
                              ifelse(x == "7 days", 5, NA)))))
}

convert_to_5_point <- function(x) {
  extracted_values <- gsub(".*\\(([^)]+)\\).*", "\\1", x)
  as.numeric(extracted_values) + 1
}

encode_scale <- function(df, resp1, resp2, resp3, resp4) {
  df[setdiff(names(df), common_cols)] <- lapply(df[setdiff(names(df), common_cols)], function(x) {
    x[x == resp1] <- 1
    x[x == resp2] <- 2
    x[x == resp3] <- 3
    x[x == resp4] <- 4
    return(as.numeric(x))
  })
  return(df)
}

process_questionnaires <- function(df, prefix, resp_freq, resp_severity) {
  # Process the frequency dataframe
  freq_df <- df %>%
    select(id, group, age, starts_with(paste0(prefix, "_freq"))) %>%
    filter(group == "Frequency")
  
  # Process the severity dataframe
  severity_df <- df %>%
    select(id, group, age, starts_with(paste0(prefix, "_severity"))) %>%
    filter(group == "Severity")
  
  # Encode the scales (assuming encode_scale is a custom function)
  freq_df <- encode_scale(freq_df, resp_freq[1], resp_freq[2], resp_freq[3], resp_freq[4])
  severity_df <- encode_scale(severity_df, resp_severity[1], resp_severity[2], resp_severity[3], resp_severity[4])
  
  # Merge the frequency and severity datasets
  colnames(freq_df) <- gsub("frequency_", "", colnames(freq_df))
  colnames(severity_df) <- gsub("severity_", "", colnames(severity_df))
  
  merged_df <- rbind(freq_df, severity_df)
  
  # Save the merged dataframe as RData and CSV
  save(merged_df, file = paste0("MEFSIRODGAS_Nileksela_2023_", prefix, ".Rdata"))
  write.csv(merged_df, paste0("MEFSIRODGAS_Nileksela_2023_", prefix, ".csv"), row.names = FALSE)
  
  # Return the merged dataframe for further use if needed
  return(merged_df)
}

# ------ Process Datasets ------ 
df <- read_excel("./Item Response Options_Raw Data.xlsx")
df <- df |>
  select(-starts_with("Gender_ID"), -starts_with("Race"), -starts_with("MH"),
         -Ethnicity, -State, 
         -Academic_Status, -region) |>
  rename(age=Age)
df$id <- seq_len(nrow(df))

# ------ Process PHQ Questionnaires ------
PHQ9_freq_resp <- c("Not at all", "Several days", 
                    "More than half the days", "Nearly every day")
PHQ9_severity_resp <- c("Not present", "Mild problem", 
                        "Moderate problem", "Severe problem")
PHQ9_df <- process_questionnaires(df, "PHQ_9", PHQ9_freq_resp, PHQ9_severity_resp)

# ------ Process CUDOS Datasets ------
CUDOS_freq_resp <- c("0 Days", "1-2 Days", "3-5 Days", "6-7 Days")
CUDOS_severity_resp <- c("Not present", "Mild problem", 
                        "Moderate problem", "Severe problem")
CUDOS_df <- process_questionnaires(df, "CUDOS", CUDOS_freq_resp, CUDOS_severity_resp)

# ------ Process GAD-7 Datasets ------
GAD7_freq_resp <- c("Not at all", "Several days","More than half the days", "Nearly every day")
GAD7_severity_resp <- c("Not present", "Mild problem", "Moderate problem", "Severe problem")
GAD7_df <- process_questionnaires(df, "GAD_7", GAD7_freq_resp, GAD7_severity_resp)

# ------ Process CUXOS Datasets ------
CUXOS_freq_resp <- c("0 Days", "1-2 Days", "3-5 Days", "6-7 Days")
CUXOS_severity_resp <- c("Not present", "Mild problem", "Moderate problem", "Severe problem")
CUXOS_df <- process_questionnaires(df, "CUXOS", CUXOS_freq_resp, CUXOS_severity_resp)

# ------ Process CCAPS Datasets ------
CCAPS_df <- df |>
  select(id, age, group, starts_with("CCAPS"))
CCAPS_df[setdiff(names(CCAPS_df), c("group", "id", "age"))] <- lapply(CCAPS_df[setdiff(names(CCAPS_df), c("group", "id", "age"))], convert_to_5_point)

# ------ Process Impairment Datasets ------
imp_df <- df |>
  select(id, age, group, starts_with("Anx"))
imp_df$Anxiety_Impairment_1...97 <- ifelse(!is.na(imp_df$Anxiety_Impairment_1...159), imp_df$Anxiety_Impairment_1...159, imp_df$Anxiety_Impairment_1...97)
imp_df$Anxiety_Impairment_2...98 <- ifelse(!is.na(imp_df$Anxiety_Impairment_2...160), imp_df$Anxiety_Impairment_2...160, imp_df$Anxiety_Impairment_2...98)
imp_df$Anxiety_Impairment_3...99 <- ifelse(!is.na(imp_df$Anxiety_Impairment_3...161), imp_df$Anxiety_Impairment_3...161, imp_df$Anxiety_Impairment_3...99)
imp_df$Anx_overall_imp...100 <- ifelse(!is.na(imp_df$Anx_overall_imp...162), imp_df$Anx_overall_imp...162, imp_df$Anx_overall_imp...100)
imp_df$Anx_days_imp...101 <- ifelse(!is.na(imp_df$Anx_days_imp...163), imp_df$Anx_days_imp...163, imp_df$Anx_days_imp...101)
imp_df <- imp_df |>
  select(-Anxiety_Impairment_1...159, -Anxiety_Impairment_2...160, -Anxiety_Impairment_3...161
         ,-Anx_overall_imp...162, -Anx_days_imp...163)

colnames(imp_df) <- gsub("\\.\\.\\.\\d+", "", colnames(imp_df))
imp_df[setdiff(names(imp_df), c("group", "id", "age", "Anx_overall_imp", "Anx_days_imp"))] <- lapply(imp_df[setdiff(names(imp_df), c("group", "id", "age", "Anx_overall_imp", "Anx_days_imp"))], function(x) {
  x[x == "No difficulty"] <- 1
  x[x == "Mild difficulty"] <- 2
  x[x == "Moderate difficulty"] <- 3
  x[x == "Marked difficulty"] <- 4
  x[x == "Extreme difficulty"] <- 5
  x[x == ""] <- NA
  return(as.numeric(x))
})
imp_df["Anx_overall_imp"] <- lapply(imp_df["Anx_overall_imp"], function(x) {
  x[x == "Not at all"] <- 1
  x[x == "A little bit"] <- 2
  x[x == "A moderate amount"] <- 3
  x[x == "Quite a bit"] <- 4
  x[x == "Extremely"] <- 5
  x[x == ""] <- NA
  return(as.numeric(x))
})
imp_df["Anx_days_imp"] <- lapply(imp_df["Anx_days_imp"], days_to_5_point)

merged_df = {}
merged_df <- merge(CCAPS_df, CUDOS_df, by=common_cols)
merged_df <- merge(merged_df, PHQ9_df, by=common_cols)
merged_df <- merge(merged_df, GAD7_df, by=common_cols)
merged_df <- merge(merged_df, CUXOS_df, by=common_cols)
merged_df <- merge(merged_df, imp_df, by=common_cols)
long_df <- pivot_longer(merged_df, col=-common_cols, names_to = "item", values_to = "resp")
freq_df <- long_df %>% 
  filter(group == "Frequency") %>%
  select(-group)
severity_df <- long_df |>
  filter(group == "Severity") |>
  select(-group)

save(freq_df, file="MEFSIRODGAS_Nileksela_2023_freq.Rdata")
save(freq_df, file="MEFSIRODGAS_Nileksela_2023_severity.Rdata")
write.csv(severity_df, "MEFSIRODGAS_Nileksela_2023_freq.csv", row.names=FALSE)
write.csv(severity_df, "MEFSIRODGAS_Nileksela_2023_severity.csv", row.names=FALSE)
