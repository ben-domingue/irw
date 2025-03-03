library(readxl)
library(tidyr)
library(dplyr)

df <- read_xlsx("data EnviRisk.xlsx")

df <- df %>% select(-c("m_polor",
                "income_r",
                "m_acc",
                "genderMF")) %>%
  rename(cov_age = age,
         cov_gender = gender,
         cov_education = education,
         cov_income = income,
         )

df$id <- seq(1, nrow(df))

df <- df %>%
  pivot_longer(bd_risk1:libcons,
               names_to = "item",
               values_to = "resp") %>%
  select(id, cov_age, cov_gender, cov_education, cov_income, item, resp) %>%
  filter(item != "attentioncheck") #attentioncheck is a constant

table(df$resp)

write.csv(df, "envirisk_lalot_2025.csv", row.names = FALSE)
