# Paper: 
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/UT9RVL
library(haven)
library(dplyr)
library(tidyr)
library(readxl)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}


CESDS_df <- read_dta("Replication Data Set - CES-D Scale in Older Filipinos.dta")

CESDS_df[] <- lapply(CESDS_df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})

CESDS_df <- CESDS_df |>
  select(starts_with("P1SD1"))
CESDS_df = remove_na(CESDS_df)


CESDS_df <- CESDS_df %>%
  mutate(id = row_number() )

CESDS_df <- pivot_longer(CESDS_df, 
                         cols = -id, 
                         names_to = "item", 
                         values_to = "resp")

save(CESDS_df, file="RD_PPCSEDSOF_Afable_2023.Rdata")
write.csv(CESDS_df, "RD_PPCSEDSOF_Afable_2023.csv", row.names=FALSE)