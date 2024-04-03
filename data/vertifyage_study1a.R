#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
#study_1a
library(dplyr)
library(tidyr)
library(haven)

data <- read_sav("Study 1a_MTurk_Data.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))
data <- data %>%
  select(ResponseId, Q4correct:Q69correct,Q67correct:Q65correct, Q57) %>%
  rename(id = ResponseId, age = Q57)
names(data) <- gsub("correct", "", names(data))

data_1 <- data %>% 
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "vertifyage_study1a.RData")         
