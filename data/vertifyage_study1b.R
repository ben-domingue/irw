#paper https://link.springer.com/article/10.3758/s13428-022-01944-y#Sec34
#study_1b
library(dplyr)
library(tidyr)
library(haven)

data <- read_sav("Study 1b_PrimePanels_Data.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data <- data[!is.na(data$Age), ]

data <- data %>%
  select(ResponseId, Q4correct:Q59correct, Age) %>%
  rename(id = ResponseId, age = Age)
names(data) <- gsub("correct", "", names(data))

data_1 <- data %>% 
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )

saveRDS(data_1, "vertifyage_study1b.RData")         
