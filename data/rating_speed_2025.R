library(dplyr)
library(tidyr)


data_arousal <- read.csv("All_Arousal.csv")
data_emotion <- read.csv("All_Primary_Emotions.csv")
data_valence <- read.csv("All_Valence.csv")

data_arousal<- data_arousal %>%
  mutate(resp = Passief...Actief,
         item = 'arousal',
         rater = Ppn,
         id = Woord) %>%
  select(id,item,resp,rater)

data_arousal$rater <- gsub("(male|female)$", "", data_arousal$rater)

data_valence<- data_valence %>%
  mutate(resp = Valence,
         item = 'valence',
         rater = Participant,
         id = Word) %>%
  select(id,item,resp,rater)


data_emotion <- data_emotion %>%
  mutate(rater = Participant,
         id = Woord) %>%
  select(rater,id,starts_with('met.'))

data_emotion_long <- data_emotion %>%
  pivot_longer(
    cols = -c(id, rater),
    names_to = "item",
    values_to = "resp"
  )

combined_data <- bind_rows(data_arousal, data_valence, data_emotion_long)

write.csv(combined_data, "rating_speed_2025.csv", row.names = FALSE)
