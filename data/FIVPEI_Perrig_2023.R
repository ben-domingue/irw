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


data_df <- read_xlsx("PXI_validation_main_data.xlsx")
data_df  <- data_df |>
  rename(id=...1)

# ------ Process PXI Dataset ------
PXI_df <- data_df |>
  select(starts_with("PXI"), id)
PXI_df  <- remove_na(PXI_df)
PXI_df <- pivot_longer(PXI_df, cols=-c(id), names_to="item", values_to="resp")

save(PXI_df, file="FIVPEI_Perrig_2023_PXI.Rdata")
write.csv(PXI_df, "FIVPEI_Perrig_2023_PXI.csv", row.names=FALSE)

# ------ Process AttDiff Dataset ------
PQ_df <- data_df |>
  select(starts_with("PQ"), id)
PQ_df  <- remove_na(PQ_df)
PQ_df <- pivot_longer(PQ_df, cols=-c(id), names_to="item", values_to="resp")

HQI_df <- data_df |>
  select(starts_with("HQI"), id)
HQI_df  <- remove_na(HQI_df)
HQI_df <- pivot_longer(HQI_df, cols=-c(id), names_to="item", values_to="resp")

HQS_df <- data_df |>
  select(starts_with("HQS"), id)
HQS_df  <- remove_na(HQS_df)
HQS_df <- pivot_longer(HQS_df, cols=-c(id), names_to="item", values_to="resp")

ATT_df <- data_df |>
  select(starts_with("ATT"), id)
ATT_df  <- remove_na(ATT_df)
ATT_df <- pivot_longer(ATT_df, cols=-c(id), names_to="item", values_to="resp")

PQ_df$group <- "PQ"
HQI_df$group <- "HQI"
HQS_df$group <- "HQS"
ATT_df$group <- "ATT"

AttDiff_df<- rbind(HQI_df,HQS_df,ATT_df)

save(AttDiff_df, file="FIVPEI_Perrig_2023_AttDiff.Rdata")
write.csv(AttDiff_df, "FIVPEI_Perrig_2023_AttDiff.csv", row.names=FALSE)

# ------ Process PENS Dataset ------
PENS_df <- data_df |>
  select(starts_with("PENS"), id)
PENS_df  <- remove_na(PENS_df)
PENS_df <- pivot_longer(PENS_df, cols=-c(id), names_to="item", values_to="resp")

save(PENS_df, file="FIVPEI_Perrig_2023_PENS.Rdata")
write.csv(PENS_df, "FIVPEI_Perrig_2023_PENS.csv", row.names=FALSE)

# ------ Process IMI Dataset ------
IMI_df <- data_df |>
  select(starts_with("IMI"), id)
IMI_df  <- remove_na(IMI_df)
IMI_df <- pivot_longer(IMI_df, cols=-c(id), names_to="item", values_to="resp")

save(IMI_df, file="FIVPEI_Perrig_2023_IMI.Rdata")
write.csv(IMI_df, "FIVPEI_Perrig_2023_IMI.csv", row.names=FALSE)