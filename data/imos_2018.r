library(haven)
library(dplyr)
library(tidyr)

remove_na <- function(df) {
  df <- df[!(rowSums(is.na(df[, -which(names(df) %in% c("id"))])) == (ncol(df) - 1)), ]
  return(df)
}

study_df <- read.csv("imo_results.csv")
study_df <- study_df |>
  mutate(id= row_number())

problem_df <- study_df %>%
  select(starts_with("Problem"),id,country, rank, award)
problem_df  <- remove_na(problem_df)
problem_df <- pivot_longer(problem_df, cols=-c(id, country, rank, award), names_to="item", values_to="resp")
problem_df <- problem_df |>
  rename(cov_country = country,cov_rank = rank,cov_award = award)
save(problem_df, file="imos_2018.Rdata")
write.csv(problem_df, "imos_2018.csv", row.names=FALSE)
