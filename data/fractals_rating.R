#https://osf.io/ckfmv/

library(dplyr)

data <- read.csv("fractals_rating_questionnaire_data.csv")

data_1 <- data %>%
  rename(rater = id, id = fractal, item = feature, resp = ratingValue) %>%
  mutate(id = sub("SHINEd_", "", id),
         id = sub("^.", "F", id))

data_2 <- select(data_1, id, item, rater, resp)

save(data_2, file = "fractals_rating.Rdata")
