#https://osf.io/ckfmv/

library(tidyverse)

data <- read_csv("fractals_rating_questionnaire_data.csv")

data_1 <- data %>%
  mutate(item = paste(fractal, feature, sep = "_")) %>%
  select(-fractal, -feature) %>%
  rename(resp = ratingValue) %>%
  select(id, item, resp)


save(data_1, file = "fractals_rating.RData")
