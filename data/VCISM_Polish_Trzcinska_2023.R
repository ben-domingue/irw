# VCISM_Polish_Trzcinska_2023 (PSPCSA items from psiat_validation.sav;
# data DOI 10.17605/OSF.IO/K2QEW).
# This file was data/PMT_Trzcińska_2023.R until irw#2844: despite that name it
# never built the PMT tables, whose script is now data/PMT_Trzcinska_2023.R.
library(haven)
library(dplyr)
library(tidyr)

# Remove participants whose responses are all NAs
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) == "id")])) == (ncol(df) - 1)), ]
  return(df)
}

df <- read_sav("psiat_validation.sav")
# id = row number of the .sav. The source's child_code holds the children's
# initials (e.g. three letters), which IRW does not publish (Ben 2026-10-05).
df <- df |>
  mutate(child_code = row_number()) |>
  select(child_code, starts_with("pspcsa"), -PSPCSA, 
         -PSPCSA_competences, -PSPCSA_acceptance) |>
  rename(id=child_code)  
df <- remove_na(df)

# ------ Process Test Dataset ------
test_df <- df |>
  select(-ends_with("r"))
test_df[] <- lapply(test_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
test_df <- pivot_longer(test_df, cols=-id, names_to = "item", values_to = "resp")
test_df$wave <- 0

# ------ Process Re-test Dataset ------
retest_df <- df |>
  select(id, ends_with("r"))
colnames(retest_df) <- gsub('r', '', colnames(retest_df))
retest_df[] <- lapply(retest_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
retest_df <- pivot_longer(retest_df, cols=-id, names_to = "item", values_to = "resp")
retest_df$wave <- 1

df <- rbind(test_df, retest_df)
save(df, file="VCISM_Polish_Trzcińska_2023.Rdata")
write.csv(df, "VCISM_Polish_Trzcińska_2023.csv", row.names=FALSE, na="")