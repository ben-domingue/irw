#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
#study_2
library(dplyr)
library(tidyr)
library(haven)

data <- read_sav("Study 2_Imposters_Data.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data <- data[!is.na(data$Q57), ]

data <- data %>%
  select(ResponseId, Q4correct:Q59correct, Q57) %>%
  rename(id = ResponseId, age = Q57)
names(data) <- gsub("correct", "", names(data))

data_1 <- data %>% 
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "vertifyage_study2.RData")         
