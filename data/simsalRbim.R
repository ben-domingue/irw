library(dplyr)
library(tidyr)
library(readr)
library(stringr)


files <- c(
  "Human_LargeValence_2018.txt",
  "Human_LargeValence_2017.txt",
  "Human_LowValence_2017.txt"
)
# The Mice_LowValence, Mice_LargeValence and Monkey_LargeValence files are not
# processed: their quantity is the amount an animal consumed (a physical
# measure, not an item response), with 6-11 animals each. Withdrawn 2026-10-01
# (irw#1700).

# The three human studies run the same task (21 paired choices among 7 pictures;
# resp = 1 for the picture chosen) on different people, and are pooled into one
# table with cov_sample naming the study (Ben 2026-10-01, irw#1700). Each alone
# is under the 100-id floor (32, 16, 63). LargeValence 2017/2018 share their 7
# pictures; LowValence uses 7 different ones, so the two stimulus sets do not
# overlap.
pooled <- list()
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
    select(id, item, resp, trial) %>%
    mutate(cov_sample = str_remove(str_remove(f, "^Human_"), "\\.txt$"))

  pooled[[f]] <- data
}

write.csv(bind_rows(pooled), "simsalrbim_human.csv", row.names = FALSE)
