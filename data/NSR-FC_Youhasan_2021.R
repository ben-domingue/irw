library(tidyr)
library(dplyr)

dat1 <- read.csv('Dataset 1. Two-hundred sixty-five students’ responses to the measurement scale of nursing students’ readiness for the flipped classroom for exploratory factor analysis and reliability testing.csv')
dat2 <- read.csv('Dataset 2. Ninety students’ responses to the measurement scale of nursing students’ readiness for the flipped classroom for confirmatory factor analysis.csv')


dat1 <- dat1 %>%
  select(Academic_Year, Q1:Q35)

dat2 <- dat2 %>%
  select(Academic_Year, Q1:Q35)

comb <- bind_rows(dat1, dat2)

comb$id <- seq(1, nrow(comb))

length(unique(comb$id))

comb <- comb %>%
  pivot_longer(c(Q1:Q35),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp) & resp !=6)

comb <- comb %>% select(id, Academic_Year, item, resp)

write.csv(comb, "NSR-FC_Youhasan_2021.csv", row.names=FALSE)
