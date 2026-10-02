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
    # RT is in milliseconds: magpie records it as a JavaScript Date.now()
    # difference, and each submission's summed RT is 31-99% of its
    # endTime - startTime span, which is itself in ms (irw#2401). IRW wants seconds.
    rt = RT / 1000,
    item = trial_name,
    rater = submission_id,
    resp
  )

write.csv(data, "emoji_scheffler_2024.csv", row.names = FALSE)

