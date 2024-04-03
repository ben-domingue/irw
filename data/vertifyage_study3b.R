#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
#study_3b
library(dplyr)
library(tidyr)
library(haven)

data <- read_sav("Study 3b_LE_Data.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))
data <- data %>%
  select(ResponseId, Q4correct:Q59correct, Q4.4) %>%
  rename(id = ResponseId, age = Q4.4)
names(data) <- gsub("correct", "", names(data))

data_1 <- data %>% 
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "vertifyage_study3b.RData")         
