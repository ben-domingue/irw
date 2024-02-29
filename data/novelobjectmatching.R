library(tidyverse)


long_form_a <- read_csv("D:/Desktop/Phase 2 Data - Part 1 (Long Form A).csv") %>%
  rename(id = 1) %>%
  pivot_longer(
    -id, 
    names_to = "item",
    values_to = "resp"
  )

long_form_b <- read_csv("D:/Desktop/Phase 2 Data - Part 1 (Long Form B).csv") %>%
  rename(id = 1) %>%
  pivot_longer(
    -id, 
    names_to = "item",
    values_to = "resp"
  )


result_df <- bind_rows(long_form_a, long_form_b)


save(result_df, file = "df.Rdata")
