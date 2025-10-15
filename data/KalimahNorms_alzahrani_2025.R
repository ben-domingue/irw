library(dplyr)

data <- read.csv("raw_ratings.csv")

# Rename multiple columns
# pos : part of speech
data <- data %>%
  filter(current_display == "main") %>%
  transmute(
    id = as.integer(factor(wordlist_ar_word)),
    rt = reaction_time/1000,   #convert ms to s
    item = task_name,
    resp = response,
    cov_frequency = wordlist_relative_frequency,
    cov_num_letters = wordlist_number_of_letters,
    cov_pos =wordlist_pos,
    cov_arabic_word = wordlist_ar_word,
    rater = as.integer(factor(participant_private_id))
)

write.csv(data, "KalimahNorms_alzahrani_2025.csv", row.names = FALSE)

