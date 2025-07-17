library(dplyr)
library(tidyr)

df <- read.delim("JEEHP-24-030_6_00_11702.tab", header = TRUE, sep = "\t")

df <- df %>%
  mutate(id = seq(1, nrow(.))) %>%
  select(-c(Code, Time)) %>%
  pivot_longer(-id,
               names_to = "item",
               values_to = "resp") %>%
  filter(grepl("^Q", item))


write.csv(df, "360emergencymed_azami_2024.csv", row.names = FALSE)
