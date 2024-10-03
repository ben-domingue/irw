# Paper: https://link.springer.com/article/10.1007/s12144-022-03323-4
# Data: https://osf.io/twzq4/files/osfstorage

library(haven)
library(dplyr)
library(tidyr)
library(readr)
rm(list = ls())

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

FFMQ_df <- read_delim("Data.csv", delim = ";")

FFMQ_df <- FFMQ_df %>%
  mutate(id = row_number() )

FFMQ_df <- FFMQ_df |>
  select(starts_with("FFMQ"), id)


FFMQ_df  <- remove_na(FFMQ_df)
FFMQ_df <- pivot_longer(FFMQ_df, cols=-c(id), names_to="item", values_to="resp")

save(FFMQ_df, file="PRCPSFFMQ_Lecuona_2017.Rdata")
write.csv(FFMQ_df, "PRCPSFFMQ_Lecuona_2017.csv", row.names=FALSE)

