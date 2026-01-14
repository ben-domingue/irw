library(dplyr)
library(haven)

data_1 <- read_sav("Data Study 1.sav")
data_2 <- read_sav("Data Study 2.sav")

data_1 <- data_1%>%
  rename(id = code,
         cov_gender = gender,
         cov_age = age)%>%
  mutate(study =1 )%>%
  select(id,study, starts_with("cov_"), starts_with("stolz_"))

data_2 <- data_2%>%
  rename(cov_gender = gender,
         cov_age = age)%>%
  mutate(study =2,
         id = row_number())%>%
  select(id,study, starts_with("cov_"), starts_with("stolz_"))

data = rbind(data_1, data_2)

data<- data %>%
  zap_labels()%>%
  pivot_longer(
    cols = starts_with("stolz"),
    names_to = "item",
    values_to = "resp"
  )

write.csv(data, "gahps_korner_2021.csv", row.names = FALSE)
