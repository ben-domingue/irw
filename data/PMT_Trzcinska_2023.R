# PMT_Trzcinska_2023_PMT, PMT_Trzcinska_2023_MVS, PMT_Trzcinska_2023_finans
#
# Paper: Trzcinska et al. (2023), Pictorial Materialism Test,
#   https://pubmed.ncbi.nlm.nih.gov/37619235/
# Data:  https://osf.io/xbrnm/ (CC BY 4.0),
#   "Pictorial Materialism Test_database_clean.sav"
# Ingestion issue: irw#462. This script was posted there (2024-10-21) but
# never committed; the file then named data/PMT_Trzcinska_2023.R built
# VCISM_Polish_Trzcinska_2023 and is now data/VCISM_Polish_Trzcinska_2023.R
# (irw#2844). Restored as posted, minus unused libraries and the unused
# PMTpilotchildren.sav read; re-run 2026-10-05, all three tables match live
# exactly.
#
# PMT: 32 items per wave (16 picture pairs; 64 codes), 0-2 (0 = not related to materialism,
#   2 = strongly related); ONE* = test (wave 0, 204 children), TWO* = retest
#   (wave 1, 27 children). The retest items keep their TWO* codes, so an item
#   cannot be joined across waves by code.
# MVS: Material Values Scale for Children, 9 items, 1-5.
# finans: shortened Happiness scale, 14 items, 1-4.
# id = row number of the .sav; respondents with no answer in a block are
# dropped from that block.
library(haven)
library(dplyr)
library(tidyr)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

PMT_data_df <- read_sav("Pictorial Materialism Test_database_clean.sav")
PMT_data_df <- PMT_data_df %>%
  mutate(id = row_number())

# ------ PMT ------
firstGroup_df <- PMT_data_df |>
  select(starts_with("ONE"), id)
firstGroup_df <- remove_na(firstGroup_df)
firstGroup_df <- pivot_longer(firstGroup_df, cols = -c(id), names_to = "item", values_to = "resp")
firstGroup_df$wave <- "0"

SecondGroup_df <- PMT_data_df |>
  select(starts_with("TWO"), id)
SecondGroup_df <- remove_na(SecondGroup_df)
SecondGroup_df <- pivot_longer(SecondGroup_df, cols = -c(id), names_to = "item", values_to = "resp")
SecondGroup_df$wave <- "1"

PMT_df <- rbind(firstGroup_df, SecondGroup_df)
write.csv(PMT_df, "PMT_Trzcinska_2023_PMT.csv", row.names = FALSE)

# ------ MVS ------
MVS_df <- PMT_data_df |>
  select(starts_with("MVS"), id)
MVS_df <- remove_na(MVS_df)
MVS_df <- pivot_longer(MVS_df, cols = -c(id), names_to = "item", values_to = "resp")
write.csv(MVS_df, "PMT_Trzcinska_2023_MVS.csv", row.names = FALSE)

# ------ finans ------
finans_df <- PMT_data_df |>
  select(starts_with("finans"), id)
finans_df <- remove_na(finans_df)
finans_df <- pivot_longer(finans_df, cols = -c(id), names_to = "item", values_to = "resp")
write.csv(finans_df, "PMT_Trzcinska_2023_finans.csv", row.names = FALSE)
