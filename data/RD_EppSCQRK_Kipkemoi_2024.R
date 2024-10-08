# Paper: https://link.springer.com/article/10.1007/s10803-024-06380-9
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/F4UYZQ

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

Scq_df <- read_csv("autism_study_scq_analysis_dataset_anon.csv")

Scq_df <- Scq_df %>%
  rename(id = studyno_anon)
Scq_df  <- Scq_df |>
  select(starts_with("scq"), id)

Scq_df <- Scq_df |>
  mutate(across(where(is.character), ~ recode(., "N" = 0, "Y" = 1)))

Scq_df <- remove_na(Scq_df )
Scq_df  <- pivot_longer(Scq_df, cols=-c(id), names_to="item", values_to="resp")

save(Scq_df, file="RD_EppSCQRK_Kipkemoi_2024_scq.Rdata")
write.csv(Scq_df, "RD_EppSCQRK_Kipkemoi_2024_scq.csv", row.names=FALSE)