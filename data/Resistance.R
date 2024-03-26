#https://link.springer.com/article/10.3758/s13428-022-01876-7#data-availability

library(tidyverse)
library(readr)

data <- read_csv("Data_Full.csv")

data_long <- data %>%
  pivot_longer(cols = -c(1,2), names_to = "item", values_to = "resp") %>%
  rename(id = 1, group = 2)

saveRDS(data_long, file = "Resistance.RData")
