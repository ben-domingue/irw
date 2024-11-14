# Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC5372834/#sec6
# Data: https://osf.io/fecgz/

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

data_df <- read_csv("CLEANEDSAMPLESR_Feb2017.csv")
data_df <- data_df |>
  rename(id=RespondentId)

OEQ_df <- data_df |>
  select(starts_with("OEQ"), id)
OEQ_df  <- remove_na(OEQ_df)
OEQ_df <- pivot_longer(OEQ_df, cols=-c(id), names_to="item", values_to="resp")

save(OEQ_df, file="SPQVS_Barnby_2017_OEQ.Rdata")
write.csv(OEQ_df, "SPQVS_Barnby_2017_OEQ.csv", row.names=FALSE)

WHO_df <- data_df |>
  select(starts_with("WHO"), id)
WHO_df  <- remove_na(WHO_df)
WHO_df <- pivot_longer(WHO_df, cols=-c(id), names_to="item", values_to="resp")

save(WHO_df, file="SPQVS_Barnby_2017_WHO.Rdata")
write.csv(WHO_df, "SPQVS_Barnby_2017_WHO.csv", row.names=FALSE)

OLIFE_df <- data_df |>
  select(starts_with("OLIFE"), id)
OLIFE_df  <- remove_na(OLIFE_df)
OLIFE_df <- pivot_longer(OLIFE_df, cols=-c(id), names_to="item", values_to="resp")

save(OLIFE_df, file="SPQVS_Barnby_2017_OLIFE.Rdata")
write.csv(OLIFE_df, "SPQVS_Barnby_2017_OLIFE.csv", row.names=FALSE)

DSE_df <- data_df |>
  select(starts_with("DSE"), id)
DSE_df  <- remove_na(DSE_df)
DSE_df <- pivot_longer(DSE_df, cols=-c(id), names_to="item", values_to="resp")

save(DSE_df, file="SPQVS_Barnby_2017_DSE.Rdata")
write.csv(DSE_df, "SPQVS_Barnby_2017_DSE.csv", row.names=FALSE)

SENPQ_df <- data_df |>
  select(starts_with("SENPQ"), id)
SENPQ_df  <- remove_na(SENPQ_df)
SENPQ_df <- pivot_longer(SENPQ_df, cols=-c(id), names_to="item", values_to="resp")

save(SENPQ_df, file="SPQVS_Barnby_2017_SENPQ.Rdata")
write.csv(SENPQ_df, "SPQVS_Barnby_2017_SENPQ.csv", row.names=FALSE)

SIAS_df <- data_df |>
  select(starts_with("SIAS"), id)
SIAS_df  <- remove_na(SIAS_df)
SIAS_df <- pivot_longer(SIAS_df, cols=-c(id), names_to="item", values_to="resp")

save(SIAS_df, file="SPQVS_Barnby_2017_SIAS.Rdata")
write.csv(SIAS_df, "SPQVS_Barnby_2017_SIAS.csv", row.names=FALSE)
