library(dplyr)
library(tidyr)
library(readr)
library(stringr)


files <- c(
  "Human_LargeValence_2018.txt",
  "Human_LargeValence_2017.txt",
  "Human_LowValence_2017.txt",
  "Mice_LowValence.txt",
  "Mice_LargeValence.txt",
  "Monkey_LargeValence.txt"
)

for (f in files) {
  data <- read.table(f, header = TRUE)
  
  data <- data %>%
    mutate(trial = row_number())  %>%
    pivot_longer(
      cols = c(optionA, optionB, quantityA, quantityB),
      names_to = c(".value", "choice_side"),
      names_pattern = "(option|quantity)([AB])",
      names_repair = "unique"  # ensures no duplicate names cause an error
    ) %>%
    rename(
      id = subjectID,
      item = option,
      resp = quantity
    ) %>%
    select(id, item, resp, trial)
    
   out_name <- str_replace(f, "\\.txt$", ".csv")
   out_name <- paste0("simsalRbim_", out_name)
   
   write.csv(data, out_name, row.names = FALSE)
  
}
