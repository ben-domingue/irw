# Paper: https://pubmed.ncbi.nlm.nih.gov/39007784/
# Data: https://github.com/ben-domingue/irw/issues/381
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

preStudy_df <- read_sav("TSK_ES_231202.sav")

preStudy_df[] <- lapply(preStudy_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

colnames(preStudy_df)[2:6] <- paste0("cov_", colnames(preStudy_df)[2:6])

# ---------- Process TSK Data ----------
tsk_df <- preStudy_df |>
  select((1:6), starts_with("tsk"), id)
tsk_df <- remove_na(tsk_df)
tsk_df  <- pivot_longer(tsk_df, cols=-c(1:6), names_to="item", values_to="resp")
tsk_df$wave <- ifelse(grepl("d7$", tsk_df$item), 1, 0)
tsk_df$item <- gsub("d7$", "", tsk_df$item)
tsk_df <- tsk_df[!is.na(tsk_df$resp), ]

save(tsk_df, file="ccapsvtskhpacr_mercedes_2023_tsk.Rdata")
write.csv(tsk_df, "ccapsvtskhpacr_mercedes_2023_tsk.csv", row.names=FALSE)

# ---------- Process SF12 Data ----------
sf_df <- preStudy_df |>
  select((1:6), starts_with("sf"), id)
sf_df <- remove_na(sf_df)
sf_df  <- pivot_longer(sf_df, cols=-c(1:6), names_to="item", values_to="resp")
sf_df <- sf_df[!is.na(sf_df$resp), ]

save(sf_df, file="ccapsvtskhpacr_mercedes_2023_sf.Rdata")
write.csv(sf_df, "ccapsvtskhpacr_mercedes_2023_sf.csv", row.names=FALSE)

# ---------- Process HADA Data ----------
hada_df <- preStudy_df |>
  select((1:6), starts_with("hada"), starts_with("hadd"), id)
hada_df <- remove_na(hada_df)
hada_df  <- pivot_longer(hada_df, cols=-c(1:6), names_to="item", values_to="resp")
hada_df <- hada_df[!is.na(hada_df$resp), ]

save(hada_df, file="ccapsvtskhpacr_mercedes_2023_hada.Rdata")
write.csv(hada_df, "ccapsvtskhpacr_mercedes_2023_hada.csv", row.names=FALSE)

# ---------- Process BECK Data ----------
beck_df <- preStudy_df |>
  select((1:6), starts_with("beck"), id)
beck_df <- remove_na(beck_df)
beck_df  <- pivot_longer(beck_df, cols=-c(1:6), names_to="item", values_to="resp")
beck_df <- beck_df[!is.na(beck_df$resp), ]

save(beck_df, file="ccapsvtskhpacr_mercedes_2023_beck.Rdata")
write.csv(beck_df, "ccapsvtskhpacr_mercedes_2023_beck.csv", row.names=FALSE)

# ---------- Process Physical Data ----------
phy_df <- preStudy_df |>
  select((1: 37), id, -time)
phy_df <- remove_na(phy_df)
phy_df <- pivot_longer(phy_df, cols=-c(starts_with("cov_"), id), names_to="item", values_to="resp")

save(phy_df, file="ccapsvtskhpacr_mercedes_2023_physical.Rdata")
write.csv(phy_df, "ccapsvtskhpacr_mercedes_2023_physical.csv", row.names=FALSE)