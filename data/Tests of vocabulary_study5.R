#paper. https://link.springer.com/article/10.3758/s13428-022-01856-x#data-availability
#study 5
library(readxl)
library(dplyr)
library(tidyr)

data <- read_excel("student_vocabulary_test_study5.xlsx",na = "NA")
data <- data %>%
  select(ID, age, BFI1:AFOQT20,T1SQ001:T10SQ005,RF1:GK65) %>% 
  rename(id = ID)
data_1 <- data %>%
  pivot_longer(
    cols = -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )
saveRDS(data_1, "Tests of vocabulary_study5.RData")  
