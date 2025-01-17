library(tidyr)
library(dplyr)

data <- read.table("EES_data.txt", sep = ",", header = TRUE)

data <- data %>%
  rename(id = Response.ID, cov_age = Age, cov_gender = Gender, cov_nationality = Nationality, study = Study) %>%
  select(-age_group) %>%
  pivot_longer(VE1:IU15,
               values_to = "resp",
               names_to = "item")

data_ve <- data %>%
  filter(grepl("VE", item))

data_iu <- data %>%
  filter(grepl("IU", item))

#write.csv(data_ve, "ees_sarling_2024_vicarious_experience.csv", row.names=FALSE)
#write.csv(data_iu, "ees_sarling_2024_intuitive_understanding.csv", row.names=FALSE)


###NOTE: ees_sarling_2024_vicarious_experience.csv & ees_sarling_2024_intuitive_understanding.csv joined to create ees_sarling_2024
