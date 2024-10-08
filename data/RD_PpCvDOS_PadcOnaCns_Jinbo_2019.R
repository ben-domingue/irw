# Paper: https://link.springer.com/article/10.1007/s40519-019-00656-1#Sec2
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/F4UYZQ

library(haven)
library(dplyr)
library(tidyr)
library(openxlsx)

rm(list = ls())

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

DOS_df <- read.xlsx("C_DOS.xlsx", sheet = 1)

DOS_df <- DOS_df %>%
  mutate(id = row_number() )

DOS_df  <- DOS_df |>
  select(starts_with("DOS"), id)
DOS_df <- DOS_df %>%
  mutate_all(~ replace(., . == -999, NA))
DOS_df  <- remove_na(DOS_df )
DOS_df  <- pivot_longer(DOS_df, cols=-c(id), names_to="item", values_to="resp")

save(DOS_df, file="RD_PpCvDOS_PadcOnaCns_Jinbo_2019_DOS.Rdata")
write.csv(DOS_df, "RD_PpCvDOS_PadcOnaCns_Jinbo_2019_DOS.csv", row.names=FALSE)