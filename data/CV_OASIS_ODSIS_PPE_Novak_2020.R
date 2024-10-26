# Paper：https://osf.io/ad6b3/
# Data:https://pubmed.ncbi.nlm.nih.gov/34639633/

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)
library(readr)
library(readxl)
library(sas7bdat)

rm(list =ls()) 
remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) -1)), ]
  return(df)
}

# ------ Pre-process Data ------
ex_data_df <- read_delim("ex.dataset.csv", delim = ";")
pa_data_df <- read_delim("pa.dataset.csv", delim = ";")
data_df <- read_sav("retest.data.oasis.odsis.sav")

ex_data_df <- ex_data_df%>%
  rename(id = code )
pa_data_df<- pa_data_df %>%
  rename(id = code )
data_df <- data_df %>%
  mutate(id = row_number() )

# ------ Process OASIS Data ------
OASIS_ex_df <- ex_data_df  |>
  select(starts_with("OASIS"), id)
OASIS_ex_df <- remove_na(OASIS_ex_df)
OASIS_ex_df <- OASIS_ex_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")
OASIS_pa_df <- pa_data_df  |>
  select(starts_with("OASIS"), id)
OASIS_pa_df <- remove_na(OASIS_pa_df)
OASIS_pa_df <- OASIS_pa_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

OASIS_ex_df$ group <- "Sample 1"
OASIS_pa_df$ group <- "Sample 2"

OASIS_df <- rbind(OASIS_ex_df, OASIS_pa_df)

# ------ Process ODSIS Data ------
ODSIS_ex_df <- ex_data_df  |>
  select(starts_with("OASIS"), id)
ODSIS_ex_df <- remove_na(ODSIS_ex_df)
ODSIS_ex_df <- ODSIS_ex_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

ODSIS_pa_df <- pa_data_df  |>
  select(starts_with("ODSIS"), id)
ODSIS_pa_df <- remove_na(ODSIS_pa_df)
ODSIS_pa_df <- ODSIS_pa_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

ODSIS_ex_df$ group <- "Sample 1"
ODSIS_pa_df$ group <- "Sample 2"

ODSIS_df <- rbind(ODSIS_ex_df, ODSIS_pa_df)
dep_df <- rbind(ODSIS_df, OASIS_df)
save(dep_df, file="CV_OASIS_ODSIS_PPE_Novak_2020_DEP/ANX.Rdata")
write.csv(dep_df, "CV_OASIS_ODSIS_PPE_Novak_2020_DEP/ANX.csv", row.names=FALSE)

# ------- Process RSES Data ------
RSES_ex_df <- ex_data_df  |>
  select(starts_with("RSES"), id)
RSES_ex_df <- remove_na(RSES_ex_df)
RSES_ex_df <- RSES_ex_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

RSES_pa_df <- pa_data_df  |>
  select(starts_with("RSES"), id)
RSES_pa_df <- remove_na(RSES_pa_df)
RSES_pa_df <- RSES_pa_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

RSES_ex_df$ group <- "Sample 1"
RSES_pa_df$ group <- "Sample 2"

RSES_df <- rbind(RSES_ex_df, RSES_pa_df)
save(RSES_df, file="CV_OASIS_ODSIS_PPE_Novak_2020_RSES.Rdata")
write.csv(RSES_df, "CV_OASIS_ODSIS_PPE_Novak_2020_RSES.csv", row.names=FALSE)

# ------ Process BFI Data ------
BFI_ex_df <- ex_data_df  |>
  select(starts_with("BFI"), id)
BFI_ex_df <- remove_na(BFI_ex_df)
BFI_ex_df <- BFI_ex_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

BFI_pa_df <- pa_data_df  |>
  select(starts_with("BFI"), id)
BFI_pa_df <- remove_na(BFI_pa_df)
BFI_pa_df <- BFI_pa_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

BFI_ex_df$ group <- "Sample 1"
BFI_pa_df$ group <- "Sample 2"

BFI_df <- rbind(BFI_ex_df, BFI_pa_df)
save(BFI_df, file="CV_OASIS_ODSIS_PPE_Novak_2020_BFI.Rdata")
write.csv(BFI_df, "CV_OASIS_ODSIS_PPE_Novak_2020_BFI.csv", row.names=FALSE)

# ------ Process PANAS Data ------
PANAS_df  <- ex_data_df  |>
  select(starts_with("PANAS"), id)
PANAS_df <- remove_na(PANAS_df)
PANAS_df <- PANAS_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")
save(PANAS_df, file="CV_OASIS_ODSIS_PPE_Novak_2020_PANAS.Rdata")
write.csv(PANAS_df, "CV_OASIS_ODSIS_PPE_Novak_2020_PANAS.csv", row.names=FALSE)

# ------ Process DSES Data ------
DSES_ex_df <- ex_data_df  |>
  select(starts_with("DSES"), id)
DSES_ex_df <- remove_na(DSES_ex_df)
DSES_ex_df <- DSES_ex_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

DSES_pa_df <- pa_data_df  |>
  select(starts_with("DSES"), id)
DSES_pa_df <- remove_na(DSES_pa_df)
DSES_pa_df <- DSES_pa_df %>%
  pivot_longer(cols = -c(id), names_to = "item", values_to = "resp")

DSES_ex_df$ group <- "Sample 1"
DSES_pa_df$ group <- "Sample 2"
DSES_df <- rbind(DSES_ex_df, DSES_pa_df)

save(DSES_df, file="CV_OASIS_ODSIS_PPE_Novak_2020_DSES.Rdata")
write.csv(DSES_df, "CV_OASIS_ODSIS_PPE_Novak_2020_DSES.csv", row.names=FALSE)
