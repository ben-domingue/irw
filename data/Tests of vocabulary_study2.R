#paper. https://link.springer.com/article/10.3758/s13428-022-01856-x#data-availability
#study 2
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("Student_vocabulary_test_study2.xlsx",na = "NA")
data <- data %>%
  select(ID, age, snout:frankincense,T1Q1:T12Q2) %>% 
  rename(id = ID)
data_1 <- data %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
saveRDS(data_1, "Tests of vocabulary_study2.RData")    
