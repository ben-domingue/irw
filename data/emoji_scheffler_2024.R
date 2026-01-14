library(dplyr)

data <- read.csv("emoji-norming-results-raw.csv")

data <- data %>%
  mutate(
    resp = case_when(
      trial_name == "familiarity" ~ familiarity,
      trial_name == "arousal" ~ answere,
      trial_name == "complexity" ~compexity,   
      trial_name == "valence" ~ valence,
      trial_name == "ambiguity" ~ ambiguity,
      TRUE ~ NA_real_
    )
  )%>%
  filter(trial_name != 'naming')

data <- data %>%
  transmute(
    id = name,
    rt = RT,
    item = trial_name,
    rater = submission_id,
    resp
  )

write.csv(data, "emoji_scheffler_2024.csv", row.names = FALSE)

