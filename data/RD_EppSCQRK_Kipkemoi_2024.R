# Paper: https://link.springer.com/article/10.1007/s10803-024-06380-9
# Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NJHSAC

library(haven)
library(dplyr)
library(tidyr)
library(readr)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id", "date"))])) == (ncol(df) - 2)), ]
  return(df)
}

Scq_df <- read_csv("autism_study_scq_analysis_dataset_anon.csv")

Scq_df <- Scq_df %>%
  rename(id = studyno_anon)
Scq_df  <- Scq_df |>
  select(starts_with("scq"), id)

# The source file ships 25 rows that are byte-identical duplicates of another
# row across all 66 of its columns -- the same studyno_anon twice, with nothing
# distinguishing the two. Left in, they emitted every one of those 25
# respondents' 40 items twice (1,000 excess id+item rows; irw#1842 block G).
Scq_df <- distinct(Scq_df)

Scq_df <- Scq_df |>
  mutate(across(where(is.character), ~ recode(., "N" = 0, "Y" = 1)))

Scq_df <- remove_na(Scq_df )
Scq_df  <- pivot_longer(Scq_df, cols=-c(id), names_to="item", values_to="resp")

save(Scq_df, file="RD_EppSCQRK_Kipkemoi_2024_scq.Rdata")
write.csv(Scq_df, "RD_EppSCQRK_Kipkemoi_2024_scq.csv", row.names=FALSE)