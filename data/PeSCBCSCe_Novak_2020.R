# Paper:https://www.tandfonline.com/doi/abs/10.1080/13674676.2020.1850666
# Data: https://osf.io/h9ktr/

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

data_df <- read_csv("data_share.csv")

data_df <- data_df %>%
  rename(id = ID)

SCBCS_df <- data_df |>
  select(starts_with("SCBCS"), id)
SCBCS_df  <- remove_na(SCBCS_df)
SCBCS_df <- pivot_longer(SCBCS_df, cols=-c(id), names_to="item", values_to="resp")

save(SCBCS_df, file="PeSCBCSCe_Novak_2020_SCBCS.Rdata")
write.csv(SCBCS_df, "PeSCBCSCe_Novak_2020_SCBCS.csv", row.names=FALSE)

SPIRIT_df <- data_df |>
  select(starts_with("SPIRIT"), id)
SPIRIT_df <- remove_na(SPIRIT_df)
SPIRIT_df <- pivot_longer(SPIRIT_df, cols=-c(id), names_to="item", values_to="resp")

save(SCBCS_df, file="PeSCBCSCe_Novak_2020_SPIRIT.Rdata")
write.csv(SCBCS_df, "PeSCBCSCe_Novak_2020_SPIRIT.csv", row.names=FALSE)