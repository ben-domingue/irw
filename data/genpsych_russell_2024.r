# Paper: https://osf.io/preprints/psyarxiv/fgbj4
# Data: https://osf.io/zcytb/?view_only=79d2c8bf12c24393863d60c4143f8a0e
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

map_to_likert <- function(resp) {
  # Define the mapping as a named vector
  likert_mapping <- c(
    "Agree" = 4,
    "Disagree" = 2,
    "Neither agree nor disagree" = 3,
    "Strongly agree" = 5,
    "Strongly Disagree" = 1
  )
  
  # Map the resp values to Likert scale
  return(likert_mapping[resp])
}

process_data <- function(file_path, file_appendix) {
  # Read the Excel file
  df <- read_xlsx(file_path)
  
  # Remove the first row
  df <- df[-1, ]
  
  # Rename and select relevant columns
  df <- df |>
    rename(cov_age = age, cov_gender = gender, cov_english = english, 
           cov_hispanic = hispanic, cov_race = race) |>
    select(starts_with("item"), starts_with("cov"))
  
  # Add an ID column
  df$id <- seq_len(nrow(df))
  
  # Pivot the data to long format
  df <- pivot_longer(
    df, 
    cols = -c(id, starts_with("cov")), 
    names_to = "item", 
    values_to = "resp"
  )
  
  # Map responses to Likert scale
  df$resp <- map_to_likert(df$resp)
  
  # Save and export the processed data
  save(df, file = paste0("genpsych_russell_2024_", file_appendix, ".Rdata"))
  write.csv(df, paste0("genpsych_russell_2024_", file_appendix, ".csv"), row.names = FALSE)
  print(table(df$resp))
}

# ---------- Process Gemma-2 Data ----------
process_data("gemma-2/gemma-2_deID.xlsx", "gemma")
# ---------- Process GPT-3.5 Data ----------
process_data("gpt-3.5/gpt-3.5_deID.xlsx", "gpt3.5")
# ---------- Process GPT-4o Data ----------
process_data("gpt-4o/gpt-4o_deID.xlsx", "gpt4o")
# ---------- Process LLAMA-3 Data ----------
process_data("llama-3/llama-3_deID.xlsx", "llama3")
# ---------- Process Mixtral Data ----------
process_data("mixtral/mixtral_deID.xlsx", "mixtral")