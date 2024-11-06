# Paper：https://www.i-jmr.org/2024/1/e50284
# Data:https://osf.io/pj5mr/ 

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

data_df <- read_dta("SOC_osf.dta")
data_df <- data_df %>%
  mutate(id = row_number())

data_df[] <- lapply(data_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

SOC_df <- data_df |>
  select(starts_with("SOC"),-ends_with("R"),-ends_with("C"),-ends_with("MA"),-ends_with("Me"),-ends_with("tot"), id)
SOC_df <- remove_na(SOC_df)
SOC_df <- SOC_df |>
  select(-SOC5)
SOC_df <- pivot_longer(SOC_df, cols=-c(id), names_to="item", values_to="resp")

save(SOC_df, file="VSOCFP_Sebo_2024.Rdata")
write.csv(SOC_df, "VSOCFP_Sebo_2024.csv", row.names=FALSE)