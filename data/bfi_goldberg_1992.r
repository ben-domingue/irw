# Paper
# Data: https://openpsychometrics.org/_rawdata/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("data.csv", header = TRUE, sep = "\t")
df[df == 0] <- NA
df <- df |>
  rename(cov_race=race, cov_age=age, cov_engnat=engnat, cov_gender=gender, cov_hand=hand,
         cov_source=source, cov_country=country)
df$id <- seq_len(nrow(df))

E_items <- paste0("E", 1:10)
N_items <- paste0("N", 1:10)
A_items <- paste0("A", 1:10)
C_items <- paste0("C", 1:10)
O_items <- paste0("O", 1:10)

# Step 3: Extract separate data frames for each scale, keeping covariates and id
covariates <- c("id", names(df)[grepl("^cov_", names(df))])

df_E <- df[, c(covariates, E_items)]
df_N <- df[, c(covariates, N_items)]
df_A <- df[, c(covariates, A_items)]
df_C <- df[, c(covariates, C_items)]
df_O <- df[, c(covariates, O_items)]

df_E <- pivot_longer(df_E, cols = -c(id, starts_with("cov")), 
                     names_to = "item", values_to = "resp")

df_N <- pivot_longer(df_N, cols = -c(id, starts_with("cov")), 
                     names_to = "item", values_to = "resp")

df_A <- pivot_longer(df_A, cols = -c(id, starts_with("cov")), 
                     names_to = "item", values_to = "resp")

df_C <- pivot_longer(df_C, cols = -c(id, starts_with("cov")), 
                     names_to = "item", values_to = "resp")

df_O <- pivot_longer(df_O, cols = -c(id, starts_with("cov")), 
                     names_to = "item", values_to = "resp")

# Correct: use list() to keep dataframes intact
suffixes <- list(
  sociability = df_E,
  emotional_instability = df_N,
  compassion = df_A,
  self_discipline = df_C,
  intellectual_curiosity = df_O
)

# Loop over the list and save one .csv and one .RData for each
for (suffix in names(suffixes)) {
  df <- suffixes[[suffix]]
  file_base <- paste0("bfi_goldberg_1992_", suffix)
  
  write.csv(df, paste0(file_base, ".csv"), row.names = FALSE)
  
  assign(file_base, df)
  save(list = file_base, file = paste0(file_base, ".RData"))
}