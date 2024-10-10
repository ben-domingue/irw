# Paper:https://pubmed.ncbi.nlm.nih.gov/38311907/
# Data: https://osf.io/f7rp3/
library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

data_df <- read_sav("Data availability.sav")

data_df[] <- lapply(data_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

data_df <- data_df %>%
  rename(id =COD1)

# ------ Process KIDS Dataset ------
KIDS_df <- data_df |>
  select(starts_with("KIDS"), id)
KIDS_df  <- remove_na(KIDS_df)
KIDS_df <- pivot_longer(KIDS_df, cols=-c(id), names_to="item", values_to="resp")
save(KIDS_df, file="PPCDRSSA_FranciscoJ_2023_KIDS.Rdata")
write.csv(KIDS_df, "PPCDRSSA_FranciscoJ_2023_KIDS.csv", row.names=FALSE)

# ------ Process SDQ Dataset ------
SDQ_df <- data_df |>
  select(starts_with("SDQ"), id, -SDQ_E_S, -SDQ_CP,-SDQ_HYP,- SDQ_Peers, -SDQ_Prosocial_behavior)
SDQ_df  <- remove_na(SDQ_df)
SDQ_df <- pivot_longer(SDQ_df, cols=-c(id), names_to="item", values_to="resp")
save(SDQ_df, file="PPCDRSSA_FranciscoJ_2023_SDQ.Rdata")
write.csv(SDQ_df, "PPCDRSSA_FranciscoJ_2023_SDQ.csv", row.names=FALSE)

# ------ Process CDRISC Dataset ------
CDRISC_df <- data_df |>
  select(starts_with("CDRISC"), id, -CDRISC_10)
CDRISC_df  <- remove_na(CDRISC_df)
CDRISC_df <- pivot_longer(CDRISC_df, cols=-c(id), names_to="item", values_to="resp")

save(CDRISC_df, file="PPCDRSSA_FranciscoJ_2023_CDRISC.Rdata")
write.csv(CDRISC_df, "PPCDRSSA_FranciscoJ_2023_CDRISC.csv", row.names=FALSE)

# ------ Process RCADS30 Dataset ------
RCADS30_df <- data_df |>
  select(starts_with("RCADS30"), id)
RCADS30_df  <- remove_na(RCADS30_df)
RCADS30_df <- pivot_longer(RCADS30_df, cols=-c(id), names_to="item", values_to="resp")

save(RCADS30_df, file="PPCDRSSA_FranciscoJ_2023_RCADS30.Rdata")
write.csv(RCADS30_df, "PPCDRSSA_FranciscoJ_2023_RCADS30.csv", row.names=FALSE)