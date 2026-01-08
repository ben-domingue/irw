library(tidyr)
library(dplyr)

data <- read.csv("/Users/rubinashrestha/Downloads/data_11.csv")

data <- data %>%
  rename(
    id = id_student,
    cov_age = age,
    cov_birth_year = birth_year,
    cov_age = age,
    cov_gender = gender,
    cov_religion = religion,
    cov_race = race,
    cov_skin_color = skin_color,
    cov_grade = grade
  )

data_long <- data %>%
  pivot_longer(
    cols = -id,
    names_to = "item",
    values_to = "resp",
    values_transform = list(resp = as.character)
  ) %>%
  mutate(resp = replace_na(resp, "0"))   # NA -> "0" (character)

write.csv(
  data_long,
  "racialsocialnormsbrazilianstudents_portella_2022.csv",
  row.names = FALSE
)


