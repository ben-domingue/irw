library(dplyr)

data <- read.csv("emoji-norming-results-raw.csv")

data <- data %>%
  mutate(
    resp = case_when(
      trial_name == "familiarity" ~ as.character(familiarity),
      trial_name == "naming" ~ paste(response1, response2, response3, sep = ", "),
      trial_name == "arousal" ~ as.character(answere),
      trial_name == "complexity" ~ as.character(compexity),   
      trial_name == "valence" ~ as.character(valence),
      trial_name == "ambiguity" ~ as.character(ambiguity),
      TRUE ~ NA_character_
    )
  )

data <- data %>%
  transmute(
    id = name,
    rt = RT,
    item = trial_name,
    rater = submission_id,
    resp
  )

write.csv(data, "emoji_scheffler_2024.csv", row.names = FALSE)

