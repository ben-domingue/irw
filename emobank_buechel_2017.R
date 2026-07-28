library(tidyverse)

# --- 1. Read both raw rating files (wide: id, V, A, D) ---
writer_raw <- read_csv("/Users/rubinashrestha/Downloads/individual_writer_ratings.csv")
reader_raw <- read_csv("/Users/rubinashrestha/Downloads/individual_reader_ratings.csv")

# --- 2. Reshape each to long format and tag the perspective ---
reshape_ratings <- function(df, perspective) {
  df %>%
    pivot_longer(
      cols = c(V, A, D),
      names_to = "dimension",
      values_to = "resp"
    ) %>%
    mutate(
      dimension = recode(dimension, V = "valence", A = "arousal", D = "dominance"),
      item = paste0(dimension, "-", perspective)
    ) %>%
    select(id, item, resp)
}

writer_long <- reshape_ratings(writer_raw, "writer")
reader_long <- reshape_ratings(reader_raw, "reader")

# --- 3. Combine into a single table ---
emobank_irw <- bind_rows(writer_long, reader_long) %>%
  arrange(id, item)

# --- 4. Write out in IRW format ---
write_csv(emobank_irw, "/Users/rubinashrestha/Downloads/emobank_buechel_2017.csv")

glimpse(emobank_irw)