# Paper: https://link.springer.com/article/10.3758/s13428-024-02480-7
# Data: https://osf.io/5qxkh/files/osfstorage
library(haven)
library(dplyr)
library(tidyr)

process_item_level_data <- function(prefix) {
  # Construct input filename
  filename <- paste0(prefix, "_itemLevel.csv")
  
  # Read and process the dataset
  df <- read.csv(filename) |>
    dplyr::select(-task) |>
    dplyr::rename(id = participant) |>
    tidyr::pivot_longer(cols = -id, names_to = "item", values_to = "resp") |>
    dplyr::filter(!grepl("\\.", as.character(resp)))  # Exclude decimal values
  
  # Print response frequency table
  print(table(df$resp))
  
  # Create output filenames
  csv_filename <- paste0("idcr_martinez_2023_", prefix, ".csv")
  rdata_filename <- paste0("idcr_martinez_2023_", prefix, ".RData")
  
  # Save to CSV
  write.csv(df, csv_filename, row.names = FALSE)
  
  # Save as RData
  save(df, file = rdata_filename)
  
  # Return processed dataframe
  return(df)
}


process_item_level_data("lns")
process_item_level_data("ravens")
process_item_level_data("vocab")
process_item_level_data("info")
process_item_level_data("raco")
process_item_level_data("numSeries")
process_item_level_data("ps")
process_item_level_data("matches")
process_item_level_data("analogies")
process_item_level_data("Story Recall 1")
process_item_level_data("Story Recall 2")
process_item_level_data("Story Recall 3")