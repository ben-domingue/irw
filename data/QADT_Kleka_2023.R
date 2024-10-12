library(tidyverse)

load('zr_cleaned.rda')

df <- zr |>
  select(OSOBA, fala, ZR_1:ZR_12) |>
  pivot_longer(c(ZR_1:ZR_12),
               names_to = "item",
               values_to = "resp") |>
  filter(!is.na(resp))  |>
  rename(id = OSOBA, wave = fala)

write.csv(df, "QADT_Kleka_2023.csv", row.names=FALSE)
