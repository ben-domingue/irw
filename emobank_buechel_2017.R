library(tidyverse)

writer_raw <- read_csv("/Users/rubinashrestha/Downloads/individual_reader_ratings.csv")

writer_irw <- writer_raw %>%
  pivot_longer(
    cols = c(V, A, D),
    names_to = "item",
    values_to = "resp"
  ) %>%
  mutate(
    item = recode(item, V = "valence", A = "arousal", D = "dominance")
  ) %>%
  select(id, item, resp) %>%
  arrange(id, item)

write_csv(writer_irw, 
          "/Users/rubinashrestha/Downloads/emobank_buechel_2017_reader.csv")