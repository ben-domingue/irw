# Paper：
# Data: https://osf.io/ymj6u/

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


data_df <- read_csv("ifm.csv")
data_df <- data_df %>%
  mutate(id = row_number())


ifm_df <- data_df |>
  select(starts_with("ifm"), id)
ifm_df<- remove_na(ifm_df)
ifm_df <- pivot_longer(ifm_df, cols=-c(id), names_to="item", values_to="resp")

save(ifm_df, file="DbdIFdM_Puga_2021.Rdata")
write.csv(ifm_df, "DbdIFdM_Puga_2021.csv", row.names=FALSE)