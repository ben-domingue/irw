library(tidyr)
library(dplyr)

df <- read.table("Jeehp-14-20_raw data.tab", header=TRUE)

df$id <- seq(1, nrow(df))

df <- df %>%
  pivot_longer(c(-id),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

write.csv(df, "KoreanNursing_Park_2017.csv", row.names=FALSE)