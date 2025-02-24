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
df_list <- split(study_df, study_df$year)
list2env(df_list, envir = .GlobalEnv)

process_df <- function(study_df, year) {
  problem_df <- study_df %>%
    select(starts_with("Problem"), id, country, rank, award)
  
  # Remove NAs (replace with an appropriate function)
  problem_df <- na.omit(problem_df)
  
  # Pivot longer
  problem_df <- pivot_longer(problem_df, cols=-c(id, country, rank, award),
                             names_to="item", values_to="resp")
  
  # Rename columns
  problem_df <- problem_df |>
    rename(cov_country = country, cov_rank = rank, cov_award = award)
  
  # Save as .Rdata
  save_filename <- paste0("imos_", year, ".Rdata")
  save(problem_df, file=save_filename)
  
  # Save as CSV
  csv_filename <- paste0("imos_", year, ".csv")
  write.csv(problem_df, csv_filename, row.names=FALSE)
}

# Loop through df_list and apply process_df function
for (year in names(df_list)) {
  process_df(df_list[[year]], year)
}
