library(tidyr)
library(dplyr)

dat1 <- read.csv("raw_data_study1.csv", sep = ";", header = TRUE)
dat2 <- read.csv("raw_data_study2.csv", sep = ";", header = TRUE)

dat1 <- dat1 %>%
  rename(id = ID) %>%
  pivot_longer(-id,
               values_to = "resp",
               names_to = "item")

dat2 <- dat2 %>%
  rename(id = ID) %>%
  pivot_longer(-id,
               values_to = "resp",
               names_to = "item")

write.csv(dat1, "icg_schakowski_2023_study1.csv", row.names=FALSE)
write.csv(dat2, "icg_schakowski_2023_study2.csv", row.names=FALSE)
