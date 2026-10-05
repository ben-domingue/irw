# Paper:https://www.tandfonline.com/doi/abs/10.1080/13674676.2020.1850666
# Data: https://osf.io/h9ktr/ (component dnz26, data_share.csv = https://osf.io/download/tyezk/)
#
# Two tables: the Santa Clara Brief Compassion Scale (SCBCS, 5 items, 1-7) and
# the 15 SPIRIT items (1-6; item 15 is 1-4).
# Rebuilt 2026-10-05 (irw#2836): the script had written SCBCS_df to the SPIRIT
# files, so PeSCBCSCe_Novak_2020_SPIRIT was a copy of the SCBCS table. The
# source's SPIRIT column names are irregular (a misspelled item 8 and item 14,
# suffixes on 12, 13 and 15), so they are mapped explicitly to SPIRIT_1..15;
# starts_with("SPIRIT") had also missed SIPRIT_8 and SPRIT_14.

library(dplyr)
library(tidyr)
library(readr)

remove_na <- function(df) {
  items <- setdiff(names(df), "id")
  df[rowSums(!is.na(df[, items, drop = FALSE])) > 0, ]
}

data_df <- read_csv("data_share.csv")

data_df <- data_df %>%
  rename(id = ID)
stopifnot(!anyDuplicated(data_df$id))

SCBCS_df <- data_df |>
  select(starts_with("SCBCS"), id)
SCBCS_df  <- remove_na(SCBCS_df)
SCBCS_df <- pivot_longer(SCBCS_df, cols=-c(id), names_to="item", values_to="resp")
SCBCS_df <- SCBCS_df[!is.na(SCBCS_df$resp), ]

save(SCBCS_df, file="PeSCBCSCe_Novak_2020_SCBCS.Rdata")
write.csv(SCBCS_df, "PeSCBCSCe_Novak_2020_SCBCS.csv", row.names=FALSE)

spirit_cols <- c(SPIRIT_1 = "SPIRIT_1", SPIRIT_2 = "SPIRIT_2", SPIRIT_3 = "SPIRIT_3",
                 SPIRIT_4 = "SPIRIT_4", SPIRIT_5 = "SPIRIT_5", SPIRIT_6 = "SPIRIT_6",
                 SPIRIT_7 = "SPIRIT_7", SPIRIT_8 = "SIPRIT_8", SPIRIT_9 = "SPIRIT_9",
                 SPIRIT_10 = "SPIRIT_10", SPIRIT_11 = "SPIRIT_11",
                 SPIRIT_12 = "SPIRIT_12_ALTR", SPIRIT_13 = "SPIRIT_13_PRIJ",
                 SPIRIT_14 = "SPRIT_14", SPIRIT_15 = "SPIRIT_15_")
SPIRIT_df <- data_df |>
  select(id, all_of(spirit_cols))
SPIRIT_df <- remove_na(SPIRIT_df)
SPIRIT_df <- pivot_longer(SPIRIT_df, cols=-c(id), names_to="item", values_to="resp")
SPIRIT_df <- SPIRIT_df[!is.na(SPIRIT_df$resp), ]
stopifnot(all(SPIRIT_df$resp %in% 1:6),
          all(SPIRIT_df$resp[SPIRIT_df$item == "SPIRIT_15"] %in% 1:4))

save(SPIRIT_df, file="PeSCBCSCe_Novak_2020_SPIRIT.Rdata")
write.csv(SPIRIT_df, "PeSCBCSCe_Novak_2020_SPIRIT.csv", row.names=FALSE)
