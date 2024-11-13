# Paper：
# Data: https://osf.io/hx8qt/

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


data_df <- read_xlsx("Raw data (K-DOCS; English).xlsx")
data_df <- data_df %>%
  rename(id = ID)

BFI_df <- data_df |>
  select(starts_with("bfi"), id)
BFI_df <- remove_na(BFI_df)
BFI_df <- pivot_longer(BFI_df, cols=-c(id), names_to="item", values_to="resp")

save(BFI_df, file="RvKDCS_Romiacg_Miroshnik_2020_BFI.Rdata")
write.csv(BFI_df, "RvKDCS_Romiacg_Miroshnik_2020_BFI.csv", row.names=FALSE)

CBI_df <- data_df |>
  select(starts_with("cbi"), id)
CBI_df <- remove_na(CBI_df)
CBI_df <- pivot_longer(CBI_df, cols=-c(id), names_to="item", values_to="resp")


save(CBI_df, file="RvKDCS_Romiacg_Miroshnik_2020_CBI.Rdata")
write.csv(CBI_df, "RvKDCS_Romiacg_Miroshnik_2020_CBI.csv", row.names=FALSE)

KDOCS_df <- data_df |>
  select(starts_with("KDOCS"), id)
KDOCS_df <- remove_na(KDOCS_df)
KDOCS_df <- pivot_longer(KDOCS_df, cols=-c(id), names_to="item", values_to="resp")

save(KDOCS_df, file="RvKDCS_Romiacg_Miroshnik_2020_KDOCS.Rdata")
write.csv(KDOCS_df, "RvKDCS_Romiacg_Miroshnik_2020_KDOCS.csv", row.names=FALSE)

