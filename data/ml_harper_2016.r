# Paper:
# Data: https://grouplens.org/datasets/movielens/
library(haven)
library(dplyr)
library(tidyr)

df <- read.csv("ratings.csv")

df <- df |>
  rename(id=movieId, item=userId, resp=rating) |>
  select(-timestamp)

save(df, file="ml_harper_2015.Rdata")
write.csv(df, "ml_harper_2015.csv", row.names=FALSE)


###BD 1-27-2025: added
#rater<-id
#id<-1
