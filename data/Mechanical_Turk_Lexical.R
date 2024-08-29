# Paper:https://link.springer.com/article/10.3758/s13428-021-01573-x#Sec7
# Data: https://osf.io/za9y8/
library(tidyr)
library(dplyr)
library(tidyverse)

# Process Experiment 1 Data
df <- read.csv("./Experiment1.data")
df <- df[df$test_word_string != "practice_word", ]

df$response_key_ID[df$response_key_ID == 0] <- NA # Set invalid key presses to NA
df$response_key_ID <- ifelse(df$task == 1, 
                               ifelse(df$response_key_ID == df$column_7_value, 1, 0), # For lexical decision
                             ifelse((df$response_key_ID == 1 & df$column_8_value %in% c(1, 2)) # For memorization
                                    | (df$response_key_ID == 2 & df$column_8_value == 3), 
                                    1, 0))

df <- df |>
  select(-block_number, -stimulus_number, 
         -column_7_value, -column_8_value, 
         -word_length, -word_id) |>
  rename(id=subject_number, rt=reaction_time, 
         resp=response_key_ID, item=test_word_string, subtest=task_number) |>
  mutate(subtest = case_when( # Rename subtest.
    subtest == 1 ~ "lexical",
    subtest == 2 ~ "recognition",
    TRUE ~ as.character(subtest)  # Keep other values unchanged if any
  ))
df$rt <- df$rt / 1000 # Convert resp time from ms to s

lexical_df <- df[df$subtest == "lexical", ] # Split the df based off the subtest
recognition_df <- df[df$subtest == "recognition", ]
lexical_df <- lexical_df[, !(names(lexical_df) %in% "subtest")] # Delete the subtest column
recognition_df <- recognition_df[, !(names(recognition_df) %in% "subtest")]
rownames(lexical_df) <- NULL # Reassign row numbers
rownames(recognition_df) <- NULL

save(lexical_df, file="Mechanical_Turk_Lexical.Rdata")
write.csv(lexical_df, "Mechanical_Turk_Lexical.csv", row.names=FALSE)
save(recognition_df, file="Mechanical_Turk_Recognition.Rdata")
write.csv(recognition_df, "Mechanical_Turk_Recognition.csv", row.names=FALSE)

