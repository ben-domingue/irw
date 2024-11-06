# Paper：https://pmc.ncbi.nlm.nih.gov/articles/PMC11392422/#sec002
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LGXP5A 

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

data_df <- read_sav("BAS2_Children_dataset.sav")
data_df <- data_df %>%
  rename(id = CODE)

data_df[] <- lapply(data_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

data_df[] <- lapply(data_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

SPP_df <- data_df |>
  select(starts_with("SPP"), id)
SPP_df <- remove_na(SPP_df)
SPP_df <- pivot_longer(SPP_df, cols=-c(id), names_to="item", values_to="resp")

BAS_df <- data_df |>
  select(starts_with("BAS"),-ends_with("sum"),-ends_with("retest"), id)
BAS_df <- remove_na(BAS_df)
BAS_df <- pivot_longer(BAS_df, cols=-c(id), names_to="item", values_to="resp")

Body_df <- data_df |>
  select(starts_with("Body"),-ends_with("sum"),-ends_with("retest"), id)
Body_df <- remove_na(Body_df)
Body_df <- pivot_longer(Body_df, cols=-c(id), names_to="item", values_to="resp")

Body_df$resp <- as.numeric(Body_df$resp)
df <- rbind(Body_df, BAS_df)
df <- rbind(df, SPP_df)

save(df, file="PEPABAS2C_Kubicka_2024.Rdata")
write.csv(df, "PEPABAS2C_Kubicka_2024.csv", row.names=FALSE)
