library(readxl)
library(tidyr)
library(dplyr)

df <- read_xlsx("DATA.xlsx")

df$id <- seq(1 : nrow(df))

df <- df %>%
  rename(cov_educators = Educators, cov_loc_of_educ_institution = "Location of Educational Institution",
         cov_education = "Educational Level", cov_employment = "Employment Status", cov_years_of_service = "Years of Service",
         cov_age = Age, cov_gender = Gender) %>%
  select(c(id, starts_with("cov"), Q1:Q15)) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp")

write.csv(df, "ilearnathome_regalado_2025.csv", row.names = FALSE)
